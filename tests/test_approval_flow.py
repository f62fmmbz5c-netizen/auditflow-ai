from auditfleet.core.security import assert_can_persist, can_persist
from auditfleet.models.schemas import ApprovalState, AuditReport, Evidence, Finding, Severity


def make_report() -> AuditReport:
    return AuditReport(
        task_id="AUD-TEST",
        audit_type="Test",
        executive_summary="Test report",
        findings=[
            Finding(
                finding_id="F-001",
                title="Test finding",
                category="TEST",
                severity=Severity.LOW,
                description="Supported finding",
                evidence=[Evidence(source="x", reference="line 1", excerpt="evidence")],
                confidence=0.9,
                recommendation="Review",
            )
        ],
    )


def test_persistence_blocked_before_approval():
    report = make_report()
    assert not can_persist(report)
    try:
        assert_can_persist(report)
        assert False, "Expected PermissionError"
    except PermissionError:
        pass


def test_persistence_allowed_after_approval():
    report = make_report()
    report.state = ApprovalState.APPROVED
    assert can_persist(report)
    assert_can_persist(report)
