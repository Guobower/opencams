# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RemUnit(models.Model):
    _inherit = 'rem.unit'

    # General Features
    bedrooms = fields.Integer(string='Bedrooms', default=1, required=True)
    bathrooms = fields.Integer(string='Bathrooms', default=1, required=True)
    toilets = fields.Integer(string='Toilets', default=1, required=True)
    living_area = fields.Float('Living Area', default=0)
    land_area = fields.Float('Land Area', default=0)
    points_interest = fields.Many2many('location.preferences', string='Points of Interest')

    # Indoor Features
    area = fields.Float(string='Area', default=0, required=True)
    airConditioning = fields.Boolean(string='Air Conditioned', default=False)
    ducted_cooling = fields.Boolean(string='Ducted Cooling', default=False)
    builtInRobes = fields.Boolean(string='Built-in Wardrobes', default=False)
    dishwasher = fields.Boolean(string='Dishwasher', default=False)

    # Outdoor Features
    garages = fields.Integer(string='Garage Spaces', default=0, required=True)
    backyard = fields.Boolean(string='Backyard', default=False)
    dog_friendly = fields.Boolean(string='Dog Friendly', default=False)
    secure_parking = fields.Boolean(string='Secure Parking', default=False)
    alarmSystem = fields.Boolean(string='Alarm System', default=False)
    swpool = fields.Boolean(string='Swimming Pool', default=False)
    entertaining = fields.Boolean(string='Outdoor Entertaining Area', default=False)
    balconies = fields.Integer(string='Balconies', default=0)

    @api.model
    def init_rem_features_in_rem_fields(self):
        self._cr.execute("""
            UPDATE ir_model_fields
            SET rem_category='general'
            WHERE model='rem.unit' AND
                  (name='bedrooms' OR
                   name='bathrooms' OR
                   name='toilets' OR
                   name='living_area' OR
                   name='land_area' OR
                   name='points_interest');
            UPDATE ir_model_fields
            SET rem_category='indoor'
            WHERE model='rem.unit' AND
                  (name='area' OR
                   name='airConditioning' OR
                   name='ducted_cooling' OR
                   name='builtInRobes' OR
                   name='dishwasher');
            UPDATE ir_model_fields
            SET rem_category='outdoor'
            WHERE model='rem.unit' AND
                  (name='garages' OR
                   name='backyard' OR
                   name='dog_friendly' OR
                   name='secure_parking' OR
                   name='alarmSystem' OR
                   name='swpool' OR
                   name='entertaining' OR
                   name='balconies');
        """)
        self._cr.commit()

    def get_formated_name(self, rec, mask):
        STREET = (rec.street or '').upper()
        STREET2 = (rec.street2 or '').upper()
        CITY = (rec.city_id.name or '').upper()
        STATE = (rec.state_id.code or '').upper()
        try:
            res = mask.format(
                street=rec.street,
                STREET=STREET,
                street2=rec.street2 or '',
                STREET2=STREET2,
                city=rec.city_id.name or '',
                CITY=CITY,
                state=rec.state_id.code or '',
                STATE=STATE,
                zip=rec.zip or '',
                bedrooms=rec.bedrooms or 0,
                bathrooms=rec.bathrooms or 0,
                living_area=rec.living_area or 0,
                land_area=rec.land_area or 0,
            )
        except:
            res = _("Parsing ERROR - Check your name format in Listing >> Settings")
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('max_planned_revenue'):
            args += [('price', '<=', context.get('max_planned_revenue'))]

        if context.get('min_garages'):
            args += [('garages', '>=', context.get('min_garages'))]
        if context.get('max_bedrooms') and context.get('min_bedrooms'):
            args += [
                ('bedrooms', '<=', context.get('max_bedrooms')) and ('bedrooms', '>=', context.get('min_bedrooms'))]
        if context.get('min_bathrooms'):
            args += [('bathrooms', '>=', context.get('min_bathrooms'))]
        if context.get('min_living_area'):
            args += [('living_area', '>=', context.get('min_living_area'))]
        return super(RemUnit, self).search(args, offset, limit, order, count=count)

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def name_get(self):
        units = []
        for rec in self:
            if rec.offer_type_id.is_computed:
                name = self.get_formated_name(rec, rec.offer_type_id.unit_name_format)
            else:
                name = rec.name2
            units.append((rec.id, name))
        return units

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def _compute_name(self):
        for rec in self:
            if rec.offer_type_id.is_computed:
                name = self.get_formated_name(rec, rec.offer_type_id.unit_name_format)
            else:
                name = rec.name2
            rec.name = name

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def _get_website_name(self):
        units = []
        for rec in self:
            name = self.get_formated_name(rec, rec.offer_type_id.unit_websitename_format)
            units.append((rec.id, name))
        return units
