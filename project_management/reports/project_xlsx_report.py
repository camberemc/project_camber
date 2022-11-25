# -*- coding: utf-8 -*-
import base64
import io

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import date, datetime


class DownloadReportXLSX(models.AbstractModel):
    _name = 'report.project.details.report.xlsx'
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

        gr_sm_h1 = workbook.add_format({'align': 'center', 'bg_color': "#BBBBBB",
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

        col_format.set_text_wrap()
        worksheet = workbook.add_worksheet('Project Report ')
        worksheet.set_column('A:A', 35)
        worksheet.set_column('B:I', 20)
        company_image = self.env.user.company_id.logo
        img_data = base64.b64decode(company_image)
        image = io.BytesIO(img_data)
        worksheet.insert_image('A1:A1', 'myimage.png', {'image_data': image, 'x_scale': 0.8, 'y_scale': 1.3})
        worksheet.merge_range(0, 0, 10, 0, '', heading_format)
        worksheet.merge_range(0, 1, 10, 3, 'Project Report', heading_format)
        # worksheet.merge_range(0, 3, 10, 3, '', heading_format)
        worksheet.merge_range(0, 4, 10, 4,
                              'Stevok Fire and Safety LLC''\n''Ware House # D25,''\n'' Al Quoz IND 2,''\n''Dubai (AE)''\n''United Arab Emirates',
                              small_heading_style)

        def date_formater(rec_date=False):
            return rec_date.strftime('%d/%m/%Y') if rec_date else '-'

        row = 11
        print(wiz)
        worksheet.write(row, 0, 'Project', yl_sm_h1)
        worksheet.merge_range(row, 1, row, 3, wiz.name, yl_sm_h1)
        row = row + 1
        worksheet.write(row, 0, 'Customer', yl_sm_h1)
        worksheet.merge_range(row, 1, row, 3, wiz.partner_id.name, yl_sm_h1)
        row = row + 2
        worksheet.merge_range(row, 0, row, 4, 'Material Details', gr_sm_h1)
        row = row + 2
        worksheet.write(row, 0, 'Sl.No.', small_heading_style)
        worksheet.write(row, 1, 'Item Description', small_heading_style)
        worksheet.write(row, 2, 'Quantity', data_format_right_bold)
        worksheet.write(row, 3, 'Unit Cost (WAC)', data_format_right_bold)
        worksheet.write(row, 4, 'Total Value', data_format_right_bold)
        row = row + 1
        total_qty = 0
        total_value = 0
        if wiz.project_line_product_ids:
            sl_no = 1
            for line in wiz.project_line_product_ids:
                if line.qty_delivered:
                    worksheet.write(row, 0, sl_no, data_format)
                    worksheet.write(row, 1, line.name, data_format)
                    worksheet.write(row, 2, line.qty_delivered, data_format_right)
                    worksheet.write(row, 3, line.cost, data_format_right)
                    worksheet.write(row, 4, (line.qty_delivered * line.cost), data_format_right)
                    total_qty = total_qty + line.qty_delivered
                    total_value = total_value + (line.qty_delivered * line.cost)
                    sl_no = sl_no + 1
                    row = row + 1
            row = row + 1
            worksheet.write(row, 0, 'Total ', small_heading_style)
            worksheet.write(row, 2, total_qty, data_format_right_bold)
            worksheet.write(row, 4, total_value, data_format_right_bold)

        row = row + 2

        journal_ids = self.env['account.journal'].search([('name', '!=', 'Customer Invoices')])
        expense = self.env['account.move.line'].search(
            [('project_id', '=', wiz.id), ('journal_id', 'in', journal_ids.ids),('move_id.state', '=', 'posted')])
        total_debit = 0
        if expense:
            worksheet.merge_range(row, 0, row, 4, 'Expense Details', gr_sm_h1)
            row = row + 2
            worksheet.write(row, 0, 'Sl.No.', small_heading_style)
            worksheet.write(row, 1, 'Trans No.', small_heading_style)
            worksheet.write(row, 2, 'Account', small_heading_style)
            worksheet.write(row, 3, 'Narration', small_heading_style)
            worksheet.write(row, 4, 'Amount', data_format_right_bold)
            row = row + 1
            sl_no = 1
            for exp in expense:
                worksheet.write(row, 0, sl_no, data_format)
                worksheet.write(row, 1, exp.move_id.name, data_format)
                worksheet.write(row, 2, exp.account_id.name, data_format)
                worksheet.write(row, 3, exp.name, data_format)
                worksheet.write(row, 4, exp.debit, data_format_right)
                total_debit = total_debit + exp.debit
                sl_no = sl_no + 1
                row = row + 1
            row = row + 1
            worksheet.write(row, 0, 'Total ', small_heading_style)
            worksheet.write(row, 4, total_debit, data_format_right_bold)
        row = row + 2
        journal_id = self.env['account.journal'].search([('name', '=', 'Customer Invoices')], limit=1)
        income = self.env['account.move'].search(
            [('project_id', '=', wiz.id), ('journal_id', '=', journal_id.id),('state', '=', 'posted')])
        total_amount = 0
        if income:
            worksheet.merge_range(row, 0, row, 4, 'Income Details', gr_sm_h1)
            row = row + 2
            worksheet.write(row, 0, 'Sl.No.', small_heading_style)
            worksheet.write(row, 1, 'Invoice No.', small_heading_style)
            worksheet.write(row, 2, 'Date', small_heading_style)
            worksheet.write(row, 3, 'Reference', small_heading_style)
            worksheet.write(row, 4, 'Amount', data_format_right_bold)
            row = row + 1
            sl_no = 1
            for inc in income:
                worksheet.write(row, 0, sl_no, data_format)
                worksheet.write(row, 1, inc.name, data_format)
                worksheet.write(row, 2, date_formater(inc.invoice_date), data_format)
                worksheet.write(row, 3, inc.ref, data_format)
                worksheet.write(row, 4, inc.amount_total, data_format_right)
                total_amount = total_amount + inc.amount_total
                row = row + 1
                sl_no = sl_no + 1
            row = row + 1
            worksheet.write(row, 0, 'Total ', small_heading_style)
            worksheet.write(row, 4, total_amount, data_format_right_bold)
        row = row + 3
        # worksheet.write(row, 2, "Material", small_heading_style)
        # worksheet.write(row, 3, "Expense", small_heading_style)
        # worksheet.write(row, 4, "Income", small_heading_style)
        # row = row + 1
        # worksheet.write(row, 2, total_value, data_format_right_bold)
        # worksheet.write(row, 3, total_debit, data_format_right_bold)
        # worksheet.write(row, 4, total_amount, data_format_right_bold)
        # row = row + 2
        # worksheet.write(row, 3, "Total Profit", data_format_right_bold)
        # total_profit = total_amount - (total_value + total_debit)
        # worksheet.write(row, 4,total_profit , data_format_right_bold)
        # row=row+1
        # worksheet.write(row, 3, "Profit (%) ", data_format_right_bold)
        # try:
        #     profit_per = (total_profit * 100)/total_amount
        # except ZeroDivisionError:
        #     profit_per = 0
        # worksheet.write(row, 4, round(profit_per,2), data_format_right_bold)
        worksheet.write(row, 1, "Income", data_format_right_bold)
        worksheet.write(row, 2, total_amount, data_format_right_bold)
        worksheet.write(row, 3, "Expense", data_format_right_bold)
        worksheet.write(row, 4, total_debit, data_format_right_bold)
        row=row+1
        worksheet.write(row, 3, "Material Cost", data_format_right_bold)
        worksheet.write(row, 4, total_value, data_format_right_bold)
        row=row+1
        worksheet.write(row, 1, "Total", data_format_right_bold)
        worksheet.write(row, 2, total_amount, data_format_right_bold)
        worksheet.write(row, 3, "Total", data_format_right_bold)
        worksheet.write(row, 4, (total_value + total_debit), data_format_right_bold)
        row=row+2
        worksheet.write(row, 3, "Total Profit", data_format_right_bold)
        total_profit = total_amount - (total_value + total_debit)
        worksheet.write(row, 4, total_profit, data_format_right_bold)
        row=row+1
        worksheet.write(row, 3, "Profit (%) ", data_format_right_bold)
        try:
            profit_per = (total_profit * 100) / total_amount
        except ZeroDivisionError:
            profit_per = 0
        worksheet.write(row, 4, round(profit_per, 2), data_format_right_bold)









        # partner_statement_wizard = wiz
        # bucket_1 = partner_statement_wizard.bucket_1
        # bucket_2 = partner_statement_wizard.bucket_2
        # bucket_3 = partner_statement_wizard.bucket_3
        # bucket_4 = partner_statement_wizard.bucket_4
        # bucket_5 = partner_statement_wizard.bucket_5
        #
        # ## Private Functions
        # def date_formater(rec_date=False):
        #     return rec_date.strftime('%d/%m/%Y') if rec_date else '-'
        #
        # def get_bucket_data(ids, day_start=False, day_end=False):
        #     if day_start:
        #         sta_date = date.today() + relativedelta(days=-day_start)
        #         ids = ids.filtered(lambda r: r.invoice_date <= sta_date)
        #     if day_end:
        #         end_date = date.today() + relativedelta(days=-day_end)
        #         ids = ids.filtered(lambda r: r.invoice_date > end_date)
        #     return sum(ids.mapped('amount_residual'))
        #
        # partner_ids = partner_statement_wizard.partner_id.ids
        # partner_ids = self.env['res.partner'].search([('parent_id', 'in', partner_ids)]).ids + partner_ids
        # search_filter = [('partner_id', 'in', partner_ids),
        #                  ('state', '=', 'posted'),
        #                  ('move_type', '=', partner_statement_wizard.invoice_type),
        #                  ('amount_residual', '>', 0.0)]
        # if partner_statement_wizard.start_date:
        #     search_filter.append(('invoice_date', '>=', partner_statement_wizard.start_date))
        # if partner_statement_wizard.end_date:
        #     search_filter.append(('invoice_date', '<=', partner_statement_wizard.end_date))
        # if not partner_statement_wizard.unverified_ok:
        #     search_filter.append(('invoice_verify', '=', 'verified'))
        # invoices = self.env['account.move'].search(search_filter, order='invoice_date asc')
        # customers = invoices.mapped('partner_id')
        # for rec in customers:
        #     invoices = self.env['account.move'].search(search_filter + [('partner_id', '=', rec.id)],
        #                                                order='invoice_date asc')
        #     row += 1
        #     worksheet.write(row, 0, 'Customer', yl_sm_h1)
        #     worksheet.merge_range(row, 1, row, 3, rec.name, yl_sm_h1)
        #     w_start_date = date_formater(partner_statement_wizard.start_date)
        #     w_end_date = date_formater(partner_statement_wizard.end_date)
        #     worksheet.merge_range(row, 4, row, 7, f"From {w_start_date} to {w_end_date}", yl_sm_h1)
        #     row += 1
        #     worksheet.write(row, 0, 'Sl.No.', small_heading_style)
        #     worksheet.write(row, 1, 'Date', small_heading_style)
        #     worksheet.write(row, 2, 'Invoice Number', small_heading_style)
        #     worksheet.write(row, 3, 'LPO No.', small_heading_style)
        #     worksheet.write(row, 4, 'Total Amount', small_heading_style_right)
        #     worksheet.write(row, 5, 'Paid', small_heading_style_right)
        #     worksheet.write(row, 6, 'Balance', small_heading_style_right)
        #     worksheet.write(row, 7, 'Due Days', small_heading_style_right)
        #     row += 1
        #     grand_total_residue = 0
        #     grand_total_balance = 0
        #     grand_total_amount = 0
        #
        #     for i, inv in enumerate(invoices):
        #         worksheet.write(row, 0, i + 1, data_format)
        #         worksheet.write(row, 1, date_formater(inv.invoice_date), data_format)
        #         worksheet.write(row, 2, inv.name, data_format)
        #         worksheet.write(row, 3, inv.ref, data_format)
        #         worksheet.write(row, 4, inv.amount_total, data_format_right)
        #         worksheet.write(row, 5, (inv.amount_total - inv.amount_residual - inv.sales_return_amount),
        #                         data_format_right)
        #         worksheet.write(row, 6, (inv.amount_residual - inv.sales_return_amount), data_format_right)
        #         worksheet.write(row, 7, (date.today() - inv.invoice_date_due).days, data_format_right)
        #         grand_total_amount = grand_total_amount + inv.amount_total
        #         grand_total_residue = grand_total_residue + inv.amount_residual - inv.sales_return_amount
        #         grand_total_balance = grand_total_balance + inv.amount_total - inv.amount_residual - inv.sales_return_amount
        #         row += 1
        #     worksheet.merge_range(row, 0, row, 3, 'Total', gr2_sm_h1)
        #     worksheet.write(row, 4, grand_total_amount, gr_sm_h1)
        #     worksheet.write(row, 5, grand_total_balance, gr_sm_h1)
        #     worksheet.write(row, 6, grand_total_residue, gr_sm_h1)
        #     worksheet.write(row, 7, '', gr2_sm_h1)
        #     row += 2
        #     worksheet.merge_range(row, 0, row + 1, 1, '', gr2_sm_h1)
        #     worksheet.merge_range(row, 7, row + 1, 7, '', gr2_sm_h1)
        #     worksheet.write(row, 2, f'{bucket_1}-{bucket_2} days', gr2_sm_h1)
        #     worksheet.write(row, 3, f'{bucket_2}-{bucket_3} days', gr2_sm_h1)
        #     worksheet.write(row, 4, f'{bucket_3}-{bucket_4} days', gr2_sm_h1)
        #     worksheet.write(row, 5, f'{bucket_4}-{bucket_5} days', gr2_sm_h1)
        #     worksheet.write(row, 6, f'{bucket_5}+ days', gr2_sm_h1)
        #     row += 1
        #     worksheet.write(row, 2, get_bucket_data(invoices, day_start=bucket_1, day_end=bucket_2), gr2_sm_h1)
        #     worksheet.write(row, 3, get_bucket_data(invoices, day_start=bucket_2, day_end=bucket_3), gr2_sm_h1)
        #     worksheet.write(row, 4, get_bucket_data(invoices, day_start=bucket_3, day_end=bucket_4), gr2_sm_h1)
        #     worksheet.write(row, 5, get_bucket_data(invoices, day_start=bucket_4, day_end=bucket_5), gr2_sm_h1)
        #     worksheet.write(row, 6, get_bucket_data(invoices, day_start=bucket_5), gr2_sm_h1)
        #     row += 2
