from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from auditfleet.agents import run_audit
from auditfleet.core.config import get_settings
from auditfleet.core.pii_masker import mask_pii
from auditfleet.models.schemas import ApprovalState, AuditTask

SAMPLE = """E-Commerce Audit Log\n2026-08-08 admin01 role=admin MFA=false email=admin@example.com\n2026-08-08 refund TX-1042 amount=25000 same user initiated and approved\n2026-08-08 repeated failed login attempts: 50 for account customer_991\nCard on file: 4111 1111 1111 1111\n"""

st.set_page_config(page_title="AuditFleet AI", page_icon="🛡️", layout="wide")
st.title("🛡️ AuditFleet AI")
st.caption("Evidence-backed multi-agent auditing with mandatory human approval")

settings = get_settings()
st.sidebar.metric("Mode", "DEMO" if settings.demo_mode else "LIVE ADK")
st.sidebar.write(f"Region: `{settings.auditfleet_region}`")
st.sidebar.info("Policy: No finding without evidence. No persistence before human approval.")

text = st.text_area("Audit evidence", value=SAMPLE, height=250)
source = st.text_input("Source name", value="sample_audit.txt")
audit_type = st.selectbox("Audit type", ["E-Commerce Audit", "Access Control Audit", "Compliance Review"])

if st.button("Run AuditFleet", type="primary"):
    task = AuditTask(title="Interactive audit", audit_type=audit_type, source_name=source, raw_text=text)
    masked = mask_pii(text)
    st.session_state.report = run_audit(task)
    st.session_state.mask_counts = masked.counts

report = st.session_state.get("report")
if report:
    st.subheader("Draft Audit Report")
    c1, c2, c3 = st.columns(3)
    c1.metric("Findings", len(report.findings))
    c2.metric("State", report.state.value)
    c3.metric("PII masked", sum(st.session_state.get("mask_counts", {}).values()))
    st.write(report.executive_summary)

    for finding in report.findings:
        with st.expander(f"{finding.finding_id} · {finding.severity.value} · {finding.title}", expanded=True):
            st.write(finding.description)
            st.write(f"**Confidence:** {finding.confidence:.0%}")
            st.write(f"**Recommendation:** {finding.recommendation}")
            st.write("**Evidence**")
            for ev in finding.evidence:
                st.code(f"{ev.source} · {ev.reference}\n{ev.excerpt}")

    st.subheader("Mandatory Human-in-the-Loop")
    col1, col2 = st.columns(2)
    if col1.button("APPROVE", disabled=report.state != ApprovalState.AWAITING_APPROVAL):
        report.state = ApprovalState.APPROVED
        report.approved_at = datetime.now(timezone.utc)
        st.session_state.report = report
        st.rerun()
    if col2.button("REJECT / REVISE", disabled=report.state != ApprovalState.AWAITING_APPROVAL):
        report.state = ApprovalState.REVISE
        st.session_state.report = report
        st.rerun()

    if report.state == ApprovalState.APPROVED:
        st.success("Approved. Persistence/dispatch gate is now open.")
    elif report.state == ApprovalState.REVISE:
        st.warning("Revision requested. Persistence/dispatch remains blocked.")
    else:
        st.error("AWAITING_APPROVAL — persistence/dispatch is blocked.")
