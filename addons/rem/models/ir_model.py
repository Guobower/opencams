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

    @api.model
    def create(self, vals):
        post = super(IrModelFields, self).create(vals)

        if self.env['ir.model.data'].search([('name', '=', 'view_rem_unit_form')], limit=1):
            # Link base/manual field to offer.type
            self.env['rem.unit'].add_features_to_offer_type()

            # Add base/manual field from rem.unit form
            rem_form_id = self.env.ref('rem.view_rem_unit_form').id
            for rem_form in self.env['ir.ui.view'].sudo().browse(rem_form_id):
                doc = etree.XML(rem_form.arch_base)
                for rem_category in ['general', 'indoor', 'outdoor']:
                    for node in doc.xpath("//group[@name='" + rem_category + "_features']"):
                        grpl = node.xpath(".//group[@class='rem_left']")[0]
                        grpr = node.xpath(".//group[@class='rem_right']")[0]
                        nd = etree.Element("field", name=vals['name'], invisible="1")
                        if grpl.xpath('count(.//field)') >= grpr.xpath('count(.//field)'):
                            grpr.append(nd)
                        else:
                            grpl.append(nd)
            rem_form.arch_base = etree.tostring(doc)

        return post

    @api.multi
    def write(self, vals):
        # TODO:
        # When the user creates a new field without rem_category and updates rem_catrgory later,
        #   he will need to update the module
        # We could add/remove the new custom field (like we are doing on create/unlink) if we
        #   detecte this particular case
        return super(IrModelFields, self).write(vals)
