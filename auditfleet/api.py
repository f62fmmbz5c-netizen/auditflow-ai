from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from auditfleet.agents import run_audit
from auditfleet.core.security import can_persist
from auditfleet.models.schemas import (
    ApprovalDecision,
    ApprovalState,
    AuditReport,
    AuditTask,
)
from auditfleet.persistence import (
    get_persisted_audit_report,
    save_audit_report,
)


app = FastAPI(title="AuditFlow AI", version="0.2.0")

# Runtime cache only.
# Approved reports are permanently stored in Firestore.
_REPORTS: dict[str, AuditReport] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/audits", response_model=AuditReport)
def create_audit(task: AuditTask) -> AuditReport:
    report = run_audit(task)
    _REPORTS[report.report_id] = report
    return report


@app.get("/api/audits/{report_id}", response_model=AuditReport)
def get_audit(report_id: str) -> AuditReport:
    # First check the current Cloud Run instance memory.
    report = _REPORTS.get(report_id)

    if report is not None:
        return report

    # If Cloud Run restarted, recover approved reports from Firestore.
    persisted = get_persisted_audit_report(report_id)

    if persisted is None:
        raise HTTPException(status_code=404, detail="Report not found")

    report = AuditReport.model_validate(persisted)
    _REPORTS[report_id] = report

    return report


@app.post("/api/audits/{report_id}/approve", response_model=AuditReport)
def approve_audit(
    report_id: str,
    decision: ApprovalDecision,
) -> AuditReport:
    report = _REPORTS.get(report_id)

    if report is None:
        persisted = get_persisted_audit_report(report_id)

        if persisted is not None:
            report = AuditReport.model_validate(persisted)

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.state not in {
        ApprovalState.AWAITING_APPROVAL,
        ApprovalState.REVISE,
    }:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid approval transition from {report.state}",
        )

    if decision.decision == "APPROVE":
        report.state = ApprovalState.APPROVED
        report.approved_at = datetime.now(timezone.utc)

    elif decision.decision == "REJECT":
        report.state = ApprovalState.REJECTED

    else:
        report.state = ApprovalState.REVISE

    report.reviewer_note = decision.note
    _REPORTS[report_id] = report

    # Mandatory human-in-the-loop persistence gate.
    if report.state == ApprovalState.APPROVED:
        if not can_persist(report):
            raise HTTPException(
                status_code=409,
                detail="Report failed persistence security gate",
            )

        try:
            save_audit_report(report)
        except Exception as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Firestore persistence failed: {exc}",
            ) from exc

    return report


@app.get("/api/audits/{report_id}/persistence-status")
def persistence_status(report_id: str) -> dict[str, bool | str]:
    report = _REPORTS.get(report_id)

    if report is not None:
        persisted = get_persisted_audit_report(report_id)

        return {
            "report_id": report_id,
            "can_persist": can_persist(report),
            "persisted": persisted is not None,
        }

    persisted = get_persisted_audit_report(report_id)

    if persisted is None:
        raise HTTPException(status_code=404, detail="Report not found")

    report = AuditReport.model_validate(persisted)

    return {
        "report_id": report_id,
        "can_persist": can_persist(report),
        "persisted": True,
    }
