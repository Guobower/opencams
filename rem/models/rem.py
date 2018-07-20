# -*- coding: utf-8 -*-

from odoo import tools, api, fields, models, _
from odoo.addons.base_geolocalize.models.res_partner import geo_find, geo_query_address
import odoo.addons.decimal_precision as dp


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


class RemImage(models.Model):
    _name = 'rem.image'
    _description = 'Unit Image'
    _order = 'sequence, id'

    name = fields.Char(string='Unit', size=32, required=True,
                       help='Unit description (like house near riverside).')
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        'Image', attachment=True, help='Unit image, limited to 1024x1024px.')
    image_medium = fields.Binary('Medium-sized image', compute='_compute_images', inverse='_inverse_image_medium',
                                 store=True, attachment=True)
    image_small = fields.Binary('Small-sized image', compute='_compute_images', inverse='_inverse_image_small',
                                store=True, attachment=True)
    sequence = fields.Integer(
        index=True, help='Gives the sequence order when displaying the images.', default=16)

    @api.depends('image')
    def _compute_images(self):
        for rec in self:
            rec.image_medium = tools.image_resize_image_medium(
                rec.image, size=(512, 512), avoid_if_small=True)
            rec.image_small = tools.image_resize_image_small(
                rec.image, size=(256, 256))

    def _inverse_image_medium(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_medium)

    def _inverse_image_small(self):
        for rec in self:
            rec.image = tools.image_resize_image_big(rec.image_small)


class RemUnit(models.Model):
    _name = 'rem.unit'
    _inherit = 'res.partner'
    _description = 'Real Estate Unit'

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
    @api.depends('event_ids')
    def _event_count(self):
        for unit in self:
            unit.event_ids_count = len(unit.event_ids)

    @api.multi
    @api.depends('image_ids')
    def _get_main_image(self):
        for unit in self:
            id = False
            res = False
            if unit.id:
                self.env.cr.execute('SELECT id FROM rem_image WHERE unit_id=%s '
                                    'ORDER BY sequence asc, id asc LIMIT 1;', [unit.id])
                res = self.env.cr.dictfetchone()
                if res:
                    id = int(res['id'])
                    res = self.env['rem.image'].search_read([('id', '=', id)])[0]['image_medium']
            unit.main_img = res
            unit.main_img_id = id

    @api.multi
    @api.depends('street', 'street2', 'zone_id.name',
                 'city_id.name', 'zip')
    def name_get(self):
        units = []
        for rec in self:
            unit_name_format = self.env['ir.config_parameter'].sudo().get_param('rem.base_unit_name_format',
                                                                                '{street} {street2}, {city}, {state} {zip}')
            name = self.get_formated_name(rec, unit_name_format)
            units.append((rec.id, name))
        return units

    @api.one
    def get_geo_coordinates(self):
        coordinates = geo_find(
            geo_query_address(
                street=self.street,
                zip=self.zip,
                city=self.city_id.name,
                state=self.state_id.name,
                country=self.country_id.name,
            )
        )

        if coordinates:
            self.latitude = coordinates[0]
            self.longitude = coordinates[1]

    type_id = fields.Many2one('rem.unit.type', string='Type')
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    owner_id = fields.Many2one('res.partner', string='Current Owner', help="Owner of the unit")
    sale_price = fields.Float(string='Sale Price', digits=dp.get_precision('Product Price'))
    area = fields.Float(string='Unit Area')
    active = fields.Boolean('Active', default=True)

    # Events
    event_ids = fields.Many2many('calendar.event', 'calendar_event_rem_unit_rel', 'rem_unit_id',
                                   'calendar_event_id', string='Meetings', copy=False,
                                 help="Appointment / meetings related to this unit")
    event_ids_count = fields.Integer(compute='_event_count')

    # Unit photo's set
    image_ids = fields.One2many(
        'rem.image', 'unit_id', string='Photos', ondelete='cascade')

    # TODO: set a default image for unit if it doesn't have any to show in kanban view
    main_img = fields.Binary('Main Image', compute='_get_main_image', attachment=True, store=True)
    main_img_id = fields.Integer('Main Image ID', compute='_get_main_image')

    # Currency
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, ondelete='cascade')

    @api.multi
    def get_unit_events(self):
        unit_ids = []
        for unit in self:
            unit_ids.append(unit.id)
        return {
            'name': _('Appointments/Meetings'),
            'type': 'ir.actions.act_window',
            'view_mode': 'calendar,tree,form',
            'res_model': 'calendar.event',
            'domain': [('unit_ids', 'in', unit_ids)],
            'context': {'default_unit_ids': unit_ids, 'default_duration': 4.0}
        }
