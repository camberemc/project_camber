# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Payment Management',
    'version': '14.0',
    'summary': """Payment Management for Accountiing""",
    'description': "All in One Payment Cash,bank,pdc",
    'category': "Accounting",
    'author': 'Siyad S',
    'company': 'Stranbys Info Solutions',
    'website': "https://www.stranbys.com",
    'depends': ['base', 'account', 'mail','project'],
    'data': [
        'views/noupdate.xml',
        'security/stranbys_pdc_security.xml',
        'security/ir.model.access.csv',
        'views/cheques.xml',
        'wizard/process_cheques.xml',
        'views/menu_items.xml',
        'views/journal.xml',
        'reports/report_menu.xml',
        'reports/payment_receipt.xml'

    ],
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
