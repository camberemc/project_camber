from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from dateutil.relativedelta import relativedelta


class EmployeeLoanWizard(models.TransientModel):
    _name = "stock.movement.wizard"
    _description = "Stock Summary Report"

    date_fr = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    product_ids = fields.Many2many('product.product', string="Product")

    def print_stock_movement(self):
        return self.env.ref('stranbys_stock_report.report_print_stock_movement').report_action(self)


class EmployeeLoanXlsx(models.AbstractModel):
    _name = 'report.stock.movement.xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, wizard):
        report_head = workbook.add_format({'font_size': 16, 'bold': True, 'font_color': '#707276'})
        report_format = workbook.add_format({'font_size': 10, 'font_color': '#707276'})
        report_bold = workbook.add_format({'font_size': 10, 'bold': True, 'font_color': '#707276'})
        h3 = workbook.add_format({'bg_color': '#00205b', 'font_size': 10, 'bold': True, 'font_color': '#ffffff'})
        sheet = workbook.add_worksheet("Stock Summary")
        sheet.write(0, 1, 'Stock Summary Report', report_head)
        sheet.write(1, 1, 'From Date:', report_bold)
        sheet.write(1, 2, str(wizard.date_fr), report_bold)
        sheet.write(2, 1, 'To Date', report_bold)
        sheet.write(2, 2, str(wizard.date_to), report_bold)

        sheet.freeze_panes(4, 1)
        sheet.set_column(0, 7, 15, None)

        sheet.write(3, 0, 'Product', h3)
        sheet.write(3, 1, 'Opening Stock', h3)
        sheet.write(3, 2, 'Purchased', h3)
        sheet.write(3, 3, 'Sold', h3)
        sheet.write(3, 4, 'Adjustments In', h3)
        sheet.write(3, 5, 'Adjustments out', h3)
        sheet.write(3, 6, 'In Stock', h3)

        row = 3

        d_sta = wizard.date_fr
        d_end = wizard.date_to
        products = wizard.product_ids

        # d_sta = datetime.strptime(wizard.date_fr, DEFAULT_SERVER_DATE_FORMAT)
        # d_end = datetime.strptime(wizard.date_to, DEFAULT_SERVER_DATE_FORMAT)

        Moves = self.env['stock.move.line'].search(
            [('date', '>=', d_sta), ('date', '<=', d_end), ('product_id', 'in', products.ids)])
        print(Moves)
        # Moves = self.env['stock.move.line'].search([])

        ClosingMoves = self.env['stock.move.line'].search([('date', '<', d_sta), ('product_id', 'in', products.ids)])
        print(ClosingMoves)

        # Products = Moves.mapped('product_id')

        Products = self.env['product.product'].search([('id', 'in', products.ids)])
        # for product in products:
        #     row += 1
        #     # adjustment
        #     adjustment_in = sum(Moves.filtered(lambda
        #                                                r: r.location_id.usage == 'inventory' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
        #         'qty_done'))
        #     adjustment_out = sum(Moves.filtered(lambda
        #                                                 r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'inventory').mapped(
        #         'qty_done'))
        # #     sale
        #     sale = sum(Moves.filtered(lambda
        #                                                r: r.location_id.usage == 'customer' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
        #         'qty_done'))
        #     sale_return = sum(Moves.filtered(lambda
        #                                                 r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'customer').mapped(
        #         'qty_done'))
        #     delivered_qty = sale - sale_return
        # #     purchase
        #     purchase_in = sum(Moves.filtered(lambda
        #                                                r: r.location_id.usage == 'supplier' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
        #         'qty_done'))
        #     purchase_return = sum(Moves.filtered(lambda
        #                                                 r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'supplier').mapped(
        #         'qty_done'))
        #     supplied_qty = purchase_in - purchase_return
        # # opening
        #     opening = sum(ClosingMoves.filtered(lambda
        #                                                       r: r.location_id.usage == 'inventory' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
        #         'qty_done'))
        #
        #     on_hand_qty = opening + supplied_qty + adjustment_in - adjustment_out - delivered_qty
        #
        #     sheet.write(row, 0, product.name, report_format)
        #     sheet.write(row, 1, opening, report_format)
        #     sheet.write(row, 2, supplied_qty, report_format)
        #     sheet.write(row, 3, delivered_qty, report_format)
        #     sheet.write(row, 4, adjustment_in, report_format)
        #     sheet.write(row, 5, adjustment_out, report_format)
        #     sheet.write(row, 6, on_hand_qty, report_format)








        for product in Products:
            row += 1

            # Adjustments
            opening_input_qty = sum(Moves.filtered(lambda
                                                       r: r.location_id.usage == 'inventory' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_input_qty_2 = sum(Moves.filtered(lambda
                                                         r: r.location_id.usage == 'production' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(Moves.filtered(lambda
                                                        r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'inventory').mapped(
                'qty_done'))

            out_opening_output_qty3 = sum(Moves.filtered(lambda
                                                             r: r.product_id.id == product.id and r.location_dest_id.name == 'Consumed Stock').mapped(
                'qty_done'))
            # adjustment in
            inventory_adj = opening_input_qty + opening_input_qty_2
            # adjustment out
            out_inventory_adj = opening_output_qty + out_opening_output_qty3

            # Supplied
            opening_input_qty = sum(Moves.filtered(lambda
                                                       r: r.location_id.usage == 'supplier' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(Moves.filtered(lambda
                                                        r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'supplier').mapped(
                'qty_done'))
            supplied_qty = opening_input_qty - opening_output_qty

            # Delivered
            opening_input_qty = sum(Moves.filtered(lambda
                                                       r: r.location_id.usage == 'customer' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(Moves.filtered(lambda
                                                        r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'customer').mapped(
                'qty_done'))
            delivered_qty = opening_output_qty - opening_input_qty

            # Opening Adjustments
            opening_input_qty = sum(ClosingMoves.filtered(lambda
                                                              r: r.location_id.usage == 'inventory' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(ClosingMoves.filtered(lambda
                                                               r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'inventory').mapped(
                'qty_done'))
            op_inventory_adj = opening_input_qty - opening_output_qty

            # Opening Supplied
            opening_input_qty = sum(ClosingMoves.filtered(lambda
                                                              r: r.location_id.usage == 'supplier' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(ClosingMoves.filtered(lambda
                                                               r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'supplier').mapped(
                'qty_done'))
            op_supplied_qty = opening_input_qty - opening_output_qty

            # Opening Delivered
            opening_input_qty = sum(ClosingMoves.filtered(lambda
                                                              r: r.location_id.usage == 'customer' and r.product_id.id == product.id and r.location_dest_id.usage == 'internal').mapped(
                'qty_done'))
            opening_output_qty = sum(ClosingMoves.filtered(lambda
                                                               r: r.location_id.usage == 'internal' and r.product_id.id == product.id and r.location_dest_id.usage == 'customer').mapped(
                'qty_done'))
            op_delivered_qty = opening_output_qty - opening_input_qty

            delivered_qty = delivered_qty + op_delivered_qty
            print(op_supplied_qty)
            print(op_delivered_qty)
            print(op_inventory_adj)

            op_on_hand_qty = op_supplied_qty  + op_inventory_adj
            print(op_on_hand_qty)

            on_hand_qty = op_on_hand_qty + supplied_qty - delivered_qty + inventory_adj - out_inventory_adj

            sheet.write(row, 0, product.name, report_format)
            sheet.write(row, 1, op_on_hand_qty, report_format)
            sheet.write(row, 2, supplied_qty, report_format)
            sheet.write(row, 3, delivered_qty, report_format)
            sheet.write(row, 4, inventory_adj, report_format)
            sheet.write(row, 5, out_inventory_adj, report_format)
            sheet.write(row, 6, on_hand_qty, report_format)
