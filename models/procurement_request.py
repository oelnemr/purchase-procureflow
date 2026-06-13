from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError, UserError


class ProcurementRequest(models.Model):
    _name = "procurement.request"
    _description = "Procurement Requests"
    _order = "request_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # Request Referance Placeholder Used to generate the sequence
    name = fields.Char(
        default="Request ID",
        index=True,
        readonly=True,
        required=True,
        string="Request Referance",
    )

    # User/Employee User Who Created The Request
    employee_id = fields.Many2one(
        "hr.employee",
        string="Created By",
        default=lambda self: self.env.user.employee_id,
        readonly=True,
        required=True,
    )

    # Manager Of The User Who Created The Request [Approver]
    manager_id = fields.Many2one(
        "hr.employee",
        string="Manager",
        related="employee_id.parent_id",
        store=True,
        readonly=True,
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        related="employee_id.department_id",
        store=True,
        readonly=True,
    )
    # used to show/hide button based on requester/approver [XML]
    requester_user_id = fields.Many2one(
        "res.users",
        related="employee_id.user_id",
        store=True,
        readonly=True,
    )

    # used to show/hide button based on requester/approver [XML]
    approver_user_id = fields.Many2one(
        "res.users",
        related="manager_id.user_id",
        store=True,
        readonly=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        domain="[('supplier_rank', '>', 0)]",
        required=True,
    )

    request_date = fields.Date(
        string="Created At",
        default=lambda self: fields.Date.context_today(self),
        readonly=True,
    )

    required_date = fields.Date(
        required=True,
        string="Need-By Date",
    )

    procurement_reason = fields.Selection(
        [
            ("inventory_replenishment", "Inventory Replenishment"),
            ("office_supply", "Office Supply Refill"),
            ("equipment_replacement", "Equipment Failure / Replacement"),
            ("new_hire", "New Hire Onboarding"),
            ("project_expense", "Project Expense"),
        ],
        string="Justification",
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
        tracking=True,
    )

    rejection_reason = fields.Text(
        string="Rejection Reason",
        readonly=True,
    )

    line_ids = fields.One2many(
        "procurement.request.line", "request_id", string="Requested Items"
    )

    total_amount = fields.Float(
        string="Total Amount", compute="_compute_total_amount", store=True
    )

    rfq_id = fields.Many2one("purchase.order", string="RFQ", copy=False)

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

    def mark_activity_as_done(self):

        for record in self:
            todo_activity = self.env["mail.activity"].search(
                [
                    ("res_model", "=", record._name),
                    ("res_id", "=", record.id),
                    (
                        "activity_type_id",
                        "=",
                        self.env.ref("mail.mail_activity_data_todo").id,
                    ),
                    (
                        "summary",
                        "=",
                        "Procurement Request Approval",
                    ),
                ],
                limit=1,
            )

            if todo_activity:
                todo_activity.action_done()

    def action_submit(self):
        for record in self:
            manager = (
                record.employee_id.parent_id.user_id
                or record.employee_id.department_id.manager_id.user_id
            )

            if record.employee_id.user_id != self.env.user:
                raise UserError("Only the requester can submit this request.")

            # Prevent empty requests
            if not record.line_ids:
                raise UserError("Please Enter At Least One Item")
            # Every request must have an approver
            elif not record.manager_id:
                raise UserError("No manager found for approval.")

            record.write({"status": "submitted"})

            self.activity_schedule(
                activity_type_id=self.env.ref("mail.mail_activity_data_todo").id,
                user_id=manager.id,
                summary="Procurement Request Approval",
                note=f"Request {record.name} needs your approval",
                date_deadline=fields.Date.today(),
            )

    def action_approve(self):
        for record in self:
            if record.manager_id.user_id != self.env.user:
                raise UserError("Only the assigned Manager can approve.")

        order_lines = []
        for line in record.line_ids:
            order_lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_name.id,
                        "name": line.product_name.display_name,
                        "product_qty": line.quantity,
                        "price_unit": line.unit_price,
                        "product_uom": line.product_name.uom_id.id,
                        "date_planned": fields.Date.today(),
                    },
                )
            )

        rfq = self.env["purchase.order"].create(
            {
                "partner_id": record.partner_id.id,
                "origin": record.name,
                "order_line": order_lines,
                "state": "draft",
            }
        )

        record.write(
            {
                "status": "approved",
                "rfq_id": rfq.id,
            }
        )

        record.message_post(
            body=f"RFQ {rfq.name} created automatically after approval."
        )
        self.mark_activity_as_done()

    # ======== reject login function moved to wizard/procurement_reject_wizard.py ==========
    # def action_reject(self):
    #     for record in self:
    #         if record.manager_id.user_id != self.env.user:
    #             raise UserError("Only the assigned manager can reject.")
    #         record.write({"status": "rejected"})

    def action_reset_to_draft(self):
        for record in self:
            if record.employee_id.user_id != self.env.user:
                raise UserError("Only the requester can reset this request.")
            if record.status != "submitted":
                raise UserError("Only submitted requests can be reset.")
            record.write({"status": "draft"})

    @api.model
    def create(self, vals):

        if not vals.get("name") or vals.get("name") == "Request ID":
            vals["name"] = self.env["ir.sequence"].next_by_code("procurement.request")

        return super().create(vals)
