from odoo import api, fields, models, _


class ProjectExtent(models.Model):
    _inherit = 'project.project'

    project_inventory_ids = fields.One2many('stock.move', 'project_id',
                                                       string='Inventory Lines')
    work_location = fields.Char("Work Location")

    def update_project_summary(self):
        for rec in self:
            rec.total_material_cost = 0
            rec.total_expense = 0
            rec.total_income = 0
            journal_ids = self.env['account.journal'].search([('name', '!=', 'Customer Invoices')])
            expense = self.env['account.move.line'].search(
                [('project_id', '=', rec.id), ('journal_id', 'in', journal_ids.ids), ('move_id.state', '=', 'posted')])
            journal_id = self.env['account.journal'].search([('name', '=', 'Customer Invoices')], limit=1)
            income = self.env['account.move'].search(
                [('project_id', '=', rec.id), ('journal_id', '=', journal_id.id), ('state', '=', 'posted')])
            if rec.project_line_product_ids:
                for line in rec.project_line_product_ids:
                    if line.qty_delivered:
                        rec.total_material_cost = rec.total_material_cost + (line.qty_delivered * line.cost)
            if rec.project_inventory_ids:
                for line in rec.project_inventory_ids:
                    if line.quantity_done:
                        rec.total_material_cost = rec.total_material_cost + (line.quantity_done * line.product_id.standard_price)

            if expense:
                for exp in expense:
                    rec.total_expense = rec.total_expense + exp.debit
            if income:
                for inc in income:
                    rec.total_income = rec.total_income + inc.amount_total
            total_expense_material = rec.total_expense + rec.total_material_cost
            rec.total_profit = rec.total_income - total_expense_material
            try:
                rec.total_profit_per = (rec.total_profit * 100) / rec.total_income
            except ZeroDivisionError:
                rec.total_profit_per = 0