from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException

from auditfleet.agents import run_audit
from auditfleet.core.security import can_persist
from auditfleet.models.schemas import ApprovalDecision, ApprovalState, AuditReport, AuditTask

app = FastAPI(title="AuditFleet AI", version="0.1.0")
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
    if report_id not in _REPORTS:
        raise HTTPException(status_code=404, detail="Report not found")
    return _REPORTS[report_id]


@app.post("/api/audits/{report_id}/approve", response_model=AuditReport)
def approve_audit(report_id: str, decision: ApprovalDecision) -> AuditReport:
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.state not in {ApprovalState.AWAITING_APPROVAL, ApprovalState.REVISE}:
        raise HTTPException(status_code=409, detail=f"Invalid approval transition from {report.state}")

    if decision.decision == "APPROVE":
        report.state = ApprovalState.APPROVED
        report.approved_at = datetime.now(timezone.utc)
    elif decision.decision == "REJECT":
        report.state = ApprovalState.REJECTED
    else:
        report.state = ApprovalState.REVISE
    report.reviewer_note = decision.note
    _REPORTS[report_id] = report
    return report


@app.get("/api/audits/{report_id}/persistence-status")
def persistence_status(report_id: str) -> dict[str, bool | str]:
    report = _REPORTS.get(report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"report_id": report_id, "can_persist": can_persist(report)}
