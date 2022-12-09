# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class DeliveryTerms(models.Model):
    _name = 'delivery.terms'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")
