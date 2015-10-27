# -*- coding: utf-8 -*-
{
    'name': 'Real Estate Management',
    'version': '0.1',
    'author': 'Diogo Duarte',
    'summary': 'Real Estate Asset Management',
    'description': """
Manage real estate assets for sale and rent management purposes
===============================================================


    """,
    'website': 'http://diogocduarte.github.io',
    'depends': ['base', 'account'],
    'category': 'Real Estate',
    'demo': [
        'rem_demo.xml'
    ],
    'data': [
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