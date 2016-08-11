# -*- coding: utf-8 -*-
import json
from openerp import tools, api, fields, models, _


class RemUnit(models.Model):
    _inherit = 'rem.unit'
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    def _website_url(self, cr, uid, ids, field_name, arg, context=None):
        res = super(RemUnit, self)._website_url(cr, uid, ids, field_name, arg, context=context)
        for unit in self.browse(cr, uid, ids, context=context):
            res[unit.id] = "/rem/unit/%s" % (unit.id,)
        return res