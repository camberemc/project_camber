from odoo import api, fields, models, _


class AccountMoveExtent(models.Model):
    _inherit = 'account.move'

    discount = fields.Float(string="Discount", readonly=1)