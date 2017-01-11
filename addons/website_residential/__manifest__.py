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
    'depends': ['website', 'website_crm', 'website_form', 'website_portal', 'rem', 'rem_residential', 'theme_material'],
    'category': 'Real Estate',
    'demo': [
    ],
    'data': [
        'data/website_residential_data.xml',
        'security/website_residential.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/templates.xml',
        'views/templates_seller.xml',
        'views/templates_atom.xml',
        'data/seller_data.xml'
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
