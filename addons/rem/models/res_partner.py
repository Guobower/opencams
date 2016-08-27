from openerp import models, fields, api
from __builtin__ import True


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('unit_ids')
    def _unit_count(self):
        for partner in self:
            partner.update({
                'unit_count': len(partner.unit_ids)
            })

    @api.depends('buyer_contract_ids')
    def _buyer_contract_count(self):
        for partner in self:
            partner.update({
                'buyer_contract_count': len(partner.buyer_contract_ids)
            })

    is_neighbor = fields.Boolean('Is a Neighbor', help="Check this box if this contact is a neighbor.")
    buyer = fields.Boolean('Buyer', help="Check this box if this contact is a buyer.")
    seller = fields.Boolean('Seller', help="Check this box if this contact is a seller.")
    tenant = fields.Boolean('Tenant', help="Check this box if this contact is a tenant.")
    unit_count = fields.Integer(compute='_unit_count')
    unit_ids = fields.One2many('rem.unit', 'partner_id', string='Unit(s)')
    buyer_contract_count = fields.Integer(compute='_buyer_contract_count')
    buyer_contract_ids = fields.One2many('rem.buyer.contract', 'partner_id', string='Contract(s)')

    @api.multi
    def write(self, vals):
        for ct1 in self:
            # if an existing contact gets new type of contract
            # gets marked as respective seller, buyer, tenant
            if self._context.get('default_tenant', False):
                vals['tenant'] = True
            if self._context.get('default_buyer', False):
                vals['buyer'] = True
            if self._context.get('default_seller', False):
                vals['seller'] = True
        res = super(ResPartner, self).write(vals)
        return res
