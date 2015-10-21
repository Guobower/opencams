# -*- coding: utf-8 -*-

import logging

from openerp import tools, api, fields, models, _
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


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

    name = fields.Char(string='Unit', size=32, required=True, help="Unit description (like house near riverside).")
    active = fields.Boolean(string='Active', default=True, help="If the active field is set to False, it will allow you to hide the analytic journal without removing it.")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Contract/Analytic', help="Link this asset to an analytic account.")
    stage_id = fields.Many2one('rem.unit.stage', string='Stage', select=True, default=_get_stage)
    user_id = fields.Many2one('res.users', string='Salesman', required=False)
    bedrooms = fields.Integer(string='Number of bedrooms', default=1, required=True)
    bathrooms = fields.Integer(string='Number of bathrooms', default=1, required=True)
    garages = fields.Integer(string='Number of garages', default=0, required=True)
    area = fields.Integer(string='Area', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    contract_type_id = fields.Many2one('contract.type', string='Contract Type', required=True)
    # image_ids = fields.Many2many('rem.image', 'rem_image_rel', 'rem_id', 'image_id', string='Photo')
    image_ids = fields.One2many('rem.image', 'unit_id', string='Photos')
