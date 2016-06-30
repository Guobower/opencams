# -*- coding: utf-8 -*-
from openerp import api, models


class Website(models.Model):
    _inherit = "website.menu"

    @api.model
    def update_menu(self):
        self.env.ref('website.menu_contactus').write({'url':'/contact-us'})
