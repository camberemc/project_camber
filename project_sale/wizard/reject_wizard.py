from odoo import api, fields, models

class EstimationReject(models.TransientModel):
    _name = 'project.reject.wizard'

    project_id = fields.Many2one('project.project', string='Project')
    reason = fields.Char(string="Reason",required=True)

    def create_rejection(self):
        self.project_id.state = 'ongoing'
        self.project_id.message_post(body="Reject Reason: %s" % (self.reason))