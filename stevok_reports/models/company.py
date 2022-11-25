# -*- coding: utf-8 -*-
# Copyright 2016, 2019 Openworx
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import models, fields

class ResCompany(models.Model):

    _inherit = 'res.company'

    header = fields.Binary(string="Header")
    footer = fields.Binary(string="Footer")
