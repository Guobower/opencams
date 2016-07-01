# -*- coding: utf-8 -*-
from openerp import fields, models
import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    unit_lead = fields.Many2many('rem.unit', string='Units')
    

    def write(self, cr, uid, ids, vals, context=None):

		# stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.datetime.now()
        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.datetime.now()
        # stage change with new stage: update probability and date_closed
        if vals.get('stage_id') and 'probability' not in vals:
            onchange_stage_values = self.onchange_stage_id(cr, uid, ids, vals.get('stage_id'), context=context)['value']
            vals.update(onchange_stage_values)
        if vals.get('probability') >= 100 or not vals.get('active', True):
            vals['date_closed'] = fields.datetime.now()
        elif 'probability' in vals and vals['probability'] < 100:
            vals['date_closed'] = False

        if 'stage_id' in vals:
        	lead = self.browse(cr, uid, ids, context)
	        user_obj = self.pool.get('res.users')
	        user_name = user_obj.browse(cr, uid, uid)
	        stage_history = self.pool['stage.history']
	        stage_history.create(cr, uid,{
	        	'stage_id': lead.stage_id.name,
	        	'date': datetime.datetime.now(),
	        	'new_stage': vals.get('stage_id'),
	        	'name': lead.name,
	        	'user_login': user_name.login,
	        	}, context=context)
        
        return super(CrmLead, self).write(cr, uid, ids, vals, context=context)




class StageHistory(models.Model):
    _name = "stage.history"

    new_stage = fields.Many2one(comodel_name='crm.stage')
    stage_id = fields.Char(comodel_name='crm.stage')
    name = fields.Char(comodel_name='crm.lead')
    date = fields.Datetime(comodel_name='crm.lead',string='Date Time')
    user_login = fields.Char(comodel_name='crm.lead')