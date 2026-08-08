from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalState(StrEnum):
    CREATED = "CREATED"
    PROCESSING = "PROCESSING"
    DRAFT = "DRAFT"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISE = "REVISE"


class AuditTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"AUD-{uuid4().hex[:10].upper()}")
    title: str = Field(min_length=3, max_length=160)
    audit_type: str = Field(default="E-Commerce Audit", max_length=120)
    source_name: str = Field(default="inline.txt", max_length=255)
    raw_text: str = Field(min_length=1)
    region: str = Field(default="asia-east1")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Evidence(BaseModel):
    source: str
    reference: str
    excerpt: str = Field(min_length=1, max_length=1200)


class Finding(BaseModel):
    finding_id: str = Field(pattern=r"^F-\d{3,}$")
    title: str
    category: str
    severity: Severity
    description: str
    evidence: list[Evidence] = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str

    @model_validator(mode="after")
    def evidence_is_mandatory(self) -> "Finding":
        if not self.evidence:
            raise ValueError("No finding without evidence.")
        return self


class AgentTrace(BaseModel):
    agent: Literal[
        "planner",
        "evidence_reviewer",
        "compliance_auditor",
        "risk_analyst",
        "report_gatekeeper",
    ]
    summary: str


class AuditReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"RPT-{uuid4().hex[:10].upper()}")
    task_id: str
    audit_type: str
    executive_summary: str
    findings: list[Finding]
    traces: list[AgentTrace] = Field(default_factory=list)
    state: ApprovalState = ApprovalState.AWAITING_APPROVAL
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved_at: datetime | None = None
    reviewer_note: str | None = None

    @model_validator(mode="after")
    def final_reports_must_have_evidence(self) -> "AuditReport":
        for finding in self.findings:
            if not finding.evidence:
                raise ValueError("Every finding must include at least one evidence item.")
        return self


class ApprovalDecision(BaseModel):
    decision: Literal["APPROVE", "REJECT", "REVISE"]
    reviewer: str = Field(default="Human Auditor", min_length=2, max_length=120)
    note: str | None = Field(default=None, max_length=2000)
