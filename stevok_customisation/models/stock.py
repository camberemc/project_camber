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


class StockMove(models.Model):
    _inherit = "stock.move"

    project_id = fields.Many2one('project.project', related='picking_id.project_id', string="Project", store=True)
