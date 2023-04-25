# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class StandType(models.Model):
    _name = 'event.stand.type'

    name = fields.Char('Stand Type', required=True)


class Sponsor(models.Model):
    _inherit = ["event.sponsor"]

    # Overridden:
    partner_id = fields.Many2one(string='Partner')
    name = fields.Char(string='Exhibitor Name')
    email = fields.Char(string='Exhibitor Email')
    phone = fields.Char(string='Exhibitor Phone')
    mobile = fields.Char(string='Exhibitor Mobile')

    # New
    visitor_id = fields.Many2one('website.visitor', string='Visitor', ondelete='set null')
    stand_number = fields.Integer(string='Stand Number')
    stand_width = fields.Integer(string='Width (m)', help="Width of Stand in mtrs")
    stand_length = fields.Integer(string='Length (m)', help="Width of Stand in mtrs")
    stand_surface_area = fields.Integer(string='Surface Area (sq.m)', compute='_compute_surface_area'
                                        , help="Surface Area for Stand in Sq mtrs", store=True)
    stand_type_id = fields.Many2one('event.stand.type', string='Stand Type', ondelete='set null')
    remarks = fields.Text('Remarks')

    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'stand_number'
            , 'stand_width', 'stand_length', 'remarks'}

    @api.depends('stand_width', 'stand_length')
    def _compute_surface_area(self):
        for case in self:
            case.stand_surface_area = case.stand_width * case.stand_length
