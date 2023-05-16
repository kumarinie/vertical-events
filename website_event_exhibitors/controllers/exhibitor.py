# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


import werkzeug
from werkzeug.exceptions import NotFound, Forbidden

from odoo import exceptions, http, fields
from odoo.addons.website_event_track.controllers.event_track import EventTrackController
from odoo.http import request

import logging

_logger = logging.getLogger(__name__)

class ExhibitorRegisterController(EventTrackController):

    # ------------------------------------------------------------
    # MAIN PAGE
    # ------------------------------------------------------------

    @http.route(['/event/<model("event.event"):event>/exhibitors_register'], type='http', auth="public", website=True, sitemap=False)
    def event_exhibitors_register(self, event, **searches):
        if not event.can_access_from_current_website():
            raise NotFound()

        return request.render(
            "website_event_exhibitors.event_exhibitors_register",
            self._event_exhibitors_get_values(event, **searches)
        )

    def _event_exhibitors_get_values(self, event, **searches):
        StandTypes = request.env['event.stand.type'].sudo().search([])
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request()

        # return rendering values
        return {
            # event information
            'event': event,
            'main_object': event,
            "name": visitor_sudo.partner_id.name or None,
            "email": visitor_sudo.partner_id.email or None,
            "mobile": visitor_sudo.partner_id.mobile or None,
            "phone": visitor_sudo.partner_id.phone or None,
            "partner_company": visitor_sudo.partner_id.company_name or None,

            # environment
            'hostname': request.httprequest.host.split(':')[0],
            'user_event_manager': request.env.user.has_group('event.group_event_manager'),

            'stand_types': StandTypes
        }


    @http.route(['''/event/<model("event.event"):event>/exhibitor_registration/new'''], type='http', auth="public", methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        registrations = self._process_exhibitor_data_form(event, post)
        exhibitor_sudo = self._create_exhibitor_from_registration_post(event, registrations)

        return request.render("website_event_exhibitors.registration_complete",
            self._get_registration_confirm_values(event, exhibitor_sudo))



    def _process_exhibitor_data_form(self, event, form_details):
        """ Process data posted from the exhibitor details form.

        :param form_details: posted data from frontend registration form, like
            {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
        """
        allowed_fields = request.env['event.sponsor']._get_website_registration_allowed_fields()
        registration_fields = {key: v for key, v in request.env['event.sponsor']._fields.items() if key in allowed_fields}

        _logger.info('process Registration Data  \n<allowed_fields> %s \n<registration_fields> %s'%(allowed_fields, registration_fields))

        registrations = {}
        global_values = {}
        for key, value in form_details.items():
            counter, attr_name = key.split('-', 1)
            field_name = attr_name.split('-')[0]
            if field_name not in registration_fields:
                continue
            elif isinstance(registration_fields[field_name], (fields.Many2one, fields.Integer)):
                value = int(value) or False  # 0 is considered as a void many2one aka False
            else:
                value = value

            if counter == '0':
                global_values[attr_name] = value
            else:
                registrations.setdefault(counter, dict())[attr_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value

        return list(registrations.values())


    # def _create_exhibitor_from_registration_post(self, event, registration_data):
    #     """ Also try to set a visitor (from request) and
    #     a partner (if visitor linked to a user for example). Purpose is to gather
    #     as much informations as possible, notably to ease future communications.
    #     Also try to update visitor informations based on registration info. """
    #     visitor_sudo = request.env['website.visitor']._get_visitor_from_request(force_create=True)
    #     visitor_sudo._update_visitor_last_visit()
    #     visitor_values = {}
    #     registrations_to_create = []
    #
    #     import logging
    #     _logger = logging.getLogger(__name__)
    #     _logger.info('Exhibitor Registration Data %s'%(registration_data))
    #
    #     request.env.ref('base.public_user').id
    #
    #     for registration_values in registration_data:
    #         registration_values['event_id'] = event.id
    #         if not registration_values.get('partner_id') and visitor_sudo.partner_id:
    #             registration_values['partner_id'] = visitor_sudo.partner_id.id
    #             _logger.info("IF : No Partner & Visitor")
    #         elif not registration_values.get('partner_id'):
    #             registration_values['partner_id'] = request.env.user.partner_id.id
    #             _logger.info("Else : No Partner & Visitor")
    #
    #         if visitor_sudo:
    #             # registration may give a name to the visitor, yay
    #             if registration_values.get('name') and not visitor_sudo.name and not visitor_values.get('name'):
    #                 visitor_values['name'] = registration_values['name']
    #             # update registration based on visitor
    #             registration_values['visitor_id'] = visitor_sudo.id
    #
    #         registration_values['sponsor_type_id'] = 1  # TODO: Need this? deep
    #         registrations_to_create.append(registration_values)
    #
    #         # Create Partner:
    #         if registration_values.get("email"):
    #             Partner = request.env["res.partner"]
    #             #FIXME: If partner already exists, link to same?
    #             vals = {}
    #             # Look for a partner with that email
    #             email = registration_values.get("email").replace("%", "").replace("_", "\\_")
    #             partner = Partner.search([("email", "=ilike", email)], limit=1)
    #             if partner:
    #                 for field in {"name", "phone", "mobile"}:
    #                     vals[field] = vals.get(field) or partner[field]
    #             elif event.create_partner:
    #                 # Create partner
    #                 partner = Partner.sudo().create(
    #                     self._prepare_partner(registration_values)
    #                 )
    #             registration_values["partner_id"] = partner.id
    #
    #     if visitor_values:
    #         visitor_sudo.write(visitor_values)
    #
    #     _logger.info('EE Registration Data [2] %s'%(registrations_to_create))
    #
    #     return request.env['event.sponsor'].sudo().create(registrations_to_create)

    #
    # def _create_exhibitor_from_registration_post(self, event, registration_data):
    #     """ Also try to set a visitor (from request) and
    #     a partner (if visitor linked to a user for example). Purpose is to gather
    #     as much informations as possible, notably to ease future communications.
    #     Also try to update visitor informations based on registration info. """
    #     visitor_sudo = request.env['website.visitor']._get_visitor_from_request(force_create=True)
    #     visitor_sudo._update_visitor_last_visit()
    #     visitor_values = {}
    #     registrations_to_create = []
    #     # partner_values = {}
    #
    #     _logger.info('Exhibitor Registration Data %s'%(registration_data))
    #     # UserLoggedIn = False
    #
    #     for registration_values in registration_data:
    #         registration_values['event_id'] = event.id
    #
    #         # if request.env.ref('base.public_user').id != request.env.user.partner_id.id:
    #         #     registration_values['partner_id'] = request.env.user.partner_id.id
    #         #     UserLoggedIn = True
    #         #     _logger.info("IF : Logged in User")
    #         # elif visitor_sudo:
    #         #     registration_values['partner_id'] = visitor_sudo.partner_id.id
    #         #     _logger.info("Else : Visitor %s"%(visitor_sudo.partner_id.name))
    #
    #         if visitor_sudo.partner_id:
    #             registration_values['partner_id'] = visitor_sudo.partner_id.id
    #             _logger.info("IF : No Partner & Visitor %s"%(visitor_sudo.partner_id))
    #         else:
    #             registration_values['partner_id'] = request.env.user.partner_id.id
    #             _logger.info("Else : No Partner %s"%(request.env.user.partner_id))
    #
    #         if visitor_sudo:
    #             # registration may give a name to the visitor, yay
    #             if registration_values.get('name') and not visitor_sudo.name and not visitor_values.get('name'):
    #                 visitor_values['name'] = registration_values['name']
    #             # update registration based on visitor
    #             registration_values['visitor_id'] = visitor_sudo.id
    #
    #         # # To Create Partner
    #         # for field in {"name", "phone", "mobile", "partner_company"}:
    #         #     partner_values[field] = registration_values.get(field, '')
    #
    #         # # Create/Link Partner:
    #         # if registration_values.get("email"):
    #         #     Partner = request.env["res.partner"]
    #         #     # Look for a partner with that email
    #         #     email = registration_values.get("email").replace("%", "").replace("_", "\\_")
    #         #     partner = Partner.search([("email", "=ilike", email)], limit=1)
    #         #     if UserLoggedIn:
    #         #         partner = request.env.user.partner_id
    #         #     elif not partner:
    #         #         # Create New partner
    #         #         partner = Partner.sudo().create(
    #         #             self._prepare_partner(partner_values)
    #         #         )
    #         #     registration_values["partner_id"] = partner.id
    #
    #
    #         registration_values['sponsor_type_id'] = 1  # TODO: Need this? deep
    #         registrations_to_create.append(registration_values)
    #
    #         # # Create Partner:
    #         # if registration_values.get("email"):
    #         #     Partner = request.env["res.partner"]
    #         #     if not UserLoggedIn:
    #         #         # Create partner
    #         #         partner = Partner.sudo().create(
    #         #             self._prepare_partner(partner_values)
    #         #         )
    #         #     else:
    #         #         partner = request.env.user.partner_id
    #         #
    #         #     registration_values["partner_id"] = partner.id
    #
    #     if visitor_values:
    #         visitor_sudo.write(visitor_values)
    #
    #     _logger.info('EE Registration Data [2] %s'%(registrations_to_create))
    #
    #
    #     return request.env['event.sponsor'].sudo().create(registrations_to_create)


    def _create_exhibitor_from_registration_post(self, event, registration_data):
        """ Also try to set a visitor (from request) and
        a partner (if visitor linked to a user for example). Purpose is to gather
        as much informations as possible, notably to ease future communications.
        Also try to update visitor informations based on registration info. """
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request(force_create=True)
        visitor_sudo._update_visitor_last_visit()
        visitor_values = {}
        registrations_to_create = []
        lead_vals = {}

        for registration_values in registration_data:
            registration_values['event_id'] = event.id

            if visitor_sudo.partner_id:
                registration_values['partner_id'] = visitor_sudo.partner_id.id
                lead_vals['partner_id'] = visitor_sudo.partner_id.id
            else:
                registration_values['partner_id'] = request.env.user.partner_id.id

            if visitor_sudo:
                # registration may give a name to the visitor, yay
                if registration_values.get('name') and not visitor_sudo.name and not visitor_values.get('name'):
                    visitor_values['name'] = registration_values['name']
                # update registration based on visitor
                registration_values['visitor_id'] = visitor_sudo.id

            # Lead Creation
            lead_vals.update({
                'contact_name': registration_values['name'],
                'email_from': registration_values['email'],
                'mobile': registration_values['mobile'],
                'phone': registration_values['phone'],
                'name': "Event: %s | %s" % (event.name, registration_values['name']),
                'partner_name': registration_values['partner_company'],
                'team_id': event.team_id.id or False,
                'event_id': event.id
            })

            registration_values['lead_id'] = self._create_lead(lead_vals)
            registration_values['sponsor_type_id'] = 1  # FIXME: Remove this
            registrations_to_create.append(registration_values)

        if visitor_values:
            visitor_sudo.write(visitor_values)

        return request.env['event.sponsor'].sudo().create(registrations_to_create)


    def _get_registration_confirm_values(self, event, exhibitor_sudo):
        urls = event._get_event_resource_urls()
        return {
            'attendees': exhibitor_sudo,
            'event': event,
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url')
        }


    def _create_lead(self, values):
        LeadObj = request.env['crm.lead']
        values.update(
            LeadObj.default_get(['type', 'stage_id'])
        )
        values.update({'type': 'lead'})

        Lead = LeadObj.sudo().create(values)
        return Lead.id
