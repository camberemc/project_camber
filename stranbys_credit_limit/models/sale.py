# -*- coding: utf-8 -*-
## Om dinkaaya Nama

from openerp import models, fields, api, _
import logging
from datetime import datetime
from odoo.exceptions import UserError


class SalesOrderExtented(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    partner_recev_amount = fields.Float(string='Receivable Amount', related='partner_id.receivable_amount')

    @api.onchange('partner_id', 'state')
    def change_partner_id(self):
        if self.partner_id.limit_ok:
            raise UserError("Credit Limit has been reached..%d " % self.partner_id.credit_limit)

    @api.constrains('state')
    def _check_credit_limit(self):
        for record in self:
            credit_limit = record.partner_id.receivable_amount + record.amount_total
            if record.partner_id.credit_limit > 0 and credit_limit > record.partner_id.credit_limit and not record.partner_id.unblock_limit:
                raise UserError("Credit Limit has been reached.. \n Credit Limit: %d \n Balance Limit: %d " % (
                record.partner_id.credit_limit, record.partner_id.credit_limit - record.partner_id.receivable_amount))
