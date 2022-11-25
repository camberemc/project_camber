# -*- coding: utf-8 -*-
{
    'name': 'Stranbys AMC',
    'version': "14.0",
    'description': 'Stranbys AMC Module',
    'author': "Siyad S",
    'depends': ['base', 'sale', 'project', 'account','hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/stranbys_amc_security.xml',
        'data/noupdate.xml',
        'views/amc_contract_view.xml',
        'views/amc_quotation_view.xml',
        'views/master_views.xml',
        'wizards/revision_wizard.xml'
    ],
    'installable': True,
    'application': True,
}
