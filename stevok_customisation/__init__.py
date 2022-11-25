from . import models,wizards

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('stevok_customisation.quotation_notes',
                                                'Please Update in system parameters (stevok_customisation.quotation_notes)')
    env['ir.config_parameter'].sudo().set_param('stevok_customisation.contract_location',
                                                'Please Update in system parameters (stevok_customisation.qtn_location)')
    env['ir.config_parameter'].sudo().set_param('stevok_customisation.agreed_upon',
                                                'Please Update in system parameters (stevok_customisation.agreed_upon)')

    env['ir.config_parameter'].sudo().set_param('stevok_customisation.maintenance_charge',
                                                'Please Update in system parameters (stevok_customisation.maintenance_charge)')
    env['ir.config_parameter'].sudo().set_param('stevok_customisation.notes',
                                                'Please Update in system parameters (stevok_customisation.notes)')
    env['ir.config_parameter'].sudo().set_param('stevok_erp.bank_details',
                                                'Please Update in system parameters (stevok_erp.bank_details)')
