# -*- coding: utf-8 -*-

import werkzeug
import openerp

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

PPG = 2 # Products Per Page

class website_rem(http.Controller):

    @http.route(['/rem', '/rem/page/<int:page>'], type='http', auth="public", website=True)
    def rem(self, page=0, category=None, ppg=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        if ppg:
            try:
                ppg = int(ppg)
            except ValueError:
                ppg = PPG
            post["ppg"] = ppg
        else:
            ppg = PPG

        domain = []# later we will use for search

        url = "/rem"

        units_obj = pool.get('rem.unit')
        units_count = units_obj.search_count(cr, uid, domain, context=context)
        pager = request.website.pager(url=url, total=units_count, page=page, step=PPG, scope=7, url_args=post)
        unit_ids = units_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], context=context)
        units = units_obj.browse(cr, uid, unit_ids, context=context)

        values = {
            'units': units,
            'pager': pager
        }

        #RemUnits = http.request.env['rem.unit']

        #return http.request.render('website_rem.units', {
        #    'rem_units': RemUnits.search([])
        #})

        return request.website.render("website_rem.units", values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth="public", website=True)
    def unit(self, unit, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry


        context.update(active_id=unit.id)












        values = {
            'unit': unit
        }
        return request.website.render("website_rem.unit", values)








    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        category_obj = pool['product.public.category']
        template_obj = pool['product.template']

        context.update(active_id=product.id)

        if category:
            category = category_obj.browse(cr, uid, int(category), context=context)
            category = category if category.exists() else False

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int,v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        keep = QueryURL('/shop', category=category and category.id, search=search, attrib=attrib_list)

        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        pricelist = self.get_pricelist()

        from_currency = pool['res.users'].browse(cr, uid, uid, context=context).company_id.currency_id
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        # get the rating attached to a mail.message, and the rating stats of the product
        Rating = pool['rating.rating']
        rating_ids = Rating.search(cr, uid, [('message_id', 'in', product.website_message_ids.ids)], context=context)
        ratings = Rating.browse(cr, uid, rating_ids, context=context)
        rating_message_values = dict([(record.message_id.id, record.rating) for record in ratings])
        rating_product = product.rating_get_stats([('website_published', '=', True)])

        if not context.get('pricelist'):
            context['pricelist'] = int(self.get_pricelist())
            product = template_obj.browse(cr, uid, int(product), context=context)

        values = {
            'search': search,
            'category': category,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'compute_currency': compute_currency,
            'attrib_set': attrib_set,
            'keep': keep,
            'categories': categs,
            'main_object': product,
            'product': product,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'rating_message_values' : rating_message_values,
            'rating_product' : rating_product
        }
        return request.website.render("website_sale.product", values)










