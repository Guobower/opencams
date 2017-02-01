# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RemUnit(models.Model):
    _inherit = 'rem.unit'

    people = fields.Integer(string='People', required=True)
    area = fields.Float(string='Area')
    seats = fields.Integer(string='Seats')
    windows = fields.Integer(string='Windows')
    desk_phones = fields.Integer(string='Desk Phones')

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
                people=rec.people or 0,
            )
        except:
            res = _("Parsing ERROR - Check your name format in Listing >> Settings")
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('max_planned_revenue'):
            args += [('price', '<=', context.get('max_planned_revenue'))]

        if context.get('max_people') and context.get('min_people'):
            args += [
                ('people', '<=', context.get('max_people')) and ('people', '>=', context.get('min_people'))]
        if context.get('min_area'):
            args += [('area', '>=', context.get('min_area'))]
        if context.get('max_seats') and context.get('min_seats'):
            args += [
                ('seats', '<=', context.get('max_seats')) and ('seats', '>=', context.get('min_seats'))]
        if context.get('min_windows'):
            args += [('windows', '>=', context.get('min_windows'))]
        if context.get('min_desk_phones'):
            args += [('desk_phones', '>=', context.get('min_desk_phones'))]

        return super(RemUnit, self).search(args, offset, limit, order, count=count)

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'people')
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
                 'city_id.name', 'zip', 'people')
    def _compute_name(self):
        for rec in self:
            if rec.offer_type_id.is_computed:
                name = self.get_formated_name(rec, rec.offer_type_id.unit_name_format)
            else:
                name = rec.name2
            rec.name = name

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'people')
    def _get_website_name(self):
        units = []
        for rec in self:
            name = self.get_formated_name(rec, rec.offer_type_id.unit_websitename_format)
            units.append((rec.id, name))
        return units
