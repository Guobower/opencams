from openerp import models, fields


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_neighbor = fields.Boolean('Is a Neighbor', help="Check this box if this contact is a neighbor.")
    buyer = fields.Boolean('Buyer', help="Check this box if this contact is a buyer.")
    seller = fields.Boolean('Seller', help="Check this box if this contact is a seller.")
