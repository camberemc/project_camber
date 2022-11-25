# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AmcSystemTypes(models.Model):
    _name = 'amc.system.type'

    name = fields.Char(string='Name', required=True)
    number = fields.Char(string='Number')
    times = fields.Selection([
        ('times_in_year', 'Times in Year'),
    ], string='Times', default='times_in_year')
    description = fields.Text(string="Description")
    # contract_id = fields.Many2one('contract.order',string="Contract")


class AmcTermsCondition(models.Model):
    _name = 'amc.terms.condition'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")

class QuotationRevision(models.Model):
    _name = 'amc.quotation.revision'

    name = fields.Char(string='Name', required=True)
    last_code = fields.Integer(string='Last Code')

class ContractFollowup(models.Model):
    _name = 'contract.order.followup'
    order_id = fields.Many2one('contract.order', string='Contract')
    comments = fields.Text(string='Comments', required=True)
    date = fields.Date(string='Date', default=fields.date.today())
    attachments_ids = fields.Many2many('ir.attachment', string='Attachments')