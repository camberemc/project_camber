# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning, ValidationError
import datetime as dt
from datetime import date

from dateutil.relativedelta import relativedelta


class ContractOrder(models.Model):
    _name = "contract.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'AMC Contracts'

    READONLY_STATES = {
        'running': [('readonly', True)],
        'expired': [('readonly', True)],

    }
    DRAFT_READONLY_STATES = {
        'draft': [('readonly', True)]

    }

    SERVICE_READONLY_STATES = {
        'cancelled': [('readonly', True)],
        'draft': [('readonly', True)],
        'expired': [('readonly', True)],
        'block': [('readonly', True)]
    }
    #
    LINE_READONLY_STATES = {
        'cancelled': [('readonly', True)],
        'running': [('readonly', True)],
        'expired': [('readonly', True)],
        'block': [('readonly', True)]
    }

    name = fields.Char(string='Contract', default='Draft', copy=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('block', 'Blocked'),
        ('expired', 'Expired')
    ], string='Status', default='draft')
    contact_id = fields.Many2one('res.partner', string='Contact', states=READONLY_STATES)
    contact = fields.Char(string='Contact')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', states=READONLY_STATES)
    start_date = fields.Date(string='Start Date', states=READONLY_STATES)
    end_date = fields.Date(string='End Date', states=READONLY_STATES)
    project_id = fields.Many2one('project.project', string='Projects')
    user_id = fields.Many2one('res.users', string='Sales Contact')

    # quotation details

    number_of_visits = fields.Integer(string='Number of Visits', states=READONLY_STATES)
    heading = fields.Char(string='Heading', states=DRAFT_READONLY_STATES)
    validity_id = fields.Many2one('sale.order.validity', string='Validity', states=DRAFT_READONLY_STATES)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    no_schedules = fields.Integer(string='No: Of Schedules', states=DRAFT_READONLY_STATES)
    callouts = fields.Char(string='Callouts', states=DRAFT_READONLY_STATES)
    quote_amount = fields.Monetary(string='Amount', readonly=True)
    currency_id = fields.Many2one('res.currency', string="Currency")
    total_amount = fields.Monetary(string='Contract Value')
    amc_system_type_ids = fields.One2many('contract.system.type', 'contract_id',
                                          string="System Types", states=LINE_READONLY_STATES)
    scope = fields.Text(string='Scope')
    contract_line_ids = fields.One2many(
        'contract.invoice.line', 'order_id', string='Contract Lines')
    service_line_ids = fields.One2many(
        'contract.order.service', 'order_id', string='Service Lines', states=SERVICE_READONLY_STATES)
    hide_visit_button = fields.Boolean(string='Show Visit Button', compute='_compute_button_status')
    sale_order_ids = fields.One2many('sale.order', 'contract_id', string='Sale Orders')
    quotation_id = fields.Many2one('quotation.order', string="Quotation", readonly=True)
    pending_completion = fields.Integer(
        string='Completion Pending', compute='_compute_total', store=True)
    lpo_number = fields.Char(string='LPO Number')
    lpo_date = fields.Date(string='LPO Date')
    lpo_attach_file = fields.Binary(string='LPO Attachment')
    lpo_attach_filename = fields.Char(string='LPO Attachment')
    amc_order_line_ids = fields.One2many('amc.order.lines', 'contract_id', string='Amc Order Lines', readonly=False)
    contract_followup_ids = fields.One2many('contract.order.followup', 'order_id', string="Contract Follow Up")
    project_site = fields.Char(string="Project Site")

    def create_sale_order(self):
        action = self.env.ref('stranbys_amc.create_amc_sale_order').read()[0]
        action['context'] = dict(
            self.env.context,
            default_sale_oder_type='amc',
            default_partner_id=self.partner_id.id,
            default_contract_id=self.id,
        )
        return action

    def set_draft(self):
        self.write({
            'state': 'draft'
        })

    def set_block(self):
        self.write({
            'state': 'block'
        })

    def set_unblock(self):
        self.write({
            'state': 'running'
        })

    def cancel_contract(self):
        self.write({
            'state': 'cancel'
        })

    def _compute_button_status(self):
        for record in self:
            record.hide_visit_button = bool(record.service_line_ids)

    def confirm_contract(self):
        self.check_data()
        if self.name == 'Draft':
            self.name = self.env['ir.sequence'].next_by_code('contract.order.code')
        self.write({
            'state': 'running',
            

        })

    def expiry_check(self):
        contracts = self.env['contract.order'].search([('end_date', '<=', date.today())])
        for rec in contracts:
            rec.write({
                'state': 'expired'
            })

    @api.onchange('start_date')
    def change_start_date(self):
        if not self.start_date: return
        self.end_date = self.start_date + relativedelta(days=365)

    def check_data(self):
        if all([self.start_date, self.end_date, self.start_date, self.number_of_visits, self.payment_term_id]):
            return
        raise UserError('Please fillout date details, payment terms and no: of visits before confirming the contract')

    @api.depends('contract_line_ids')
    def _compute_schedules(self):
        for record in self:
            record.no_schedules = len(record.contract_line_ids)

    @api.depends('contract_line_ids', 'service_line_ids')
    def _compute_total(self):
        for record in self:
            record.pending_completion = len(
                record.service_line_ids.filtered(lambda r: not r.document_signed))

    def generate_scope_of_work(self):
        if self.amc_system_type_ids:
            self.scope = ''
            for rec in self.amc_system_type_ids:
                if rec.description:
                    self.write({
                        'scope': self.scope + "\r\n" + rec.description
                    })

    @api.constrains('start_date', 'start_date', 'number_of_visits')
    def check_date_vist(self):
        if self.start_date > self.end_date:
            raise ValidationError('End date must be a value greater than start date')
        if self.start_date and self.end_date and self.number_of_visits == 0:
            raise ValidationError('Please input number of visits')

    def create_visits(self):
        days = self.end_date - self.start_date
        interval = (days.days + 1) / self.number_of_visits
        service_line_ids = []
        date = self.start_date
        for n in range(self.number_of_visits):
            service_line_ids.append((0, 0, {
                'name': 'Visit ' + str(n + 1),
                'date': date,
                'partner_id':self.partner_id.id,
                'project_name':self.project_site
            }))
            date = date + dt.timedelta(days=interval)
        self.write({
            'service_line_ids': service_line_ids
        })

    def unlink(self):
        for record in self:
            if record.quotation_id:
                raise UserError('Cannot delete Contract')
        return super(ContractOrder, self).unlink()


class ContractInvoiceLine(models.Model):
    _name = 'contract.invoice.line'

    order_id = fields.Many2one('contract.order', string='Contract')
    name = fields.Char(string='Description', required=True)
    date = fields.Date(string='Date')
    amount = fields.Float(string='Invoice Amount')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Confirmed'),
        ('cancel', 'Cancelled'),
        ('block', 'Blocked'),
        ('expired', 'Expired')
    ], string='Status', compute='_compute_contract_state')
    invoice_id = fields.Many2one('account.move', string='Invoice')
    invoice_status = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], string='Status',
        compute='_compute_invoice_create')
    invoice_created_ok = fields.Boolean(
        string='Invoice Created', store=True, compute='_compute_invoice_create')

    def create_invoice(self):
        if self.order_id.state in ['running', 'expired'] and not self.invoice_created_ok:
            product_id = self.env['ir.config_parameter'].sudo().get_param('stranbys_amc.invoice_product')
            account_id = self.env['ir.config_parameter'].sudo().get_param('stranbys_amc.invoice_account')
            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
            invoice_id = self.env['account.move'].create({
                'partner_id':self.order_id.partner_id.id,
                'move_type': 'out_invoice',
                'journal_id': journal.id,
                'invoice_date': self.date,
                'date': self.date,
                'invoice_line_ids': [(0, 0, {
                    'product_id': product_id,
                    'quantity': 1,
                    'name': self.name,
                    'price_unit': self.amount,
                    'account_id': account_id
                })]
            })

            self.write({
                'invoice_id': invoice_id.id,
            })

    @api.depends('invoice_id', 'invoice_id.state')
    def _compute_invoice_create(self):
        for record in self:
            record.invoice_status = False
            if record.invoice_id:
                record.invoice_created_ok = True
                record.invoice_status = record.invoice_id.state

    @api.depends('order_id', 'order_id.state')
    def _compute_contract_state(self):
        for record in self:
            record.state = False
            if record.order_id:
                record.state = record.order_id.state


class ContractServiceRequest(models.Model):
    _name = 'contract.order.service'

    order_id = fields.Many2one('contract.order', string='Contract')
    name = fields.Char(string='Service Details', required=True)
    date = fields.Date(string='Date')
    attachments_ids = fields.Many2many('ir.attachment', string='Attachments')
    document_signed = fields.Boolean(string='Completed/Document Signed')
    system_type_ids = fields.Many2many(
        'amc.system.type', string='Type of Systems')

    partner_id = fields.Many2one('res.partner',string='Customer', readonly=True)

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    project_name = fields.Char(string="Project Name")
    completion_date = fields.Date(string='Completion Date')

    @api.onchange('order_id')
    def _onchange_order_id(self):
        if self.order_id and self.order_id.partner_id:
            self.partner_id = self.order_id.partner_id.id

    @api.constrains('attachments_ids', 'document_signed')
    def _check_documents(self):
        for record in self:
            if record.document_signed and len(record.attachments_ids) < 1:
                raise UserError(
                    'Please upload the completion document of completed services')


class ContractSystemTypes(models.Model):
    _name = 'contract.system.type'
    amc_service_type = fields.Many2one('amc.system.type', string='Name')
    number = fields.Char(string='Number')
    times = fields.Selection([
        ('times_in_year', 'Times in Year'),
    ], string='Times', default='times_in_year')
    description = fields.Text(string="Description")
    contract_id = fields.Many2one('contract.order', string="Contract")
    quotation_id = fields.Many2one('quotation.order', string="Quotation")

    @api.onchange('amc_service_type')
    def _onchange_amc_service_type(self):
        if self.amc_service_type:
            self.number = self.amc_service_type.number
            self.times = self.amc_service_type.times
            self.description = self.amc_service_type.description


class SaleOrderValidity(models.Model):
    _name = 'sale.order.validity'

    name = fields.Char(string='Name', required=True)


class AmcOrderLine(models.Model):
    _name = 'amc.order.lines'

    building_name = fields.Char("Building Name", required=1)
    location = fields.Char("Location")
    unit_price = fields.Float("Unit Price")
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id.id)
    contract_id = fields.Many2one('contract.order', string="Contract")
    quotation_id = fields.Many2one('quotation.order', string="Quotation")
