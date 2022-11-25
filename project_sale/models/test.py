from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime, date
from odoo.addons import decimal_precision as dp

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class ProjectExtented(models.Model):
    _name = 'project.project'
    _inherit = ['project.project', 'portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    code = fields.Char(string='Project Code', store=True,
                       default="Drafted", copy=False)

    description = fields.Text(string='Description')

    state = fields.Selection([
        ('draft', 'New Project'), ('ongoing', 'Ongoing'), ('completed', 'Completed'),
    ], string='Status', readonly=True,
        copy=False, index=True, track_visibility='onchange', default='draft')
    is_approve_request = fields.Boolean(string="Approval Request", default=False, copy=False)
    is_approved = fields.Boolean(string="Approved", default=False, copy=False)

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    project_line_service_ids = fields.One2many('project.project.orderline', 'project_id', string='Project Services')
    project_line_product_ids = fields.One2many('project.project.orderline', 'project_id', string='Project Products')
    # project_estimation_sale_line_ids = fields.One2many('project.sales.line', 'project_id', string='Estimation Sales Line')
    project_indent_ids = fields.One2many('project.delivery.indent', 'project_id', string='Delivery Indents')
    project_cheque_ids = fields.One2many('project.project.cheque', 'project_id', string='Security Cheques')
    project_return_ids = fields.One2many('stock.inventory.return.line', 'project_id', string='Inventory Return',
                                         domain=[('state', '=', 'confirm')])
    retention_date = fields.Date(string='Retention Date')

    total_expense = fields.Float(string="Expense", readonly=True)
    total_income = fields.Float(string="Invoiced", readonly=True)
    total_material_cost = fields.Float(string="Material Cost", readonly=True)
    total_profit = fields.Float(string="Profit", readonly=True)
    total_profit_per = fields.Float(string="Profit (%)", readonly=True)
    contract_amount = fields.Float(string="Contract Amount")
    project_inventory_ids = fields.One2many('stock.move', 'project_id',
                                            string='Inventory Lines')
    total_sale_value = fields.Float(string="Project Value")

    def update_project_summary(self):
        for rec in self:
            rec.total_material_cost = 0
            rec.total_expense = 0
            rec.total_income = 0
            journal_id = self.env['account.journal'].search([('name', 'like', 'Customer Invoice')], limit=1)
            # journal_ids = self.env['account.journal'].search([('name', '!=', 'Customer Invoices')])
            expense = self.env['account.move.line'].search(
                [('project_id', '=', rec.id), ('journal_id', '!=', journal_id.id), ('move_id.state', '=', 'posted')])
            journal_id = self.env['account.journal'].search([('name', 'like', 'Customer Invoice')], limit=1)
            income = self.env['account.move'].search(
                [('project_id', '=', rec.id), ('journal_id', '=', journal_id.id), ('state', '=', 'posted')])
            if rec.project_line_product_ids:
                for line in rec.project_line_product_ids:
                    if line.qty_delivered:
                        rec.total_material_cost = rec.total_material_cost + (line.qty_delivered * line.cost)
            if rec.project_indent_ids:
                for line in rec.project_indent_ids:
                    if line.delivered_qty:
                        rec.total_material_cost = rec.total_material_cost + (line.delivered_qty * line.product_cost)

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

    def action_expense_entries(self):
        journal_id = self.env['account.journal'].search([('name', 'like', 'Customer Invoice')])
        action = {
            'name': _("Expense Entries"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move.line',
            'domain': [('project_id', '=', self.id), ('journal_id', 'not in', journal_id.ids)]
        }
        return action

    def action_income_entries(self):
        journal_id = self.env['account.journal'].search([('name', 'like', 'Customer Invoice')])
        action = {
            'name': _("Income Entries"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'domain': [('project_id', '=', self.id), ('journal_id', 'in', journal_id.ids)]
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

    def action_project_order_lines(self):
        action = {
            'name': _("Products"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'project.project.orderline',
            'domain': [('project_id', '=', self.id)]
        }
        return action

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
        self.write({
            'state': 'ongoing',
            'code': code,
        })

    def send_approval(self):
        users = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('project_sale.group_show_send_approval').id)])
        if users:
            for user in users:
                self.env['mail.activity'].create({
                    'summary': 'Approval Request',
                    'date_deadline': date.today(),
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'project.project')], limit=1).id,
                    'res_id': self.id,
                    'user_id': user.id
                })
        self.write({
            'is_approve_request': True
        })

    def button_approval(self):
        self.write({
            'is_approved': True
        })

    # def reject_approval(self):
    #     self.write({
    #         'state': 'ongoing'
    #     })
    # def create_rejection(self):
    #     action = self.env.ref('project_sale.action_reject_project').read()[0]
    #     action['context'] = dict(
    #         self.env.context,
    #         default_project_id=self.id,
    #     )
    #     return action

    def complete_project(self):
        if self.retention_date:
            self.write({
                'state': 'completed',
            })
        else:
            raise UserError('Retension date not Added. Please fill out the retension date and close the project.')

    # def close_project(self):
    #     if self.retention_date:
    #         self.write({
    #             'state': 'close',
    #         })
    #     else:
    #         raise UserError('Retension date not Added. Please fill out the retension date and close the project.')

    def unlink(self):
        if self.code != 'Drafted':
            raise UserError('Cannot delete Project')
        return super(ProjectExtented, self).unlink()


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
            record.total_shop_qty = sum(record.project_order_line_ids.mapped('quantity'))


class ProjectOderLine(models.Model):
    _name = "project.project.orderline"
    _description = "Project Order Lines"
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    sequence = fields.Integer(string='Sequence')

    project_sales_line_id = fields.Many2one('project.sales.line', string='Project Estimation Lines',
                                            track_visibility='onchange')

    est_product_qty = fields.Float(related="project_sales_line_id.product_qty", store=True, string='Tender Quantity',
                                   readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Waiting Approval'),
        ('level_1', 'Waiting L2'),
        ('confirm', 'Confirmed')
    ], string='Status', default='draft', copy=False, track_visibility='onchange')

    name = fields.Text(string='Description', required=True, track_visibility='onchange')
    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    uom_id = fields.Many2one(related='product_id.uom_id', string='Unit of Measure', readonly=True,
                             track_visibility='onchange')

    product_uom_qty = fields.Float(string='Product Quantity')

    qty_added = fields.Float(string='Added +')
    qty_added_delivery = fields.Float(string='Added +')
    order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    qty_on_hand = fields.Float(string='On Hand', compute='_compute_qty', track_visibility='onchange')
    qty_purchased = fields.Float(string='Purchased Quantity', compute='_compute_qty', track_visibility='onchange')
    qty_balance = fields.Float(string='Balance Purchase', compute='_compute_qty', track_visibility='onchange')

    order_id = fields.Many2one(related='order_line_id.order_id', store=True, string='Sale Order')

    partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer')

    shop_qty = fields.Float(string='Shop Quantity', track_visibility='onchange')
    dcd_qty = fields.Float(string='DCD Quantity', track_visibility='onchange')

    indented_qty = fields.Float(string='Indented Quantity', compute='_compute_indented_qty', store=True,
                                track_visibility='onchange')
    indented_qty_added = fields.Float(string='Added +')
    intented_date = fields.Date(string='Intented Date', track_visibility='onchange')
    qty_pending = fields.Float(string='Pending Quantity', compute='_compute_pending_qty', store=True,
                               track_visibility='onchange')

    qty_delivered = fields.Float(string='Delivered Qty', compute='_compute_qty', track_visibility='onchange')
    qty_balance_delivery = fields.Float(string='Balance Delivery', compute='_compute_qty', track_visibility='onchange')

    project_purchase_ids = fields.One2many('project.purchase.line', 'project_order_line_id', string='Project Purchases')
    project_delivery_ids = fields.One2many('project.delivery.line', 'project_order_line_id', string='Project Delivery')
    project_indent_request_ids = fields.One2many('project.indent.request.line', 'project_order_line_id',
                                                 string='Project Indents')

    dcd_access = fields.Boolean(string='DCD Access', compute='_compute_access')
    shop_access = fields.Boolean(string='Shop Access', compute='_compute_access')

    remarks = fields.Text(related='project_sales_line_id.remarks', readonly=True, store=True, string='Remarks',
                          track_visibility='onchange')

    cost = fields.Float(string="Cost", related='product_id.standard_price')
    quantity = fields.Float(string='Quantity', track_visibility='onchange')
    qty_added_inventory_return = fields.Float(string='Added +')

    def _compute_access(self):
        for record in self:
            record.dcd_access = False
            record.shop_access = False
            if self.env.user.has_group('project_sale.group_edit_dcd'):
                record.dcd_access = True

            if self.env.user.has_group('project_sale.group_edit_shop'):
                record.shop_access = True

    purchase_status = fields.Selection([
        ('pending', 'Ongoing'),
        ('completed', 'Completed')], default='pending', compute='_compute_status', store=True)

    @api.onchange('indented_qty_added')
    def _onchange_indented_qty_added(self):
        for record in self:
            if record.indented_qty_added > (record.quantity - record.indented_qty):
                raise UserError('Cannot request quantity greater than shop quantity and previously indented quantity')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            record.name = record.product_id.name

    @api.depends('project_indent_request_ids')
    def _compute_indented_qty(self):
        for record in self:
            record.indented_qty = sum(record.project_indent_request_ids.mapped('qty'))

    @api.depends('indented_qty', 'qty_delivered')
    def _compute_pending_qty(self):
        for record in self:
            record.qty_pending = record.indented_qty - record.qty_delivered

    @api.depends('project_purchase_ids')
    def _compute_status(self):
        for record in self:
            if record.qty_purchased == record.product_uom_qty:
                record.purchase_status = 'completed'
            else:
                record.purchase_status = 'pending'

    def _compute_price(self):
        for record in self:
            record.unit_sell_price = record.order_line_id.price_unit
            record.total_sell_price = record.order_line_id.price_subtotal
            record.total_cost = sum(record.project_purchase_ids.mapped('price_subtotal'))

    def _compute_qty(self):
        for record in self:
            record.qty_purchased = sum(record.project_purchase_ids.mapped('qty'))
            record.qty_balance = record.quantity - record.qty_purchased
            record.qty_delivered = sum(record.project_delivery_ids.mapped('qty'))
            record.qty_balance_delivery = record.quantity - record.qty_delivered
            record.qty_on_hand = record.product_id.qty_available

    @api.onchange('qty_added')
    def _check_quantity_purchased(self):
        for record in self:
            if record.qty_added > record.qty_balance:
                raise Warning(
                    _('You cannot create purchase order with excess quanity for each projects. To purchase more please create seperate purchase order'))

            # if record.state != 'confirm':
            #     raise Warning(_(record.state))

            # raise Warning(_('Shop quantity is not confirmed, so you cannot create purchase for this item, remove the item from the list and follow the approval workflow'))

    @api.onchange('qty_added_delivery')
    def _check_quantity_delivered(self):
        for record in self:
            if record.qty_added_delivery > record.qty_balance_delivery - record.indented_qty:
                raise Warning(
                    _('You cannot create delivery order with excess quanity or without an indent. To deliver more please create seperate delivery order'))
            if record.qty_added_delivery > record.qty_on_hand:
                raise Warning(_('Cannot deliver more than stock quantity. Purchase more..'))

    @api.onchange('qty_added_inventory_return')
    def _check_quantity_return(self):
        for record in self:
            if record.qty_added_inventory_return > record.qty_balance_delivery :
                raise Warning(
                    _('You cannot create return delivery with excess delivered quantity'))

    # if record.state != 'confirm':
    #     raise Warning(_('Shop quantity is not confirmed, so you cannot create delivery for this item, remove the item from the list and please follow the approval workflow'))


def send_approval(self):
    self.write({
        'state': 'send'
    })


def l1_approval(self):
    self.write({
        'state': 'level_1'
    })


def confirm_state(self):
    self.write({
        'state': 'confirm'
    })

    # subject = self.product_id.name + ' Approved for project : ' + self.project_id.name
    # channel_id = self.env['mail.channel'].browse(22)
    # needaction_partner_ids = channel_id.channel_last_seen_partner_ids.mapped('partner_id.id')
    #
    # message = {
    #     'record_name': 'Quote Request',
    #     'message_type': 'notification',
    #     'email_from': self.env.user.partner_id.email,
    #     "subtype_id": self.env.ref("mail.mt_comment").id,
    #     'body': subject,
    #     'subject': subject,
    #     'needaction_partner_ids': [(6, 0, needaction_partner_ids)],
    #     'model': 'mail.channel',
    #     'channel_ids': [(4, channel_id.id)],
    # }
    #
    # self.env['mail.message'].sudo().create(message)


def set_draft(self):
    self.write({
        'state': 'draft'
    })


def create_delivery(self):
    record_ids = self._context.get('active_ids')
    if record_ids:
        selected = self.env['project.project.orderline'].browse(
            record_ids)
        for record in selected:
            if not record.project_id.is_approved:
                raise UserError('You Have No Permission to Create Delivery')

        action = self.env.ref('project_sale.project_delivery_form_wizard').read()[0]
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
        for record in selected:
            if not record.project_id.is_approved:
                # if record.project_id.state != 'approved':
                raise UserError('You have No Permission to Create Purchase')
        action = self.env.ref('project_sale.project_purchase_form_wizard_new').read()[0]
        action['context'] = dict(
            self.env.context,
            default_orderline_ids=selected.ids,
        )
        return action


class ProjectPurchaseLines(models.Model):
    _name = "project.purchase.line"
    _description = "Project Purchase Line"
    _order = 'id desc'

    project_order_line_id = fields.Many2one('project.project.orderline', string='Project Order Line')
    project_id = fields.Many2one(string='Project', related='project_order_line_id.project_id')

    order_id = fields.Many2one('purchase.order', string='Purchase Order', related='order_line_id.order_id',
                               readonly=True)
    order_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    price_unit = fields.Float(string='Purchase Cost', compute='_compute_cost')

    qty = fields.Float(string='Purchased Qty')
    price_subtotal = fields.Float(string='Total Cost', compute='_compute_cost')
    state = fields.Selection(related='order_line_id.order_id.state', string='State')

    date_planned = fields.Datetime(string='Expected Date', related='order_line_id.date_planned')

    def _compute_cost(self):
        for record in self:
            record.price_unit = record.order_line_id.price_unit
            record.price_subtotal = record.price_unit * record.qty


class ProjectDeliveryines(models.Model):
    _name = "project.delivery.line"
    _description = "Project Delivery Line"
    _order = 'id desc'

    project_order_line_id = fields.Many2one('project.project.orderline', string='Project Order Line')

    picking_id = fields.Many2one('stock.picking', string='Delivery Order', related='move_line_id.picking_id',
                                 readonly=True)
    move_line_id = fields.Many2one('stock.move', string='Delivery Order Line')
    qty = fields.Float(string='Delivered Qty')
    state = fields.Selection(related='move_line_id.picking_id.state', string='State')
    date_planned = fields.Datetime(string='Expected Date')


class ProjectIndentRequests(models.Model):
    _name = "project.indent.request.line"
    _description = "Project Indent Request"
    _order = 'id desc'

    project_order_line_id = fields.Many2one('project.project.orderline', string='Project Order Line')
    user_id = fields.Many2one('res.users', string='Requested By')
    requested_date = fields.Datetime(string='Requested Date', default=lambda self: fields.datetime.now())
    date = fields.Date(string='Required Date')
    qty = fields.Float(string='Requested Qty')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Status', default='draft')


class ProjectDeliveryIndent(models.Model):
    _name = "project.delivery.indent"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    name = fields.Char(string='Description', required=True)
    new_item = fields.Boolean(string='New Item')
    consumable_list_id = fields.Many2one('crm.estimation.consumable.line', string='Estimated Product')
    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0,
                               track_visibility='onchange')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    currency_id = fields.Many2one('res.currency', string='Currency', related='project_id.currency_id')
    unit_cost = fields.Monetary(string='Unit Cost')
    cost = fields.Monetary(string='Total Cost', compute='_compute_calcs')
    estimated_qty = fields.Float(string='Estimated Quantity', related='consumable_list_id.product_qty', readonly=True)
    delivered_qty = fields.Float(string='Delivered Quantity', track_visibility='onchange')
    qty_added_delivery = fields.Float(string='Added to Delivery')
    picking_ids = fields.Many2many('stock.picking', string='Delivery Orders')
    partner_id = fields.Many2one(related='project_id.partner_id', string='Customer', readonly=True)
    processed = fields.Boolean(string='Processed')
    product_cost = fields.Float(related='product_id.standard_price', string="Cost")
    is_readonly = fields.Boolean(string="Readonly", default=False)
    quantity_on_hand = fields.Float(related='product_id.qty_available', string="Quantity on Hand")

    @api.onchange('qty_added_delivery')
    def onchange_qty_added_delivery(self):
        for record in self:
            if record.qty_added_delivery > (record.product_qty - record.delivered_qty):
                raise UserError('Quantity should be lesser that total quantity')
            elif record.qty_added_delivery > record.quantity_on_hand:
                raise UserError('Quantity should not exceed the on hand quantity')

    @api.onchange('new_item')
    def onchange_new_item(self):
        for record in self:
            record.product_id = False
            record.consumable_list_id = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for record in self:
            if record.product_id:
                record.uom_id = record.product_id.uom_id.id
                record.name = record.product_id.name

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
            action = self.env.ref('project_sale.project_delivery_indent_wizard').read()[0]
            action['context'] = dict(
                self.env.context,
                default_line_ids=selected.ids,
                default_partner_id=selected.mapped('partner_id.id')[0]
            )
            return action


class ProjectCheque(models.Model):
    _name = "project.project.cheque"
    _order = 'id desc'

    project_id = fields.Many2one('project.project', string='Project', copy=False)
    partner_id = fields.Many2one(related='project_id.partner_id', string='Customer', readonly=True)
    name = fields.Char(string='Cheque Number', required=True)
    cheque_date = fields.Date(string='Date')
    cheque_amount = fields.Float(string='Amount')
    status = fields.Selection([
        ('issued', 'Issued'),
        ('collected', 'Collected'),
        ('claimed', 'Claimed')
    ], string='Cheque Details')
    note = fields.Text(string='Note')
