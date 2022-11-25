from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class EstimationRevision(models.TransientModel):
    _name = 'crm.estimation.revision.wizard'

    estimation_id = fields.Many2one('crm.estimation', string='Estimation')
    revision_id = fields.Many2one('crm.estimation.revision', string='Revision Group')
    next_code = fields.Integer(string='Next Code')
    reason = fields.Char(string="Reason", required=True)

    def create_revision(self):
        vals = {
            'name': self.revision_id.name + ' R' + str(self.next_code),
            'state': 'draft',
            'revision_id': self.revision_id.id,
        }
        copy_id = self.estimation_id.copy(default=vals)
        copy_id.compute_line_data()
        self.revision_id.write({
            'last_code': self.next_code
        })
        self.estimation_id.message_post(body=_("Revision: %s Reason: %s") % (self.next_code, self.reason))
        action = self.env.ref('chamber_erp.act_estimation_view').read()[0]
        form_view = [(self.env.ref('chamber_erp.estimation_form_view').id, 'form')]
        action['views'] = form_view
        action['res_id'] = copy_id.id
        return action
