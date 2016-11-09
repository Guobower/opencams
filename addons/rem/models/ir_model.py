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
        # Field will be automatically removed from offer.type
        # Remove base/manual field from rem.unit form
        self.remove_field_from_rem_unit_form(self.name)
        return super(IrModelFields, self).unlink()

    # TODO:
    # Check for duplicated fields
    @api.model
    def create(self, vals):
        post = super(IrModelFields, self).create(vals)
        # If view_rem_unit_form exists and field is a feature
        if self.env['ir.model.data'].search([('name', '=', 'view_rem_unit_form')], limit=1) and vals['rem_category'] in ['general', 'indoor', 'outdoor']:
            # Link base/manual field to offer.type
            self.env['rem.unit'].add_features_to_offer_type()
            # Add base/manual field to rem.unit form
            self.add_field_from_rem_unit_form(vals['name'], vals['rem_category'])
        return post

    @api.multi
    def write(self, vals):
        old_name = self.name
        old_rem_category = self.rem_category

        # add_features_to_offer_type() needs up-to-date record
        post = super(IrModelFields, self).write(vals)

        if 'rem_category' in vals:
            # If field is a feature now but it wasn't
            if vals['rem_category'] in ['general', 'indoor', 'outdoor'] and old_rem_category not in ['general', 'indoor', 'outdoor']:
                # Link base/manual field to offer.type
                self.env['rem.unit'].add_features_to_offer_type()
            # If field is not a feature now but it was
            elif vals['rem_category'] not in ['general', 'indoor', 'outdoor'] and old_rem_category in ['general', 'indoor', 'outdoor']:
                # Remove base/manual field from offer.type
                self.env.cr.execute("DELETE FROM offer_type_ir_model_fields_rel WHERE ir_model_field_id=%i" % self.id)
                self.env.cr.commit()
        # rem.unit form only needs to be updated if name/rem_category changes
        if 'name' in vals or 'rem_category' in vals:
            if not 'name' in vals:
                vals['name'] = old_name
            if not 'rem_category' in vals:
                vals['rem_category'] = old_rem_category
            # Remove base/manual field from rem.unit form (if exists)
            self.remove_field_from_rem_unit_form(vals['name'])
            # If field is a feature
            if vals['rem_category'] in ['general', 'indoor', 'outdoor']:
                # Add base/manual field to rem.unit form
                self.add_field_from_rem_unit_form(vals['name'], vals['rem_category'])

        return post

    def remove_field_from_rem_unit_form(self, name):
        rem_form_id = self.env.ref('rem.view_rem_unit_form').id
        for rem_form in self.env['ir.ui.view'].sudo().browse(rem_form_id):
            doc = etree.XML(rem_form.arch_base)
            for node in doc.xpath("//field[@name='%s']" % name):
                node.getparent().remove(node)
        rem_form.arch_base = etree.tostring(doc)

    def add_field_from_rem_unit_form(self, name, rem_category):
        rem_form_id = self.env.ref('rem.view_rem_unit_form').id
        for rem_form in self.env['ir.ui.view'].sudo().browse(rem_form_id):
            doc = etree.XML(rem_form.arch_base)
            for node in doc.xpath("//group[@name='" + rem_category + "_features']"):
                grpl = node.xpath(".//group[@class='rem_left']")[0]
                grpr = node.xpath(".//group[@class='rem_right']")[0]
                nd = etree.Element("field", name=name, invisible="1")
                if grpl.xpath('count(.//field)') >= grpr.xpath('count(.//field)'):
                    grpr.append(nd)
                else:
                    grpl.append(nd)
        rem_form.arch_base = etree.tostring(doc)
