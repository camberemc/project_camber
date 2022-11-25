from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime, date
from odoo.addons import decimal_precision as dp


class ProjectSaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    lock_sale = fields.Binary(string='Lock Sale')
    project_status = fields.Selection(related='project_id.state')
    project_id = fields.Many2one('project.project', string='Project Name', copy=False)
    is_project_assigned = fields.Boolean(string='Project Assigned', compute='_project_assigned')
    date_start = fields.Datetime(string="Start Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending of Approval'),
        ('draft_quot', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    # approver_id = fields.Many2one('res.users', string='Approved By', track_visibility='onchange')

    def release_quotation(self):
        self.write({
            'state': 'draft'
        })

    def approve_quotation(self):
        self.write({
            'state': 'draft_quot'
        })

    def send_approve_quotation(self):
        users = self.env['res.users'].search(
            [('groups_id', '=', self.env.ref('project_sale.group_show_qtn_approval').id)])
        if users:
            for user in users:
                self.env['mail.activity'].create({
                    'summary': 'Approval Request',
                    'date_deadline': date.today(),
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'sale.order')], limit=1).id,
                    'res_id': self.id,
                    'user_id': user.id
                })
        self.write({
            'state': 'pending'
        })

    @api.onchange('order_line')
    def _on_change_order_line(self):
        if self.state in ('draft_quot', 'send', 'sale'):
            raise UserError(_('You have no access to edit this quotation'))

    def write(self, values):
        if 'order_line' in values:
            self._on_change_order_line()
        return super(ProjectSaleOrder, self).write(values)

    @api.depends('project_id')
    def _project_assigned(self):
        for record in self:
            if record.project_id:
                record.is_project_assigned = True
            else:
                record.is_project_assigned = False

    def assign_project(self):
        action = self.env.ref('project_sale.action_assign_project').read()[0]
        action['context'] = dict(
            self.env.context,
            default_order_id=self.id,
        )
        return action

    def _prepare_invoice(self):
        invoice_vals = super(ProjectSaleOrder, self)._prepare_invoice()
        if self.project_id:
            invoice_vals['project_id'] = self.project_id.id
            invoice_vals['project_value'] = self.project_id.total_sale_value
        # print(jahas)
        return invoice_vals

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft_quot').with_context(tracking_disable=True).write(
                {'state': 'sent'})
        return super(ProjectSaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)




class ProjectSalesOrderLineExtent(models.Model):
    _name = 'sale.order.line'
    _inherit = 'sale.order.line'

    project_id = fields.Many2one('project.project', related='order_id.project_id', string='Project Name')

    def _prepare_invoice_line(self, **optional_values):
        """
        Prepare the dict of values to create the new invoice line for a sales order line.

        :param qty: float quantity to invoice
        :param optional_values: any parameter that should be added to the returned invoice line
        """
        self.ensure_one()
        res = {
            'display_type': self.display_type,
            'sequence': self.sequence,
            'name': self.name,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.qty_to_invoice,
            'discount': self.discount,
            'price_unit': self.price_unit,
            'tax_ids': [(6, 0, self.tax_id.ids)],
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
            'sale_line_ids': [(4, self.id)],
            'project_id': self.project_id.id
        }
        if optional_values:
            res.update(optional_values)
        if self.display_type:
            res['account_id'] = False
        return res


class AccountMoveExtent(models.Model):
    _name = 'account.move'
    _inherit = 'account.move'

    discount = fields.Float(string="Discount")


class LeadCRMProjects(models.Model):
    _inherit = 'crm.lead'

    def action_view_sale_order(self):
        # raise UserError('Goo Away')
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context'] = {
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id,
        }
        action['domain'] = [('opportunity_id', '=', self.id), ('state', 'in', ('sale', 'done'))]
        orders = self.mapped('order_ids').filtered(lambda l: l.state in ('sale', 'done'))
        if len(orders) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = orders.id
        return action

    def action_view_sale_quotation(self):
        # raise UserError('Goo Away')
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context'] = {
            'search_default_draft': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_partner_id': self.partner_id.id,
            'default_opportunity_id': self.id
        }
        action['domain'] = [('opportunity_id', '=', self.id),
                            ('state', 'in', ['draft', 'sent', 'pending', 'draft_quot'])]
        quotations = self.mapped('order_ids').filtered(lambda l: l.state in ('draft', 'sent', 'pending', 'draft_quot'))
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = quotations.id
        return action

    @api.depends('order_ids.state', 'order_ids.currency_id', 'order_ids.amount_untaxed', 'order_ids.date_order',
                 'order_ids.company_id')
    def _compute_sale_data(self):
        for lead in self:
            total = 0.0
            quotation_cnt = 0
            sale_order_cnt = 0
            company_currency = lead.company_currency or self.env.company.currency_id
            for order in lead.order_ids:
                if order.state in ('draft', 'sent', 'pending', 'draft_quot'):
                    quotation_cnt += 1
                if order.state in ('sale', 'done'):
                    sale_order_cnt += 1
                    total += order.currency_id._convert(
                        order.amount_untaxed, company_currency, order.company_id,
                        order.date_order or fields.Date.today())
            lead.sale_amount_total = total
            lead.quotation_count = quotation_cnt
            lead.sale_order_count = sale_order_cnt


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        res = super()._prepare_invoice_values(order, name, amount, so_line)
        if order.project_id:
            res['project_id'] = order.project_id.id
        return res
