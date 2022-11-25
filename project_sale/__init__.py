# -*- coding: utf-8 -*-
from . import models, wizard

from odoo.api import Environment, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('project.analytic.group_id', '1')
    env['ir.config_parameter'].sudo().set_param('inventory.return.operation_id', '1')