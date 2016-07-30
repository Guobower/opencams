# -*- coding: utf-8 -*-
import logging

from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class RemConfigSettings(models.TransientModel):
    _name = 'rem.config.settings'
    _inherit = 'res.config.settings'

    module_website_rem = fields.Boolean('Install Real Estate Website', help="By checking this option you "
                                        "will be installing the Real Estate Website on the front-end of your system.")
