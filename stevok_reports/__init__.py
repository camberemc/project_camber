from . import models

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})

    env['ir.config_parameter'].sudo().set_param('bank_details',
                                                'Please Update in system parameters (bank_details)')
