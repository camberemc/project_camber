# -*- coding: utf-8 -*-
{
    'name': 'Hemito Customisation',
    'version': "14.0",
    'description': 'Hemito Customisation',
    'author': "Siyad S",
    'depends': ['base', 'purchase', 'sale', 'crm', 'stranbys_saleorder_revision'],
    'data': [
        'reports/noupdate.xml',
        'security/data.xml',
        'security/ir.model.access.csv',
        'views/masters.xml',
        'views/purchase_order.xml',
        'views/sale_order_view.xml',
        'views/crm_lead_view.xml',
        'views/product_view.xml',
        'views/hr_employee_view.xml',
        'reports/report.xml',
        'reports/purchase_order_report.xml',
        'reports/sale_order_report.xml'

    ],
    'installable': True,
    'application': True,
}
