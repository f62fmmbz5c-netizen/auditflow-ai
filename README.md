# AuditFlow AI

AuditFleet AI is an evidence-backed multi-agent audit control system designed around three rules:

1. **PII is masked before model processing.**
2. **No finding without evidence.**
3. **No persistence or external dispatch before human approval.**

## Architecture

```text
Auditor / API / Streamlit
        |
        v
Security Gateway -> PII Masker
        |
        v
Planner -> Evidence Reviewer -> Compliance Auditor -> Risk Analyst -> Report Gatekeeper
        |
        v
AWAITING_APPROVAL
        |
  Human APPROVE / REVISE
        |
        v
Persistence gate / Cloud deployment
```

## Phase 1 features

- Deterministic offline demo mode
- Optional Google ADK / Gemini live mode
- Structured Pydantic audit schemas
- Evidence-backed findings
- PII masking
- Mandatory human-in-the-loop approval
- FastAPI endpoints
- Streamlit demo console
- Docker + Cloud Build + Cloud Run scaffold
- Unit tests for PII, agent output, and approval gating

## Quick start (offline demo)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# DEMO_MODE=true is already the default
pytest -q
streamlit run auditfleet/app.py
```

## REST API

```bash
uvicorn auditfleet.api:app --reload --port 8080
```

Health check:

```bash
curl http://localhost:8080/health
```

Create an audit:

```bash
curl -X POST http://localhost:8080/api/audits \
  -H 'Content-Type: application/json' \
  -d '{
    "title":"E-Commerce Audit",
    "audit_type":"E-Commerce Audit",
    "source_name":"sample_audit.txt",
    "raw_text":"admin01 role=admin MFA=false\nrefund TX-1 same user initiated and approved"
  }'
```

## Live Google mode

Set `DEMO_MODE=false` and configure either a Gemini API key or Google Cloud credentials. Live mode validates/builds the ADK fleet and requests a structured `AuditReport` from the Google Gen AI SDK.

## Cloud Run

The container binds to `0.0.0.0` and uses the Cloud Run supplied `PORT` environment variable.

```bash
gcloud builds submit --config cloudbuild.yaml
```

Before deploying, create the Artifact Registry repository referenced by `cloudbuild.yaml`, configure least-privilege service accounts, and set secrets through Google Cloud rather than committing credentials.

## Status

**v0.1.0 — Phase 1 MVP.** Firestore persistence, production PDF ingestion, richer ADK delegation, OpenTelemetry exporters, and policy-specific control libraries are Phase 2.
