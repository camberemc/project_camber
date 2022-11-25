# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Stock Report',
    'version': "14.0.1",
    'description': """Stock Reports""",
    'author': "Siyad (siyad.dx007@gmail.com",
    'depends': ['base', 'stock', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock.xml',
        'wizard/stock_movement_report.xml',
        'reports/stock_report.xml'

    ],
    'installable': True,
    'application': True,
}
