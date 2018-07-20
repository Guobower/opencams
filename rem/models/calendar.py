
# -*- coding: utf-8 -*-
from odoo import tools, api, fields, models, _
from odoo import exceptions
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    @api.model
    def _default_name(self):
        for event in self:
            if len(event.unit_ids) == 1:
                return event.unit_ids[0].reference + ':' or ''
        return ''

    unit_ids = fields.Many2many('rem.unit', 'crm_lead_calendar_rel1', 'unit_id', 'cal_id', string='Units',
                                help="Units to show during the appointment / meeting")
