from odoo import models, fields, api
from odoo.exceptions import ValidationError, AccessError, UserError


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
        if self.request_id.manager_id.user_id != self.env.user:
            raise UserError("Only the assigned manager can reject.")
        self.request_id.write(
            {
                "status": "rejected",
                "rejection_reason": self.wizard_rejection_reason,
            }
        )
        procurement = self.env["procurement.request"].browse(int(self.request_id))
        procurement.mark_activity_as_done()

        return {"type": "ir.actions.act_window_close"}
