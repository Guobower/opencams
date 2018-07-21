from odoo import models, fields, api, _


class RemUniType(models.Model):
    _name = 'rem.unit.type'
    _description = 'Unit Type'

    name = fields.Char(string='Type Name', size=32,
                       required=True, help='Type Name.')
    sequence = fields.Integer(
        string='Sequence', help='Used to order stages. Lower is better.')
    notes = fields.Text(string='Notes', help='Description of the type.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_formated_name(self, rec, mask):
        STREET = (rec.street or '').upper()
        STREET2 = (rec.street2 or '').upper()
        CITY = (rec.city or '').upper()
        STATE = (rec.state_id.code or '').upper()
        try:
            res = mask.format(
                street=rec.street,
                STREET=STREET,
                street2=rec.street2 or '',
                STREET2=STREET2,
                city=rec.city or '',
                CITY=CITY,
                state=rec.state_id.code or '',
                STATE=STATE,
                zip=rec.zip or '',
            )
        except:
            res = _("Parsing ERROR - Check your name format in Listing >> Settings")
        return res

    @api.multi
    @api.depends('street', 'street2', 'city', 'zip', 'state_id',
                 'state_id.name')
    def name_get(self):
        res = []
        for record in self:
            if record.is_unit:
                unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.base_unit_name_format',
                                                                                    '{street} {street2}, {city}, {state} {zip}')
                name = self.get_formated_name(record, unit_name_format)
            else:
                name = super(ResPartner, self).name_get()[0][1]
            res.append((record.id, name))
        return res


    # Home Owners
    is_home_owner = fields.Boolean(string="Is Home Owner?")
    unit_count = fields.Integer(compute='_unit_count')
    unit_ids = fields.One2many('res.partner', 'owner_id', string='Unit(s)')

    # Units
    is_unit = fields.Boolean(string="Is Unit?")
    type_id = fields.Many2one('rem.unit.type', string='Type')
    owner_id = fields.Many2one('res.partner', string='Current Owner', help="Owner of the unit",
                               domain=[('is_home_owner', '=', True)])

    # Related Owner
    u_title = fields.Many2one(related='owner_id.title', help="This field is stored in the Owner file")
    u_function = fields.Char(related='owner_id.function', help="This field is stored in the Owner file")
    u_email = fields.Char(related='owner_id.email', help="This field is stored in the Owner file")
    u_phone = fields.Char(related='owner_id.phone', help="This field is stored in the Owner file")
    u_mobile = fields.Char(related='owner_id.mobile', help="This field is stored in the Owner file")
    u_website = fields.Char(related='owner_id.website', help="This field is stored in the Owner file")
    u_vat = fields.Char(related='owner_id.vat', string="TIN", help="This field is stored in the Owner file")

    area = fields.Float(string='Unit Area')
    ownership_percentage = fields.Float(string='Ownership', help="Ownership percentage of the property")
    monthly_fees = fields.Monetary('Monthly Fees')
    special_assessment = fields.Monetary('Special Assessment')
    deed_date = fields.Date('Deed Date', help="Date when the current owner bought this unit.")

    @api.depends('unit_ids')
    def _unit_count(self):
        for partner in self:
            partner.update({
                'unit_count': len(partner.unit_ids)
            })

    # Currency
    # currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    # company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')