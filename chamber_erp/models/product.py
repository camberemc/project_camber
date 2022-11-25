from odoo import api, fields, models


class ProjectProductTemplate(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.product.brand', string='Brand')
    is_quotation_product = fields.Boolean(string="Quotation Product")
    estimation_type = fields.Selection([
        ('product', 'Product Estimation'),
        ('service', 'Service Estimation')
    ], string='Estimation Type')
    project_consu = fields.Boolean(string='Project Consumable')

    @api.onchange('is_quotation_product')
    def _onchange_is_quotation_product(self):
        for record in self:
            record.product_variant_id.is_quotation_product = record.is_quotation_product


class ProjectProduct(models.Model):
    _inherit = 'product.product'

    is_quotation_product = fields.Boolean(string="Quotation Product")


class ProductBrand(models.Model):
    _name = 'product.product.brand'

    name = fields.Char(string='Brand Name')



