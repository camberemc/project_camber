from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectDeliveryWizard(models.TransientModel):
    _name = 'project.delivery.wizard'

    partner_id = fields.Many2one('res.partner', string='Delivery Address')
    reference = fields.Text(string='Reference')
    orderline_ids = fields.Many2many(
        'project.project.orderline', 'm2m_project_oderline_delivery_ids', string='Order Lines')

    def project_delivery_request(self):
        if self.orderline_ids:
            for line in self.orderline_ids:
                if line.qty_added_delivery <= 0:
                    raise Warning(
                        _('You cannot set 0 quatity, to deliver. Remove from orderline to deliver later'))
        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))

        picking_type_id = self.env['stock.picking.type'].browse(2)
        location_id = picking_type_id.default_location_src_id.id
        location_dest_id = picking_type_id.default_location_dest_id.id
        line_ids = ['id', 'in', self.orderline_ids.ids]
        group_projects = self.orderline_ids.read_group(
            [line_ids], fields=['project_id', 'product_id'], groupby='project_id')

        if self.partner_id:
            vals = {
                'partner_id': self.partner_id.id,
                'scheduled_date': datetime.now(),
                'state': 'draft',
                'origin': group_projects[0]['project_id'][1],
                'picking_type_id': picking_type_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
            }
        do_id = self.env['stock.picking'].create(vals)

        for line in self.orderline_ids:
            vals2 = {
                'product_id': line.product_id.id,
                'name': line.name,
                'picking_id': do_id.id,
                'product_uom_qty': line.qty_added_delivery,
                'product_uom': line.uom_id.id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'picking_type_id': picking_type_id.id,
            }
            move_id = self.env['stock.move'].create(vals2)

            vals3 = {
                'move_line_id': move_id.id,
                'project_order_line_id': line.id,
                'qty': line.qty_added_delivery,
            }

            self.env['project.delivery.line'].create(vals3)

            line.write({
                'qty_added_delivery': 0,
            })
