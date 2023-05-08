# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import _, api, exceptions, fields, models

import logging

_logger = logging.getLogger(__name__)

class CrmLead(models.Model):
    _inherit = "crm.lead"


    def _prepare_customer_values(self, name, is_company=False, parent_id=False):
        """ Include Exhibtor Status."""
        values = super(CrmLead, self)._prepare_customer_values(
            name, is_company=is_company, parent_id=parent_id
        )
        values.update({
                "exhibitor_status": 'draft'
            })

        return values