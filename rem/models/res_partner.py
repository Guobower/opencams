from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('unit_ids')
    def _unit_count(self):
        for partner in self:
            partner.update({
                'unit_count': len(partner.unit_ids)
            })

    unit_count = fields.Integer(compute='_unit_count')
    unit_ids = fields.One2many('rem.unit', 'owner_id', string='Unit(s)')
