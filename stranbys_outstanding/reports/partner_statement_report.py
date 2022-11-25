# -*- coding: utf-8 -*-

import base64
import io

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import date, datetime


class PartnerStatementReport(models.AbstractModel):
    _name = 'report.stranbys_outstanding.partner_statement_templates'
    _description = "Partner Statement Report "

    def _get_report_values(self, docids, data=None, sessions=False):
        partner_statement_wizard = self.env['partner.statements.wizard'].browse(
            docids)
        wiz = self.env['partner.statements.wizard'].browse(
            docids)

        data = []
        pdc_data = []


        def get_bucket_data(ids, day_start=False, day_end=False):
            if day_start:
                sta_date = date.today() + relativedelta(days=-day_start)
                ids = ids.filtered(lambda r: r.invoice_date <= sta_date)
            if day_end:
                end_date = date.today() + relativedelta(days=-day_end)
                ids = ids.filtered(lambda r: r.invoice_date > end_date)
            return sum(ids.mapped('amount_residual'))

        grand_total_amount = 0
        grand_total_balance = 0
        grand_total_residue = 0
        grand_total_pdc_amount = 0
        customers = []
        search_filter = []
        pdc_filter = []
        refund_filter = []
        if partner_statement_wizard.invoice_type == 'in_invoice':
            search_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '<', 0.0)]
            refund_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', 'in_refund'), (
                                 'amount_residual', '>', 0.0)]
        if partner_statement_wizard.invoice_type == 'out_invoice':
            search_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '>', 0.0)
                             ]
            refund_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', 'out_refund'), (
                                 'amount_residual', '<', 0.0)
                             ]


        if partner_statement_wizard.start_date:
            search_filter.append(
                ('invoice_date', '>=', partner_statement_wizard.start_date))
            refund_filter.append(
                ('invoice_date', '>=', partner_statement_wizard.start_date))
            pdc_filter.append(('payment_date', '>=', partner_statement_wizard.start_date))
        if partner_statement_wizard.end_date:
            search_filter.append(
                ('invoice_date', '<=', partner_statement_wizard.end_date))
            refund_filter.append(
                ('invoice_date', '<=', partner_statement_wizard.end_date))
            pdc_filter.append(('payment_date', '<=', partner_statement_wizard.end_date))
        if partner_statement_wizard.partner_id:
            for rec in partner_statement_wizard.partner_id:
                customers.append(rec.name)
            if partner_statement_wizard.partner_id.child_ids:
                for cus in partner_statement_wizard.partner_id.child_ids:
                    customers.append(cus.name)
        invoices = self.env['account.move'].search(
            search_filter, order='invoice_date asc')
        refund = self.env['account.move'].search(
            refund_filter, order='invoice_date asc')
        invoices = invoices-refund.mapped('reversed_entry_id')
        pdc_records = self.env['account.cheque'].search(pdc_filter +
                                                        [('payment_type', '=', 'pdc'),
                                                         ('move_type', '=', partner_statement_wizard.invoice_type),
                                                         ('partner_id', '=', partner_statement_wizard.partner_id.id),
                                                         ('state', 'in', ('received', 'issued'))])
        if invoices:
            for inv in invoices:
                data.append({
                    'reference': inv.name,
                    'bill_ref': inv.ref,
                    'lpo':inv.source_id.name if inv.source_id else '',
                    'customer': inv.partner_id.name,
                    'date': inv.invoice_date,
                    'total_amount': "{:,.2f}".format(inv.amount_total),
                    'amount_residue': "{:,.2f}".format(inv.amount_residual),
                    'balance': "{:,.2f}".format(
                        inv.amount_total + inv.amount_residual) if wiz.invoice_type == 'in_invoice' else "{:,.2f}".format(
                        inv.amount_total - inv.amount_residual),
                    'due_date': (inv.invoice_date_due - date.today()).days * -1,
                    'due_dates': inv.invoice_date_due
                })
                grand_total_amount = grand_total_amount + inv.amount_total
                grand_total_balance = grand_total_balance + (
                            inv.amount_total - inv.amount_residual) if wiz.invoice_type == 'out_invoice' else grand_total_balance + (
                            inv.amount_total + inv.amount_residual)
                grand_total_residue = grand_total_residue + inv.amount_residual
        if pdc_records:
            for pdc in pdc_records:
                pdc_data.append({
                    'seq': pdc.cheque_sequence,
                    'date': pdc.date,
                    'amount': "{:,.2f}".format(pdc.amount),
                    'bank': pdc.journal_id.name,
                    'voucher': pdc.voucher_no
                })
                grand_total_pdc_amount = grand_total_pdc_amount + pdc.amount
        return {
            'currency_precision': 2,
            'doc_ids': docids,
            'doc_model': 'partner.statements.wizard',
            'start_dt': partner_statement_wizard.start_date,
            'end_dt': partner_statement_wizard.end_date,
            'in_data': data,
            'pdc_data': pdc_data,
            'company_id': self.env.company,
            'customer': partner_statement_wizard.partner_id,
            'grand_total_amount': "{:,.2f}".format(grand_total_amount),
            'grand_total_balance': "{:,.2f}".format(grand_total_balance),
            'grand_total_residue': "{:,.2f}".format(grand_total_residue),
            'grand_total_pdc_amount': "{:,.2f}".format(grand_total_pdc_amount)
        }

