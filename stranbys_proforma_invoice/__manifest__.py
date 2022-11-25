# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Proforma Invoice',
    'version': "12.0.0.1",
    'description': 'Stranbys Proforma Invoice',
    'author': "Manish Manyat(sales@stranbys.com)",
    'depends': ['account'],
    'data': [
        'security/proforma_invoice_security.xml',
        'security/ir.model.access.csv',
        'views/noupdate.xml',

        'views/account_invoice.xml',
    ],
    'installable': True,
    'application': True,
}
