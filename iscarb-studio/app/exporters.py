from __future__ import annotations

from pathlib import Path

from docx import Document
from pptx import Presentation
from pptx.util import Inches, Pt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

from .models import Blueprint


def _readiness_for_unit(bp: Blueprint, unit_no: int) -> list[str]:
    refs: list[str] = []
    for r in bp.readiness_alignment:
        if unit_no in r.evidence_units or unit_no in {3, 16, 19, 20}:
            label = f"{r.sku}: {', '.join(r.slo_refs)} → {', '.join(r.klo_refs)}"
            if label not in refs:
                refs.append(label)
    return refs


def export_docx(bp: Blueprint, out: Path) -> Path:
    doc = Document()
    doc.add_heading(bp.lecture_title, 0)
    doc.add_paragraph(bp.engineering_thesis)
    doc.add_paragraph(f"Live session: {bp.session_minutes} minutes | 20 Units")
    doc.add_paragraph(f"Named ethical purpose: {bp.named_ethical_purpose}")

    doc.add_heading("Lecture Source Bundle", level=1)
    for s in bp.source_manifest:
        doc.add_paragraph(s, style="List Bullet")
    if bp.deferred_topics:
        doc.add_heading("Explicitly Deferred Beyond This 90-Minute Session", level=2)
        for t in bp.deferred_topics:
            doc.add_paragraph(t, style="List Bullet")

    doc.add_heading("Central Engineering Crisis", level=1)
    doc.add_paragraph(bp.central_engineering_crisis)

    doc.add_heading("Weekly CLOs", level=1)
    for c in bp.clOs:
        doc.add_paragraph(f"{c.id}: {c.statement}", style="List Bullet")
        doc.add_paragraph(f"Evidence: {c.evidence_expected}")

    doc.add_heading("ETEC IT Readiness Alignment", level=1)
    for r in bp.readiness_alignment:
        doc.add_paragraph(
            f"{r.gku} | {r.sku} | {', '.join(r.slo_refs)} | {', '.join(r.klo_refs)} | {r.strength}",
            style="List Bullet",
        )
        doc.add_paragraph(f"Rationale: {r.rationale}")
        doc.add_paragraph(f"Atomicity evidence: {r.atomicity_evidence}")
        doc.add_paragraph(f"Evidence units: {', '.join(str(x) for x in r.evidence_units)} | ETEC pages: {', '.join(str(x) for x in r.standard_source_pages)}")

    for u in bp.units:
        doc.add_page_break()
        doc.add_heading(f"UNIT {u.number:02d} — {u.phase} — {u.title} — {u.planned_minutes} min", level=1)
        doc.add_paragraph(f"Engineering question: {u.engineering_question}")
        if u.core_content:
            doc.add_heading("Lecture-bundle technical content", level=2)
            for bullet in u.core_content:
                doc.add_paragraph(bullet, style="List Bullet")
        if u.pedagogy_content:
            doc.add_heading("ISCARB Pedagogy / Decision Work", level=2)
            for bullet in u.pedagogy_content:
                doc.add_paragraph(bullet, style="List Bullet")
        if u.enrichment_content:
            doc.add_heading("ISCARB Contextual Enrichment", level=2)
            for bullet in u.enrichment_content:
                doc.add_paragraph(bullet, style="List Bullet")
            for basis in u.enrichment_basis:
                doc.add_paragraph(f"Basis: {basis}")
        if u.scenario_assumptions:
            doc.add_heading("Scenario assumptions", level=2)
            for assumption in u.scenario_assumptions:
                doc.add_paragraph(assumption, style="List Bullet")
        refs = _readiness_for_unit(bp, u.number)
        if refs:
            doc.add_heading("Readiness trace", level=2)
            for ref in refs:
                doc.add_paragraph(ref, style="List Bullet")
        doc.add_paragraph(f"Visual suggestion: {u.visual_suggestion}")
        doc.add_paragraph(f"Student action: {u.student_action}")
        doc.add_paragraph(f"Takeaway: {u.takeaway}")
        doc.add_paragraph(f"CIMT: {', '.join(u.cimtlens)} | CLO: {', '.join(u.clo_ids)}")
        doc.add_paragraph(f"Source anchor: {u.source_anchor or 'N/A — ISCARB pedagogy'}")
        doc.add_paragraph(f"Evidence: {u.evidence}")

    doc.add_page_break()
    doc.add_heading("Four-Level Engineering Rubric", level=1)
    for r in bp.rubric_criteria:
        doc.add_heading(r.criterion, level=2)
        doc.add_paragraph(f"4 — Distinguished: {r.distinguished}")
        doc.add_paragraph(f"3 — Ready: {r.ready}")
        doc.add_paragraph(f"2 — Developing: {r.developing}")
        doc.add_paragraph(f"1 — Not Yet Ready: {r.not_yet_ready}")
        if r.readiness_refs:
            doc.add_paragraph(f"Readiness: {', '.join(r.readiness_refs)}")
    doc.save(out)
    return out


def export_pptx(bp: Blueprint, out: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    for u in bp.units:
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        title = slide.shapes.title
        title.text = f"{u.number:02d} · {u.phase} · {u.title} · {u.planned_minutes} min"
        title.text_frame.paragraphs[0].font.size = Pt(24)

        tx = slide.shapes.add_textbox(Inches(0.7), Inches(1.15), Inches(7.5), Inches(5.55))
        tf = tx.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = u.engineering_question
        p.font.bold = True
        p.font.size = Pt(17)
        for bullet in u.core_content[:4]:
            p = tf.add_paragraph(); p.text = bullet; p.level = 0; p.font.size = Pt(14)
        if u.pedagogy_content:
            p = tf.add_paragraph(); p.text = "ISCARB PEDAGOGY / DECISION WORK"; p.font.bold = True; p.font.size = Pt(10)
            for bullet in u.pedagogy_content[:3]:
                p = tf.add_paragraph(); p.text = bullet; p.font.size = Pt(12)
        if u.enrichment_content:
            p = tf.add_paragraph(); p.text = "ISCARB CONTEXTUAL ENRICHMENT"; p.font.bold = True; p.font.size = Pt(10)
            for bullet in u.enrichment_content[:2]:
                p = tf.add_paragraph(); p.text = bullet; p.font.size = Pt(11)
        p = tf.add_paragraph(); p.text = "STUDENT ACTION — " + u.student_action; p.font.bold = True; p.font.size = Pt(13)

        side = slide.shapes.add_textbox(Inches(8.45), Inches(1.25), Inches(4.15), Inches(5.1))
        sf = side.text_frame
        sf.word_wrap = True
        side_items = [
            ("Visual", u.visual_suggestion),
            ("Takeaway", u.takeaway),
            ("Evidence", u.evidence),
            ("Source", u.source_anchor or "N/A — ISCARB pedagogy"),
        ]
        refs = _readiness_for_unit(bp, u.number)
        if refs:
            side_items.append(("ETEC readiness", " | ".join(refs[:2])))
        if u.enrichment_basis:
            side_items.append(("Enrichment basis", " | ".join(u.enrichment_basis[:2])))
        for label, value in side_items:
            p = sf.paragraphs[0] if len(sf.paragraphs) == 1 and not sf.paragraphs[0].text else sf.add_paragraph()
            p.text = f"{label}: {value}"; p.font.size = Pt(10.5)

        footer = slide.shapes.add_textbox(Inches(0.7), Inches(6.85), Inches(11.9), Inches(0.35))
        fp = footer.text_frame.paragraphs[0]
        fp.text = f"{u.planned_minutes} min  |  CIMT: {', '.join(u.cimtlens)}  |  CLO: {', '.join(u.clo_ids)}  |  IDR: {', '.join(u.inherited_requirements)}"
        fp.font.size = Pt(9)

    prs.save(out)
    return out


def export_pdf(bp: Blueprint, out: Path) -> Path:
    styles = getSampleStyleSheet()
    story = [
        Paragraph(bp.lecture_title, styles["Title"]),
        Paragraph(bp.engineering_thesis, styles["BodyText"]),
        Paragraph(f"<b>Live session:</b> {bp.session_minutes} minutes | 20 Units", styles["BodyText"]),
        Paragraph(f"<b>Named ethical purpose:</b> {bp.named_ethical_purpose}", styles["BodyText"]),
        Spacer(1, 8),
        Paragraph("<b>LECTURE SOURCE BUNDLE</b>", styles["BodyText"]),
    ]
    for source in bp.source_manifest:
        story.append(Paragraph("• " + source, styles["BodyText"]))
    if bp.deferred_topics:
        story.append(Paragraph("<b>DEFERRED BEYOND THIS 90-MINUTE SESSION</b>", styles["BodyText"]))
        for topic in bp.deferred_topics:
            story.append(Paragraph("• " + topic, styles["BodyText"]))
    story.append(PageBreak())

    for u in bp.units:
        story.append(Paragraph(f"UNIT {u.number:02d} — {u.phase} — {u.title} — {u.planned_minutes} min", styles["Heading1"]))
        story.append(Paragraph(f"<b>Engineering question:</b> {u.engineering_question}", styles["BodyText"]))
        if u.core_content:
            story.append(Paragraph("<b>LECTURE-BUNDLE TECHNICAL CONTENT</b>", styles["BodyText"]))
            for bullet in u.core_content:
                story.append(Paragraph("• " + bullet, styles["BodyText"]))
        if u.pedagogy_content:
            story.append(Paragraph("<b>ISCARB PEDAGOGY / DECISION WORK</b>", styles["BodyText"]))
            for bullet in u.pedagogy_content:
                story.append(Paragraph("• " + bullet, styles["BodyText"]))
        if u.enrichment_content:
            story.append(Paragraph("<b>ISCARB CONTEXTUAL ENRICHMENT</b>", styles["BodyText"]))
            for bullet in u.enrichment_content:
                story.append(Paragraph("• " + bullet, styles["BodyText"]))
            story.append(Paragraph(f"<b>Basis:</b> {' | '.join(u.enrichment_basis)}", styles["BodyText"]))
        if u.scenario_assumptions:
            story.append(Paragraph(f"<b>Scenario assumptions:</b> {' | '.join(u.scenario_assumptions)}", styles["BodyText"]))
        refs = _readiness_for_unit(bp, u.number)
        if refs:
            story.append(Paragraph(f"<b>ETEC readiness:</b> {' | '.join(refs)}", styles["BodyText"]))
        if u.number == 19:
            story.append(Paragraph("<b>FOUR-LEVEL RUBRIC MATRIX</b>", styles["BodyText"]))
            for r in bp.rubric_criteria:
                story.append(Paragraph(f"<b>{r.criterion}</b> — 4: {r.distinguished} | 3: {r.ready} | 2: {r.developing} | 1: {r.not_yet_ready}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Student action:</b> {u.student_action}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Takeaway:</b> {u.takeaway}", styles["BodyText"]))
        story.append(Paragraph(f"<b>Source:</b> {u.source_anchor or 'N/A — ISCARB pedagogy'}", styles["BodyText"]))
        story.append(PageBreak())
    SimpleDocTemplate(str(out), pagesize=A4).build(story)
    return out
