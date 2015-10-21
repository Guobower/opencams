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

        domain = [] # later we will use for search

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

        return request.website.render("website_rem.units", values)

    @http.route(['/rem/unit/<model("rem.unit"):unit>'], type='http', auth="public", website=True)
    def unit(self, unit, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        values = {
            'unit': unit
        }

        return request.website.render("website_rem.unit", values)