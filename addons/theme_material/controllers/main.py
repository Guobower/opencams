# -*- coding: utf-8 -*-
import openerp
import werkzeug
from openerp import http
from openerp.http import request


class WebsiteContact(openerp.addons.web.controllers.main.Home):

	@http.route(['/page/contactus'], type='http', auth="none")
	def web_login(self):
		return werkzeug.utils.redirect('/contact-us', 303)


class RemWebsite(http.Controller):

	@http.route(['/contact-us'], type='http', auth="public", website=True)
	def contact_us(self):
		return request.website.render("theme_material.contact_us_page")
