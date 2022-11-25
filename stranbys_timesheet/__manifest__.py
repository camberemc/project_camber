# -*- coding: utf-8 -*-
{
    'name': 'Stranbys Timesheet',
    'version': "14.0.1",
    'description': """Timesheet for Project""",
    'author': "Siyad (siyad.dx007@gmail.com",
    'depends': ['base', 'project', 'hr'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/timesheet_view.xml',
        'views/project_view.xml',
        'views/hr_employee_view.xml'

    ],
    'installable': True,
    'application': True,
}
