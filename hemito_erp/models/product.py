from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    vendor_id = fields.Many2one('res.partner', string="Vendor")

    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'), ('product', 'Storable Product')], string='Product Type', default='product',
        required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
