from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, Warning
from datetime import datetime
from odoo.addons import decimal_precision as dp

READONLY_STATES = {
    'confirmed': [('readonly', True)]
}


class CRMEstimationLines(models.Model):
    _name = 'crm.estimation.line'
    _description = 'Esimation'
    _order = 'sequence,id asc'

    estimation_id = fields.Many2one('crm.estimation', string='Estimation', copy=True, auto_join=True)
    estimation_id_serv = fields.Many2one('crm.estimation', string='Estimation', copy=True, auto_join=True)
    estimation_type = fields.Selection([
        ('service', 'Service'),
        ('product', 'Products'), ],
        default='product',
        string='Estimation Type',
    )

    name = fields.Char(string='Description', required=True)

    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')

    expected_date = fields.Date(string='Expected Date')

    currency_id = fields.Many2one('res.currency', string='Currency', related='estimation_id.currency_id')

    unit_man_hour_installation = fields.Float(string='Unit Man Hour For Installation')
    total_man_hour_installation = fields.Float(string='Total Man Hour For Installation', compute='_get_amount',
                                                  store=True)
    unit_price_material = fields.Float(string='Unit rate Material Cost Price (AED)')
    total_price_material = fields.Float(string='Total rate Material Cost Price (AED)', compute='_get_amount',
                                           store=True)
    unit_rate_man_hour_tf = fields.Float(string='Unit Rate Manhour *TF(AED)', compute='_get_amount', store=True)
    total_rate_man_hour = fields.Float(string='Total Rate Manhour (AED)', compute='_get_amount', store=True)
    unit_rate_material_supply = fields.Float(string='Unit rate Material Supply (AED)', compute='_get_amount',
                                                store=True)
    total_rate_material_supply = fields.Float(string='Total Rate Material Supply  (AED)', compute='_get_amount',
                                                 store=True)
    unit_rate_installation = fields.Float(string='Unit Rate Installation (AED)', compute='_get_amount', store=True)
    total_rate_installation = fields.Float(string='Total Rate Installation (AED) ', compute='_get_amount',
                                              store=True)
    remarks = fields.Text(string="Remarks")

    sequence = fields.Integer(string='Sequence', default=10)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('unit_man_hour_installation', 'unit_price_material', 'product_qty',
                 'estimation_id.man_hour_multiplication_factor', 'estimation_id.material_multiplication_factor')
    def _get_amount(self):
        for rec in self:
            rec.total_man_hour_installation = rec.product_qty * rec.unit_man_hour_installation
            rec.total_price_material = rec.product_qty * rec.unit_price_material
            rec.unit_rate_man_hour_tf = rec.unit_man_hour_installation * rec.estimation_id.man_hour_multiplication_factor
            rec.total_rate_man_hour = rec.unit_rate_man_hour_tf * rec.product_qty
            rec.unit_rate_material_supply = rec.unit_price_material * rec.estimation_id.material_multiplication_factor
            rec.total_rate_material_supply = rec.unit_rate_material_supply * rec.product_qty
            rec.unit_rate_installation = rec.unit_rate_man_hour_tf + rec.unit_rate_material_supply
            rec.total_rate_installation = rec.total_rate_man_hour + rec.total_rate_material_supply

    @api.onchange('product_id')
    def on_change_product_id(self):
        for record in self:
            record.product_uom = record.product_id.uom_id.id
            record.name = record.product_id.default_code or record.product_id.name
            record.unit_price_material = record.product_id.standard_price


class CRMEstimation(models.Model):
    _name = 'crm.estimation'
    _description = 'Esimations'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Estimation', required=True, default='_Draft', copy=False)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    currency_id = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id',
                                  readonly=True)

    estimation_type = fields.Selection(
        [('fire_consulting', 'Fire Consulting'),
         ('electro_mechanical', 'Electro Mechanical'),
         ('technical_outsourcing', 'Technical Outsourcing'),
         ('facility_management', 'Facility Management')], string='Type',
        required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('send', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('confirmed', 'Lock'),
    ],
        default='draft',
        string='Status',
        copy=False, track_visibility='onchange')

    expected_date = fields.Date(string='Expected Date')
    estimator_id = fields.Many2one('res.users', string='Engineer', required=True, track_visibility='onchange',
                                   states=READONLY_STATES)
    lead_id = fields.Many2one('crm.lead', string='Lead', track_visibility='onchange')
    service_line_ids = fields.One2many('crm.estimation.line', 'estimation_id_serv', string='Service Estimation',
                                       states=READONLY_STATES, copy=True)
    product_line_ids = fields.One2many('crm.estimation.line', 'estimation_id', string='Product Estimation',
                                       states=READONLY_STATES, copy=True)
    edt_id = fields.Many2one('crm.estimation.etd', string='Estimated Delivery', track_visibility='onchange',
                             states=READONLY_STATES)
    description = fields.Text(string='Description', track_visibility='onchange')
    requirement = fields.Text(string='Requirement')
    is_quoted = fields.Boolean(string="Is Quote", default=False, copy=False)

    quotation_count = fields.Integer(string='Quotations')

    service_description = fields.Text(string='Service Description')

    copy_estimation_id = fields.Many2one('crm.estimation', string='Copy Estimation')
    partner_id = fields.Many2one('res.partner', string="Customer")

    expense_line_ids = fields.One2many('estimation.expense.line', 'estimation_id', string="Expense Lines", copy=True)
    calculation_ids = fields.One2many('estimation.calculation', 'estimation_id', string="Calculation", copy=True)
    man_hour_ids = fields.One2many('estimation.man.hours', 'estimation_id', string="Man Hours", copy=True)
    man_hour_id = fields.Many2one('estimation.man.hours',string="Man Hour",copy=False)
    material_ids = fields.One2many('estimation.material', 'estimation_id', string="Materials", copy=True)

    material_id = fields.Many2one('estimation.material',string="Material",copy=False)
    man_power_ids = fields.One2many('estimation.man.powers', 'estimation_id', string="Man Powers", copy=True)
    material_hour_profit_ids = fields.One2many('estimation.material.profit', 'estimation_id',
                                               string="Material Hours Profit", copy=True)
    man_hour_profit_ids = fields.One2many('estimation.man.hour.profit', 'estimation_id', string="Man Hours Profit",
                                          copy=True)

    # totals
    material_total = fields.Float(string="Material Total", compute='_get_all_amounts', store=True)
    other_expense_total = fields.Float(string="Other Expense", compute='_get_all_amounts', store=True)
    man_hours_total = fields.Float(string="Man Hours", compute='_get_all_amounts', store=True)
    material_total_with_profit = fields.Float(string="Material Total with Profit", compute='_get_all_amounts',
                                                 store=True)
    man_hours_other_expense_total = fields.Float(string="Work + Other Expense Total", compute='_get_all_amounts',
                                                    store=True)
    man_hours_other_expense_total_with_profit = fields.Float(string="Work + Other Expense Total with Profit",
                                                                compute='_get_all_amounts', store=True)
    overall_total = fields.Float(string="Overall Total", compute='_get_all_amounts', store=True)
    overall_total_percentage = fields.Float(string="Overall Total (%) ", compute='_get_all_amounts', store=True)

    # Multiplication Factor
    material_multiplication_factor = fields.Float(string="Material Multiplication Factor",
                                                     compute='_get_all_amounts', store=True)
    man_hour_multiplication_factor = fields.Float(string="Man-hour Multiplication Factor",
                                                     compute='_get_all_amounts', store=True)

    # revision
    revision_id = fields.Many2one('crm.estimation.revision', string='Revision Group', copy=False)
    revision_number = fields.Char(string='Revision Number', copy=False)
    revision_count = fields.Integer(string='Revisions', compute='_compute_revision_count')
    is_completed = fields.Boolean(string="Completed", default=True)

    # VG Code : 
    @api.model
    def default_get(self, fields):
        result = super(CRMEstimation, self).default_get(fields)
        if 'daily_worker_line_ids' in fields:
            shipments = self.env['farm.shipment'].sudo().search([('state', '=', 'open')])
            daily_worker_line_list = []
            if shipments:
                for shipment in shipments:
                    daily_worker_line = self.env['daily.worker.line'].create({
                        'shipment_id': shipment.id,
                    })
                    daily_worker_line_list.append(daily_worker_line.id)
                if daily_worker_line_list:
                    result.update({
                        'daily_worker_line_ids': [(6, 0, daily_worker_line_list)]
                    })
        return result

    def compute_line_data(self):
        for rec in self.product_line_ids:
            rec._get_amount()

    def _compute_revision_count(self):
        for record in self:
            record.revision_count = len(self.env['crm.estimation'].search([('revision_id', '=', self.revision_id.id)]))

    def create_new_version(self):
        revision_id = self.revision_id
        if not revision_id:
            vals = {
                'name': self.name,
                'last_code': 0
            }
            revision_id = self.env['crm.estimation.revision'].create(vals)
            self.write({
                'revision_id': revision_id.id
            })

        action = self.env.ref('chamber_erp.action_make_revision_wizard_estimation').read()[0]
        action['context'] = dict(
            self.env.context,
            default_estimation_id=self.id,
            default_revision_id=revision_id.id,
            default_next_code=revision_id.last_code + 1
        )
        return action

    def action_view_revisions(self):
        #     sale_orders = self.env['sale.order'].search([('revision_id', '=', self.revision_id.id)])
        #
        #     result = self.env['ir.actions.act_window']._for_xml_id('stranbys_saleorder_revision.action_view_revised_quote')
        #     result['domain'] = [('id', 'in', sale_orders.ids)]
        return True

    @api.depends('product_line_ids', 'calculation_ids', 'man_hour_profit_ids', 'material_hour_profit_ids',
                 'man_hour_ids', 'material_ids', 'man_hour_ids.total')
    def _get_all_amounts(self):
        for rec in self:
            rec.material_total = sum(
                rec.product_line_ids.mapped(
                    'total_price_material'))
            rec.other_expense_total = sum(rec.calculation_ids.mapped('total')) + sum(
                rec.expense_line_ids.mapped('total'))
            rec.man_hours_total = sum(rec.man_hour_ids.mapped(
                'total'))
            rec.man_hours_other_expense_total = rec.other_expense_total + \
                                                sum(rec.man_hour_ids.mapped(
                                                    'total'))
            rec.material_total_with_profit = sum(rec.material_hour_profit_ids.mapped('total')) + sum(
                rec.product_line_ids.mapped('total_price_material'))
            rec.man_hours_other_expense_total_with_profit = rec.man_hours_other_expense_total + \
                                                            sum(rec.man_hour_profit_ids.mapped('total'))
            rec.overall_total = rec.material_total_with_profit + rec.man_hours_other_expense_total_with_profit
            # rec.material_multiplication_factor = rec.material_total_with_profit / rec.material_total

            try:
                rec.overall_total_percentage = (((rec.material_total_with_profit - rec.material_total) +
                                                 (
                                                         rec.man_hours_other_expense_total_with_profit - rec.man_hours_other_expense_total)) / (
                                                    rec.overall_total)) * 100
            except ZeroDivisionError:
                rec.overall_total_percentage = 0

            try:
                rec.man_hour_multiplication_factor = rec.man_hours_other_expense_total_with_profit / sum(
                    rec.man_hour_ids.mapped('man_hours'))
            except ZeroDivisionError:
                rec.man_hour_multiplication_factor = 0

            try:
                rec.material_multiplication_factor = rec.material_total_with_profit / rec.material_total
            except ZeroDivisionError:
                rec.material_multiplication_factor = 0

    def copy_estimation(self):

        def change_line(ids):
            for record in ids:
                new_record = record.copy()
                # if record.estimation_type == 'service':
                #     new_record.write({
                #         'estimation_id_serv': self.id,
                #     })
                # if record.estimation_type == 'product':
                new_record.write({
                    'estimation_id': self.id
                })

        self.product_line_ids.unlink()
        self.service_line_ids.unlink()

        ids = self.copy_estimation_id.product_line_ids
        change_line(ids)
        ids = self.copy_estimation_id.service_line_ids
        change_line(ids)

    # def _compute_count(self):
    #     for record in self:
    #         record.quotation_count = len(self.env['sale.order'].search([('estimation_id', '=', record.id)]))

    def unlink(self):
        if self.name != '_Draft':
            raise UserError('Cannot delete Estimation')
        return super(CRMEstimation, self).unlink()

    def send_approval(self):
        # estimation = self.env['crm.estimation'].search([('lead_id', '=', self.lead_id.id)])
        if not self.revision_id:
            self.write({
                'name': self.lead_id.seq,
                'state': 'send'
            })
        else:
            self.write({
                'state': 'send'
            })

    def approval_estimation(self):
        self.write({
            'state': 'approved'
        })

    def lock_estimation(self):
        self.write({
            'state': 'confirmed'
        })

    def update_datas(self):
        # self.man_hour_id = self.man_hour_ids[0]
        rate =  self.man_hour_ids[0].rate if self.man_hour_ids else 1
        self.material_ids.unlink()
        self.man_hour_ids.unlink()
        total_material_cost = sum(
            self.product_line_ids.mapped(
                'total_price_material'))
        total_man_hour_installation = sum(
            self.product_line_ids.mapped(
                'total_man_hour_installation'))

        self.material_ids = [(0, 0, {
            'name': 'Materials',
            'total': total_material_cost
        })]
        self.man_hour_ids = [(0, 0, {
            'name': 'Installation Services ',
            'man_hours': total_man_hour_installation,
            'rate': rate
        })]
        self.product_line_ids._get_amount()



    def create_quotation(self):
        action = self.env.ref('chamber_erp.act_estimation_quotation_wizard').read()[0]
        action['context'] = dict(
            self.env.context,
            default_lead_id=self.lead_id.id,
            default_estimation_id=self.id
        )
        return action

    def write(self, vals):
        res = super(CRMEstimation, self).write(vals)
        if vals.get('product_line_ids'):
            self.compute_line_data()
        # else:
        #     print(asjdgfagvsmd)
        return res

    # def create(self, vals_list):
    #     res = super(CRMEstimation, self).create(vals_list)
    #     if vals_list:
    #         res.compute_line_data()
    #     return res

    # if self.service_cost > 0 and not self.service_description:
    #     raise UserError(
    #         _('Service Description is empty, please fill out service description in service details page.'))
    # vals = {
    #     'partner_id': self.lead_id.partner_id.id,
    #     'partner_invoice_id': self.lead_id.partner_id.id,
    #     'partner_shipping_id': self.lead_id.partner_id.id,
    #     'estimation_id': self.id,
    #     'opportunity_id': self.lead_id.id,
    #     'estimation_type': self.estimation_type
    # }
    # order_id = self.env['sale.order'].create(vals)
    #
    # for line in self.product_line_ids:
    #     vals2 = {
    #         'order_id': order_id.id,
    #         'product_id': line.product_id.id,
    #         'sequence': line.sequence,
    #         'product_uom_qty': line.product_qty,
    #         'price_unit': line.unit_rate_installation,
    #         'display_type': line.display_type,
    #         'name': line.name,
    #         'product_uom': line.product_uom.id,
    #         'tax_id': False,
    #         'remarks': line.remarks
    #     }
    #     self.env['sale.order.line'].create(vals2)
    # self.is_quoted = True

    def create_rejection(self):
        action = self.env.ref('sales_estimation.action_reject_estimation').read()[0]
        action['context'] = dict(
            self.env.context,
            default_estimation_id=self.id,
        )
        return action

    def action_project_estimations(self):
        action = {
            'name': _("Project Estimation"),
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.estimation.line',
            'domain': [('estimation_id', '=', self.id)],
            'context': {
                'estimation_id': self.id,
            }
        }
        return action
    def button_report_xlsx(self):
        return self.env.ref('chamber_erp.report_estimation_print').report_action(self)


class ExpenseLines(models.Model):
    _name = 'estimation.expense.line'
    _description = 'Estimated Expense'
    _order = 'id desc'

    expense_type_id = fields.Many2one('estimation.expense.type', string="Expense")
    name = fields.Char(string="Item")
    month = fields.Float(string="Month")
    qty = fields.Float(string="Qty")
    salary = fields.Float(string="Salary")
    total = fields.Float(string="Total", compute='_get_total_amount', store=True)
    estimation_id = fields.Many2one('crm.estimation', string='Estimation')
    sequence = fields.Integer(string='Sequence', default=10)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('expense_type_id')
    def _onchange_expense_type_id(self):
        if self.expense_type_id:
            self.name = self.expense_type_id.department

    @api.depends('month', 'qty', 'salary')
    def _get_total_amount(self):
        for rec in self:
            rec.total = rec.month * rec.qty * rec.salary


class EstimatedDelivery(models.Model):
    _name = 'crm.estimation.etd'
    _description = 'Estimated Delivery'
    _order = 'id desc'

    name = fields.Char(string="Name")
    days = fields.Integer(string="Days")


class EstimationSaleOrder(models.Model):
    _inherit = 'sale.order'
    _name = 'sale.order'

    estimation_id = fields.Many2one('crm.estimation', string='Estimation')


class EstimationRevision(models.Model):
    _name = 'crm.estimation.revision'

    name = fields.Char(string='Name', required=True)
    last_code = fields.Integer(string='Last Code')
