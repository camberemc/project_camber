# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd. - ©
# Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_is_zero, float_compare
from itertools import groupby


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('amount_untaxed', 'amount_tax', 'discount_type', 'discount_rate')
    def _amount_all(self):
        res = super(SaleOrder, self)._amount_all()
        for order in self:
            order.amount_grand = order.amount_untaxed
            order.amount_total_with_discount = order.amount_grand
            if (order.discount_type == 'percent'):
                order.amount_discount = round((order.amount_grand * order.discount_rate / 100), 2)
            elif (order.discount_type == 'amount'):
                order.amount_discount = order.discount_rate
            if (order.amount_grand >= order.amount_discount):
                # order.amount_tax =
                order.amount_total_with_discount = order.amount_grand - order.amount_discount
                # tax_amount = 0
                # if self.order_line:
                #     for line in self.order_line:
                #         if line.price_tax:
                #             tax_amount = tax_amount + line.price_tax
                # print(tax_amount)
                # print(round((order.amount_total_with_discount * 5) / 100, 2))
                # order.amount_tax = tax_amount

                if order.amount_tax:
                    order.amount_tax = round((order.amount_total_with_discount * 5) / 100, 2)
                else:
                    order.amount_tax = 0

                order.amount_total = round((order.amount_untaxed + order.amount_tax) - order.amount_discount, 2)
        return res

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], 'Discount Type', readonly=True,
                                     states={'draft': [('readonly', False)]})
    discount_rate = fields.Float('Discount Rate', readonly=True, states={'draft': [('readonly', False)]})
    discount_narration = fields.Char('Discount Narration', readonly=True, states={'draft': [('readonly', False)]})
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                  readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'),
                                   store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_grand = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Float(string='Net Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_amount_all')
    amount_total_with_discount = fields.Float('Total', readonly=True)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.amount_discount > 0:
            res.update({
                'discount_type': self.discount_type or '',
                'discount_rate': self.discount_rate or '',
                'discount_narration': self.discount_narration or '',
                'analytic_id': self.analytic_id.id or '',
                'amount_grand': self.amount_grand,
                'amount_discount': self.amount_discount,
                # 'amount_tax':self.amount_tax,
                # 'invoice_line_ids': [(0, 0, {
                #     'price_unit': -self.amount_discount,
                #     'debit': self.amount_discount,
                #     'credit': 0,
                #     'quantity': 1,
                #     'amount_currency': -self.amount_discount,
                #     'currency_id': self.currency_id.id if self.currency_id != self.company_id.currency_id else False,
                #     'account_id': int(self.env['ir.config_parameter'].get_param
                #                       ('tis_sales_purchase_global_discount.def_discount_sales_account_id')),
                #     'analytic_account_id': self.analytic_id.id if self.analytic_id else '',
                #     'partner_id': self.partner_id.id,
                #     'exclude_from_invoice_tab': True
                # })]
            })
        return res
