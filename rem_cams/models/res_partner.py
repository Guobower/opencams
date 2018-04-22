from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_home_owner = fields.Boolean(string="Is Home Owner?")
