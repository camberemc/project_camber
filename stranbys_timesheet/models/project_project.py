from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def show_timesheet(self):
        ctx = {'default_project_id': self.id}
        action = {
            'name': _('Timesheet'),
            'domain': [('project_id', '=', self.id)],
            'res_model': 'project.timesheet',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('stranbys_timesheet.view_project_timesheet_list').id, 'tree'), (False, 'form')],
            'context': ctx
        }
        return action
