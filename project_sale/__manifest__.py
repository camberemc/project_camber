# -*- coding: utf-8 -*-
{
    'name': 'Sales Project Connection',
    'version': "14.0.0.1",
    'description': 'Workflow for sales to project and project delivery',
    'author': "Roopesh Sivam (sales@stranbys.com)",
    'depends': [
        'sale', 'stock', 'project',
        'purchase', 'sales_estimation','crm'],
    'data': [
        'data/project_server_actions.xml',
        'security/project_sale_security.xml',
        'security/ir.model.access.csv',
        'views/noupdate.xml',
        'views/project.xml',
        'views/sale.xml',
        'views/inventory_return.xml',
        'views/invoice.xml',
        'wizard/assign_project_wizard.xml',
        'wizard/project_order_delivery_wizard.xml',
        'wizard/project_order_purchase_wizard.xml',
        'wizard/project_indent_request_wizard.xml',
        'wizard/project_consumable_delivery_wizard.xml',
        'wizard/rejection_wizard.xml',
        'wizard/inventory_return_wizard.xml',
        'wizard/indent_inventory_return.xml'
    ],
    'installable': True,
    'application': True,
}
