# -*- coding: utf-8 -*-

import logging


from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)


class rem_unit_type(osv.Model):
    _name = "rem.unit.type"
    _description = "Unit Type"
    
    _columns = {
        'name': fields.char('Name', size=32, help="Stage Name"),
        'note': fields.text('Notes', help="Description of the stage"),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the analytic journal without removing it."),
    }
    _defaults = {
        'active': True,
    }


class rem_unit_stage(osv.Model):
    _name = "rem.unit.stage"
    _description = "Unit Stage"
    
    _columns = {
        'name': fields.char('Name', size=32, help="Stage Name"),
        'sequence': fields.integer('Sequence', help="Used to order stages. Lower is better."),
        'note': fields.text('Note', help="Description of the stage"),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the analytic journal without removing it."),
    }
    _defaults = {
        'active': True,
    }
    
    
class rem_unit(osv.Model):
    _name = "rem.unit"
    _description = "Real Estate Unit"

    _columns = {
        'name': fields.char('Unit', size=32, help="Unit description, like (house near riverside)"),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Contract/Analytic',
                                               help="Link this asset to an analytic account."),
        'active': fields.boolean('Active', help="If the active field is set to False, it will allow you to hide the analytic journal without removing it."),
        'stage_id': fields.many2one('rem.unit.stage', 'Stage', select=True),
        'user_id': fields.many2one('res.users', 'Salesman', required=False),
        'bedrooms': fields.integer('Number of beadrooms'),
        'bathrooms': fields.integer('Number of bathrooms'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    
    _defaults = {
        'active': True,
        'bedrooms': 1,
        'bathrooms': 1,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.id,
    }
    