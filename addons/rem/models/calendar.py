# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError


class CalendarEvent(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'

    unit_ids = fields.Many2many('rem.unit', 'crm_lead_calendar_rel1', 'unit_id', 'cal_id', string='Show Units',
                                help="Units to show during the appointment / meeting")
