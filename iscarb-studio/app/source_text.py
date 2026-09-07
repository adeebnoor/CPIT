from __future__ import annotations

from pathlib import Path


def extract_source_text(path: Path, limit: int = 600_000) -> str:
    """Best-effort local text extraction for deterministic gates.

    This is NOT used to replace Gemini's reading of the source. It gives hard gates
    a local corpus for conservative checks such as ETEC SLO atomicity and obvious
    unsupported-term detection.
    """
    suffix = path.suffix.lower()
    try:
        if suffix in {".txt", ".md"}:
            return path.read_text(encoding="utf-8", errors="replace")[:limit]
        if suffix == ".pdf":
            # Preserve page order and recover tables conservatively. pypdf is
            # fast for ordinary text; pdfplumber supplies a second pass when a
            # page is sparse or contains tabular structure. This remains local
            # source extraction only — it never creates unsupported content.
            from pypdf import PdfReader
            import pdfplumber

            reader = PdfReader(str(path))
            chunks: list[str] = []
            with pdfplumber.open(str(path)) as pdf:
                page_count = max(len(reader.pages), len(pdf.pages))
                for index in range(page_count):
                    primary = ""
                    if index < len(reader.pages):
                        primary = reader.pages[index].extract_text() or ""
                    plumber_page = pdf.pages[index] if index < len(pdf.pages) else None
                    fallback = ""
                    tables: list[str] = []
                    if plumber_page is not None:
                        # Use plumber text when pypdf produced little usable text.
                        if len(primary.strip()) < 120:
                            fallback = plumber_page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                        try:
                            for table in plumber_page.extract_tables() or []:
                                rows = []
                                for row in table or []:
                                    cells = [" ".join(str(cell or "").split()) for cell in row or []]
                                    if any(cells):
                                        rows.append(" | ".join(cells))
                                if rows:
                                    tables.append("[TABLE]\n" + "\n".join(rows))
                        except Exception:
                            # A malformed table must never discard the page text.
                            pass
                    page_text = primary if len(primary.strip()) >= len(fallback.strip()) else fallback
                    chunks.append(f"--- Page {index + 1} ---\n{page_text.strip()}")
                    chunks.extend(tables)
                    if sum(len(x) for x in chunks) >= limit:
                        break
            return "\n".join(chunks)[:limit]
        if suffix == ".pptx":
            from pptx import Presentation
            prs = Presentation(str(path))
            chunks: list[str] = []
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        chunks.append(shape.text)
            return "\n".join(chunks)[:limit]
        if suffix == ".docx":
            from docx import Document
            doc = Document(str(path))
            chunks = [p.text for p in doc.paragraphs if p.text]
            for table in doc.tables:
                for row in table.rows:
                    chunks.append(" | ".join(cell.text for cell in row.cells))
            return "\n".join(chunks)[:limit]
    except Exception:
        return ""
    return ""
