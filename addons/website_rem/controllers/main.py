# -*- coding: utf-8 -*-
import openerp
import werkzeug
import json
import base64
import random
import string
from openerp import http, api
from openerp.http import request
from openerp.addons.web.controllers.main import binary_content, ensure_db
from openerp import SUPERUSER_ID
from openerp.addons.website.models.website import slug

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

    @http.route(['/mobile/units',
                 '/mobile/units/page/<int:page>',
                 ], type='http', auth="public", methods=['GET'], website=True)
    def feed_units(self, page=0, ppg=10, **post):
        env = request.env

        results = {}
        units_html = ''
        mobile_feed_domain = env['ir.config_parameter'].get_param('mobile_feed_domain')

        units_count = env['rem.unit'].sudo().search_count([])
        pager = request.website.pager(url='', total=units_count, page=page, step=ppg, scope=7, url_args=post)
        units = env['rem.unit'].sudo().search([], limit=ppg, offset=pager['offset'])

        if units:
            for unit in units:

                units_html += '''
                    <a href="#/tab/unit/''' + str(unit.id) + '''" class="rem-unit-link">
                        <div class="list card">
                            <div class="item item-image">
                                <img src="''' + mobile_feed_domain + '''/rem/unit/image/''' + str(unit.image_ids[0].id) + '''" alt="''' + unit.display_name + '''">
                                <div class="rem-unit-offer-type">''' + unit.offer_type_id.name + '''</div>
                            </div>
                            <div class="rem-unit-card-agent-container">
                                <figure class="rem-unit-card-agent">
                                    <div class="rem-unit-card-agent-wrapper">
                                        <img class="rem-unit-card-agent-photo" src="''' + mobile_feed_domain + '''/rem/user/''' + str(unit.user_id.id) + '''" alt="Jermaine D. Fort" title="''' + unit.user_id.name + '''">
                                    </div>
                                    <figcaption>''' + unit.user_id.name + '''</figcaption>
                                </figure>
                            </div>
                            <div class="rem-unit-card-price">
                    '''

                if unit.price > 0:
                    units_html += self.display_price_with_currency(unit)

                units_html += '''
                            </div>
                            <div class="rem-unit-card-title">''' + unit.display_name + '''</div>
                            <div class="rem-unit-card-details">
                    '''

                if unit.bedrooms > 0:
                    units_html += '<span><i class="zmdi zmdi-hotel"></i> ' + str(unit.bedrooms) + '</span>'
                if unit.bathrooms > 0:
                    units_html += '<span><i class="fa fa-shower"></i> ' + str(unit.bathrooms) + '</span>'
                if unit.garages > 0:
                    units_html += '<span><i class="zmdi zmdi-car"></i> ' + str(unit.garages) + '</span>'

                units_html += '''
                            </div>
                        </div>
                    </a>
                    '''

        results = {
            'result': units_html,
            'page_previous': pager['page_previous']['num'],
            'page_next': pager['page_next']['num'],
            'page_num': pager['page']['num'],
            'page_count': pager['page_count'],
            'col_off_set': ' col-offset-50' if pager['page']['num'] == 1 else '',
        }

        return json.dumps(results)

    def display_price_with_currency(self, unit):
        if unit.currency_id.position == 'before':
            return unit.currency_id.symbol + ' ' + '{0:g}'.format(unit.price)
        return '{0:g}'.format(unit.price) + ' ' + unit.currency_id.symbol

    @http.route(['/mobile/units/<int:unit_id>'], type='http', auth="public", methods=['GET'], website=True)
    def feed_unit(self, unit_id):
        env = request.env

        results = {}

        unit_html = ''
        unit_title = ''
        unit_images = []
        mobile_feed_domain = env['ir.config_parameter'].get_param('mobile_feed_domain')

        unit = env['rem.unit'].sudo().search([('id', '=', unit_id)])

        if unit:

            unit_title = unit.display_name

            for img in unit.image_ids:
                unit_images.append(('<img src="' + mobile_feed_domain + '/rem/unit/image/' + str(img.id) + '" alt="' + unit.display_name + '" class="item item-image">'))

            unit_html += '''
                <div class="rem-unit-card">
                    <div class="rem-unit-title">''' + unit.display_name + '''</div>
                '''

            if unit.price > 0:
                unit_html += '<div class="rem-unit-price">' + str(unit.price) + '</div>'

            unit_html += '<div class="rem-unit-sub-title">'

            if unit.bedrooms > 0:
                unit_html += '<span title="Bedrooms" class="margin-right-20"><i class="zmdi zmdi-hotel"></i> ' + str(unit.bedrooms) + '</span>'

            if unit.bathrooms > 0:
                unit_html += '<span title="Bathrooms" class="margin-right-20"><i class="fa fa-shower aria-hidden="true""></i> ' + str(unit.bathrooms) + '</span>'

            if unit.garages > 0:
                unit_html += '<span title="Garages" class="margin-right-20"><i class="zmdi zmdi-car"></i> ' + str(unit.garages) + '</span>'

            unit_html += '</div>'

            unit_html += '''
                    <div class="rem-unit-description">''' + unit.website_description + '''</div>
                </div>
                <div class="features">
                    <div class="rem-unit-card">
                        <div class="feature-title margin-bottom-10">General Features</div>
            '''

            if unit.bedrooms > 0:
                unit_html += '<div><label>Bedrooms:</label>' + str(unit.bedrooms) + '</div>'

            if unit.bathrooms > 0:
                unit_html += '<div><label>Bathrooms:</label>' + str(unit.bathrooms) + '</div>'

            if unit.living_area > 0:
                unit_html += '<div><label>Living Area:</label>' + str(unit.living_area) + '</div>'

            if unit.land_area > 0:
                unit_html += '<div><label>Land area:</label>' + str(unit.land_area) + '</div>'

            unit_html += '</div>'

            if unit.airConditioning or unit.ducted_cooling or unit.builtInRobes or unit.dishwasher:

                unit_html += '<div class="rem-unit-card"><div class="feature-title margin-bottom-10">Indoor Features</div>'

                if unit.airConditioning:
                    unit_html += '<div><label>Air Conditioned:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.ducted_cooling:
                    unit_html += '<div><label>Ducted Cooling:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.builtInRobes:
                    unit_html += '<div><label>Built-in Wardrobes:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.dishwasher:
                    unit_html += '<div><label>Dishwasher:</label><i class="zmdi zmdi-check"></i></div>'

                unit_html += '</div>'

            if unit.backyard or unit.alarmSystem or unit.pool or unit.entertaining or unit.garages > 0 or unit.secure_parking or  unit.dog_friendly:

                unit_html += '<div class="rem-unit-card"><div class="feature-title margin-bottom-10">Outdoor Features</div>'

                if unit.backyard:
                    unit_html += '<div><label>Backyard:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.alarmSystem:
                    unit_html += '<div><label>Alarm System:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.pool:
                    unit_html += '<div><label>Swimming Pool:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.entertaining:
                    unit_html += '<div><label>Outdoor Entertaining Area:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.garages > 0:
                    unit_html += '<div><label>Garage spaces:</label>' + str(unit.garages) + '</div>'

                if unit.secure_parking:
                    unit_html += '<div><label>Secure Parking:</label><i class="zmdi zmdi-check"></i></div>'

                if unit.dog_friendly:
                    unit_html += '<div><label>Dog Friendly:</label><i class="zmdi zmdi-check"></i></div>'

                unit_html += '</div>'

            unit_html += '</div>'

            if unit.table_id and unit.table_id.line_ids:

                unit_html += '''
                    <div class="rem-unit-card">
                        <table>
                            <thead>
                                <tr>
                                    <th>Rental Period</th>
                                    <th>Price</th>
                                </tr>
                            </thead>
                            <body>
                    '''

                for line in unit.table_id.line_ids:
                    unit_html += '''
                                <tr>
                                    <td>
                                        ''' + str(unit.table_id.format_season_dates(line.date_start)) + ''' &nbsp;-&nbsp; ''' + str(unit.table_id.format_season_dates(line.date_end)) + '''
                                    </td>
                                    <td>
                                        ''' + str(unit.table_id.calculate_unit_price(unit.price, line.discount, line.fixed_price)) + '''
                                    </td>
                                </tr>
                    '''

                unit_html += '''
                            </body>
                        </table>
                    </div>
                '''

        results = { 'result': unit_html, 'title': unit_title, 'images': unit_images }

        return json.dumps(results)

    @http.route(['/my/favorites',
                 '/my/favorites/page/<int:page>',
                 ], type='http', auth='public', website=True)
    def my_favorites(self, page=0, ppg=False, **post):
        env = request.env
        ensure_db()

        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)

        PPG = 9

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        url = '/my/favorites'

        domain_user = [('user_id', '=', request.session.uid)]
        domain_ids = []

        favorites_units = env['rem.unit.favorite'].sudo().search_read(domain_user, ['unit_id'])

        for favorite_unit in favorites_units:
            domain_ids.append([favorite_unit['unit_id'][0]])

        domain_ids = [('id', 'in', domain_ids)]

        favorites_units = env['rem.unit.favorite'].sudo().search(domain_user)

        units_count = env['rem.unit'].sudo().search_count(domain_ids)
        pager = request.website.pager(url=url, total=units_count, page=page, step=ppg, scope=9, url_args=post)
        units = env['rem.unit'].sudo().search(domain_ids, limit=ppg, offset=pager['offset'])

        favorites_units = env['rem.unit.favorite'].sudo().search(domain_user)

        values = {
            'units': units,
            'favorites_units': favorites_units,
            'pager': pager,
        }

        return request.render('website_rem.my_favorites_units_page', values)

    @http.route('/rem/favorite/set/<int:rem_unit_id>', type='http', auth="public", methods=['GET'], website=True)
    def set_rem_favorite(self, rem_unit_id, **kwargs):
        env = request.env
        ensure_db()
        results = {'result': []}
        if request.session.uid:
            record = env['rem.unit.favorite'].sudo().search([
                ('user_id', '=', request.session.uid), ('unit_id', '=', rem_unit_id)], limit=1)
            if not record:
                env['rem.unit.favorite'].sudo().create({
                    'user_id': [(4, request.session.uid)],
                    'unit_id': [(4, rem_unit_id)],
                    })
            results['result'].append({'result': 1})
        else:
            results['result'].append({'result': 0})

        return json.dumps(results)

    @http.route('/rem/favorite/unset/<int:rem_unit_id>', type='http', auth="public", methods=['GET'], website=True)
    def unset_rem_favorite(self, rem_unit_id, **kwargs):
        env = request.env
        ensure_db()
        results = {'result': []}
        if request.session.uid:
            record = env['rem.unit.favorite'].sudo().search([
                ('user_id', '=', request.session.uid), ('unit_id', '=', rem_unit_id)], limit=1)
            if record:
                record.sudo().unlink()
            results['result'].append({'result': 1})
        else:
            results['result'].append({'result': 0})

        return json.dumps(results)

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
                    <a href="rem/unit/''' + slug(featured_unit) + '''" target="_blank">
                        <div class="col-sm-3">
                            <div class="rem-feature-unit">
                                <div class="rem-feature-unit-img">
                                    <img class="img img-responsive" alt="" src="/rem/unit/image/''' + str(featured_unit.image_ids[0].id) + '''">
                                </div>
                                <div class="rem-feature-unit-text">
                                ''' + featured_unit.display_name + '''
                                </div>
                            </div>
                        </div>
                    </a>
                    '''

                row += 1;
                if row == UPR:
                    featured_units_html += '</div></div>'
                    row = 0

            if row != 0:
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
            'offers_type': env['offer.type'].sudo().search([]),
            'units_types': env['rem.unit.type'].sudo().search([]),
            'selected_offer_type': selected_offer_type,
            'selected_type_listing': 0,
            'featured_units_html': featured_units_html,
            'keep': keep,
        }

        return request.render('website_rem.homepage_rem', values)

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

        # Query Offer type
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
            for rem_unit_search in rem_unit_searchs:
                domain += eval(rem_unit_search.domain)

        units_count = env['rem.unit'].sudo().search_count(domain)
        pager = request.website.pager(url=url, total=units_count, page=page, step=ppg, scope=7, url_args=post)
        units = env['rem.unit'].sudo().search(domain, limit=ppg, offset=pager['offset'])

        gmaps_units = []

        if selected_type_listing == 1:
            domain += [('latitude', '!=', 0), ('longitude', '!=', 0)]
            gmaps_units = env['rem.unit'].sudo().search(domain)

        ensure_db()
        favorites_units = []
        if request.session.uid:
            favorites_units = env['rem.unit.favorite'].sudo().search([('user_id', '=', request.session.uid)])

        values = {
            'units': units,
            'offers_type': env['offer.type'].sudo().search([]),
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
            'favorites_units': favorites_units,
            'gmaps_units': gmaps_units,
            'gmaps_url': 'http://maps.googleapis.com/maps/api/js?key=' + env['ir.config_parameter'].get_param('gmaps_key') + '&callback=initMap',
            'keep': keep,
        }

        return request.render('website_rem.rem_units_list_page', values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth='public', website=True)
    def unit(self, unit):
        env = request.env

        unit = env['rem.unit'].sudo().search([('id', '=', unit[0].id)])

        left_general_features_html = ''
        right_general_features_html = ''
        left_indoor_features_html = ''
        right_indoor_features_html = ''
        left_outdoor_features_html = ''
        right_outdoor_features_html = ''

        left_general_index = 0
        right_general_index = 0
        left_indoor_index = 0
        right_indoor_index = 0
        left_outdoor_index = 0
        right_outdoor_index = 0

        for fields in unit.offer_type_id.showfields_ids:
            if hasattr(unit, fields.name):

                feature = self.get_custom_field_value(unit, fields)

                if feature != '':
                    if fields.rem_category == 'general':
                        if left_general_features_html == '' or left_general_index <= right_general_index:
                            left_general_features_html += feature
                            left_general_index += 1
                        else:
                            right_general_features_html += feature
                            right_general_index += 1

                    elif fields.rem_category == 'indoor':
                        if left_indoor_features_html == '' or left_indoor_index <= right_indoor_index:
                            left_indoor_features_html += feature
                            left_indoor_index += 1
                        else:
                            right_indoor_features_html += feature
                            right_indoor_index += 1

                    elif fields.rem_category == 'outdoor':
                        if left_outdoor_features_html == '' or left_outdoor_index <= right_outdoor_index:
                            left_outdoor_features_html += feature
                            left_outdoor_index += 1
                        else:
                            right_outdoor_features_html += feature
                            right_outdoor_index += 1

        values = {
            'unit': unit,
            'left_general_features_html': left_general_features_html,
            'right_general_features_html': right_general_features_html,
            'left_indoor_features_html': left_indoor_features_html,
            'right_indoor_features_html': right_indoor_features_html,
            'left_outdoor_features_html': left_outdoor_features_html,
            'right_outdoor_features_html': right_outdoor_features_html
        }

        return request.render('website_rem.rem_unit_page', values)

    def get_custom_field_value(self, unit, fields):
        feature = ''
        if fields.ttype == 'integer' or fields.ttype == 'float':
            if getattr(unit, fields.name) > 0:
                feature = '<div><label>' + fields.label + ':</label>' + str(getattr(unit, fields.name)) + '</div>'
        elif fields.ttype == 'boolean':
            if getattr(unit, fields.name):
                feature = '<div><label>' + fields.label + ':</label><i class="zmdi zmdi-check"></i></div>'
        elif fields.ttype == 'many2many':
            for values in getattr(unit, fields.name):
                if feature == '':
                    feature = '<div class="rem-inline-block"><label>' + fields.label + ':</label></div>'
                feature += '<div class="rem-tag rem-inline-block">' + values.name + '</div>'
        elif getattr(unit, fields.name) != '' and getattr(unit, fields.name) != False:
            feature = '<div><label>' + fields.label + ':</label>' + str(getattr(unit, fields.name)) + '</div>'
        return feature

    @http.route('/rem/user/signup/<string:email>', type='http', auth="public", methods=['GET'], website=True)
    def user_signup(self, email, **kwargs):
        env = request.env
        ensure_db()
        results = {'result': []}
        password = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))

        # TODO:
        # create user
        # send an email with password

        results['result'].append({'result': 1})

        return json.dumps(results)

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

    @http.route(['/atom/sellers/<model("offer.type"):otype>/feed'], type='http', auth="public")
    def re_atom_feed(self, otype, limit='15'):
        v = {}
        v['otype'] = otype
        v['base_url'] = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        v['posts'] = request.env['rem.unit'].sudo().search(
            [('offer_type_id', '=', otype.id), ('website_published', '=', True)], limit=min(int(limit), 50))
        return request.render("website_rem.sell_feed", v, headers=[('Content-Type', 'application/atom+xml')])

    @http.route(['/rem/sell'], type='http', auth='public', website=True)
    def website_rem_sell(self):
        env = request.env
        values = {
            'unit_types': env['rem.unit.type'].sudo().search([]),
        }
        return request.render('website_rem.sell', values)


class WebsiteContact(openerp.addons.web.controllers.main.Home):

    @http.route(['/contact-us'], type='http', auth='public', website=True)
    def website_rem_contact(self):
        return request.render('website_rem.contact_us_page')

    @http.route(['/page/contactus'], type='http', auth='none')
    def website_contact(self):
        return werkzeug.utils.redirect('/contact-us', 303)
