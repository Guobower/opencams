# -*- coding: utf-8 -*-
import logging
import requests

from openerp import api, fields, models, _
_logger = logging.getLogger(__name__)


class RemConfigSettings(models.TransientModel):
    _inherit = 'rem.config.settings'

    @api.multi
    def check_simple_rets(self):
        print "______________"
        # These are our demo API keys, you can use them!
        api_key = 'simplyrets'
        api_secret = 'simplyrets'
        api_url = 'https://api.simplyrets.com/properties' 

        response = requests.get(api_url, auth=(api_key, api_secret)) 
        for r in response.json():
            print "___V_", r
            field_list = []
            for k, v in r.iteritems():
                print "_K_", k, v
                field_list.append(k)
            print field_list 

    simplyrets_api = fields.Char(string='simplyRETS API Key')
    simplyrets_secret = fields.Char(string='simplyRETS API Secret')
    simplyrets_url = fields.Char(string='simplyRETS API URL')

    @api.model
    def get_default_simplyrets_api(self, fields):
        simplyrets_api = False
        if 'simplyrets_api' in fields:
            simplyrets_api = self.env['ir.config_parameter'].sudo().get_param('rem.simplyrets_api')
        return {
            'simplyrets_api': simplyrets_api
        }

    @api.multi
    def set_simplyrets_api(self):
        for rec in self:
            self.env['ir.config_parameter'].sudo().set_param('rem.simplyrets_api', rec.simplyrets_api)

    @api.model
    def get_default_simplyrets_secret(self, fields):
        simplyrets_secret = False
        if 'simplyrets_secret' in fields:
            if self.env['ir.config_parameter'].sudo().get_param('rem.simplyrets_secret'):
                simplyrets_secret = '********'
            else:
                simplyrets_secret = ''
        return {
            'simplyrets_secret': simplyrets_secret
        }

    @api.multi
    def set_simplyrets_secret(self):
        for rec in self:
            if rec.simplyrets_secret != '********':
                self.env['ir.config_parameter'].sudo().set_param('rem.simplyrets_secret', rec.simplyrets_secret)

    @api.model
    def get_default_simplyrets_url(self, fields):
        simplyrets_url = False
        if 'simplyrets_url' in fields:
            simplyrets_url = self.env['ir.config_parameter'].sudo().get_param('rem.simplyrets_url')
        return {
            'simplyrets_url': simplyrets_url
        }

    @api.multi
    def set_simplyrets_url(self):
        for rec in self:
            self.env['ir.config_parameter'].sudo().set_param('rem.simplyrets_url', rec.simplyrets_url)
