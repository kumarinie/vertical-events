# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_id = fields.Many2one('event.event', string='Event', ondelete='restrict', tracking=True)
    customer_contact = fields.Many2one('res.partner', 'Contact Person', domain=[('is_customer', '=', True)])

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

    @api.onchange('partner_id')
    def onchange_partner2(self):
        if not self.partner_id:
            self.customer_contact = False

        if self.partner_id.type == 'contact':
            contact = self.env['res.partner'].search([('is_company','=', False),('type','=', 'contact'),('parent_id','=', self.partner_id.id)])
            if len(contact) >=1:
                contact_id = contact[0]
            else:
                contact_id = False
        else:
            addr = self.partner_id.address_get(['delivery', 'invoice'])
            contact_id = addr['contact']
        if not self.partner_id.is_company and not self.partner_id.parent_id:
            contact_id = self.partner_id

        if not self.customer_contact:
            self.customer_contact = contact_id

    @api.model
    def create(self, vals):
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
            vals['type_id'] = self.env.ref('website_event_exhibitors.event_sale_type').id
            vals['event_id'] = event.id
            vals['brand_id'] = event.brand_id and event.brand_id.id or False
        return super(SaleOrder, self).create(vals)

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        if self.customer_contact:
            invoice_vals['customer_contact'] = self.customer_contact.id
        return invoice_vals



