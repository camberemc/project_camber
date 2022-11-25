from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    project_id = fields.Many2one('project.project', string='Project')


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    project_id = fields.Many2one('project.project', string='Project',
                                 readonly=False)
