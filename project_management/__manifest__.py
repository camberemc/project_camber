# -*- coding: utf-8 -*-
{
    'name': 'Project Management',
    'version': "14.0",
    'description': 'Workflow for Project',
    'author': "Siyad S (sales@stranbys.com)",
    'depends': ['account', 'sale', 'project', 'purchase', 'stock', 'report_xlsx', 'sale_crm' ],
    'data': [
        'data/project_server_actions.xml',
        'security/project_invoice_security.xml',
        'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/sale_order_report_template.xml',
        'views/noupdate.xml',
        'views/invoice.xml',
        'views/sale.xml',
        'views/project.xml',
        'wizard/assign_project_wizard.xml',
        'wizard/project_order_delivery_wizard.xml',
        'wizard/project_order_purchase_wizard.xml',
        'wizard/project_consumable_delivery_wizard.xml'
    ],
    'installable': True,
    'application': True,
}
