from . import models , wizards

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('stranbys_amc.invoice_product',
                                                'Please Update in system parameters (stranbys_amc.invoice_product)')
    env['ir.config_parameter'].sudo().set_param('stranbys_amc.invoice_account',
                                                'Please Update in system parameters (stranbys_amc.invoice_account)')
    # env['ir.config_parameter'].sudo().set_param('stevok_erp.safety_hse_quality',
    #                                             'Please Update in system parameters (stevok_erp.safety_hse_quality)')
    # env['ir.config_parameter'].sudo().set_param('stevok_erp.notes',
    #                                             'Please Update in system parameters (stevok_erp.notes)')
