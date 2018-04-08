# -*- coding: utf-8 -*-
{
    'name': 'Community Association Management System',
    'version': '11.0.1.0',
    'author': 'Diogo Duarte',
    'summary': 'Community Association Management Systemt',
    'description': """
Community Association Management System
=======================================
This module allows to manage real estate communities.

Feature list:


    """,
    'website': 'http://www.opencams.org',
    'depends': ['rem', 'l10n_us', 'account_invoicing'],
    'category': 'Real Estate',
    'data': [
        'data/main_data.xml',
        'views/cams_menu.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
