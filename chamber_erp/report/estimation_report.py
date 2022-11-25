# -*- coding: utf-8 -*-
import base64
import io

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from datetime import date, datetime


class DownloadReportXLSX(models.AbstractModel):
    _name = 'report.estimation.report.xlsx'
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
        small_heading_style_left = workbook.add_format({'align': 'left',
                                                        'valign': 'left',
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
        data_format_left = workbook.add_format({'valign': 'center',
                                                'align': 'left',
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

        def get_address(partner_id):
            partner = self.env['res.partner'].search([('id', '=', partner_id)])
            address = partner.name + '\n'
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
        worksheet = workbook.add_worksheet('Estimation Report')
        worksheet.set_column('A:A', 15)
        # worksheet.set_column('B:B', 15)
        # worksheet.set_column('A:A', 15)
        worksheet.set_column('B:O', 20)
        # company_image = self.env.user.company_id.logo
        # img_data = base64.b64decode(company_image)
        # image = io.BytesIO(img_data)
        # worksheet.insert_image('A1:C1', 'myimage.png', {'image_data': image, 'x_scale': 0.9, 'y_scale': 0.9})
        worksheet.merge_range(0, 0, 6, 1, '', heading_format)
        worksheet.merge_range(0, 2, 6, 5, 'Estimation Report- %s' % wiz.name, heading_format)
        worksheet.merge_range(0, 6, 6, 7, str(get_address(self.env.user.company_id.id)),
                              small_heading_style)
        row = 7
        partner_statement_wizard = wiz
        worksheet.write(row, 0, 'Customer', heading_format)
        worksheet.merge_range(row, 1, row, 4, wiz.partner_id.name, data_format_left)
        row += 1
        worksheet.write(row, 0, 'Lead', heading_format)
        worksheet.merge_range(row, 1, row, 4, wiz.lead_id.name, data_format_left)
        row += 2

        if wiz.product_line_ids:
            worksheet.merge_range(row, 1, row, 13, "Project Estimation", yl_sm_h1)
            row += 1
            i = 1
            unit_cost = 0
            inst_cost = 0
            net_cost = 0
            profit = 0
            service_subtotal = 0
            unit_selling_price = 0
            with_service = 0
            service_price = 0
            top_selling = 0
            worksheet.write(row, 0, 'Sl.No.', small_heading_style)
            worksheet.write(row, 1, 'Description', small_heading_style)
            worksheet.write(row, 2, 'Unit', small_heading_style)
            worksheet.write(row, 3, 'Qty', small_heading_style)
            worksheet.write(row, 4, 'U/MH', small_heading_style_right)
            worksheet.write(row, 5, 'T/MH', small_heading_style_right)
            worksheet.write(row, 6, 'U/MAT', small_heading_style_right)
            worksheet.write(row, 7, 'T/MAT', small_heading_style_right)
            worksheet.write(row, 8, 'U/R-MH', small_heading_style_right)
            worksheet.write(row, 9, 'T/R-MH', small_heading_style_right)
            worksheet.write(row, 10, 'U/R-MAT', small_heading_style_right)
            worksheet.write(row, 11, 'T/R-MAT', small_heading_style_right)
            worksheet.write(row, 12, 'U/R-INS', small_heading_style_right)
            worksheet.write(row, 13, 'T/R-INS', small_heading_style_right)
            row += 1
            sub_unit_man_hour_installation = 0
            sub_total_man_hour_installation = 0
            sub_unit_price_material = 0
            sub_total_price_material = 0
            sub_unit_rate_man_hour_tf = 0
            sub_total_rate_man_hour = 0
            sub_unit_rate_material_supply = 0
            sub_total_rate_material_supply = 0
            sub_unit_rate_installation = 0
            sub_total_rate_installation = 0
            for line in wiz.product_line_ids:
                current_section = False
                if line.display_type in ('line_section', 'line_note'):
                    worksheet.merge_range(row, 0, row, 13, line.name, small_heading_style_left)
                    row = row + 1
                else:
                    worksheet.write(row, 0, i, data_format)
                    worksheet.write(row, 1, line.name, data_format_left)
                    worksheet.write(row, 2, line.product_uom.name, data_format)
                    worksheet.write(row, 3, line.product_qty, data_format)
                    worksheet.write(row, 4, "{:,.2f}".format(line.unit_man_hour_installation), data_format_right)
                    worksheet.write(row, 5, "{:,.2f}".format(line.total_man_hour_installation), data_format_right)
                    worksheet.write(row, 6, "{:,.2f}".format(line.unit_price_material), data_format_right)
                    worksheet.write(row, 7, "{:,.2f}".format(line.total_price_material), data_format_right)
                    worksheet.write(row, 8, "{:,.2f}".format(line.unit_rate_man_hour_tf), data_format_right)
                    worksheet.write(row, 9, "{:,.2f}".format(line.total_rate_man_hour), data_format_right)
                    worksheet.write(row, 10, "{:,.2f}".format(line.unit_rate_material_supply), data_format_right)
                    worksheet.write(row, 11, "{:,.2f}".format(line.total_rate_material_supply), data_format_right)
                    worksheet.write(row, 12, "{:,.2f}".format(line.unit_rate_installation), data_format_right)
                    worksheet.write(row, 13, "{:,.2f}".format(line.total_rate_installation), data_format_right)
                    i = i + 1

                    sub_unit_man_hour_installation = sub_unit_man_hour_installation + line.unit_man_hour_installation
                    sub_total_man_hour_installation = sub_total_man_hour_installation + line.total_man_hour_installation
                    sub_unit_price_material = sub_unit_price_material + line.unit_price_material
                    sub_total_price_material = sub_total_price_material + line.total_price_material
                    sub_unit_rate_man_hour_tf = sub_unit_rate_man_hour_tf + line.unit_rate_man_hour_tf
                    sub_total_rate_man_hour = sub_total_rate_man_hour + line.total_rate_man_hour
                    sub_unit_rate_material_supply = sub_unit_rate_material_supply + line.unit_rate_material_supply
                    sub_total_rate_material_supply = sub_total_rate_material_supply + line.total_rate_material_supply
                    sub_unit_rate_installation = sub_unit_rate_installation + line.unit_rate_installation
                    sub_total_rate_installation = sub_total_rate_installation + line.total_rate_installation


                    # inst_cost = inst_cost + line.service_cost
                    # net_cost = net_cost + line.net_cost
                    # profit = profit + line.profit
                    # service_subtotal = service_subtotal + line.service_subtotal
                    # unit_selling_price = unit_selling_price + line.unit_selling_price
                    # with_service = with_service + line.unit_total
                    # service_price = service_price + line.selling_price
                    # top_selling = top_selling + line.total_selling_service
                    row += 1
            worksheet.merge_range(row, 0, row, 3, "Total", small_heading_style)
            worksheet.write(row, 4, "{:,.2f}".format(sub_unit_man_hour_installation), data_format_right_bold)
            worksheet.write(row, 5, "{:,.2f}".format(sub_total_man_hour_installation), data_format_right_bold)
            worksheet.write(row, 6, "{:,.2f}".format(sub_unit_price_material), data_format_right_bold)
            worksheet.write(row, 7, "{:,.2f}".format(sub_total_price_material), data_format_right_bold)
            worksheet.write(row, 8, "{:,.2f}".format(sub_unit_rate_man_hour_tf), data_format_right_bold)
            worksheet.write(row, 9, "{:,.2f}".format(sub_total_rate_man_hour), data_format_right_bold)
            worksheet.write(row, 10, "{:,.2f}".format(sub_unit_rate_material_supply), data_format_right_bold)
            worksheet.write(row, 11, "{:,.2f}".format(sub_total_rate_material_supply), data_format_right_bold)
            worksheet.write(row, 12, "{:,.2f}".format(sub_unit_rate_installation), data_format_right_bold)
            worksheet.write(row, 13, "{:,.2f}".format(sub_total_rate_installation), data_format_right_bold)

            # # worksheet.write(row, 6, "{:,.2f}".format(inst_cost), data_format_right_bold)
            # worksheet.write(row, 5, "{:,.2f}".format(net_cost), data_format_right_bold)
            # # worksheet.write(row, 6, "{:,.2f}".format(profit), data_format_right_bold)
            # # worksheet.write(row, 10, "{:,.2f}".format(service_subtotal), data_format_right_bold)
            # worksheet.write(row, 6, "{:,.2f}".format(unit_selling_price), data_format_right_bold)
            # # worksheet.write(row, 12, "{:,.2f}".format(with_service), data_format_right_bold)
            # worksheet.write(row, 7, "{:,.2f}".format(service_price), data_format_right_bold)
            # # worksheet.write(row, 14, "{:,.2f}".format(top_selling), data_format_right_bold)
            # row += 1
        # if wiz.consumable_line_ids:
        #     worksheet.merge_range(row, 1, row, 7, "Consumable Estimation", yl_sm_h1)
        #     row += 1
        #     i = 1
        #     quantity = 0
        #     unit_cost = 0
        #     cost = 0
        #     worksheet.write(row, 0, 'Sl.No.', small_heading_style)
        #     worksheet.write(row, 1, 'Product', small_heading_style)
        #     worksheet.write(row, 2, 'Description', small_heading_style)
        #     worksheet.write(row, 3, 'Brand', small_heading_style)
        #     worksheet.write(row, 4, 'Unit Of Measure', small_heading_style)
        #     worksheet.write(row, 5, 'Quantity', small_heading_style_right)
        #     worksheet.write(row, 6, 'Unit Cost', small_heading_style_right)
        #     worksheet.write(row, 7, 'Total Cost', small_heading_style_right)
        #     row += 1
        #
        #     for line in wiz.consumable_line_ids:
        #         worksheet.write(row, 0, i, data_format)
        #         worksheet.write(row, 1, line.product_id.name, data_format_left)
        #         worksheet.write(row, 2, line.name, data_format_left)
        #         worksheet.write(row, 3, line.brand_id.name, data_format_left) if line.brand_id else ''
        #         worksheet.write(row, 4, line.uom_id.name, data_format_left) if line.uom_id else ''
        #         worksheet.write(row, 5, line.product_qty, data_format_right)
        #         worksheet.write(row, 6, "{:,.2f}".format(line.unit_cost), data_format_right)
        #         worksheet.write(row, 7, "{:,.2f}".format(line.cost), data_format_right)
        #         quantity = quantity + line.product_qty
        #         unit_cost = unit_cost + line.unit_cost
        #         cost = cost + line.cost
        #         i = i + 1
        #         row += 1
        #     worksheet.merge_range(row, 0, row, 4, "Total", small_heading_style)
        #     worksheet.write(row, 5, quantity, data_format_right_bold)
        #     worksheet.write(row, 6, "{:,.2f}".format(unit_cost), data_format_right_bold)
        #     worksheet.write(row, 7, "{:,.2f}".format(cost), data_format_right_bold)
        #     row += 1
        # if wiz.expense_line_ids:
        #     worksheet.merge_range(row, 1, row, 7, "Expense", yl_sm_h1)
        #     row += 1
        #     i = 1
        #     amount = 0
        #     worksheet.write(row, 0, 'Sl.No.', small_heading_style)
        #     worksheet.write(row, 1, 'Expense Name', small_heading_style)
        #     worksheet.write(row, 2, 'Amount', small_heading_style)
        #     row += 1
        #     for line in wiz.expense_line_ids:
        #         worksheet.write(row, 0, i, data_format)
        #         worksheet.write(row, 1, line.name, data_format_left)
        #         worksheet.write(row, 2, "{:,.2f}".format(line.amount), data_format_right)
        #         amount = amount + line.amount
        #         i = i + 1
        #         row += 1
        #     worksheet.merge_range(row, 0, row, 1, "Total", small_heading_style)
        #     worksheet.write(row, 2, "{:,.2f}".format(amount), data_format_right_bold)
        #     row += 1
        # worksheet.merge_range(row, 6, row, 7, "Estimation Cost", yl_sm_h1)
        # row += 1
        # worksheet.write(row, 6, 'Product Cost', data_format_right_bold)
        # worksheet.write(row, 7, "{:,.2f}".format(wiz.cost), data_format_right_bold)
        # row += 1
        # worksheet.write(row, 6, 'Installation Price', data_format_right_bold)
        # worksheet.write(row, 7, "{:,.2f}".format(wiz.service_cost), data_format_right_bold)
        # row += 1
        # worksheet.write(row, 6, 'Expense', data_format_right_bold)
        # worksheet.write(row, 7, "{:,.2f}".format(wiz.expense_total, 2), data_format_right_bold)
        # row += 1
        # worksheet.write(row, 6, 'Profit', data_format_right_bold)
        # worksheet.write(row, 7, "{:,.2f}".format(wiz.profit), data_format_right_bold)
        # row += 1
        # worksheet.write(row, 6, 'Price', data_format_right_bold)
        # worksheet.write(row, 7, "{:.2f}".format(wiz.total_selling_price), data_format_right_bold)
