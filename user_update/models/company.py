# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, tools


class Company(models.Model):
    _inherit = 'res.company'


    company_stamp = fields.Binary(string="Company Stamp")
    file_name = fields.Char(string="File Name")
