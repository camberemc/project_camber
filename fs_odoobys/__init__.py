from . import models

from odoo.api import SUPERUSER_ID, Environment


def _post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    env['ir.config_parameter'].sudo().set_param('fs_odoobys.reference_drawing',
                                                'Please Update in system parameters (fs_odoobys.reference_drawing)')
    env['ir.config_parameter'].sudo().set_param('fs_odoobys.scope_of_work',
                                                'Please Update in system parameters (fs_odoobys.scope_of_work)')
    env['ir.config_parameter'].sudo().set_param('fs_odoobys.safety_hse_quality',
                                                'Please Update in system parameters (fs_odoobys.safety_hse_quality)')
    env['ir.config_parameter'].sudo().set_param('fs_odoobys.notes',
                                                'Please Update in system parameters (fs_odoobys.notes)')
