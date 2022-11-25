from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime


class CRMEstimationWizard(models.TransientModel):
    _name = "crm.estimation.wizard"
    _description = "Request Estimation"

    estimator_id = fields.Many2one('res.users', 'User', required=True)
    requirement = fields.Text(string='Message')
    lead_id = fields.Many2one('crm.lead', 'Lead')
    estimation_id = fields.Many2one('crm.estimation', 'Estimations')
    create_revison = fields.Boolean(string='Create Copy')

    def create_estimation(self):
        if self.estimation_id and self.create_revison:
            rec = self.estimation_id
            s_ids = self.estimation_id.service_line_ids
            p_ids = self.estimation_id.product_line_ids
            vals = {
                'estimator_id': self.estimator_id.id,
                'requirement': self.requirement,
                'service_line_ids' :  [(0, 0, line.copy_data()[0]) for line in s_ids],
                'product_line_ids' :  [(0, 0, line.copy_data()[0]) for line in p_ids],
                'partner_id':self.lead_id.partner_id.id
            }
            rec.copy(default=vals)

        elif self.estimation_id and self.create_revison == False:
            vals = {
                'estimator_id': self.estimator_id.id,
                'state' : 'draft',
                'requirement': self.requirement,
                'partner_id': self.lead_id.partner_id.id
            }
            self.estimation_id.write(vals)
            
        else:
            if not self.lead_id.partner_id:
                raise UserError(
                    'Please assign a Customer to this Lead ')
            vals = {
                'estimator_id': self.estimator_id.id,
                'lead_id' : self.lead_id.id,
                'requirement': self.requirement,
                'partner_id': self.lead_id.partner_id.id
            }

            self.env['crm.estimation'].create(vals)

        return {'type': 'ir.actions.act_window_close'}
