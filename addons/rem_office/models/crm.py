# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.addons.rem.models.crm import MATCH_RE

MATCH_RE.update({
    # General Features
    'self.re_min_people': {'min_people': 'self.re_min_people'},
    'self.re_max_people': {'max_people': 'self.re_max_people'},
    'self.re_min_area > 0': {'min_area': 'self.re_min_area'},
    'self.re_min_seats': {'min_seats': 'self.re_min_seats'},
    'self.re_max_seats': {'max_seats': 'self.re_max_seats'},
    'self.re_min_windows > 0': {'min_windows': 'self.re_min_windows'},
    'self.re_min_desk_phones > 0': {'min_desk_phones': 'self.re_min_desk_phones'},
})


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    re_min_people = fields.Integer(
        'Min People', help="Min number of People")
    re_max_people = fields.Integer(
        'Max People', help="Max number of People")
    re_min_area = fields.Float(
        'Min Area', help="Min Number of Area")
    re_min_seats = fields.Integer(
        'Min Seats', help="Min number of Seats")
    re_max_seats = fields.Integer(
        'Max Seats', help="Max number of Seats")
    re_min_windows = fields.Float(
        'Min Windows', help="Min Number of Windows")
    re_min_desk_phones = fields.Float(
        'Min Desk Phones', help="Min Number of Desk Phones")
