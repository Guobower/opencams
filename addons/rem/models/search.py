# -*- coding: utf-8 -*-
from odoo import api, fields, models


class RemUnitSearch(models.Model):
    _name = 'rem.unit.search'
    _description = 'Search'

    keys = fields.Char(string='Keys', required=True)
    result = fields.Char(string='Result', required=True)
    domain = fields.Char(string='Domain', required=True)
    offer_type_id = fields.Integer(string='Offer Type', required=True)

    @api.model
    def populate_rem_unit_search(self):
        #
        # TODO:
        #
        # - add street2
        # - result must be stored using the unit name format config parameter
        #

        self.env.cr.execute('TRUNCATE TABLE rem_unit_search')

        units = self.env['rem.unit'].search([])

        states = {}
        cities = {}
        zones = {}
        streets = {}
        zips = {}

        for unit in units:

            for offer_type_id in unit.offer_type_id:

                result = ''
                domain = ''

                if unit.state_id:
                    if not unit.state_id in states:
                        states[unit.state_id] = unit.state_id.name
                        if result != '':
                            result += ', '
                        result += unit.state_id.name
                        if domain != '':
                            domain += ', '
                        domain += '("state_id", "=", ' + str(unit.state_id.id) + ')'
                        self.create_rem_unit_search(unit.state_id.name, result, domain, offer_type_id.id)

                if unit.city_id:
                    if not unit.city_id in cities:
                        cities[unit.city_id] = unit.city_id.name
                        if result != '':
                            result += ', '
                        result += unit.city_id.name
                        if domain != '':
                            domain += ', '
                        domain += '("city_id", "=", ' + str(unit.city_id.id) + ')'
                        self.create_rem_unit_search(unit.city_id.name, result, domain, offer_type_id.id)

                if unit.zone_id:
                    if not unit.zone_id in zones:
                        zones[unit.zone_id] = unit.zone_id.name
                        if result != '':
                            result += ', '
                        result += unit.zone_id.name
                        if domain != '':
                            domain += ', '
                        domain += '("zone_id", "=", ' + str(unit.zone_id.id) + ')'
                        self.create_rem_unit_search(unit.zone_id.name, result, domain, offer_type_id.id)

                if unit.street:
                    if not unit.street in streets:
                        streets[unit.street] = unit.street
                        if result != '':
                            result += ', '
                        result += unit.street
                        if domain != '':
                            domain += ', '
                        domain += '("street", "=", "' + str(unit.street) + '")'
                        self.create_rem_unit_search(unit.street, result, domain, offer_type_id.id)

                if unit.zip:
                    if not unit.zip in zips:
                        zips[unit.zip] = unit.zip
                        if result != '':
                            result += ', '
                        result += unit.zip
                        if domain != '':
                            domain += ', '
                        domain += '("zip", "=", "' + str(unit.zip) + '")'
                        self.create_rem_unit_search(unit.zip, result, domain, offer_type_id.id)

    def create_rem_unit_search(self, keys, result, domain, offer_type_id):
        self.env['rem.unit.search'].create({
            'keys': keys,
            'result': result,
            'domain': '[' + domain + ']',
            'offer_type_id': offer_type_id,
        })


class WizardRemUnitSearch(models.TransientModel):
    _name = 'wizard.rem.unit.search'

    @api.multi
    def do_populate_rem_unit_search(self):
        self.env['rem.unit.search'].populate_rem_unit_search()

        return {'type': 'ir.actions.act_window_close'}
