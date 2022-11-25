# -*- coding: utf-8 -*-

from . import models

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})

    env['ir.config_parameter'].sudo().set_param('stevok_erp.bank_details',
                                                'Please Update in system parameters (stevok_erp.bank_details)')