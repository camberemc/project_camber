from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class CRMEstimationLines(models.Model):
    _name = 'crm.estimation.line'
    _description = 'Esimation'
    _order = 'sequence,id asc'

    estimation_id = fields.Many2one('crm.estimation', string='Estimation', copy=True, auto_join=True)
    estimation_id_serv = fields.Many2one('crm.estimation', string='Estimation', copy=True, auto_join=True)
    estimation_type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Products'), ],
        default='product',
        string='Estimation Type',
        required=True)

    name = fields.Char(string='Description', required=True)

    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')

    expected_date = fields.Date(string='Expected Date')

    currency_id = fields.Many2one('res.currency', string='Currency', related='estimation_id.currency_id')

    unit_cost = fields.Monetary(string='Unit Cost')
    net_cost = fields.Monetary(string='Net Cost')
    cost = fields.Monetary(string='Total Cost')
    selling_price = fields.Monetary(string='Selling Price')

    duty_percent = fields.Float(string='Duty Percent',
                                default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                    'estimation.deafult.duty_percent'))
    freight_percent = fields.Float(string='Freight Percent',
                                   default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                       'estimation.deafult.freight_percent'))
    profit_percent = fields.Float(string='Profit Percent',
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                      'estimation.deafult.profit_percent'))
    others = fields.Float(string='Other Values', default=0.0)
    duty = fields.Float(string='Duty')
    profit = fields.Float(string='Profit')
    freight = fields.Float(string='Freight')
    landed_cost = fields.Float(string='Landed Cost')
    unit_selling_price = fields.Float(string='Unit Selling Price')

    unit_total = fields.Float(string='Unit Total Price', compute='_compute_totals', store=True)
    total_selling_service = fields.Float(string='Total Selling With Service', compute='_compute_totals', store=True)

    service_cost = fields.Float(string='Service Cost')
    service_subtotal = fields.Float(string='Service Subtotal')

    sequence = fields.Integer(string='Sequence', default=10)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('unit_selling_price', 'service_cost', 'product_qty')
    def _compute_totals(self):
        for record in self:
            record.unit_total = record.unit_selling_price + record.service_cost
            record.total_selling_service = record.unit_total * record.product_qty

    #
    @api.onchange('service_cost', 'unit_selling_price')
    def cal_change_sell(self):
        for record in self:
            if record.estimation_type == 'product':
                record.selling_price = record.unit_selling_price * record.product_qty
                record.service_subtotal = record.service_cost * record.product_qty

    @api.onchange('product_id')
    def on_change_product_id(self):
        for record in self:
            record.product_uom = record.product_id.uom_id.id
            record.name = record.product_id.default_code or record.product_id.name
            record.unit_cost = record.product_id.standard_price
            record.unit_selling_price = record.product_id.lst_price

    @api.onchange('product_qty', 'service_cost', 'unit_selling_price', 'unit_cost')
    def on_change_product(self):
        for record in self:
            if record.product_id:
                record.net_cost = record.product_qty * record.unit_cost
                record.selling_price = record.unit_selling_price * record.product_qty
                record.service_subtotal = record.service_cost * record.product_qty
                record.profit = record.selling_price - record.net_cost
                try:
                    record.profit_percent = (record.profit * 100) / record.net_cost
                except ZeroDivisionError:
                    record.profit_percent = 0


class CRMConsumableLines(models.Model):
    _name = 'crm.estimation.consumable.line'
    _description = 'Consumable Esimation'
    _order = 'sequence,id asc'

    sequence = fields.Integer(string='Sequence')
    estimation_id = fields.Many2one('crm.estimation', string='Estimation', copy=True, auto_join=True)
    project_id = fields.Many2one('project.project', string='Project', copy=False)
    name = fields.Char(string='Description', required=True)
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='estimation_id.currency_id')
    unit_cost = fields.Monetary(string='Unit Cost')
    cost = fields.Monetary(string='Total Cost', compute='_compute_calcs')

    @api.onchange('product_id')
    def change_product(self):
        for record in self:
            record.uom_id = record.product_id.uom_id.id
            record.name = record.product_id.name
            record.unit_cost = record.product_id.standard_price

    def _compute_calcs(self):
        for record in self:
            record.cost = record.product_qty * record.unit_cost


## Please create ir_config_parameter_in xml

class CRMEstimation(models.Model):
    _name = 'crm.estimation'
    _description = 'Esimations'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Estimation', required=True, default='_Draft', copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('confirmed', 'Lock'),
    ],
        default='draft',
        string='Status',
        copy=False, track_visibility='onchange')

    expected_date = fields.Date(string='Expected Date')
    estimator_id = fields.Many2one('res.users', string='Engineer', required=True, track_visibility='onchange',
                                   states=READONLY_STATES)
    lead_id = fields.Many2one('crm.lead', string='Lead', track_visibility='onchange')
    service_line_ids = fields.One2many('crm.estimation.line', 'estimation_id_serv', string='Service Estimation',
                                       states=READONLY_STATES, copy=True)
    product_line_ids = fields.One2many('crm.estimation.line', 'estimation_id', string='Product Estimation',
                                       states=READONLY_STATES, copy=True)
    consumable_line_ids = fields.One2many('crm.estimation.consumable.line', 'estimation_id',
                                          string='Consumable Estimation', states=READONLY_STATES, copy=True)
    cost = fields.Monetary(string='Cost', compute='_compute_calcs', track_visibility='onchange')
    profit = fields.Monetary(string='Profit', compute='_compute_calcs', track_visibility='onchange')
    selling_price = fields.Monetary(string='Selling Price', compute='_compute_calcs', track_visibility='onchange')
    total_selling_price = fields.Monetary(string='Project Price', compute='_compute_calcs', track_visibility='onchange')
    expense_total = fields.Monetary(string='Expense', compute='_compute_calcs', track_visibility='onchange')
    service_cost = fields.Monetary(string='Service Cost', compute='_compute_calcs', track_visibility='onchange')

    total_value = fields.Monetary(string='Total', compute='_compute_calcs', track_visibility='onchange')
    edt_id = fields.Many2one('crm.estimation.etd', string='Estimated Delivery', track_visibility='onchange',
                             states=READONLY_STATES)
    description = fields.Text(string='Description', track_visibility='onchange')
    requirement = fields.Text(string='Requirement')

    currency_id = fields.Many2one('res.currency', 'Currency', related='lead_id.company_currency', readonly=True)

    quotation_count = fields.Integer(string='Quotations', compute='_compute_count')

    service_description = fields.Text(string='Service Description')

    copy_estimation_id = fields.Many2one('crm.estimation', string='Copy Estimation')
    partner_id = fields.Many2one('res.partner', string="Customer")

    expense_line_ids = fields.One2many('estimation.expense.line', 'estimation_id', string="Expense Lines")
    amc_total = fields.Monetary(string='Amc Total', compute='_compute_calcs', track_visibility='onchange')

    def copy_estimation(self):

        def change_line(ids):
            for record in ids:
                new_record = record.copy()
                if record.estimation_type == 'service':
                    new_record.write({
                        'estimation_id_serv': self.id,
                    })
                if record.estimation_type == 'product':
                    new_record.write({
                        'estimation_id': self.id
                    })

        self.product_line_ids.unlink()
        self.service_line_ids.unlink()

        ids = self.copy_estimation_id.product_line_ids
        change_line(ids)
        ids = self.copy_estimation_id.service_line_ids
        change_line(ids)

    def _compute_count(self):
        for record in self:
            record.quotation_count = len(self.env['sale.order'].search([('estimation_id', '=', record.id)]))

    @api.depends('product_line_ids','expense_line_ids')
    def _compute_calcs(self):
        for record in self:
            service_products_price = sum(
                record.product_line_ids.filtered(lambda r: r.product_id.estimation_type == 'service').mapped(
                    'net_cost'))
            product_net_cost = sum(record.product_line_ids.mapped('net_cost'))
            product_profit = sum(record.product_line_ids.mapped('profit'))
            product_selling_price = sum(record.product_line_ids.mapped('selling_price'))
            record.amc_total = sum(
                record.product_line_ids.filtered(lambda r: r.product_id.is_amc == True).mapped(
                    'net_cost'))
            record.cost = product_net_cost - sum(
                record.product_line_ids.filtered(lambda r: r.product_id.estimation_type == 'service').mapped(
                    'net_cost')) - record.amc_total
            record.selling_price = product_selling_price
            record.profit = product_profit
            record.service_cost = sum(
                record.product_line_ids.mapped('service_subtotal')) + service_products_price
            record.total_selling_price = sum(record.product_line_ids.mapped('total_selling_service')) + sum(
                record.expense_line_ids.mapped('amount'))
            record.expense_total = sum(record.expense_line_ids.mapped('amount'))
            record.total_value = record.cost + record.expense_total + record.service_cost + record.amc_total

    def unlink(self):
        if self.name != '_Draft':
            raise UserError('Cannot delete Estimation')
        return super(CRMEstimation, self).unlink()

    def send_approval(self):
        self.write({
            'name': self.env['ir.sequence'].next_by_code('estimation.code'),
            'state': 'send'
        })

    def approval_estimation(self):
        self.write({
            'state': 'approved'
        })

    def lock_estimation(self):
        self.write({
            'state': 'confirmed'
        })

    @api.onchange('service_line_ids', 'product_line_ids')
    def _onchange_line_ids(self):
        self.state = 'draft'

    def create_quotation(self):
        # if self.service_cost > 0 and not self.service_description:
        #     raise UserError(
        #         _('Service Description is empty, please fill out service description in service details page.'))
        vals = {
            'partner_id': self.lead_id.partner_id.id,
            'partner_invoice_id': self.lead_id.partner_id.id,
            'partner_shipping_id': self.lead_id.partner_id.id,
            'estimation_id': self.id,
            'opportunity_id': self.lead_id.id,
        }
        order_id = self.env['sale.order'].create(vals)

        for line in self.product_line_ids:
            vals2 = {
                'order_id': order_id.id,
                'product_id': line.product_id.id,
                'sequence': line.sequence,
                'product_uom_qty': line.product_qty,
                'price_unit': line.unit_selling_price + line.service_cost,
                'display_type': line.display_type,
                'name': line.name,
                'service_cost': line.service_cost,
                'unit_estd_cost': line.unit_selling_price,
                'product_uom': line.product_id.uom_id.id
            }
            self.env['sale.order.line'].create(vals2)
            sequence = line.sequence
        for line in self.service_line_ids:
            sequence += 1
            vals3 = {
                'order_id': order_id.id,
                'product_id': line.product_id.id,
                'sequence': sequence,
                'product_uom_qty': line.product_qty,
                'price_unit': line.unit_selling_price,
                'display_type': line.display_type,
                'name': line.name,
                'product_uom': line.product_id.uom_id.id
            }
            self.env['sale.order.line'].create(vals3)

    def create_rejection(self):
        action = self.env.ref('sales_estimation.action_reject_estimation').read()[0]
        action['context'] = dict(
            self.env.context,
            default_estimation_id=self.id,
        )
        return action


class SaleOrderLineEst(models.Model):
    _inherit = 'sale.order.line'

    unit_estd_cost = fields.Float(string='Estimated')
    service_cost = fields.Float(string='Service')

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.unit_estd_cost != 0 or self.service_cost != 0:
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)

    @api.onchange('unit_estd_cost', 'service_cost')
    def _onchange_estimated(self):
        for record in self:
            record.price_unit = record.unit_estd_cost + record.service_cost

    def with_service_price(self):
        unit_price = self.service_cost + self.price_unit
        if self.product_id.id == int(
                self.env['ir.config_parameter'].sudo().get_param('estimation.deafult.service_product')):
            unit_price = 0
        price = unit_price * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.tax_id.compute_all(price, self.order_id.currency_id, self.product_uom_qty, product=self.product_id,
                                        partner=self.order_id.partner_shipping_id)
        return {
            's_price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
            's_price_total': taxes['total_included'],
            's_price_subtotal': taxes['total_excluded'],
            's_price_unit': unit_price
        }

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav.product_attribute_value_id not in self.product_id.product_tmpl_id._get_valid_product_attribute_values():
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        result = {'domain': domain}

        name = self.get_sale_order_line_multiline_description_sale(product)

        vals.update(name=name)

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
            vals['unit_estd_cost'] = 0
            vals['service_cost'] = 0
        # self.update(vals)

        title = False
        message = False
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s") % product.name
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        return result


class ExpenseLines(models.Model):
    _name = 'estimation.expense.line'
    _description = 'Estimated Expense'
    _order = 'id desc'

    name = fields.Char(string="Expense Name")
    amount = fields.Float(string="Amount")
    estimation_id = fields.Many2one('crm.estimation', string='Estimation')


class EstimatedDeleivery(models.Model):
    _name = 'crm.estimation.etd'
    _description = 'Estimated Delivery'
    _order = 'id desc'

    name = fields.Char(string="Name")
    days = fields.Integer(string="Days")


class EstimationSaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    estimation_id = fields.Many2one('crm.estimation', string='Estimation')

    total_service_cost = fields.Monetary(string='Service Cost', compute='_compute_service_cost')

    @api.depends('order_line')
    def _compute_service_cost(self):
        for record in self:
            total_service_cost = 0
            for line in record.order_line:
                total_service_cost += line.service_cost * line.product_uom_qty
            record.total_service_cost = total_service_cost


class ProjectExtentedConsumable(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    project_line_consume_ids = fields.One2many('crm.estimation.consumable.line', 'project_id',
                                               string='Project Consumables')
