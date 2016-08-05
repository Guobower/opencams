from openerp import models, SUPERUSER_ID


class Lead(models.Model):
    _inherit = 'crm.lead'

    def website_form_input_filter(self, request, values):
        res = super(Lead, self).website_form_input_filter(request, values)

        if request.params.get('type_seller', False):

            city = ''

            if request.params.get('city'):
                city = request.params.get('city').strip()
            re_city = False
            cities = self.sudo().env['rem.unit.city'].search_read(domain=[('name', '=ilike', (city or '') + "%")])
            if len(cities) == 1:
                re_city = cities[0]['id']
            else:
                values.update({'description': city})

            values.update({
                'priority': '3',
                'color': 3,
                'name': 'Seller contact: ' + request.params.get('name').strip(),
                're_city': re_city,
            })
        elif request.params.get('type_buyer', False):
            if request.params.get('unit_id'):
                unit_id = request.params.get('unit_id')
            unit = self.sudo().env['rem.unit'].search_read(domain=[('id', '=', unit_id)])[0]
            values.update({
                'priority': '3',
                'color': 5,
                'name': ('%s contact: %s' % (unit['contract_type_id'][1], request.params.get('name').strip())),
                'user_id': unit['user_id'][0]
            })
        return res
