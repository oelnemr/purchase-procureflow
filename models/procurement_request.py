from odoo import models, fields, api


class ProcurementRequest(models.Model):
    _name = "procurement.request"
    _description = "Procurement Requests"
    _order = "name desc"

    name = fields.Char(
        default="Request ID",
        index=True,
        readonly=True,
        required=True,
        string="Request Referance",
    )
    employee_name = fields.Many2one(
        "res.users",
        string="Employee",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    line_ids = fields.One2many(
        "procurement.request.line", "request_id", string="Requested Items"
    )

    @api.model
    def create(self, vals):

        if not vals.get("name") or vals.get("name") == "Request ID":
            vals["name"] = self.env["ir.sequence"].next_by_code("procurement.request")

        return super().create(vals)
