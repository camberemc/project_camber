# -*- coding: utf-8 -*-
import base64
import io

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import date, datetime


class PartnerStatementReport(models.AbstractModel):
    _name = 'report.stranbys_partner_statement.partner_statement_template'
    _description = "Partner Statement Report "

    def _get_report_values(self, docids, data=None, sessions=False):
        partner_statement_wizard = self.env['partner.statement.wizard'].browse(
            docids)

        data = []
        ageing_30 = 0
        ageing_60 = 0
        ageing_90 = 0
        ageing_120 = 0
        ageing_150 = 0
        bucket_1 = partner_statement_wizard.bucket_1
        bucket_2 = partner_statement_wizard.bucket_2
        bucket_3 = partner_statement_wizard.bucket_3
        bucket_4 = partner_statement_wizard.bucket_4
        bucket_5 = partner_statement_wizard.bucket_5

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
        customers = []
        search_filter = []
        if partner_statement_wizard.invoice_type == 'in_invoice':
            search_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '<', 0.0)
                             ]
        if partner_statement_wizard.invoice_type == 'out_invoice':
            search_filter = ['|', ('partner_id', 'in', partner_statement_wizard.partner_id.ids),
                             ('partner_id', 'in',
                              partner_statement_wizard.partner_id.child_ids.ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '>', 0.0)
                             ]
        if partner_statement_wizard.start_date:
            search_filter.append(
                ('invoice_date', '>=', partner_statement_wizard.start_date))
        if partner_statement_wizard.end_date:
            search_filter.append(
                ('invoice_date', '<=', partner_statement_wizard.end_date))
        # if not partner_statement_wizard.unverified_ok:
        #     search_filter.append(('invoice_verify', '=', 'verified'))
        if partner_statement_wizard.partner_id:
            for rec in partner_statement_wizard.partner_id:
                customers.append(rec.name)
            if partner_statement_wizard.partner_id.child_ids:
                for cus in partner_statement_wizard.partner_id.child_ids:
                    customers.append(cus.name)
        invoices = self.env['account.move'].search(
            search_filter, order='invoice_date asc')

        if invoices:
            for inv in invoices:
                data.append({
                    'reference': inv.name,
                    'lpo': inv.ref,
                    'customer': inv.partner_id.name or '',
                    'date': inv.invoice_date,
                    'total_amount': inv.amount_total,
                    'amount_residue': inv.amount_residual,
                    'balance': inv.amount_total - inv.amount_residual,
                    'due_date': (inv.invoice_date_due - date.today()).days
                })
                grand_total_amount = grand_total_amount + inv.amount_total
                grand_total_balance = grand_total_balance + (
                        inv.amount_total - inv.amount_residual)
                grand_total_residue = grand_total_residue + inv.amount_residual
            # ageing_30 = sum(invoices.filtered(
            #     lambda line: line.invoice_date <= date.today() + relativedelta(days=+ 30)).mapped(
            #     'amount_residual'))
            # ageing_60 = sum(invoices.filtered(
            #     lambda line: line.invoice_date <= date.today() + relativedelta(days=+ 60)).mapped(
            #     'amount_residual'))
            # ageing_90 = sum(invoices.filtered(
            #     lambda line: line.invoice_date <= date.today() + relativedelta(days=+ 90)).mapped(
            #     'amount_residual'))
            # ageing_120 = sum(invoices.filtered(
            #     lambda line: line.invoice_date <= date.today() + relativedelta(days=+ 120)).mapped(
            #     'amount_residual'))
            # ageing_150 = sum(invoices.filtered(
            #     lambda line: line.invoice_date <= date.today() + relativedelta(days=+ 150)).mapped(
            #     'amount_residual'))

        return {
            'currency_precision': 2,
            'doc_ids': docids,
            'doc_model': 'partner.statement.wizard',
            'start_dt': partner_statement_wizard.start_date,
            'end_dt': partner_statement_wizard.end_date,
            'in_data': data,
            'company_id': self.env.company,
            'customer': partner_statement_wizard.partner_id,
            'h_ageing_30': f'{bucket_1}-{bucket_2} days',
            'h_ageing_60': f'{bucket_2}-{bucket_3} days',
            'h_ageing_90': f'{bucket_3}-{bucket_4} days',
            'h_ageing_120': f'{bucket_4}-{bucket_5} days',
            'h_ageing_150': f'{bucket_5}+ days',
            'ageing_30': get_bucket_data(invoices, day_start=bucket_1, day_end=bucket_2),
            'ageing_60': get_bucket_data(invoices, day_start=bucket_2, day_end=bucket_3),
            'ageing_90': get_bucket_data(invoices, day_start=bucket_3, day_end=bucket_4),
            'ageing_120': get_bucket_data(invoices, day_start=bucket_4, day_end=bucket_5),
            'ageing_150': get_bucket_data(invoices, day_start=bucket_5),
            'grand_total_amount': grand_total_amount,
            'grand_total_balance': grand_total_balance,
            'grand_total_residue': grand_total_residue,
            'customers': customers

        }


class DownloadReportXLSX(models.AbstractModel):
    _name = 'report.partner.statement.report.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wiz):

        heading_format = workbook.add_format({'align': 'center',
                                              'valign': 'vcenter',
                                              'bold': True, 'size': 15,
                                              })
        small_heading_style = workbook.add_format({'align': 'center',
                                                   'valign': 'vcenter',
                                                   'bold': True, 'size': 11,
                                                   'text_wrap': True
                                                   })
        yl_sm_h1 = workbook.add_format({'align': 'center', 'bg_color': "#FFFF00",
                                        'valign': 'vcenter',
                                        'bold': True, 'size': 11,
                                        })

        gr_sm_h1 = workbook.add_format({'align': 'right', 'bg_color': "#BBBBBB",
                                        'valign': 'vcenter',
                                        'bold': True, 'size': 11,
                                        })
        gr2_sm_h1 = workbook.add_format({'align': 'right', 'bg_color': "#EEEEEE",
                                         'valign': 'vcenter',
                                         'bold': True, 'size': 11,
                                         })

        small_heading_style_right = workbook.add_format({'align': 'right',
                                                         'valign': 'right',
                                                         'bold': True, 'size': 11,
                                                         })

        col_format = workbook.add_format({'valign': 'left',
                                          'align': 'left',
                                          'bold': True,
                                          'size': 10,
                                          'font_color': '#000000'
                                          })
        data_format = workbook.add_format({'valign': 'center',
                                           'align': 'center',
                                           'size': 10,
                                           'font_color': '#000000'
                                           })
        data_format_right = workbook.add_format({'valign': 'center',
                                                 'align': 'right',
                                                 'size': 10,
                                                 'font_color': '#000000'
                                                 })
        data_format_right_bold = workbook.add_format({'valign': 'center',
                                                      'align': 'right',
                                                      'size': 10,
                                                      'font_color': '#000000',
                                                      'bold': True,
                                                      })
        company_format = workbook.add_format(
            {'font_size': 7, 'font_color': '#000000', 'align': 'left', 'valign': 'vcenter'})
        def get_company_address():
            partner = self.env.user.company_id
            address = self.env.user.company_id.name + '\n'
            if partner.street:
                address = address + partner.street
            if partner.street2:
                address = address + ' ' + partner.street2
            if partner.city:
                address = address + ' ' + partner.city

            if partner.state_id:
                address = address + '\n' + partner.state_id.name
            if partner.country_id:
                address = address + '\n' + partner.country_id.name
            if partner.phone:
                address = address + '\n''Ph.No: ' + partner.phone
            return address

        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Outstanding Report ')
        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:I', 20)
        company_image = self.env.user.company_id.logo
        img_data = base64.b64decode(company_image)
        image = io.BytesIO(img_data)
        worksheet.insert_image('A1:C1', 'myimage.png', {'image_data': image, 'x_scale': 0.9, 'y_scale': 0.9})
        worksheet.merge_range(0, 0, 10, 1, '', heading_format)
        worksheet.merge_range(0, 2, 10, 5, 'Outstanding Statement', heading_format)
        worksheet.merge_range(0, 6, 10, 7,
                              str(get_company_address()),
                              small_heading_style)
        row = 12
        partner_statement_wizard = wiz
        bucket_1 = partner_statement_wizard.bucket_1
        bucket_2 = partner_statement_wizard.bucket_2
        bucket_3 = partner_statement_wizard.bucket_3
        bucket_4 = partner_statement_wizard.bucket_4
        bucket_5 = partner_statement_wizard.bucket_5

        ## Private Functions
        def date_formater(rec_date=False):
            return rec_date.strftime('%d/%m/%Y') if rec_date else '-'

        def get_bucket_data(ids, day_start=False, day_end=False):
            if day_start:
                sta_date = date.today() + relativedelta(days=-day_start)
                ids = ids.filtered(lambda r: r.invoice_date <= sta_date)
            if day_end:
                end_date = date.today() + relativedelta(days=-day_end)
                ids = ids.filtered(lambda r: r.invoice_date > end_date)
            return sum(ids.mapped('amount_residual'))

        partner_ids = partner_statement_wizard.partner_id.ids
        partner_ids = self.env['res.partner'].search([('parent_id', 'in', partner_ids)]).ids + partner_ids
        search_filter = []
        # search_filter = [('partner_id', 'in', partner_ids),
        #                  ('state', '=', 'posted'),
        #                  ('move_type', '=', partner_statement_wizard.invoice_type),
        #                  ('amount_residual', '>', 0.0)]
        if partner_statement_wizard.invoice_type == 'in_invoice':
            search_filter = [('partner_id', 'in', partner_ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '<', 0.0)
                             ]
        if partner_statement_wizard.invoice_type == 'out_invoice':
            search_filter = [('partner_id', 'in', partner_ids),
                             ('state', '=', 'posted'),
                             ('move_type', '=', partner_statement_wizard.invoice_type), (
                                 'amount_residual', '>', 0.0)
                             ]
        if partner_statement_wizard.start_date:
            search_filter.append(('invoice_date', '>=', partner_statement_wizard.start_date))
        if partner_statement_wizard.end_date:
            search_filter.append(('invoice_date', '<=', partner_statement_wizard.end_date))
        # if not partner_statement_wizard.unverified_ok:
        #     search_filter.append(('invoice_verify', '=', 'verified'))
        invoices = self.env['account.move'].search(search_filter, order='invoice_date asc')
        customers = invoices.mapped('partner_id')
        for rec in customers:
            invoices = self.env['account.move'].search(search_filter + [('partner_id', '=', rec.id)],
                                                       order='invoice_date asc')
            row += 1
            worksheet.write(row, 0, 'Customer', yl_sm_h1)
            worksheet.merge_range(row, 1, row, 3, rec.name, yl_sm_h1)
            w_start_date = date_formater(partner_statement_wizard.start_date)
            w_end_date = date_formater(partner_statement_wizard.end_date)
            worksheet.merge_range(row, 4, row, 7, f"From {w_start_date} to {w_end_date}", yl_sm_h1)
            row += 1
            worksheet.write(row, 0, 'Sl.No.', small_heading_style)
            worksheet.write(row, 1, 'Date', small_heading_style)
            worksheet.write(row, 2, 'Invoice Number', small_heading_style)
            worksheet.write(row, 3, 'LPO No.', small_heading_style)
            worksheet.write(row, 4, 'Total Amount', small_heading_style_right)
            worksheet.write(row, 5, 'Paid', small_heading_style_right)
            worksheet.write(row, 6, 'Balance', small_heading_style_right)
            worksheet.write(row, 7, 'Due Days', small_heading_style_right)
            row += 1
            grand_total_residue = 0
            grand_total_balance = 0
            grand_total_amount = 0

            for i, inv in enumerate(invoices):
                worksheet.write(row, 0, i + 1, data_format)
                worksheet.write(row, 1, date_formater(inv.invoice_date), data_format)
                worksheet.write(row, 2, inv.name, data_format)
                worksheet.write(row, 3, inv.ref, data_format)
                worksheet.write(row, 4, inv.amount_total, data_format_right)
                worksheet.write(row, 5, inv.amount_total - inv.amount_residual,
                                data_format_right)
                worksheet.write(row, 6, inv.amount_residual, data_format_right)
                worksheet.write(row, 7, (date.today() - inv.invoice_date_due).days, data_format_right)
                grand_total_amount = grand_total_amount + inv.amount_total
                grand_total_residue = grand_total_residue + inv.amount_residual
                grand_total_balance = grand_total_balance + inv.amount_total - inv.amount_residual
                row += 1
            worksheet.merge_range(row, 0, row, 3, 'Total', gr2_sm_h1)
            worksheet.write(row, 4, grand_total_amount, gr_sm_h1)
            worksheet.write(row, 5, grand_total_balance, gr_sm_h1)
            worksheet.write(row, 6, grand_total_residue, gr_sm_h1)
            worksheet.write(row, 7, '', gr2_sm_h1)
            row += 2
            worksheet.merge_range(row, 0, row + 1, 1, '', gr2_sm_h1)
            worksheet.merge_range(row, 7, row + 1, 7, '', gr2_sm_h1)
            worksheet.write(row, 2, f'{bucket_1}-{bucket_2} days', gr2_sm_h1)
            worksheet.write(row, 3, f'{bucket_2}-{bucket_3} days', gr2_sm_h1)
            worksheet.write(row, 4, f'{bucket_3}-{bucket_4} days', gr2_sm_h1)
            worksheet.write(row, 5, f'{bucket_4}-{bucket_5} days', gr2_sm_h1)
            worksheet.write(row, 6, f'{bucket_5}+ days', gr2_sm_h1)
            row += 1
            worksheet.write(row, 2, get_bucket_data(invoices, day_start=bucket_1, day_end=bucket_2), gr2_sm_h1)
            worksheet.write(row, 3, get_bucket_data(invoices, day_start=bucket_2, day_end=bucket_3), gr2_sm_h1)
            worksheet.write(row, 4, get_bucket_data(invoices, day_start=bucket_3, day_end=bucket_4), gr2_sm_h1)
            worksheet.write(row, 5, get_bucket_data(invoices, day_start=bucket_4, day_end=bucket_5), gr2_sm_h1)
            worksheet.write(row, 6, get_bucket_data(invoices, day_start=bucket_5), gr2_sm_h1)
            row += 2
