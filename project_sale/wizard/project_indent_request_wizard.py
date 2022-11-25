from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp


class ProjectIndentRequestWizard(models.TransientModel):
    _name = 'project.indent.request.wizard'

    line_ids = fields.Many2many('project.project.orderline', string='Indent Lines')

    @api.model
    def default_get(self, fields):
        """ 
        Use active_ids from the context to fetch.
        """
        record_ids = self._context.get('active_ids')
        result = super(ProjectIndentRequestWizard, self).default_get(fields)
        context = self._context.get('active_ids')

        #selecting records from active id
        if record_ids:
            if 'line_ids' in fields:
                selected = self.env['project.project.orderline'].browse(context)
                result['line_ids'] = selected.ids
        return result

    def indent_request(self):
        if self.line_ids:
            for line in self.line_ids:
                if line.indented_qty_added <= 0:
                    raise Warning(
                        _('You cannot set 0 quatity, to indent request. Remove from orderline to request later'))
        else:
            raise Warning(
                _('No Orderlines or Something went Wrong'))  
        
        for line in self.line_ids:
            vals = {
                'project_order_line_id' : line.id,
                'date' : line.intented_date,
                'user_id' : self.env.uid,
                'qty' : line.indented_qty_added,
            }
            self.env['project.indent.request.line'].create(vals)
            line.update({
                'intented_date' : False,
                'indented_qty_added' : 0
            })




              
        # picking_type_id = 2
        # location_id = 11
        # location_dest_id = 9
        # line_ids = ['id', 'in', self.line_ids.ids]
        # group_projects = self.line_ids.read_group(
        #     [line_ids], fields=['project_id', 'product_id'], groupby='project_id')

        # if self.partner_id:
        #     vals = {
        #     'partner_id': self.partner_id.id,
        #     'date_order': datetime.now(),
        #     'state': 'draft',
        #     'origin': group_projects[0]['project_id'][1],
        #     'picking_type_id': picking_type_id,
        #     'location_id': location_id,
        #     'location_dest_id': location_dest_id,
        # }
        # do_id = self.env['stock.picking'].create(vals)

        # for line in self.line_ids:
        #     vals2 = {
        #         'product_id' : line.product_id.id,
        #         'name': line.name,
        #         'picking_id': do_id.id,
        #         'product_uom_qty' : line.qty_added_delivery,
        #         'product_uom': line.uom_id.id,
        #         'location_id': location_id,
        #         'location_dest_id': location_dest_id,
        #     }
        #     move_id = self.env['stock.move'].create(vals2)

        #     vals3 = {
        #         'move_line_id' : move_id.id,
        #         'project_order_line_id' : line.id,
        #         'qty' : line.qty_added_delivery,
        #     }

        #     added = line.qty_added_delivery
        #     # self.env['project.delivery.line'].create(vals3)

        #     line.write({
        #         'qty_added_delivery' : 0,
        #         'delivered_qty' : line.delivered_qty + added,
        #         'picking_ids' :  [(4, do_id.id)]
        #     })