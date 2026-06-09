from odoo import models, fields, api


class ProcurementRequest(models.Model):
    _name = "procurement.request"
    _description = "Procurement Requests"
    _order = "name desc"

    name = fields.Text(
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
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting_approval", "Waiting Approval"),
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
