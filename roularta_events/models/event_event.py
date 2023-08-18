# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug


class EventEvent(models.Model):
    _inherit = "event.event"

    website_exhibitor_reg_url = fields.Char('Exhibitor Registration URL', compute='_compute_exreg_url', store=True)

    @api.depends('website_url')
    def _compute_exreg_url(self):
        for rec in self:
            url = ''
            if rec.website_url: url = rec.website_url + '/exhibitors_register'
            rec.website_exhibitor_reg_url = url or ''
