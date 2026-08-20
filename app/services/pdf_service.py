"""PDF report generation using ReportLab."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    NextPageTemplate,
)
from reportlab.lib.enums import TA_CENTER

from app.services.report_data import build_assessment_report_data
from app.models.question import ANSWER_LABELS
from app.models.risk import RISK_LEVEL_LABELS
from app.models.action import ACTION_STATUS_LABELS, PRIORITY_LABELS

DARK_BLUE = colors.HexColor("#0B2545")
BLUE = colors.HexColor("#1565C0")
TEAL = colors.HexColor("#00897B")
GREY = colors.HexColor("#5F6B7A")
LIGHT_GREY = colors.HexColor("#EEF1F5")
RED = colors.HexColor("#C62828")
ORANGE = colors.HexColor("#EF6C00")

LEVEL_COLORS = {
    "critical": RED,
    "high": ORANGE,
    "medium": colors.HexColor("#F9A825"),
    "low": colors.HexColor("#2E7D32"),
}


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontSize=24, textColor=DARK_BLUE, spaceAfter=6, leading=28))
    styles.add(ParagraphStyle(name="ReportSubtitle", fontSize=13, textColor=GREY, spaceAfter=20))
    styles.add(ParagraphStyle(name="SectionHeading", fontSize=15, textColor=DARK_BLUE, spaceBefore=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="SubHeading", fontSize=11.5, textColor=BLUE, spaceBefore=8, spaceAfter=4))
    styles.add(ParagraphStyle(name="Body", fontSize=9.5, textColor=colors.black, leading=13))
    styles.add(ParagraphStyle(name="Small", fontSize=8, textColor=GREY, leading=11))
    styles.add(ParagraphStyle(name="CoverOrg", fontSize=18, textColor=colors.white, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="CoverTitle", fontSize=26, textColor=colors.white, alignment=TA_CENTER, spaceAfter=10))
    styles.add(ParagraphStyle(name="CoverSub", fontSize=12, textColor=colors.white, alignment=TA_CENTER))
    return styles


def _score_table(title, data_dict, styles):
    rows = [["Dominio", "Puntuación"]]
    for name, score in data_dict.items():
        rows.append([name, f"{score:.1f} / 5" if score is not None else "Sin datos"])
    table = Table(rows, colWidths=[10 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _percent_table(data_dict):
    rows = [["Marco / Dominio", "% Cumplimiento"]]
    for name, pct in data_dict.items():
        rows.append([name, f"{pct:.1f}%" if pct is not None else "Sin datos"])
    table = Table(rows, colWidths=[10 * cm, 4 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE0")),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def generate_assessment_pdf(assessment):
    data = build_assessment_report_data(assessment)
    styles = _styles()
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        title=f"Informe - {assessment.name}",
    )

    story = []
    org = data["organization"]

    # --- Cover ---
    cover_table = Table(
        [[Paragraph("Cyber & Privacy Assessment Platform", styles["CoverSub"])],
         [Spacer(1, 40)],
         [Paragraph(org.display_name, styles["CoverOrg"])],
         [Paragraph(assessment.name, styles["CoverTitle"])],
         [Spacer(1, 30)],
         [Paragraph(f"Fecha del informe: {datetime.now().strftime('%d/%m/%Y')}", styles["CoverSub"])],
         [Paragraph("Diagnóstico integral de ciberseguridad y protección de datos personales", styles["CoverSub"])],
         ],
        colWidths=[16.4 * cm],
        rowHeights=[1.2 * cm, 1 * cm, 1.4 * cm, 1.2 * cm, 1 * cm, 0.8 * cm, 0.8 * cm],
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), DARK_BLUE),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    story.append(Spacer(1, 6 * cm))
    story.append(cover_table)
    story.append(PageBreak())

    # --- 1. Resumen ejecutivo ---
    story.append(Paragraph("1. Resumen ejecutivo", styles["SectionHeading"]))
    maturity = data["maturity"]
    gap = data["gap"]
    risk_summary = data["risk_summary"]
    global_score = maturity["global"]
    story.append(
        Paragraph(
            f"Esta evaluación de referencia analiza la postura de ciberseguridad y protección de datos "
            f"personales de <b>{org.display_name}</b>. El nivel de madurez global obtenido es de "
            f"<b>{global_score if global_score is not None else 'N/D'} / 5</b> "
            f"({maturity['global_label']}), con un cumplimiento agregado frente a los marcos evaluados de "
            f"<b>{gap['overall_percent'] if gap['overall_percent'] is not None else 'N/D'}%</b>. "
            f"Se identificaron <b>{risk_summary['counts']['critical']}</b> riesgos críticos y "
            f"<b>{risk_summary['counts']['high']}</b> riesgos altos que requieren atención prioritaria.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Este documento constituye una evaluación de referencia / diagnóstico de cumplimiento y no "
            "sustituye una asesoría legal formal.",
            styles["Small"],
        )
    )

    # --- 2. Cybersecurity Score ---
    story.append(Paragraph("2. Cybersecurity Score", styles["SectionHeading"]))
    story.append(
        Paragraph(
            f"Puntuación de madurez global: <b>{global_score if global_score is not None else 'N/D'} / 5</b> "
            f"&mdash; {maturity['global_label']}",
            styles["Body"],
        )
    )

    # --- 3. Maturity Assessment ---
    story.append(Paragraph("3. Evaluación de madurez por dominio", styles["SectionHeading"]))
    if maturity["by_framework"]:
        story.append(_score_table("Marco", maturity["by_framework"], styles))
    story.append(Spacer(1, 10))
    if maturity["by_domain"]:
        story.append(_score_table("Dominio", maturity["by_domain"], styles))

    story.append(PageBreak())

    # --- 4. ISO 27001 Gap Analysis ---
    story.append(Paragraph("4. Gap Analysis ISO/IEC 27001:2022", styles["SectionHeading"]))
    iso27001_pct = gap["by_framework"].get("ISO/IEC 27001:2022 - Sistema de Gestión de Seguridad de la Información")
    story.append(
        Paragraph(
            f"Cumplimiento ISO/IEC 27001:2022: <b>{iso27001_pct}%</b>" if iso27001_pct is not None else "Sin datos suficientes.",
            styles["Body"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(_percent_table(gap["by_domain"]))

    # --- 5. ISO 27002 Controls ---
    story.append(Paragraph("5. Estado de controles ISO/IEC 27002:2022", styles["SectionHeading"]))
    totals = gap["totals"]
    story.append(
        Paragraph(
            f"Controles aplicables evaluados: {totals['applicable']} &mdash; Cumplidos: {totals['compliant']} "
            f"&mdash; Parciales: {totals['partial']} &mdash; No cumplidos: {totals['non_compliant']}",
            styles["Body"],
        )
    )

    story.append(PageBreak())

    # --- 6. LOPDP ---
    story.append(Paragraph("6. Protección de datos personales (LOPDP Ecuador)", styles["SectionHeading"]))
    if data["privacy_gap"]:
        pg = data["privacy_gap"]
        story.append(
            Paragraph(
                f"Cumplimiento de referencia LOPDP: <b>{pg['overall_percent']}%</b>. "
                "Este resultado es un diagnóstico de referencia y no constituye una certificación legal.",
                styles["Body"],
            )
        )
        story.append(Spacer(1, 8))
        story.append(_percent_table(pg["by_domain"]))
    else:
        story.append(Paragraph("No se registraron respuestas para el marco LOPDP.", styles["Body"]))

    story.append(PageBreak())

    # --- 7. Risk Assessment ---
    story.append(Paragraph("7. Evaluación de riesgos", styles["SectionHeading"]))
    counts = risk_summary["counts"]
    risk_rows = [["Nivel", "Cantidad"]]
    for level in ["critical", "high", "medium", "low"]:
        risk_rows.append([RISK_LEVEL_LABELS[level], str(counts[level])])
    risk_table = Table(risk_rows, colWidths=[10 * cm, 4 * cm])
    risk_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE0")),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(risk_table)

    # --- 8. Top Risks ---
    story.append(Paragraph("8. Principales riesgos identificados", styles["SectionHeading"]))
    top_rows = [["Código", "Riesgo", "Prob.", "Impacto", "Nivel", "Tratamiento"]]
    for r in risk_summary["top_risks"]:
        top_rows.append(
            [r.code, r.name, str(r.probability), str(r.impact), RISK_LEVEL_LABELS[r.inherent_level], r.treatment]
        )
    top_table = Table(top_rows, colWidths=[2 * cm, 6.5 * cm, 1.5 * cm, 1.7 * cm, 2 * cm, 2.7 * cm])
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE0")),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i, r in enumerate(risk_summary["top_risks"], start=1):
        style_cmds.append(("TEXTCOLOR", (4, i), (4, i), LEVEL_COLORS.get(r.inherent_level, colors.black)))
    top_table.setStyle(TableStyle(style_cmds))
    story.append(top_table)

    story.append(PageBreak())

    # --- 9. Plan de tratamiento ---
    story.append(Paragraph("9. Plan de tratamiento de riesgos", styles["SectionHeading"]))
    action_rows = [["Acción", "Responsable", "Prioridad", "Estado", "Fecha objetivo"]]
    for a in data["actions"]:
        action_rows.append(
            [
                a.title,
                a.responsible or "-",
                PRIORITY_LABELS.get(a.priority, a.priority),
                ACTION_STATUS_LABELS.get(a.status, a.status),
                a.target_date.strftime("%d/%m/%Y") if a.target_date else "-",
            ]
        )
    action_table = Table(action_rows, colWidths=[6 * cm, 3.5 * cm, 2.2 * cm, 2.5 * cm, 2.2 * cm])
    action_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D5DAE0")),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(action_table)

    # --- 10. Roadmap ---
    story.append(Paragraph("10. Roadmap 90 / 180 / 365 días", styles["SectionHeading"]))
    for horizon, label in [(90, "0-90 días (crítico / corto plazo)"), (180, "91-180 días (estructural)"), (365, "181-365 días (madurez)")]:
        items = data["roadmap"][horizon]
        story.append(Paragraph(label, styles["SubHeading"]))
        if items:
            for action in items:
                story.append(Paragraph(f"• {action.title} ({PRIORITY_LABELS.get(action.priority, action.priority)})", styles["Body"]))
        else:
            story.append(Paragraph("Sin acciones planificadas en este horizonte.", styles["Small"]))

    story.append(PageBreak())

    # --- 11. Conclusiones ---
    story.append(Paragraph("11. Conclusiones", styles["SectionHeading"]))
    story.append(
        Paragraph(
            "La organización presenta un nivel de madurez "
            f"\"{maturity['global_label']}\" con oportunidades de mejora concentradas en los dominios de menor "
            "puntuación. Se recomienda priorizar el tratamiento de los riesgos críticos y altos identificados, "
            "así como avanzar en el cierre de brechas de cumplimiento normativo dentro de los horizontes definidos "
            "en el roadmap.",
            styles["Body"],
        )
    )

    # --- 12. Anexo ---
    story.append(Paragraph("12. Anexo: detalle de respuestas", styles["SectionHeading"]))
    annex_rows = [["Código", "Pregunta", "Respuesta"]]
    for r in data["responses"]:
        annex_rows.append([r.question.code, r.question.title, ANSWER_LABELS.get(r.answer, r.answer)])
    annex_table = Table(annex_rows, colWidths=[2.5 * cm, 11 * cm, 3 * cm], repeatRows=1)
    annex_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DAE0")),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREY]),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(annex_table)

    def _footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(GREY)
        canvas.drawString(1.8 * cm, 1.2 * cm, "Cyber & Privacy Assessment Platform - Informe de diagnóstico")
        canvas.drawRightString(19.5 * cm, 1.2 * cm, f"Página {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    buffer.seek(0)
    return buffer


def generate_pdf_bytes(assessment):
    return generate_assessment_pdf(assessment).getvalue()
