from odoo import models, fields, api


class UnitOwnership(models.Model):
    """TODO: this object will record the historic of ownership"""
    _name = 'rem.unit.ownership'
    _description = 'Unit Ownership'
    _order = "deed_date"
    _rec_name = 'deed_date'

    deed_date = fields.Date('Deed Date', help="Date when the current owner bought this unit.")
    unit_id = fields.Many2one('rem.unit', string='Unit', required=True)
    partner_id = fields.Many2one('Home Owner', domain=[('is_home_owner', '=', True)])


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('unit_ids')
    def _unit_count(self):
        for partner in self:
            partner.unit_count = len(partner.unit_ids)

    is_home_owner = fields.Boolean(string="Is Home Owner?")
    unit_count = fields.Integer(compute='_unit_count')
    unit_ids = fields.One2many('rem.unit', 'partner_id', string='Unit(s)')
    monthly_fees = fields.Monetary(compute='_compute_amount', string='Total Monthly Fees Amount', readonly=True)
    special_assessment = fields.Monetary(compute='_compute_amount', string='Total Special Assessment', readonly=True)

    @api.depends('unit_ids', 'unit_ids.monthly_fees', 'unit_ids.special_assessment')
    def _compute_amount(self):
        for partner in self:
            monthly_fees = sum(partner.unit_ids.mapped('monthly_fees'))
            special_assessment = sum(partner.unit_ids.mapped('special_assessment'))
            partner.update({
                'monthly_fees': monthly_fees or 0.0,
                'special_assessment': special_assessment or 0.0,
            })
