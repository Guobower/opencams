# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Agency Website',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Agency Website',
    'description': """
Public real estate agency website showroom
==========================================
This Module allows to sell/rent real estate units


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['website', 'website_crm', 'website_form', 'rem', 'theme_material'],
    'category': 'Real Estate',
    'demo': [
    ],
    'data': [
        'views/menu.xml',
        'views/templates.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
