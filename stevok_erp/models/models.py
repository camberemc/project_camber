# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stevok_erp(models.Model):
    _name = 'stevok_erp.stevok_erp'
    _description = 'stevok_erp.stevok_erp'

class AccountMove(models.Model):
    _inherit = 'account.move'

    bank_details = fields.Text(string="Bank Details",
                               default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                   'stevok_erp.bank_details'))