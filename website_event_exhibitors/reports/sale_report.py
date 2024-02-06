
from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    event_id = fields.Many2one(
        comodel_name="event.event",
        string="Event",
    )
    brand_id = fields.Many2one(
        comodel_name="res.brand",
        string="Brand",
    )

    def _query(self, with_clause="", fields={}, groupby="", from_clause=""):
        fields["event_id"] = ", s.event_id as event_id"
        fields["brand_id"] = ", s.brand_id as brand_id"
        groupby += ", s.event_id, s.brand_id"
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)
