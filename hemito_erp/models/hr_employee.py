from odoo import api, fields, models, _

class HrEmployeeExtend(models.Model):
    _inherit = "hr.employee"

    overtime_per_hour = fields.Float(string="Overtime Per Hour")
    employee_id_no = fields.Char(string="Employee No")
    uid_no = fields.Char(string="UID No")
    joining_date = fields.Date(string="Joining Date")