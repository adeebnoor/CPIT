from __future__ import annotations

from pathlib import Path

from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

from .models import Blueprint


def export_docx(bp: Blueprint, out: Path) -> Path:
    doc = Document()
    doc.add_heading(bp.lecture_title, 0)
    doc.add_paragraph(bp.engineering_thesis)
    doc.add_heading("Central Engineering Crisis", level=1)
    doc.add_paragraph(bp.central_engineering_crisis)
    doc.add_heading("Weekly CLOs", level=1)
    for c in bp.clOs:
        doc.add_paragraph(f"{c.id}: {c.statement}", style="List Bullet")
        doc.add_paragraph(f"Evidence: {c.evidence_expected}")
    for u in bp.units:
        doc.add_page_break()
        doc.add_heading(f"UNIT {u.number:02d} — {u.phase} — {u.title}", level=1)
        doc.add_paragraph(f"Engineering question: {u.engineering_question}")
        for bullet in u.core_content:
            doc.add_paragraph(bullet, style="List Bullet")
        doc.add_paragraph(f"Visual suggestion: {u.visual_suggestion}")
        doc.add_paragraph(f"Student action: {u.student_action}")
        doc.add_paragraph(f"Takeaway: {u.takeaway}")
        doc.add_paragraph(f"CIMT: {', '.join(u.cimtlens)} | CLO: {', '.join(u.clo_ids)}")
        doc.add_paragraph(f"Source anchor: {u.source_anchor}")
        doc.add_paragraph(f"Evidence: {u.evidence}")
    doc.save(out)
    return out


def export_pptx(bp: Blueprint, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for u in bp.units:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = f"{u.number:02d} · {u.phase} · {u.title}"
        title.text_frame.paragraphs[0].font.size = Pt(24)

        tx = slide.shapes.add_textbox(Inches(0.7), Inches(1.25), Inches(7.7), Inches(5.4))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = u.engineering_question
        p.font.bold = True
        p.font.size = Pt(18)
        for bullet in u.core_content[:5]:
            p = tf.add_paragraph()
            p.text = bullet
            p.level = 0
            p.font.size = Pt(16)
        p = tf.add_paragraph()
        p.text = "STUDENT ACTION — " + u.student_action
        p.font.bold = True
        p.font.size = Pt(16)

        side = slide.shapes.add_textbox(Inches(8.7), Inches(1.35), Inches(3.9), Inches(4.8))
        sf = side.text_frame
        sf.word_wrap = True
        for label, value in [
            ("Visual", u.visual_suggestion),
            ("Takeaway", u.takeaway),
            ("Evidence", u.evidence),
            ("Source", u.source_anchor),
        ]:
            p = sf.paragraphs[0] if len(sf.paragraphs) == 1 and not sf.paragraphs[0].text else sf.add_paragraph()
            p.text = f"{label}: {value}"
            p.font.size = Pt(13)

        footer = slide.shapes.add_textbox(Inches(0.7), Inches(6.85), Inches(11.9), Inches(0.35))
        fp = footer.text_frame.paragraphs[0]
        fp.text = f"CIMT: {', '.join(u.cimtlens)}  |  CLO: {', '.join(u.clo_ids)}  |  IDR: {', '.join(u.inherited_requirements)}"
        fp.font.size = Pt(9)

    prs.save(out)
    return out


def export_pdf(bp: Blueprint, out: Path) -> Path:
    styles = getSampleStyleSheet()
    story = [Paragraph(bp.lecture_title, styles["Title"]), Paragraph(bp.engineering_thesis, styles["BodyText"]), Spacer(1, 12)]
    for u in bp.units:
        story.append(Paragraph(f"UNIT {u.number:02d} — {u.phase} — {u.title}", styles["Heading1"]))
        story.append(Paragraph(f"<b>Engineering question:</b> {u.engineering_question}", styles["BodyText"]))
        for bullet in u.core_content:
            story.append(Paragraph("• " + bullet, styles["BodyText"]))
        story.append(Paragraph(f"<b>Student action:</b> {u.student_action}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Takeaway:</b> {u.takeaway}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Source:</b> {u.source_anchor}", styles["BodyText"]))
        story.append(PageBreak())
    SimpleDocTemplate(str(out), pagesize=A4).build(story)
    return out
