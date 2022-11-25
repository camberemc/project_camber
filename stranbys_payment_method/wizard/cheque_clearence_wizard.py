from odoo import exceptions
from odoo import api, fields, models, _, SUPERUSER_ID


class ClearChequeWizard(models.TransientModel):
    _name = 'account.cheque.clear.wizard'
    _description = 'Clearence Wizard'

    line_ids = fields.Many2many('account.payment', string='Cheques')

    date = fields.Date('Date', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal', domain=[('type', '=', 'bank')])
    clearence_account_id = fields.Many2one('account.payment.method.line', string='Clearence Account', required=True)

    payment_type = fields.Char('Payment Type')


    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        self.clearence_account_id = False


    def update_some(self):
        self.line_ids.write({
            'cleared_date' : self.date,
            'clearence_account_id' : self.clearence_account_id.id
        })

        return {
        'name': _('Cheque Clearence'),
        'view_mode': 'form',
        'view_id': False,
        'res_model': self._name,
        'domain': [],
        'context': dict(self._context, active_ids=self.line_ids),
        'type': 'ir.actions.act_window',
        'target': 'new',
        'res_id': self.id,
    }

    # @api.model
    # def default_get(self, fields):
    #     """ 
    #     Use active_ids from the context to fetch.
    #     """
    #     record_ids = self._context.get('active_ids')
    #     result = super(ClearChequeWizard, self).default_get(fields)
    #     context = self._context.get('active_ids')

    #     if record_ids:
    #         if 'line_ids' in fields:
    #             selected = self.env['account.cheque'].browse(context).filtered(
    #                 lambda r: not r.hide_clearence
    #             ).ids
    #             result['line_ids'] = selected
    #     return result


    def clear_cheques(self):
        for record in self.line_ids:
            record.action_clear()

