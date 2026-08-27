from app.db import repository
from app.ingestion.pipeline import ingest_text_document

SAMPLE_KB_TEMPLATES = [
    {
        "id": "kb-refund-policy",
        "filename": "Sample KB - Refund & Cancellation.pdf",
        "description": "Refund windows, exceptions, and cancellation timeline.",
        "pages": [
            "Refund policy: Physical items can be refunded within 30 days from delivery. "
            "Digital products are non-refundable unless the product is defective.",
            "Cancellation policy: Subscription cancellations are effective at the end of the billing cycle. "
            "No prorated refunds are issued for partial months unless a billing error is confirmed.",
            "Escalation policy: If a customer requests a refund outside policy, gather order ID and reason, "
            "then escalate to a supervisor review queue.",
        ],
    },
    {
        "id": "kb-account-access",
        "filename": "Sample KB - Account Access.pdf",
        "description": "Password reset, lockout, and account verification flow.",
        "pages": [
            "Password reset flow: User clicks Forgot Password, enters registered email, and receives a reset link. "
            "Reset links expire in 15 minutes.",
            "Lockout policy: Accounts are locked for 30 minutes after 5 failed login attempts. "
            "Support cannot bypass lockout manually.",
            "Identity verification: For account recovery, collect registered email and last 4 digits of payment method "
            "before escalating.",
        ],
    },
    {
        "id": "kb-shipping-support",
        "filename": "Sample KB - Shipping & Delivery.pdf",
        "description": "Shipping SLAs, delays, and missing package guidance.",
        "pages": [
            "Shipping SLA: Orders process in 1-2 business days and standard delivery takes 5-7 business days. "
            "Tracking email is sent when the order ships.",
            "Delay guidance: If no tracking update appears for 48 hours, apologize and open a carrier investigation ticket.",
            "Missing package workflow: Confirm shipping address, verify delivery timestamp, and advise customer to wait 24 hours "
            "before escalating to loss claim.",
        ],
    },
]


def list_sample_kb() -> list[dict]:
    return [
        {"id": item["id"], "filename": item["filename"], "description": item["description"]}
        for item in SAMPLE_KB_TEMPLATES
    ]


def bootstrap_sample_kb() -> dict:
    created: list[dict] = []
    existing: list[dict] = []

    for template in SAMPLE_KB_TEMPLATES:
        current = repository.get_document_by_filename(template["filename"])
        if current and current.get("status") == "indexed":
            existing.append(current)
            continue
        doc = ingest_text_document(template["filename"], template["pages"])
        created.append(doc)

    return {"created": created, "existing": existing}
