# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Event Exhibitors Registration',
    'category': 'Marketing/Events',
    'sequence': 1005,
    'version': '1.0',
    'summary': 'Event: upgrade sponsors to exhibitors with registration',
    'author' : 'Deepa, The Open Source Company (TOSC)',
    'website': 'https://www.tosc.nl',
    'description': "",
    'depends': [
        'website_event_track_exhibitor',
        'website_event_track',
        'website_jitsi',
    ],
    'data': [
        'views/event_stand_views.xml',
        'views/event_event_views.xml',
        'views/event_sponsor_views.xml',
        'views/event_exhibitor_templates_registration.xml',
        'views/event_exhibitor_templates_list.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
