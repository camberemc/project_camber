# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class SaleOrderExtend(models.Model):
    _inherit = "sale.order"

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrderExtend, self)._prepare_invoice()
        for rec in self.order_line:
            if rec.product_id.default_code == 'DISC':
                invoice_vals.update({
                    'invoice_line_ids': [(0, 0, {
                        'display_type': rec.display_type,
                        'sequence': rec.sequence,
                        'name': rec.name,
                        'product_id': rec.product_id.id,
                        'product_uom_id': rec.product_uom.id,
                        'quantity': rec.product_uom_qty,
                        'discount': rec.discount,
                        'price_unit': rec.price_unit,
                        'tax_ids': [(6, 0, rec.tax_id.ids)],
                        'analytic_account_id': rec.order_id.analytic_account_id.id,
                        'analytic_tag_ids': [(6, 0, rec.analytic_tag_ids.ids)],
                        'sale_line_ids': [(4, rec.id)],
                    })]
                })
        return invoice_vals
