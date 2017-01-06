# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime


MATCH_RE = {
    'self.planned_revenue': {'max_planned_revenue': 'self.planned_revenue * 0.1 + self.planned_revenue'},
    # General Features
    'self.re_offer_type_id': {'search_default_offer_type_id': 'self.re_offer_type_id.id'},
    'self.re_city': {'search_default_city_id': 'self.re_city.id'},
    'self.re_type': {'search_default_type_id': 'self.re_type.ids[0]'},
    'self.re_min_bedrooms': {'min_bedrooms': 'self.re_min_bedrooms'},
    'self.re_max_bedrooms': {'max_bedrooms': 'self.re_max_bedrooms'},
    'self.re_bathrooms > 0': {'min_bathrooms': 'self.re_bathrooms'},
    'self.re_is_new': {'search_default_is_new': 'self.re_is_new'},
    'self.re_points_interest': {'search_default_points_interest': 'self.re_points_interest.ids'},
    # Indoor Features
    'self.re_air_conditioned': {'search_default_air_condicioned': 'self.re_air_conditioned'},
    'self.re_ducted_cooling': {'search_default_ducted_cooling': 'self.re_ducted_cooling'},
    'self.re_wardrobes': {'search_default_wardrobes': 'self.re_wardrobes'},
    'self.re_dishwasher': {'search_default_dishwasher': 'self.re_dishwasher'},
    'self.re_living_area > 0': {'min_living_area': 'self.re_living_area'},
    # Outdoor Features
    'self.re_backyard': {'search_default_backyard': 'self.re_backyard'},
    'self.re_alarm': {'search_default_alarm': 'self.re_alarm'},
    'self.re_entertaining': {'search_default_entertaining': 'self.re_entertaining'},
    'self.re_pool': {'search_default_sw_pool': 'self.re_pool'},
    'self.re_garage_spaces > 0': {'min_garages': 'self.re_garage_spaces'},
    'self.re_secure_parking': {'search_default_secure_parking': 'self.re_secure_parking'},
    'self.re_dog_friendly': {'search_default_air_dog_friendly': 'self.re_dog_friendly'},
}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planned_revenue = fields.Float('Client Budget', track_visibility='always')

    # General Features
    re_offer_type_id = fields.Many2one(
        'offer.type', string='Offer Type')
    re_type = fields.Many2many('rem.unit.type', string='Property Type')
    re_min_bedrooms = fields.Integer(
        'Min Bedrooms', help="Min number of bedrooms")
    re_max_bedrooms = fields.Integer(
        'Max Bedrooms', help="Max number of bedrooms")
    re_bedrooms = fields.Integer(string='Bedrooms', help="Bedrooms")
    re_bathrooms = fields.Integer(
        'Min Bathrooms', help="Min Number of bathrooms", re_field='bathrooms')
    re_street = fields.Char('Street')
    re_city = fields.Many2one(
        'rem.unit.city', string='City', help='place in order of gratest zone e.g. US, CA, Los Angeles, Beverly Hills')
    re_points_interest = fields.Many2many(
        'location.preferences', string='Points of Interest')
    re_is_new = fields.Boolean(string='Is New', help='Active if you want to search for units new.')

    # Indoor Features
    re_air_conditioned = fields.Boolean(
        string='Air Conditioned', help='Active if you want to search for units with air conditioned.')
    re_ducted_cooling = fields.Boolean(
        string='Ducted Cooling', help='Active if you want to search for units with ducted cooling.')
    re_wardrobes = fields.Boolean(
        string='Built-in Wardrobes', help='Active if you want to search for units with built-in wardrobes.')
    re_dishwasher = fields.Boolean(
        string='Dishwasher', help='Active if you want to search for units with dishwasher.')
    re_living_area = fields.Integer(
        'Min living Areas', help='Min number of living areas')

    # Outdoor Features
    re_backyard = fields.Boolean(
        string='Backyard', help='Active if you want to search for units with backyard.')
    re_dog_friendly = fields.Boolean(
        string='Dog Friendly', help='Active if you want to search for units with dog friendly.')
    re_garage_spaces = fields.Integer(
        'Min Garage Spaces', help='Number of garage spaces')
    re_secure_parking = fields.Boolean(
        string='Secure Parking', help='Active if you want to search for units with secure parking.')
    re_alarm = fields.Boolean(
        string='Alarm System', help='Active if you want to search for units with alarm system.')
    re_pool = fields.Boolean(
        string='Swimming Pool', help='Active if you want to search for units with swimming pool.')
    re_entertaining = fields.Boolean(
        string='Outdoor Entertaining Area', help='Active if you want to search for units with outdoor entertaining area.')
