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
    # VG Code: New Field ADD
    project_code = fields.Char(string="Project code")
    sage_code = fields.Char(string="SAGE code")
    project_lead_id = fields.Many2one('crm.lead', string="Project Lead")
    em_ids = fields.One2many("em.em", "project_id", string="EM",readonly=True,
        states = {'draft': [('readonly', False)],'budgeting': [('readonly', False)],'approval': [('readonly', False)]},)
    hvac_ids = fields.One2many("hvac.hvac", "project_id", string="HVAC",readonly=True,
        states = {'draft': [('readonly', False)], 'budgeting': [('readonly', False)],'approval': [('readonly', False)]},)
    fc_ids = fields.One2many("fc.fc", "project_id", string="FC",readonly=True,
        states = {'draft': [('readonly', False)], 'budgeting': [('readonly', False)],'approval': [('readonly', False)]},)
    it_ids = fields.One2many("it.it", "project_id", string="IT",readonly=True,
        states = {'draft': [('readonly', False)], 'budgeting': [('readonly', False)],'approval': [('readonly', False)]},)
    admin_ids = fields.One2many("admin.admin", "project_id", string="ADMIN",readonly=True,
        states = {'draft': [('readonly', False)], 'budgeting': [('readonly', False)],'approval': [('readonly', False)]},)

    @api.model
    def default_get(self, fields):
        result = super(ProjectExtent, self).default_get(fields)

        if 'em_ids' in fields:
            em_list = []
            em_obj1 = self.env.ref("chamber_erp.em_em_obj_1")
            em_1 = self.env['em.em'].create({
                'code': em_obj1.code,
                'name': em_obj1.name,
            })
            em_list.append(em_1.id)
            em_obj2 = self.env.ref("chamber_erp.em_em_obj_2")
            em_2 = self.env['em.em'].create({
                'code': em_obj2.code,
                'name': em_obj2.name,
            })
            em_list.append(em_2.id)
            em_obj3 = self.env.ref("chamber_erp.em_em_obj_3")
            em_3 = self.env['em.em'].create({
                'code': em_obj3.code,
                'name': em_obj3.name,
            })
            em_list.append(em_3.id)
            em_obj4 = self.env.ref("chamber_erp.em_em_obj_4")
            em_4 = self.env['em.em'].create({
                'code': em_obj4.code,
                'name': em_obj4.name,
            })
            em_list.append(em_4.id)
            if em_list:
                result.update({
                    'em_ids': [(6, 0, em_list)]
                })

        if 'hvac_ids' in fields:
            hv_list = []
            hv_obj1 = self.env.ref("chamber_erp.hvac_hvac_obj_1")
            hv_1 = self.env['hvac.hvac'].create({
                'code': hv_obj1.code,
                'name': hv_obj1.name,
            })
            hv_list.append(hv_1.id)
            hv_obj2 = self.env.ref("chamber_erp.hvac_hvac_obj_2")
            hv_2 = self.env['hvac.hvac'].create({
                'code': hv_obj2.code,
                'name': hv_obj2.name,
            })
            hv_list.append(hv_2.id)
            hv_obj3 = self.env.ref("chamber_erp.hvac_hvac_obj_3")
            hv_3 = self.env['hvac.hvac'].create({
                'code': hv_obj3.code,
                'name': hv_obj3.name,
            })
            hv_list.append(hv_3.id)
            hv_obj4 = self.env.ref("chamber_erp.hvac_hvac_obj_4")
            hv_4 = self.env['hvac.hvac'].create({
                'code': hv_obj4.code,
                'name': hv_obj4.name,
            })
            hv_list.append(hv_4.id)
            if hv_list:
                result.update({
                    'hvac_ids': [(6, 0, hv_list)]
                })

        if 'fc_ids' in fields:
            fc_list = []
            fc_obj1 = self.env.ref("chamber_erp.fc_fc_obj_1")
            fc_1 = self.env['fc.fc'].create({
                'code': fc_obj1.code,
                'name': fc_obj1.name,
            })
            fc_list.append(fc_1.id)
            fc_obj2 = self.env.ref("chamber_erp.fc_fc_obj_2")
            fc_2 = self.env['fc.fc'].create({
                'code': fc_obj2.code,
                'name': fc_obj2.name,
            })
            fc_list.append(fc_2.id)
            fc_obj3 = self.env.ref("chamber_erp.fc_fc_obj_3")
            fc_3 = self.env['fc.fc'].create({
                'code': fc_obj3.code,
                'name': fc_obj3.name,
            })
            fc_list.append(fc_3.id)
            fc_obj4 = self.env.ref("chamber_erp.fc_fc_obj_4")
            fc_4 = self.env['fc.fc'].create({
                'code': fc_obj4.code,
                'name': fc_obj4.name,
            })
            fc_list.append(fc_4.id)
            if fc_list:
                result.update({
                    'fc_ids': [(6, 0, fc_list)]
                })

        if 'it_ids' in fields:
            it_list = []
            it_obj1 = self.env.ref("chamber_erp.it_it_obj_1")
            it_1 = self.env['it.it'].create({
                'code': it_obj1.code,
                'name': it_obj1.name,
            })
            it_list.append(it_1.id)
            it_obj2 = self.env.ref("chamber_erp.it_it_obj_2")
            it_2 = self.env['it.it'].create({
                'code': it_obj2.code,
                'name': it_obj2.name,
            })
            it_list.append(it_2.id)
            it_obj3 = self.env.ref("chamber_erp.it_it_obj_3")
            it_3 = self.env['it.it'].create({
                'code': it_obj3.code,
                'name': it_obj3.name,
            })
            it_list.append(it_3.id)
            it_obj4 = self.env.ref("chamber_erp.it_it_obj_4")
            it_4 = self.env['it.it'].create({
                'code': it_obj4.code,
                'name': it_obj4.name,
            })
            it_list.append(it_4.id)
            if it_list:
                result.update({
                    'it_ids': [(6, 0, it_list)]
                })

        if 'admin_ids' in fields:
            admin_list = []
            admin_obj1 = self.env.ref("chamber_erp.admin_admin_obj_1")
            admin_1 = self.env['admin.admin'].create({
                'code': admin_obj1.code,
                'name': admin_obj1.name,
                'wbs_char': admin_obj1.wbs_char,
            })
            admin_list.append(admin_1.id)
            admin_obj2 = self.env.ref("chamber_erp.admin_admin_obj_2")
            admin_2 = self.env['admin.admin'].create({
                'code': admin_obj2.code,
                'name': admin_obj2.name,
                'wbs_char': admin_obj2.wbs_char,
            })
            admin_list.append(admin_2.id)
            admin_obj3 = self.env.ref("chamber_erp.admin_admin_obj_3")
            admin_3 = self.env['admin.admin'].create({
                'code': admin_obj3.code,
                'name': admin_obj3.name,
                'wbs_char': admin_obj3.wbs_char,
            })
            admin_list.append(admin_3.id)

            if admin_list:
                result.update({
                    'admin_ids': [(6, 0, admin_list)]
                })
        return result

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

    def action_budgeting(self):
        self.write({
            'state' : 'budgeting'
        })

    def action_budget_complete(self):
        self.write({
            'state' : 'approval'
        })


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
