from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountExpenseVoucher(models.Model):
    _name = 'account.expense.voucher'
    _description = 'Expense Voucher'
    _order = 'date desc, id desc'

    partner_id = fields.Many2one('res.partner', string="Customer")
    name = fields.Char(string='Name', readonly=True,
                       tracking=True, default='Draft')
    journal_id = fields.Many2one('account.journal', string="Journal", required=True,
                                 domain="['|', ('type', '=', 'cash'), ('type', '=', 'bank')]")
    date = fields.Date(string="Date", required=True)
    voucher_type = fields.Selection([
        ('send', 'Send Money'),
        ('receive', 'Receive Money'),
    ], string='Type', required=True, default='send')
    untaxed_amount = fields.Float(string="Untaxed Amount", compute='_compute_grand_total')
    tax_amount = fields.Float(string="Tax Amount", compute='_compute_grand_total')
    total_amount = fields.Float(string="Total", compute='_compute_grand_total')
    expense_line_ids = fields.One2many('account.expense.voucher.line', 'expense_id', string="Expense Lines")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('posted', 'Post'), ('cancel', 'Cancel')
    ], readonly=True, default='draft')
    payment_entry_id = fields.Many2one('account.move', string='Payment Entry', copy=False, readonly=True)
    reference = fields.Char(string="Reference")
    comments = fields.Char(string="Comments")
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.depends('expense_line_ids.tax_amount', 'expense_line_ids.price_amount', 'expense_line_ids.subtotal')
    def _compute_grand_total(self):
        for rec in self:
            rec.total_amount = 0
            rec.untaxed_amount = 0
            rec.tax_amount = 0
            if rec.expense_line_ids:
                for line in rec.expense_line_ids:
                    rec.untaxed_amount = rec.untaxed_amount + line.price_amount
                    rec.tax_amount = rec.tax_amount + line.tax_amount
                    rec.total_amount = rec.total_amount + line.subtotal

    def unlink(self):
        if self.state != 'draft':
            raise UserError('Cannot delete records in posted stage')
        return super(AccountExpenseVoucher, self).unlink()

    def action_submit(self):
        self.write({
            'name': self.env['ir.sequence'].next_by_code('expense.voucher.code'),
            'state': 'submit'
        })

    def action_cancel(self):
        self.payment_entry_id.button_draft()
        self.payment_entry_id.button_cancel()
        self.state = 'cancel'

    def action_post(self):
        if self.total_amount <= 0:
            raise UserError("Please enter a valid amount")

        if self.expense_line_ids:
            if self.voucher_type == 'send':
                taxes_paid = self.env['account.account'].search([('code', '=', '104301')], limit=1)
                account_lines = []
                account_lines.append([0, 0, {
                    'name': self.reference,
                    'account_id': self.journal_id.payment_credit_account_id.id,
                    'partner_id': self.partner_id.id,
                    'debit': 0.0,
                    'credit': self.total_amount,
                }])
                total_tax = 0
                for line in self.expense_line_ids:
                    account_lines.append([0, 0, {
                        'name': self.reference,
                        'account_id': line.account_id.id,
                        'partner_id': self.partner_id.id,
                        'tax_ids': line.tax_id,
                        'debit': line.price_amount,
                        'credit': 0.0,
                        'tax_line_id': line.tax_id.id,
                        'project_id': line.project_id.id if line.project_id else False,
                        'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False
                    }])
                    if line.tax_amount:
                        total_tax = total_tax + line.tax_amount
                if total_tax:
                    account_lines.append([0, 0, {
                        'name': self.reference,
                        'account_id': taxes_paid.id,
                        'partner_id': self.partner_id.id,
                        'debit': total_tax,
                        'credit': 0.0,

                    }])
                vals = {
                    'date': self.date,
                    'journal_id': self.journal_id.id,
                    'ref': 'Expense Voucher of ' + self.name,
                    'narration': self.comments,
                    'line_ids': account_lines
                }
                move_id = self.env['account.move'].create(vals)
                move_id.post()
                self.write(
                    {
                        'payment_entry_id': move_id.id,
                        'state': 'posted'
                    }
                )
            if self.voucher_type == 'receive':
                taxes_received = self.env['account.account'].search([('code', '=', '204311')], limit=1)
                account_lines = []
                account_lines.append([0, 0, {
                    'name': self.reference,
                    'account_id': self.journal_id.payment_credit_account_id.id,
                    'partner_id': self.partner_id.id,
                    'debit': self.total_amount,
                    'credit': 0.0
                }])
                total_tax = 0
                for line in self.expense_line_ids:
                    account_lines.append([0, 0, {
                        'name': self.reference,
                        'account_id': line.account_id.id,
                        'partner_id': self.partner_id.id,
                        'tax_ids': line.tax_id,
                        'debit': 0.0,
                        'credit': line.price_amount,
                        'project_id': line.project_id.id if line.project_id else False,
                        'analytic_account_id': line.analytic_account_id.id if line.analytic_account_id else False
                    }])
                    if line.tax_amount:
                        total_tax = total_tax + line.tax_amount
                if total_tax:
                    account_lines.append([0, 0, {
                        'name': self.reference,
                        'account_id': taxes_received.id,
                        'partner_id': self.partner_id.id,
                        'credit': total_tax,
                        'debit': 0.0
                    }])

                vals = {
                    'date': self.date,
                    'journal_id': self.journal_id.id,
                    'ref': 'Expense Voucher of ' + self.name,
                    'narration': self.comments,
                    'line_ids': account_lines
                }
                move_id = self.env['account.move'].create(vals)
                move_id.post()
                self.write(
                    {
                        'payment_entry_id': move_id.id,
                        'state': 'posted'
                    }
                )


        else:
            raise UserError("Please add expense Lines")


class AccountExpenseVoucherLine(models.Model):
    _name = 'account.expense.voucher.line'

    expense_id = fields.Many2one('account.expense.voucher', string="Expense")
    account_id = fields.Many2one('account.account', string="Account", required=True)
    label = fields.Char(string="Label", required=True)
    price_amount = fields.Float(string="Price")
    tax_id = fields.Many2one('account.tax', string="Tax")
    tax_amount = fields.Float(string="Tax Amount", compute='_compute_amount')
    subtotal = fields.Float(string="Sub Total", compute='_compute_amount')
    project_id = fields.Many2one('project.project', string="Project")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    @api.onchange('account_id', 'expense_id.voucher_type')
    def _onchange_account_id(self):
        if self.expense_id.voucher_type == 'send':
            return {'domain': {'tax_id': [('id', '=', self.env.company.account_purchase_tax_id.id)]}}
        if self.expense_id.voucher_type == 'receive':
            return {'domain': {'tax_id': [('id', '=', self.env.company.account_sale_tax_id.id)]}}

    @api.depends('price_amount', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            # price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(line.price_amount, line.expense_id.currency_id, 1,
                                            product=False, partner=False)
            line.update({
                'tax_amount': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'subtotal': taxes['total_included'],
            })
