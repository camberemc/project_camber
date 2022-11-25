# -*- coding: utf-8 -*-
## Om dinkaaya Nama

from openerp import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveExtent(models.Model):
    _inherit = 'account.move'

    credit_days = fields.Float(string="Credit Days", related='partner_id.credit_days')

    @api.onchange('invoice_date', 'invoice_date_due', 'invoice_payment_term_id')
    def _onchange_date(self):
        if self.invoice_date and self.invoice_date_due and self.move_type == 'out_invoice':
            date = (self.invoice_date_due - self.invoice_date).days
            if date > self.credit_days:
                raise UserError("Exceed Credit Days of  %s " % self.partner_id.name)

    # @api.compute('invoice_date', 'invoice_date_due')
    # def _get_credit_days(self):
    #     for rec in self:
    #         if rec.invoice_date and rec.invoice_date_due:
