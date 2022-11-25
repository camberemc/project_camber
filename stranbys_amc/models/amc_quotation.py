# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning, ValidationError
import datetime as dt
from odoo.addons import decimal_precision as dp

from dateutil.relativedelta import relativedelta


class QuotationOrder(models.Model):
    _name = "quotation.order"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'
    _description = 'AMC Quotation'

    READONLY_STATES = {
        'confirmed': [('readonly', True)],

    }
    name = fields.Char(string='Contract', default='Draft', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting Approval'),
        ('quote', 'Quotation'),
        ('quote_send', 'Quotation Send'),
        ('confirmed', 'Confirmed'),
    ], string='Status', default='draft', copy=False, track_visibility='onchange')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', states=READONLY_STATES)
    contact_id = fields.Many2one('res.partner', string='Contact', states=READONLY_STATES)
    contact = fields.Char(string='Contact')
    project_id = fields.Many2one('project.project', string='Projects', states=READONLY_STATES)
    user_id = fields.Many2one('res.users', string='Sales Contact', states=READONLY_STATES)
    heading = fields.Char(string='Heading', states=READONLY_STATES)
    validity_id = fields.Many2one('sale.order.validity', string='Validity', states=READONLY_STATES)
    payment_term_id = fields.Many2one(
        'account.payment.term', string='Payment Terms')
    no_schedules = fields.Integer(string='No: Of Schedules', states=READONLY_STATES)
    callouts = fields.Char(string='Callouts', states=READONLY_STATES)
    quote_amount = fields.Monetary(string='Amount', states=READONLY_STATES)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                  default=lambda self: self.env.company.currency_id.id, states=READONLY_STATES)

    terms_and_condition_id = fields.Many2one('amc.terms.condition', string="Terms and Condition",
                                             states=READONLY_STATES)

    terms_and_condition = fields.Text(string="Terms and Condition", states=READONLY_STATES)
    amc_system_type_ids = fields.One2many('contract.system.type', 'quotation_id',
                                          string="System Types", states=READONLY_STATES, copy=True)
    scope = fields.Text(string='Scope', states=READONLY_STATES)
    lpo_number = fields.Char(string='LPO Number')
    lpo_date = fields.Date(string='LPO Date')
    lpo_attach_file = fields.Binary(string='LPO Attachment')
    lpo_attach_filename = fields.Char(string='LPO Attachment')
    amc_order_line_ids = fields.One2many('amc.order.lines', 'quotation_id', string='Amc Order Lines',
                                         states=READONLY_STATES, copy=True)

    revision_id = fields.Many2one('amc.quotation.revision', string='Revision Group')
    revision_number = fields.Char(string='Revision Number')
    revision_count = fields.Integer(string='Revisions', compute='_compute_revision_count')

    def generate_scope_of_work(self):
        if self.amc_system_type_ids:
            self.scope = ''
            for rec in self.amc_system_type_ids:
                if rec.description:
                    self.write({
                        'scope': self.scope + "\r\n" + rec.description
                    })

    def check_data(self):
        if all([self.lpo_number, self.lpo_date, self.lpo_attach_file, self.lpo_attach_filename]):
            return
        raise UserError('Please fillout registration details')

    @api.onchange('terms_and_condition_id')
    def change_terms_and_condition_id(self):
        if self.terms_and_condition_id:
            self.write({
                'terms_and_condition': self.terms_and_condition_id.description
            })

    def confirm_quotation(self):
        self.check_data()
        vals = {
            'partner_id': self.partner_id.id,
            'contact_id': self.contact_id.id,
            'contact': self.contact,
            'project_id': self.project_id.id,
            'user_id': self.user_id.id,
            'heading': self.heading,
            'validity_id': self.validity_id.id,
            'payment_term_id': self.payment_term_id.id,
            'no_schedules': self.no_schedules,
            'callouts': self.callouts,
            'quote_amount': self.quote_amount,
            'currency_id': self.currency_id.id,
            'quotation_id': self.id,
            'amc_system_type_ids': self.amc_system_type_ids.ids,
            'scope': self.scope,
            'lpo_number': self.lpo_number,
            'lpo_date': self.lpo_date,
            'lpo_attach_file': self.lpo_attach_file,
            'lpo_attach_filename': self.lpo_attach_filename,
            'amc_order_line_ids': self.amc_order_line_ids.ids
        }
        contract = self.env['contract.order'].create(vals)
        self.write({
            'state': 'confirmed'
        })

    def request_quote_approval(self):
        if self.name == 'Draft':
            self.name = self.env['ir.sequence'].next_by_code('contract.quote.code')
        self.write({
            'state': 'waiting_approval'
        })

    def confirm_draft(self):
        self.write({
            'state': 'quote',
        })

    def reject_quotation(self):
        self.write({
            'state': 'draft'
        })

    def quotation_send(self):
        self.write({
            'state': 'quote_send',
        })

    def view_contracts(self):
        contract = self.env['contract.order'].search([('quotation_id', '=', self.id)])
        if contract:
            return {
                'name': 'Contracts',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'contract.order',
                'view_id': False,
                'target': 'current',
                'domain': [('id', '=', contract.ids)],
                'type': 'ir.actions.act_window',
            }

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('Cannot delete Quotation')
        return super(QuotationOrder, self).unlink()

    def create_new_version(self):
        revision_id = self.revision_id
        if not revision_id:
            vals = {
                'name': self.name,
                'last_code': 0
            }
            revision_id = self.env['amc.quotation.revision'].create(vals)
            self.write({
                'revision_id': revision_id.id
            })
        action = self.env.ref('stranbys_amc.action_make_revision_wizard').read()[0]
        action['context'] = dict(
            self.env.context,
            default_order_id=self.id,
            default_revision_id=revision_id.id,
            default_next_code=revision_id.last_code + 1
        )
        return action

    def action_view_revisions(self):
        quotations = self.env['quotation.order'].search([('revision_id', '=', self.revision_id.id)])

        result = self.env['ir.actions.act_window']._for_xml_id(
            'stranbys_amc.action_view_revised_quote_amc')
        result['domain'] = [('id', 'in', quotations.ids)]
        return result

    def _compute_revision_count(self):
        for record in self:
            record.revision_count = len(
                self.env['quotation.order'].search([('revision_id', '=', self.revision_id.id)]))

    # @api.model
    # def create(self, vals):
    #     if not vals.get('name') or vals['name'] == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('contract.quote.code') or _('New')
    #     return super(QuotationOrder, self).create(vals)
