# -*- coding: utf-8 -*-
import base64

from odoo import http, _
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        ArchRequest = request.env['architectural.request']

        # Child of because might be some employee of a owner company
        request_count = ArchRequest.search_count([
            ('unit_id', 'child_of', [partner.commercial_partner_id.id]),
        ])

        values.update({
            'request_count': request_count,
        })
        return values

    def _request_check_access(self, req_id, access_token=None):
        arch_request = request.env['architectural.request'].browse([req_id])
        arch_request_sudo = arch_request.sudo()
        try:
            arch_request.check_access_rights('read')
            arch_request.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(arch_request_sudo.access_token, access_token):
                raise
        return arch_request_sudo

    @http.route(['/my/architectural/requests', '/my/architectural/requests/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_orders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ArchRequest = request.env['architectural.request']

        # Child of because might be some employee of a owner company
        domain = [
            ('unit_id', 'child_of', [partner.commercial_partner_id.id]),
        ]

        searchbar_sortings = {
            'date': {'label': _('Request Date'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Status'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'create_date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('architectural.request', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        request_count = ArchRequest.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/architectural/requests",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=request_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        arch_requests = ArchRequest.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_arch_requests_history'] = arch_requests.ids[:100]

        values.update({
            'date': date_begin,
            'arch_requests': arch_requests.sudo(),
            'page_name': 'order',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/orders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("opencams.portal_my_requests", values)
