from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class ProjectExtent(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    project_type = fields.Selection(
        [('fire_consulting', 'Fire Consulting'),
         ('electro_mechanical', 'Electro Mechanical'),
         ('technical_outsourcing', 'Technical Outsourcing'),
         ('facility_management', 'Facility Management')], string='Type',
        required=True)
    project_return_ids = fields.One2many('stock.inventory.return.line', 'project_id', string='Inventory Return',
                                         domain=[('state', '=', 'confirm')])
    project_delivery_ids = fields.One2many('stock.move', 'project_id', string='Delivery')
    total_labour_expense = fields.Float(string="Labour Expense")

    def confirm_project(self):
        if self.project_type == 'fire_consulting':
            code = self.env['ir.sequence'].next_by_code('project.lead.fire')
        if self.project_type == 'electro_mechanical':
            code = self.env['ir.sequence'].next_by_code('project.lead.electro')
        if self.project_type == 'technical_outsourcing':
            code = self.env['ir.sequence'].next_by_code('project.lead.technical')
        if self.project_type == 'facility_management':
            code = self.env['ir.sequence'].next_by_code('project.lead.facility')

        vals = ({
            'name': '[' + code + '] ' + self.name,
            'partner_id': self.partner_id.id,
            'group_id': int(self.env['ir.config_parameter'].sudo().get_param('project.analytic.group_id')),
        })
        analytic_account_id = self.env['account.analytic.account'].create(vals)

        self.write({
            'state': 'ongoing',
            'code': code,
            'analytic_account_id': analytic_account_id.id,
        })

    def update_project_summary(self):
        for rec in self:
            rec.total_material_cost = 0
            rec.total_expense = 0
            rec.total_income = 0
            journal_ids = self.env['account.journal'].search([('name', '!=', 'Customer Invoices')])
            expense = self.env['account.move.line'].search(
                [('project_id', '=', rec.id), ('journal_id', 'in', journal_ids.ids), ('move_id.state', '=', 'posted')])
            journal_id = self.env['account.journal'].search([('name', '=', 'Customer Invoices')], limit=1)
            income = self.env['account.move'].search(
                [('project_id', '=', rec.id), ('journal_id', '=', journal_id.id), ('state', '=', 'posted')])
            timesheet = self.env['project.timesheet'].search([('project_id', '=', rec.id), ('state', '=', 'approved')])
            rec.total_labour_expense = sum(timesheet.mapped('total_hour_rates'))
            if rec.project_line_product_ids:
                for line in rec.project_line_product_ids:
                    if line.qty_delivered:
                        rec.total_material_cost = rec.total_material_cost + (line.qty_delivered * line.cost)
            if expense:
                for exp in expense:
                    rec.total_expense = rec.total_expense + exp.debit
            if income:
                for inc in income:
                    rec.total_income = rec.total_income + inc.amount_total
            total_expense_material = rec.total_expense + rec.total_material_cost
            rec.total_profit = rec.total_income - total_expense_material
            try:
                rec.total_profit_per = (rec.total_profit * 100) / rec.total_income
            except ZeroDivisionError:
                rec.total_profit_per = 0


class ProjectOrderLines(models.Model):
    _inherit = "project.project.orderline"

    project_sales_line_id = fields.Many2one('project.sales.line', string='Project Estimation Lines',
                                            track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', related='project_id.partner_id', store=True, string='Customer')


class ProjectEstimationLines(models.Model):
    _name = "project.sales.line"
    _description = "Project Estimation Line"
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    product_id = fields.Many2one('product.product', string='Product', required=True)
    order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    order_id = fields.Many2one('sale.order', string='Sale Order')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    name = fields.Text(string='Description', required=True, track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Project')
    currency_id = fields.Many2one('res.currency', string='Currency')
    product_qty = fields.Float(string='Product Quantity', track_visibility='onchange')
    total_shop_qty = fields.Float(string='Total Shop Quantity', store=True, compute='_compute_total_shop_qty',
                                  track_visibility='onchange')
    project_order_line_ids = fields.One2many('project.project.orderline', 'project_sales_line_id',
                                             string='Product Assignment')

    remarks = fields.Text(string='Remarks', track_visibility='onchange')

    @api.depends('project_order_line_ids')
    def _compute_total_shop_qty(self):
        for record in self:
            record.total_shop_qty = sum(record.project_order_line_ids.mapped('product_uom_qty'))


class SaleOrderAssignProjectWizard(models.TransientModel):
    _inherit = "sale.project.assign.wizard"
    _description = "Sale Order Assign Project"

    project_id = fields.Many2one('project.project', 'Project', domain=[('state', '=', 'ongoing')], required=True)
    order_id = fields.Many2one('sale.order', 'Quotation')
    message = fields.Text(string='Message')

    def assign_project_to(self):
        if self.order_id.state == 'sale':
            for line in self.order_id.order_line.filtered(
                    lambda r: r.display_type == False and r.is_downpayment == False):
                vals = {

                    'project_id': self.project_id.id,
                    'order_id': self.order_id.id,
                    'order_line_id': line.id,
                    'uom_id': line.product_uom.id,
                    'name': line.name,
                    'product_qty': line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'currency_id': self.order_id.pricelist_id.currency_id.id
                }
                self.env['project.sales.line'].create(vals)

            self.order_id.write({
                'project_id': self.project_id.id,
            })
            self.project_id.write({
                'partner_id': self.order_id.partner_id.id
            })
            # if self.order_id.estimation_id:
            #     self.order_id.estimation_id.consumable_line_ids.write({'project_id' : self.project_id.id})
        else:
            raise Warning(
                'This order is not confirmed, Please conifirm the quotation before assigning to a project.')
        return {'type': 'ir.actions.act_window_close'}
