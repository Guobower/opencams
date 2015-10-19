# -*- coding: utf-8 -*-

import werkzeug
import openerp

from openerp import SUPERUSER_ID
from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug


class website_rem(http.Controller):

    @http.route(['/rem', '/rem/page/<int:page>'], type='http', auth="public", website=True)
    def rem(self, page=0, category=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        values = {}
        return request.website.render("website_rem.units", values)
    