from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime


class ProjectInventoryReturnWizard(models.TransientModel):
    _name = 'project.inventory.return.wizard'

    partner_id = fields.Many2one('res.partner', string='Return Address')
    reference = fields.Text(string='Reference')
    orderline_ids = fields.Many2many(
        'project.project.orderline', 'm2m_project_oderline_delivery_wizard_ids', string='Order Lines')
    project_id = fields.Many2one('project.project', string="Project")

    def project_inventory_return_request(self):
        if self.orderline_ids:
            lines = []
            for line in self.orderline_ids:
                if line.qty_added_inventory_return <= 0:
                    raise Warning(
                        _('You cannot set 0 quantity, to Return'))
                else:
                    lines.append([0, 0, {
                        'product_id': line.product_id.id,

                        'project_id': line.project_id.id,
                        'uom_id': line.product_id.uom_id.id,
                        'quantity': line.qty_added_inventory_return,
                        'project_order_line_id':line.id
                    }])
                line.write({
                    'qty_added_inventory_return': 0,
                })
            vals = {
                'date': fields.date.today(),
                'project_id': self.project_id.id,
                'return_line_ids': lines
            }
            inventory_return = self.env['stock.inventory.return'].create(vals)

        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))

