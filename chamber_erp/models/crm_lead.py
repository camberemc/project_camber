from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_type = fields.Selection(
        [('fire_consulting', 'Fire Consulting'),
         ('electro_mechanical', 'Electro Mechanical'),
         ('technical_outsourcing', 'Technical Outsourcing'),
         ('facility_management', 'Facility Management')], string='Type',
        required=True)
    seq = fields.Char(
        'Lead', index=True, readonly=True, tracking=True, store=True)

    estimatior_id = fields.Many2one('res.users', string='Estimator')
    estimation_count = fields.Integer(string='Estimation', compute='_compute_count')

    partner_id = fields.Many2one(
        'res.partner', string='Customer', index=True, tracking=10, required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")

    def _compute_count(self):
        for record in self:
            record.estimation_count = len(self.env['crm.estimation'].search([('lead_id', '=', record.id)]))

    def action_create_estimation(self):
        vals = {
            'crm_id': self.id,
            'user_id': self.estimator_id.id,
            'estimation_type': self.crm_type
        }
        self.env['crm.estimation'].create(vals)

    # def create_quote(self):
    #     vals = {
    #         'name': self.get_quote_code()
    #     }
    #     self.env['sale.order'].create(vals)

    # def get_quote_code(self):
    #     if not self.so_code:
    #         so_code = self.env['ir.sequence'].next_by_code('crm.quote.code')
    #     else:
    #         so_code = self.so_code
    #     version = self.version + 1
    #     self.write({
    #         'so_code': so_code,
    #         'version': version
    #     })
    #     return so_code + 'Ver.' + str(version)

    def assign_to_estimate(self):
        action = self.env.ref('chamber_erp.act_assign_to_estimation_wizard').read()[0]
        action['context'] = dict(
            self.env.context,
            default_lead_id=self.id,
            default_crm_type=self.crm_type
        )
        return action

    @api.model
    def create(self, vals):
        if vals['crm_type'] == 'fire_consulting':
            vals['seq'] = self.env['ir.sequence'].next_by_code('crm.lead.fire')
        if vals['crm_type'] == 'electro_mechanical':
            vals['seq'] = self.env['ir.sequence'].next_by_code('crm.lead.electro')
        if vals['crm_type'] == 'technical_outsourcing':
            vals['seq'] = self.env['ir.sequence'].next_by_code('crm.lead.technical')
        if vals['crm_type'] == 'facility_management':
            vals['seq'] = self.env['ir.sequence'].next_by_code('crm.lead.facility')
        return super(CrmLead, self).create(vals)

    def unlink(self):
        raise UserError('Cannot delete Lead')
        return super(CrmLead, self).unlink()

    def action_sale_quotations_new(self):
        if not self.partner_id:
            ctx = {'default_name': self.seq}
            action = {
                'name': _('Quotation'),
                'res_model': 'sale.order',
                'type': 'ir.actions.act_window',
                'context': ctx
            }
            return action

            # return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            return self.action_new_quotation()

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = {
            'search_default_opportunity_id': self.id,
            'default_opportunity_id': self.id,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_campaign_id': self.campaign_id.id,
            'default_medium_id': self.medium_id.id,
            'default_origin': self.name,
            'default_source_id': self.source_id.id,
            'default_company_id': self.company_id.id or self.env.company.id,
            'default_tag_ids': [(6, 0, self.tag_ids.ids)],
            'default_name': self.seq
        }
        if self.team_id:
            action['context']['default_team_id'] = self.team_id.id,
        if self.user_id:
            action['context']['default_user_id'] = self.user_id.id
        return action
