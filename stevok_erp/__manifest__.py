# -*- coding: utf-8 -*-
{
    'name': "Stevok",
    'version': '14.0',
    'description': """
        Long description of module's purpose
    """,
    'author': " ",

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/report.xml',
        'reports/invoice_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
