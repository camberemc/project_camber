from odoo import api, fields, models, _


class HrEmployeeExtend(models.Model):
    _inherit = "hr.employee"

    overtime_per_hour = fields.Float(string="Overtime Per Hour")