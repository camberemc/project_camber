# -*- coding: utf-8 -*-
{
    'name': ' Stranbys Outstanding Statement',
    'version': "14.0.0.1",
    'description': 'Partner Outstanding Statement',
    'author': "Siyad S ",
    'depends': ['base', 'account','report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'reports/report_menu.xml',
        'reports/partner_statement_template.xml',
        'wizard/partner_statement_wizard_view.xml',

    ],
    'installable': True,
    'application': True,
    # 'post_init_hook': 'post_init_hook',
}
