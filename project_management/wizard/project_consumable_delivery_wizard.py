from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectIndentDeliveryWizard(models.TransientModel):
    _name = 'project.delivery.indent.wizard'

    partner_id = fields.Many2one('res.partner', string='Delivery Address')
    reference = fields.Text(string='Reference')
    line_ids = fields.Many2many('project.delivery.indent', string='Indent Lines')

    def indent_delivery_request(self):
        if self.line_ids:
            for line in self.line_ids:
                if line.qty_added_delivery <= 0:
                    raise Warning(
                        _('You cannot set 0 quatity, to deliver. Remove from orderline to deliver later'))
        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))
        picking_type_id = 2
        location_id = 8
        location_dest_id = 5
        line_ids = ['id', 'in', self.line_ids.ids]
        group_projects = self.line_ids.read_group(
            [line_ids], fields=['project_id', 'product_id'], groupby='project_id')

        if self.partner_id:
            vals = {
                'partner_id': self.partner_id.id,
                'scheduled_date': datetime.now(),
                'state': 'draft',
                'origin': group_projects[0]['project_id'][1],
                'picking_type_id': picking_type_id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            }
        do_id = self.env['stock.picking'].create(vals)

        for line in self.line_ids:
            if not line.product_id:
                raise UserError('Please add the products to be delivered before making the delivery')
            vals2 = {
                'product_id': line.product_id.id,
                'name': line.name,
                'picking_id': do_id.id,
                'product_uom_qty': line.qty_added_delivery,
                'product_uom': line.product_id.uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            }
            move_id = self.env['stock.move'].create(vals2)

            vals3 = {
                'move_line_id': move_id.id,
                'project_order_line_id': line.id,
                'qty': line.qty_added_delivery,
            }

            added = line.qty_added_delivery

            line.write({
                'qty_added_delivery': 0,
                'delivered_qty': line.delivered_qty + added,
                'picking_ids': [(4, do_id.id)],
                'processed': True,
                'is_readonly':True
            })
