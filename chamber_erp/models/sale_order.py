# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime


class SaleOrderExtend(models.Model):
    _inherit = "sale.order"

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending of Approval'),
        ('draft_quot', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Award'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    job_title = fields.Char(string="Job Title")
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True, )
    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )

    # electromechanical
    e_project = fields.Text(string="Project")
    e_subject = fields.Text(string="Subject", default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
        'chamber_erp.e_subject'))
    e_introduction = fields.Text(string="Introduction",
                                 default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                     'chamber_erp.e_introduction'))
    e_scope_of_work = fields.Text(string="Scope of Work",
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                      'chamber_erp.e_scope_of_work'))
    e_hsq = fields.Text(string="Health, Safety and Quality",
                        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                            'chamber_erp.e_hsq'))
    e_camber_scope = fields.Text(string="Camber Scope and Considerations",
                                 default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                     'chamber_erp.e_camber_scope'))
    e_exclusion = fields.Text(string="Exclusion / Limitation",
                              default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                  'chamber_erp.e_exclusion'))
    e_notes_assumption = fields.Text(string="Notes & Assumptions",
                                     default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                         'chamber_erp.e_notes_assumption'))
    e_service_terms = fields.Text(string="Service Terms",
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                      'chamber_erp.e_service_terms'))
    e_order_cancellation = fields.Text(string="Order Cancellation",
                                       default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                           'chamber_erp.e_order_cancellation'))
    e_payment_terms = fields.Text(string="Payment Terms",
                                  default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                                      'chamber_erp.e_payment_terms')
                                  )
    electro_mechanic_lines = fields.One2many('sale.order.electro.lines', 'order_id', string="Electro Lines", copy=True)

    e_notes = fields.Text(string="Notes",
                          default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
                              'chamber_erp.e_notes'))
    e_department = fields.Char(string="Department")
    validity = fields.Char(string="Validity")
    e_end_user = fields.Char(string="End User")
    phn_number = fields.Char(string="Phone")
    email = fields.Char(string="Email")

    # Technical Outsourcing
    t_contract_period = fields.Char(string="Contract Period")
    t_food = fields.Char(string="Food")
    t_normal_working_hours = fields.Char(string="Normal Working Hours")
    t_accommodation = fields.Char(string="Accommodation")
    t_over_time = fields.Char(string="Over Time")
    t_transportation = fields.Char(string="Transportation")
    t_validity = fields.Date(string="Validity")
    technical_outsourcing_line_ids = fields.One2many('sale.order.outsourcing.lines', 'order_id',
                                                     string="Outsourcing Lines",
                                                     copy=True)
    technical_terms_ids = fields.One2many('sale.order.outsourcing.terms.lines', 'order_id',
                                          string="Terms and Condition",
                                          copy=True)
    price_type = fields.Selection([
        ('hour', 'Rate / Hour'),
        ('day', 'Rate / Day')
    ], 'Rate Type', default='hour')
    estimation_type = fields.Selection(
        [('fire_consulting', 'Fire Consulting'),
         ('electro_mechanical', 'Electro Mechanical'),
         ('technical_outsourcing', 'Technical Outsourcing'),
         ('facility_management', 'Facility Management')], string='Type')
    # 
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, readonly=False)
    # 

    @api.depends('opportunity_id', 'contract_id')
    def _compute_so_name(self):
        for rec in self:
            if rec.opportunity_id:
                rec.name = rec.opportunity_id.seq
            if rec.revision_id:
                rec.name = rec.revision_id.name + ' R' + str(rec.revision_id.last_code + 1)
            if not rec.opportunity_id and rec.contract_id:
                rec.name = rec.contract_id.name + ' - SO' + self.env['ir.sequence'].next_by_code('contract.sale.order')

    def _get_all_revisions(self):
        for rec in self:
            # if rec.revision_id:
            res = []
            sale = self.env['sale.order'].search([('opportunity_id', '=', rec.opportunity_id.id)])
            if sale:
                for s in sale:
                    date = datetime.strptime(str(s.date_order), "%Y-%m-%d %H:%M:%S").strftime('%d-%m-%Y')
                    res.append({
                        'name': s.name,
                        'date': date
                    })
                return res


class SaleOrderLineExtend(models.Model):
    _inherit = "sale.order.line"

    remarks = fields.Text(string="Remarks")
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain="[('type', '=', 'service'),('is_quotation_product', '=', True)]",
        change_default=True, ondelete='restrict', check_company=True)
    unit_estd_cost = fields.Float(string='Estimated')
    service_cost = fields.Float(string='Service')


    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLineExtend, self).product_id_change()
        self.name = self.product_id.name or self.product_id.description_sale
        return res

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        return


class ElectroMechanicalLines(models.Model):
    _name = 'sale.order.electro.lines'
    _order = 'sequence, id'

    name = fields.Char(string="Description", required=True)
    product_uom = fields.Many2one('uom.uom', string="Unit")
    qty = fields.Float(string="Qty")
    price_unit = fields.Float(strig="Unit rate")
    order_id = fields.Many2one('sale.order', string="Sale Order")
    total_rate = fields.Float(string="Total Rate", compute='_compute_values', store=True, default=False)
    remarks = fields.Char(string="Remarks")
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('price_unit', 'qty')
    def _compute_values(self):
        for rec in self:
            rec.total_rate = rec.price_unit * rec.qty


class TechnicalOutsourcing(models.Model):
    _name = 'sale.order.outsourcing.lines'
    _order = 'sequence, id'

    name = fields.Char(string="Description", required=True)
    qty = fields.Char(string="Qty")
    price_unit = fields.Float(strig="Unit rate")
    order_id = fields.Many2one('sale.order', string="Sale Order")
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")


class TechnicalOutsourcingTerms(models.Model):
    _name = 'sale.order.outsourcing.terms.lines'
    _order = 'sequence, id'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    name = fields.Char(string="Name", required=True)
    description = fields.Char(string="Description")
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
