# -*- coding: utf-8 -*-
{
    'name': 'Sales Estimation for Projects',
    'version': "14.0.0.1",
    'description': 'Workflow for Sales Estimation and Rivisions for projects',
    'author': "Roopesh Sivam (sales@stranbys.com)",
    'depends': [
        'base','product','sale_crm', 'crm', 'sale_management',
        'contacts', 'l10n_ae', 'stock', 'project'],
    'data': [
        'security/sales_estimation_security.xml',
        'security/ir.model.access.csv',
        'views/noupdate.xml',

        'wizard/crm_wizard.xml',

        'views/crm.xml',
        'views/estimation.xml',
        'views/sale.xml',
        'views/product.xml',

        'wizard/reject_wizard.xml'
    ],
    'installable': True,
    'application': True,
    'post_init_hook': 'post_init_hook',
}
