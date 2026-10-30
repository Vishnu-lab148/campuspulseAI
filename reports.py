from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def build_pdf_report(summary, students_df, flagged_df):
    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("CampusPulse AI — Student Support Summary", styles["Title"]),
        Spacer(1, 8),
        Paragraph(
            f"Students: {summary['total']} &nbsp;&nbsp; Average attendance: {summary['attendance']:.1f}% "
            f"&nbsp;&nbsp; Average score: {summary['score']:.1f}/100 &nbsp;&nbsp; Support flags: {summary['flagged']}",
            styles["BodyText"]
        ),
        Spacer(1, 14),
        Paragraph("Current filtered student records (synthetic demo data unless connected to Db2)", styles["Heading2"]),
    ]
    columns = ["student_id", "name", "course", "attendance", "score"]
    data = [columns]
    for _, row in students_df[columns].head(40).iterrows():
        data.append([str(row[c]) for c in columns])
    table = Table(data, repeatRows=1, colWidths=[100, 140, 100, 100, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#183153")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), .35, colors.HexColor("#b9c7d8")),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#edf3f9")]),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("PADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Responsible use: support flags are transparent indicators for educator review, not diagnoses or automated decisions.", styles["Italic"]))
    doc.build(story)
    return output.getvalue()
