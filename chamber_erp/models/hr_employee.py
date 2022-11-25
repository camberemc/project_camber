from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class HrEmployeeExtend(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'

    employee_id_no = fields.Char(string="Employee No")
    uid_no = fields.Char(string="UID No")
    joining_date = fields.Date(string="Joining Date")