# -*- coding: utf-8 -*-
import openerp
import werkzeug
import json
import base64
from openerp import http, api
from openerp.http import request
from openerp.addons.web.controllers.main import binary_content
from openerp import SUPERUSER_ID

PPG = 8  # Units Per Page
UPR = 4 # Units Per Row


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k,v in self.args.items():
            kw.setdefault(k,v)
        l = []
        for k,v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k,i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k,v)]))
        if l:
            path += '?' + '&'.join(l)
        return path


class WebsiteRem(http.Controller):

    @http.route('/rem/search/<string:multi_search>/<int:offer_type_id>', type='http', auth="public", methods=['GET'], website=True)
    def get_offer_type_products(self, multi_search, offer_type_id, **kwargs):
        results = {
            'result': []
        }

        query = '''
                SELECT result
                FROM rem_unit_search
                WHERE keys ilike %s AND
                      offer_type_id = %s
                LIMIT 10
                '''

        request.env.cr.execute(query, ('%' + multi_search + '%', offer_type_id))

        for row in request.env.cr.fetchall():
            results['result'].append({'result': row})

        return json.dumps(results)

    @http.route(['/page/homepage'], type='http', auth='public', website=True)
    def homepage(self):
        env = request.env
        featured_units = env['rem.unit'].sudo().search([('is_featured', '=', True)])

        row = 0
        first = True
        featured_units_html = ''

        if featured_units:
            for featured_unit in featured_units:
                if row == 0:
                    if first:
                        featured_units_html += '<div class="item active">'
                        first = False
                    else:
                        featured_units_html += '<div class="item">'
                    featured_units_html += '<div class="row">'

                featured_units_html += '''
                    <div class="col-sm-3">
                        <div class="rem-feature-unit">
                            <div class="rem-feature-unit-img">
                                <img class="img img-responsive" src="/rem/unit/image/''' + str(featured_unit.image_ids[0].id) + '''" style="">
                            </div>
                            <div class="rem-feature-unit-text">
                            ''' + featured_unit.display_name + '''
                            </div>
                        </div>
                    </div>
                    '''

                row += 1;
                if row == UPR:
                    featured_units_html += '</div></div>'
                    row = 0

            if row != UPR:
                featured_units_html += '</div></div>'

        try:
            selected_offer_type = env['offer.type'].sudo().search([])[0].id
        except IndexError:
            selected_offer_type = 0

        keep = QueryURL('/rem',
                        offer_type=selected_offer_type,
                        unit_type='',
                        multi_search='',
                        min_beds='',
                        max_beds='',
                        min_price='',
                        max_price='')

        values = {
            'contracts_type': env['offer.type'].sudo().search([]),
            'units_types': env['rem.unit.type'].sudo().search([]),
            'selected_offer_type': selected_offer_type,
            'selected_type_listing': 0,
            'featured_units_html': featured_units_html,
            'keep': keep,
        }

        return request.website.render('website_rem.homepage_rem', values)

    @http.route(['/rem/unit/image/<int:image_id>'], type='http', auth="public", website=True)
    def unit_image(self, image_id=0, **post):
        status, headers, content = binary_content(model='rem.image', id=image_id, field='image', default_mimetype='image/jpg', env=request.env(user=openerp.SUPERUSER_ID))

        if not content:
            img_path = openerp.modules.get_module_resource('website_rem', 'static/img/units', 'default_unit.jpg')
            with open(img_path, 'rb') as f:
                image = f.read()
            content = image.encode('base64')
        if status == 304:
            return werkzeug.wrappers.Response(status=304)
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response

    @http.route(['/rem',
                 '/rem/page/<int:page>',
                 ], type='http', auth='public', website=True)
    def rem(self, page=0, type_listing=0, offer_type=0, unit_type='', multi_search='', min_beds='', max_beds='', min_price='', max_price='', ppg=False, **post):
        env = request.env
        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        url = '/rem'

        domain = []

        keep = QueryURL('/rem',
                        offer_type=offer_type,
                        unit_type=unit_type,
                        multi_search=multi_search,
                        min_beds=min_beds,
                        max_beds=max_beds,
                        min_price=min_price,
                        max_price=max_price)

        # type listing
        selected_type_listing = 0
        try:
            if int(type_listing) == 1:
                selected_type_listing = 1
                post["type_listing"] = 1
                ppg = 9
        except ValueError:
            pass

        # Query contract type
        try:
            if offer_type > 0:
                offer_type = int(offer_type)
                selected_offer_type = offer_type
                domain += [('offer_type_id.id', '=', offer_type)]
                post["offer_type"] = offer_type
            else:
                selected_offer_type = env['offer.type'].sudo().search([])[0].id
                domain += [('offer_type_id.id', '=', selected_offer_type)]
                post["offer_type"] = offer_type
        except:
            selected_offer_type = 0

        # Query unit type
        try:
            unit_type = int(unit_type)
            domain += [('type_id.id', '=', unit_type)]
            post["unit_type"] = unit_type
        except ValueError:
            unit_type = 0

        # Bedrooms
        try:
            min_beds = int(min_beds)
        except ValueError:
            min_beds = 0

        try:
            max_beds = int(max_beds)
        except ValueError:
            max_beds = 0

        # Switch min to max and vice-versa if min > max
        if min_beds > 0 and max_beds > 0 and min_beds > max_beds:
            temp = max_beds
            max_beds = min_beds
            min_beds = temp

        # Query bedrooms
        if min_beds > 0:
            domain += [('bedrooms', '>=', min_beds)]
            post["min_beds"] = min_beds

        if max_beds > 0:
            domain += [('bedrooms', '<=', max_beds)]
            post["max_beds"] = max_beds

        # Price
        try:
            min_price = int(min_price.replace(',', ''))
        except ValueError:
            min_price = 0

        try:
            max_price = int(max_price.replace(',', ''))
        except ValueError:
            max_price = 0

        # Switch min to max and vice-versa if min > max
        if min_price > 0 and max_price > 0 and min_price > max_price:
            temp = max_price
            max_price = min_price
            min_price = temp

        # Query price
        if min_price > 0:
            domain += [('price', '>=', min_price)]
            post["min_price"] = min_price

        if max_price > 0:
            domain += [('price', '<=', max_price)]
            post["max_price"] = max_price

        # Query state, city, zone, street and zip
        if multi_search:
            rem_unit_searchs = env['rem.unit.search'].sudo().search([('result', '=', multi_search)])
            if rem_unit_searchs:
                domain += eval(rem_unit_searchs.domain)

        units_count = env['rem.unit'].sudo().search_count(domain)
        pager = request.website.pager(url=url, total=units_count, page=page, step=ppg, scope=7, url_args=post)
        units = env['rem.unit'].sudo().search(domain, limit=ppg, offset=pager['offset'])

        gmaps_units = []

        if selected_type_listing == 1:
            domain += [('latitude', '!=', 0), ('longitude', '!=', 0)]
            gmaps_units = env['rem.unit'].sudo().search(domain)

        values = {
            'units': units,
            'contracts_type': env['offer.type'].sudo().search([]),
            'units_types': env['rem.unit.type'].sudo().search([]),
            'pager': pager,
            'result_offer_type': offer_type,
            'result_unit_type': unit_type,
            'result_multi_search': multi_search,
            'result_min_beds': min_beds,
            'result_max_beds': max_beds,
            'result_min_price': str(min_price),
            'result_max_price': str(max_price),
            'selected_offer_type': selected_offer_type,
            'selected_type_listing': selected_type_listing,
            'gmaps_units': gmaps_units,
            'gmaps_url': 'http://maps.googleapis.com/maps/api/js?key=' + env['ir.config_parameter'].get_param('gmaps_key') + '&callback=initMap',
            'keep': keep,
        }

        return request.website.render('website_rem.rem_units_list_page', values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth='public', website=True)
    def unit(self, unit):
        env = request.env

        values = {
            'unit': env['rem.unit'].sudo().search([('id', '=', unit[0].id)])
        }
        return request.website.render('website_rem.rem_unit_page', values)

    @http.route(['/rem/user/<int:user_id>'], type='http', auth="public", website=True)
    def user_agent(self, user_id=0, **post):
        status, headers, content = binary_content(model='res.users', id=user_id, field='image', default_mimetype='image/jpg', env=request.env(user=openerp.SUPERUSER_ID))

        if not content:
            img_path = openerp.modules.get_module_resource('website_rem', 'static/img/agents', 'default_agent.jpg')
            with open(img_path, 'rb') as f:
                image = f.read()
            content = image.encode('base64')
        if status == 304:
            return werkzeug.wrappers.Response(status=304)
        image_base64 = base64.b64decode(content)
        headers.append(('Content-Length', len(image_base64)))
        response = request.make_response(image_base64, headers)
        response.status = str(status)
        return response


class WebsiteContact(openerp.addons.web.controllers.main.Home):

    @http.route(['/contact-us'], type='http', auth='public', website=True)
    def website_rem_contact(self):
        return request.website.render('website_rem.contact_us_page')

    @http.route(['/page/contactus'], type='http', auth='none')
    def website_contact(self):
        return werkzeug.utils.redirect('/contact-us', 303)
