from odoo import api, fields, models, _
from lxml import etree


class productTemplate(models.Model):
    _inherit = "product.template"

    price_edit = fields.Boolean('Price Editable')

    @api.model
    def fields_view_get(
            self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        result = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )        
        if view_type == "form":
            doc = etree.XML(result["arch"])
            if doc.xpath("//field[@name='price_edit']"):
                # Field was inserted explicitely
                return result

            for node in doc.xpath("//field[@name='categ_id']"):
                elem = etree.Element(
                    "field",
                    {
                        "name": "price_edit",
                    },
                )
                node.addnext(elem)

            result["arch"] = etree.tostring(doc, encoding="unicode")

        return result