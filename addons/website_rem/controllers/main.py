# -*- coding: utf-8 -*-

import werkzeug

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools, api, fields, models
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug


PPG = 20 # Products Per Page

class website_rem(http.Controller):


    @http.route(['/rem', '/rem/page/<int:page>'], type='http', auth="public", website=True)
    def rem(self, page=0, city='', type='', is_new='', beds=0, baths=0, min_price=0, max_price=0, search_box='', **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        domain = [('name', 'ilike', search_box)]

        url = "/rem"
        units = False
        cities = False
        types = False
        pager = False

        units_obj = request.env['rem.unit']
        units_count = units_obj.search_count(domain)
        # pager = request.website.pager(url=url, total=units_count, page=page, step=PPG, scope=7, url_args=post)

        units = units_obj.search(domain)
        attrib_list = request.httprequest.args.getlist('attrib')

        values = {
            'units': units,
            'cities': cities,
            'types': types,
            'pager': pager,
            'search_city': city,
            'search_type': type,
            'search_is_new': is_new,
            'search_beds': beds,
            'search_baths': baths,
            'search_min_price': min_price,
            'search_max_price': max_price,
            'search': search_box
        }

        return request.website.render("website_rem.rem_list_page1", values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth="public", website=True)
    def unit(self, unit, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        values = {
            'unit': unit
        }

        return request.website.render("website_rem.rem_unit_page", values)