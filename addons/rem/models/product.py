# -*- coding: utf-8 -*-
from openerp import api, fields, models


class ProductUoMCategory(models.Model):
    _inherit = 'product.uom.categ'

    @api.model
    def delete_all_uom_categories(self):
        uom_categories = self.env['product.uom.categ'].search([])
        
        for uom_category in uom_categories:
            uom_categories.unlink()
