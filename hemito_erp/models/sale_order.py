# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning

from odoo.addons import decimal_precision as dp

class SaleOrderExtend(models.Model):
    _inherit = "sale.order"

    delivery_term_id = fields.Many2one('delivery.terms', string="Delivery Terms")
    subject = fields.Text(string="Subject")
    reference = fields.Char(string="Reference")
    remarks = fields.Text(string="Remarks")
    warranty = fields.Char(string="Warranty")
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, compute='_compute_so_name',
                       store=True)
    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending of Approval'),
        ('draft_quot', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    other_expense = fields.Float(string="Other Expense")
    cost = fields.Float(string="Total Unit Cost", compute='_get_total_amounts', store=True)
    total_cost = fields.Float(string="Total Cost", compute='_get_total_amounts', store=True)
    cost_with_expense = fields.Float(string="Total Cost with Expense", compute='_get_total_amounts', store=True)
    margin_value = fields.Float(string="Total Margin Value", compute='_get_total_amounts', store=True)
    sales_price = fields.Float(string="Total Cost with margin", compute='_get_total_amounts', store=True)

    @api.depends('other_expense', 'order_line')
    def _get_total_amounts(self):
        for rec in self:
            rec.cost = sum(rec.order_line.mapped('cost'))
            rec.total_cost = sum(rec.order_line.mapped('total_cost'))
            rec.cost_with_expense = sum(rec.order_line.mapped('cost_with_expense'))
            rec.margin_value = sum(rec.order_line.mapped('margin_value'))
            rec.sales_price = sum(rec.order_line.mapped('sales_price'))

    def release_quotation(self):
        self.write({
            'state': 'draft'
        })

    def approve_quotation(self):
        self.write({
            'state': 'draft_quot'
        })

    def send_approve_quotation(self):
        self.write({
            'state': 'pending'
        })

    @api.onchange('order_line')
    def _on_change_order_line(self):
        if self.state in ('draft_quot', 'send', 'sale'):
            raise UserError(_('You have no access to edit this quotation'))

    def write(self, values):
        if 'order_line' in values:
            self._on_change_order_line()
        return super(SaleOrderExtend, self).write(values)

    @api.depends('opportunity_id')
    def _compute_so_name(self):
        for rec in self:
            rec.name = rec.opportunity_id.seq
            if rec.revision_id:
                rec.name = rec.revision_id.name + ' R' + str(rec.revision_id.last_code)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft_quot').with_context(tracking_disable=True).write(
                {'state': 'sent'})
        return super(SaleOrderExtend, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def action_confirm_expense(self):
        for rec in self:
            if rec.other_expense:
                if rec.order_line:
                    total = sum(rec.order_line.mapped("total_cost"))
                    for line in rec.order_line:
                        line.other_expense = (line.total_cost * rec.other_expense) / total
                        line.cost_with_expense = line.other_expense + line.total_cost
                        if line.margin_per:
                            line.margin_value = line.cost_with_expense / (1 - line.margin_per / 100) - line.cost_with_expense
                            line.sales_price = line.cost_with_expense + line.margin_value
            else:
                for line in rec.order_line:
                    line.other_expense = 0.00
                    line.cost_with_expense = line.total_cost
                    if line.margin_per:
                        line.margin_value = line.total_cost / (1 - line.margin_per / 100) - line.total_cost
                        line.sales_price = line.total_cost + line.margin_value

    def _prepare_confirmation_values(self):
        return {
            'state': 'sale',
        }
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderExtend, self)._prepare_invoice()
        for rec in self.order_line:
            if rec.product_id.default_code == 'DISC':
                invoice_vals.update({
                    'invoice_line_ids': [(0, 0, {
                        'display_type': rec.display_type,
                        'sequence': rec.sequence,
                        'name': rec.name,
                        'product_id': rec.product_id.id,
                        'product_uom_id': rec.product_uom.id,
                        'quantity': rec.product_uom_qty,
                        'discount': rec.discount,
                        'price_unit': rec.price_unit,
                        'tax_ids': [(6, 0, rec.tax_id.ids)],
                        'analytic_account_id': rec.order_id.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                        'sale_line_ids': [(4, rec.id)],
                    })]
                })
        return invoice_vals


class SaleOrderLineExtend(models.Model):
    _inherit = "sale.order.line"


    cost =  fields.Float(string='Unit Cost', digits=dp.get_precision('Sale Order Unit Cost'))

    
    total_cost = fields.Float(string="Total Cost", compute='_compute_cost_amount')
    other_expense = fields.Float(string="Other Expense")
    cost_with_expense = fields.Float(string="Total Cost with Expense")
    margin_per = fields.Float(string="Margin(%)")
    margin_value = fields.Float(string="Margin Value", store=True)
    sales_price = fields.Float(string="Total Cost with margin", store=True)


    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLineExtend, self).product_id_change()
        self.cost = self.product_id.standard_price
        return res

    @api.depends('cost', 'product_id', 'product_uom_qty')
    def _compute_cost_amount(self):
        for rec in self:
            rec.total_cost = False
            if rec.cost:
                rec.total_cost = rec.cost * rec.product_uom_qty

    @api.onchange('margin_per', 'total_cost', 'cost_with_expense')
    def margin_per_change(self):
        if self.margin_per:
            if self.cost_with_expense:
                self.margin_value = self.cost_with_expense / (1 - self.margin_per / 100) - self.cost_with_expense
                # self.margin_value = (self.cost_with_expense * self.margin_per) / 100
                # =K9 / (1 - 0.15) - K9
                self.sales_price = self.cost_with_expense + self.margin_value
            elif self.total_cost:
                self.margin_value = self.total_cost / (1 - self.margin_per / 100) - self.total_cost
                # self.margin_value = (self.total_cost * self.margin_per) / 100
                self.sales_price = self.total_cost + self.margin_value
