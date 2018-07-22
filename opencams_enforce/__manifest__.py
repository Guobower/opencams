# -*- coding: utf-8 -*-
{
    'name': 'OpenCAMS - Enforcement',
    'version': '11.0.1.0',
    'author': 'opencams.org',
    'summary': 'Open Community Association Management System Enforcement Module',
    'description': """
Community Association Management System - Enforcement
=====================================================
This module helps HOA's to Enforce Community Rules and Regulations

Feature list:


    """,
    'website': 'http://www.opencams.org',
    'depends': ['opencams'],
    'category': 'Real Estate',
    'data': [
        'security/ir.model.access.csv',

        'views/violation_views.xml',
        'views/partner_views.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
