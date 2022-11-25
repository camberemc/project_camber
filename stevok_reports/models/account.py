# -*- coding: utf-8 -*-

from odoo import models, fields, api



class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_details = fields.Text(string="Bank Details",
                               default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                   'bank_details'))