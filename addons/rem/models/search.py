# -*- coding: utf-8 -*-
from openerp import api, fields, models


class RemUniCity(models.Model):
    _name = 'rem.unit.search'
    _description = 'Search'

    keys = fields.Char(string='Keys', required=True)
    result = fields.Char(string='Result', required=True)
    domain = fields.Char(string='Domain', required=True)
    contract_type_id = fields.Integer(string='Contract Type', required=True)

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

        for unit in units:

            for contract_type_id in unit.contract_type_id:

                result = ''
                domain = ''

                if unit.state_id:
                    if result != '':
                        result += ', '
                    result += unit.state_id.name
                    if domain != '':
                        domain += ', '
                    domain += '("state_id", "=", "' + str(unit.state_id.id) + '")'
                    self.create_rem_unit_search(unit.state_id.name, result, domain, contract_type_id.id)

                if unit.city_id:
                    if result != '':
                        result += ', '
                    result += unit.city_id.name
                    if domain != '':
                        domain += ', '
                    domain += '("city_id", "=", "' + str(unit.city_id.id) + '")'
                    self.create_rem_unit_search(unit.city_id.name, result, domain, contract_type_id.id)

                if unit.zone_id:
                    if result != '':
                        result += ', '
                    result += unit.zone_id.name
                    if domain != '':
                        domain += ', '
                    domain += '("zone_id", "=", "' + str(unit.zone_id.id) + '")'
                    self.create_rem_unit_search(unit.zone_id.name, result, domain, contract_type_id.id)

                if unit.street:
                    if result != '':
                        result += ', '
                    result += unit.street
                    if domain != '':
                        domain += ', '
                    domain += '("street", "=", "' + str(unit.street) + '")'
                    self.create_rem_unit_search(unit.street, result, domain, contract_type_id.id)

                if unit.zip:
                    if result != '':
                        result += ', '
                    result += unit.zip
                    if domain != '':
                        domain += ', '
                    domain += '("zip", "=", "' + str(unit.zip) + '")'
                    self.create_rem_unit_search(unit.zip, result, domain, contract_type_id.id)

    def create_rem_unit_search(self, keys, result, domain, contract_type_id):
        self.env['rem.unit.search'].create({
            'keys': keys,
            'result': result,
            'domain': '[' + domain + ']',
            'contract_type_id': contract_type_id,
        })


class WizardRemUnitSearch(models.TransientModel):
    _name = 'wizard.rem.unit.search'

    @api.multi
    def do_populate_rem_unit_search(self):
        self.env['rem.unit.search'].populate_rem_unit_search()

        return {'type': 'ir.actions.act_window_close'}
