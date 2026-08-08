from auditfleet.models.schemas import ApprovalState, AuditReport


def can_persist(report: AuditReport) -> bool:
    """Hard gate: persistence/dispatch is allowed only after explicit human approval."""
    return report.state == ApprovalState.APPROVED


def assert_can_persist(report: AuditReport) -> None:
    if not can_persist(report):
        raise PermissionError("Report is not APPROVED; persistence and external dispatch are blocked.")
