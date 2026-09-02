from __future__ import annotations

"""Source-aware visual planning for ISCARB Visual Lecture Engine v2.

The visual layer never changes technical claims in the Blueprint. It only
chooses how source-supported ideas are shown. Local P1 PDFs are the preferred
visual source because they preserve complete slide/page composition. Public
SlideShare image discovery is opportunistic only; failure always falls back to
ISCARB redraws without breaking Presenter generation.
"""

import base64
import hashlib
import json
import mimetypes
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import fitz  # PyMuPDF
from bs4 import BeautifulSoup

from .models import Blueprint, LectureUnit
from .url_source import _download, _validate_public_url

APP_ROOT = Path(__file__).resolve().parent
DATA_ROOT = APP_ROOT.parent / "data"
UPLOAD_ROOT = DATA_ROOT / "uploads"
CACHE_ROOT = DATA_ROOT / "source_visual_cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
MAX_VISUAL_BYTES = 4 * 1024 * 1024
MAX_SLIDES = 80

# A source page has to stay readable once it fills the teaching canvas. At the
# previous 1.45x a 13.33in slide received roughly 91 DPI, which is what made
# figures look enlarged and soft; 2.6x lands near 163 DPI, the range where
# projected and printed diagram text stays crisp.
PDF_RENDER_ZOOM = 2.6

# Below this a rasterized or downloaded asset cannot be shown full-width without
# visible softening, so the unit is better served by a redrawn diagram.
MIN_PRESENTABLE_ASSET_WIDTH = 1100


@dataclass(frozen=True)
class VisualAsset:
    slide_number: int
    image_url: str = ""
    alt_text: str = ""
    source_url: str = ""
    local_path: str = ""
    source_kind: str = "public"
    visual_area_ratio: float = 0.0


@dataclass(frozen=True)
class VisualRegistry:
    source_url: str
    source_title: str
    assets: tuple[VisualAsset, ...]
    source_kind: str = "public"


@dataclass(frozen=True)
class VisualPlan:
    visual_type: str
    teaching_purpose: str
    reuse_mode: str
    citation: str
    source_visual_available: bool = False
    source_slide: int | None = None
    asset: VisualAsset | None = None
    focal_elements: tuple[str, ...] = ()


VISUAL_TYPES = {
    1: "incident-scene", 2: "domain-map", 3: "capability-evidence-path",
    4: "six-lens-model", 5: "predict-derive-reveal", 6: "mechanism-diagram",
    7: "architecture-diagram", 8: "tradeoff-decision-matrix",
    9: "claim-test-falsification", 10: "uncertainty-map",
    11: "context-system-map", 12: "accountability-map",
    13: "trend-implication-map", 14: "workload-recovery-map",
    15: "ai-permissibility-gate", 16: "mission-brief",
    17: "constraint-mutation", 18: "claim-evidence-warrant",
    19: "performance-ladder", 20: "assurance-case-tree",
}

TEACHING_PURPOSE = {
    1: "Expose the failure before naming the mechanism.",
    2: "Show the complete technical territory of the primary lecture.",
    3: "Make capability promises traceable to evidence.",
    4: "Inspect the same decision through six human-engineering lenses.",
    5: "Make first-principles derivation visible before terminology is revealed.",
    6: "Show how the mechanism transforms inputs, assumptions and failure modes.",
    7: "Make architectural boundaries and protection layers spatially visible.",
    8: "Compare alternatives through an explicit engineering trade-off.",
    9: "Connect a claim to a test that could falsify it.",
    10: "Separate knowns from decision-sensitive unknowns and monitoring needs.",
    11: "Make Saudi context change a technical decision rather than decorate it.",
    12: "Connect system events to evidence, responsibility and amanah.",
    13: "Separate enduring principles from changing practice and future implications.",
    14: "Connect architecture to operational workload and recovery burden.",
    15: "Show where AI may assist and where human engineering sign-off is mandatory.",
    16: "Frame the portfolio task as a professional engineering mission.",
    17: "Show how a design changes when a constraint mutates.",
    18: "Make the assurance argument inspectable as claim, evidence, warrant and uncertainty.",
    19: "Make readiness levels visible as observable performance, not vague grading.",
    20: "Close the original crisis with a bounded engineering verdict supported by evidence.",
}

SOURCE_VISUAL_PRIORITY = {2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

_STOP = {
    "the", "and", "for", "with", "from", "into", "that", "this", "what", "which",
    "how", "why", "unit", "engineering", "software", "system", "systems", "security",
    "design", "source", "student", "students", "lecture", "using", "used", "use",
}


def _cache_dir(key_text: str) -> Path:
    key = hashlib.sha256(key_text.encode("utf-8")).hexdigest()[:20]
    path = CACHE_ROOT / key
    path.mkdir(parents=True, exist_ok=True)
    return path


def primary_url_from_manifest(source_manifest: list[str]) -> str | None:
    for line in source_manifest or []:
        if "[P1]" not in line.upper():
            continue
        m = re.search(r"https?://[^\s]+", line)
        if m:
            return m.group(0).rstrip(".,;)")
    return None


def _primary_display_name(source_manifest: list[str]) -> str | None:
    for line in source_manifest or []:
        if "[P1]" not in line.upper():
            continue
        # SourceBundle label format: [P1] PRIMARY: filename.pdf
        if ":" in line:
            value = line.split(":", 1)[1].strip()
            if value and not value.startswith("http"):
                return Path(value).name
    return None


def _find_local_primary_pdf(source_root: Path | None) -> Path | None:
    if not source_root or not source_root.exists():
        return None
    if source_root.is_file():
        return source_root if source_root.suffix.lower() == ".pdf" else None
    patterns = ("P1__*.pdf", "P1/*.pdf", "**/P1__*.pdf", "**/linked_source.pdf")
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(source_root.glob(pattern))
    candidates = sorted({p for p in candidates if p.is_file()}, key=lambda p: p.stat().st_mtime_ns, reverse=True)
    return next((p for p in candidates if p.stat().st_size > 1000), None)


def _discover_local_primary_pdf(bp: Blueprint) -> Path | None:
    """Find the uploaded P1 PDF that belongs to this Blueprint.

    Exports only receive the Blueprint, not the job id. SourceBundle preserves
    the P1 display name in source_manifest, so an exact filename match gives us
    a deterministic bridge back to the upload directory. We never select an
    unrelated PDF when no exact P1 filename is available.
    """
    name = _primary_display_name(bp.source_manifest)
    if not name or not name.lower().endswith(".pdf") or not UPLOAD_ROOT.exists():
        return None
    expected = f"P1__{name}"
    candidates = [p for p in UPLOAD_ROOT.glob(f"*/{expected}") if p.is_file() and p.stat().st_size > 1000]
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime_ns)


def _build_pdf_registry(path: Path, source_title: str | None = None) -> VisualRegistry | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    cache = _cache_dir(f"pdf:{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}:z{PDF_RENDER_ZOOM}:v50")
    manifest_path = cache / "manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = tuple(VisualAsset(**x) for x in data.get("assets", []))
            if assets and all(Path(a.local_path).exists() for a in assets if a.local_path):
                return VisualRegistry(data.get("source_url", f"local:{path.name}"), data.get("source_title", source_title or path.stem), assets, "local-pdf")
        except Exception:
            pass
    try:
        doc = fitz.open(str(path))
    except Exception:
        return None
    assets: list[VisualAsset] = []
    try:
        for idx, page in enumerate(doc):
            if idx >= MAX_SLIDES:
                break
            slide_no = idx + 1
            image_path = cache / f"slide-{slide_no:03d}.png"
            if not image_path.exists() or image_path.stat().st_size < 1000:
                pix = page.get_pixmap(matrix=fitz.Matrix(PDF_RENDER_ZOOM, PDF_RENDER_ZOOM), alpha=False)
                pix.save(str(image_path))
            page_text = " ".join(page.get_text("text").split())[:1600]
            image_area = max((fitz.Rect(info["bbox"]).get_area() for info in page.get_image_info()), default=0)
            ratio = min(1.0, image_area / max(1.0, page.rect.get_area()))
            assets.append(VisualAsset(slide_no, "", page_text or f"Primary lecture page {slide_no}", f"local:{path.name}", str(image_path), "local-pdf", ratio))
            for figure_no, (clip, caption, labels) in enumerate(_captioned_figures(page), 1):
                figure_path = cache / f"figure-{slide_no:03d}-{figure_no}.png"
                if not figure_path.exists() or figure_path.stat().st_size < 1000:
                    # Vector art is crisp at any zoom; pick the zoom that makes the
                    # crop presentable full-width rather than the page's zoom.
                    zoom = min(MAX_FIGURE_ZOOM, max(PDF_RENDER_ZOOM, MIN_PRESENTABLE_ASSET_WIDTH * 1.1 / max(1.0, clip.width)))
                    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, alpha=False).save(str(figure_path))
                assets.append(VisualAsset(
                    slide_no, "", f"{caption}. {labels}"[:1600], f"local:{path.name}", str(figure_path),
                    FIGURE_KIND, min(1.0, clip.get_area() / max(1.0, page.rect.get_area())),
                ))
    finally:
        doc.close()
    if not assets:
        return None
    title = source_title or path.stem
    registry = VisualRegistry(f"local:{path.name}", title, tuple(assets), "local-pdf")
    manifest_path.write_text(json.dumps({
        "source_url": registry.source_url, "source_title": registry.source_title,
        "source_kind": registry.source_kind, "assets": [asdict(x) for x in assets],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


# A book chapter carries its diagrams as vector drawings under a "Figure N.N"
# caption, not as embedded images, so the page-level registry saw a text wall
# and the deck showed no figure at all. Each captioned figure is cropped into an
# asset of its own, anchored to the page it was printed on.
FIGURE_KIND = "local-pdf-figure"
MAX_FIGURE_ZOOM = 6.0
_FIGURE_CAPTION = re.compile(r"^(?:Figure|Fig\.|Table)\s+\d{1,2}[.\-]\d{1,2}\b")
# The figure sits above or beside its caption; drawings farther away than this
# belong to something else on the page.
FIGURE_REACH_ABOVE = 330.0
FIGURE_REACH_BELOW = 24.0
# How close a text block has to sit to the artwork to be part of the figure.
LABEL_REACH = 8.0


# A figure label is a few words in a narrow box. The body paragraph that follows
# the figure spans the text column and runs for lines; growing into it turned a
# clean diagram crop into a diagram with a page of prose stapled underneath.
MAX_LABEL_WORDS = 10
MAX_LABEL_WIDTH_SHARE = 0.45


def _is_figure_label(rect, text: str, caption_rect, page_rect) -> bool:
    if len(text.split()) > MAX_LABEL_WORDS or rect.width > page_rect.width * MAX_LABEL_WIDTH_SHARE:
        return False
    # The caption is the figure's bottom edge; body text sits below it.
    if rect.y0 > caption_rect.y1 + 4:
        return False
    near_edge = rect.y1 < page_rect.height * .14 or rect.y0 > page_rect.height * .9
    return not near_edge


def _captioned_figures(page) -> list[tuple["fitz.Rect", str, str]]:
    """(clip, caption, label text) for every captioned figure drawn on the page."""
    page_rect = page.rect
    blocks = [(fitz.Rect(b[:4]), " ".join(str(b[4]).split())) for b in page.get_text("blocks") if str(b[4]).strip()]
    captions = [
        (rect, text) for rect, text in blocks
        # An in-text mention ("Figure 14.5 shows the architecture of...") runs on
        # as a paragraph; the caption itself is a short block.
        if _FIGURE_CAPTION.match(text) and len(text.split()) <= 14 and rect.width < page_rect.width * .6
    ]
    if not captions:
        return []
    # Page frames and crop marks cover most of the page; a figure never does. A
    # figure drawn as a stack of thin lines (a layer diagram) has zero-height
    # paths, so a line counts by its length - but a rule that spans the text
    # column is page furniture, not part of any figure.
    drawings = []
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"])
        if r.height >= page_rect.height * .6 or r.width >= page_rect.width * .9:
            continue
        boxy = r.width > 2 and r.height > 2
        line = (r.width > 40 or r.height > 40) and min(r.width, r.height) <= 2 and r.width < page_rect.width * .6
        if boxy or line:
            # A zero-height line is an "empty" rect to PyMuPDF and never
            # intersects anything; give it a hairline of area so it takes part.
            drawings.append(fitz.Rect(r.x0, r.y0 - 0.5, r.x1, r.y1 + 0.5) if line else r)
    if not drawings:
        return []
    found = []
    for caption_rect, caption in captions:
        band = fitz.Rect(0, caption_rect.y0 - FIGURE_REACH_ABOVE, page_rect.width, caption_rect.y1 + FIGURE_REACH_BELOW)
        nearby = [r for r in drawings if band.intersects(r) and r.y1 > caption_rect.y0 - FIGURE_REACH_ABOVE]
        if len(nearby) < 2:
            continue
        clip = fitz.Rect(nearby[0])
        for r in nearby[1:]:
            clip |= r
        # A heading printed just above the first box ("Platform-Level Protection")
        # is part of the figure, and cropping to the drawings alone sliced it in
        # half. Text sitting against the artwork is pulled into the clip, then the
        # clip is re-measured so a label pulls in the label above it.
        labels: list[str] = []
        for _pass in range(3):
            reach = fitz.Rect(clip.x0 - LABEL_REACH, clip.y0 - LABEL_REACH, clip.x1 + LABEL_REACH, clip.y1 + LABEL_REACH)
            attached = [
                (rect, text) for rect, text in blocks
                if rect.intersects(reach) and (rect, text) != (caption_rect, caption)
                and _is_figure_label(rect, text, caption_rect, page_rect)
            ]
            grown = fitz.Rect(clip)
            for rect, _text in attached:
                grown |= rect
            labels = [text for _rect, text in attached]
            if grown == clip:
                break
            clip = grown
        clip |= caption_rect
        clip = fitz.Rect(clip.x0 - 6, clip.y0 - 6, clip.x1 + 6, clip.y1 + 6) & page_rect
        if clip.width < 80 or clip.height < 50:
            continue
        found.append((clip, caption, " ".join(labels)[:600]))
    return found


def _candidate_image_url(img) -> str:
    values = [img.get("data-full"), img.get("data-normal"), img.get("data-src"), img.get("data-lazy-src"), img.get("src"), img.get("srcset")]
    for raw in values:
        if not raw:
            continue
        value = str(raw).strip().split(",")[0].strip().split(" ")[0]
        if value.startswith("//"):
            value = "https:" + value
        if value.startswith("http") and "slidesharecdn" in value:
            return value
    return ""


def _build_slideshare_registry(url: str) -> VisualRegistry | None:
    """Best-effort only; SlideShare frequently blocks server-side visual discovery."""
    cache = _cache_dir(url)
    manifest_path = cache / "manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = tuple(VisualAsset(**x) for x in data.get("assets", []))
            if assets:
                return VisualRegistry(data.get("source_url", url), data.get("source_title", "SlideShare lecture"), assets, "public")
        except Exception:
            pass
    try:
        data, ctype, final_url = _download(url)
    except Exception:
        return None
    if "html" not in ctype and b"<html" not in data[:5000].lower():
        return None
    soup = BeautifulSoup(data, "html.parser")
    title_tag = soup.find("h1")
    title = " ".join(title_tag.get_text(" ", strip=True).split()) if title_tag else "SlideShare lecture"
    assets: list[VisualAsset] = []
    seen: set[str] = set()
    for img in soup.find_all("img"):
        image_url = _candidate_image_url(img)
        if not image_url or image_url in seen:
            continue
        alt = " ".join(str(img.get("alt") or "").split()).strip()
        if len(alt) < 12:
            continue
        seen.add(image_url)
        assets.append(VisualAsset(len(assets) + 1, image_url, alt, final_url, "", "public"))
        if len(assets) >= MAX_SLIDES:
            break
    if not assets:
        return None
    registry = VisualRegistry(final_url, title, tuple(assets), "public")
    manifest_path.write_text(json.dumps({
        "source_url": final_url, "source_title": title, "source_kind": "public", "assets": [asdict(x) for x in assets],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


def load_registry(bp: Blueprint, source_root: Path | None = None) -> VisualRegistry | None:
    # An explicitly scoped export must never borrow another user's identically
    # named file when its own upload has expired.
    local_pdf = _find_local_primary_pdf(source_root) if source_root is not None else _discover_local_primary_pdf(bp)
    if local_pdf:
        registry = _build_pdf_registry(local_pdf, local_pdf.name.removeprefix("P1__").rsplit(".", 1)[0])
        if registry:
            return registry
    url = primary_url_from_manifest(bp.source_manifest)
    if url and "slideshare.net" in (urlparse(url).hostname or "").lower():
        return _build_slideshare_registry(url)
    return None


def anchor_slides(anchor: str) -> list[int]:
    r"""Return every explicit page/slide coordinate in a provenance anchor.

    ``pp?\.?`` used to accept a bare ``P``.  In an anchor such as
    ``[P1] PAGE 7`` it therefore read the source label's ``1`` as page one and
    reused the cover slide throughout the deck.  The parser now requires an
    actual PAGE/SLIDE token (or the conventional p./pp. abbreviation), and it
    preserves multiple coordinates such as ``PAGE 4; PAGE 5``.
    """
    text = str(anchor or "").replace("–", "-").replace("—", "-")
    marker = re.compile(
        r"(?:slides?|pages?|p{1,2}\.)\s*(\d+)(?:\s*-\s*(\d+))?",
        flags=re.I,
    )
    found: list[int] = []
    for match in marker.finditer(text):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start:
            start, end = end, start
        if end - start > 30:
            continue
        for number in range(start, end + 1):
            if number not in found:
                found.append(number)
    return found


def _keywords(unit: LectureUnit) -> set[str]:
    raw = " ".join([unit.title, unit.engineering_question, *unit.core_content[:4]])
    words = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", raw.lower()))
    return {w for w in words if w not in _STOP}


def _asset_score(asset: VisualAsset, unit: LectureUnit, anchors: set[int]) -> float:
    alt = asset.alt_text.lower()
    overlap = sum(1 for w in _keywords(unit) if w in alt)
    score = overlap * 4.0
    if asset.slide_number in anchors:
        score += 18.0
    cues = ("figure", "diagram", "architecture", "layer", "model", "process", "structure", "component", "protection", "threat", "risk", "guideline", "survivability")
    score += sum(2.0 for cue in cues if cue in alt)
    n = len(asset.alt_text)
    if 35 <= n <= 650:
        score += 3.0
    elif n > 1800:
        score -= 5.0
    return score


def _looks_source_backed(anchor: str) -> bool:
    a = (anchor or "").upper()
    return bool(a.strip()) and ("P1" in a or "SLIDE" in a or "PAGE" in a)


def plan_for_unit(bp: Blueprint, unit: LectureUnit, registry: VisualRegistry | None = None) -> VisualPlan:
    visual_type = VISUAL_TYPES.get(unit.number, "concept-visual")
    purpose = TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip()
    source_backed = _looks_source_backed(anchor)
    if registry and unit.number in SOURCE_VISUAL_PRIORITY and source_backed:
        anchors = set(anchor_slides(anchor))
        ranked = sorted(registry.assets, key=lambda a: _asset_score(a, unit, anchors), reverse=True)
        if ranked:
            best = ranked[0]; score = _asset_score(best, unit, anchors)
            if best.slide_number in anchors or score >= 8.0:
                return VisualPlan(visual_type, purpose, "USE", f"Source visual: [P1] Slide/Page {best.slide_number} · {registry.source_title}", True, best.slide_number, best, (unit.takeaway, unit.student_action))
    if source_backed:
        return VisualPlan(visual_type, purpose, "REDRAW", anchor or "[P1] source-anchored redraw", False, None, None, (unit.takeaway, unit.student_action))
    return VisualPlan(visual_type, purpose, "NEW", "ISCARB pedagogy — original teaching visualization", False, None, None, (unit.takeaway, unit.student_action))


def plans_for_blueprint(bp: Blueprint, source_root: Path | None = None) -> list[VisualPlan]:
    registry = load_registry(bp, source_root=source_root)
    return [plan_for_unit(bp, unit, registry) for unit in bp.units]


def local_asset(asset: VisualAsset) -> Path | None:
    if asset.local_path:
        path = Path(asset.local_path)
        if path.exists() and path.stat().st_size > 1000:
            return path
    if not asset.image_url:
        return None
    cache = _cache_dir(asset.source_url or asset.image_url)
    ext = Path(urlparse(asset.image_url).path).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        ext = ".jpg"
    path = cache / f"slide-{asset.slide_number:03d}{ext}"
    if path.exists() and path.stat().st_size > 1000:
        return path
    try:
        safe = _validate_public_url(asset.image_url)
        req = Request(safe, headers={"User-Agent": "ISCARB-Visual-Lecture-Engine/2.0", "Accept": "image/*"})
        with urlopen(req, timeout=15) as resp:
            final = _validate_public_url(resp.geturl())
            host = (urlparse(final).hostname or "").lower()
            if "slidesharecdn" not in host:
                return None
            data = resp.read(MAX_VISUAL_BYTES + 1)
            if len(data) > MAX_VISUAL_BYTES or len(data) < 1000:
                return None
            ctype = (resp.headers.get_content_type() or "").lower()
            if not ctype.startswith("image/"):
                return None
            guessed = mimetypes.guess_extension(ctype) or ext
            if guessed in {".jpe", ".jpeg"}:
                guessed = ".jpg"
            path = cache / f"slide-{asset.slide_number:03d}{guessed}"
            path.write_bytes(data)
            return path
    except Exception:
        return None


def asset_data_uri(asset: VisualAsset) -> str | None:
    path = local_asset(asset)
    if not path:
        return None
    ext = path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
