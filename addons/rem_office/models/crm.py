# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.rem.models.crm import MATCH_RE

MATCH_RE.update({
    # General Features
    'self.re_min_people': {'min_people': 'self.re_min_people'},
    'self.re_max_people': {'max_people': 'self.re_max_people'},
    'self.re_min_area > 0': {'min_area': 'self.re_min_area'},
    'self.re_min_windows > 0': {'min_windows': 'self.re_min_windows'},
})


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    re_min_people = fields.Integer(
        'Min People', help="Min number of People")
    re_max_people = fields.Integer(
        'Max People', help="Max number of People")
    re_min_area = fields.Float(
        'Min Area', help="Min Number of Area")
    re_min_windows = fields.Float(
        'Min Windows', help="Min Number of Windows")
