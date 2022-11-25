from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp




class ProjectTaskExtented(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'

    task_employee_lines = fields.One2many('project.task.employee.line', 'task_id', string="Overtime Details")


class ProjectTaskEmployee(models.Model):
    _name = 'project.task.employee.line'
    _description = "Project Task Employee line"
    _order = 'id desc'

    task_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', related='task_id.project_id', string="Project")
    employee_id = fields.Many2one('hr.employee', string="Employee Assigned")
    ot_hours = fields.Float(string="Overtime")
    total_cost = fields.Float(string="Total Cost", compute='_get_employee_cost')

    @api.depends('employee_id', 'ot_hours')
    def _get_employee_cost(self):
        for record in self:
            record.total_cost = 0
            if record.employee_id:
                if record.ot_hours:
                    record.total_cost = record.ot_hours * record.employee_id.ot_cost
                else:
                    record.total_cost = record.employee_id.daily_cost
