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

    @http.route('/rem/search/<string:multi_search>/<int:contract_type_id>', type='http', auth="public", methods=['GET'], website=True)
    def get_contract_type_products(self, multi_search, contract_type_id, **kwargs):
        results = {
            'result': []
        }

        query = '''
                SELECT result
                FROM rem_unit_search
                WHERE keys ilike %s AND
                      contract_type_id = %s
                LIMIT 10
                '''

        request.env.cr.execute(query, ('%' + multi_search + '%', contract_type_id))

        for row in request.env.cr.fetchall():
            results['result'].append({'result': row})

        return json.dumps(results)

    @http.route(['/page/homepage'], type='http', auth='public', website=True)
    def homepage(self):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        contracts_type_obj = pool.get('contract.type')
        contracts_type_ids = contracts_type_obj.search(cr, uid, [], context=context)
        contracts_type = contracts_type_obj.browse(cr, uid, contracts_type_ids, context=context)

        units_types_obj = pool.get('rem.unit.type')
        units_types_ids = units_types_obj.search(cr, uid, [], context=context)
        units_types = units_types_obj.browse(cr, uid, units_types_ids, context=context)
        
        try:
            selected_contract_type = contracts_type[0].id
        except IndexError:
            selected_contract_type = 0

        keep = QueryURL('/rem',
                        contract_type=selected_contract_type,
                        unit_type='',
                        multi_search='',
                        min_beds='',
                        max_beds='',
                        min_price='',
                        max_price='')

        values = {
            'contracts_type': contracts_type,
            'units_types': units_types,
            'selected_contract_type': selected_contract_type,
            'selected_type_listing': 0,
            'keep': keep,
        }

        return request.website.render('website_rem.homepage_rem', values)

    @http.route(['/rem',
                 '/rem/page/<int:page>',
                 ], type='http', auth='public', website=True)
    def rem(self, page=0, type_listing=0, contract_type=0, unit_type='', multi_search='', min_beds='', max_beds='', min_price='', max_price='', ppg=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        contracts_type_obj = pool.get('contract.type')
        contracts_type_ids = contracts_type_obj.search(cr, uid, [], context=context)
        contracts_type = contracts_type_obj.browse(cr, uid, contracts_type_ids, context=context)

        units_types_obj = pool.get('rem.unit.type')
        units_types_ids = units_types_obj.search(cr, uid, [], context=context)
        units_types = units_types_obj.browse(cr, uid, units_types_ids, context=context)

        url = '/rem'

        domain = []

        keep = QueryURL('/rem',
                        contract_type=contract_type,
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
            if contract_type > 0:
                contract_type = int(contract_type)
                selected_contract_type = contract_type
                domain += [('contract_type_id.id', '=', contract_type)]
                post["contract_type"] = contract_type
            else:
                selected_contract_type = contracts_type[0].id
                domain += [('contract_type_id.id', '=', selected_contract_type)]
                post["contract_type"] = contract_type
        except:
            selected_contract_type = 0

        # Query unit type
        try:
            unit_type = int(unit_type)
            domain += [('type_id.id', '=', unit_type)]
            post["unit_type"] = unit_type
        except ValueError:
            unit_type=0

        # Bedrooms
        try:
            min_beds = int(min_beds)
        except ValueError:
            min_beds=0

        try:
            max_beds = int(max_beds)
        except ValueError:
            max_beds=0

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
            min_price=0

        try:
            max_price = int(max_price.replace(',', ''))
        except ValueError:
            max_price=0

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
            rem_unit_searchs = request.env['rem.unit.search'].search([('result', '=', multi_search)])
            if rem_unit_searchs:
                domain += eval(rem_unit_searchs.domain)

        units_obj = pool.get('rem.unit')
        units_count = units_obj.search_count(cr, SUPERUSER_ID, domain, context=context)
        pager = request.website.pager(url=url, total=units_count, page=page, step=ppg, scope=7, url_args=post)
        unit_ids = units_obj.search(cr, SUPERUSER_ID, domain, limit=ppg, offset=pager['offset'], context=context)
        units = units_obj.browse(cr, SUPERUSER_ID, unit_ids, context=context)

        gmaps_units = []

        if selected_type_listing == 1:
            domain += [('latitude', '!=', 0),('longitude', '!=', 0)]
            gmaps_units_obj = pool.get('rem.unit')
            gmaps_units_ids = gmaps_units_obj.search(cr, uid, domain, context=context)
            gmaps_units = gmaps_units_obj.browse(cr, uid, gmaps_units_ids, context=context)

        values = {
            'units': units,
            'contracts_type': contracts_type,
            'units_types': units_types,
            'pager': pager,
            'result_contract_type': contract_type,
            'result_unit_type': unit_type,
            'result_multi_search': multi_search,
            'result_min_beds': min_beds,
            'result_max_beds': max_beds,
            'result_min_price': str(min_price),
            'result_max_price': str(max_price),
            'selected_contract_type': selected_contract_type,
            'selected_type_listing': selected_type_listing,
            'gmaps_units': gmaps_units,
            'gmaps_url': 'http://maps.googleapis.com/maps/api/js?key=' + pool.get('ir.config_parameter').get_param(request.cr, SUPERUSER_ID, 'gmaps_key') + '&callback=initMap',
            'keep': keep,
        }

        return request.website.render('website_rem.rem_units_list_page', values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth='public', website=True)
    def unit(self, unit):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        unit_obj = pool.get('rem.unit')
        unit_ids = unit_obj.search(cr, SUPERUSER_ID, [('id', '=', unit[0].id)], context=context)
        unit = unit_obj.browse(cr, SUPERUSER_ID, unit_ids, context=context)

        values = {
            'unit': unit
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
