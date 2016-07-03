# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import datetime


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    unit_lead = fields.Many2many('rem.unit', string='Units')
    re_rooms = fields.Integer('Bathrooms', help="Number of bathrooms", re_link="bathrooms")
    
    @api.multi
    def action_stage_history(self):
        return {
            'name': _('Get stage history'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'stage.history',
            'domain': "[('lead_id','=',active_id)]",
        }

    def write(self, cr, uid, ids, vals, context=None):
        
        if 'stage_id' in vals:
            lead = self.browse(cr, uid, ids, context)
            stage_history = self.pool['stage.history']
            stage_history.create(cr, uid, {
                'lead_id': lead.id,
                'stage_id': lead.stage_id.id,
                'date': datetime.datetime.now(),
                'new_stage': vals.get('stage_id'),
                'user_id': uid,
            }, context=context)

        return super(CrmLead, self).write(cr, uid, ids, vals, context=context)


class StageHistory(models.Model):
    _name = 'stage.history'
    _rec_name = 'create_date'
    _order = 'date'
    
    new_stage = fields.Many2one('crm.stage', 'To Stage')
    stage_id = fields.Many2one('crm.stage', 'From Stage')
    date = fields.Datetime('Date Time', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson')
    lead_id = fields.Many2one('crm.lead', 'Lead')
