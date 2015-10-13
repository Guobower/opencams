# -*- coding: utf-8 -*-

import logging


from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class rem_unit_type(osv.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'
    name = fields.Char(
        string='Type Name',
        size=32,
        help='Type Name',
        required=True
    )
    notes = fields.Text(
        string='Notes',
        help='Description of the type'
    )
    active = fields.Boolean(
        string='Active',
        help='If the active field is set to False, it will allow you to hide the analytic journal without removing it',
        default=True
    )


class rem_unit_stage(osv.Model):
    _name = 'rem.unit.stage'
    _description = 'Unit Stage'
    name = fields.Char(
        string='Stage Name',
        size=32,
        help='Stage Name',
        required=True
    )
    sequence = fields.Integer(
        string='Sequence',
        help='Used to order stages. Lower is better',
        required=True
    )
    notes = fields.Text(
        string='Notes',
        help='Description of the stage'
    )
    active = fields.Boolean(
        string='Active',
        help='If the active field is set to False, it will allow you to hide the analytic journal without removing it',
        default=True
    )


class rem_unit(osv.Model):
    _name = 'rem.unit'
    _description = 'Real Estate Unit'
    name = fields.Char(
        string='Unit',
        size=32,
        help='Unit description (like house near riverside)',
        required=True
    )
    active = fields.Boolean(
        string='Active',
        help='If the active field is set to False, it will allow you to hide the analytic journal without removing it',
        default=True
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract/Analytic',
        help='Link this asset to an analytic account'
    )
    stage_id = fields.Many2one(
        comodel_name='rem.unit.stage',
        string='Stage',
        select=True
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Salesman',
        required=False
    )
    bedrooms = fields.Integer(
        string='Number of bedrooms',
        default=1
    )
    bathrooms = fields.Integer(
        string='Number of bathrooms',
        default=1
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id
    )
