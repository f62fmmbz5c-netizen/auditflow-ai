from __future__ import annotations

import json
from typing import Any

from auditfleet.core.config import get_settings
from auditfleet.core.pii_masker import mask_pii
from auditfleet.mock.mock_responses import build_demo_report
from auditfleet.models.schemas import AuditReport, AuditTask

MODEL = "gemini-3.6-flash"


def build_adk_fleet() -> dict[str, Any]:
    """Build the Google ADK fleet lazily so deterministic demo mode stays dependency-light."""
    try:
        from google.adk.agents import Agent
        from google.adk.models import Gemini
    except ImportError as exc:  # pragma: no cover - only exercised in live deployment
        raise RuntimeError("google-adk is required for live mode") from exc

    model = Gemini(model=MODEL)

    planner = Agent(
        name="planner",
        model=model,
        instruction=(
            "You are the AuditFleet planner. Decompose the audit request into evidence, compliance, "
            "and risk workstreams. Never invent evidence."
        ),
    )
    evidence = Agent(
        name="evidence_reviewer",
        model=model,
        instruction="Identify only findings directly supported by supplied evidence and quote a precise source reference.",
    )
    compliance = Agent(
        name="compliance_auditor",
        model=model,
        instruction="Assess control design and compliance implications. Distinguish facts from assumptions.",
    )
    risk = Agent(
        name="risk_analyst",
        model=model,
        instruction="Assign severity and confidence based only on supported evidence and likely business impact.",
    )
    gatekeeper = Agent(
        name="report_gatekeeper",
        model=model,
        instruction=(
            "Produce a structured audit draft. Enforce the rule: no finding without evidence. "
            "The final state must be AWAITING_APPROVAL; never auto-approve or dispatch."
        ),
    )
    return {
        "planner": planner,
        "evidence_reviewer": evidence,
        "compliance_auditor": compliance,
        "risk_analyst": risk,
        "report_gatekeeper": gatekeeper,
    }


def run_audit(task: AuditTask) -> AuditReport:
    """Run AuditFleet in deterministic demo mode or Google model live mode."""
    settings = get_settings()
    masked = mask_pii(task.raw_text)

    if settings.demo_mode:
        return build_demo_report(task, masked.text)

    # MVP live path: use the Google Gen AI SDK with a strict structured schema.
    # ADK fleet objects are built and validated here; richer delegation is Phase 2.
    build_adk_fleet()
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("google-genai is required for live mode") from exc

    client = genai.Client()
    prompt = f"""
You are AuditFleet, a multi-agent audit control system.
Simulate these roles in order: planner, evidence reviewer, compliance auditor, risk analyst, report gatekeeper.
Return only findings backed by exact evidence from the supplied masked audit text.
No finding without evidence. Final state must be AWAITING_APPROVAL.

Audit type: {task.audit_type}
Source: {task.source_name}
Masked audit text:\n{masked.text}
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AuditReport,
        ),
    )
    if response.parsed:
        report = response.parsed
    else:
        report = AuditReport.model_validate(json.loads(response.text))

    report.task_id = task.task_id
    report.audit_type = task.audit_type
    report.state = "AWAITING_APPROVAL"
    client.close()
    return report
