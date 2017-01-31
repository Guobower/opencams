# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management Office',
    'version': '10.0.1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Management Office',
    'description': """
Manage real estate office assets for rent management purposes
===========================================================================
This module allows to rent real estate office units


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['rem'],
    'category': 'Real Estate',
    'data': [
        'data/rem_data.xml',
        'data/fields_data.xml',
        'views/crm_view.xml',
        'views/rem_menu.xml',
        'views/rem_view.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
