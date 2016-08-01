# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from openerp import exceptions
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError


class RemUniCity(models.Model):
    _name = 'rem.unit.city'
    _description = 'Unit City'

    name = fields.Char(
        string='City Name', size=32, required=True, help='City Name.')
    state_id = fields.Many2one('res.country.state', string='Federal States', required=False)
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUniZone(models.Model):
    _name = 'rem.unit.zone'
    _description = 'Unit Zone'

    name = fields.Char(
        string='Zone Name', size=32, required=True, help='Zone Name.')
    city_id = fields.Many2one('rem.unit.city', string='Unit City', required=False)
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


class RemUnitContractType(models.Model):
    _name = 'contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Contract Name', size=32, required=True,
                       help='Type of contract : renting, buying, selling ..')
    sequence = fields.Integer(string='Sequence')
    is_rent = fields.Boolean(string='Is Rentable', default=False,
                             help='Set if the contract type is rent based. This will make the Unit of Rent apear in the unit (e.g.: per month, per week..).')
    notes = fields.Text(string='Notes', help='Notes for the contract type.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class RemUnitStage(models.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'

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
    contract_type_id = fields.Many2one(
        'contract.type', string='Contract Type', required=False)
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

    def _website_url(self, cr, uid, ids, field_name, arg, context=None):
        res = super(RemUnit, self)._website_url(cr, uid, ids, field_name, arg, context=context)
        for unit in self.browse(cr, uid, ids, context=context):
            res[unit.id] = "/rem/unit/%s" % (unit.id,)
        return res

    @api.model
    def _get_stage(self):
        return self.env['rem.unit.stage'].search([('contract_type_id', '=', False)], limit=1, order='sequence')

    @api.model
    def _get_default_contract_type(self):
        return self.env['contract.type'].search([], limit=1, order='id')

    @api.one
    def add_feature(self):
        self.env.cr.execute('SELECT COUNT(rem_unit_id) FROM rem_unit_res_users_rel WHERE res_user_id=%s LIMIT 1',
                            [self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if feature_units['count'] < 5:
                self.feature_id = [(4, self.env.uid)]
            else:
                raise exceptions.ValidationError(
                    'You can only have 5 Feature Units.')
        return True

    @api.one
    def remove_feature(self):
        self.feature_id = [(3, self.env.uid)]
        return True

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env[
                'ir.sequence'].next_by_code('rem.unit') or 'New'
            return super(RemUnit, self).create(vals)

    @api.model
    def _is_featured(self):
        self.env.cr.execute(
            'SELECT COUNT(rem_unit_id) FROM rem_unit_res_users_rel WHERE rem_unit_id=%s AND res_user_id=%s LIMIT 1',
            [self.id, self.env.uid])
        for feature_units in self.env.cr.dictfetchall():
            if feature_units['count'] > 0:
                self.is_featured = 1
            else:
                self.is_featured = 0
        return True

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
            args += [('living_areas', '>=', context.get('min_living_areas'))]

        return super(RemUnit, self).search(args, offset, limit, order, count=count)

    @api.one
    def _get_company_currency(self):
        if self.company_id:
            self.currency_id = self.sudo().company_id.currency_id
        else:
            self.currency_id = self.env.user.company_id.currency_id

    @api.depends('price_rent')
    def _get_rent_rate(self):
        # TODO: implement rent rate depending on season for vacation rental
        pass

    @api.depends('current_contract_id', 'listing_contract_ids')
    def _get_current_contract(self):
        for unit in self:
            curr_ctr = False
            self.env.cr.execute('select id from rem_listing_contract '
                                'where unit_id=%s and current = True;'
                                , [unit.id])
            all_lines = self.env.cr.fetchone()
            if all_lines:
                curr_ctr = all_lines[0]
                unit.update({
                    'current_contract_id': curr_ctr,
                })

    @api.depends('listing_contract_count', 'listing_contract_ids')
    def _listing_contract_count(self):
        for unit in self:
            unit.update({
                'listing_contract_count': len(self.listing_contract_ids)
            })

    @api.one
    @api.depends('stage_id', 'contract_type_id', 'contract_type_id.is_rent')
    def _check_active(self):
        for unit in self:
            res = False
            if self.stage_id.force_show:
                unit.update({'active': True})
                return
            if self.stage_id.force_hide:
                unit.update({'active': False})
                return
            if len(self.listing_contract_ids) == 0:
                unit.update({'active': True})
                return
            date_now = fields.Date.today()
            if (self.current_contract_id.date_start <= date_now and
                    self.current_contract_id.date_end >= date_now):
                res = True
            unit.update({'active': res})

    reference = fields.Char(string='Reference', required=True, copy=False,
                            readonly=True, index=True, default='New')
    partner_id = fields.Many2one('res.partner', string='Owner', help="Owner of the unit")
    user_id = fields.Many2one('res.users', string='Salesman', required=False)
    is_rent = fields.Boolean(related='contract_type_id.is_rent', string='Is Rentable')
    # TODO: implement rent rate depending on season for vacation rental or simple for long term rent
    price_rent = fields.Float(compute='_get_rent_rate', string='Rent Rate', digits=(16, 2))
    rent_unit = fields.Selection([('per_hour', 'per Hour'), ('per_day', 'per Day'), ('per_week', 'per Week'),
                                  ('per_month', 'per Month')], string='Rent Unit', change_default=True,
                                 default=lambda self: self._context.get('rent_unit', 'per_month'))
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    active = fields.Boolean(compute='_check_active', store=True, 
                            help='An inactive unit will not be listed in the'
                            ' back-end nor in the Website. Active field depends'
                            ' on the stage and on the current contract start and end date')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic',
                                          help='Link this asset to an analytic account.')
    image_ids = fields.One2many(
        'rem.image', 'unit_id', string='Photos', ondelete='cascade')
    feature_id = fields.Many2many(
        'res.users', 'rem_unit_res_users_rel', 'rem_unit_id', 'res_user_id')
    is_featured = fields.Boolean(compute=_is_featured, store=False)
    reason = fields.Many2one('reason.for.buy', string='Reason for Buy')
    type_id = fields.Many2one('rem.unit.type', string='Type')
    is_new = fields.Boolean(string='Is New', default=True,
                            help='If the field is new is set to False, the unit is considered used.')
    contract_type_id = fields.Many2one('contract.type', string='Offer Type', required=True,
                                       default=_get_default_contract_type)
    price = fields.Float(string='Sale Price', digits=(16, 2), required=True)
    description = fields.Text(string='Detailed Description', required=True)
    stage_id = fields.Many2one(
        'rem.unit.stage', string='Stage', default=_get_stage)

    currency_id = fields.Many2one('res.currency', string='Currency', compute='_get_company_currency',
                                  readonly=True)
    neighborhood_id = fields.One2many('rem.neighborhood', 'comment', string='Neighborhood Contact List')
    listing_contract_count = fields.Integer(compute='_listing_contract_count')
    listing_contract_ids = fields.One2many('rem.listing.contract', 'unit_id', string='Listing Contracts')
    current_contract_id = fields.Many2one('rem.listing.contract', string='Current Contract',
                                          compute='_get_current_contract',)

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
    living_area = fields.Float('Living Area', default=0)
    land_area = fields.Float('Land Area', default=0)
    points_interest = fields.Many2many(
        'location.preferences', string='Points of Interest')

    # Indoor Features
    # TODO: check if area is being used, it's not being used on backend (unit -> indoor features)
    area = fields.Float(string='Area', default=0, required=True)
    air_conditioned = fields.Boolean(string='Air Conditioned', default=False)
    ducted_cooling = fields.Boolean(string='Ducted Cooling', default=False)
    wardrobes = fields.Boolean(string='Built-in Wardrobes', default=False)
    dishwasher = fields.Boolean(string='Dishwasher', default=False)
    living_areas = fields.Float('Living Areas', default=0)

    # Outdoor Features
    garages = fields.Integer(
        string='Garage Spaces', default=0, required=True)
    backyard = fields.Boolean(string='Backyard', default=False)
    dog_friendly = fields.Boolean(string='Dog Friendly', default=False)
    secure_parking = fields.Boolean(string='Secure Parking', default=False)
    alarm = fields.Boolean(string='Alarm System', default=False)
    sw_pool = fields.Boolean(string='Swimming Pool', default=False)
    entertaining = fields.Boolean(string='Outdoor Entertaining Area', default=False)

    @api.multi
    def action_listing_contracts(self):
        return {
            'name': _('Get listing contracts'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'rem.listing.contract',
            'domain': "[('unit_id','=',active_id)]",
            'context': {'default_unit_id': self.id}
        }

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name', 'city_id.name', 'zip')
    def name_get(self):
        units = []
        unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.unit_name_format')
        for rec in self:
            name = unit_name_format.format(
                street=rec.street,
                street2=rec.street2 or '',
                city=rec.city_id.name or '',
                state=rec.state_id.code or '',
                zip=rec.zip or ''
            )
            units.append((rec.id, name))
        return units
