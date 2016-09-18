# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    rem_category = fields.Selection([
        ('general', _('General Features')),
        ('indoor', _('Indoor Features')),
        ('outdoor', _('Outdoor Features'))], string="REM Category")
