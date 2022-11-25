from datetime import datetime, timedelta

from odoo import api, fields, models, _
from ast import literal_eval


class EmployeeLoanWizard(models.TransientModel):
    _name = "stock.movement.wizard"
    _description = "Stock Summary Report"

    date_fr = fields.Date(string="From Date")
    date_to = fields.Date(string="To Date")
    product_ids = fields.Many2many('product.product', string="Product")

    def print_stock_movement(self):
        return self.env.ref('stranbys_stock_report.report_print_stock_movement').report_action(self)

    def print_stock_movement_preview(self):
        return self.env.ref('stranbys_stock_report.action_print_stock_report_html').report_action(self)

    def print_stock_movement_pdf(self):
        return self.env.ref('stranbys_stock_report.action_print_stock_report').report_action(self)

    def print_stock_move_entries(self):
        action = self.env["ir.actions.actions"]._for_xml_id('stranbys_stock_report.stock_move_action_pivot')

        context = {
            'search_default_done': 1,
            'search_default_by_product': 1,
            'search_default_groupby_dest_location_id': 1,
            # 'search_default_groupby_picking_id': 1
        }
        domain = [
            ('date', '>=', self.date_fr), ('date', '<=', self.date_to), ('product_id', 'in', self.product_ids.ids)
        ]
        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        action['domain'] = domain
        return action


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
        sheet.write(3, 2, 'Purchase', h3)
        sheet.write(3, 3, 'Sale', h3)
        sheet.write(3, 4, 'Adjustments In', h3)
        sheet.write(3, 5, 'Adjustments out', h3)
        sheet.write(3, 6, 'Stock in Hand', h3)
        # sheet.write(3, 7, 'Closing Stock', h3)

        row = 4


        d_sta = wizard.date_fr
        d_end = wizard.date_to
        if wizard.product_ids:
            products = wizard.product_ids
        else:
            products = self.env['product.product'].search([])
        Moves = self.env['stock.move.line'].search(
            [('date', '>=', d_sta), ('date', '<=', d_end), ('product_id', 'in', products.ids)])
        # Moves = self.env['stock.move.line'].search([])

        ClosingMoves = self.env['stock.move.line'].search([('date', '<', d_sta), ('product_id', 'in', products.ids)])

        # Products = Moves.mapped('product_id')

        # Products = self.env['product.product'].search([('id', 'in', products.ids)])
        print(products)
        for product in products:


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

            op_on_hand_qty = op_supplied_qty + op_inventory_adj

            on_hand_qty = op_on_hand_qty + supplied_qty - delivered_qty + inventory_adj - out_inventory_adj
            if not op_on_hand_qty and not supplied_qty and not delivered_qty and not inventory_adj and not out_inventory_adj:
                print("hiii")
            #
            # # closing_stock = op_on_hand_qty + supplied_qty - delivered_qty + inventory_adj - out_inventory_adj
            else:
            # if  op_on_hand_qty or supplied_qty or delivered_qty or inventory_adj or out_inventory_adj:
                sheet.write(row, 0, product.name, report_format)
                sheet.write(row, 1, op_on_hand_qty, report_format)
                sheet.write(row, 2, supplied_qty, report_format)
                sheet.write(row, 3, delivered_qty, report_format)
                sheet.write(row, 4, inventory_adj, report_format)
                sheet.write(row, 5, out_inventory_adj, report_format)
                sheet.write(row, 6, on_hand_qty, report_format)
                row += 1
            # sheet.write(row, 6, on_hand_qty, report_format)


class StockPdfReport(models.AbstractModel):
    _name = 'report.stranbys_stock_report.report_stock_template'
    _description = "Stock Report"

    def _get_report_values(self, docids, data=None, sessions=False):
        stock_wizard = self.env['stock.movement.wizard'].browse(
            docids)
        if stock_wizard:
            d_sta = stock_wizard.date_fr
            d_end = stock_wizard.date_to
            products = stock_wizard.product_ids
            if stock_wizard.product_ids:
                products = stock_wizard.product_ids
            else:
                products = self.env['product.product'].search([])

            Moves = self.env['stock.move.line'].search(
                [('date', '>=', d_sta), ('date', '<=', d_end), ('product_id', 'in', products.ids)])

            ClosingMoves = self.env['stock.move.line'].search(
                [('date', '<', d_sta), ('product_id', 'in', products.ids)])

            # Products = self.env['product.product'].search([('id', 'in', products.ids)])
            data = []

            for product in products:
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

                op_on_hand_qty = op_supplied_qty + op_inventory_adj

                on_hand_qty = op_on_hand_qty + supplied_qty - delivered_qty + inventory_adj - out_inventory_adj
                if not op_on_hand_qty and not supplied_qty and not delivered_qty and not inventory_adj and not out_inventory_adj:
                    print("hii")
                # if op_on_hand_qty or supplied_qty or delivered_qty or inventory_adj or out_inventory_adj:
                else:
                    data.append({
                        'product': product.name,
                        'op_on_hand_qty': op_on_hand_qty,
                        'supplied_qty': supplied_qty,
                        'delivered_qty': delivered_qty,
                        'inventory_adj': inventory_adj,
                        'out_inventory_adj': out_inventory_adj,
                        'on_hand_qty': on_hand_qty
                    })

        return {
            'currency_precision': 2,
            'doc_ids': docids,
            'doc_model': 'partner.statement.wizard',
            'start_dt': stock_wizard.date_fr,
            'end_dt': stock_wizard.date_to,
            'in_data': data,
            'company_id': self.env.company
        }
