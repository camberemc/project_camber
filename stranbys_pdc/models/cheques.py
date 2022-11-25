from datetime import datetime

from openerp import models, fields, api, _
from odoo.exceptions import UserError


class Cheque(models.Model):
    _name = 'account.cheque'
    _description = 'Cheques'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # def unlink(self):
    #     if self.cheque_sequence != 'Draft':
    #         raise UserError('Cannot delete number generated cheques')
    #     return super(Cheque, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        # TDE FIXME: should probably be copy_data
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = self.name + " (COPY)"
        return super(Cheque, self).copy(default=default)

    name = fields.Char(string='Cheque Number', required=True, track_visibility='onchange', copy=False)
    cheque_type = fields.Selection([
        ('pay', 'Pay'),
        ('receive', 'Receive'),
    ], string='Type', required=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('received', 'Received'),
        ('cleared', 'Cleared'),
        ('return', 'Return'),
    ], string='Status', default='draft', track_visibility='onchange', copy=False)

    currency_id = fields.Many2one('res.currency', string='Currency')
    journal_id = fields.Many2one('account.journal', string='Bank Account', domain=([('type', '=', 'bank')]),
                                 required=True)

    bank_name = fields.Char(string='Bank Name', track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Float(string='Amount', track_visibility='onchange')
    issue_date = fields.Date(string='Issue Date')
    date = fields.Date(string='Cheque Date', copy=False)
    cleared_date = fields.Date(string='Cleared Date', track_visibility='onchange', copy=False)
    returned_date = fields.Date(string='Returned Date', track_visibility='onchange', copy=False)

    pdc_entry_id = fields.Many2one('account.move', string='Cheque Entry', copy=False)
    payment_entry_id = fields.Many2one('account.move', string='Payment Entry', copy=False)
    reverse_entry_id = fields.Many2one('account.move', string='Reverse Entry', copy=False)

    narration = fields.Text(string='Narration')
    transaction = fields.Char(string='Transaction Details')
    voucher_no = fields.Char(string='Voucher')
    cheque_sequence = fields.Char(string="Voucher Number", copy=False, default='Draft')
    reconciled_invoice_ids = fields.Many2many('account.move', string="Reconciled Invoices",
                                              compute='_compute_stat_buttons_from_reconciliation',
                                              help="Invoices whose journal items have been reconciled with these payments.")
    reconciled_invoices_count = fields.Integer(string="# Reconciled Invoices",
                                               compute="_compute_stat_buttons_from_reconciliation")
    reconciled_bill_ids = fields.Many2many('account.move', string="Reconciled Bills",
                                           compute='_compute_stat_buttons_from_reconciliation',
                                           help="Invoices whose journal items have been reconciled with these payments.")
    reconciled_bills_count = fields.Integer(string="# Reconciled Bills",
                                            compute="_compute_stat_buttons_from_reconciliation")
    reconciled_statement_ids = fields.Many2many('account.bank.statement', string="Reconciled Statements",
                                                compute='_compute_stat_buttons_from_reconciliation',
                                                help="Statements matched to this payment")
    reconciled_statements_count = fields.Integer(string="# Reconciled Statements",
                                                 compute="_compute_stat_buttons_from_reconciliation")

    # @api.model
    # def create(self, values):
    #     result = super(Cheque, self).create(values)
    #     date = datetime.today()
    #     if result.cheque_type == 'pay':
    #         if not values.get('cheque_sequence', False) or values['cheque_sequence'] == _('New'):
    #             result.cheque_sequence = 'PAY/' + str(date.year) + '/' + self.env['ir.sequence'].next_by_code(
    #                 'account.cheque.send') or _('New')
    #     if result.cheque_type == 'receive':
    #         if not values.get('cheque_sequence', False) or values['cheque_sequence'] == _('New'):
    #             result.cheque_sequence = 'RCVQ/' + str(date.year) + '/' + self.env['ir.sequence'].next_by_code(
    #                 'account.cheque.receipts') or _('New')
    #     return result

    def pdc_journal(self):
        id = int(self.env['ir.config_parameter'].sudo().get_param('stranbys_pdc.default_pdc_journal_id')),
        print(id)
        journal_id = self.env['account.journal'].browse(id)
        cr = journal_id.payment_credit_account_id.id
        dr = journal_id.payment_debit_account_id.id
        vals = {
            'cr': journal_id.payment_credit_account_id.id,
            'dr': journal_id.payment_debit_account_id.id,
            'id': journal_id.id
        }
        return vals

    def create_pdc(self):
        cheque_sequence = 'Draft'
        if self.amount <= 0:
            raise UserError("Please enter a valid amount")
        if self.cheque_type == 'receive':
            cr_account_id = self.partner_id.property_account_receivable_id.id
            dr_account_id = self.pdc_journal().get('dr')
            name = 'Received Cheque No:' + self.name,
            state = 'received'
            if self.cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.receipts')

        elif self.cheque_type == 'pay':
            cr_account_id = self.pdc_journal().get('cr')
            dr_account_id = self.partner_id.property_account_payable_id.id
            name = 'Paid Cheque No:' + self.name,
            state = 'issued'
            if self.cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.send')
        else:
            raise UserError('Failed')

        json_obj = {
            'journal_id': self.pdc_journal().get('id'),
            'cr_account_id': cr_account_id,
            'dr_account_id': dr_account_id,
            'amount': self.amount,
            'name': name,
            'state': state,
            'date': self.date,
            'ref': name
        }
        move_id = self._process_entry(json_obj)
        self.write(
            {
                'pdc_entry_id': move_id.id,
                'state': state,
                'cheque_sequence': cheque_sequence
            }
        )

    def clear_pdc(self):
        if self.cheque_type == 'receive':
            cr_account_id = self.pdc_journal().get('dr')
            dr_account_id = self.journal_id.payment_debit_account_id.id
            name = 'Received Cheque No:' + self.name,

        elif self.cheque_type == 'pay':
            cr_account_id = self.journal_id.payment_credit_account_id.id
            dr_account_id = self.pdc_journal().get('cr')
            name = 'Paid Cheque No:' + self.name,

        else:
            raise UserError('Failed')

        if not self.cleared_date:
            raise UserError('Please enter cleared date before clearing the cheque')

        json_obj = {
            'journal_id': self.journal_id.id,
            'cr_account_id': cr_account_id,
            'dr_account_id': dr_account_id,
            'amount': self.amount,
            'name': name,
            'date': self.cleared_date,
            'ref': name
        }
        move_id = self._process_entry(json_obj)

        self.write(
            {
                'payment_entry_id': move_id.id,
                'state': 'cleared'
            }
        )

    def _process_entry(self, json_obj):
        # ref, name, cr_account_id, dr_account_id, state, amount
        vals = {
            'date': json_obj.get('date'),
            'journal_id': json_obj.get('journal_id'),
            'ref': json_obj.get('ref')[0],
            'narration': self.narration,
            'line_ids': [
                (0, 0, {
                    'name': json_obj.get('name')[0],
                    'account_id': json_obj.get('cr_account_id'),
                    'partner_id': self.partner_id.id,
                    'debit': 0.0,
                    'credit': json_obj.get('amount'),
                }),
                (0, 0, {
                    'name': json_obj.get('name')[0],
                    'account_id': json_obj.get('dr_account_id'),
                    'partner_id': self.partner_id.id,
                    'credit': 0.0,
                    'debit': json_obj.get('amount'),
                }),
            ]
        }
        move_id = self.env['account.move'].create(vals)
        move_id.post()
        return move_id

    def reverse_pdc(self):
        if not self.returned_date:
            raise UserError('Please enter Return date before reversing the entry')
        if self.pdc_entry_id:
            move_reversal = self.env['account.move.reversal'].with_context(
                {'active_ids': [self.pdc_entry_id.id], 'active_id': self.pdc_entry_id.id,
                 'active_model': 'account.move'}).create({
                'refund_method': 'cancel',
                'journal_id': self.pdc_entry_id.journal_id.id,
                'date': self.returned_date

            })
            reversal = move_reversal.reverse_moves()
            reverse_move = self.env['account.move'].browse(reversal['res_id'])
            reverse_move.date = self.returned_date
            self.write(
                {
                    'reverse_entry_id': reverse_move,
                    'state': 'return'
                }
            )

    def open_payment_matching_screen(self):
        # Open reconciliation view for customers/suppliers
        # move_line_id = False
        # for move_line in self.line_ids:
        #     if move_line.account_id.reconcile:
        #         move_line_id = move_line.id
        #         break
        if not self.partner_id:
            raise UserError(_("Payments without a customer can't be matched"))

        # partner_ids = [self.partner_id.commercial_partner_id.id, self.partner_id.id]
        partner_ids = [self.partner_id.commercial_partner_id.id, self.partner_id.id]
        partner_ids.extend(self.partner_id.commercial_partner_id.child_ids.ids)
        # raise UserError(str(partner_ids))
        action_context = {'company_ids': [self.env.user.company_id.id], 'partner_ids': partner_ids}
        action_context.update({'mode': 'customers'})
        if self.cheque_type == 'pay':
            action_context.update({'mode': 'suppliers'})
        action_context.update({'move_line_id': self.pdc_entry_id.id})
        return {
            'type': 'ir.actions.client',
            'tag': 'manual_reconciliation_view',
            'context': action_context,
        }

    @api.depends('pdc_entry_id.line_ids.matched_debit_ids', 'pdc_entry_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        print("ahdgahgsd")
        ''' Retrieve the invoices reconciled to the payments through the reconciliation (account.partial.reconcile). '''
        stored_payments = self.filtered('id')
        if not stored_payments:
            self.reconciled_invoice_ids = False
            self.reconciled_invoices_count = 0
            self.reconciled_bill_ids = False
            self.reconciled_bills_count = 0
            self.reconciled_statement_ids = False
            self.reconciled_statements_count = 0
            return

        self.env['account.move'].flush()
        self.env['account.move.line'].flush()
        self.env['account.partial.reconcile'].flush()

        self._cr.execute('''
                SELECT
                    payment.id,
                    ARRAY_AGG(DISTINCT invoice.id) AS invoice_ids,
                    invoice.move_type
                
                FROM account_cheque payment
                JOIN account_move move ON move.id = payment.pdc_entry_id
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_partial_reconcile part ON
                    part.debit_move_id = line.id
                    OR
                    part.credit_move_id = line.id
                JOIN account_move_line counterpart_line ON
                    part.debit_move_id = counterpart_line.id
                    OR
                    part.credit_move_id = counterpart_line.id
                JOIN account_move invoice ON invoice.id = counterpart_line.move_id
                JOIN account_account account ON account.id = line.account_id
                WHERE account.internal_type IN ('receivable', 'payable')
                    AND payment.id IN %(payment_ids)s
                    AND line.id != counterpart_line.id
                    AND invoice.move_type in ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
                GROUP BY payment.id, invoice.move_type
            ''', {
            'payment_ids': tuple(stored_payments.ids)
        })
        query_res = self._cr.dictfetchall()
        self.reconciled_invoice_ids = self.reconciled_invoices_count = False
        self.reconciled_bill_ids = self.reconciled_bills_count = False
        print(query_res)
        for res in query_res:
            pay = self.browse(res['id'])
            if res['move_type'] in self.env['account.move'].get_sale_types(True):
                pay.reconciled_invoice_ids += self.env['account.move'].browse(res.get('invoice_ids', []))
                pay.reconciled_invoices_count = len(res.get('invoice_ids', []))
            else:
                pay.reconciled_bill_ids += self.env['account.move'].browse(res.get('invoice_ids', []))
                pay.reconciled_bills_count = len(res.get('invoice_ids', []))

        self._cr.execute('''
                SELECT
                    payment.id,
                    ARRAY_AGG(DISTINCT counterpart_line.statement_id) AS statement_ids
                FROM account_payment payment
                JOIN account_move move ON move.id = payment.move_id
                JOIN account_journal journal ON journal.id = move.journal_id
                JOIN account_move_line line ON line.move_id = move.id
                JOIN account_account account ON account.id = line.account_id
                JOIN account_partial_reconcile part ON
                    part.debit_move_id = line.id
                    OR
                    part.credit_move_id = line.id
                JOIN account_move_line counterpart_line ON
                    part.debit_move_id = counterpart_line.id
                    OR
                    part.credit_move_id = counterpart_line.id
                WHERE (account.id = journal.payment_debit_account_id OR account.id = journal.payment_credit_account_id)
                    AND payment.id IN %(payment_ids)s
                    AND line.id != counterpart_line.id
                    AND counterpart_line.statement_id IS NOT NULL
                GROUP BY payment.id
            ''', {
            'payment_ids': tuple(stored_payments.ids)
        })
        query_res = dict((payment_id, statement_ids) for payment_id, statement_ids in self._cr.fetchall())

        for pay in self:
            statement_ids = query_res.get(pay.id, [])
            pay.reconciled_statement_ids = [(6, 0, statement_ids)]
            pay.reconciled_statements_count = len(statement_ids)

    def button_open_invoices(self):
        ''' Redirect the user to the invoice(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Paid Invoices"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.reconciled_invoice_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.reconciled_invoice_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.reconciled_invoice_ids.ids)],
            })
        return action

    def button_open_bills(self):
        ''' Redirect the user to the bill(s) paid by this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Paid Bills"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'context': {'create': False},
        }
        if len(self.reconciled_bill_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.reconciled_bill_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.reconciled_bill_ids.ids)],
            })
        return action

    def button_open_statements(self):
        ''' Redirect the user to the statement line(s) reconciled to this payment.
        :return:    An action on account.move.
        '''
        self.ensure_one()

        action = {
            'name': _("Matched Statements"),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'context': {'create': False},
        }
        if len(self.reconciled_statement_ids) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.reconciled_statement_ids.id,
            })
        else:
            action.update({
                'view_mode': 'list,form',
                'domain': [('id', 'in', self.reconciled_statement_ids.ids)],
            })
        return action
