from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    seq = fields.Char(
        'Lead', index=True, readonly=True, tracking=True, store=True)

    @api.model
    def create(self, vals):
        vals['seq'] = self.env['ir.sequence'].next_by_code('crm.lead.seq')
        return super(CrmLead, self).create(vals)

    def unlink(self):
        raise UserError('Cannot delete Lead')
        return super(CrmLead, self).unlink()
