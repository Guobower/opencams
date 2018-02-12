# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import datetime


class SaleOrder(models.Model):
    _inherit = 'account.invoice'

    @api.depends('tenant_contract_ids')
    def _compute_units(self):
        for invoice in self:
            contracts = self.env['rem.tenant.contract'].search([('id', 'in', invoice.tenant_contract_ids.ids)])
            unit_ids = [ctr.unit_id.id for ctr in contracts]
            invoice.unit_ids = unit_ids

    tenant_contract_ids = fields.Many2many('rem.tenant.contract', 'account_invoice_tenant_ctr_rel', 'ctr_id',
                                           'invoice_id', string='Tenant Contracts')
    unit_ids = fields.Many2many('rem.unit', compute='_compute_units', string='Units', readonly=True)
