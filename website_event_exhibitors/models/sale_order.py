# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from lxml import etree
import logging

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_id = fields.Many2one('event.event', string='Event', ondelete='restrict', tracking=True)
    state = fields.Selection(selection_add=[
        ('submitted', "Submit for Approval"),
        ('approved1', "Approved by Sales Mgr"),
    ])

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
            return

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

    # Logic for Webshop Orders, not to be written here -- deepa
    # @api.model
    # def create(self, vals):
    #     Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id
    #
    #     SOT = vals.get('type_id', '') or self.context.get('type_id', '')
    #     if SOT != Event_SOT:
    #         return super(SaleOrder, self).create(vals)
    #
    #     website_id = self.env.context.get('website_id', False)
    #     allowed_company_ids = self.env.context.get('allowed_company_ids', False)
    #     # dt_now = fields.Datetime.to_string(datetime.today())
    #     event = self.env['event.event'].search([
    #         # ('date_begin', '<=', dt_now),
    #         # ('date_end', '>=', dt_now),
    #         ('active', '=', True),
    #         ('website_id', '=', website_id),
    #         ('company_id', 'in', allowed_company_ids),
    #         ('stage_id.name', 'not in', ('Ended', 'Cancelled'))
    #     ], limit=1)
    #     if event:
    #         # vals['type_id'] = self.env.ref('website_event_exhibitors.event_sale_type').id # FIXME: SOT not to be enforced here
    #         vals['event_id'] = event.id
    #         vals['brand_id'] = event.brand_id and event.brand_id.id or False
    #     return super(SaleOrder, self).create(vals)
    
    
    def action_submit(self):
        orders = self.filtered(lambda s: s.state in ['draft'])
        for o in orders:
            if not o.order_line:
                raise UserError(_('You cannot submit a quotation/sales order which has no line.'))
        self.write({'state':'submitted'})
        
    def action_approve1(self):
        orders = self.filtered(lambda s: s.state in ['submitted'])
        orders.write({'state':'approved1'})
    
    def action_refuse(self):
        orders = self.filtered(lambda s: s.state in ['submitted', 'sale', 'sent', 'approved1'])
        orders.write({'state': 'draft'})
        return True

    @api.model
    def fields_view_get(
            self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        ret_val = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            doc = etree.XML(ret_val["arch"])
            order_type = self.env.context.get('default_type_id', False)
            Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id
            if not order_type or (order_type and Event_SOT != order_type):

                doc_tree = etree.XML(ret_val['fields']['order_line']['views']['tree']['arch'])
                for node in doc_tree.xpath("//field[@name='price_unit']"):
                    node.set('invisible', '1')
                    node.set(
                        "attrs",
                        "{}"
                    )
                    self.setup_modifiers(
                        node,
                        # field=field_sub,
                        context=self._context,
                        current_node_path="tree",
                    )

                ret_val['fields']['order_line']['views']['tree']['arch'] = etree.tostring(doc_tree)

                doc_form = etree.XML(ret_val['fields']['order_line']['views']['form']['arch'])
                for node in doc_form.xpath("//field[@name='price_unit']"):
                    node.set('invisible', '1')
                    node.set(
                        "attrs",
                        "{}"
                    )
                    self.setup_modifiers(
                        node,
                        # field=field_sub,
                        context=self._context,
                        current_node_path="form",
                    )

                ret_val['fields']['order_line']['views']['form']['arch'] = etree.tostring(doc_form)

                return ret_val

            if not self.env.user.has_group('event.group_event_manager'):
                for node in doc.xpath("//button[@name='action_confirm'][1]"):
                    node.set('invisible', '1')
                    self.setup_modifiers(
                        node,
                        # field=field,
                        context=self._context,
                        current_node_path="form",
                    )
                for node in doc.xpath("//button[@name='action_confirm'][2]"):
                    node.set('invisible', '1')
                    self.setup_modifiers(
                        node,
                        # field=field,
                        context=self._context,
                        current_node_path="form",
                    )
            else:
                for node in doc.xpath("//button[@name='action_confirm'][1]"):
                    node.set(
                    "attrs",
                    "{'invisible': "
                    "[('state', '!=', 'approved1')]}"
                    )
                    self.setup_modifiers(
                        node,
                        # field=field,
                        context=self._context,
                        current_node_path="form",
                    )

                for node in doc.xpath("//button[@name='action_confirm'][2]"):
                    node.set('invisible', '1')
                    self.setup_modifiers(
                        node,
                        # field=field,
                        context=self._context,
                        current_node_path="form",
                    )
            ret_val["arch"] = etree.tostring(doc, encoding="unicode")
        return ret_val


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _compute_event_price_edit(self):
        if self.order_id.type_id.id == self.env.ref('website_event_exhibitors.event_sale_type').id:
            self.event_price_edit = False
            if self.product_template_id and self.product_template_id.price_edit:
                self.event_price_edit = True

    price_subtotal_disc_amt = fields.Monetary(string='Subtotal after discount')
    event_price_edit = fields.Boolean(compute='_compute_event_price_edit', string='Event Price Editable')

    @api.onchange('price_subtotal_disc_amt')
    def _onchange_subtotal_discount(self):
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id
        if self.order_id.type_id.id == Event_SOT and self.price_unit:
            differnce_amt = self.price_subtotal - self.price_subtotal_disc_amt
            self.discount = (differnce_amt / self.price_subtotal) * 100

    @api.onchange('product_uom_qty', 'price_unit')
    def reset_discount_price_subtotal_disc_amt(self):
        Event_SOT = self.env.ref('website_event_exhibitors.event_sale_type').id
        if self.order_id.type_id.id == Event_SOT:
            self.discount = 0
            self.price_subtotal_disc_amt = 0

