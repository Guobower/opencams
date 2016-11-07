# -*- coding: utf-8 -*-
from openerp import tools, api, fields, models, _
from lxml import etree

_rem_categories = [
	('general', _('General Features')),
	('indoor', _('Indoor Features')),
	('outdoor', _('Outdoor Features'))]


class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'

    rem_category = fields.Selection(_rem_categories, string="REM Category")

    @api.multi
    def unlink(self):
    	# Remove base/manual field from rem.unit form
    	rem_form_id = self.env.ref('rem.view_rem_unit_form').id
        for rem_form in self.env['ir.ui.view'].sudo().browse(rem_form_id):
        	doc = etree.XML(rem_form.arch_base)
        	for node in doc.xpath("//field[@name='%s']" % self.name):
        		node.getparent().remove(node)
        rem_form.arch_base = etree.tostring(doc)
        return super(IrModelFields, self).unlink()
