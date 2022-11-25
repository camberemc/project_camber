from odoo import api, fields, models, _


class ProjectExtented(models.Model):
    _inherit = 'project.project'

    total_labour_expense = fields.Float(string="Labour Expense")

    def update_project_summary(self):
        for rec in self:
            timesheet = self.env['project.timesheet'].search([('project_id', '=', rec.id), ('state', '=', 'approved')])
            if timesheet:
                rec.total_labour_expense = sum(timesheet.mapped('total_hour_rates'))
            else:
                rec.total_labour_expense = 0
