# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import datetime

MATCH_RE = {
    're_contract_type_id': 'contract_type_id',
    're_type': 'type_id',
    're_rooms': 'rooms',
    're_bathrooms': 'bathrooms',
    're_reason': 'reason'
}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    unit_lead = fields.Many2many('rem.unit', string='Units')

    re_contract_type_id = fields.Many2one(
        'contract.type', string='Contract Type')
    re_type = fields.Many2many('rem.unit.type', string='Property Type')
    re_rooms = fields.Integer('Rooms', help="Number of rooms")
    re_bathrooms = fields.Integer(
        'Bathrooms', help="Number of bathrooms", re_field='bathrooms')
    #re_datemovein = fields.Date('Deadline', help="Move in deadline for customer", default=lambda self: self._context.get('date', fields.Date.context_today(self)))
    re_zone = fields.Char(
        'Zone', help="place in order of gratest zone e.g. US, CA, Los Angeles, Beverly Hills")
    re_reason = fields.Many2one('reason.for.buy', string='Reason for Buy')
    re_living_area = fields.Float('Living Area')
    re_land_area = fields.Float('Land Area')

    @api.multi
    def action_find_matching_units(self):
        # TODO: implement search
        return False

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
    date = fields.Datetime(
        'Date Time', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson')
    lead_id = fields.Many2one('crm.lead', 'Lead')
