from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime


class EstimationQuotationWizard(models.TransientModel):
    _name = "estimation.quotation.wizard"
    _description = "Estimation Quotation"

    lead_id = fields.Many2one('crm.lead', 'Lead')
    estimation_id = fields.Many2one('crm.estimation', 'Estimations')
    order_id = fields.Many2one('sale.order', string="Order")

    def create_quotation(self):
        vals2 = []
        for line in self.estimation_id.product_line_ids:
            vals2.append((0, 0, {
                'product_id': line.product_id.id,
                'sequence': line.sequence,
                'product_uom_qty': line.product_qty,
                'price_unit': line.unit_rate_installation,
                'display_type': line.display_type,
                'name': line.name,
                'product_uom': line.product_uom.id,
                'tax_id': False,
                'remarks': line.remarks
            }))
        #     self.env['sale.order.line'].create(vals2)
        # self.is_quoted = True
        print(vals2)
        # print(hghgf)
        if self.order_id:
            vals = {
                'estimation_id': self.estimation_id.id,
                'name': self.estimation_id.name,
                'order_line': vals2,
            }
            new_sale = self.order_id.copy(default=vals)
        else:
            vals = {
                'partner_id': self.lead_id.partner_id.id,
                'partner_invoice_id': self.lead_id.partner_id.id,
                'partner_shipping_id': self.lead_id.partner_id.id,
                'estimation_id': self.estimation_id.id,
                'opportunity_id': self.lead_id.id,
                'estimation_type': self.lead_id.crm_type,
                'order_line': vals2,
                'name':self.estimation_id.name
            }
            order_id = self.env['sale.order'].create(vals)
        self.estimation_id.is_quoted = True
