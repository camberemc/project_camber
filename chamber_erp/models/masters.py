from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class EstimationCalculation(models.Model):
	_name = 'estimation.calculation'
	_description = 'Estimation Calculation'
	_order = 'sequence,id asc'
	_rec_name = 'item_type'

	sequence = fields.Integer(string='Sequence', default=10)
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")

	display_type = fields.Selection([
		('line_section', "Section"),
		('line_note', "Note")], default=False, help="Technical field for UX purpose.")

	item_type = fields.Selection([('admin_cost', 'Admin Cost'),
								  ('bank_charges', 'Bank Charges'),
								  ('fd_accommodation', 'FOOD & ACCOMMODATION '),
								  ('transportation', 'TRANSPORTATION'),
								  ('temporary_site', 'TEMPORARY SITE FACILITIES'),
								  ('tools_ppe', 'TOOLS & PPE'),
								  ('special_tools_equipment', 'SPECIAL TOOLS & HEAVY EQUIPMENTS'),
								  ('other_expenses', 'OTHER EXPENSES'),
								  # ('material_transport_to_site', 'Material Transport to site'),
								  # ('scaffolding', 'Scaffolding'),
								  # ('civil_power_tools', 'Civil Power Tools'),
								  # ('additional_mob_demob', 'Additional Mob/Demob'),
								  # ('consumables', 'Consumables')
								  ], string="Type")
	total = fields.Float(string="Total", compute='_compute_total', store=True)
	calculation_line_ids = fields.One2many('estimation.calculation.line', 'calculation_id', string="Calculation Lines",
										   copy=True)

	# VG Code : Get Expense Details By Selection Type
	@api.onchange('item_type')
	def onchange_item_type(self):
		if self.item_type == 'admin_cost':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Visa',
				'product_qty': 0,
				'unit_price_material': 7500,
			}),(0,0,{
				'name': 'CNIA',
				'product_qty': 0,
				'unit_price_material': 110,
			}),(0,0,{
				'name': 'contigency',
				'product_qty': 1,
				'unit_price_material': 5000,
			}),(0,0,{
				'name': 'Medical + Redzone+BA Training',
				'product_qty': 0,
				'unit_price_material': 250,
			}),(0,0,{
				'name': 'H2S',
				'product_qty': 0,
				'unit_price_material': 60,
			}),(0,0,{
				'name': 'Covid Test',
				'product_qty': 0,
				'unit_price_material': 30,
			})]
		elif self.item_type == 'bank_charges':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Bid Bond',
			}),(0,0,{
				'name': 'Performance Bond',
			}),(0,0,{
				'name': 'Retention Bond',
			}),(0,0,{
				'name': 'LC Charges',
			}),(0,0,{
				'name': 'Others',
			})]
		elif self.item_type == 'fd_accommodation':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Senior (CAMBER)',
				'product_qty': 1,
				'duration_days': 1,
				'unit_price_material': 75,
			}),(0,0,{
				'name': 'Junior (CAMBER)',
				'product_qty': 1,
				'duration_days': 1,
				'unit_price_material': 50,
			}),(0,0,{
				'name': 'Driver',
				'product_qty': 1,
				'duration_days': 1,
				'unit_price_material': 50,
			}),(0,0,{
				'name': 'Sub Contract',
				'product_qty': 1,
				'duration_days': 0,
				'unit_price_material': 50,
			})]
		elif self.item_type == 'transportation':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Maxus',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 4500,
			}),(0,0,{
				'name': 'Fuel - Maxus',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 2600,
			}),(0,0,{
				'name': 'Driver',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 3000,
			}),(0,0,{
				'name': 'Pick Up',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 3000,
			}),(0,0,{
				'name': 'Fuel - Pick Up',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 2600,
			}),(0,0,{
				'name': 'crane',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 3000,
			})]
		elif self.item_type == 'temporary_site':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Office Caravan',
				'product_qty': 1,
				'duration_month': 2,
				'unit_price_material': 6000,
			}),(0,0,{
				'name': 'Pantry',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Storage',
				'product_qty': 1,
				'duration_month': 2.5,
				'unit_price_material': 5000,
			}),(0,0,{
				'name': 'Toilet',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Generator',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Fuel',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Mob/Demo',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Others',
				'product_qty': 1,
				'duration_month': 2.5,
				'unit_price_material': 2000,
			})]
		elif self.item_type == 'tools_ppe':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Tool Box',
				'product_qty': 1,
				'duration_month': 2,
				'unit_price_material': 2000,
			}),(0,0,{
				'name': 'Coverall',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 70,
			}),(0,0,{
				'name': 'Safety shoes',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 38,
			}),(0,0,{
				'name': 'Helmet',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 25,
			}),(0,0,{
				'name': 'Goggles',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 5,
			}),(0,0,{
				'name': 'H2S Detector',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 175,
			}),(0,0,{
				'name': 'Escape Mask',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 200,
			}),(0,0,{
				'name': 'BA',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			})]
		elif self.item_type == 'special_tools_equipment':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]
			self.calculation_line_ids = [(0,0,{
				'name': 'Splicing Machine',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'HART',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 350,
			}),(0,0,{
				'name': 'Megger',
				'product_qty': 1,
				'duration_month': 0,
				'unit_price_material': 150,
			}),(0,0,{
				'name': 'Hiab',
				'product_qty': 1,
				'duration_month': 4,
				'unit_price_material': 1800,
			}),(0,0,{
				'name': '15 mtr Manlift',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 7200,
			}),(0,0,{
				'name': '8 mtr Scissor Liftg ',
				'product_qty': 1,
				'duration_month': 1,
				'unit_price_material': 3400,
			}),(0,0,{
				'name': 'Crane',
				'product_qty': 1,
				'duration_month': 4,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Scaffolding',
				'product_qty': 1,
				'duration_month': 4,
				'unit_price_material': 0,
			}),(0,0,{
				'name': 'Crane',
				'product_qty': 1,
				'duration_month': 4,
				'unit_price_material': 0,
			})]
		elif self.item_type == 'other_expenses':
			for cal_line in self.calculation_line_ids:
				self.calculation_line_ids = [(2,cal_line.id)]


	@api.depends('calculation_line_ids', 'calculation_line_ids.total')
	def _compute_total(self):
		for rec in self:
			rec.total = sum(rec.calculation_line_ids.mapped('total'))


class EstimationCalculationLine(models.Model):
	_name = 'estimation.calculation.line'
	_description = 'Estimation Calculation Line'
	_order = 'id asc'

	name = fields.Char(string="Item")
	product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), default=1.0)
	unit_price_material = fields.Float(string='Unit Rate')
	bond_value = fields.Float(string='Bond Value')
	validity_monthly = fields.Float(string='Validity(MTH)')
	# validity_days = fields.Float(string='Validity(DAYS)')
	duration_days = fields.Float(string='Duration(DAYS)')
	duration_month = fields.Float(string='Duration(MTH)')
	bank_charges = fields.Float(string='Bank Charges', compute='_get_total_amount', store=True)
	total = fields.Float(string='Total', compute='_get_total_amount', store=True)
	calculation_id = fields.Many2one('estimation.calculation', string="Calculation")

	@api.depends('product_qty', 'unit_price_material', 'duration_days', 'duration_month', 'bond_value',
				 'validity_monthly', 'calculation_id.item_type', 'bank_charges')
	def _get_total_amount(self):
		for rec in self:
			rec.bank_charges = 0
			rec.total = 0
			if rec.calculation_id.item_type in (
					'admin_cost', 'material_transport_to_site', 'scaffolding', 'civil_power_tools',
					'additional_mob_demob',
					'consumables'):
				rec.total = rec.product_qty * rec.unit_price_material
			if rec.calculation_id.item_type == 'fd_accommodation':
				rec.total = rec.product_qty * rec.unit_price_material * rec.duration_days
			if rec.calculation_id.item_type in (
					'transportation', 'temporary_site', 'special_tools_equipment'):
				rec.total = rec.product_qty * rec.unit_price_material * rec.duration_month
			if rec.calculation_id.item_type == 'tools_ppe':
				rec.total = rec.product_qty * rec.unit_price_material * (rec.duration_month / 12)
			if rec.calculation_id.item_type == 'bank_charges' and rec.bond_value and rec.validity_monthly:
				rec.bank_charges = rec.bond_value * rec.validity_monthly * 0.00125
				rec.total = rec.bank_charges
			if rec.calculation_id.item_type == 'other_expenses':
				rec.total = rec.product_qty * rec.unit_price_material * rec.duration_month


class ExpenseType(models.Model):
	_name = 'estimation.expense.type'
	_rec_name = 'name'

	name = fields.Char(string="Name", required=True)
	department = fields.Char(string="Department")


class EstimationManHours(models.Model):
	_name = 'estimation.man.hours'
	_rec_name = 'name'

	name = fields.Char(string="Name")
	man_hours = fields.Float(string="Man Hours")
	rate = fields.Float(string="Rate")
	total = fields.Float(string="Total", compute='_get_total_amount', store=True)
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")

	@api.depends('man_hours', 'rate')
	def _get_total_amount(self):
		for rec in self:
			rec.total = rec.man_hours * rec.rate


class EstimationMaterial(models.Model):
	_name = 'estimation.material'
	_rec_name = 'name'

	name = fields.Char(string="Name")
	total = fields.Float(string="Total")
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")


class EstimationManPowers(models.Model):
	_name = 'estimation.man.powers'
	_rec_name = 'name'

	name = fields.Char(string="Name")
	man_hours = fields.Float(string="Man Hours")
	hours_per_day = fields.Float(string="Hrs/Day")
	days_per_month = fields.Float(string="Days/Month")
	month = fields.Float(string="Month")
	man_power = fields.Float(string="Man Power")
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")


class EstimationMaterialProfit(models.Model):
	_name = 'estimation.material.profit'
	_rec_name = 'name'

	name = fields.Char(string="Name")
	percentage = fields.Float(string="Percentage")
	total = fields.Float(string="Total", compute='_get_total_amount', store=True)
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")

	@api.depends('percentage', 'estimation_id.product_line_ids')
	def _get_total_amount(self):
		for rec in self:
			total_material_cost = sum(
				rec.estimation_id.product_line_ids.mapped(
					'total_price_material'))
			try:
				rec.total = (total_material_cost * rec.percentage) / 100
			except ZeroDivisionError:
				rec.total = 0


class EstimationManHoursProfit(models.Model):
	_name = 'estimation.man.hour.profit'
	_rec_name = 'name'

	name = fields.Char(string="Name")
	percentage = fields.Float(string="Percentage")
	total = fields.Float(string="Total", compute='_get_total_amount', store=True)
	estimation_id = fields.Many2one('crm.estimation', string="Estimation")

	@api.depends('percentage', 'estimation_id')
	def _get_total_amount(self):
		for rec in self:
			total_expense_ids = rec.estimation_id.man_hours_other_expense_total

			try:
				rec.total = (total_expense_ids * rec.percentage) / 100
			except ZeroDivisionError:
				rec.total = 0
