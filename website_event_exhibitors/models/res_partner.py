# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

import logging

_logger = logging.getLogger(__name__)

class Partner(models.Model):
    _inherit = ["res.partner"]


    exhibitor_status = fields.Selection([('draft', 'Draft Exhibitor'), ('confirmed', 'Exhibitor')], 'Exhibitor?', copy=False)


    # # Overridden:
    # def _get_contact_name(self, partner, name):
    #     if self._context.get('show_wo_company'):
    #         return "%s" % (name)
    #     else:
    #         return "%s, %s" % (partner.commercial_company_name or partner.sudo().parent_id.name, name)
