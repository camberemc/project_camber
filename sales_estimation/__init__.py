# -*- coding: utf-8 -*-
from . import models, wizard

from odoo.api import Environment, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('estimation.deafult.duty_percent', '0.00')
    env['ir.config_parameter'].sudo().set_param('estimation.deafult.freight_percent', '0.00')
    env['ir.config_parameter'].sudo().set_param('estimation.deafult.profit_percent', '0.00')
    env['ir.config_parameter'].sudo().set_param('estimation.deafult.service_product', '1')