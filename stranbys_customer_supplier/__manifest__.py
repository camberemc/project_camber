# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Customer Supplier',
    'version': "14.0.0.1",
    'description': 'To Identify Customer and Supplier in odoo14',
    'author': "Siyad S",
    'depends': ['base', 'sale','purchase'],
    'data': [
        'views/res_partner.xml'

    ],
    'installable': True,
    'application': True,
    # 'post_init_hook': 'post_init_hook',
}
