from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectTimesheet(models.Model):
    _name = 'project.timesheet'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Timesheet'
    # _order = 'id desc'
    _order = 'name'

    code = fields.Char(string="Code", default='_draft', copy=False, readonly=True,track_visibility='onchange')
    name = fields.Char(string="Name", default='_draft', copy=False, readonly=True, store=True, compute='_get_name')
    project_id = fields.Many2one('project.project', string="Project", copy=False, required=True,track_visibility='onchange')

    from_date = fields.Date(String='From Date', required=True,track_visibility='onchange')
    to_date = fields.Date(String='To Date', required=True,track_visibility='onchange')
    prepared_by = fields.Many2one('res.users', string="Prepared By", default=lambda self: self.env.user,track_visibility='onchange')
    project_timesheet_line_ids = fields.One2many('project.timesheet.line', 'timesheet_id', string="Project Lines",
                                                 copy=True)
    total_working_hour = fields.Float(string="Total Working Hour", compute='_get_all_hours', store=True)
    total_ot_hour = fields.Float(string="Total Ot Hour", compute='_get_all_hours', store=True)
    total_holiday_ot_hour = fields.Float(string="Total Holiday Ot Hour", compute='_get_all_hours', store=True,track_visibility='onchange')
    total_hours = fields.Float(string="Total", compute='_get_all_hours', store=True)
    note = fields.Text(string="Notes")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approval', 'Waiting Approval'),
        ('reject', 'Rejected'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', copy=False, track_visibility='onchange')

    @api.depends('project_id', 'code', 'from_date', 'to_date')
    def _get_name(self):
        for rec in self:
            if rec.name and rec.project_id and rec.from_date and rec.to_date and rec.code:
                from_date = rec.from_date.strftime('%d/%m/%Y')
                to_date = rec.to_date.strftime('%d/%m/%Y')
                rec.name = rec.project_id.display_name + '-' + str(from_date) + '-' + str(to_date) + '-' + rec.code
            else:
                rec.name = False

    def send_approve_quotation(self):
        self.write({
            'state': 'approval'
        })

    def reject_quotation(self):
        self.write({
            'state': 'reject',
        })
    def approve_quotation(self):
        self.write({
            'state': 'approved',
        })
    def set_to_draft(self):
        self.write({
            'state':'draft'
        })

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('project.timesheet.code')
        return super(ProjectTimesheet, self).create(vals)

    @api.depends('project_timesheet_line_ids')
    def _get_all_hours(self):
        for rec in self:
            if rec.project_timesheet_line_ids:
                total_working_hour = 0
                total_ot_hour = 0
                total_holiday_ot_hour = 0
                total_hours = 0
                for line in rec.project_timesheet_line_ids:
                    total_working_hour = total_working_hour + line.normal_working_hour
                    total_ot_hour = total_ot_hour + line.normal_ot_hour
                    total_holiday_ot_hour = total_holiday_ot_hour + line.holiday_ot_hour
                    total_hours = total_hours + line.total_hour
                rec.total_working_hour = total_working_hour
                rec.total_ot_hour = total_ot_hour
                rec.total_holiday_ot_hour = total_holiday_ot_hour
                rec.total_hours = total_hours

    def unlink(self):
        raise UserError('Cannot delete Timesheet')
        return super(ProjectTimesheet, self).unlink()


class ProjectTimesheetLine(models.Model):
    _name = 'project.timesheet.line'

    timesheet_id = fields.Many2one('project.timesheet', string="Timesheet")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    job_id = fields.Many2one('hr.job', 'Job Position',related='employee_id.job_id')
    normal_working_hour = fields.Float(string="Normal Working Hour")
    normal_ot_hour = fields.Float(string="Normal Ot Hour")
    holiday_ot_hour = fields.Float(string="Holiday Ot Hour")
    total_hour = fields.Float(string="Total Hour", compute='_get_total_hour', store=True)
    project_id = fields.Many2one('project.project', string="Project", related='timesheet_id.project_id')

    @api.depends('normal_working_hour', 'normal_ot_hour', 'holiday_ot_hour')
    def _get_total_hour(self):
        for rec in self:
            rec.total_hour = rec.normal_working_hour + rec.holiday_ot_hour + rec.normal_ot_hour
            rec.timesheet_id._get_all_hours()
