import os

os.environ["DEMO_MODE"] = "true"

from auditfleet.agents import run_audit
from auditfleet.core.config import get_settings
from auditfleet.models.schemas import ApprovalState, AuditTask


def test_demo_fleet_returns_evidence_backed_findings():
    get_settings.cache_clear()
    task = AuditTask(
        title="Test audit",
        raw_text="admin01 role=admin MFA=false\nrefund 1 same user initiated and approved",
        source_name="test.txt",
    )
    report = run_audit(task)
    assert report.state == ApprovalState.AWAITING_APPROVAL
    assert len(report.findings) >= 2
    assert all(f.evidence for f in report.findings)
