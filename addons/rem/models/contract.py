# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError, UserError
from docutils.parsers.rst.directives import flag


class RemAbstractContractType(models.AbstractModel):
    _name = 'rem.abstract.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    code = fields.Char(string='Short Code', size=5, required=True, help="The contracts will be named using this prefix.")
    notes = fields.Text(string='Description', help='Brief description.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')
    sale_product_id = fields.Many2one('product.product', string='Sale Product', required=True)


class RemTenantContractType(models.Model):
    _name = 'rem.tenant.contract.type'
    _description = 'Tenant Agreement Type'
    _inherit = ['rem.abstract.contract.type']

    sale_product_id = fields.Many2one(default=lambda self: self.env.ref('rem.product_rem_rentservice'),
                                      domain=lambda self: [('uom_id.category_id.id', '=', self.env.ref('rem.uom_categ_rentime').id)])


class RemBuyerContractType(models.Model):
    _name = 'rem.buyer.contract.type'
    _description = 'Buyer Agreement Type'
    _inherit = ['rem.abstract.contract.type']

    sale_product_id = fields.Many2one(default=lambda self: self.env.ref('rem.product_rem_brokerservice'))


class RemListingContractType(models.Model):
    _name = 'rem.listing.contract.type'
    _description = 'Listing Agreement Type'
    _inherit = ['rem.abstract.contract.type']

    sale_product_id = fields.Many2one(default=lambda self: self.env.ref('rem.product_rem_brokerservice'))


class RemAbstractContract(models.AbstractModel):
    _name = 'rem.abstract.contract'
    _description = 'Abstract Contract'
    _order = "date_start desc"

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

    type_id = fields.Many2one('rem.abstract.contract.type', string='Type', required=True)
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
    current = fields.Boolean(string='Current Contract', compute='_compute_current',
                             help='This contract is the current one for this unit?')

    def get_date_end(self, date_start, period, unit):
        if unit == 'months':
            return datetime.strptime(date_start + ' 00:00:00',
                                     DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=period)
        else:
            return datetime.strptime(date_start + ' 00:00:00',
                                     DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=period)

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
            if rec.date_end:
                if rec.notice_period_unit == 'months':
                    date_calc = datetime.strptime(rec.date_end + ' 00:00:00',
                                                  DEFAULT_SERVER_DATETIME_FORMAT) + relativedelta(months=rec.notice_period)
                else:
                    date_calc = datetime.strptime(rec.date_end + ' 00:00:00',
                                                  DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=rec.notice_period)
            rec.notice_date = date_calc

    def get_is_contract_current(self, date_start=False, date_end=False):
        today_date = fields.Date.today()
        return (date_start <= today_date and date_end >= today_date)

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def _compute_current(self):
        for ct in self:
            ct.current = self.get_is_contract_current(ct.date_start, ct.date_end)


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
    commission = fields.Float(string='Commission', help="For percent enter a ratio between 0-100.", default=5)
    ordering = fields.Integer('Ordering Field', default=1)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.listing.contract')], string='Attachments')
    # TODO: scheduled action for auto renewal

    @api.multi
    @api.constrains('date_start', 'period', 'period_unit')
    def _check_dates(self):
        for ct1 in self:
            contracts = self.search([('unit_id', '=', ct1.unit_id.id), ('id', '!=', ct1.id)])
            maxdate = False
            mindate = False
            for ct in contracts:
                maxdate = max(maxdate, ct.date_end) if maxdate else ct.date_end
                mindate = min(mindate, ct.date_start) if mindate else ct.date_start
            if ct1.date_start < maxdate and ct1.date_end > mindate:
                raise ValidationError(_('The first contract start date for this unit is %s.\n'
                                        'The last contract end date for this unit is %s.\n'
                                        'Please chose a prior or next start-end period for this contract.') % (mindate, maxdate))

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
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.buyer.contract')], string='Attachments')


class RemTenantContract(models.Model):
    _name = 'rem.tenant.contract'
    _description = 'Buyer Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread', 'ir.needaction_mixin']

    @api.multi
    @api.depends('order_ids_count', 'order_ids')
    def _sale_order_count(self):
        for ctr in self:
            ctr.order_ids_count = len(ctr.order_ids)

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def name_get(self):
        units = []
        for rec in self:
            if rec.date_start and rec.period and rec.period_unit:
                name = "%s %s - %s %s" % (rec.partner_id.name,
                                          rec.date_start, rec.period, rec.period_unit)
            units.append((rec.id, name))
        return units

    allday = fields.Boolean('All Day', default=True)
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    type_id = fields.Many2one('rem.tenant.contract.type', string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Tenant', required=True)
    reservation = fields.Boolean(string='Reservation', default=False,
                                 help='Check if this is a reservation')
    deposit = fields.Float(string='Deposit', help="For percentage for deposit.", default=30)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.tenant.contract')], string='Attachments')
    order_ids_count = fields.Integer(compute='_sale_order_count')
    order_ids = fields.Many2many('sale.order', 'sale_order_tenant_ctr_rel', 'order_id', 'ctr_id', string='Sale Orders')

    def get_rates_and_qtts(self, ctr):

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        date_start = datetime.strptime(ctr.date_start + ' 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)
        date_end = datetime.strptime(ctr.date_end + ' 00:00:00', DEFAULT_SERVER_DATETIME_FORMAT)

        renttime_categ = self.env.ref('rem.uom_categ_rentime')
        uom_day = self.env.ref('rem.product_rent_day').id
        uom_week = self.env.ref('rem.product_rent_week').id
        uom_month = self.env.ref('rem.product_rent_month').id

#         if ctr.type_id.sale_product_id.categ_id.id != renttime_categ.id:
#             raise UserError(_('Contract type "%s", sale product "%s" unit of\n'
#                               'measure must in the "%s" UoM category.') %
#                             (ctr.type_id.display_name, ctr.type_id.sale_product_id.name, renttime_categ.name))

        if ctr.unit_id.table_id:
            print "___________", date_start, date_end
            for single_date in daterange(date_start, date_end):
                print single_date.strftime("%Y-%m-%d")
        else:

            qtt = (date_end - date_start).days
            
            res = {
                'product_id': ctr.type_id.sale_product_id.id,
                'qtt': qtt,
                'uom': ctr.unit_id.rent_uom_id.id,
                'price': ctr.unit_id.rent_price
            }
            return [res]

    @api.multi
    def get_sale_orders(self):
        contract_ids = []
        for ctr in self:
            contract_ids.append(ctr.id)
        return {
            'name': _('Sales Orders'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,kanban,form,calendar,pivot,graph',
            'res_model': 'sale.order',
            'domain': [('tenant_contract_ids', 'in', contract_ids)],
            'context': {'default_tenant_contract_ids': contract_ids}
        }

    @api.multi
    def create_sale_order(self):
        action = self.env.ref('sale.action_quotations')
        edit_form_action = action.read()[0]
        for ctr in self:
            qtt_rate_lines = self.get_rates_and_qtts(ctr)
            order = {
                'partner_id': self.partner_id.id,
                'partner_invoice_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id,
                'tenant_contract_ids': [(6, 0, [ctr.id])],
            }

            lines = []
            for ln in qtt_rate_lines:
                prod = self.env['product.product'].browse(ln['product_id'])
                lines.append((0, 0, {
                    'name': prod.name,
                    'product_id': prod.id,
                    'product_uom_qty': ln['qtt'],
                    'product_uom': ln['uom'],
                    'price_unit': ln['price'],
                }))

            order.update({'order_line': lines})
            so = self.env['sale.order'].create(order)

            edit_form_action['views'] = [(False, 'form')]
            edit_form_action['res_id'] = so.id
            return edit_form_action

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
