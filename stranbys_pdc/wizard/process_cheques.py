from odoo import exceptions
from odoo import api, fields, models, _, SUPERUSER_ID


class ClearChequeWizard(models.TransientModel):
    _name = 'account.cheque.clear.wizard'

    line_ids = fields.Many2many('account.cheque', string='Cheques')

    @api.model
    def default_get(self, fields):
        """ 
        Use active_ids from the context to fetch.
        """
        record_ids = self._context.get('active_ids')
        result = super(ClearChequeWizard, self).default_get(fields)
        context = self._context.get('active_ids')

        if record_ids:
            if 'line_ids' in fields:
                selected = self.env['account.cheque'].browse(context).ids
                result['line_ids'] = selected
        return result

    # @api.multi
    def clear_cheques(self):
        if self.line_ids:
            for line in self.line_ids:
                if line.state not in ['issued', 'received']:
                    raise exceptions.Warning(
                        _('You cannot process Draft, Cleared or Returned cheques'))
        else:
            raise exceptions.Warning(
                _('No cheques selected or something went wrong'))

        for cheque in self.line_ids:
            cheque.clear_pdc()


