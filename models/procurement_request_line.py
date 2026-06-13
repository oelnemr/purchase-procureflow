# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError, UserError


class ProcurementRequestLine(models.Model):
    _name = "procurement.request.line"
    _description = "Procurement Request Line Item"

    request_id = fields.Many2one(
        "procurement.request",
        string="Request Reference",
        ondelete="cascade",
        required=True,
    )

    product_name = fields.Many2one(
        "product.product",
        string="Product",
    )
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    unit_price = fields.Float(string="Estimated Price / Unit Price", required=True)
    subtotal = fields.Float(
        compute="_compute_total_price", string="Total Price", required=True
    )

    @api.constrains("quantity", "unit_price")
    def _check_excpected_values(self):
        for record in self:
            if record.quantity <= 0 or record.unit_price <= 0:
                raise ValidationError(
                    "Requested Quantity or Estimated Price / Unit Price Cant = 0"
                )

    @api.depends("quantity", "unit_price")
    def _compute_total_price(self):
        for record in self:
            record.subtotal = record.unit_price * record.quantity
