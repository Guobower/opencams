# -*- coding: utf-8 -*-

import werkzeug
import openerp

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug

PPG = 20 # Products Per Page
PPR = 4  # Products Per Row

class website_rem(http.Controller):

    @http.route(['/rem', '/rem/page/<int:page>'], type='http', auth="public", website=True)
    def rem(self, page=0, category=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        domain = []# later we will use for search
        pager_offset = 0
        units_obj = pool.get('rem.unit')
        units_count = units_obj.search_count(cr, uid, domain, context=context)
        unit_ids = units_obj.search(cr, uid, domain, limit=PPG, offset=pager_offset, context=context)
        units = units_obj.browse(cr, uid, unit_ids, context=context)
        values = {
            'units': units
        }
        return request.website.render("website_rem.units", values)
    