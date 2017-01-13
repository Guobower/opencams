# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Management',
    'description': """
Manage real estate assets
===============================================================
This module allows to manage real estate units


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
        'views/account_invoice_view.xml',
        'wizard/event_unit_multi.xml',
        'views/rem_cron.xml',
        'res_config_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
