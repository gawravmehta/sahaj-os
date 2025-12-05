from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime


def generate_agreement_pdf(artifact: dict) -> BytesIO:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Custom Styles
    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # Title
    story.append(Paragraph("Consent Agreement", title_style))
    story.append(Spacer(1, 12))

    # Agreement Details
    agreement_id = artifact.get("agreement_id", "N/A")
    timestamp = artifact.get("timestamp", "N/A")

    story.append(Paragraph(f"<b>Agreement ID:</b> {agreement_id}", normal_style))
    story.append(Paragraph(f"<b>Date:</b> {timestamp}", normal_style))
    story.append(Spacer(1, 12))

    # Data Principal
    dp = artifact.get("artifact", {}).get("data_principal", {})
    story.append(Paragraph("Data Principal", heading_style))
    story.append(Paragraph(f"<b>ID:</b> {dp.get('dp_id', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Residency:</b> {dp.get('dp_residency', 'N/A')}", normal_style))
    story.append(Spacer(1, 12))

    # Data Fiduciary
    df = artifact.get("artifact", {}).get("data_fiduciary", {})
    story.append(Paragraph("Data Fiduciary", heading_style))
    story.append(Paragraph(f"<b>ID:</b> {df.get('df_id', 'N/A')}", normal_style))
    story.append(Paragraph(f"<b>Agreement Date:</b> {df.get('agreement_date', 'N/A')}", normal_style))
    story.append(Spacer(1, 12))

    # Consent Scope
    story.append(Paragraph("Consent Scope", heading_style))
    story.append(Spacer(1, 6))

    data_elements = artifact.get("artifact", {}).get("consent_scope", {}).get("data_elements", [])

    for de in data_elements:
        de_title = de.get("title", "Unknown Data Element")
        story.append(Paragraph(f"<b>{de_title}</b>", styles["Heading3"]))

        consents = de.get("consents", [])
        if consents:
            table_data = [["Purpose", "Status", "Expiry"]]
            for consent in consents:
                purpose = consent.get("purpose_title", "N/A")
                status = consent.get("consent_status", "N/A")
                expiry = consent.get("consent_expiry_period", "N/A")
                table_data.append([purpose, status, expiry])

            t = Table(table_data, colWidths=[300, 80, 140])
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(t)
        else:
            story.append(Paragraph("No consents recorded for this element.", normal_style))

        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer
