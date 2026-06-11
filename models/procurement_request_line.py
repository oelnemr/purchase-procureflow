# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProcurementRequestLine(models.Model):
    _name = "procurement.request.line"
    _description = "Procurement Request Line Item"

    request_id = fields.Many2one(
        "procurement.request",
        string="Request Reference",
        ondelete="cascade",
        required=True,
    )

    # Item details
    product_name = fields.Char(string="Product Name", required=True)
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    unit_price = fields.Float(string="Estimated Unit Price", required=True)
    subtotal = fields.Float(
        compute="_compute_total_price", string="Total Price", required=True
    )

    @api.depends("quantity", "unit_price")
    def _compute_total_price(self):
        for record in self:
            record.subtotal = record.unit_price * record.quantity
