# -*- coding: utf-8 -*-
import openerp
import werkzeug
from openerp import http
from openerp.http import request


class WebsiteContact(openerp.addons.web.controllers.main.Home):

	@http.route(['/page/contactus'], type='http', auth='none')
	def website_contact(self):
		return werkzeug.utils.redirect('/contact-us', 303)


class WebsiteRem(http.Controller):

	@http.route(['/contact-us'], type='http', auth='public', website=True)
	def website_rem_contact(self):
		return request.website.render('theme_material.contact_us_page')
