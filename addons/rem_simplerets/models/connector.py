# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _


class SimpleRetsConnector(models.Model):
    _name = 're.connector.rets'
    _inherit = 're.connector.abstract.model'
