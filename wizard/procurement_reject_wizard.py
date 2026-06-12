from odoo import models, fields, api


class ProcurementRejectReasonWizard(models.TransientModel):
    _name = "procurement.reject.wizard"
    _description = "Reject Procurement Request"

    wizard_rejection_reason = fields.Text(required=True, string="Rejection Reason")

    request_id = fields.Many2one(
        "procurement.request",
        required=True,
    )

    def action_confirm_reject(self):
        self.ensure_one()
        self.request_id.write(
            {
                "status": "rejected",
                "rejection_reason": self.wizard_rejection_reason,
            }
        )
        return {"type": "ir.actions.act_window_close"}
