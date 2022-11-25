# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd. - ©
# Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ast import literal_eval


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.depends('amount_untaxed', 'amount_tax', 'discount_type', 'discount_rate', 'order_line.price_total')
    def _amount_all(self):
        res = super(PurchaseOrder, self)._amount_all()
        for order in self:
            order.amount_grand = order.amount_untaxed
            order.amount_total_with_discount = order.amount_grand
            if (order.discount_type == 'percent'):
                order.amount_discount = round((order.amount_grand * order.discount_rate / 100), 2)
            elif (order.discount_type == 'amount'):
                order.amount_discount = order.discount_rate
            if (order.amount_grand >= order.amount_discount):
                order.amount_total_with_discount = order.amount_grand - order.amount_discount
                if order.amount_tax:
                    order.amount_tax = round((order.amount_total_with_discount * 5) /100,2)
                else:
                    order.amount_tax = 0
                order.amount_total = round((order.amount_untaxed + order.amount_tax) - order.amount_discount,2)
        return res

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], 'Discount Type',
                                     )
    discount_rate = fields.Float('Discount Rate')
    discount_narration = fields.Char('Discount Narration')
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                  )
    amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'),
                                   store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_grand = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Float(string='Net Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all')
    amount_total_with_discount = fields.Float('Total', readonly=True)

    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['discount_type'] = self.discount_type
        res['discount_rate'] = self.discount_rate
        res['discount_narration'] = self.discount_narration
        res['analytic_id'] = self.analytic_id
        res['amount_discount'] = self.amount_discount
        if self.amount_discount:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            purchase_discount_account = self.env['ir.config_parameter'].sudo().get_param(
                'tis_sales_purchase_global_discount.def_discount_purchase_account_id')
            default_discount_account = False
            if not purchase_discount_account:
                raise UserError(
                    _('Please Configure  Purchase Discount Account.'))
            else:
                default_discount_account = literal_eval(
                    ICPSudo.get_param('tis_sales_purchase_global_discount.def_discount_purchase_account_id',
                                      default='False'))
            if self.amount_tax:
                tax_id = self.order_line.mapped('taxes_id')[0]
                invoice_line_ids = [(0, 0, {
                    'name': 'Discount',
                    'price_unit': -self.amount_discount,
                    'quantity': 1,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'account_id': default_discount_account,
                    'partner_id': self.partner_id.id,
                    'tax_ids': [(6, 0, [tax_id.id])],
                    'exclude_from_invoice_tab': True,
                    'is_discount': True
                })]
            else:
                invoice_line_ids = [(0, 0, {
                    'name': 'Discount',
                    'price_unit': -self.amount_discount,
                    'quantity': 1,
                    'move_id': self.id,
                    'currency_id': self.currency_id.id,
                    'account_id': default_discount_account,
                    'partner_id': self.partner_id.id,
                    # 'tax_ids': [(6, 0, [19])],
                    'exclude_from_invoice_tab': True,
                    'is_discount': True
                })]

            res['invoice_line_ids']=invoice_line_ids
        return res



