# -*- coding: utf-8 -*-
{
    'name': 'Labour Supply ERP',
    'version': "14.0",
    'description': 'Labour Supply ERP',
    'author': "Siyad S",
    'depends': ['base', 'project', 'hr','stranbys_timesheet'],
    'data': [
        'views/project_view.xml',
        'views/hr_employee_view.xml',
        'views/timsheet_view.xml'

    ],
    'installable': True,
    'application': True,
}
