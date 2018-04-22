# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management Core',
    'version': '11.0.1.0',
    'author': 'Diogo Duarte',
    'summary': 'Real Estate Management',
    'description': """
Manage real estate assets
=========================
This module allows to manage real estate units

    """,
    'website': 'http://www.odoogap.com',
    'depends': ['account', 'calendar'],
    'category': 'Real Estate',
    'data': [
        'security/rem_security.xml',
        'security/ir.model.access.csv',
        'views/rem_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
