# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

from odoo.http import request
from odoo.addons.website.models import ir_http
from odoo.addons.http_routing.models.ir_http import url_for

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'


    def _prepare_sale_order_values(self, partner, pricelist):
        " Link Active Event & its Brand"
        values = super()._prepare_sale_order_values(partner, pricelist)

        website = self._context.get('website_id')
        event = self.env['event.event'].search([('website_id', '=', website),
                                        ('stage_id', '=', self.env.ref('event.event_stage_announced').id)], limit=1)

        if event:
            values.update({'event_id': event.id, 'brand_id': event.brand_id.id})

        return values