from __future__ import annotations

"""ISCARB v6.9.4 — latency-safe source-native presenter.

Two old compatibility paths made a current Chapter 13 preview exceed two minutes
on the free Render CPU:
1. v4.6.11 rebuilt/re-audited a saved Blueprint every time preview/export was
   opened, re-extracting the full PDF text with pypdf.
2. the visual registry rasterized every PDF page at high resolution before it
   knew which source pages could actually be used.

v6.9.4 makes preview/export a read-only operation over the already compiled
Blueprint and builds a content-addressed registry only for P1 pages explicitly
anchored to visual-priority units. Text-heavy pages are never turned into
"document screenshot" illustrations: only pages with real image/vector density
enter the source-visual pool. Missing visuals fall through to native/text-first.
"""

import hashlib
import json
from dataclasses import asdict
from pathlib import Path

import fitz
from fastapi import HTTPException

from . import main as engine
from . import start_v440 as base
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import presenter_v44
from . import presenter_v67_prod as presenter
from . import patch_v671 as reliability

PUBLIC_VERSION = "6.9.4"
PIPELINE_ID = "faculty-studio-v6.9.4-latency-safe-source-native"
_PATCHED = False
MAX_ANCHORED_VISUAL_PAGES = 18
FAST_PAGE_ZOOM = 2.15
FAST_PICTURE_ZOOM = 3.6
MIN_VISUAL_IMAGE_SHARE = 0.18
MIN_VECTOR_DRAWINGS = 8
MAX_VISUAL_TEXT_WORDS = 170


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[:24]


def _wanted_pages(bp) -> list[int]:
    """Only P1 coordinates that can legitimately supply a source figure."""
    pages: list[int] = []
    # Visual-priority units first. Unit 1 may use source incident evidence when
    # the source actually anchors it, so include it after the priority set.
    ordered = [u for u in list(getattr(bp, "units", []) or []) if int(getattr(u, "number", 0) or 0) in sv.SOURCE_VISUAL_PRIORITY]
    ordered += [u for u in list(getattr(bp, "units", []) or []) if int(getattr(u, "number", 0) or 0) == 1]
    for unit in ordered:
        for n in sv.anchor_slides(str(getattr(unit, "source_anchor", "") or "")):
            if 1 <= n <= sv.MAX_SLIDES and n not in pages:
                pages.append(n)
                if len(pages) >= MAX_ANCHORED_VISUAL_PAGES:
                    return pages
    return pages


def _manifest_registry(manifest: Path, fallback_title: str):
    if not manifest.exists():
        return None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        assets = tuple(
            sv.VisualAsset(**{
                **row,
                "text_boxes": tuple(tuple(float(v) for v in b) for b in row.get("text_boxes", ())),
            })
            for row in data.get("assets", [])
        )
        if assets and all(Path(a.local_path).exists() for a in assets if a.local_path):
            return sv.VisualRegistry(
                data.get("source_url", "local:primary.pdf"),
                data.get("source_title", fallback_title),
                assets,
                "local-pdf",
            )
    except Exception:
        return None
    return None


def _fast_pdf_registry(path: Path, bp, source_title: str | None = None):
    wanted = _wanted_pages(bp)
    if not wanted:
        return None
    try:
        signature = _digest(path)
    except OSError:
        return None
    page_key = "-".join(str(n) for n in wanted)
    cache = sv._cache_dir(f"pdf-fast-v694:{signature}:p{page_key}:z{FAST_PAGE_ZOOM}")
    manifest = cache / "manifest.json"
    cached = _manifest_registry(manifest, source_title or path.stem)
    if cached:
        return cached

    try:
        doc = fitz.open(str(path))
    except Exception:
        return None

    assets: list[sv.VisualAsset] = []
    try:
        for slide_no in wanted:
            if slide_no < 1 or slide_no > len(doc):
                continue
            page = doc[slide_no - 1]
            page_text = " ".join(page.get_text("text").split())[:1600]
            word_count = len(page_text.split())
            infos = page.get_image_info()
            image_area = max((fitz.Rect(info["bbox"]).get_area() for info in infos), default=0)
            ratio = min(1.0, image_area / max(1.0, page.rect.get_area()))
            try:
                drawing_count = len(page.get_drawings())
            except Exception:
                drawing_count = 0

            # A source page must contain actual visual structure. This rejects
            # text documents such as generic classified-information pages.
            visual_page = ratio >= MIN_VISUAL_IMAGE_SHARE or (
                drawing_count >= MIN_VECTOR_DRAWINGS and word_count <= MAX_VISUAL_TEXT_WORDS
            )
            if not visual_page:
                continue

            # If one or more embedded pictures dominate the page, crop their
            # union so the picture, not the slide furniture, fills the canvas.
            if ratio >= sv.MIN_PICTURE_AREA_SHARE and infos:
                box = fitz.Rect()
                for info in infos:
                    box |= fitz.Rect(info["bbox"])
                if box.width > 8 and box.height > 8:
                    box = sv._whole_words(page, box)
                    picture_path = cache / f"picture-{slide_no:03d}.png"
                    if not picture_path.exists() or picture_path.stat().st_size < 1000:
                        zoom = min(FAST_PICTURE_ZOOM, max(FAST_PAGE_ZOOM, FAST_PAGE_ZOOM * page.rect.width / max(1.0, box.width)))
                        page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=box, alpha=False).save(str(picture_path))
                    assets.append(sv.VisualAsset(
                        slide_no, "", page_text or f"Primary lecture page {slide_no}",
                        f"local:{path.name}", str(picture_path), sv.PICTURE_KIND, ratio,
                        sv._text_boxes_in(page, box),
                    ))

            # Keep one crisp whole-page option for vector diagrams / visual
            # slides. We deliberately do not rasterize ordinary text pages.
            page_path = cache / f"slide-{slide_no:03d}.png"
            if not page_path.exists() or page_path.stat().st_size < 1000:
                page.get_pixmap(matrix=fitz.Matrix(FAST_PAGE_ZOOM, FAST_PAGE_ZOOM), alpha=False).save(str(page_path))
            assets.append(sv.VisualAsset(
                slide_no, "", page_text or f"Primary lecture page {slide_no}",
                f"local:{path.name}", str(page_path), "local-pdf", ratio,
            ))
    finally:
        doc.close()

    if not assets:
        return None
    title = source_title or path.stem
    registry = sv.VisualRegistry(f"local:{path.name}", title, tuple(assets), "local-pdf")
    try:
        manifest.write_text(json.dumps({
            "source_url": registry.source_url,
            "source_title": registry.source_title,
            "source_kind": registry.source_kind,
            "assets": [asdict(x) for x in assets],
        }, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass
    return registry


def _fast_load_registry(bp, source_root: Path | None = None):
    # Production v6.9 is explicitly local/P1-only. Never fall through to the
    # legacy SlideShare/public-web discovery path.
    local_pdf = sv._find_local_primary_pdf(source_root) if source_root is not None else sv._discover_local_primary_pdf(bp)
    if not local_pdf:
        return None
    return _fast_pdf_registry(local_pdf, bp, local_pdf.name.removeprefix("P1__").rsplit(".", 1)[0])


def _fast_presenter_job(job_id: str):
    """Preview/export must never rebuild a current saved Blueprint."""
    try:
        job = engine.load_job(job_id)
    except FileNotFoundError:
        raise HTTPException(404, base.JOB_MISSING_MESSAGE)
    if job.blueprint is None:
        raise HTTPException(409, "No blueprint is available yet")
    return job


def _cache_paths(job_id: str) -> dict[str, Path]:
    root = engine.EXPORTS
    tag = "v694"
    return {
        "pptx": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pptx",
        "presenter-pdf": root / f"ISCARB_{job_id}_{tag}_Visual_Presenter.pdf",
        "pdf": root / f"ISCARB_{job_id}_{tag}_Faculty_Reading_Pack.pdf",
        "docx": root / f"ISCARB_{job_id}_{tag}_Instructor_Guide.docx",
        "student": root / f"ISCARB_{job_id}_{tag}_Student_Activity_Pack.docx",
        "json": root / f"ISCARB_{job_id}_{tag}_Blueprint.json",
    }


def apply_v694_patch(app) -> None:
    global _PATCHED
    if _PATCHED:
        return
    _PATCHED = True

    # Remove historical request-time self-healing. Compile owns generation and
    # gating; preview/export is read-only over the saved current Blueprint.
    base._presenter_job = _fast_presenter_job

    # Content-addressed, anchor-bounded source visual registry.
    sv.load_registry = _fast_load_registry
    for module in (sv42, presenter_v44, presenter):
        if hasattr(module, "load_registry"):
            setattr(module, "load_registry", _fast_load_registry)

    reliability._cache_paths = _cache_paths
    base.PUBLIC_VERSION = PUBLIC_VERSION
    base.PIPELINE_ID = PIPELINE_ID
    try:
        from . import start_v670_prod as prod
        prod.PUBLIC_VERSION = PUBLIC_VERSION
        prod.PIPELINE_ID = PIPELINE_ID
    except Exception:
        pass

    previous_health = base._health_v440
    def health():
        data = dict(previous_health())
        data.update({
            "version": PUBLIC_VERSION,
            "pipeline": PIPELINE_ID,
            "presenter_request_rebuild": False,
            "source_visual_registry": "content-addressed; anchored visual-priority P1 pages only",
            "text_document_as_visual": False,
            "source_visual_page_cap": MAX_ANCHORED_VISUAL_PAGES,
            "public_web_image_fallback": False,
            "presenter_latency_fix": True,
        })
        return data
    base._health_v440 = health
    base.engine.health = health
