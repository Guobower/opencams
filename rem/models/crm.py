# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime

MATCH_RE = {
    'self.planned_revenue': {'max_planned_revenue': 'self.planned_revenue * 0.1 + self.planned_revenue'},
    'self.re_offer_type_id': {'search_default_offer_type_id': 'self.re_offer_type_id.id'},
    'self.re_type': {'search_default_type_id': 'self.re_type.ids[0]'},
    'self.re_city': {'search_default_city_id': 'self.re_city.id'},
    'self.re_is_new': {'search_default_is_new': 'self.re_is_new'},
}


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planned_revenue = fields.Float('Client Budget', track_visibility='always')

    re_offer_type_id = fields.Many2one(
        'offer.type', string='Offer Type')
    re_type = fields.Many2many('rem.unit.type', string='Property Type')
    re_city = fields.Many2one(
        'rem.unit.city', string='City', help='place in order of gratest zone e.g. US, CA, Los Angeles, Beverly Hills')
    re_is_new = fields.Boolean(string='Is New', help='Active if you want to search for units new.')

    unit_ids = fields.Many2many('rem.unit', 'crm_lead_rem_unit_rel1', 'unit_id', 'lead_id', string='Units')
    re_reason = fields.Many2one('reason.for.buy', string='Reason for Buy')

    @api.multi
    def action_schedule_meeting(self):
        for lead in self:
            res1 = super(CrmLead, self).action_schedule_meeting()
            res1['context'].update({
                'default_unit_ids': lead.unit_ids.ids,
            })
            return res1

    @api.multi
    def action_find_matching_units(self):
        context = dict(self._context or {})
        for conditions in MATCH_RE:
            if eval(conditions):
                for key, val in MATCH_RE[conditions].iteritems():
                    context[key] = eval(val)
        context['from_lead_id'] = self.id
        res = {
            'name': _('Search results'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'rem.unit',
            'context': context,
        }

        return res

    @api.multi
    def action_stage_history(self):
        return {
            'name': _('Get stage history'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form,graph',
            'res_model': 'stage.history',
            'domain': "[('lead_id','=',active_id)]",
        }

    @api.multi
    def write(self, vals):
        if 'stage_id' in vals:
            for lead in self:
                stage_history = self.env['stage.history']
                stage_history.create({
                    'lead_id': lead.id,
                    'stage_id': lead.stage_id.id,
                    'date': datetime.datetime.now(),
                    'new_stage': vals.get('stage_id'),
                    'user_id': self._uid,
                })
        return super(CrmLead, self).write(vals)


class CrmStage(models.Model):
    _inherit = 'crm.stage'

    @api.model
    def rename_crm_stages(self):
        stages = self.env['crm.stage'].search([('id', '<', 5)])
        for stage in stages:
            if stage.id == 1:
                stage.update({'name': 'Showing', 'sequence': 1})
            elif stage.id == 2:
                stage.update({'name': 'Offer submitted', 'sequence': 2})
            elif stage.id == 3:
                stage.update({'name': 'Pending', 'sequence': 3})
            elif stage.id == 4:
                stage.update({'name': 'Closed', 'sequence': 4})


class StageHistory(models.Model):
    _name = 'stage.history'
    _rec_name = 'create_date'
    _order = 'create_date'

    new_stage = fields.Many2one('crm.stage', 'To Stage')
    stage_id = fields.Many2one('crm.stage', 'From Stage')
    date = fields.Datetime('Date Time', default=lambda self: fields.Datetime.now(), readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson')
    lead_id = fields.Many2one('crm.lead', 'Lead')
