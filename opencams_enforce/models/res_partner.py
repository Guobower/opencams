from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    violation_count = fields.Integer(compute='_violation_count')
    violation_ids = fields.One2many('cams.violation', 'unit_id', string='Unit(s)')

    @api.depends('violation_ids')
    def _violation_count(self):
        for partner in self:
            partner.update({
                'violation_count': len(partner.violation_ids)
            })
