from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp

class QuotationRevision(models.TransientModel):
    _name = 'quotation.order.revision.wizard'

    order_id = fields.Many2one('quotation.order', string='Quotation Order')
    revision_id = fields.Many2one('amc.quotation.revision', string='Revision Group')
    next_code = fields.Integer(string='Next Code')
    reason = fields.Char(string="Reason", required=True)

    def create_revision(self):
        vals = {
                'name': self.revision_id.name + ' R' + str(self.next_code),
                # 'state': 'draft',
                'revision_id': self.revision_id.id
            }
        copy_id = self.order_id.copy(default=vals)
        self.revision_id.write({
            'last_code' : self.next_code
        })
        self.order_id.message_post(body=_("Revision: %s Reason: %s") % (self.next_code, self.reason))
        action = self.env.ref('stranbys_amc.act_amc_quotation_view').read()[0]
        form_view = [(self.env.ref('stranbys_amc.view_amc_quotation_form').id, 'form')]
        action['views'] = form_view
        action['res_id'] = copy_id.id
        return action