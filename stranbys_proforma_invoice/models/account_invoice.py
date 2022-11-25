from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime, date
from odoo.addons import decimal_precision as dp


class AccountMoveExtented(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    # state = fields.Selection(selection_add=[('proforma', 'Proforma')])
    # name = fields.Char(string='Number', default='/', copy=False, readonly=False, index=True, tracking=True)

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('proforma', 'Proforma'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')
    proforma_name = fields.Char(string='Voucher Name', default="Draft")

    def reset_name(self):
        if self.state == 'draft':
            self.update({
                'name': False,
                'proforma_name': 'Draft'
            })

    # @api.depends('posted_before', 'state', 'journal_id', 'date')
    # def _compute_name(self):
    #     res = super(AccountMoveExtented, self)._compute_name()
    #     print(res)
    #     return res

    def create_proforma(self):
        if self.state == 'draft':
            vals = {}
            if self.proforma_name == 'Draft':
                code = self.env['ir.sequence'].next_by_code('account.performa.invoice.code')
                vals = {
                    'proforma_name': code,
                    # 'name': code
                }
            # else:
            #     vals = {
            #         'name': self.proforma_name
            #     }
            vals['state'] = 'proforma'
            vals['invoice_date'] = date.today()
            self.write(vals)
        else:
            raise UserError('Can only set draft invoice to Proforma')

    def set_to_draft(self):
        self.write({
            'state': 'draft',
            # 'name': False
        })
