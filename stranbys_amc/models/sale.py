from odoo import api, fields, models, _


class AMCSale(models.Model):
    _inherit = "sale.order"

    sale_oder_type = fields.Selection([
        ('amc', 'AMC'),
        ('regular', 'Regular'),
    ], string='Sale Order Type')

    contract_id = fields.Many2one('contract.order', string='AMC Contract')