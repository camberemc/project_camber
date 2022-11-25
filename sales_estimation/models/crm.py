# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CRMExtented(models.Model):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    code = fields.Char(string="Opportunity", default="_Draft", copy=False)
    so_code = fields.Char(string="Quotation Number", copy=False)
    version = fields.Integer(string="Version", copy=False, default=0)
    estimatior_id = fields.Many2one('res.users', string='Estimator')
    estimation_count = fields.Integer(string='Estimation', compute='_compute_count')

    def _compute_count(self):
        for record in self:
            record.estimation_count = len(self.env['crm.estimation'].search([('lead_id', '=', record.id)]))

    def action_create_estimation(self):
        vals = {
            'crm_id': self.id,
            'user_id': self.estimator_id.id,
        }
        self.env['crm.estimation'].create(vals)

    def create_quote(self):
        vals = {
            'name': self.get_quote_code()
        }
        self.env['sale.order'].create(vals)

    def get_quote_code(self):
        if not self.so_code:
            so_code = self.env['ir.sequence'].next_by_code('crm.quote.code')
        else:
            so_code = self.so_code
        version = self.version + 1
        self.write({
            'so_code': so_code,
            'version': version
        })
        return so_code + 'Ver.' + str(version)

    def assign_to_estimate(self):
        action = self.env.ref('sales_estimation.act_assign_to_estimation_wizard').read()[0]
        action['context'] = dict(
            self.env.context,
            default_lead_id=self.id
        )
        return action

    @api.model_create_multi
    def create(self, values):
        res = super(CRMExtented, self).create(values)
        res.write({
            'code': self.env['ir.sequence'].next_by_code('crm.quote.code')
        })
        return res
