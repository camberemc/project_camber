from odoo import fields, models, api, _


class EM(models.Model):
    _name = 'em.em'
    _description = 'EM'

    code = fields.Char(string="EM")
    name = fields.Char(string="Description")
    wbs = fields.Char(string="WBS",compute='_compute_wbs',store=True)
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project', string="Project")

    def write(self, values):
        if values.get('amount') and self.project_id:
            message = _(
                "Budgeting : EM -> %s -> Amount(%s) -> Edited by %s") % \
                      (self.name, values.get('amount'), self.env.user.name)
            self.project_id.message_post(body=message)
        return super(EM, self).write(values)

    @api.depends('code','name','project_id.project_code','project_id.sage_code')
    def _compute_wbs(self):
        for rec in self:
            if rec.code and rec.name:
                first_part = ''
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.name == 'PROJECT MATERIAL':
                    last_part = '-EMPM'
                elif rec.name == 'PROJECT SERVICES':
                    last_part = '-EMPS'
                elif rec.name == 'PROJECT OTHER EXP':
                    last_part = '-EMPOH'
                elif rec.name == 'LABOR COST':
                    last_part = '-EMPLAB'
                """
                first_part = 'EM'
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = first_part + rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.code == 'EM' and rec.name == 'PROJECT MATERIAL':
                    last_part = '-EMPM'
                elif rec.code == 'EM' and rec.name == 'PROJECT SERVICES':
                    last_part = '-EMPS'
                elif rec.code == 'EM' and rec.name == 'PROJECT OTHER EXP':
                    last_part = '-EMPOH'
                elif rec.code == 'EM' and rec.name == 'LABOR COST':
                    last_part = '-EMPLAB'
                """

                rec.wbs = first_part + second_part + last_part
            else:
                rec.wbs = ''


class HVAC(models.Model):
    _name = 'hvac.hvac'
    _description = 'HVAC'

    code = fields.Char(string="EM")
    name = fields.Char(string="Description")
    wbs = fields.Char(string="WBS",compute='_compute_wbs',store=True)
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project', string="Project")

    def write(self, values):
        if values.get('amount') and self.project_id:
            message = _(
                "Budgeting : HVAC -> %s -> Amount(%s) -> Edited by %s") % \
                      (self.name, values.get('amount'), self.env.user.name)
            self.project_id.message_post(body=message)
        return super(HVAC, self).write(values)

    @api.depends('code','name','project_id.project_code','project_id.sage_code')
    def _compute_wbs(self):
        for rec in self:
            if rec.code and rec.name:
                first_part = ''
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part =  rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.name == 'PROJECT MATERIAL':
                    last_part = '-HVPM'
                elif rec.name == 'PROJECT SERVICES':
                    last_part = '-HVPS'
                elif rec.name == 'PROJECT OTHER EXP':
                    last_part = '-HVPOH'
                elif rec.name == 'LABOR COST':
                    last_part = '-HVPLAB'
                """
                first_part = 'EM'
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = first_part + rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.code == 'HVAC' and rec.name == 'PROJECT MATERIAL':
                    last_part = '-HVPM'
                elif rec.code == 'HVAC' and rec.name == 'PROJECT SERVICES':
                    last_part = '-HVPS'
                elif rec.code == 'HVAC' and rec.name == 'PROJECT OTHER EXP':
                    last_part = '-HVPOH'
                elif rec.code == 'HVAC' and rec.name == 'LABOR COST':
                    last_part = '-HVPLAB'
                """

                rec.wbs = first_part + second_part + last_part
            else:
                rec.wbs = ''


class FC(models.Model):
    _name = 'fc.fc'
    _description = 'FC'

    code = fields.Char(string="EM")
    name = fields.Char(string="Description")
    wbs = fields.Char(string="WBS",compute='_compute_wbs',store=True)
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project', string="Project")

    def write(self, values):
        if values.get('amount') and self.project_id:
            message = _(
                "Budgeting : FC -> %s -> Amount(%s) -> Edited by %s") % \
                      (self.name, values.get('amount'), self.env.user.name)
            self.project_id.message_post(body=message)
        return super(FC, self).write(values)

    @api.depends('code','name','project_id.project_code','project_id.sage_code')
    def _compute_wbs(self):
        for rec in self:
            if rec.code and rec.name:
                first_part = ''
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.name == 'PROJECT MATERIAL':
                    last_part = '-FCPM'
                elif rec.name == 'PROJECT SERVICES':
                    last_part = '-FCPS'
                elif rec.name == 'PROJECT OTHER EXP':
                    last_part = '-FCPOH'
                elif rec.name == 'LABOR COST':
                    last_part = '-FCPLAB'
                """
                first_part = 'EM'
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = first_part + rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.code == 'FC' and rec.name == 'PROJECT MATERIAL':
                    last_part = '-FCPM'
                elif rec.code == 'FC' and rec.name == 'PROJECT SERVICES':
                    last_part = '-FCPS'
                elif rec.code == 'FC' and rec.name == 'PROJECT OTHER EXP':
                    last_part = '-FCPOH'
                elif rec.code == 'FC' and rec.name == 'LABOR COST':
                    last_part = '-FCPLAB'
                """

                rec.wbs = first_part + second_part + last_part
            else:
                rec.wbs = ''


class IT(models.Model):
    _name = 'it.it'
    _description = 'IT'

    code = fields.Char(string="EM")
    name = fields.Char(string="Description")
    wbs = fields.Char(string="WBS",compute='_compute_wbs',store=True)
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project', string="Project")

    def write(self, values):
        if values.get('amount') and self.project_id:
            message = _(
                "Budgeting : IT -> %s -> Amount(%s) -> Edited by %s") % \
                      (self.name, values.get('amount'), self.env.user.name)
            self.project_id.message_post(body=message)
        return super(IT, self).write(values)

    @api.depends('code','name','project_id.project_code','project_id.sage_code')
    def _compute_wbs(self):
        for rec in self:
            if rec.code and rec.name:
                first_part = ''
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part =  rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.name == 'PROJECT MATERIAL':
                    last_part = '-ITPM'
                elif rec.name == 'PROJECT SERVICES':
                    last_part = '-ITPS'
                elif rec.name == 'PROJECT OTHER EXP':
                    last_part = '-ITPOH'
                elif rec.name == 'LABOR COST':
                    last_part = '-ITPLAB'
                """
                first_part = 'EM'
                second_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = first_part + rec.project_id.project_code

                if rec.project_id.sage_code:
                    second_part = '-' + rec.project_id.sage_code

                if rec.code == 'IT' and rec.name == 'PROJECT MATERIAL':
                    last_part = '-ITPM'
                elif rec.code == 'IT' and rec.name == 'PROJECT SERVICES':
                    last_part = '-ITPS'
                elif rec.code == 'IT' and rec.name == 'PROJECT OTHER EXP':
                    last_part = '-ITPOH'
                elif rec.code == 'IT' and rec.name == 'LABOR COST':
                    last_part = '-ITPLAB'
                """

                rec.wbs = first_part + second_part + last_part
            else:
                rec.wbs = ''


class ADMIN(models.Model):
    _name = 'admin.admin'
    _description = 'ADMIN'

    code = fields.Char(string="EM")
    name = fields.Char(string="Description")
    wbs_char = fields.Char(string="WBS")
    wbs = fields.Char(string="WBS",compute='_compute_wbs',store=True)
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('project.project', string="Project")

    def write(self, values):
        if values.get('amount') and self.project_id:
            message = _(
                "Budgeting : ADMIN -> %s -> Amount(%s) -> Edited by %s") % \
                      (self.name, values.get('amount'), self.env.user.name)
            self.project_id.message_post(body=message)
        return super(ADMIN, self).write(values)

    @api.depends('code','name','project_id.project_code','project_id.sage_code')
    def _compute_wbs(self):
        for rec in self:
            if rec.code and rec.name:
                first_part = ''
                last_part = ''
                if rec.project_id.project_code:
                    first_part = rec.project_id.project_code

                if rec.code == 'ADMIN' and rec.name == 'ASSET PURCHASE':
                    last_part = '-AHAP'
                elif rec.code == 'ADMIN' and rec.name == 'SERVICES':
                    last_part = '-AHAS'
                elif rec.code == 'ADMIN' and rec.name == 'LABOR COST':
                    last_part = '-AHLAB'

                rec.wbs = first_part + last_part
            else:
                rec.wbs = ''
