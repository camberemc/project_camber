{
   'name' : "Credit Limit",
   'version' : "14.0.0.1",
   'description' : 'ERP Modules for Credit imit',
   'category': 'Credit Limit',
   'depends' : ['base', 'account', 'sale_management', ],
   'data' : [
       'views/res_partner_view.xml',
       'views/sale.xml'

   		],
   'installable' : True,
   'application': True,
}

