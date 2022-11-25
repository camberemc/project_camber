from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectStockOut(models.Model):
    _name = 'project.stock.out'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    project_id = fields.Many2one('project.project', string='Project')
    partner_id = fields.Many2one('res.partner', related="project_id.partner_id", string="Customer", store=True)
    #                                   )
    picking_id = fields.Many2one('stock.picking', string='Delivery Return')

    def confirm_move(self):
        if self.picking_id.picking_type_id.id == 1:
            picking_type_id = self.env['stock.picking.type'].browse(1)
            vals = {
                'origin': self.picking_id.name,
                'location_id': picking_type_id.default_location_src_id.id,
                'location_dest_id': picking_type_id.default_location_dest_id.id,
                'picking_type_id': picking_type_id.id,
                'partner_id': self.partner_id.id
            }
            picking_id = self.env['stock.picking'].create(vals)
            for line in self.picking_id.move_ids_without_package:
                vals2 = {
                    'name': line.product_id.name,
                    'picking_id': picking_id.id,
                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'picking_type_id': picking_type_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity_done,
                    'quantity_done': line.quantity_done,
                    'product_uom': line.product_uom.id
                }
                move_id = self.env['stock.move'].create(vals2)
            picking_id.action_confirm()
            picking_id.project_id = self.project_id.id
            self.picking_id.is_delivered = True
            picking_id.is_delivered = True
        else:
            raise UserError(_('You Cannot Deliver this picking '))


class ProjectStockOutLine(models.Model):
    _name = 'project.stock.out.line'

    inventory_id = fields.Many2one('project.stock.out', string='Inventory Return')
    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('product_id.uom_id', string='Unit of Measure', readonly=True)
