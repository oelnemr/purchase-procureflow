from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    procurement_request_id = fields.Many2one(
        "procurement.request",
        string="Procurement Request",
        readonly=True,
        copy=False,
    )

    requested_employee_id = fields.Many2one(
        "hr.employee",
        string="Requested By",
        related="procurement_request_id.employee_id",
        store=True,
        readonly=True,
    )

    approver_employee_id = fields.Many2one(
        "hr.employee",
        string="Approved By",
        related="procurement_request_id.manager_id",
        store=True,
        readonly=True,
    )
