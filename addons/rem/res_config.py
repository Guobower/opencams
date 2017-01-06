# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning


class RemConfigSettings(models.TransientModel):
    _name = 'rem.config.settings'
    _inherit = 'res.config.settings'

    module_website_rem = fields.Boolean('Install Real Estate Website', help="By checking this option you "
                                        "will be installing the Real Estate Website on the front-end of your system.")
    group_use_buyer_contracts = fields.Boolean('Use Buyer Representations Agreements', implied_group='rem.group_use_buyer_contracts',
                                               help="By checking this option you will make visible buyer representation"
                                               " agreements / contracts in the system ")

    @api.multi
    def button_immediate_upgrade(self):
    	module = self.env['ir.module.module'].search([('name', '=', 'rem')], limit=1)
    	if module:
    		module.button_immediate_upgrade()
    		self.env.cr.commit()
    		raise Warning("Update complete.")
