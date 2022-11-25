#!/usr/bin/env python
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class SaleOrderAssignProjectWizard(models.TransientModel):
    _name = "sale.project.assign.wizard"
    _description = "Sale Order Assign Project"

    project_id = fields.Many2one('project.project', 'Project', domain=[('state', '=', 'ongoing')], required=True)
    order_id = fields.Many2one('sale.order', 'Quotation')
    message = fields.Text(string='Message')

    def assign_project_to(self):
        if self.order_id.state == 'sale':
            for line in self.order_id.order_line.filtered(lambda r: r.display_type == False and r.is_downpayment == False ):
                vals = {

                    'project_id': self.project_id.id ,
                    'order_id': self.order_id.id,
                    'order_line_id': line.id,
                    'uom_id': line.product_uom.id,
                    'name': line.name,
                    'product_uom_qty' : line.product_uom_qty,
                    'product_id': line.product_id.id,
                    'currency_id': self.order_id.pricelist_id.currency_id.id
                }
                self.env['project.project.orderline'].create(vals)

            self.order_id.write({
                'project_id': self.project_id.id,
                # 'project_status': 'assigned',
                # 'date_start': fields.Datetime.now()
            })
            self.project_id.write({
                'partner_id' : self.order_id.partner_id.id
            })
        else:
            raise Warning(
                'This order is not confirmed, Please conifirm the quotation before assigning to a project.')
        return {'type': 'ir.actions.act_window_close'}
