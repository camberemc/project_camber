# -*- coding: utf-8 -*-
# This module and its content is copyright of Technaureus Info Solutions Pvt. Ltd. - ©
# Technaureus Info Solutions Pvt. Ltd 2020. All rights reserved.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from ast import literal_eval


class AccountMove(models.Model):
    _inherit = 'account.move'

    # @api.depends(
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
    #     'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
    #     'line_ids.debit',
    #     'line_ids.credit',
    #     'line_ids.currency_id',
    #     'line_ids.amount_currency',
    #     'line_ids.amount_residual',
    #     'line_ids.amount_residual_currency',
    #     'line_ids.payment_id.state',
    #     'line_ids.full_reconcile_id',
    #     'discount_type',
    #     'discount_rate'
    # )
    # def _compute_amount(self):
    #     for rec in self:
    #         res = super(AccountMove, self)._compute_amount()
    #         rec.amount_grand = rec.amount_untaxed
    #         if (rec.discount_type == 'percent'):
    #             rec.amount_discount = round((rec.amount_grand * rec.discount_rate / 100), 2)
    #         elif (rec.discount_type == 'amount'):
    #             rec.amount_discount = rec.discount_rate
    #         if (rec.amount_grand >= rec.amount_discount):
    #             rec.amount_total_with_discount = round(rec.amount_grand - rec.amount_discount, 2)
    #             amount_untaxed_signed = rec.amount_untaxed
    #             rec.amount_total = round((rec.amount_untaxed - rec.amount_discount) + rec.amount_tax, 2)
    #         else:
    #             amount_untaxed_signed = rec.amount_untaxed
    #         if rec.currency_id and rec.company_id and rec.currency_id != rec.company_id.currency_id:
    #             currency_id = rec.currency_id.with_context(date=rec.invoice_date)
    #             amount_untaxed_signed = currency_id.compute(rec.amount_untaxed, rec.company_id.currency_id)
    #         sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
    #         rec.amount_total_signed = rec.amount_total * sign
    #         rec.amount_untaxed_signed = amount_untaxed_signed * sign
    #         return res
    #
    # discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], 'Discount Type',
    #                                  readonly=True, states={'draft': [('readonly', False)]})
    # discount_rate = fields.Float('Discount Rate', readonly=True, states={'draft': [('readonly', False)]})
    # discount_narration = fields.Char('Discount Narration', readonly=True, states={'draft': [('readonly', False)]})
    # # analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
    # #                               readonly=True, states={'draft': [('readonly', False)]})
    # amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'),
    #                                readonly=True,  track_visibility='always')
    # amount_grand = fields.Float(string='Total', digits=dp.get_precision('Account'),
    #                             store=True, readonly=True, track_visibility='always')
    # amount_total = fields.Float(string='Net Total', digits=dp.get_precision('Account'),
    #                             store=True, readonly=True)
    # amount_total_with_discount = fields.Float('Total', readonly=True)

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id',
        # 'discount_type',
        # 'discount_rate'
    )
    def _compute_amount(self):
        for rec in self:
            res = super(AccountMove, self)._compute_amount()
            rec.amount_grand = rec.amount_untaxed + rec.amount_tax
            if (rec.discount_type == 'percent'):
                rec.amount_discount = round((rec.amount_grand * rec.discount_rate / 100), 2)
            elif (rec.discount_type == 'amount'):
                rec.amount_discount = rec.discount_rate
            if (rec.amount_grand >= rec.amount_discount):
                rec.amount_total = rec.amount_grand - rec.amount_discount
            amount_untaxed_signed = rec.amount_untaxed
            if rec.currency_id and rec.company_id and rec.currency_id != rec.company_id.currency_id:
                currency_id = rec.currency_id.with_context(date=rec.invoice_date)
                amount_untaxed_signed = currency_id.compute(rec.amount_untaxed, rec.company_id.currency_id)
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_signed = rec.amount_total * sign
            rec.amount_untaxed_signed = amount_untaxed_signed * sign
            if rec.amount_discount:
                rec.amount_total_with_discount = rec.amount_untaxed - rec.amount_discount
            else:
                rec.amount_total_with_discount = rec.amount_untaxed

            return res

    discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')], 'Discount Type',
                                     readonly=True, states={'draft': [('readonly', False)]})
    discount_rate = fields.Float('Discount Rate', readonly=True, states={'draft': [('readonly', False)]})
    discount_narration = fields.Char('Discount Narration', readonly=True, states={'draft': [('readonly', False)]})
    analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                  readonly=True, states={'draft': [('readonly', False)]})
    amount_discount = fields.Float(string='Discount', digits=dp.get_precision('Account'),
                                   readonly=True, compute='_compute_amount', track_visibility='always')
    amount_grand = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    amount_total = fields.Float(string='Net Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_compute_amount')
    amount_total_with_discount = fields.Float('Total', store=True, readonly=True, compute='_compute_amount')

    def apply_discount(self):

        line_id = self.line_ids.filtered(lambda x: x.is_discount)
        line_id.with_context({
            'check_move_validity': False
        }).unlink()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        sale_discount_account = self.env['ir.config_parameter'].sudo().get_param(
            'tis_sales_purchase_global_discount.def_discount_sales_account_id')
        purchase_discount_account = self.env['ir.config_parameter'].sudo().get_param(
            'tis_sales_purchase_global_discount.def_discount_purchase_account_id')
        default_discount_account = False
        if not sale_discount_account or not purchase_discount_account:
            raise UserError(
                _('Please Configure Sales & Purchase Discount Account.'))
        if self.move_type in ('in_invoice', 'in_refund'):
            default_discount_account = literal_eval(
                ICPSudo.get_param('tis_sales_purchase_global_discount.def_discount_purchase_account_id',
                                  default='False'))
        elif self.move_type in ('out_invoice', 'out_refund'):
            default_discount_account = literal_eval(
                ICPSudo.get_param('tis_sales_purchase_global_discount.def_discount_sales_account_id',
                                  default='False'))
        if self.amount_tax:
            tax_id = self.invoice_line_ids.mapped('tax_ids')[0]
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
        self.write({
            'invoice_line_ids': invoice_line_ids
        })
        super(AccountMove, self)._onchange_recompute_dynamic_lines()
        self.amount_discount = self.discount_rate
        self.amount_total_with_discount = self.amount_untaxed - self.discount_rate
        self.amount_total = self.amount_total_with_discount + self.amount_tax


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_discount = fields.Boolean(string="Discount Applied")
