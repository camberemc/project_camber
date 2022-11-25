# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Expense Voucher',
    'version': '14.0',
    'summary': """Expense Voucher""",
    'description': "Expense Voucher",
    'category': "Accounting",
    'author': 'Siyad S',
    'company': 'Stranbys Info Solutions',
    'website': "https://www.stranbys.com",
    'depends': ['base', 'account'],
    'data': [
        'security/data.xml',
        'security/ir.model.access.csv',
        'views/expense_voucher_view.xml',
        'reports/report_menu.xml',
        'reports/expense_voucher_template.xml'

    ],
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
