# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_id = fields.Many2one('event.event', string='Event', ondelete='restrict', tracking=True)

    @api.onchange('brand_id')
    def _onchange_brand(self):
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id

        # Event Orders:
        if (self.type_id and self.type_id.id != Event_SOT):
            return

        if self.brand_id:
            # If Event exists
            if self.event_id and self.event_id.brand_id.id != self.brand_id.id:
                self.event_id = False


    @api.onchange('event_id')
    def _onchange_event(self):
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id

        # Event Orders:
        if (self.type_id and self.type_id.id != Event_SOT):
            return True

        if self.event_id:
            self.website_id = self.event_id.website_id.id or False
            self.analytic_account_id = self.event_id.analytic_account_id.id or False

            line_ids = []
            for product in self.event_id.default_product_ids:
                line_ids += [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "product_uom_qty":1,
                        },
                    )]
            self.order_line = line_ids
            for line in self.order_line:
                line.product_id_change()

    @api.model
    def create(self, vals):
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id

        SOT = vals.get('type_id', '') or self.context.get('type_id', '')
        if SOT != Event_SOT:
            return super(SaleOrder, self).create(vals)

        website_id = self.env.context.get('website_id', False)
        allowed_company_ids = self.env.context.get('allowed_company_ids', False)
        # dt_now = fields.Datetime.to_string(datetime.today())
        event = self.env['event.event'].search([
            # ('date_begin', '<=', dt_now),
            # ('date_end', '>=', dt_now),
            ('active', '=', True),
            ('website_id', '=', website_id),
            ('company_id', 'in', allowed_company_ids),
            ('stage_id.name', 'not in', ('Ended', 'Cancelled'))
        ], limit=1)
        if event:
            # vals['type_id'] = self.env.ref('website_event_exhibitors.event_sale_type').id # FIXME: SOT not to be enforced here
            vals['event_id'] = event.id
            vals['brand_id'] = event.brand_id and event.brand_id.id or False
        return super(SaleOrder, self).create(vals)

