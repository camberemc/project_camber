from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class StockPickingExtend(models.Model):
    _inherit = 'stock.picking'

    project_id = fields.Many2one('project.project', string="Project")
    is_delivered = fields.Boolean(string="Delivered")
    # is_sale = fields.Boolean(string="Sale", compute='_compute_sale', store=True, copy=False)
    #
    # # @api.depends('operation_type_id')
    # def _compute_sale(self):
    #     for rec in self:
    #         if rec.operation_type_id.code == 'incoming':
    #             rec.is_sale = False
    #         else:
    #             rec.is_sale = True

    def create_delivery(self):
        action = self.env.ref('chamber_erp.act_stock_out').read()[0]
        action['context'] = dict(
            self.env.context,
            default_picking_id=self.id,
        )
        #     print(action)
        return action


class StockMoveExtend(models.Model):
    _inherit = 'stock.move'

    project_id = fields.Many2one('project.project', related='picking_id.project_id', string="Project")
