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
        if self.brand_id:
            self.website_id = self.brand_id.website_id.id or False
            self.event_id = False





