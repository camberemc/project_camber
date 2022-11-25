from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class HrEmployeeExtend(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'


    employee_status = fields.Selection(
        [("active", "Active"), ("vacation", "Vacation")],
        string="Online Status",
        default="active",
    )

    def action_timesheet_lines(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stranbys_timesheet.act_project_timesheet_line")
        action['domain'] = [('employee_id', '=', self.id)]
        return action

    @api.depends('address_id')
    def _compute_phones(self):
        for employee in self:
            employee.work_phone = False