# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


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
    stand_number = fields.Char(string='Stand Number')
    stand_width = fields.Integer(string='Width (m)', help="Width of Stand in mtrs")
    stand_length = fields.Integer(string='Length (m)', help="Width of Stand in mtrs")
    stand_surface_area = fields.Integer(string='Surface Area (sq.m)', compute='_compute_surface_area'
                                        , help="Surface Area for Stand in Sq mtrs", store=True)
    stand_type_id = fields.Many2one('event.stand.type', string='Stand Type', ondelete='set null')
    remarks = fields.Text('Remarks')
    prod_remarks = fields.Text('Products / Services')
    partner_company = fields.Char(string='Partner Company')
    lead_id = fields.Many2one('crm.lead', string='Lead')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirmed'),
        ('reject', 'Rejected')], string='Status',
        default='draft', copy=False, readonly=True, tracking=True)


    def _get_website_registration_allowed_fields(self):
        return {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'stand_number'
                , 'stand_width', 'stand_length', 'remarks', 'stand_type_id', 'partner_company'
                , 'prod_remarks'}

    @api.depends('stand_width', 'stand_length')
    def _compute_surface_area(self):
        for case in self:
            case.stand_surface_area = case.stand_width * case.stand_length


    def button_confirm(self):
        '''
            Confirm status of Partner from "Draft Exhibitor" to "Confirmed Exhibitor"
            Create Lead with information
        '''

        for case in self.filtered(lambda x: x.state == 'draft'):
            # Update partner status
            if case.partner_id.exhibitor_status == 'draft':
                case.partner_id.exhibitor_status = 'confirmed'
                if case.partner_id.parent_id:
                    case.partner_id.parent_id.exhibitor_status = 'confirmed'

            lead, partner = case.lead_id, False

            if lead.partner_id: partner = lead.partner_id.id
            else:
                partner = lead._find_matching_partner()
                _logger.info("Else >>> Find Matching %s"%(partner))

            if not partner:
                lead.handle_partner_assignment(create_missing=True)
                partner = lead.partner_id.id
                _logger.info("Nope >>> Handle Assignment %s"%(partner))
            lead.convert_opportunity(partner)
            case.write({'state': 'confirm'})
        return True

    def button_reject(self):
        for case in self.filtered(lambda x: x.state == 'draft'):
            case.lead_id.action_set_lost()
            case.write({'state': 'reject'})
        return True



