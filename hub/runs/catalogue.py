"""The closed job catalogue of R1 (F06-2). Nothing here touches Zone H; jobs have no import path to the gate (AC-RUN-12)."""

INTAKE_JOBS = {
    "intake_partner_feed": ("partner_feed",),
    "intake_gateway": ("gateway",),
    "intake_source_messages": ("source_message",),
    "intake_vendor_csv": ("vendor_csv",),
    "backfill_legacy": ("partner_feed", "source_message", "gateway"),
}
OTHER_JOBS = ("rebuild_projection", "verify_projection", "verify_audit", "metrics_snapshot")
JOBS = tuple(sorted(list(INTAKE_JOBS) + list(OTHER_JOBS)))
TRIGGERS = ("manual", "scheduled")
RUN_ROLES = ("quality_lead", "compliance", "integration")  # BEH-RUN-01
