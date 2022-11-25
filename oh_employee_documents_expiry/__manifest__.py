# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Document Management',
    'version': '14.0.0',
    'summary': """Documents Manamgement""",
    'category': 'Human Resources',
    'author': 'Nishad Pavil',
    'company': 'Stranbys Info Solution FZC',
    'maintainer': 'Stranbys Info Solution FZC',
    'website': "https://www.stranbys.com",
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_document_view.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
