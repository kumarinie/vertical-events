# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from datetime import datetime
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
        """ update Sale Order Type """
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id

        self_ctx = self.with_context(default_type_id=Event_SOT)
        return super(Website, self_ctx).sale_get_order(
                force_create=force_create, code=code,
                update_pricelist=update_pricelist,
                force_pricelist=force_pricelist,
            )

    def _prepare_sale_order_values(self, partner, pricelist):
        ' Update Active Event & Brand'
        vals = super()._prepare_sale_order_values(partner, pricelist)

        website_id = self.id
        # allowed_company_ids = self.env.context.get('allowed_company_ids', False)
        dt_now = fields.Datetime.to_string(datetime.today())

        # Active Event on Website
        event = self.env['event.event'].sudo().search([
            ('date_begin', '<=', dt_now),
            ('date_end', '>=', dt_now),
            ('active', '=', True),
            ('website_id', '=', website_id),
            # ('company_id', 'in', allowed_company_ids), # FIXME: In bo-test, check if needed
            ('stage_id.pipe_end', '!=', True)
        ], limit=1, order='date_begin desc')

        if event:
            vals.update({'event_id':  event.id,
                         'brand_id': event.brand_id.id
                    })

        return vals


