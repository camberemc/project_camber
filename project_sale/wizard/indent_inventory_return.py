from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime


class ProjectIntendInventoryReturnWizard(models.TransientModel):
    _name = 'project.intend.inventory.return.wizard'

    partner_id = fields.Many2one('res.partner', string='Return Address')
    reference = fields.Text(string='Reference')
    orderline_ids = fields.Many2many('project.delivery.indent', 'm2m_project_indent_wizard_ids', string='Indent Lines')
    project_id = fields.Many2one('project.project', string="Project")

    def project_inventory_return_request(self):
        if self.orderline_ids:
            lines = []
            project = False
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
                        # 'project_order_line_id': line.id
                    }])
                    project = line.project_id.id
                    line.write({
                        'qty_return_quantity':line.qty_return_quantity + line.qty_added_inventory_return,
                        'total_qty_delivered':line.total_qty_delivered - line.qty_added_inventory_return,
                        'qty_balance_delivery': line.product_qty - line.total_qty_delivered + line.qty_added_inventory_return
                    })
                line.write({
                    'qty_added_inventory_return': 0,

                })
            vals = {
                'date': fields.date.today(),
                'project_id': project,
                'return_line_ids': lines
            }
            inventory_return = self.env['stock.inventory.return'].create(vals)

        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))
