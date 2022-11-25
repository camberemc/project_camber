from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp



class ProductTemplateExt(models.Model):
    _inherit = 'product.template'

    estimation_type = fields.Selection([
        ('product', 'Product Estimation'),
        ('service', 'Service Estimation')
    ], string='Estimation Type')
    project_consu = fields.Boolean(string='Project Consumable')
    is_amc = fields.Boolean(string="Amc")