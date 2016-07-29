from openerp import models, fields, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.depends('unit_ids')
    def _unit_count(self):
        for partner in self:
            partner.update({
                'unit_count': len(partner.unit_ids)
            })

    is_neighbor = fields.Boolean('Is a Neighbor', help="Check this box if this contact is a neighbor.")
    buyer = fields.Boolean('Buyer', help="Check this box if this contact is a buyer.")
    seller = fields.Boolean('Seller', help="Check this box if this contact is a seller.")
    unit_count = fields.Integer(compute='_unit_count')
    unit_ids = fields.One2many('rem.unit', 'partner_id', string='Unit(s)')
