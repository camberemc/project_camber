from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class ProjectExtented(models.Model):
    _name = 'project.project'
    _inherit = ['project.project','portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char(string='Project Code', store=True,
                       default="Drafted", copy=False)

    description = fields.Text(string='Description')

    state = fields.Selection([
        ('draft', 'New Project'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('close', 'Closed')], string='Status', readonly=True, copy=False, index=True,
        track_visibility='onchange', default='draft')

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    project_line_product_ids = fields.One2many('project.project.orderline', 'project_id', string='Project Products')
    project_indent_ids = fields.One2many('project.delivery.indent', 'project_id', string='Delivery Indents')

    retention_date = fields.Date(string='Retention Date')
    total_expense = fields.Float(string="Total Expense", readonly=True)
    total_income = fields.Float(string="Total Income", readonly=True)
    total_material_cost = fields.Float(string="Total Material Cost", readonly=True)
    total_profit = fields.Float(string="Total Profit", readonly=True)
    total_profit_per = fields.Float(string="Total Profit (%)", readonly=True)
    project_inventory_ids = fields.One2many('stock.move', 'project_id',
                                                       string='Inventory Lines')

    # def unlink(self):
    #     if self.code !='Drafted':
    #         raise UserError('Cannot delete Project')
    #     return super(ProjectExtented, self).unlink()

    # @api.multi
    def name_get(self):
        """ Return the categories' display name, including their direct
            parent by default.
            If ``context['partner_category_display']`` is ``'short'``, the short
            version of the category name (without the direct parent) is used.
            The default is the long version.
        """

        res = []
        for record in self:
            combined = '[' + record.code + '] ' + record.name
            res.append((record.id, combined))
        return res

    def confirm_project(self):
        code = self.env['ir.sequence'].next_by_code('project.code.order')

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

    def complete_project(self):
        self.write({
            'state': 'completed',
        })

    def close_project(self):
        if self.retention_date:
            self.write({
                'state': 'close',
            })
        else:
            raise UserError('Retension date not Added. Please fill out the retension date and close the project.')

    def action_expense_entries(self):
        journal_ids = self.env['account.journal'].search([('name', '!=', 'Customer Invoices')])
        action = {
            'name': _("Expense Entries"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'domain': [('project_id', '=', self.id), ('journal_id', 'in', journal_ids.ids)]
        }
        return action

    def action_income_entries(self):
        journal_id = self.env['account.journal'].search([('name', '=', 'Customer Invoices')], limit=1)
        action = {
            'name': _("Income Entries"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'domain': [('project_id', '=', self.id), ('journal_id', '=', journal_id.id)]
        }
        return action

    def action_sale_entries(self):
        action = {
            'name': _("Sales"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'domain': [('project_id', '=', self.id)]
        }
        return action

    def action_export_project_details(self):
        return self.env.ref('project_management.report_project_details_xlsx').report_action(self)

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


class ProjectOderLine(models.Model):
    _name = "project.project.orderline"
    _description = "Project Order Lines"
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Approved'),
        ('confirm', 'Confirmed')
    ], string='Status', default='draft', copy=False, track_visibility='onchange')

    name = fields.Text(string='Description', required=True, track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', readonly=True,
                             track_visibility='onchange')
    cost = fields.Float(string="cost", related='product_id.standard_price')

    product_uom_qty = fields.Float(string='Product Quantity')

    qty_added = fields.Float(string='Added +')
    qty_added_delivery = fields.Float(string='Added +')
    order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    qty_on_hand = fields.Float(string='On Hand', compute='_compute_qty', track_visibility='onchange')
    qty_purchased = fields.Float(string='Purchased Quantity', compute='_compute_qty', track_visibility='onchange')

    order_id = fields.Many2one('sale.order', string='Sale Order')

    partner_id = fields.Many2one('res.partner', related='order_id.partner_id', store=True, string='Customer')

    qty_delivered = fields.Float(string='Delivered Qty', compute='_compute_qty', track_visibility='onchange')

    project_purchase_ids = fields.One2many('project.purchase.line', 'project_order_line_id', string='Project Purchases')
    project_delivery_ids = fields.One2many('project.delivery.line', 'project_order_line_id', string='Project Delivery')
    qty_balance_purchase = fields.Float('Balance Purchase Qty', compute='_compute_balance_qty')
    qty_balance_delivery = fields.Float('Balance Delivery Qty', compute='_compute_balance_qty')
    purchase_status = fields.Selection([
        ('pending', 'Ongoing'),
        ('completed', 'Completed')], default='pending', compute='_compute_status', store=True)

    def create_delivery(self):
        record_ids = self._context.get('active_ids')
        if record_ids:
            selected = self.env['project.project.orderline'].browse(
                record_ids)
            action = self.env.ref('project_management.project_delivery_form_wizard').read()[0]
            action['context'] = dict(
                self.env.context,
                default_orderline_ids=selected.ids,
                default_partner_id=selected.mapped('partner_id.id')[0]
            )
            return action

    def create_purchase(self):
        record_ids = self._context.get('active_ids')
        if record_ids:
            selected = self.env['project.project.orderline'].browse(
                record_ids)
            action = self.env.ref('project_management.project_purchase_form_wizard').read()[0]
            action['context'] = dict(
                self.env.context,
                default_orderline_ids=selected.ids,
            )
            print(action)
            return action

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.name = record.product_id.name

    @api.depends('project_purchase_ids')
    def _compute_status(self):
        for record in self:
            if record.qty_purchased == record.product_uom_qty:
                record.purchase_status = 'completed'
            else:
                record.purchase_status = 'pending'

    @api.depends('qty_purchased', 'qty_delivered')
    def _compute_balance_qty(self):
        for rec in self:
            rec.qty_balance_purchase = rec.product_uom_qty
            rec.qty_balance_delivery = rec.product_uom_qty
            if rec.qty_purchased or rec.qty_balance_delivery:
                rec.qty_balance_purchase = rec.product_uom_qty - rec.qty_purchased
                rec.qty_balance_delivery = rec.product_uom_qty - rec.qty_delivered

    def _compute_price(self):
        for record in self:
            record.unit_sell_price = record.order_line_id.price_unit
            record.total_sell_price = record.order_line_id.price_subtotal
            record.total_cost = sum(record.project_purchase_ids.mapped('price_subtotal'))

    def _compute_qty(self):
        for record in self:
            record.qty_purchased = sum(record.project_purchase_ids.mapped('qty'))
            record.qty_delivered = sum(record.project_delivery_ids.mapped('qty'))
            record.qty_on_hand = record.product_id.qty_available

    @api.onchange('qty_added')
    def _check_quantity_purchased(self):
        for record in self:
            if record.qty_added > record.qty_balance_purchase:
                raise Warning(
                    _('You cannot create purchase order with excess quanity for each projects.'))

    @api.onchange('qty_added_delivery')
    def _check_quantity_delivery(self):
        for record in self:
            if record.qty_added_delivery > record.qty_balance_delivery:
                raise Warning(_('You cannot create delivery order with excess quanity '))
            if record.qty_added_delivery > record.qty_on_hand:
                raise Warning(_('Cannot deliver more than stock quantity. Purchase more..'))

    def l1_approval(self):
        self.write({
            'state': 'send'
        })

    def set_confirm(self):
        self.write({
            'state': 'confirm'
        })

    def set_draft(self):
        self.write({
            'state': 'draft'
        })


class ProjectPurchaseLines(models.Model):
    _name = "project.purchase.line"
    _description = "Project Purchase Line"
    _order = 'id desc'

    project_order_line_id = fields.Many2one('project.project.orderline', string='Project Order Line')
    project_id = fields.Many2one(string='Project', related='project_order_line_id.project_id')
    order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    order_id = fields.Many2one('purchase.order', string='Purchase Order',
                               readonly=True)

    price_unit = fields.Float(string='Purchase Cost', compute='_compute_cost')

    qty = fields.Float(string='Purchased Qty')
    price_subtotal = fields.Float(string='Total Cost', compute='_compute_cost')
    state = fields.Selection(related='order_line_id.order_id.state', string='State')

    date_planned = fields.Datetime(string='Expected Date', related='order_line_id.date_planned')

    @api.depends('order_id.state')
    def _compute_cost(self):
        for record in self:
            record.price_unit = 0
            record.price_subtotal = 0
            if record.state != 'draft':
                record.price_unit = record.order_line_id.price_unit
                record.price_subtotal = record.price_unit * record.qty


class ProjectDeliveryines(models.Model):
    _name = "project.delivery.line"
    _description = "Project Delivery Line"
    _order = 'id desc'

    project_order_line_id = fields.Many2one('project.project.orderline', string='Project Order Line')
    move_line_id = fields.Many2one('stock.move', string='Delivery Order Line')

    picking_id = fields.Many2one('stock.picking', string='Delivery Order', related='move_line_id.picking_id',
                                 readonly=True)

    qty = fields.Float(string='Delivered Qty')
    state = fields.Selection(string='State', related='move_line_id.picking_id.state')
    date_planned = fields.Datetime(string='Expected Date', related='move_line_id.date_deadline')

class ProjectDeliveryIndent(models.Model):
    _name = "project.delivery.indent"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    name = fields.Char(string='Description', required=True)
    new_item = fields.Boolean(string='New Item')
    # consumable_list_id = fields.Many2one('crm.estimation.consumable.line', string='Estimated Product')
    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0,
                               track_visibility='onchange')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    currency_id = fields.Many2one('res.currency', string='Currency', related='project_id.currency_id')
    unit_cost = fields.Monetary(string='Unit Cost')
    cost = fields.Monetary(string='Total Cost', compute='_compute_calcs')
    # estimated_qty = fields.Float(string='Estimated Quantity', related='consumable_list_id.product_qty', readonly=True)
    delivered_qty = fields.Float(string='Delivered Quantity', track_visibility='onchange')
    qty_added_delivery = fields.Float(string='Added to Delivery')
    picking_ids = fields.Many2many('stock.picking', string='Delivery Orders')
    partner_id = fields.Many2one(related='project_id.partner_id', string='Customer', readonly=True)
    processed = fields.Boolean(string='Processed')
    product_cost = fields.Float(related='product_id.standard_price', string="Cost")
    is_readonly= fields.Boolean(string="Readonly",default=False)

    @api.onchange('qty_added_delivery')
    def onchange_qty_added_delivery(self):
        for record in self:
            if record.qty_added_delivery > (record.product_qty - record.delivered_qty):
                raise UserError('Quantity should be lesser that total quantity')

    @api.onchange('new_item')
    def onchange_new_item(self):
        for record in self:
            record.product_id = False
            record.consumable_list_id = False

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     for record in self:
    #             record.uom_id = record.product_id.uom_id.id
    #             record.name = record.product_id.name

    @api.onchange('consumable_list_id')
    def onchange_consumable_list_id(self):
        for record in self:
            if record.consumable_list_id:
                record.product_id = record.consumable_list_id.product_id.id

    def _compute_calcs(self):
        for record in self:
            record.cost = record.product_qty * record.unit_cost
            # search([('product_id', '=', record.product_id.id), ('project_id', '=', record.project_id.id)]).mapped('product_qty'))

    def create_delivery(self):
        record_ids = self._context.get('active_ids')
        if record_ids:
            selected = self.env['project.delivery.indent'].browse(
                record_ids)
            print(selected.ids
                  )
            action = self.env.ref('project_management.project_delivery_indent_wizard').read()[0]
            action['context'] = dict(
                self.env.context,
                default_line_ids=selected.ids,
                default_partner_id=selected.mapped('partner_id.id')[0]
            )
            return action
