from odoo import api, fields, models, _

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    project_id = fields.Many2one('project.project', string='Project')
    project_value = fields.Float(string="Project Value")


    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            self.project_value = self.project_id.total_sale_value




class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    project_id = fields.Many2one('project.project', string='Project',
                                 readonly=False)
