# -*- coding: utf-8 -*-
import json
import urllib
from lxml import etree
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from openerp.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
from openerp.osv import expression
from openerp.tools.translate import html_translate

import openerp.addons.decimal_precision as dp


class RemUnitFavorite(models.Model):
    _name = 'rem.unit.favorite'
    _description = 'Favorite'

    user_id = fields.Many2many(
        'res.users', 'rem_unit_favorite_res_users_rel', 'rem_unit_favorite_id', 'res_user_id')
    unit_id = fields.Many2many(
        'rem.unit', 'rem_unit_favorite_res_rem_unit_rel', 'rem_unit_favorite_id', 'rem_unit_id')


class RemUnitCity(models.Model):
    _name = 'rem.unit.city'
    _description = 'Unit City'

    name = fields.Char(
        string='City Name', size=32, required=True, help='City Name.')
    state_id = fields.Many2one('res.country.state', string='Federal States', required=False)
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUnitStreet(models.Model):
    _name = 'rem.unit.street'
    _description = 'Unit Street'

    name = fields.Char(
        string='Street Name', size=32, required=True, help='Street Name.')
    city_id = fields.Many2one('rem.unit.city', string='City', required=False)
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUnitZip(models.Model):
    _name = 'rem.unit.zip'
    _description = 'Unit Zip'

    name = fields.Char(
        string='Zip Name', size=32, required=True, help='Zip Name.')
    street_id = fields.Many2one('rem.unit.street', string='Street', required=False)
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUniType(models.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    notes = fields.Text(string='Notes', help='Description of the type.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUnitZone(models.Model):
    _name = 'rem.unit.zone'
    _description = 'Unit Zone'

    name = fields.Char(
        string='Zone Name', size=32, required=True, help='Zone Name.')
    city_id = fields.Many2one('rem.unit.city', string='Unit City', required=False)
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class OfferTypeFields(models.Model):
    _name = 'offer.type.fields'
    _description = 'Offer Type Fields'

    name = fields.Char(string='Key', required=True)
    description = fields.Char(string='Field Name', size=32)


class RemUnitOfferType(models.Model):
    _name = 'offer.type'
    _inherit = ['website.seo.metadata', 'website.published.mixin']
    _description = 'Offer Type'

    name = fields.Char(string='Offer Name', size=32, required=True,
                       help='Type of offer : renting, buying, selling ..')
    sequence = fields.Integer(string='Sequence')
    is_rent = fields.Boolean(string='Is Rentable', default=False,
                             help='Set if the offer type is rent based. This will make the Unit of Rent '
                             'appear in the unit (e.g.: per month, per week..).')
    notes = fields.Text(string='Notes', help='Notes for the offer type.')
    active = fields.Boolean(string='Active', default=True, help='If the active field is set to False, it will '
                            'allow you to hide without removing it.')
    stage_id = fields.One2many('rem.unit.stage', 'offer_type_id', string='Stage Name', ondelete='restrict')
    showfields_ids = fields.Many2many('offer.type.fields', 'offer_type_rem_unit_fields_rel', 'offe_type_id', 'field_id', string="Show Fields")
    hidefields_ids = fields.Many2many('offer.type.fields', 'offer_type_rem_unit_fields_hide_rel', 'offe_type_id', 'field_id', string="Hide Fields")


class RemUnitStage(models.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'
    _order = "offer_type_id,sequence,id"

    name = fields.Char(
        string='Stage Name', size=32, required=True, help='Stage Name.')
    force_show = fields.Boolean(string='Force Show', default=False,
                                help='Set if the stage is a standby stage (e.g. refurbishing or data entry ..)')
    force_hide = fields.Boolean(string='Force Hide', default=False,
                                help='Set if the stage is a final stage (e.g. sold or out of market ..)')
    sequence = fields.Integer(
        string='Sequence', help='Used to order stages. Lower is better.')
    notes = fields.Text(string='Notes', help='Description of the stage.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide the analytic journal without removing it.')
    offer_type_id = fields.Many2one(
        'offer.type', string='Contract Type', required=False)
    # TODO: what could happen to the units if some stage (with units assigned) is deactivated?


class ReasonForBuy(models.Model):
    _name = 'reason.for.buy'
    _description = 'Reason for Buy'

    name = fields.Char(string='Reason for Buy', size=32,
                       required=True, help='Reason for Buy')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class LocationPreferences(models.Model):
    _name = 'location.preferences'
    _description = 'Location Preferences'

    name = fields.Char(string='Location Preferences', size=32,
                       required=True, help='Location Preferences')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class NeighborhoodContacts(models.Model):
    _name = 'rem.neighborhood'
    _description = 'Neighborhood Contact List'

    sequence = fields.Integer(required=True, default=1,
                              help="The sequence field is used to define order in which the tax lines are applied.")
    comment = fields.Char(string='Comment', size=32,
                          required=True, help='Comment')
    is_neighbor = fields.Boolean(default=True)
    partner_id = fields.Many2one('res.partner', string='Neighbor')
    email = fields.Char(string="Email", related='partner_id.email')
    phone = fields.Char(string="Phone", related='partner_id.phone')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class SeasonalRates(models.Model):
    _name = 'season.rates'
    _description = 'Seasonal Rates'

    unit_ids = fields.One2many('rem.unit', 'table_id', string='Units')
    name = fields.Char(string='Name', size=32, required=True,
                       help='Discount table name, e.g. Summer 2029')
    line_ids = fields.One2many('season.rates.line', 'table_id', string='Table Lines')

    def calculate_unit_price(self, price, discount, fixed):
        if fixed == 0:
            return price * ((100.0 - discount) / 100)
        return fixed

    def get_unit_price(self, unit, date=fields.Date.today()):
        unit_rent = unit.rent_price
        for table in self:
            lin = False
            for line in table.line_ids:
                if date > line.date_start and date < line.date_end and lin is False:
                    lin = line
            if lin:
                unit_rent = self.calculate_unit_price(unit_rent, lin.discount, lin.fixed_price)
        return unit_rent

    def format_season_dates(self, date):
        return datetime.strptime(str(date), '%Y-%m-%d').strftime("%d %b %Y")


class PriceTableLine(models.Model):
    _name = 'season.rates.line'
    _description = 'Rent Discount Table Line'

    name = fields.Char(string='Name', size=32, required=True,
                       help='Season name, e.g. Highest/High/Shoulder/Low/Lowest Seasons')
    table_id = fields.Many2one('season.rates', string='Rent Table', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    discount = fields.Float(string='Discount', help="For percent enter a ratio between 0-100.")
    fixed_price = fields.Float(string='Fixed Price', digits=dp.get_precision('Product Price'))

    @api.multi
    @api.constrains('date_start', 'date_end', 'discount', 'fixed_price')
    def _check_dates(self):
        for line in self:
            if line.date_start > line.date_end:
                raise ValidationError(_('Start date cannot be older then the end date.'))
            if line.discount == 0 and line.fixed_price == 0:
                raise ValidationError(_('Enter a discount or product price.'))
            if line.discount < 0 or line.discount > 100:
                raise ValidationError(_('Discount ratio must be between 0-100.'))
            if line.fixed_price < 0:
                raise ValidationError(_('Product Price must be positive.'))
        self.check_if_season_rates_table_has_overlaping_dates(self.table_id.id)

    def dates_are_overlaping(self, i_date_start, i_date_end, j_date_start, j_date_end):
        latest_start = max(datetime.strptime(i_date_start, '%Y-%m-%d'), datetime.strptime(j_date_start, '%Y-%m-%d'))
        earliest_end = min(datetime.strptime(i_date_end, '%Y-%m-%d'), datetime.strptime(j_date_end, '%Y-%m-%d'))
        if ((earliest_end - latest_start).days + 1) > 0:
            return True
        return False

    def check_if_season_rates_table_has_overlaping_dates(self, table_id):
        lines = self.env['season.rates.line'].search([('table_id', '=', table_id)])
        dates = []
        for line in lines:
            dates.append((line.id, line.date_start, line.date_end))
        for i in range(len(dates)):
            for j in range(len(dates)):
                if dates[i][0] == dates[j][0]:
                    continue;
                if self.dates_are_overlaping(dates[i][1], dates[i][2], dates[j][1], dates[j][2]):
                    raise ValidationError(_('The following dates are overlaping: %s until %s and %s until %s') % (dates[i][1], dates[i][2], dates[j][1], dates[j][2]))


class RemImage(models.Model):
    _name = 'rem.image'
    _description = 'Unit Image'
    _order = 'sequence, id'

    name = fields.Char(string='Unit', size=32, required=True,
                       help='Unit description (like house near riverside).')
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        'Image', attachment=True, help='Unit image, limited to 1024x1024px.')
    image_medium = fields.Binary('Medium-sized image', compute='_compute_images', inverse='_inverse_image_medium',
                                 store=True, attachment=True)
    image_small = fields.Binary('Small-sized image', compute='_compute_images', inverse='_inverse_image_small',
                                store=True, attachment=True)
    sequence = fields.Integer(
        index=True, help='Gives the sequence order when displaying the images.', default=16)

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(
                rec.image, size=(512, 512), avoid_if_small=True)
            rec.image_small = tools.image_resize_image_small(
                rec.image, size=(256, 256))

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


class RemUnit(models.Model):
    _inherit = ['website.seo.metadata', 'website.published.mixin']
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    def get_formated_name(self, rec, mask):
        STREET = (rec.street or '').upper()
        STREET2 = (rec.street2 or '').upper()
        CITY = (rec.city_id.name or '').upper()
        STATE = (rec.state_id.code or '').upper()
        try:
            res = mask.format(
                street=rec.street,
                STREET=STREET,
                street2=rec.street2 or '',
                STREET2=STREET2,
                city=rec.city_id.name or '',
                CITY=CITY,
                state=rec.state_id.code or '',
                STATE=STATE,
                zip=rec.zip or '',
                bedrooms=rec.bedrooms or 0,
                bathrooms=rec.bathrooms or 0,
                living_area=rec.living_area or 0,
                land_area=rec.land_area or 0,
            )
        except:
            res = _("Parsing ERROR - Check your name format in Listing >> Settings")
        return res

    @api.model
    def _get_stage(self):
        return self.env['rem.unit.stage'].search([('offer_type_id', '=', False)], limit=1, order='sequence')

    @api.model
    def _get_default_offer_type(self):
        return self.env['offer.type'].search([], limit=1, order='id')

    @api.one
    def add_feature(self):
        max_feature_units = self.pool.get('ir.config_parameter').get_param(self.env.cr, self.env.uid, 'max_feature_units')

        self.env.cr.execute('SELECT COUNT(rem_unit_id) AS total FROM rem_unit_res_users_rel WHERE res_user_id=%s LIMIT 1',
                            [self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if int(max_feature_units) == 0 or int(feature_units['total']) < int(max_feature_units):
                self.feature_id = [(4, self.env.uid)]
                self.is_featured = True
            else:
                raise exceptions.ValidationError(
                    'You can only have %s Feature Units.' % max_feature_units)
        return True

    @api.one
    def remove_feature(self):
        self.feature_id = [(3, self.env.uid)]
        return True

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('reference', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&'] + domain
        units = self.search(domain + args, limit=limit)
        return units.name_get()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        if context.get('max_planned_revenue'):
            args += [('price', '<=', context.get('max_planned_revenue'))]
        if context.get('min_garages'):
            args += [('garages', '>=', context.get('min_garages'))]
        if context.get('max_bedrooms') and context.get('min_bedrooms'):
            args += [('bedrooms', '<=', context.get('max_bedrooms')) and ('bedrooms', '>=', context.get('min_bedrooms'))]
        if context.get('min_bathrooms'):
            args += [('bathrooms', '>=', context.get('min_bathrooms'))]
        if context.get('min_living_areas'):
            args += [('livingArea', '>=', context.get('min_living_areas'))]
        return super(RemUnit, self).search(args, offset, limit, order, count=count)

    @api.one
    def _get_company_currency(self):
        if self.company_id:
            self.currency_id = self.sudo().company_id.currency_id
        else:
            self.currency_id = self.env.user.company_id.currency_id

    @api.depends('current_listing_contract_id', 'listing_contract_ids')
    def _get_current_listing_contract(self):
        for unit in self:
            contracts = self.env['rem.listing.contract'].search([('unit_id', '=', unit.id), ('current', '=', True)], limit=1)
            for ct in contracts:
                unit.update({
                    'current_listing_contract_id': ct.id,
                })

    @api.depends('current_tenant_contract_id', 'tenant_contract_ids')
    def _get_current_tenant_contract(self):
        for unit in self:
            contracts = self.env['rem.tenant.contract'].search([('unit_id', '=', unit.id), ('current', '=', True)], limit=1)
            for ct in contracts:
                unit.update({
                    'current_tenant_contract_id': ct.id,
                })

    @api.multi
    @api.depends('listing_contract_count', 'listing_contract_ids')
    def _listing_contract_count(self):
        for unit in self:
            unit.listing_contract_count = len(unit.listing_contract_ids)

    @api.multi
    @api.depends('tenant_contract_count', 'tenant_contract_ids')
    def _tenant_contract_count(self):
        for unit in self:
            unit.tenant_contract_count = len(unit.tenant_contract_ids)

    @api.multi
    @api.depends('event_ids_count', 'event_ids')
    def _event_count(self):
        for unit in self:
            unit.event_ids_count = len(unit.event_ids)

    @api.multi
    @api.depends('image_ids', 'lead_ids')
    def _get_main_image(self):
        for unit in self:
            id = False
            res = False
            if unit.id:
                self.env.cr.execute('SELECT id FROM rem_image WHERE unit_id=%s '
                                    'ORDER BY sequence asc, id asc LIMIT 1;', [unit.id])
                res = self.env.cr.dictfetchone()
                if res:
                    id = int(res['id'])
                    res = self.env['rem.image'].search_read([('id', '=', id)])[0]['image_medium']
            unit.main_img = res
            unit.main_img_id = id

    @api.multi
    @api.depends('stage_id', 'current_listing_contract_id.date_start',
                 'current_listing_contract_id.period', 'current_listing_contract_id.period_unit',
                 'current_tenant_contract_id.date_start', 'current_tenant_contract_id.period',
                 'current_tenant_contract_id.period_unit',)
    def _check_active(self):
        for unit in self:
            flag = False
            date_now = fields.Date.today()
            if (unit.current_listing_contract_id.date_start <= date_now and
                    unit.current_listing_contract_id.date_end >= date_now):
                flag = True

            if (unit.current_tenant_contract_id.date_start <= date_now and
                    unit.current_tenant_contract_id.date_end >= date_now):
                flag = True

            if unit.stage_id.force_show:
                unit.active = True
                continue
            if unit.stage_id.force_hide:
                unit.active = False
                continue

            if len(unit.listing_contract_ids) == 0:
                flag = True
            unit.active = flag

    @api.multi
    def _context_has_lead_id(self):
        lead_id = int(self._context.get('from_lead_id', False))
        for unit in self:
            unit.has_lead_id = (lead_id in unit.lead_ids.ids)

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def name_get(self):
        units = []
        unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_name_format')
        for rec in self:
            name = self.get_formated_name(rec, unit_name_format)
            units.append((rec.id, name))
        return units

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def _compute_name(self):
        unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_name_format')
        for rec in self:
            name = self.get_formated_name(rec, unit_name_format)
            rec.name = name

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip', 'bedrooms',
                 'bathrooms', 'living_area', 'land_area')
    def _get_website_name(self):
        units = []
        unit_websitename_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_websitename_format')
        for rec in self:
            name = self.get_formated_name(rec, unit_websitename_format)
            units.append((rec.id, name))
        return units

    @api.multi
    @api.depends('table_id', 'rent_price', 'rent_uom_id')
    def _get_current_rent(self):
        today_date = fields.Date.today()
        for unit in self:
            if unit.table_id:
                unit.rent_current_price = unit.table_id.get_unit_price(unit, today_date)
            else:
                unit.rent_current_price = unit.rent_price

    @api.one
    def get_geo_coordinates(self):
        coordinates = geo_find(
            geo_query_address(
                street=self.street,
                zip=self.zip,
                city=self.city_id.name,
                state=self.state_id.name,
                country=self.country_id.name,
            )
        )

        if coordinates:
            self.latitude = coordinates[0]
            self.longitude = coordinates[1]

    def _default_uom(self):
        uom_categ_id = self.env.ref('rem.uom_categ_rentime').id
        return self.env['product.uom'].search([('category_id', '=', uom_categ_id), ('factor', '=', 1)], limit=1)

    @api.depends('order_ids')
    def _compute_orders(self):
        for unit in self:
            orders = self.env['sale.order'].search([('tenant_contract_ids', 'in', unit.tenant_contract_ids.ids)])
            unit.order_ids = orders.ids

    @api.multi
    @api.depends('order_ids_count', 'order_ids')
    def _sale_order_count(self):
        for unit in self:
            unit.order_ids_count = len(unit.order_ids)

    offer_type_id = fields.Many2one('offer.type', string='Offer Type', required=True,
                                    default=_get_default_offer_type)
    type_id = fields.Many2one('rem.unit.type', string='Type')
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    reference = fields.Char(string='Reference', default=lambda self: self.env['ir.sequence'].next_by_code('rem.unit.sl'),
                            copy=False, readonly=True, index=True)
    website_name = fields.Char(compute='_get_website_name', string='Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Owner', help="Owner of the unit")
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    active = fields.Boolean(compute='_check_active',
                            store=True, default=True,
                            help='An inactive unit will not be listed in the'
                            ' back-end nor in the Website. Active field depends'
                            ' on the stage and on the current contract start and end date')
    currency_id = fields.Many2one('res.currency', string='Currency', compute='_get_company_currency', readonly=True)
    # TODO: make user_id not required, but change contact form for having a default agent defined in res_config
    user_id = fields.Many2one('res.users', string='Salesperson', required=True, default=lambda self: self.env.user)
    is_rent = fields.Boolean(related='offer_type_id.is_rent', string='Is Rentable', store=True)
    price = fields.Float(string='Sale Price', digits=dp.get_precision('Product Price'))

    # Rental
    table_id = fields.Many2one('season.rates', string='Discount Table', help="Season price table that sets"
                               " discounts on the base rent price or fixed values for unit types or"
                               " with the same category")
    rent_price = fields.Float(string='Rent Rate', digits=dp.get_precision('Product Price'))
    rent_uom_id = fields.Many2one('product.uom', string='Rent Unit', default=_default_uom)
    rent_current_price = fields.Float(string='Current Rent Rate', compute='_get_current_rent',
                                      help="Current rent rate, based on the Season price table defined for this unit"
                                      " or unit type and the current date", digits=dp.get_precision('Product Price'))
    rent_current_uom_id = fields.Many2one('product.uom', related="rent_uom_id", string='Rent Unit', readonly=True)
    rent_min = fields.Float(string='Minimal Period', digits=dp.get_precision('Product Price'))
    rent_min_uom_id = fields.Many2one('product.uom', string='Period Unit', default=_default_uom)

    # Leads and Events
    event_ids = fields.Many2many('calendar.event', 'crm_lead_calendar_rel1', 'cal_id', 'unit_id', string='Show Units',
                                 help="Appointment / meetings related to this unit")
    event_ids_count = fields.Integer(compute='_event_count')
    lead_ids = fields.Many2many('crm.lead', 'crm_lead_rem_unit_rel1', 'lead_id', 'unit_id', string='Leads')
    has_lead_id = fields.Boolean(compute='_context_has_lead_id')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic',
                                          help='Link this asset to an analytic account.')
    order_ids_count = fields.Integer(compute='_sale_order_count')
    order_ids = fields.Many2many('sale.order', compute='_compute_orders', string='Units', readonly=True)

    image_ids = fields.One2many(
        'rem.image', 'unit_id', string='Photos', ondelete='cascade')
    main_img = fields.Binary('Main Image', compute='_get_main_image', attachment=True, store=True)
    main_img_id = fields.Integer('Main Image ID', compute='_get_main_image')
    feature_id = fields.Many2many(
        'res.users', 'rem_unit_res_users_rel', 'rem_unit_id', 'res_user_id')
    is_featured = fields.Boolean(string='Is Featured', default=False)
    is_new = fields.Boolean(string='Is New', default=True,
                            help='If the field is new is set to False, the unit is considered used.')
    website_description = fields.Html(string='Description', sanitize=False, translate=html_translate)
    stage_id = fields.Many2one(
        'rem.unit.stage', string='Stage', default=_get_stage)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'rem.unit')], string='Attachments')
    neighborhood_id = fields.One2many('rem.neighborhood', 'comment', string='Neighborhood Contact List')
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get('rem.unit'))

    # Listing contracts
    listing_contract_count = fields.Integer(compute='_listing_contract_count')
    listing_contract_ids = fields.One2many('rem.listing.contract', 'unit_id', string='Listing Contracts')
    current_listing_contract_id = fields.Many2one('rem.listing.contract', string='Current Contract',
                                                  compute='_get_current_listing_contract',)

    # Tenant contracts
    tenant_contract_count = fields.Integer(compute='_tenant_contract_count')
    tenant_contract_ids = fields.One2many('rem.tenant.contract', 'unit_id', string='Rent Contracts')
    current_tenant_contract_id = fields.Many2one('rem.tenant.contract', string='Current Contract',
                                                 compute='_get_current_tenant_contract',)

    # Location
    street = fields.Char(string='Street', required=True)
    street2 = fields.Char(string='Street2')
    zone_id = fields.Many2one('rem.unit.zone', string='Zone')
    city_id = fields.Many2one('rem.unit.city', string='City', required=True)
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    zip = fields.Char(string='Zip', change_default=True, size=24, required=True)

    # General Features
    bedrooms = fields.Integer(
        string='Bedrooms', default=1, required=True)
    bathrooms = fields.Integer(
        string='Bathrooms', default=1, required=True)
    toilets = fields.Integer(
        string='Toilets', default=1, required=True)
    living_area = fields.Float('Living Area', default=0)
    land_area = fields.Float('Land Area', default=0)
    points_interest = fields.Many2many(
        'location.preferences', string='Points of Interest')

    # Indoor Features
    # TODO: check if area is being used, it's not being used on backend (unit -> indoor features)
    area = fields.Float(string='Area', default=0, required=True)
    airConditioning = fields.Boolean(string='Air Conditioned', default=False)
    ducted_cooling = fields.Boolean(string='Ducted Cooling', default=False)
    builtInRobes = fields.Boolean(string='Built-in Wardrobes', default=False)
    dishwasher = fields.Boolean(string='Dishwasher', default=False)
    livingArea = fields.Float('Living Areas', default=0)

    # Outdoor Features
    garages = fields.Integer(
        string='Garage Spaces', default=0, required=True)
    backyard = fields.Boolean(string='Backyard', default=False)
    dog_friendly = fields.Boolean(string='Dog Friendly', default=False)
    secure_parking = fields.Boolean(string='Secure Parking', default=False)
    alarmSystem = fields.Boolean(string='Alarm System', default=False)
    swpool = fields.Boolean(string='Swimming Pool', default=False)
    entertaining = fields.Boolean(string='Outdoor Entertaining Area', default=False)

    # Geo
    latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    longitude = fields.Float(string='Geo Longitude', digits=(16, 5))

    balconies = fields.Integer(string='Balconies')

#     councilRates = fields.Float(string='Annual council rates')
#     secureParking = fields.Boolean(string='Secure parking')
#     broadband = fields.Boolean(string='Broadband Internet')
#     recreationRoom = fields.Boolean(string='Recreation Room')
#     gym = fields.Boolean(string='Gym')
#     payTV = fields.Boolean(string='Pay TV')
#     ductedHeating = fields.Boolean(string='Ducted Heating')
#     ductedCooling = fields.Boolean(string='Ducted Cooling')
#     splitsystemHeating = fields.Boolean(string='Split-System Heating')
#     hydronicHeating = fields.Boolean(string='Hydronic Heating')
#     splitsystemAircon = fields.Boolean(string='Split-System Air Conditioning')
#     gasHeating = fields.Boolean(string='Gas Heating')
#     reverseCycleAircon = fields.Boolean(string='Reverse Cycle Air Conditioning')
#     evaporativeCooling = fields.Boolean(string='Evaporative Cooling')
#     vacuumSystem = fields.Boolean(string='Built-in ducted vacuum system')
#     intercom = fields.Boolean(string='Intercom')
#     poolInGround = fields.Boolean(string='Inground swimming pool')
#     poolAboveGround = fields.Boolean(string='Above ground swimming pool')
#     spa = fields.Boolean(string='Spa')
#     tennisCourt = fields.Boolean(string='Tennis court')
#     deck = fields.Boolean(string='Deck')
#     courtyard = fields.Boolean(string='Courtyard')
#     outdoorEnt = fields.Boolean(string='Outdoor entertaining area')
#     shed = fields.Boolean(string='Shed')
#     fullyFenced = fields.Boolean(string='Fence around the full perimeter')
#     openFirePlace = fields.Boolean(string='')
#     insideSpa = fields.Boolean(string='Open fire place')
#     outsideSpa = fields.Boolean(string='Spa outside the house')
#     waterTank = fields.Boolean(string='Water tank')

    # anualReturn = fields.Char(string='Annual rate of return in percentage')
    # rentPerSquareMetre = fields.Char(string='Rent per square metre per annum')
    # buildingDetails = fields.Char(string='Information about the physical structure of the building')
    # externalLink = fields.Char(string='Link to other material')
    # 
    # site = fields.Char(string='Name or site of the commercial listing')
    # improvements = fields.Char(string='Improvements made')
    # 
    #
    # carryingCapacity = fields.Char(string='Stock carrying capacity')
    # 
    # annualRainfall = fields.Char(string='Annual rain fall')
    # 
    # videoLink = fields.Char(string='Link to a video display of the listing')
    # vendorDetails = fields.Char(string='Contact details for the vendor')
    # linkedInURL = fields.Char(string='LinkedIn profile page of a listing agent')
    # facebookURL = fields.Char(string='Facebook page of a listing agent')
    # twitterURL = fields.Char(string='Twitter profile of a listing agent')
    # terms = fields.Char(string='Sale terms of the property')
    # municipality = fields.Char(string='Local administrative entity')
    # outgoings = fields.Char(string='Expenses incurred in generating income')
    # soilTypes = fields.Char(string='Services supplied')
    #
    # remoteGarage = fields.Boolean(string='Remotely controlled garage door')
    #
    # study = fields.Boolean(string='Study')
    #
    # workshop = fields.Boolean(string='Workshop')
    #
    # floorboards = fields.Boolean(string='Floorboards')


    # solarHotWater = fields.Boolean(string='Solar hot water')
    # solarPanels = fields.Boolean(string='Solar panels')
    # petFriendly = fields.Boolean(string='Allow pets')

    # greyWaterSystem = fields.Boolean(string='Hrey water system')
    # furnished = fields.Boolean(string='Is furnished')
    # crossOver = fields.Boolean(string='Cross over is present on a vacant block of land')

    # ensuite = fields.Integer(string='Ensuites')
    # carports = fields.Integer(string='Car spaces')
    # openSpaces = fields.Integer(string='Car spaces available on the entire property')
    # heating = fields.Selection([
    #     ('Gas', _('Gas')),
    #     ('Electric', _('Electric')),
    #     ('GDH', _('GDH')),
    #     ('Solid', _('Solid')),
    #     ('Other', _('Other'))],
    #     string="Type of heating")
    # hotWaterService = fields.Selection([
    #     ('Gas', _('Gas')),
    #     ('Electric', _('Electric')),
    #     ('Solar', _('Solar'))],
    #     string="Type of hot water")
    # views = fields.Selection([
    #     ('City', _('City')),
    #     ('Water', _('Water')),
    #     ('Valley', _('Valley')),
    #     ('Mountain', _('Mountain')),
    #     ('Ocean', _('Ocean'))],
    #     string="Views available from the property")
    # tax = fields.Selection([
    #     ('Unknown', _('Unknown')),
    #     ('Exempt', _('Exempt')),
    #     ('Inclusive', _('Inclusive')),
    #     ('Exclusive', _('Exclusive'))],
    #     string="Sale Tax", default="Unknown")
    # idealFor = fields.Selection([
    #     ('firstHomeBuyer', _('First home buyer')),
    #     ('investors', _('Investors')),
    #     ('downsizing', _('Downsizing')),
    #     ('couples', _('Couples')),
    #     ('students', _('Students')),
    #     ('lrgFamilies', _('Large families')),
    #     ('reitrees', _('Reitrees'))],
    #     string="Suitable for")
    # ruralCategory = fields.Selection([
    #     ('Cropping', _('Cropping')),
    #     ('Dairy', _('Dairy')),
    #     ('Farmlet', _('Farmlet')),
    #     ('Horticulture', _('Horticulture')),
    #     ('Lifestyle', _('Lifestyle')),
    #     ('Livestock', _('Livestock')),
    #     ('Viticulture', _('Viticulture')),
    #     ('MixedFarming', _('MixedFarming')),
    #     ('Other', _('Other'))],
    #     string="Principal agricultural focus")

    @api.model
    def add_custom_offer_type_fields_while_updating_module(self):
        self._cr.execute("""
        DELETE FROM offer_type_fields where name ilike 'x_%';
        DELETE FROM ir_model_data where name ilike 'offer_type_cfield_%';
        """)
        for fld in self.env['ir.model.fields'].sudo().search([('state', '=', 'manual'),
                                                              ('model', '=', 'rem.unit')]):
            rec = self.env['offer.type.fields'].sudo().create({
                'name': fld.name,
                'description': fld.field_description,
            })
            self.env['ir.model.data'].sudo().create({
                'name': 'offer_type_cfield_' + fld.name,
                'model': 'offer.type.fields',
                'module': 'rem',
                'res_id': rec.id,
                'noupdate': True
            })

    @api.model
    def add_custom_fields_while_updating_module(self):
        rem_form_id = self.env.ref('rem.view_rem_unit_form').id
        for rem_form in self.env['ir.ui.view'].sudo().browse(rem_form_id):
            doc = etree.XML(rem_form.arch_base)
            for node in doc.xpath("//group[@name='general_features']"):
                grpl = node.xpath(".//group[@class='rem_left']")[0]
                grpr = node.xpath(".//group[@class='rem_right']")[0]
                for fld in self.env['ir.model.fields'].sudo().search([('state', '=', 'manual'),
                                                                      ('model', '=', 'rem.unit'),
                                                                      ('rem_category', '=', 'general')]):
                    nd = etree.Element("field", name=fld.name, invisible="1")
                    if grpl.xpath('count(.//field)') >= grpr.xpath('count(.//field)'):
                        grpr.append(nd)
                    else:
                        grpl.append(nd)
            for node in doc.xpath("//group[@name='indoor_features']"):
                grpl = node.xpath(".//group[@class='rem_left']")[0]
                grpr = node.xpath(".//group[@class='rem_right']")[0]
                for fld in self.env['ir.model.fields'].sudo().search([('state', '=', 'manual'),
                                                                      ('model', '=', 'rem.unit'),
                                                                      ('rem_category', '=', 'indoor')]):
                    nd = etree.Element("field", name=fld.name, invisible="1")
                    if grpl.xpath('count(.//field)') >= grpr.xpath('count(.//field)'):
                        grpr.append(nd)
                    else:
                        grpl.append(nd)
            for node in doc.xpath("//group[@name='outdoor_features']"):
                grpl = node.xpath(".//group[@class='rem_left']")[0]
                grpr = node.xpath(".//group[@class='rem_right']")[0]
                for fld in self.env['ir.model.fields'].sudo().search([('state', '=', 'manual'),
                                                                      ('model', '=', 'rem.unit'),
                                                                      ('rem_category', '=', 'outdoor')]):
                    nd = etree.Element("field", name=fld.name, invisible="1")
                    if grpl.xpath('count(.//field)') >= grpr.xpath('count(.//field)'):
                        grpr.append(nd)
                    else:
                        grpl.append(nd)
            rem_form.arch_base = etree.tostring(doc)

    @api.model
    def fields_view_get(self, view_id=None, view_type=None, toolbar=False, submenu=False):
        res = super(RemUnit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            if self._context.get('offer_type'):
                offer = self.env['offer.type'].sudo().search([('id', '=', self._context.get('offer_type'))])
                for fld in offer.showfields_ids:
                    for node in doc.xpath("//field[@name='%s']" % fld.name):
                        node.set('invisible', '0')
                        node.set('modifiers', '')
                for fld in offer.hidefields_ids:
                    for node in doc.xpath("//field[@name='%s']" % fld.name):
                        node.set('invisible', '1')
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def action_select_unit(self):
        for unit in self:
            lead_id = int(self._context.get('from_lead_id', False))
            unit.lead_ids = [(6, 0, list(set(self.lead_ids.ids) | set([lead_id])))]

    @api.multi
    def action_remove_unit(self):
        for unit in self:
            lead_id = int(self._context.get('from_lead_id', False))
            unit.lead_ids = [(6, 0, list(set(self.lead_ids.ids) - set([lead_id])))]

    @api.multi
    def get_sale_orders(self):
        for unit in self:
            return {
                'name': _('Sales Orders'),
                'type': 'ir.actions.act_window',
                'view_mode': 'tree,kanban,form,calendar,pivot,graph',
                'res_model': 'sale.order',
                'domain': [('tenant_contract_ids', 'in', unit.tenant_contract_ids.ids)],
            }

    @api.multi
    def get_unit_events(self):
        unit_ids = []
        for unit in self:
            unit_ids.append(unit.id)
        return {
            'name': _('Appointments/Meetings'),
            'type': 'ir.actions.act_window',
            'view_mode': 'calendar,tree,form',
            'res_model': 'calendar.event',
            'domain': [('unit_ids', 'in', unit_ids)],
            'context': {'default_unit_ids': unit_ids, 'default_duration': 4.0}
        }

    @api.onchange('offer_type_id')
    def _onchange_offer_type_id(self):
        if self.offer_type_id:
            ids = self.env['rem.unit.stage'].search(
                [('offer_type_id', '=', self.offer_type_id.id)], order='sequence, id').ids
            if ids:
                self.stage_id = ids[0]
            else:
                self.stage_id = False