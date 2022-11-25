# Copyright 2018 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class PartnerStatementWizard(models.TransientModel):
    """Partner Statement wizard."""

    _name = "partner.statements.wizard"
    _description = "Partner Statement Wizard"

    partner_id = fields.Many2one('res.partner', string="Customer", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    invoice_type = fields.Selection([
        ('out_invoice', 'Receivable'),
        ('in_invoice', 'Payable')
    ], string='Type', required=True)
    # bucket_1 = fields.Integer(string="Ageing - 30", default=30)
    # bucket_2 = fields.Integer(string="Ageing - 60", default=60)
    # bucket_3 = fields.Integer(string="Ageing - 90", default=90)
    # bucket_4 = fields.Integer(string="Ageing - 120", default=120)
    # bucket_5 = fields.Integer(string="Ageing - 150", default=150)

    # unverified_ok = fields.Boolean(string='Include Unverified')
    

    def button_export_pdf(self):
        """Export to PDF."""
        return self.env.ref('stranbys_outstanding.action_print_partner_statements').report_action(self)

    # def button_report_xlsx(self):
    #     return self.env.ref('stranbys_partner_statement_with_pdc.report_partner_statement_xlsx').report_action(self)


