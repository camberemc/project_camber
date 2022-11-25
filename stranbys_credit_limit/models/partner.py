from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_limit = fields.Float("Credit Limit")
    receivable_amount = fields.Float("Receivable Amount", compute="_check_credit_limit")
    limit_ok = fields.Boolean(compute="_check_credit_limit")
    unblock_limit = fields.Boolean(string='Unblock Credit Limit')
    credit_days = fields.Float(string="Credit Days")

    def _check_credit_limit(self):
        for record in self:
            record.limit_ok = False
            limit_dr, limit_cr = record.property_account_receivable_id.get_opening_balance(record.id)
            record.receivable_amount = limit_dr - limit_cr
            if record.credit_limit > 0 and record.receivable_amount >= record.credit_limit and not record.unblock_limit:
                record.limit_ok = True
