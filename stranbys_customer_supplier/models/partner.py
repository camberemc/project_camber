from odoo import models, fields, api, _


class ResPartnerExtend(models.Model):
    _inherit = 'res.partner'
    is_supplier = fields.Boolean(string="Is a Supplier")
    is_customer = fields.Boolean(string="Is a Customer")

