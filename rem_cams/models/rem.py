# -*- coding: utf-8 -*-

from odoo import tools, api, fields, models, _
from odoo.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
import odoo.addons.decimal_precision as dp


class RemUnit(models.Model):
    _inherit = 'rem.unit'

    @api.model
    def _get_stage(self):
        return self.env['rem.unit.stage'].search([], limit=1, order='sequence')

    monthly_fees = fields.Monetary('Monthly Fees Amount')
    special_assessment = fields.Monetary('Special Assessment')
    stage_id = fields.Many2one( default=_get_stage)
    partner_id = fields.Many2one(domain=[('is_home_owner', '=', True)])
