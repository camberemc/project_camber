from . import models , wizard, report

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_subject',
                                                'Please Update in system parameters (chamber_erp.e_subject)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_introduction',
                                                'Please Update in system parameters (chamber_erp.e_introduction)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_scope_of_work',
                                                'Please Update in system parameters (chamber_erp.e_scope_of_work)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_hsq',
                                                'Please Update in system parameters (chamber_erp.e_hsq)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_camber_scope',
                                                'Please Update in system parameters (chamber_erp.e_camber_scope)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_exclusion',
                                                'Please Update in system parameters (chamber_erp.e_exclusion)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_notes_assumption',
                                                'Please Update in system parameters (chamber_erp.e_notes_assumption)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_service_terms',
                                                'Please Update in system parameters (chamber_erp.e_service_terms)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_order_cancellation',
                                                'Please Update in system parameters (chamber_erp.e_order_cancellation)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_payment_terms',
                                                'Please Update in system parameters (chamber_erp.e_payment_terms)')
    env['ir.config_parameter'].sudo().set_param('chamber_erp.e_notes',
                                                'Please Update in system parameters (chamber_erp.e_notes)')
