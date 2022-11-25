from odoo import api, fields, models, _

class UserExtend(models.Model):
    _inherit = 'res.users'

    job_position = fields.Char(string="Job Position")