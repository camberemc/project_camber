from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class InventoryReturn(models.Model):
    _name = 'stock.inventory.return'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    READONLY_STATES = {
        'confirm': [('readonly', True)]
    }

    name = fields.Char(string='Name', default="Draft")
    date = fields.Date(string='Date', states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Project', states=READONLY_STATES)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
    ], string='Status', default='draft')

    return_line_ids = fields.One2many('stock.inventory.return.line', 'inventory_id', string='Return List',
                                      states=READONLY_STATES)

    picking_id = fields.Many2one('stock.picking', string='Delivery Return')

    def confirm_move(self):
        code = False
        if self.name == 'Draft':
            code = self.env['ir.sequence'].next_by_code('inventory.return.code')
            self.write({
                'name': code
            })

        operation_id = int(self.env['ir.config_parameter'].sudo().get_param('inventory.return.operation_id'))

        picking_type_id = self.env['stock.picking.type'].browse(2)

        vals = {
            'origin': code or self.name,
            'location_id': picking_type_id.default_location_src_id.id,
            'location_dest_id': picking_type_id.default_location_dest_id.id,
            'picking_type_id': picking_type_id.id,
        }

        picking_id = self.env['stock.picking'].create(vals)

        for record in self.return_line_ids:
            line = picking_id.move_ids_without_package.search(
                [('product_id', '=', record.product_id.id), ('picking_id', '=', picking_id.id)], limit=1)
            if line:
                line.write({
                    'product_uom_qty': line.product_uom_qty + record.quantity
                })
            else:
                vals2 = {
                    'name': record.product_id.name,
                    'picking_id': picking_id.id,
                    'location_dest_id': picking_type_id.default_location_dest_id.id,
                    'location_id': picking_type_id.default_location_src_id.id,
                    'picking_type_id': picking_type_id.id,
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.quantity,
                    'product_uom': record.product_id.uom_id.id
                }
                self.env['stock.move'].create(vals2)

        self.write({
            'state': 'confirm',
            'picking_id': picking_id.id
        })


class InventoryReturnLine(models.Model):
    _name = 'stock.inventory.return.line'

    inventory_id = fields.Many2one('stock.inventory.return', string='Inventory Return')
    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')
    uom_id = fields.Many2one('product_id.uom_id', string='Unit of Measure', readonly=True)
    state = fields.Selection(related='inventory_id.state', string='State')
