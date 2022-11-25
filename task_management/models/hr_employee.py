from odoo import api, fields, models, _


class HrEmployeeExtend(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    daily_cost = fields.Float(string="Daily Cost")
    ot_cost = fields.Float(string="Overtime Cost")
