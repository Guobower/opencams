# -*- coding: utf-8 -*-

import logging

from openerp import tools, api, fields, models

_logger = logging.getLogger(__name__)


class RemUniCity(models.Model):
    _name = 'rem.unit.city'
    _description = 'Unit City'

    name = fields.Char(string='City Name', size=32, required=True, help="City Name.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUniType(models.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string='Type Name', size=32, required=True, help="Type Name.")
    notes = fields.Text(string='Notes', help="Description of the type.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUnitContractType(models.Model):
    _name = 'contract.type'
    _description = 'Contract Type'

    name = fields.Char(string='Contract Name', size=32, required=True, help="Type of contract : renting, selling, selling ..")
    sequence = fields.Integer(string='Sequence')
    is_rent = fields.Boolean(string='Is Rentable', default=False, help="Set if the contract type is rent based. This will make the Unit of Rent apear in the unit (e.g.: per month, per week..).")
    notes = fields.Text(string='Notes', help="Notes for the contract type.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide without removing it.")


class RemUnitStage(models.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'

    name = fields.Char(string='Stage Name', size=32, required=True, help="Stage Name.")
    sequence = fields.Integer(string='Sequence', help="Used to order stages. Lower is better.")
    notes = fields.Text(string='Notes', help="Description of the stage.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")
    contract_type_id = fields.Many2one('contract.type', string='Contract Type', required=False)


class RemImage(models.Model):
    _name = 'rem.image'
    _description = 'Unit Image'
    
    name = fields.Char(string='Unit', size=32, required=True, help="Unit description (like house near riverside).")
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary("Image", attachment=True, help="Unit image, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", compute='_compute_images', inverse='_inverse_image_medium', store=True, attachment=True)
    image_small = fields.Binary("Small-sized image", compute='_compute_images', inverse='_inverse_image_small', store=True, attachment=True)
    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying the images.", default=1)

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(rec.image, size=(512, 512), avoid_if_small=True)
            rec.image_small = tools.image_resize_image_small(rec.image, size=(256, 256))

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


class RemUnit(models.Model):
    _name = 'rem.unit'
    _description = 'Real Estate Unit'

    @api.model
    def _get_stage(self):
        return self.env['rem.unit.stage'].search([('contract_type_id', '=', False)], limit=1, order='sequence')
    
    @api.model
    def _get_default_contract_type(self):
        return self.env['contract.type'].search([], limit=1, order='id')

    @api.one
    def	add_feature(self):
        self.feature_id = [(4, self.env.uid)]
        # n_features = self.env['res.users'].search_count([('res_user_id', '=', self.env.uid),
        #                                                  ('rem_unit_res_users_rel', '=', self.id)])
        # if (n_features < 5):
        #     self.feature_id = [(4, self.env.uid)]
        # else:
        #     raise exceptions.ValidationError("You can only have 5 feature units.")
        return True

    @api.one
    def	remove_feature(self):
        self.feature_id = [(3, self.env.uid)]
        return True

    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('rem.unit') or 'New'
            return super(RemUnit, self).create(vals)

    reference = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default='New')
    name = fields.Char(string='Unit', size=32, required=True, help="Unit description (like house near riverside).")
    is_new = fields.Boolean(string='Is New', default=True, help="If the field is new is set to False, the unit is considered used.")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic', help="Link this asset to an analytic account.")
    stage_id = fields.Many2one('rem.unit.stage', string='Stage', select=True, default=_get_stage)
    user_id = fields.Many2one('res.users', string='Salesman', required=False)
    bedrooms = fields.Integer(string='Number of bedrooms', default=1, required=True)
    bathrooms = fields.Integer(string='Number of bathrooms', default=1, required=True)
    garages = fields.Integer(string='Number of garages', default=0, required=True)
    area = fields.Integer(string='Area', default=0, required=True)
    price = fields.Float(string='Price', digits=(16, 2), required=True)
    rent_unit = fields.Selection([('per_hour', 'per Hour'), ('per_day', 'per Day'), ('per_week', 'per Week'),
                                  ('per_month', 'per Month')], string='Rent Unit', change_default=True, 
                                 default=lambda self: self._context.get('rent_unit', 'per_month'))
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    contract_type_id = fields.Many2one('contract.type', string='Contract Type', required=True, default=_get_default_contract_type)
    city_id = fields.Many2one('rem.unit.city', string='City', select=True)
    is_rent = fields.Boolean(related='contract_type_id.is_rent', string='Is Rentable')
    # image_ids = fields.Many2many('rem.image', 'rem_image_rel', 'rem_id', 'image_id', string='Photo')
    image_ids = fields.One2many('rem.image', 'unit_id', string='Photos', ondelete='cascade')
    feature_id = fields.Many2many('res.users', 'rem_unit_res_users_rel', 'rem_unit_id', 'res_user_id')
