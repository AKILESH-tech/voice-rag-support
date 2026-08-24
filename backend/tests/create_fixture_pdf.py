#!/usr/bin/env python
"""Generate tests/fixtures/policy.pdf for testing."""
from fpdf import FPDF
import os

def create_policy_pdf():
    pdf = FPDF()
    pages_content = [
        ("Support Policy Overview", "This document outlines the support policy for all customers. Our team is available 24/7 for critical issues. Standard support hours are Monday to Friday, 9 AM to 6 PM EST."),
        ("Ticket Submission Guidelines", "All support tickets must include a detailed description of the issue. Attach relevant screenshots or logs. Priority levels: Critical, High, Medium, Low. Critical tickets are addressed within 1 hour."),
        ("Escalation Procedures", "If your issue is not resolved within the SLA timeframe, contact your account manager. Escalation paths: Level 1 Support > Level 2 Engineering > Management. SLA for critical: 1h, High: 4h, Medium: 24h, Low: 72h."),
        ("Refund and Billing Policy", "Refund requests must be submitted within 30 days of purchase. Approved refunds are processed within 5-7 business days. For billing disputes, contact billing@support.example.com with your invoice number."),
        ("Service Level Agreements", "Our uptime guarantee is 99.9% for all paid plans. Downtime excluding scheduled maintenance counts toward SLA. Credits are issued automatically for SLA breaches. Review your dashboard for real-time status."),
    ]
    for title, content in pages_content:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        pdf.set_font("Helvetica", size=12)
        pdf.multi_cell(0, 8, content)
    out_path = os.path.join(os.path.dirname(__file__), "fixtures", "policy.pdf")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    pdf.output(out_path)
    print(f"Created: {out_path}")

if __name__ == "__main__":
    create_policy_pdf()
