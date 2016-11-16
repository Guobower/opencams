# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Asset Management',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Asset Management',
    'description': """
Manage real estate assets for sale and rent management purposes
===============================================================
This module allows to sell/rent real estate units


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['account', 'crm', 'calendar', 'analytic', 'sale', 'website'],
    'category': 'Real Estate',
    'data': [
        'data/rem_data.xml',
        'data/fields_data.xml',
        'data/rent_cron.xml',
        'security/rem_security.xml',
        'security/ir.model.access.csv',
        'views/crm_view.xml',
        'views/ir_model_view.xml',
        'views/contract_view.xml',
        'views/partner_view.xml',
        'views/sale_view.xml',
        'views/rem_menu.xml',
        'views/rem_view.xml',
        'views/stage_history_form.xml',
        'views/rem_menu.xml',
        'views/account_invoice_view.xml',
        'wizard/event_unit_multi.xml',
        'views/rem_cron.xml',
        'res_config_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
