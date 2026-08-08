from __future__ import annotations

from auditfleet.models.schemas import AgentTrace, AuditReport, AuditTask, Evidence, Finding, Severity


def build_demo_report(task: AuditTask, masked_text: str) -> AuditReport:
    """Return deterministic findings so the demo works without cloud credentials."""
    source = task.source_name
    lower = masked_text.lower()
    findings: list[Finding] = []

    if "mfa=false" in lower or "mfa disabled" in lower or "without mfa" in lower:
        findings.append(
            Finding(
                finding_id="F-001",
                title="Privileged account without MFA",
                category="ACCESS_CONTROL",
                severity=Severity.HIGH,
                description="A privileged account is shown without multi-factor authentication.",
                evidence=[Evidence(source=source, reference="matched text", excerpt="admin01 role=admin MFA=false")],
                confidence=0.98,
                recommendation="Enforce MFA for every privileged account and block exceptions by policy.",
            )
        )

    if "refund" in lower and ("same user" in lower or "self-approved" in lower or "approver=creator" in lower):
        findings.append(
            Finding(
                finding_id=f"F-{len(findings)+1:03d}",
                title="Refund approval lacks segregation of duties",
                category="SEGREGATION_OF_DUTIES",
                severity=Severity.CRITICAL,
                description="The same identity can initiate and approve a refund transaction.",
                evidence=[Evidence(source=source, reference="matched text", excerpt="refund ... same user initiated and approved")],
                confidence=0.96,
                recommendation="Require independent refund approval above the configured materiality threshold.",
            )
        )

    if "failed login" in lower and ("50" in lower or "100" in lower or "repeated" in lower):
        findings.append(
            Finding(
                finding_id=f"F-{len(findings)+1:03d}",
                title="Repeated failed logins not escalated",
                category="SECURITY_MONITORING",
                severity=Severity.MEDIUM,
                description="Repeated authentication failures are present without evidence of lockout or escalation.",
                evidence=[Evidence(source=source, reference="matched text", excerpt="repeated failed login attempts detected")],
                confidence=0.88,
                recommendation="Add alerting, rate limiting, and lockout thresholds for repeated authentication failures.",
            )
        )

    if not findings:
        findings.append(
            Finding(
                finding_id="F-001",
                title="Manual review required for unclassified evidence",
                category="EVIDENCE_REVIEW",
                severity=Severity.LOW,
                description="The deterministic demo did not match a predefined control exception.",
                evidence=[Evidence(source=source, reference="input sample", excerpt=masked_text[:300])],
                confidence=0.60,
                recommendation="Review the evidence manually or switch to ADK live mode for broader analysis.",
            )
        )

    traces = [
        AgentTrace(agent="planner", summary="Decomposed the audit into evidence, compliance, and risk workstreams."),
        AgentTrace(agent="evidence_reviewer", summary="Mapped each candidate issue to source evidence."),
        AgentTrace(agent="compliance_auditor", summary="Evaluated control design and segregation-of-duties concerns."),
        AgentTrace(agent="risk_analyst", summary="Assigned severity and confidence to supported findings."),
        AgentTrace(agent="report_gatekeeper", summary="Blocked unsupported findings and prepared the draft for human approval."),
    ]

    return AuditReport(
        task_id=task.task_id,
        audit_type=task.audit_type,
        executive_summary=f"AuditFleet identified {len(findings)} evidence-backed finding(s). Human approval is required before persistence or dispatch.",
        findings=findings,
        traces=traces,
    )
