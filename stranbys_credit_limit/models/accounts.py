# -*- coding: utf-8 -*-
## Om dinkaaya Nama

from openerp import models, fields, api, _
import logging
from datetime import datetime
from odoo import exceptions
from odoo.addons import decimal_precision as dp


class AccountAccountInheritted(models.Model):
    _inherit = "account.account"

    def get_opening_balance(self, partner_id):
        MoveLine = self.env['account.move.line']
        acount_move_line = MoveLine.sudo().search(
            [('account_id', '=', self.id), ('move_id.state', '=', 'posted'), ('partner_id', '=', partner_id)])
        return sum(acount_move_line.mapped('debit')), sum(acount_move_line.mapped('credit'))
