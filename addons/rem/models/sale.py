# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('tenant_contract_ids')
    def _compute_units(self):
        for order in self:
            contracts = self.env['rem.tenant.contract'].search([('id', 'in', order.tenant_contract_ids.ids)])
            unit_ids = [ctr.unit_id.id for ctr in contracts]
            order.unit_ids = unit_ids

    tenant_contract_ids = fields.Many2many('rem.tenant.contract', 'sale_order_tenant_ctr_rel', 'ctr_id', 'order_id', string='Tenant Contracts')
    unit_ids = fields.Many2many('rem.unit', compute='_compute_units', string='Units', readonly=True)
