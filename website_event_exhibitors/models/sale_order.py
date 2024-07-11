# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import logging

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

