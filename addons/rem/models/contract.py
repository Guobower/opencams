# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from docutils.parsers.rst.directives import flag


class RemContractType(models.Model):
    _name = 'rem.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    code = fields.Char(string='Short Code', size=5, required=True, help="The contracts will be named using this prefix.")
    notes = fields.Text(string='Description', help='Brief description.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemTenantContractType(models.Model):
    _name = 'rem.tenant.contract.type'
    _description = 'Tenant Agreement Type'
    _inherit = ['rem.contract.type']


class RemBuyerContractType(models.Model):
    _name = 'rem.buyer.contract.type'
    _description = 'Buyer Agreement Type'
    _inherit = ['rem.contract.type']


class RemListingContractType(models.Model):
    _name = 'rem.listing.contract.type'
    _description = 'Listing Agreement Type'
    _inherit = ['rem.contract.type']


class RemAbstractContract(models.Model):
    _name = 'rem.abstract.contract'
    _description = 'Abstract Contract'

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def name_get(self):
        units = []
        for rec in self:
            name = rec.type_id.code or _("Agreement")
            if rec.date_start and rec.period and rec.period_unit:
                name += " %s - %s %s" % (rec.date_start, rec.period, rec.period_unit)
            units.append((rec.id, name))
        return units

    type_id = fields.Many2one('rem.contract.type', string='Type', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', compute='_compute_date_end', required=True)
    auto_renew = fields.Boolean(string='Auto Renew?', default=False,
                                help='Check for automatically renew for same period and log in the chatter')
    notice_date = fields.Date('Notice Date', compute='_compute_date_notice',)
    period = fields.Integer('Period', default=1)
    period_unit = fields.Selection([('days', 'Day(s)'), ('months', 'Month(s)')], string='Period Unit',
                                   default='months')
    notice_period = fields.Integer('Notice Period', default=15)
    notice_period_unit = fields.Selection([('days', 'Days'), ('months', 'Months')], string='Notice Unit',
                                          default='days')
    current = fields.Boolean(string='Current Contract', default=True,
                             help='This contract is the current one for this unit?')

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def _compute_date_end(self):
        for rec in self:
            date_calc = False
            if not rec.date_start:
                return False
            if rec.period_unit == 'months':
                date_calc = datetime.strptime(rec.date_start + ' 00:00:00',
                                              DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=rec.period)
            else:
                date_calc = datetime.strptime(rec.date_start + ' 00:00:00',
                                              DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=rec.period)
            rec.date_end = date_calc

    @api.multi
    @api.depends('date_end', 'notice_period_unit', 'notice_period')
    def _compute_date_notice(self):
        for rec in self:
            date_calc = False
            if rec.notice_period_unit == 'months':
                date_calc = datetime.strptime(rec.date_end + ' 00:00:00',
                                              DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=rec.notice_period)
            else:
                date_calc = datetime.strptime(rec.date_end + ' 00:00:00',
                                              DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=rec.notice_period)
            rec.notice_date = date_calc

    def get_is_contract_current(self, date_start, date_end):
        today_date = fields.Date.today()
        return (date_start <= today_date and date_end >= today_date)

    @api.multi
    def unlink(self):
        for ct1 in self:
            ct1.with_context(avoid_recursion=True).current = self.get_is_contract_current(ct1.date_start, ct1.date_end)
        return super(RemListingContract, self).unlink()

    @api.multi
    def write(self, vals):
        ct = super(RemListingContract, self).write(vals)
        for ct1 in self:
            if not self._context.get('avoid_recursion', False):
                ct1.with_context(avoid_recursion=True).current = self.get_is_contract_current(ct1.date_start, ct1.date_end)
        return ct

    @api.model
    def create(self, vals):
        res = super(RemListingContract, self).create(vals)
        res.update({'current': self.get_is_contract_current(vals['date_start'], vals['date_end'])})
        return res


class RemListingContract(models.Model):
    _name = 'rem.listing.contract'
    _description = 'Listing Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread', 'ir.needaction_mixin']

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'auto_renew' in init_values and self.auto_renew:
            return 'rem.mt_listing_created'
        return super(RemListingContract, self)._track_subtype(init_values)

    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    type_id = fields.Many2one('rem.listing.contract.type', string='Type', required=True)
    partner_id = fields.Many2one(related='unit_id.partner_id', string='Seller')
    commission = fields.Float(string='Commission', help="For percent enter a ratio between 0-100.")
    ordering = fields.Integer('Ordering Field', default=1)
    # TODO: scheduled action for auto renewal or just trigger when unit is read

    @api.multi
    @api.constrains('date_start', 'period')
    def _check_dates(self):
        contracts = self.search([('unit_id', '=', self.unit_id.id)])
        for ct in contracts:
            if ct.id != self.id:
                if ct.date_end > self.date_start:
                    raise ValidationError(_('The last contract date for this unit is %s. please chose a following start date.') % ct.date_end)

    @api.model
    def default_get(self, flds):
        rec = super(RemListingContract, self).default_get(flds)
        unit_id = rec.get('unit_id', False)
        max_date = False
        if unit_id:
            contracts = self.search([('unit_id', '=', unit_id)])
            for ct in contracts:
                max_date = max(max_date, ct.date_end)

        rec.update({'date_start': max_date or fields.Date.context_today(self)})
        return rec


class RemBuyerContract(models.Model):
    _name = 'rem.buyer.contract'
    _description = 'Buyer Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread', 'ir.needaction_mixin']

    type_id = fields.Many2one('rem.buyer.contract.type', string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)


class RemTenantContract(models.Model):
    _name = 'rem.tenant.contract'
    _description = 'Buyer Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread', 'ir.needaction_mixin']

    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    type_id = fields.Many2one('rem.tenant.contract.type', string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Tenant', required=True)

    def update_current_unit(self, unit_id, **kwargs):
        contracts = self.with_context(avoid_recursion=True).search([('unit_id', '=', unit_id)])
        today_date = fields.Date.today()
        for ct in contracts:
            flag = (ct.date_start <= today_date and ct.date_end >= today_date)
            ct.current = flag

    @api.multi
    def unlink(self):
        for ct1 in self:
            self.update_current_unit(ct1.unit_id.id)
        return super(RemTenantContract, self).unlink()

    @api.multi
    def write(self, vals):
        ct = super(RemTenantContract, self).write(vals)
        for ct1 in self:
            if not self._context.get('avoid_recursion', False):
                self.update_current_unit(ct1.unit_id.id)
        return ct
