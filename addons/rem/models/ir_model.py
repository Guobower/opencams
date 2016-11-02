# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _

_rem_categories = [
	('general', _('General Features')),
	('indoor', _('Indoor Features')),
	('outdoor', _('Outdoor Features'))]


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    rem_category = fields.Selection(_rem_categories, string="REM Category")
