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
    'depends': ['account', 'crm', 'calendar', 'analytic'],
    'category': 'Real Estate',
    'data': [
        'data/rem_data.xml',
        'security/ir.model.access.csv',
        'security/rem_security.xml',
        'views/crm_view.xml',
        'views/contract_view.xml',
        'views/partner_view.xml',
        'views/rem_menu.xml',
        'views/rem_view.xml',
        'views/stage_history_form.xml',
        'views/res_config_view.xml',
        'views/rem_menu.xml',
        'wizard/event_unit_multi.xml',
        'views/rem_cron.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
