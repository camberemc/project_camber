# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrderExtend(models.Model):
    _inherit = "purchase.order"

    delivery_term_id = fields.Many2one('delivery.terms', string="Delivery Terms")
    remarks = fields.Char(string="Remarks")

    state = fields.Selection([
        ('draft_new', 'Draft'),
        ('approval_pending', 'Pending of Approval'),
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft_new', tracking=True)

    def approve_quotation(self):
        self.write({
            'state': 'draft'
        })

    def send_approve_quotation(self):
        self.write({
            'state': 'approval_pending'
        })

    def button_draft(self):
        self.write({'state': 'draft_new'})
        return {}



