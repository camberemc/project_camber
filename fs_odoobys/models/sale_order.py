from odoo import api, fields, models, _


class SalesOrderExtent(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    # quotation_ref = fields.Char("Quotation Ref")
    quotation_reverse = fields.Char("Quotation Revise")
    attention = fields.Char("Attention")
    project_name = fields.Text("Project Name")
    work_location = fields.Char("Work Location")
    scope_of_work = fields.Text("Scope Of Work", default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
        'fs_odoobys.scope_of_work'))
    safety_hse_quality = fields.Text("Safety, HSE & Quality",
                                     default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                         'fs_odoobys.safety_hse_quality'))
    reference_drawing = fields.Text("Reference Drawings",
                                    default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                        'fs_odoobys.reference_drawing'))
    notes = fields.Text("Notes",
                        default=lambda self: self.env['ir.config_parameter'].sudo().get_param('fs_odoobys.notes'))

    discount = fields.Float(string="Discount", compute='_compute_sale_discount', store=True)

    @api.depends('order_line', 'order_line.product_id', 'order_line.price_unit')
    def _compute_sale_discount(self):
        for rec in self:
            rec.discount = False
            for line in rec.order_line:
                if line.product_id:
                    if line.product_id.default_code == 'DISC':
                        rec.discount = line.price_unit

    def _prepare_invoice(self):
        invoice_vals = super(SalesOrderExtent, self)._prepare_invoice()
        invoice_vals['discount'] = self.discount
        return invoice_vals
