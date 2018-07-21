# -*- coding: utf-8 -*-
{
    'name': 'Open Community Association Management System',
    'version': '11.0.1.0',
    'author': 'opencams.org',
    'summary': 'Open Community Association Management System',
    'description': """
Community Association Management System
=======================================
This module allows to manage real estate communities.

Feature list:


    """,
    'website': 'http://www.opencams.org',
    'depends': ['base', 'l10n_us', 'account_invoicing'],
    'category': 'Real Estate',
    'data': [
        'security/rem_security.xml',
        'security/ir.model.access.csv',

        'data/main_data.xml',
        'views/partner_views.xml',
        'views/unit_views.xml',
        'views/res_config_settings_views.xml',
        'views/root_menu.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
