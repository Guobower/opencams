# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProjectProject(models.Model):
    _inherit = 'project.project'

    unit_id = fields.Many2one('rem.unit', string='Rem Unit')


class ProjectTasl(models.Model):
    _inherit = 'project.task'

    unit_id = fields.Many2one('rem.unit', string='Rem Unit', related='project_id.unit_id', readonly=True)
