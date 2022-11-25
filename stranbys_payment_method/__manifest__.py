# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Payments and Receipts',
    'version': '14.0.1.0',
    'summary': """Payment Management for odoo14 """,
    'email' : "roopeshsivam@gmail.com",
    'description': "Payments, Receipts,",
    'category': "Accounting",
    'author': 'Roopesh Sivam',
    'company': 'Stranbys Info Solutions',
    'website': "https://www.stranbys.com",
    'depends': ['base', 'account', 'mail'],
    'data': [
        'views/noupdate.xml',
        
        # 'security/stranbys_pdc_security.xml',
        'security/ir.model.access.csv',
        
        'views/account_payment.xml',
        'views/account_move.xml',
        'views/master_view.xml',
        

        # 'wizard/process_cheques.xml',
        # 'wizard/journal_matching_wizard.xml',
        'wizard/payment_maping_wizard.xml',
        # 'wizard/cheque_clearence_wizard.xml',

        # 'reports/report_menu.xml',
        # 'reports/payment_receipt.xml'

    ],
    'demo': [
    ],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
