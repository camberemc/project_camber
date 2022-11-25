from odoo import models, fields, api, _  # type: ignore
from odoo.exceptions import UserError  # type: ignore
import json


class Payments(models.Model):
    _inherit = 'account.payment'

    # def _get_payment_method_codes_to_exclude(self):
    #     # can be overriden to exclude payment methods based on the payment characteristics
    #     return []
    #
    # def unlink(self):
    #     res = []
    #     for record in self:
    #         if (record.state != 'draft') or (record.name != '/'):
    #             raise UserError(f'Cannot delete posted/cancelled entries {record.voucher_number} / {record.name}. ')
    #         res.append(super().unlink())
    #     return res
    #
    #
    # def action_clear_cheque_wizard(self):
    #     ids = self.filtered(lambda r: not r.hide_clearence).ids
    #     if not ids:
    #         raise UserError('Nothing to clear, Take a Break')
    #     return {
    #         'name': _('Cheque Clearence'),
    #         'res_model': 'account.cheque.clear.wizard',
    #         'view_mode': 'form',
    #         'context': {
    #             'active_model': 'account.move',
    #             'default_line_ids': ids,
    #             'default_payment_type' : self.mapped('payment_type')[0]
    #         },
    #         'target': 'new',
    #         'type': 'ir.actions.act_window',
    #     }
    #
    #
    # f_j_id = fields.Many2one('account.journal', string='F J')
    #
    # def line_reconcile(self, line_ids, date,  write_off):
    #     payment_line_ids = []
    #     for line in line_ids:
    #         amount = abs(line.move_id.amount_residual)
    #         if  not write_off:
    #             amount = self.balance_amount if self.balance_amount < amount else amount
    #
    #         payment_line_ids.append((0,0,{
    #             'move_line_id' : line.id,
    #             'amount' : amount,
    #             'date' : date
    #         }))
    #     self.write({
    #         'payment_line_ids' : payment_line_ids
    #     })
    #
    #
    # cleared_date = fields.Date('Cleared Date')
    # clearence_id = fields.Many2one('account.move', string='Clearence Entry')
    # hide_clearence = fields.Boolean('Hide Clearence', default=True)
    #
    # clearence_account_id = fields.Many2one('account.payment.method.line', string='Clearence Account')
    #
    # clearence_state = fields.Selection(related='clearence_id.state', string='Clearence Status')
    #
    # dest_method_ids = fields.Many2many('account.payment.method.line', string='Dest Method Lines', relation='m2m_dest_method_payment_relation', store=True, compute='_compute_dest_payment_method_line_fields')
    #
    #
    # voucher_number = fields.Char('Voucher Number', copy=False)
    #
    # cheque_number = fields.Char('Name/Number')
    # partner_bank_account_id = fields.Many2one('account.partner.bank', company_dependent=True,
    #                                           string="Customer/Supplier Bank Name")
    #
    # def get_voucher_number(self):
    #     for record in self:
    #         code = 'account.payment.inbound'
    #         if record.payment_type == 'outbound':
    #             code = 'account.payment.outbound'
    #         if record.is_internal_transfer:
    #             code = 'account.payment.internal'
    #         if not record.voucher_number:
    #             voucher_number = self.env['ir.sequence'].next_by_code(code)
    #             if not voucher_number:
    #                 raise UserError('No Voucher Code Sequence set for this company. Please create voucher sequence in Settings/Sequences')
    #             record.update({
    #                 'voucher_number' : voucher_number
    #             })
    #
    #
    # @api.depends('voucher_number')
    # def name_get(self):
    #     return [(payment.id, (payment.voucher_number or _('Draft Payment'))) for payment in self]
    #
    # destination_journal_id = fields.Many2one(
    #     comodel_name='account.journal',
    #     string='Destination Journal',
    #     domain="[('type', 'in', ('bank','cash')), ('company_id', '=', company_id)]",
    #     check_company=True,
    # )
    #
    #
    # clear_status = fields.Selection([
    #     ('na', 'N/A'),
    #     ('pending', 'Pending'),
    #     ('cleared', 'Cleared'),
    # ], string='Clearence', default='na')
    #
    #
    # def _prepare_move_line_default_vals(self, write_off_line_vals=None):
    #     ''' Prepare the dictionary to create the default account.move.lines for the current payment.
    #     :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
    #         * amount:       The amount to be added to the counterpart amount.
    #         * name:         The label to set on the line.
    #         * account_id:   The account on which create the write-off.
    #     :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
    #     '''
    #     self.ensure_one()
    #     write_off_line_vals = write_off_line_vals or {}
    #
    #     if not self.outstanding_account_id:
    #         raise UserError(_(
    #             "You can't create a new payment without an outstanding payments/receipts account set either on the company or the %s payment method in the %s journal.",
    #             self.payment_method_line_id.name, self.journal_id.display_name))
    #
    #     # Compute amounts.
    #     write_off_amount_currency = write_off_line_vals.get('amount', 0.0)
    #
    #     if self.payment_type == 'inbound':
    #         # Receive money.
    #         liquidity_amount_currency = self.amount
    #     elif self.payment_type == 'outbound':
    #         # Send money.
    #         liquidity_amount_currency = -self.amount
    #         write_off_amount_currency *= -1
    #     else:
    #         liquidity_amount_currency = write_off_amount_currency = 0.0
    #
    #     write_off_balance = self.currency_id._convert(
    #         write_off_amount_currency,
    #         self.company_id.currency_id,
    #         self.company_id,
    #         self.date,
    #     )
    #     liquidity_balance = self.currency_id._convert(
    #         liquidity_amount_currency,
    #         self.company_id.currency_id,
    #         self.company_id,
    #         self.date,
    #     )
    #     counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
    #     counterpart_balance = -liquidity_balance - write_off_balance
    #     currency_id = self.currency_id.id
    #
    #     if self.is_internal_transfer:
    #         liquidity_balance = -liquidity_balance
    #         counterpart_balance = -counterpart_balance
    #         if self.payment_type == 'inbound':
    #             liquidity_line_name = _('Transfer to %s', self.journal_id.name)
    #         else: # payment.payment_type == 'outbound':
    #             liquidity_line_name = _('Transfer from %s', self.journal_id.name)
    #     else:
    #         liquidity_line_name = self.payment_reference
    #
    #     # Compute a default label to set on the journal items.
    #
    #     payment_display_name = {
    #         'outbound-customer': _("Customer Reimbursement"),
    #         'inbound-customer': _("Customer Payment"),
    #         'outbound-supplier': _("Vendor Payment"),
    #         'inbound-supplier': _("Vendor Reimbursement"),
    #     }
    #
    #     cheque_number = ' - '+ self.cheque_number if self.cheque_number else ''
    #
    #     default_line_name = self.env['account.move.line']._get_default_line_name(
    #         _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
    #         self.amount,
    #         self.currency_id,
    #         self.date,
    #         partner=self.partner_id,
    #     ) + f'{cheque_number}'
    #
    #
    #     line_vals_list = [
    #         # Liquidity line.
    #         {
    #             'name': self.voucher_number or default_line_name,
    #             'date_maturity': self.date,
    #             'amount_currency': liquidity_amount_currency,
    #             'currency_id': currency_id,
    #             'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
    #             'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
    #             'partner_id': self.partner_id.id,
    #             'account_id': self.outstanding_account_id.id,
    #         },
    #         # Receivable / Payable.
    #         {
    #             'name': self.payment_reference or default_line_name,
    #             'date_maturity': self.date,
    #             'amount_currency': counterpart_amount_currency,
    #             'currency_id': currency_id,
    #             'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
    #             'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
    #             'partner_id': self.partner_id.id,
    #             'account_id': self.destination_account_id.id,
    #         },
    #     ]
    #     if not self.currency_id.is_zero(write_off_amount_currency):
    #         # Write-off line.
    #         line_vals_list.append({
    #             'name': write_off_line_vals.get('name') or default_line_name,
    #             'amount_currency': write_off_amount_currency,
    #             'currency_id': currency_id,
    #             'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
    #             'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
    #             'partner_id': self.partner_id.id,
    #             'account_id': write_off_line_vals.get('account_id'),
    #         })
    #     return line_vals_list

    # @api.model_create_multi
    # def create(self,vals_list):
    #     # vals = {}
    #     # res = super(Payments, self).create(vals)
    #     write_off_line_vals_list = []
    #     for vals in vals_list:
    #         write_off_line_vals_list.append(vals.pop('write_off_line_vals', None))
    #         vals['move_type'] = 'entry'

    #     res =  osv.Model.create(self, vals)

    #     for i, pay in enumerate(res):
    #         write_off_line_vals = write_off_line_vals_list[i]

    #         # Write payment_id on the journal entry plus the fields being stored in both models but having the same
    #         # name, e.g. partner_bank_id. The ORM is currently not able to perform such synchronization and make things
    #         # more difficult by creating related fields on the fly to handle the _inherits.
    #         # Then, when partner_bank_id is in vals, the key is consumed by account.payment but is never written on
    #         # account.move.
    #         to_write = {'payment_id': pay.id}
    #         for k, v in vals_list[i].items():
    #             if k in self._fields and self._fields[k].store and k in pay.move_id._fields and pay.move_id._fields[k].store:
    #                 to_write[k] = v

    #         if 'line_ids' not in vals_list[i]:
    #             to_write['line_ids'] = [(0, 0, line_vals) for line_vals in pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]

    #         pay.move_id.write(to_write)

    #     return res

    # outstanding_account_id
    # destination_account_id 

    # destination_journal_id

    # def _synchronize_from_moves(self, changed_fields):
    #     pass

    # hide_dest_payment_method_line = fields.Boolean('Hide DEst PAyment MEthod Line', compute='_compute_dest_payment_method_line_fields', store=True)
    #
    #
    # @api.depends('destination_journal_id', 'is_internal_transfer')
    # def _compute_dest_payment_method_line_fields(self):
    #     for rec in self:
    #         hide_dest_payment_method_line = True
    #         if len(rec.destination_journal_id.inbound_payment_method_line_ids):
    #             hide_dest_payment_method_line = False
    #         rec.hide_dest_payment_method_line = hide_dest_payment_method_line
    #         rec.dest_method_ids = rec.destination_journal_id.inbound_payment_method_line_ids.filtered(lambda r: not r.reconcile_ok).ids
    #
    # dest_payment_method_line_id = fields.Many2one('account.payment.method.line', string='Destination')
    #
    # @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer')
    # def _compute_destination_account_id(self):
    #     self.destination_account_id = False
    #     for pay in self:
    #         if pay.is_internal_transfer:
    #             pay.destination_account_id = self.dest_payment_method_line_id.payment_account_id or pay.destination_journal_id.default_account_id
    #
    #         elif pay.partner_type == 'customer':
    #             # Receive money from invoice or send money to refund it.
    #             if pay.partner_id:
    #                 pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_receivable_id
    #             else:
    #                 pay.destination_account_id = self.env['account.account'].search([
    #                     ('company_id', '=', pay.company_id.id),
    #                     ('internal_type', '=', 'receivable'),
    #                     ('deprecated', '=', False),
    #                 ], limit=1)
    #         elif pay.partner_type == 'supplier':
    #             # Send money to pay a bill or receive money to refund it.
    #             if pay.partner_id:
    #                 pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
    #             else:
    #                 pay.destination_account_id = self.env['account.account'].search([
    #                     ('company_id', '=', pay.company_id.id),
    #                     ('internal_type', '=', 'payable'),
    #                     ('deprecated', '=', False),
    #                 ], limit=1)

    # def _process_entry(self, json_obj, move_id=False):
    #     # ref, name, cr_account_id, dr_account_id, state, amount
    #     vals = {
    #         'date': json_obj.get('date'),
    #         'journal_id': json_obj.get('journal_id'),
    #         'ref': json_obj.get('ref')[0],
    #         'narration': self.narration,
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': json_obj.get('name')[0],
    #                 'account_id': json_obj.get('cr_account_id'),
    #                 'partner_id': self.partner_id.id,
    #                 'debit': 0.0,
    #                 'credit': json_obj.get('amount'),
    #             }),
    #             (0, 0, {
    #                 'name': json_obj.get('name')[0],
    #                 'account_id': json_obj.get('dr_account_id'),
    #                 'partner_id': self.partner_id.id,
    #                 'credit': 0.0,
    #                 'debit': json_obj.get('amount'),
    #             }),
    #         ]
    #     }
    #     if move_id:
    #         move_id.write(vals)
    #     else:
    #         move_id = self.env['account.move'].create(vals)
    #     move_id.post()
    #     return move_id

    # def _process_move_entry(self):
    #     receive = self.amount
    #     payment = 0
    #     if self.payment_type == 'outbound' or  self.is_internal_transfer:
    #         receive = 0
    #         payment = self.amount
    #
    #     payment_display_name = {
    #         'outbound-customer': _("Customer Reimbursement"),
    #         'inbound-customer': _("Customer Payment"),
    #         'outbound-supplier': _("Vendor Payment"),
    #         'inbound-supplier': _("Vendor Reimbursement"),
    #     }
    #
    #     default_line_name = self.env['account.move.line']._get_default_line_name(
    #         _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
    #         self.amount,
    #         self.currency_id,
    #         self.date,
    #         partner=self.partner_id,
    #     )
    #     vals = {
    #         'date': self.date,
    #         'ref': default_line_name ,
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': self.voucher_number or 'Draft',
    #                 'account_id': self.outstanding_account_id.id,
    #                 'partner_id': self.partner_id.id,
    #                 'debit': receive,
    #                 'credit': payment,
    #             }),
    #             (0, 0, {
    #                 'name': self.voucher_number or 'Draft',
    #                 'account_id': self.destination_account_id.id,
    #                 'partner_id': self.partner_id.id,
    #                 'credit': receive,
    #                 'debit': payment,
    #             }),
    #         ]
    #     }
    #     move_id = self.move_id
    #     if move_id:
    #         move_id.write(vals)
    #     else:
    #         vals['journal_id'] = self.journal_id.id
    #         move_id = self.env['account.move'].create(vals)
    #     move_id._post(soft=False)
    #     self.update({
    #         'move_id' : move_id,
    #     })
    #     self.check_clearence()
    #
    #
    # def _process_clearence_entry(self):
    #
    #
    #     if not self.cleared_date or not self.clearence_account_id:
    #         raise UserError('Please provide clearing Date and Account')
    #
    #     if self.payment_method_line_id == self.clearence_account_id:
    #         raise UserError('You cannot choose same account for both payment and clearence')
    #
    #     if self.move_id and self.move_id.state == 'draft':
    #         self.move_id._post(soft=False)
    #
    #     if not self.move_id or self.move_id.state == 'cancel':
    #         raise UserError('There is an error. Please reset the payment and post again')
    #
    #     receive = self.amount
    #     payment = 0
    #     if self.payment_type == 'outbound' and not self.is_internal_transfer:
    #         receive = 0
    #         payment = self.amount
    #
    #
    #     vals = {
    #         'date': self.cleared_date,
    #         'ref': 'Clearence Entry ' + (self.voucher_number or 'Draft') ,
    #         'line_ids': [
    #             (0, 0, {
    #                 'name': 'Payment Clearence of ' + (self.voucher_number or 'Draft'),
    #                 'account_id': self.clearence_account_id.payment_account_id.id,
    #                 'partner_id': self.partner_id.id,
    #                 'debit': receive,
    #                 'credit': payment,
    #             }),
    #             (0, 0, {
    #                 'name': 'Payment Clearence of ' + (self.voucher_number or 'Draft'),
    #                 'account_id': self.payment_method_line_id.payment_account_id.id,
    #                 'partner_id': self.partner_id.id,
    #                 'credit': receive,
    #                 'debit': payment,
    #             }),
    #         ]
    #     }
    #     clearence_id = self.clearence_id
    #     if clearence_id:
    #         clearence_id.write(vals)
    #     else:
    #         vals['journal_id'] = self.journal_id.id
    #         clearence_id = self.env['account.move'].create(vals)
    #     clearence_id._post(soft=False)
    #     self.update({
    #         'clearence_id' : clearence_id,
    #         'hide_clearence' : True,
    #         'clear_status' : 'cleared'
    #     })

    # def action_post(self):
    #     for record in self:
    #         record.get_voucher_number()
    #         record.move_id._post(soft=False)
    #         # record._process_move_entry()
    #         record.move_id.line_ids.write({
    #             'payment_id' : record.id,
    #         })
    #         record.check_clearence()
    # self.move_id._post(soft=False)

    # def check_clearence(self):
    #     hide_clearence = True
    #     clear_status = 'na'
    #     if self.payment_method_line_id.reconcile_ok:
    #         hide_clearence = False
    #         clear_status = 'pending'
    #
    #     if self.clearence_id and self.clearence_id.state in ['posted', 'cancel']:
    #         hide_clearence = True
    #         clear_status = 'cleared'
    #     self.update({
    #             'hide_clearence' : hide_clearence,
    #             'clear_status' : clear_status
    #         })

    # def action_clear(self):
    #     self._process_clearence_entry()

    # def action_draft(self):
    #     res = super().action_draft()
    #     if self.clearence_id:
    #         self.clearence_id.button_draft()
    #         self.clearence_id.line_ids.unlink()
    #     self.check_clearence()
    #     return res
    #
    # def action_cancel(self):
    #     res = super().action_cancel()
    #     if self.clearence_id:
    #         self.clearence_id.button_cancel()
    #     return res

    payment_line_ids = fields.One2many('account.payment.matching.line', 'payment_id', string='Payment Lines')

    move_line_allocate_ids = fields.Many2many(
        'account.move.line', string='Lines', relation='m2m_payment_move_line_relation')

    balance_amount = fields.Monetary('Balance Amount', compute='_compute_balance_amount', store=True)

    @api.depends('payment_line_ids', 'payment_line_ids.amount', 'amount')
    def _compute_balance_amount(self):
        for record in self:
            debit_balance = sum(record.payment_line_ids.filtered(
                lambda r: r.move_line_id.debit > 0).mapped('amount'))
            credit_balance = sum(record.payment_line_ids.filtered(
                lambda r: r.move_line_id.credit > 0).mapped('amount'))
            print(debit_balance)
            print(credit_balance)

            sign = 1 if record.payment_type == 'inbound' else -1

            record.balance_amount = record.amount - (sign * (debit_balance - credit_balance))

    def auto_allocate_amount(self):
        self.move_line_allocate_ids.write({'allocated_amount': 0})
        balance_amount = self.balance_amount
        print(balance_amount)
        # print(asdhga)
        for line in self.move_line_allocate_ids.sorted(key=lambda ml: ml.id, reverse=False):
            if line.amount_residual < 0:
                amount_residual = -1 * line.amount_residual
            elif line.amount_residual >=0 :
                amount_residual = line.amount_residual
            if balance_amount >= amount_residual:
                balance_amount -= amount_residual
                line.write({
                    'allocated_amount': abs(amount_residual),
                })
            else:
                line.write({
                    'allocated_amount': abs(balance_amount),
                })
                break

    def create_payment_matching(self):
        payment_line_ids = []
        for record in self.move_line_allocate_ids.filtered(lambda r: r.allocated_amount > 0):
            payment_line_ids.append((0, 0, {
                'move_line_id': record.id,
                'amount': record.allocated_amount,
            }))
        self.move_line_allocate_ids.write({'allocated_amount': 0})
        self.write({
            'payment_line_ids': payment_line_ids,
            'move_line_allocate_ids': False
        })


class PaymentEntryLine(models.Model):
    _name = 'account.payment.matching.line'
    _description = 'Reconcile'
    _order = 'date desc, id desc'

    invoice_matching = fields.Boolean('Invoice Matching')

    parent_id = fields.Many2one('account.payment.matching.line', string='Parent', ondelete='cascade')

    matching_line_ids = fields.One2many('account.payment.matching.line', 'parent_id', string='Matching Lines')

    payment_id = fields.Many2one('account.payment', string='Payment')
    move_id = fields.Many2one('account.move', string='Payment Move')
    name = fields.Char(string='Payment Line Name', store=True, compute='compute_things')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount = fields.Monetary(string='Allocated Amount')

    partner_id = fields.Many2one('res.partner', string='Partner')

    move_line_id = fields.Many2one(
        'account.move.line', string='Move Line', required=True)

    rec_move_id = fields.Many2one(string='Invoice', related='move_line_id.move_id')
    rec_account_id = fields.Many2one(string='Account', related='move_line_id.account_id')

    date = fields.Date(string='Date', default=lambda self: fields.Date.today())

    def recalculate_parent(self):
        if self.invoice_matching:
            self.write({
                'amount': sum(self.matching_line_ids.mapped('amount'))
            })

    @api.depends('payment_id', 'parent_id', 'rec_move_id')
    def compute_things(self):
        for record in self:
            record.name = record.payment_id.name or record.parent_id.move_id.name or record.rec_move_id.name

    @api.onchange('move_line_id')
    def _onchange_move_line_id(self):
        for record in self:
            record.amount = record.move_line_id.amount_residual

    @api.model
    def unlink(self):
        val = []
        for record in self:
            move_line_id = record.move_line_id
            parent_id = record.parent_id
            child_ids = record.matching_line_ids.mapped('move_line_id')
            res = super(PaymentEntryLine, record).unlink()
            val.append(res)
            move_line_id._compute_amount_residual()
            if child_ids:
                child_ids._compute_amount_residual()
            parent_id.recalculate_parent()

        return val

    @api.model
    def create(self, vals):
        res = super(PaymentEntryLine, self).create(vals)
        res.move_line_id._compute_amount_residual()
        return res

    @api.model
    def write(self, vals):
        res = super(PaymentEntryLine, self).write(vals)
        self.parent_id.recalculate_parent()
        self.move_line_id._compute_amount_residual()
        return res


# class PaymentsLine(models.Model):
#     _inherit = 'account.payment.method.line'
#
#     reconcile_ok  = fields.Boolean('Clearence Entry')


class NewPay(models.TransientModel):
    _inherit = 'account.payment.register'

    test = fields.Boolean('test')

    def _reconcile_payments(self, to_process, edit_mode=False):
        write_off = self.payment_difference_handling == 'reconcile'
        for crv in to_process:
            date = fields.Date.today()
            crv['payment'].line_reconcile(crv['to_reconcile'], date, write_off)
