from odoo import api, fields, models, _
from datetime import datetime, date


class AccountMove(models.Model):
    _inherit = 'account.move'

    create_do = fields.Boolean(string="Is do")
    picking_ids = fields.Many2many('stock.picking', string='Delivery Details')

    def create_delivery(self):
        for rec in self:
            if not rec.create_do:
                if rec.move_type == 'out_invoice':
                    picking_type_id = 2
                if rec.move_type == 'in_invoice':
                    picking_type_id = 1
                picking_type = self.env['stock.picking.type'].search([('id', '=', picking_type_id)])
                location_id = picking_type.default_location_src_id.id
                location_dest_id = picking_type.default_location_dest_id.id
                vals = {
                    'picking_type_id': picking_type.id,
                    'partner_id': rec.partner_id.id,
                    'scheduled_date': datetime.now(),
                    'state': 'draft',
                    'origin': rec.name,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    'move_type': 'direct',
                    'invoice_id': rec.id
                }

                do_id = self.env['stock.picking'].create(vals)
                vals2 = {}
                for line in self.invoice_line_ids:
                    bom_ids = self.env['mrp.bom'].search([('product_tmpl_id', '=', line.product_id.product_tmpl_id.id)],
                                                         limit=1)
                    if bom_ids:
                        ref_count = line.quantity / bom_ids.product_qty
                        print(line.product_id.name)
                        print(ref_count)
                        print(bom_ids)
                        for bom in bom_ids.bom_line_ids:
                            print(bom.product_qty)
                            print(bom.product_qty * ref_count)

                            vals2 = {
                                'product_id': bom.product_id.id,
                                'name': line.name,
                                'picking_id': do_id.id,
                                'product_uom_qty': bom.product_qty * ref_count,
                                'product_uom': bom.product_uom_id.id,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'quantity_done': bom.product_qty * ref_count
                            }
                            self.env['stock.move'].create(vals2)
                    else:
                        if line.product_id.type != 'service':
                            # print(line.product_id.bom_ids)
                            vals2 = {
                                'product_id': line.product_id.id,
                                'name': line.name,
                                'picking_id': do_id.id,
                                'product_uom_qty': line.quantity,
                                'product_uom': line.product_id.uom_id.id,
                                'location_id': location_id,
                                'location_dest_id': location_dest_id,
                                'quantity_done': line.quantity
                            }
                            self.env['stock.move'].create(vals2)
                do_id.action_confirm()
                do_id.button_validate()
                rec.write({
                    'create_do': True,
                    'picking_ids': [(6, 0, [do_id.id])]
                })

                # move_ine_ids_without_package = []
                # for line in self.invoice_line_ids:
                #     bom_ids = self.env['mrp.bom'].search([('product_id', '=', line.product_id.id)],limit=1)
                #     if bom_ids:
                #         ref_count = line.quantity / bom_ids.product_qty
                #         for bom in bom_ids:
                #             move_ine_ids_without_package.append((0, 0, {
                #                 'product_id': bom.product_id.id,
                #                 # 'name': line.name,
                #                 'product_uom_qty': bom.product_qty*ref_count,
                #                 'product_uom_id': bom.product_uom_id.id,
                #                 'location_id': location_id,
                #                 'location_dest_id': location_dest_id,
                #                 # 'qty_done': line.quantity
                #             }))
                #             move = self.env['stock.move'].create
                #
                #
                #     # if line.product_id.type != 'service':
                #     #     move_ine_ids_without_package.append((0, 0, {
                #     #         'product_id': line.product_id.id,
                #     #         # 'name': line.name,
                #     #         'product_uom_qty': line.quantity,
                #     #         'product_uom_id': line.product_id.uom_id.id,
                #     #         'location_id': location_id,
                #     #         'location_dest_id': location_dest_id,
                #     #         # 'qty_done': line.quantity
                #     #     }))
                #
                # do_id = self.env['stock.picking'].create(vals)
                # # do_id.action_confirm()
                # # do_id.button_validate()
                # rec.write({
                #     'create_do': True,
                #     'picking_ids': [(6, 0, [do_id.id])]
                # })

# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     bom_id = fields.Many2one('mrp.bom', string="Bom")
