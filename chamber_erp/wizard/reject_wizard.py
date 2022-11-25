from odoo import api, fields, models

class EstimationReject(models.TransientModel):
    _name = 'estimation.reject.wizard'

    estimation_id = fields.Many2one('crm.estimation', string='Sale Order')
    reason = fields.Char(string="Reason",required=True)

    def create_rejection(self):
        self.estimation_id.state = 'draft'
        self.estimation_id.message_post(body="Reject Reason: %s" % (self.reason))