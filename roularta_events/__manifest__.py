# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Roularta Events',
    'category': 'Marketing/Events',
    'sequence': 1005,
    'version': '14.1.0',
    'summary': 'Event: Improvements specific to Roularta',
    'author' : 'Deepa, The Open Source Company (TOSC)',
    'website': 'https://www.tosc.nl',
    'description': "",
    'depends': [
        'website_event_exhibitors'
    ],
    'data': [
        "views/sale_report_template.xml",
        "views/invoice_report_template.xml",
        "views/event_sponsor_views.xml",
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
