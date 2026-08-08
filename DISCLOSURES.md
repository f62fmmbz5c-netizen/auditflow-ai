# AuditFleet AI Disclosures

## AI use
AuditFleet uses generative AI to assist auditors with evidence review, compliance analysis, risk classification, and draft report preparation. It is an assistive system and does not replace professional judgment.

## Mandatory human approval
Draft findings enter `AWAITING_APPROVAL`. External dispatch and durable persistence are blocked until a human reviewer explicitly changes the report state to `APPROVED`.

## Evidence policy
**No finding without evidence.** Every finding must contain at least one source reference and excerpt. Unsupported model output must be discarded by the report gatekeeper.

## Privacy and security
Audit input is passed through a PII masking layer before model processing. The Phase 1 masker covers common email, Taiwan ID, US SSN, mobile phone, and payment-card patterns. Production deployments should add organization-specific DLP policies and Google Cloud IAM controls.

## Demo mode
`DEMO_MODE=true` uses deterministic local responses and requires no cloud credential. This protects live demonstrations from quota, network, or credential failures and must be clearly disclosed during judging.

## Limitations
The Phase 1 PDF path is intentionally not enabled in the deterministic reader. Production PDF ingestion, OCR, retention policies, and regulatory mappings require additional controls and testing.
