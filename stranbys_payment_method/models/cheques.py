from datetime import datetime

from openerp import models, fields, api, _
from odoo.exceptions import UserError


class Cheque(models.Model):
    _name = 'account.cheque'
    _description = 'Cheques'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'


    def unlink(self):
        if self.cheque_sequence != 'Draft':
            raise UserError('Cannot delete number generated cheques')
        return super(Cheque, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = self.name + " (COPY)"
        return super(Cheque, self).copy(default=default)

    name = fields.Char(string='Cheque Number', required=True, tracking=True, copy=False)
    cheque_type = fields.Selection([
        ('pay', 'Pay'),
        ('receive', 'Receive'),
    ], string='Type', required=True)

    move_type = fields.Selection([
        ('in_invoice', 'Bills'),
        ('out_invoice', 'Invoice'),
    ], string='Invoice Type', compute='_compute_move_type')


    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('pdc', 'PDC'),
    ], string='Payment Method')


    payment_method_type = fields.Char('Payment Method', store=True, compute='_compute_p_method')

    
    @api.depends('payment_method')
    def _compute_p_method(self):
        for record in self:
            payment_method = record.payment_method
            if payment_method == 'pdc':
                payment_method = 'bank'
            record.payment_method_type = payment_method
    
    
    @api.depends('cheque_type')
    def _compute_move_type(self):
        for record in self:
            if record.cheque_type == 'pay':
                record.move_type = 'in_invoice'
                return
            record.move_type = 'out_invoice'
            
    edit_mode = fields.Boolean(string='Edit')

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode

    state = fields.Selection([
        ('draft', 'Draft'),
        ('issued', 'Issued'),
        ('received', 'Received'),
        ('cleared', 'Cleared'),
        ('return', 'Return'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    currency_id = fields.Many2one('res.currency', string='Currency')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True)

    bank_name = fields.Char(string='Bank Name', tracking=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Float(string='Amount', tracking=True)
    issue_date = fields.Date(string='Collected Date')
    date = fields.Date(string='Date', copy=False)
    cleared_date = fields.Date(string='Cleared Date', tracking=True, copy=False)
    returned_date = fields.Date(string='Returned Date', tracking=True, copy=False)

    pdc_entry_id = fields.Many2one('account.move', string='Cheque Entry', copy=False)
    payment_entry_id = fields.Many2one('account.move', string='Payment Entry', copy=False)
    reverse_entry_id = fields.Many2one('account.move', string='Reverse Entry', copy=False)

    narration = fields.Text(string='Narration')
    transaction = fields.Char(string='Transaction Details')
    voucher_no = fields.Char(string='Voucher')
    cheque_sequence = fields.Char(string="Voucher Number",copy=False, default='Draft')

    pending_invoice_ids = fields.Many2many('account.move', relation='m2m_invoice_pending_cheque_relation', string='PendingInvoices')
    allocated_invoice_ids = fields.Many2many('account.move', relation='m2m_invoice_allocated_cheque_relation', string='Allocated Invoices')

    partner_ids = fields.Many2many('res.partner', string='Financial Partners', compute='_find_partner_ids')

    balance_amount = fields.Float(string='Balance Amount', compute='_compute_balance_amount', store=True)
    allocated_invoice_amount = fields.Float(string='Allocated Amount')

    partial_rec_ids = fields.One2many('account.partial.reconcile', 'cheque_id', string='Partials')

    entry_date = fields.Date(string='Entry Date')

    ch_payment_ids = fields.One2many('cheque.account.payment.line', 'cheque_id', string='Payments')



    def cancel_entry(self):
        if self.partial_rec_ids :
            raise UserError('Cannot cancel cheque having reconciled entries')

        if self.state == 'return':
            raise UserError('Cannot cancel returned cheque entries')
        
        if self.pdc_entry_id:
            self.pdc_entry_id.button_draft()
            self.pdc_entry_id.button_cancel()
        
        if self.pdc_entry_id:
            self.payment_entry_id.button_draft()
            self.payment_entry_id.button_cancel()
        
        self.write({'state':'cancel'})


    def open_reconciled_invoice(self):
        reconcile_ids = self.env['account.partial.reconcile'].search([('credit_move_id', 'in', self.pdc_entry_id.line_ids.ids)])
        debit_move_ids = self.env['account.move.line'].browse(reconcile_ids.mapped('debit_move_id').ids)
        move_ids = self.env['account.move.line'].browse(debit_move_ids.ids).mapped('move_id').ids
        reconcile_move_ids = self.env['account.partial.reconcile'].search([('credit_move_id', 'in', debit_move_ids.move_id.line_ids.ids)]).mapped('debit_move_id').ids
        
        move_ids + (self.env['account.move.line'].browse(reconcile_move_ids).mapped('move_id').ids)
        # move_ids = self.env('a')


        # raise UserError(str(reconcile_ids))
        # ids = self.pdc_entry_id.line_ids._reconciled_lines()
        # move_ids = self.env['account.move.line'].browse(ids).mapped('move_id').ids
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_line_form')
        action['domain'] = [('id', 'in', move_ids)]
        return action
        # 

            # def open_reconcile_view(self):
            #     return self.line_ids.open_reconcile_view()


            # def open_reconcile_view(self):
            # action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_line_form')
            # ids = self._reconciled_lines()
            # action['domain'] = [('id', 'in', ids)]
            # 

    @api.onchange('date')
    def _onchange_date_to_entry_date(self):
        pass
        # if self.date:
        #     self.entry_date = self.date if fields.Date.today() >= self.date else fields.Date.today()

    
    @api.depends('ch_payment_ids.amount', 'ch_payment_ids', 'amount')
    def _compute_balance_amount(self):
        for record in self:
            record.balance_amount = record.amount-sum(record.ch_payment_ids.mapped('amount'))

            # move_ids = record.pdc_entry_id.line_ids._reconciled_lines()
            # moves = self.env['account.move.line'].browse(move_ids)
            # balance_amount = sum(moves.mapped('amount_currency'))
            # record.balance_amount = balance_amount
            # if record.cheque_type == 'receive':
            #     record.balance_amount = abs(-balance_amount)

            # if record.partial_rec_ids:
            #     rec_ids = record.partial_rec_ids.mapped('amount')
            #     balance_amount = record.amount - sum(rec_ids)
            #     record.balance_amount = balance_amount
            #     if record.cheque_type == 'receive':
            #         record.balance_amount = abs(-balance_amount)





    def allcocate_amount_to_invoce(self):
        self.pending_invoice_ids.write({'amount_cheque_allocated' : 0})
        balance_amount = self.balance_amount
        for inv in self.pending_invoice_ids.sorted(key=lambda ml: ml.id, reverse=False):
            if balance_amount >= inv.amount_residual:
                balance_amount -= inv.amount_residual
                inv.write({
                    'amount_cheque_allocated' : inv.amount_residual,
                })
            else:
                inv.write({
                    'amount_cheque_allocated' : balance_amount,
                })
                break

    def fast_reconcile(self):
        # partial_ids = []
        if not self.cheque_type:
            raise UserError('Cheque enty is not Valid, Please recreate the entry')
        if self.state in ['draft', 'return']:
            raise UserError ('Cannot reconcile Draft/Returned cheques')
        if self.cheque_type == 'pay':
            raise UserError ('Cannot reconcile payables with this method')
        account_id = self.partner_id.property_account_receivable_id.id
        pdc_reconcile_line_id = self.pdc_entry_id.line_ids.filtered(lambda r: r.account_id.id == account_id)
        if not pdc_reconcile_line_id:
            raise UserError('No Matching lines found, please check the PDC Journal Entry')
        invoice_ids = self.pending_invoice_ids.filtered(lambda r: r.amount_cheque_allocated == r.amount_residual)
        invoice_ids.filtered(lambda r: r.js_assign_outstanding_line(pdc_reconcile_line_id.id))
        # for invoice in invoice_ids:
        #     partial_ids.append(invoice.js_assign_outstanding_line(pdc_reconcile_line_id.id).get('partials').id)
        invoice_ids.write({'amount_cheque_allocated' : 0})
        # for inv in self.pending_invoice_ids:
        #     if inv.amount_cheque_allocated == inv.amount_residual:
        #                 reco_obj = inv.js_assign_outstanding_line(pdc_reconcile_line_id.id)
        #                 partial_ids.append(reco_obj.get('partials').id)
        self.pending_invoice_ids = False
        # self.write({
        #     'allocated_invoice_ids' : [(6, 0, invoice_ids.ids+self.allocated_invoice_ids.ids)]
        # })


    def reconcile_invioces(self):
        if not self.cheque_type:
            raise UserError('Cheque enty is not Valid, Please recreate the entry')
        if self.state in ['draft', 'return']:
            raise UserError ('Cannot reconcile Draft/Returned cheques')
        account_id = self.partner_id.property_account_receivable_id.id
        if self.cheque_type == 'pay':
            account_id = self.partner_id.property_account_payable_id.id
        if round(sum(self.pending_invoice_ids.mapped('amount_cheque_allocated')), 2) > round(self.balance_amount, 2):
            raise UserError("Total allocated amount doesn't match balance unallocated amount.")
        pdc_reconcile_line_id = self.pdc_entry_id.line_ids.filtered(lambda r: r.account_id.id == account_id)
        if not pdc_reconcile_line_id:
            raise UserError('No Matching lines found, please check the PDC Journal Entry')

        line_ids = []
        total_allocated = 0
        allocated_invoices = []
        move_id = False
        partial_ids = []
        for inv in self.pending_invoice_ids:
            if inv.amount_cheque_allocated >0:
                
                if inv.amount_cheque_allocated > inv.amount_residual:
                    raise UserError(f"""Cannot reconcile with excess amount. Please recheck Invoice {inv.name}. \n Pending amount must not be greater than {inv.amount_residual}""")
                if inv.amount_cheque_allocated == inv.amount_residual:
                    reco_obj = inv.js_assign_outstanding_line(pdc_reconcile_line_id.id)
                    partial_ids.append(reco_obj.get('partials').id)
                if inv.amount_cheque_allocated < inv.amount_residual:
                    line_ids.append((0,0, {
                        'name': f"""Payment Matching {self.cheque_sequence}""",
                        'account_id': account_id,
                        'partner_id': inv.partner_id.id,
                        'credit': inv.amount_cheque_allocated if self.cheque_type == 'receive' else 0,
                        'debit': 0 if self.cheque_type == 'receive' else inv.amount_cheque_allocated,
                        'allocated_invoice_id' : inv.id,
                        'payment_allocation_entry' : True
                    }))
                    total_allocated += inv.amount_cheque_allocated
                    allocated_invoices.append(inv)
        if line_ids:
            line_ids.append((0,0, {
                    'name': f"""Payment Matching {self.cheque_sequence}""",
                    'account_id': account_id,
                    'partner_id': self.partner_id.id,
                    'credit': 0 if self.cheque_type == 'receive' else total_allocated,
                    'debit': total_allocated if self.cheque_type == 'receive' else 0,
                    'payment_allocation_entry' : True
                }))
        
            vals = {
                'date': self.entry_date,
                'journal_id': self.pdc_entry_id.journal_id.id,
                'ref': f"""Payment Matching {self.cheque_sequence}""",
                'narration': self.narration,
                'line_ids' : line_ids,
            }
            move_id = self.env['account.move'].create(vals)
            move_id.post()

        for inv in allocated_invoices:
            move_line_id = self.env['account.move.line'].search([('allocated_invoice_id', '=', inv.id)], limit=1)
            reco_obj = inv.js_assign_outstanding_line(move_line_id.id)
            partial_ids.append(reco_obj.get('partials').id)
            move_line_id.write({
                'allocated_invoice_id' : False
            })
        if move_id:
            pdc_reconcile_line_id = pdc_reconcile_line_id[0]
            move_id.js_assign_outstanding_line(pdc_reconcile_line_id.id)

        
        partial_reconcile_ids = self.env['account.partial.reconcile'].browse(partial_ids)
        # raise UserError(str(partial_reconcile_ids))
        partial_reconcile_ids.write({
            'cheque_id' : self.id
        })

        # pdc_reconcile_line_id.reconcile()
        self.pending_invoice_ids.write({
            'amount_cheque_allocated' : 0
        })
        self.pending_invoice_ids = False
        self.write({
            'allocated_invoice_amount' : self.allocated_invoice_amount + total_allocated,
            'allocated_invoice_ids' : [(6, 0, self.pending_invoice_ids.ids+self.allocated_invoice_ids.ids)]
        })
            
    
    



    def _find_partner_ids(self):
        for record in self:
            partner_ids = self.env['res.partner'].search(['|', '|', ('parent_id', '=', record.partner_id.id), ('commercial_partner_id', '=', record.partner_id.id), ('id', '=', record.partner_id.id)])
            record.partner_ids = partner_ids.ids

    def new_reconcile_invoice(self):
        if not any(self.pending_invoice_ids.mapped('amount_cheque_allocated')):
            raise UserError('No invoice has allocated amount. Please check Auto allocate or allocate manuallly')
        ch_payment_ids = []
        for inv in self.pending_invoice_ids.filtered(lambda r: r.amount_cheque_allocated > 0):
            ch_payment_ids.append((0,0, {
                'move_id' : self.payment_entry_id.id,
                'invoice_id' : inv.id,
                'date' : self.entry_date,
                'amount' : inv.amount_cheque_allocated
            }))
        self.update({
            'ch_payment_ids' : ch_payment_ids
        })
        self.pending_invoice_ids.write({'amount_cheque_allocated' : 0})
        # self.pending_invoice_ids.filtered(lambda r: r._compute_amount_state())
        self.pending_invoice_ids = False


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
        vals = {
            'cr': journal_id.payment_credit_account_id.id,
            'dr': journal_id.payment_debit_account_id.id,
            'id': journal_id.id
        }
        return vals

    def account_check(self):
        if self.amount <= 0:
            raise UserError("Please enter a valid amount")
        if not self.entry_date:
            raise UserError('Please update the entry date')



    def confirm_payment(self):
        self.account_check()
        if self.payment_method != "pdc":
            self.confirm_bank_cash_entry()
            return
        self.create_pdc()

    
    def confirm_bank_cash_entry(self):
        cheque_sequence = self.cheque_sequence
        if self.cheque_type == 'receive':
            cr_account_id = self.partner_id.property_account_receivable_id.id
            dr_account_id = self.journal_id.payment_debit_account_id.id
            name = 'Received :' + self.name,
            if cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.receipts')
        if self.cheque_type == 'pay':
            cr_account_id = self.journal_id.payment_credit_account_id.id
            dr_account_id = self.partner_id.property_account_payable_id.id
            name = 'Paid :' + self.name,
            if cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.send')

        json_obj = {
            'journal_id': self.journal_id.id,
            'cr_account_id': cr_account_id,
            'dr_account_id': dr_account_id,
            'amount': self.amount,
            'name': name,
            'date': self.entry_date,
            'ref': name
        }
        move_id = self._process_entry(json_obj, move_id=self.payment_entry_id)
        self.write(
            {
                'payment_entry_id': move_id.id,
                'state': 'cleared',
                'cheque_sequence' : cheque_sequence
            }
        )
    
    def reset_entry(self):
        self.pdc_entry_id.button_draft()
        self.payment_entry_id.button_draft()
        self.write({
            'state' : 'draft'
        })
        

            

    def create_pdc(self):
        cheque_sequence = self.cheque_sequence
        if self.cheque_type == 'receive':
            cr_account_id = self.partner_id.property_account_receivable_id.id
            dr_account_id = self.pdc_journal().get('dr')
            name = 'Received Cheque No:' + self.name,
            state = 'received'
            if cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.receipts')

        if self.cheque_type == 'pay':
            cr_account_id = self.pdc_journal().get('cr')
            dr_account_id = self.partner_id.property_account_payable_id.id
            name = 'Paid Cheque No:' + self.name,
            state = 'issued'
            if cheque_sequence == 'Draft':
                cheque_sequence = self.env['ir.sequence'].next_by_code('account.cheque.send')


        json_obj = {
            'journal_id': self.pdc_journal().get('id'),
            'cr_account_id': cr_account_id,
            'dr_account_id': dr_account_id,
            'amount': self.amount,
            'name': name,
            'state': state,
            'date': self.entry_date,
            'ref': name
        }
        move_id = self._process_entry(json_obj, move_id=self.pdc_entry_id)
        self.write(
            {
                'pdc_entry_id': move_id.id,
                'state': state,
                'cheque_sequence' : cheque_sequence
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
        move_id = self._process_entry(json_obj, move_id=self.payment_entry_id)

        self.write(
            {
                'payment_entry_id': move_id.id,
                'state': 'cleared'
            }
        )

    def _process_entry(self, json_obj, move_id=False):
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
        if move_id:
            move_id.write(vals)
        else:
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


    def re_allocate(self):
        ch_payment_ids = []
        for line in self.partial_rec_ids:
            ch_payment_ids.append((0,0,{
                'invoice_id' : line.debit_move_id.move_id.id,
                'date' : line.max_date,
                'amount' : line.amount
            }))
        self.write({
            'ch_payment_ids' : ch_payment_ids
        })

    def write_payment(self):
        for record in self:
            record.write({
                'payment_method' : 'pdc'
            })


class InvoiceCheque(models.Model):
    _inherit = 'account.move'


    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id')
    def _compute_amount(self):
        for move in self:

            if move.payment_state == 'invoicing_legacy':
                # invoicing_legacy state is set via SQL when setting setting field
                # invoicing_switch_threshold (defined in account_accountant).
                # The only way of going out of this state is through this setting,
                # so we don't recompute it here.
                move.payment_state = move.payment_state
                continue

            total_untaxed = 0.0
            total_untaxed_currency = 0.0
            total_tax = 0.0
            total_tax_currency = 0.0
            total_to_pay = 0.0
            total_residual = 0.0
            total_residual_currency = 0.0
            total = 0.0
            total_currency = 0.0
            currencies = move._get_lines_onchange_currency().currency_id

            for line in move.line_ids:
                if move.is_invoice(include_receipts=True):
                    # === Invoices ===

                    if not line.exclude_from_invoice_tab:
                        # Untaxed amount.
                        total_untaxed += line.balance
                        total_untaxed_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.tax_line_id:
                        # Tax amount.
                        total_tax += line.balance
                        total_tax_currency += line.amount_currency
                        total += line.balance
                        total_currency += line.amount_currency
                    elif line.account_id.user_type_id.type in ('receivable', 'payable'):
                        # Residual amount.
                        total_to_pay += line.balance
                        total_residual += line.amount_residual
                        total_residual_currency += line.amount_residual_currency
                else:
                    # === Miscellaneous journal entry ===
                    if line.debit:
                        total += line.balance
                        total_currency += line.amount_currency

            if move.move_type == 'entry' or move.is_outbound():
                sign = 1
            else:
                sign = -1
            move.amount_untaxed = sign * (total_untaxed_currency if len(currencies) == 1 else total_untaxed)
            move.amount_tax = sign * (total_tax_currency if len(currencies) == 1 else total_tax)
            move.amount_total = sign * (total_currency if len(currencies) == 1 else total)
            move.amount_residual = -sign * (total_residual_currency if len(currencies) == 1 else total_residual)
            move.amount_untaxed_signed = -total_untaxed
            move.amount_tax_signed = -total_tax
            move.amount_total_signed = abs(total) if move.move_type == 'entry' else -total
            move.amount_residual_signed = total_residual

            currency = len(currencies) == 1 and currencies or move.company_id.currency_id

            # Compute 'payment_state'.
            new_pmt_state = 'not_paid' if move.move_type != 'entry' else False

            if move.is_invoice(include_receipts=True) and move.state == 'posted':

                if currency.is_zero(move.amount_residual):
                    reconciled_payments = move._get_reconciled_payments()
                    if not reconciled_payments or all(payment.is_matched for payment in reconciled_payments):
                        new_pmt_state = 'paid'
                    else:
                        new_pmt_state = move._get_invoice_in_payment_state()
                elif currency.compare_amounts(total_to_pay, total_residual) != 0:
                    new_pmt_state = 'partial'

            if new_pmt_state == 'paid' and move.move_type in ('in_invoice', 'out_invoice', 'entry'):
                reverse_type = move.move_type == 'in_invoice' and 'in_refund' or move.move_type == 'out_invoice' and 'out_refund' or 'entry'
                reverse_moves = self.env['account.move'].search([('reversed_entry_id', '=', move.id), ('state', '=', 'posted'), ('move_type', '=', reverse_type)])

                # We only set 'reversed' state in cas of 1 to 1 full reconciliation with a reverse entry; otherwise, we use the regular 'paid' state
                reverse_moves_full_recs = reverse_moves.mapped('line_ids.full_reconcile_id')
                if reverse_moves_full_recs.mapped('reconciled_line_ids.move_id').filtered(lambda x: x not in (reverse_moves + reverse_moves_full_recs.mapped('exchange_move_id'))) == move:
                    new_pmt_state = 'reversed'

            # move.payment_state = new_pmt_state

    payment_selection_ok = fields.Boolean('Payment Selection')

    amount_cheque_allocated = fields.Float(string='Allocated Amount')
    ch_payment_ids = fields.One2many('cheque.account.payment.line', 'invoice_id', string='Payments')
    ch_move_ids = fields.One2many('cheque.account.payment.line', 'move_id', string='Payments')

    amount_residual = fields.Monetary(string='Amount Due', store=True, compute='compute_amount_state')

    payment_state = fields.Selection(selection=[
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy')],
        string="Payment Status", store=True, readonly=True, copy=False, tracking=True,
        compute='compute_amount_state')

    @api.depends('ch_payment_ids.amount', 'ch_payment_ids', 'amount_total', 'ch_move_ids', 'ch_move_ids.amount')
    def compute_amount_state(self):
        for record in self:
            sign = -1
            if record.move_type == 'entry' or record.is_outbound():
                sign = 1
            amount = sum(record.ch_payment_ids.mapped('amount'))
            amount += sum(record.ch_move_ids.mapped('amount'))
            record.amount_residual = -sign *(record.amount_total - amount)
            record.payment_state = 'partial'
            if amount >= record.amount_total and record.state == 'posted':
                record.payment_state = 'paid'
                return
            if amount == 0:
                record.payment_state = 'not_paid'
                return

    def action_payment_mapping_wizard(self):
        action = self.env.ref('stranbys_pdc.act_payment_maping_wizard').read()[0]
        search_filter = [
                ('partner_id', '=', self.partner_id.id), 
                ('payment_state', 'in', ('not_paid', 'partial')),
                ('state', '=', 'posted')]
        if self.move_type == 'out_refund':
            search_filter.append(('move_type', '=', 'out_invoice'))
        if self.move_type == 'in_refund':
            search_filter.append(('move_type', '=', 'in_invoice'))
        invoice_ids = self.env['account.move'].search(search_filter)
        action['context'] = dict(
            self.env.context,
            default_invoice_ids = invoice_ids.ids,
            default_move_type = self.move_type,
            default_move_id = self.id
        )
        return action


class InvoiceLineCheque(models.Model):
    _inherit = 'account.move.line'

    allocated_invoice_id = fields.Many2one('account.move', string='Allocated Invoice')
    payment_allocation_entry = fields.Boolean(string='Payment Allocation Entry')
    cheque_id = fields.Many2one('account.cheque', string='Cheque')
    

class ChequePartialReconcile(models.Model):
    _inherit = 'account.partial.reconcile'

    cheque_id = fields.Many2one('account.cheque', string='Cheque')


class PaymentEntry(models.Model):
    _name = 'cheque.account.payment.line'
    _description = 'Payments'
    _order = 'date desc, id desc'


    name = fields.Char(string='Payment', store=True, compute='compute_things')

    invoice_id = fields.Many2one('account.move', string='Invoice')
    move_id = fields.Many2one('account.move', string='Move')
    currency_id = fields.Many2one('res.currency', string='Currency')
    cheque_id = fields.Many2one('account.cheque', string='Cheque')
    amount_invoice = fields.Monetary(string='Amount in Inovice Currency')
    amount = fields.Monetary(string='Allocated Amount')
    date = fields.Date(string='Date', default = lambda self: fields.Date.today())


    @api.depends('move_id','cheque_id')
    def compute_things(self):
        for record in self:
            record.name = record.move_id.name or record.cheque_id.name


    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        for record in self:
            record.amount = record.invoice_id.amount_residual

    
    @api.model
    def unlink(self):
        val = []
        for record in self:
            invoice_id = record.invoice_id
            res = super(PaymentEntry, record).unlink()
            val.append(res)
            invoice_id.compute_amount_state()
        return val

    @api.model
    def create(self, vals):
        res = super(PaymentEntry, self).create(vals)
        res.invoice_id.compute_amount_state()        
        return res

    @api.model
    def write(self, vals):
        res = super(PaymentEntry, self).write(vals)
        self.invoice_id.compute_amount_state()  
        return res