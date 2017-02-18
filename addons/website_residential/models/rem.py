# -*- coding: utf-8 -*-
import json
from odoo import tools, api, fields, models, _


class RemUnit(models.Model):
    _inherit = ['rem.unit']

    is_featured = fields.Boolean(string='Is Featured', default=False)
    feature_id = fields.Many2many(
        'res.users', 'rem_unit_res_users_rel', 'rem_unit_id', 'res_user_id')
    website_name = fields.Char(compute='_get_website_name', string='Reference', readonly=True)

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip')
    def _get_website_name(self):
        units = []
        for rec in self:
            name = self.get_formated_name(rec, rec.offer_type_id.unit_websitename_format)
            units.append((rec.id, name))
        return units

    @api.multi
    def _compute_website_url(self):
        super(RemUnit, self)._compute_website_url()
        for unit in self:
            unit.website_url = "/rem/unit/%s" % (unit.id,)

    @api.one
    def add_feature(self):
        max_feature_units = self.pool.get('ir.config_parameter').get_param(self.env.cr, self.env.uid,
                                                                           'max_feature_units')

        self.env.cr.execute(
            'SELECT COUNT(rem_unit_id) AS total FROM rem_unit_res_users_rel WHERE res_user_id=%s LIMIT 1',
            [self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if int(max_feature_units) == 0 or int(feature_units['total']) < int(max_feature_units):
                self.feature_id = [(4, self.env.uid)]
                self.is_featured = True
            else:
                raise exceptions.ValidationError(
                    'You can only have %s Feature Units.' % max_feature_units)
        return True

    @api.one
    def remove_feature(self):
        self.feature_id = [(3, self.env.uid)]
        return True
