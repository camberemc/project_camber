# -*- coding: utf-8 -*-
{
    'name': 'Task Management',
    'version': "14.0",
    'description': 'Workflow for Project Task',
    'author': "Siyad S (sales@stranbys.com)",
    'depends': ['project', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/project_task.xml',
    ],
    'installable': True,
    'application': True,
}
