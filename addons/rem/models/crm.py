# -*- coding: utf-8 -*-
from openerp import fields, models


class CrmLead(models.Model):
	_inherit = 'crm.lead'

	unit_lead = fields.Many2many('rem.unit', string='Units')
