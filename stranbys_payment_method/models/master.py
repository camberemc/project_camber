# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools  # type: ignore


class BankMaster(models.Model):
    _name = 'account.partner.bank'
    _description = 'Partner Banks'

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id

    @api.model
    def _compute_company_id(self):
        return self.env.company

    company_id = fields.Many2one(
        'res.company', string='Company', store=True, readonly=True, default=_compute_company_id)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=_get_default_currency)

    name = fields.Char(string='Bank Name', required=True)