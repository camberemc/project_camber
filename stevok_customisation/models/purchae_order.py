# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrderExtend(models.Model):
    _inherit = "purchase.order"

    delivery_term_id = fields.Many2one('delivery.terms',string="Delivery Terms")
    notes = fields.Text('Terms and Conditions',default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                         'stevok_customisation.notes'))
    job_number = fields.Char(string="Job Number")