# -*- coding: utf-8 -*-
import json
from openerp import tools, api, fields, models, _


class RemUnit(models.Model):
    _inherit = 'rem.unit'
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    @api.multi
    def _compute_website_url(self):
        super(RemUnit, self)._compute_website_url()
        for unit in self:
            unit.website_url = "/rem/unit/%s" % (unit.id,)


class RemUnitOfferType(models.Model):
    _inherit = 'offer.type'

    @api.multi
    def _compute_website_url(self):
        super(RemUnitOfferType, self)._compute_website_url()
        for unit in self:
            unit.website_url = "/rem?offer_type=%s" % (unit.id,)
