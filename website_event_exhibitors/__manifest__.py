# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Event Exhibitors Registration',
    'category': 'Marketing/Events',
    'sequence': 1005,
    'version': '14.0.20.1',
    'summary': 'Event: upgrade sponsors to exhibitors with registration',
    'author' : 'Deepa, The Open Source Company (TOSC)',
    'website': 'https://www.tosc.nl',
    'description': "",
    'depends': [
        'website_event_track_exhibitor', 'website_sale',
        'website_event_track', 'google_recaptcha',
        'website_jitsi', 'crm', 'sale_crm', 'brand', 'sale_brand',
        'sale_order_type', "analytic"
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sale_order_type.xml',
        "reports/sale_report_view.xml",
        'views/event_stand_views.xml',
        'views/event_theme_views.xml',
        'views/event_event_views.xml',
        'views/product_views.xml',
        'views/event_sponsor_views.xml',
        'views/sale_order_views.xml',
        'views/event_exhibitor_templates_registration.xml',
        'views/event_exhibitor_templates_list.xml',
        "views/sale_report_template.xml",
        'views/website_sale.xml',
        "views/invoice_report_template.xml",

        'views/menu_views.xml',        
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
