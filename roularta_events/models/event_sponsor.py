# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)


class Sponsor(models.Model):
    _inherit = ["event.sponsor"]
    _order = "id desc"

    # Overridden:
    name = fields.Char('Exhibitor Name/Company', compute='_compute_name', readonly=False, store=True)

    # New
    partner_parent_id = fields.Many2one('res.partner', related="partner_id.parent_id", string='Exhibitor Company',
                                        tracking=True, store=True)


    @api.depends('partner_id')
    def _compute_name(self):
        "Update it with Exhibitor Company"
        CompanyName = False
        if self.partner_id:
            CompanyName = self.partner_id.parent_id and self.partner_id.parent_id.name or ''

        if CompanyName:
            self.name = CompanyName
        else:
            self._synchronize_with_partner('name')