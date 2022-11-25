# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning, ValidationError
import datetime as dt
from odoo.addons import decimal_precision as dp

from dateutil.relativedelta import relativedelta


class ContractOrderExtend(models.Model):
    _inherit = "contract.order"

    contract_date = fields.Date(string="Contract Date")
    terms_and_condition_id = fields.Many2one('amc.terms.condition', string="Terms and Condition"
                                             )
    terms_and_condition = fields.Text(string="Terms and Condition")
    maintenance_charge = fields.Text(string="Maintenance Charge",
                                     default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                         'stevok_customisation.maintenance_charge'))
    contract_location = fields.Char(string="Location",
                                    default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                        'stevok_customisation.contract_location'))
    agreed_upon = fields.Text(string="Both Parties Hereby agreed upon ",
                              default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                  'stevok_customisation.agreed_upon'))
    project_name = fields.Char(string="Project Name")
    quotation_notes = fields.Text(string="Quotation Note")
    remarks = fields.Text(string="Remarks")

    @api.onchange('terms_and_condition_id')
    def change_terms_and_condition_id(self):
        if self.terms_and_condition_id:
            self.write({
                'terms_and_condition': self.terms_and_condition_id.description
            })

    def confirm_contract(self):
        self.check_data()
        if self.name == 'Draft':
            self.name = self.env['ir.sequence'].next_by_code('contract.order.code')
        self.write({
            'state': 'running',
        })

    def _get_date(self):
        date = int(round(((self.end_date) - (self.start_date)).days / 365, 0))
        if date > 1:
            return 'years'
        if date == 1:
            return 'year'

    def cancel_contract(self):
        visits = self.env['contract.order.service'].search([('order_id', '=', self.id)])
        visits.unlink()
        self.write({
            'state': 'cancel'
        })

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
                'project_name':self.project_name
            }))
            date = date + dt.timedelta(days=interval)
        self.write({
            'service_line_ids': service_line_ids
        })
