# -*- coding: utf-8 -*-
import logging

from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class RemConfigSettings(models.TransientModel):
    _name = 'rem.config.settings'
    _inherit = 'res.config.settings'

    module_website_rem = fields.Boolean('Install Real Estate Website', help="By checking this option you "
                                        "will be installing the Real Estate Website on the front-end of your system.")
    group_use_buyer_contracts = fields.Boolean('Use Buyer Representations Agreements', implied_group='rem.group_use_buyer_contracts',
                                               help="By checking this option you will make visible buyer representation"
                                               " agreements / contracts in the system ")
    unit_name_format = fields.Char(string='Unit Name Format', required=True)
    unit_websitename_format = fields.Char(string='Unit Website Name Format', required=True)

    @api.model
    def get_default_unit_name_format(self, fields):
        unit_name_format = False
        if 'unit_name_format' in fields:
            unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_name_format')
        return {
            'unit_name_format': unit_name_format
        }

    @api.model
    def get_default_unit_websitename_format(self, fields):
        unit_websitename_format = False
        if 'unit_websitename_format' in fields:
            unit_websitename_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_websitename_format')
        return {
            'unit_websitename_format': unit_websitename_format
        }

    @api.multi
    def set_unit_name_format(self):
        for rec in self:
            self.env['ir.config_parameter'].sudo().set_param('rem.unit_name_format', rec.unit_name_format)
    