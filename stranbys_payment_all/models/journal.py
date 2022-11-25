from odoo import api, fields, models, _


class AccountJournalExtend(models.Model):
    _inherit = 'account.journal'

    is_bank = fields.Boolean(string="Is Bank")