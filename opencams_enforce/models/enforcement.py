from odoo import models, fields, api, _


class ProductImage(models.Model):
    _name = 'cams.violation.image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    violation_id = fields.Many2one('cams.violation', 'Related Violation', copy=True)


class ViolationReason(models.Model):
    _name = 'cams.violation.reason'
    _description = 'Violation Reason'

    sequence = fields.Integer(string='Sequence')
    name = fields.Char(string='Reason')
    notes = fields.Text(string='Notes', help='Description of the violation.')
    active = fields.Boolean(string='Active', default=True,
                            help='If the active field is set to False, it will allow you to hide without removing it.')


class Enforcement(models.Model):
    _name = 'cams.violation'

    reason_id = fields.Many2one('cams.violation.reason', string="Violation Reason", required=True)
    name = fields.Char(string='Subject')
    notes = fields.Text(string='Notes', help='Description of the type.')
    unit_id = fields.Many2one('res.partner', string='Partner', domain=[('is_unit', '=', True)])
    state = fields.Selection([
            ('normal', 'Normal'),
            ('disputed', 'Disputed'),
            ('reversed', 'Reversed'),
            ], string='Status', readonly=True, index=True, copy=False, default='normal', track_visibility='onchange')
    image_ids = fields.One2many('cams.violation.image', 'violation_id', string='Images')
