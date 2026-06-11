from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError, UserError


class ProcurementRequest(models.Model):
    _name = "procurement.request"
    _description = "Procurement Requests"
    _order = "request_date desc"

    name = fields.Char(
        default="Request ID",
        index=True,
        readonly=True,
        required=True,
        string="Request Referance",
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Requested By",
        default=lambda self: self.env.user.employee_id,
        readonly=True,
        required=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )

    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager",
        related="employee_id.parent_id",
        store=True,
        readonly=True,
    )

    request_date = fields.Date(
        string="Request Date",
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )

    required_date = fields.Date(
        required=True,
        string="Required Date",
    )

    procurement_reason = fields.Selection(
        [
            ("inventory_replenishment", "Inventory Replenishment"),
            ("office_supply", "Office Supply Refill"),
            ("equipment_replacement", "Equipment Failure / Replacement"),
            ("new_hire", "New Hire Onboarding"),
        ],
        string="Reason for Request",
        required=True,
    )

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Manager Approved"),
            ("rejected", "Manager Rejected"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    line_ids = fields.One2many(
        "procurement.request.line", "request_id", string="Requested Items"
    )

    total_amount = fields.Float(
        string="Total Amount", compute="_compute_total_amount", store=True
    )

    @api.constrains("line_ids", "required_date")
    def _check_lines(self):
        today = fields.Date.today()
        for record in self:
            if not record.line_ids:
                raise UserError("Purchase Request must have at least one line.")
            elif record.required_date < today:
                raise ValidationError(
                    "Required Date Can't be before Request Create Date"
                )

    @api.depends("line_ids.subtotal")
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped("subtotal"))

    def action_submit(self):
        for record in self:
            if not self.line_ids:
                raise ValidationError("Please Enter At Least One Item")
            record.write({"status": "submitted"})

    def action_approve(self):
        for record in self:
            record.write({"status": "approved"})

    def action_reject(self):
        for record in self:
            record.write({"status": "rejected"})

    def action_reset_to_draft(self):
        for record in self:
            record.write({"status": "draft"})

    @api.model
    def create(self, vals):

        if not vals.get("name") or vals.get("name") == "Request ID":
            vals["name"] = self.env["ir.sequence"].next_by_code("procurement.request")

        return super().create(vals)
