# -*- coding: utf-8 -*-
from odoo import tools, api, fields, models, _
from odoo import exceptions
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError
from docutils.parsers.rst.directives import flag
from .utils import RentDate
import pytz


class RemAbstractContractType(models.AbstractModel):
    _name = 'rem.abstract.contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    code = fields.Char(string='Short Code', size=5, required=True,
                       help="The contracts will be named using this prefix.")
    notes = fields.Text(string='Description', help='Brief description.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')
    sale_product_id = fields.Many2one('product.product', string='Sale Product', required=True)


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
            if rec.date_start and rec.period and rec.period_unit.name:
                name += " %s - %s %s" % (rec.date_start, rec.period,
                                         rec.period_unit.name[4:] + 's' if rec.period > 1 else rec.period_unit.name[4:])
            units.append((rec.id, name))
        return units

    def _default_uom(self):
        uom_categ_id = self.env.ref('rem.uom_categ_rentime').id
        return self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1,
                                              order="factor")

    type_id = fields.Many2one('rem.abstract.contract.type', string='Type', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', compute='_compute_date_end', store=True)
    auto_invoice = fields.Boolean(string='Auto Invoice?', default=True,
                                  help='Check for automatic invoice')
    auto_renew = fields.Boolean(string='Auto Renew?', default=False,
                                help='Check for automatic renew for same period and log in the chatter')
    notice_date = fields.Date('Notice Date', compute='_compute_date_notice', )
    period = fields.Integer('Period', default=1, required=True)
    period_unit = fields.Many2one('product.uom', string='Period Unit', default=_default_uom, required=True)
    notice_period = fields.Integer('Notice Period', default=15)
    notice_period_unit = fields.Many2one('product.uom', string='Period Unit', default=_default_uom)
    current = fields.Boolean(string='Current Contract', compute='_compute_current',
                             search='_search_current', help='This contract is the current one for this unit?')

    def _search_current(self, operator, value):
        self._do_search_current('rem_abstract_contract', operator, value)

    def _do_search_current(self, table_name, operator, value):
        contracts = []
        ids = []
        tools = RentDate(env=self.env)
        if (operator == '=' and value == True) or (operator in ('<>', '!=') and value == False):
            query = """
                SELECT id
                FROM """ + str(table_name) + """
                WHERE date_start <= now() AND
                      (
                        (date_start + interval '1 day' * period >= now() AND period_unit = '""" + str(
                tools.uom_month.id) + """') OR
                        (date_start + interval '1 month' * period >= now() AND period_unit = '""" + str(
                tools.uom_month.id) + """')
                      )
                """
        else:
            query = """
                SELECT id
                FROM """ + str(table_name) + """
                WHERE date_start > now() OR
                      (date_start + interval '1 day' * period < now() AND period_unit = '""" + str(tools.uom_day.id) + """') OR
                      (date_start + interval '1 month' * period < now() AND period_unit = '""" + str(
                tools.uom_month.id) + """')
                """
        self.env.cr.execute(query)
        for ct in self.env.cr.dictfetchall():
            ids.append((ct['id']))
        contracts.append(('id', 'in', ids))
        return contracts

    def _get_date(self, date_start_end, period, period_unit_id):
        if not date_start_end:
            return False
        if period_unit_id == RentDate(env=self.env).uom_month.id:
            return datetime.strptime(date_start_end, DEFAULT_SERVER_DATE_FORMAT) + relativedelta(months=period)
        else:
            return datetime.strptime(date_start_end, DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=period)

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def _compute_date_end(self):
        for rec in self:
            rec.date_end = self._get_date(rec.date_start, rec.period, rec.period_unit.id)

    @api.multi
    @api.depends('date_start', 'notice_period', 'notice_period_unit')
    def _compute_date_notice(self):
        for rec in self:
            rec.notice_date = self._get_date(rec.date_start, rec.notice_period, rec.notice_period_unit.id)

    @api.multi
    @api.depends('date_start', 'date_end')
    def _compute_current(self):
        for ct in self:
            ct.current = self.is_current_contract(ct.date_start, ct.date_end)

    def is_current_contract(self, date_start=False, date_end=False):
        today_date = fields.Date.today()
        return (date_start <= today_date and date_end >= today_date)


class RemTenantContractType(models.Model):
    _name = 'rem.tenant.contract.type'
    _description = 'Tenant Agreement Type'
    _inherit = ['rem.abstract.contract.type']

    sale_product_id = fields.Many2one(default=lambda self: self.env.ref('rem.product_rem_rentservice'),
                                      domain=lambda self: [
                                          ('uom_id.category_id.id', '=', self.env.ref('rem.uom_categ_rentime').id)])


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


class RemListingContract(models.Model):
    _name = 'rem.listing.contract'
    _description = 'Listing Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread']

    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    type_id = fields.Many2one('rem.listing.contract.type', string='Type', required=True)
    partner_id = fields.Many2one(related='unit_id.partner_id', string='Seller')
    listing_price = fields.Monetary(string='Listing Price', default=0.0, currency_field='company_currency_id')
    fee = fields.Float(string='Fee', help="For percent enter a ratio between 0-100.", default=5)
    fee_amount = fields.Monetary(string='Fee Amount', default=0.0, currency_field='company_currency_id')
    ordering = fields.Integer('Ordering Field', default=1)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.listing.contract')],
                                     string='Attachments')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True,
                                          help='Utility field to express amount currency', store=True)
    company_id = fields.Many2one('res.company', related='unit_id.company_id', string='Company', store=True)

    # TODO: scheduled action for auto renewal

    @api.onchange('listing_price', 'fee')
    def _onchange_fee(self):
        if self.fee != 0:
            self.fee_amount = self.fee * self.listing_price

    @api.onchange('fee_amount')
    def _onchange_fee_amount(self):
        if self.fee_amount > 0 and self.listing_price > 0:
            self.fee = self.fee_amount / self.listing_price

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'auto_renew' in init_values and self.auto_renew:
            return 'rem.mt_listing_created'
        return super(RemListingContract, self)._track_subtype(init_values)

    def _search_current(self, operator, value):
        self._do_search_current('rem_listing_contract', operator, value)

    @api.multi
    @api.constrains('date_start', 'date_end')
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
                                        'Please chose a prior or next start-end period for this contract.') % (
                                      mindate, maxdate))

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
    _inherit = ['rem.abstract.contract', 'mail.thread']

    type_id = fields.Many2one('rem.buyer.contract.type', string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Buyer', required=True)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.buyer.contract')],
                                     string='Attachments')


class RemTenantContract(models.Model):
    _name = 'rem.tenant.contract'
    _description = 'Buyer Contract'
    _inherit = ['rem.abstract.contract', 'mail.thread']

    name = fields.Char('Contract Name')
    allday = fields.Boolean('All Day', default=True)
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    type_id = fields.Many2one('rem.tenant.contract.type', string='Type', required=True)
    partner_id = fields.Many2one('res.partner', string='Tenant', required=True)
    reservation = fields.Boolean(string='Reservation', default=False,
                                 help='Check if this is a reservation')
    deposit = fields.Float(string='Deposit', help="For percentage for deposit.", default=30)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.tenant.contract')],
                                     string='Attachments')
    order_ids_count = fields.Integer(compute='_sale_order_count')
    order_ids = fields.Many2many('sale.order', 'sale_order_tenant_ctr_rel', 'order_id', 'ctr_id', string='Sale Orders')
    invoice_ids = fields.Many2many('account.invoice', compute='_get_invoice_ids', string='Invoices', readonly=True)
    invoice_ids_count = fields.Integer(compute='_invoice_count')
    parent_id = fields.Integer('Parent Contract')
    child_id = fields.Integer('Child Contract')

    @api.model
    def create(self, vals):
        # Calculate contract end date and remove ' 00:00:00' time from date
        vals['date_end'] = str(self._get_date(vals['date_start'], vals['period'], vals['period_unit']))[:-9]

        if 'date_start' not in vals:
            vals['date_start'] = self.env.context['default_unit_id']

        # Check if dates are overlapping
        # (date_start_x <= date_end_y) and (date_end_x >= date_start_y)
        contract = self.env['rem.tenant.contract'].search([
            ('unit_id', '=', vals['date_start']),
            ('date_start', '<=', vals['date_end']),
            ('date_end', '>=', vals['date_start'])
        ], limit=1)

        if contract:
            raise ValidationError(_('The following dates are overlapping: %s until %s and %s until %s') % (
            vals['date_start'], vals['date_end'], contract[0].date_start, contract[0].date_end))

        return super(RemTenantContract, self).create(vals)

    @api.multi
    def write(self, vals):
        for tenant_contract in self:
            # Check if dates are overlapping
            # (date_start_x <= date_end_y) and (date_end_x >= date_start_y)
            if 'date_start' in vals or 'period' in vals or 'period_unit' in vals:
                if 'date_start' not in vals:
                    vals['date_start'] = tenant_contract.date_start
                if 'period' not in vals:
                    vals['period'] = tenant_contract.period
                if 'period_unit' not in vals:
                    vals['period_unit'] = tenant_contract.period_unit.id

                # Calculate contract end date and remove ' 00:00:00' time from date
                vals['date_end'] = str(self._get_date(vals['date_start'], vals['period'], vals['period_unit']))[:-9]

                contract = self.env['rem.tenant.contract'].search([
                    ('id', '!=', tenant_contract.id),
                    ('unit_id', '=', tenant_contract.unit_id.id),
                    ('date_start', '<=', vals['date_end']),
                    ('date_end', '>=', vals['date_start'])
                ], limit=1)

                if contract:
                    raise ValidationError(_('The following dates are overlapping: %s until %s and %s until %s') % (
                    vals['date_start'], vals['date_end'], contract[0].date_start, contract[0].date_end))

        ct = super(RemTenantContract, self).write(vals)
        for ct1 in self:
            if not self._context.get('avoid_recursion', False):
                self.update_current_unit(ct1.unit_id.id)
        return ct

    @api.multi
    def unlink(self):
        for ct1 in self:
            self.update_current_unit(ct1.unit_id.id)
        return super(RemTenantContract, self).unlink()

    @api.multi
    @api.depends('order_ids')
    def _sale_order_count(self):
        for ctr in self:
            ctr.order_ids_count = len(ctr.order_ids)

    @api.multi
    @api.depends('order_ids.invoice_ids')
    def _invoice_count(self):
        for ctr in self:
            ctr.invoice_ids_count = len(ctr.invoice_ids)

    @api.multi
    @api.depends('date_start', 'period', 'period_unit')
    def name_get(self):
        units = []
        for rec in self:
            if rec.partner_id.name and rec.date_start and rec.period and rec.period_unit.name:
                name = "%s %s - %s %s" % (rec.partner_id.name,
                                          rec.date_start, rec.period,
                                          rec.period_unit.name[4:] + 's' if rec.period > 1 else rec.period_unit.name[
                                                                                                4:])
                units.append((rec.id, name))
        return units

    @api.depends('order_ids.invoice_ids')
    def _get_invoice_ids(self):
        for ctr in self:
            ctr.invoice_ids = list(set([oid for order in ctr.order_ids for oid in order.invoice_ids.ids]))

    def _search_current(self, operator, value):
        self._do_search_current('rem_tenant_contract', operator, value)

    @api.multi
    def create_sale_order(self):
        action = self.env.ref('sale.action_quotations')
        edit_form_action = action.read()[0]
        for ctr in self:
            # lines = []
            # for ln in self.get_rates_and_qtts(ctr):
            # lines.append((0, 0, {
            #     'name': ln['name'],
            #     'product_id': ln['product_id'],
            #     'product_uom_qty': ln['qtt'],
            #     'product_uom': ln['uom'],
            #     'price_unit': ln['price'],
            # }))

            so = self.env['sale.order'].create(
                self._create_sale_order_dict(ctr)
            )

            edit_form_action['views'] = [(False, 'form')]
            edit_form_action['res_id'] = so.id
            return edit_form_action

    def _create_sale_order_dict(self, ctr):
        order = {
            'partner_id': ctr.partner_id.id,
            'partner_invoice_id': ctr.partner_id.id,
            'partner_shipping_id': ctr.partner_id.id,
            'tenant_contract_ids': [(6, 0, [ctr.id])],
        }

        line = [(0, 0, {
            # TODO: get date_start and date_end with res.lang.date_format format
            'name': 'From ' + ctr.date_start + ' to ' + ctr.date_end,
            'product_id': ctr.type_id.sale_product_id.id,
            'product_uom_qty': ctr.period,
            'product_uom': ctr.period_unit.id,
            'price_unit': ctr.unit_id.rent_price,
        })]

        order.update({'order_line': line})

        return order

    def get_rates_and_qtts(self, ctr):

        date_start = datetime.strptime(ctr.date_start, DEFAULT_SERVER_DATE_FORMAT)
        date_end = datetime.strptime(ctr.date_end, DEFAULT_SERVER_DATE_FORMAT)

        renttime_categ = self.env.ref('rem.uom_categ_rentime')

        if ctr.type_id.sale_product_id.uom_id.category_id.id != renttime_categ.id:
            raise UserError(_('Contract type "%s", sale product "%s" unit of\n'
                              'measure must in the "%s" UoM category.') %
                            (ctr.type_id.display_name, ctr.type_id.sale_product_id.name, renttime_categ.name))
        else:
            return self.sale_lines(
                date_start, date_end,
                ctr.unit_id.rent_uom_id,
                ctr.unit_id.rent_price,
                ctr.type_id.sale_product_id.id)

    def sale_lines(self, date_start, date_end, rent_uom_id, rent_price, sale_product_id):
        dlt = relativedelta(date_end, date_start)
        qtt = RentDate(env=self.env)
        tz = pytz.timezone(self._context.get('tz') or 'UTC')
        if rent_uom_id.id == qtt.uom_month.id:
            qtt.months = dlt.months + (dlt.years * 12)
            qtt.t_months = "From {:%Y-%d-%m} to {:%Y-%d-%m}".format(
                pytz.utc.localize(date_start).astimezone(tz),
                pytz.utc.localize(date_start + relativedelta(months=qtt.months)).astimezone(tz), )
            qtt.r_months = rent_price
            qtt.days = dlt.days
            qtt.r_days = rent_price / qtt.uom_month.factor_inv
            qtt.t_days = "From {:%Y-%d-%m} to {:%Y-%d-%m}".format(
                pytz.utc.localize(date_start).astimezone(tz),
                pytz.utc.localize(date_start + timedelta(days=qtt.days)).astimezone(tz))

        elif rent_uom_id.id == qtt.uom_week.id:
            qtt.weeks, qtt.days = divmod((date_end - date_start).days, qtt.uom_week.factor_inv)
            qtt.t_weeks = "From {:%Y-%d-%m} to {:%Y-%d-%m}".format(
                pytz.utc.localize(date_start).astimezone(tz),
                pytz.utc.localize(date_start + timedelta(days=qtt.weeks * 7)).astimezone(tz))
            qtt.r_weeks = rent_price
            qtt.r_days = rent_price / qtt.uom_week.factor_inv
            qtt.t_days = "From {:%Y-%d-%m} to {:%Y-%d-%m}".format(
                pytz.utc.localize(date_start).astimezone(tz),
                pytz.utc.localize(date_start + timedelta(days=qtt.days)).astimezone(tz))

        elif rent_uom_id.id == qtt.uom_day.id:
            qtt.days = (date_end - date_start).days
            qtt.t_days = "From {:%Y-%d-%m} to {:%Y-%d-%m}".format(
                pytz.utc.localize(date_start).astimezone(tz),
                pytz.utc.localize(date_start + timedelta(days=qtt.days)).astimezone(tz))
            qtt.r_days = rent_price

        return qtt.get_lines(sale_product_id)

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
    def get_account_invoices(self):
        inv_ids = []
        for ctr in self:
            inv_ids += ctr.invoice_ids.ids
        return {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form,calendar,graph',
            'res_model': 'account.invoice',
            'domain': [('id', 'in', inv_ids)],
        }

    def update_current_unit(self, unit_id, **kwargs):
        contracts = self.with_context(avoid_recursion=True).search([('unit_id', '=', unit_id)])
        today_date = fields.Date.today()
        for ct in contracts:
            flag = (ct.date_start <= today_date and ct.date_end >= today_date)
            ct.current = flag

    @api.model
    def create_invoices_for_auto_invoice_contracts(self):
        # TODO: get a proper account_id
        account_id = 1

        # Get current date
        date_today = datetime.now().strftime("%Y-%m-%d")
        # Get units with rentable offer type
        for unit in self.env['rem.unit'].search([('offer_type_id.is_rent', '=', True)]):
            # Get unit contracts with auto invoice
            for ctr in self.env['rem.tenant.contract'].search([('unit_id', '=', unit.id), ('auto_invoice', '=', True)]):
                # If the contract doesn't have a SO
                if ctr.order_ids_count == 0:
                    # Create SO
                    self.env['sale.order'].create(
                        self._create_sale_order_dict(ctr)
                    )
                # Get contract SOs
                for so in self.env['sale.order'].search([('tenant_contract_ids', '=', ctr.id)]):

                    date_start = ctr.date_start

                    # For each line from top to bottom
                    for line in so.order_line:

                        # Calculate the number of invoices the SOL should have based on the date_start, date_today and product_uom
                        expected_qty_invoiced = self._get_date_diff(ctr.date_start, date_today, line.product_uom.name)

                        # If we have invoices to create
                        if line.qty_invoiced < expected_qty_invoiced:

                            # Quantity to invoice
                            invoice_qty = expected_qty_invoiced - line.qty_invoiced

                            # Create invoice
                            invoice = {
                                'partner_id': ctr.partner_id.id,
                                'partner_shipping_id': ctr.partner_id.id,
                                'tenant_contract_ids': [(6, 0, [ctr.id])],
                                'origin': so.name,
                            }

                            line = [(0, 0, {
                                # TODO: get date_start and date_end with res.lang.date_format format
                                'name': 'From ' + ctr.date_start + ' to ' + ctr.date_end,
                                'product_id': line.product_id.id,
                                'quantity': invoice_qty,
                                'uom_id': line.product_uom.id,
                                'price_unit': line.price_unit,
                                'account_id': account_id,
                            })]

                            invoice.update({'invoice_line_ids': line})

                            new_invoice = self.env['account.invoice'].create(invoice)

                            # Validate invoice
                            new_invoice.action_invoice_open()

                            # Update invoiced quantity on SOL
                            line.update({'qty_invoiced': line.qty_invoiced + invoice_qty})

                            # SOL has more invoices to invoice in the next hour(s)/day(s)/week(s)/month(s)
                            if line.product_uom_qty != expected_qty_invoiced:
                                break

                            # The date_start on the next line will be equal to the contract date_start plus
                            # the amount of hour(s)/day(s)/week(s)/month(s) on the current line
                            # example: 2016-01-01 + 6 months
                            date_start = self._sum_date_with_qty_uom(date_start, line.product_uom_qty,
                                                                     line.product_uom.name)

    @api.model
    def create_auto_renew_contracts(self):
        # Get current date
        date_today = datetime.now().strftime("%Y-%m-%d")
        # Get units with rentable offer type
        for unit in self.env['rem.unit'].search([('offer_type_id.is_rent', '=', True)]):
            # Get unit contracts with auto renew
            for ctr in self.env['rem.tenant.contract'].search(
                    [('unit_id', '=', unit.id), ('auto_renew', '=', True), ('child_id', '=', False)]):
                # If we reached or passed the notice date
                if datetime.strptime(date_today, "%Y-%m-%d").date() > datetime.strptime(ctr.notice_date,
                                                                                        "%Y-%m-%d").date():
                    # Create a new contract based on the current one
                    child = self.env['rem.tenant.contract'].create({
                        'type_id': ctr.type_id.id,
                        'unit_id': ctr.unit_id.id,
                        'partner_id': ctr.partner_id.id,
                        'date_start': str(
                            self._sum_date_with_qty_uom(ctr.date_start, ctr.period, ctr.period_unit.name)),
                        'period': ctr.period,
                        'period_unit': ctr.period_unit.id,
                        'auto_invoice': ctr.auto_invoice,
                        'auto_renew': True,
                        'parent_id': ctr.id,
                    })

                    # Update parent contract with child_id to avoid creating a new renewal for this contract
                    ctr.update({'child_id': child.id})

                    # The new contract may already need a renewal (routine wasn't executed as intended for some reason for a while)
                    self._cr.commit()
                    self.create_auto_renew_contracts()

    def _get_date_diff(self, d1, d2, uom):
        # TODO: 'per Hour' and 'per Week'
        if uom == 'per Day':
            return self._date_diff_in_days(d1, d2)
        else:
            # should be uom == 'per Month'
            return self._date_diff_in_months(d1, d2)

    def _date_diff_in_days(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return abs((d2 - d1).days)

    def _date_diff_in_months(self, d1, d2):
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        return (d2.year - d1.year) * 12 + d2.month - d1.month

    def _sum_date_with_qty_uom(self, date, qty, uom):
        # TODO: 'per Hour' and 'per Week'
        if uom == 'per Day':
            return datetime.strptime(date, "%Y-%m-%d").date() + timedelta(days=qty)
        else:
            # should be uom == 'per Month'
            return datetime.strptime(date, "%Y-%m-%d").date() + relativedelta(months=qty)
