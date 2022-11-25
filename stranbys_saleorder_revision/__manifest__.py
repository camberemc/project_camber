# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Ouotation Revision',
    'version': "14.0.1",
    'description': """Revisions and Versions for Sales Orders and Quotations""",
    'author': "Roopesh Sivam (roopeshsivam@gmail.com)",
    'depends': ['base', 'sale'],
    'data': [
        'security/stranbys_saleorder_revision_security.xml',
        'security/ir.model.access.csv',
        'views/noupdate.xml',
        'views/sales.xml',
        'wizards/revision_wizard.xml'
    ],
    'installable': True,
    'application': True,
}
