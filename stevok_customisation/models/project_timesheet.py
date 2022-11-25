from odoo import api, fields, models, _


class ProjectTimesheetExtend(models.Model):
    _inherit = 'project.timesheet'

    total_hour_rates = fields.Float(string="Total Cost", compute='_get_all_hours', store=True)

    @api.depends('project_timesheet_line_ids')
    def _get_all_hours(self):
        for rec in self:
            if rec.project_timesheet_line_ids:
                total_working_hour = 0
                total_ot_hour = 0
                total_holiday_ot_hour = 0
                total_hours = 0
                total_price = 0
                for line in rec.project_timesheet_line_ids:
                    total_working_hour = total_working_hour + line.normal_working_hour
                    total_ot_hour = total_ot_hour + line.normal_ot_hour
                    total_holiday_ot_hour = total_holiday_ot_hour + line.holiday_ot_hour
                    total_hours = total_hours + line.total_hour
                    total_price = total_price + line.total_hour_rate
                rec.total_working_hour = total_working_hour
                rec.total_ot_hour = total_ot_hour
                rec.total_holiday_ot_hour = total_holiday_ot_hour
                rec.total_hours = total_hours
                rec.total_hour_rates = total_price


class ProjectTimesheetLineExtend(models.Model):
    _inherit = 'project.timesheet.line'

    overtime_per_hour = fields.Float(string="Hour Rate", related='employee_id.overtime_per_hour')
    total_hour_rate = fields.Float(string="Total Hour Rate", compute='_get_total_hour', store=True)

    @api.depends('normal_working_hour', 'normal_ot_hour', 'holiday_ot_hour')
    def _get_total_hour(self):
        for rec in self:
            rec.total_hour = rec.normal_working_hour + rec.holiday_ot_hour + rec.normal_ot_hour
            rec.total_hour_rate = rec.overtime_per_hour * rec.total_hour
            rec.timesheet_id._get_all_hours()
