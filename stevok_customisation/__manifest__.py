# -*- coding: utf-8 -*-
{
    'name': 'Stevok Customisation',
    'version': "14.0",
    'description': 'Stevok Customisation',
    'author': "Siyad S",
    'depends': ['base', 'sale', 'stranbys_amc', 'project_management', 'purchase', 'report_xlsx', 'stranbys_timesheet'],
    'data': [
        'report/noupdate.xml',
        'security/ir.model.access.csv',
        'views/amc_contract_view.xml',
        'views/amc_quotation_view.xml',
        'views/masters.xml',
        'views/purchase_order.xml',
        'views/sale_order_view.xml',
        'views/stock_picking.xml',
        'views/project_view.xml',
        'views/hr_employee_view.xml',
        'views/invoice_view.xml',
        'views/timsheet_view.xml',
        'wizards/assign_project_wizard_extend.xml',
        'wizards/project_order_purchase_wizard.xml',
        'report/report.xml',
        'report/custom_reports_view.xml',
        'report/custom_sale_report.xml',
        'report/stevok_amc_quotation_report.xml',
        'report/stevok_amc_contract_report.xml',
        'report/purchase_order.xml',
        'report/invoice_report.xml'


    ],
    'installable': True,
    'application': True,
}
