# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning, ValidationError
import datetime as dt
from odoo.addons import decimal_precision as dp

from dateutil.relativedelta import relativedelta
from datetime import date, timedelta


class QuotationOrderExtend(models.Model):
    _inherit = "quotation.order"

    READONLY_STATES = {
        'confirmed': [('readonly', True)],

    }
    quotation_date = fields.Date(string="Quotation Date", states=READONLY_STATES)
    project_name = fields.Char(string="Project Name", states=READONLY_STATES)
    quotation_notes = fields.Text(string="Quotation Note",
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                      'stevok_customisation.quotation_notes'), states=READONLY_STATES)

    user_id = fields.Many2one('res.users', string='Sales Contact', default=lambda self: self.env.user,
                              states=READONLY_STATES)

    remarks = fields.Text(string="Remarks")

    def confirm_quotation(self):
        res = super(QuotationOrderExtend, self).confirm_quotation()
        contract = self.env['contract.order'].search([('quotation_id', '=', self.id)])
        contract.write({
            'contract_date': date.today(),
            'project_name': self.project_name,
            'quotation_notes': self.quotation_notes,
            'terms_and_condition_id': self.terms_and_condition_id.id,
            'terms_and_condition': self.terms_and_condition
        })
        return res


