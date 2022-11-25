# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    project_id = fields.Many2one('project.project', string="Project")

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id.id

    # @api.model_create_multi
    # def create(self, vals_list):
    #     move_lines = super(StockPicking, self).create(vals_list)
    #     for move_line in move_lines:
    #         if move_line.picking_type_id:
    #             if move_line.picking_type_id.
    #     return move_lines



class StockMove(models.Model):
    _inherit = "stock.move"

    project_id = fields.Many2one('project.project', related='picking_id.project_id', string="Project",store=True)

