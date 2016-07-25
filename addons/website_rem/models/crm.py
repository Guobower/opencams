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
                'name': 'Seller contact: ' + request.params.get('name').strip(),
                're_city': re_city,
            })

        return res
