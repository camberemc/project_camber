# -*- coding: utf-8 -*-
{
    'name': 'Stevok Reports',
    'version': "14.0",
    'description': 'Stevok Reports',
    'author': "Siyad S",
    'depends': ['base', 'account','stevok_customisation'],
    'data': [
        'report/report.xml',
        'report/invoice_report.xml',
        'views/company.xml',
        'views/account.xml'
    ],
    'installable': True,
    'application': True,
}
