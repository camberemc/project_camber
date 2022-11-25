from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectPurchaseWizard(models.TransientModel):
    _name = 'project.purcahase.wizard'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')
    partner_id = fields.Many2one('res.partner', string='Supplier')
    create_new = fields.Boolean(string='Create New')
    reference = fields.Text(string='Reference')
    orderline_ids = fields.Many2many(
        'project.project.orderline', 'm2m_project_oderline_purchase_ids', string='Order Lines')

    # @api.model
    # def default_get(self, fields):
    #     """
    #     Use active_ids from the context to fetch.
    #     """
    #     record_ids = self._context.get('active_ids')
    #     result = super(ProjectPurchaseWizard, self).default_get(fields)
    #     context = self._context.get('active_ids')
    #
    #     #selecting records from active id
    #     if record_ids:
    #         if 'orderline_ids' in fields:
    #             selected = self.env['project.project.orderline'].browse(
    #                 context).ids
    #             result['orderline_ids'] = selected
    #
    #     return result

    


    def project_purchase_request(self):
        if self.orderline_ids:
            for line in self.orderline_ids:
                if line.qty_added <= 0:
                    raise Warning(
                        _('You cannot set 0 quatity, to purchase. Remove from orderline to purchase later'))
        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))
        line_ids = ['id', 'in', self.orderline_ids.ids]
        po_id = self.purchase_order_id
        if self.create_new:
            vals = {
                'partner_id': self.partner_id.id,
                'company_id': self.env.user.company_id.id,
                'currency_id': self.partner_id.property_purchase_currency_id.id or self.env.user.company_id.currency_id.id,
                'date_order': datetime.now(),
                'name': self.env['ir.sequence'].next_by_code('purchase.order'),
                'state': 'draft',
                'create_uid' : self.env.uid
            }
            po_id = self.env['purchase.order'].create(vals)
        for line in self.orderline_ids:
            fpos = po_id.fiscal_position_id
            if self.env.uid == SUPERUSER_ID:
                company_id = self.env.user.company_id.id
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id.filtered(
                    lambda r: r.company_id.id == company_id))
            else:
                taxes_id = fpos.map_tax(line.product_id.supplier_taxes_id)
            order_line_id = self.env['purchase.order.line'].search([('order_id', '=', po_id.id), ('product_id', '=', line.product_id.id)], limit=1)
            if order_line_id:
                order_line_id.write({
                    'product_qty' : line.qty_added + order_line_id.product_qty,
                })
            else:
                vals2 = {
                    'name' : line.product_id.name,
                    'order_id': po_id.id,
                    'product_id': line.product_id.id,
                    'product_qty' : line.qty_added,
                    'product_uom': line.product_id.uom_id.id,
                    'price_unit' : line.product_id.list_price,
                    'date_planned': datetime.now(),
                    'taxes_id': [(4, taxes_id.id)],
                    'create_uid' : self.env.uid,
                }
                order_line_id = self.env['purchase.order.line'].create(vals2)


            vals3 = {
                'project_order_line_id' : line.id,
                'order_line_id' : order_line_id.id,
                'qty' : line.qty_added
            }
            self.env['project.purchase.line'].create(vals3)


            line.write({
                'qty_added' : 0,
            })