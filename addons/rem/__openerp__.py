# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Asset Management',
    'version': '1.0',
    'author': 'Odoo GAP',
    'summary': 'Real Estate Asset Management',
    'description': """
Manage real estate assets for sale and rent management purposes
===============================================================


    """,
    'website': 'http://www.odoogap.com',
    'depends': ['account', 'crm'],
    'category': 'Real Estate',
    'demo': [
        'rem_demo.xml'
    ],
    'data': [
        'security/ir.model.access.csv',
        'rem_view.xml',
        'rem_data.xml',
        'unit_sequence.xml'
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}