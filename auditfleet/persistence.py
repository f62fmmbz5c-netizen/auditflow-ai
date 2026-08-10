from google.cloud import firestore

from auditfleet.models.schemas import AuditReport


COLLECTION_NAME = "audit_reports"


def get_firestore_client() -> firestore.Client:
    """Create a Firestore client using Cloud Run's service account."""
    return firestore.Client()


def save_audit_report(report: AuditReport) -> str:
    """Persist an approved audit report to Firestore."""
    client = get_firestore_client()

    document = report.model_dump(mode="json")

    client.collection(COLLECTION_NAME).document(report.report_id).set(document)

    return report.report_id


def get_persisted_audit_report(report_id: str) -> dict | None:
    """Retrieve a persisted audit report from Firestore."""
    client = get_firestore_client()

    snapshot = (
        client.collection(COLLECTION_NAME)
        .document(report_id)
        .get()
    )

    if not snapshot.exists:
        return None

    return snapshot.to_dict()
