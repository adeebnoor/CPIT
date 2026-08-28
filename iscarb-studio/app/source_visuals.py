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
CACHE_ROOT = APP_ROOT.parent / "data" / "source_visual_cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
MAX_VISUAL_BYTES = 4 * 1024 * 1024
MAX_SLIDES = 80
PDF_RENDER_ZOOM = 1.45


@dataclass(frozen=True)
class VisualAsset:
    slide_number: int
    image_url: str = ""
    alt_text: str = ""
    source_url: str = ""
    local_path: str = ""
    source_kind: str = "public"  # public | local-pdf


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
    reuse_mode: str  # USE | REDRAW | NEW
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

# Source figures are most valuable when the source itself owns a mechanism,
# architecture, comparison, process or accountability structure.
SOURCE_VISUAL_PRIORITY = {6, 7, 8, 9, 12, 13}

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


def _find_local_primary_pdf(source_root: Path | None) -> Path | None:
    if not source_root or not source_root.exists():
        return None
    candidates: list[Path] = []
    candidates.extend(source_root.glob("P1__*.pdf"))
    candidates.extend(source_root.glob("P1/*.pdf"))
    candidates.extend(source_root.glob("**/P1__*.pdf"))
    candidates.extend(source_root.glob("**/linked_source.pdf"))
    seen: set[Path] = set()
    for path in candidates:
        try:
            p = path.resolve()
        except Exception:
            p = path
        if p in seen:
            continue
        seen.add(p)
        if path.is_file() and path.stat().st_size > 1000:
            return path
    return None


def _build_pdf_registry(path: Path, source_title: str | None = None) -> VisualRegistry | None:
    try:
        stat = path.stat()
    except OSError:
        return None
    cache = _cache_dir(f"pdf:{path.resolve()}:{stat.st_mtime_ns}:{stat.st_size}")
    manifest_path = cache / "manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = tuple(VisualAsset(**x) for x in data.get("assets", []))
            if assets and all(Path(a.local_path).exists() for a in assets if a.local_path):
                return VisualRegistry(
                    data.get("source_url", f"local:{path.name}"),
                    data.get("source_title", source_title or path.stem),
                    assets,
                    "local-pdf",
                )
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
            assets.append(VisualAsset(
                slide_number=slide_no,
                alt_text=page_text or f"Primary lecture page {slide_no}",
                source_url=f"local:{path.name}",
                local_path=str(image_path),
                source_kind="local-pdf",
            ))
    finally:
        doc.close()
    if not assets:
        return None
    title = source_title or path.stem
    registry = VisualRegistry(f"local:{path.name}", title, tuple(assets), "local-pdf")
    manifest_path.write_text(json.dumps({
        "source_url": registry.source_url,
        "source_title": registry.source_title,
        "source_kind": registry.source_kind,
        "assets": [asdict(x) for x in assets],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


def _candidate_image_url(img) -> str:
    values = [img.get("data-full"), img.get("data-normal"), img.get("data-src"),
              img.get("data-lazy-src"), img.get("src"), img.get("srcset")]
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
    """Best-effort only. SlideShare may block server-side visual discovery."""
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
        "source_url": final_url, "source_title": title, "source_kind": "public",
        "assets": [asdict(x) for x in assets],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


def load_registry(bp: Blueprint, source_root: Path | None = None) -> VisualRegistry | None:
    # Local P1 PDF is authoritative for visual reuse because it preserves the
    # complete page/slide composition and is not dependent on third-party HTML.
    local_pdf = _find_local_primary_pdf(source_root)
    if local_pdf:
        registry = _build_pdf_registry(local_pdf, local_pdf.stem.replace("P1__", ""))
        if registry:
            return registry
    url = primary_url_from_manifest(bp.source_manifest)
    if url and "slideshare.net" in (urlparse(url).hostname or "").lower():
        return _build_slideshare_registry(url)
    return None


def anchor_slides(anchor: str) -> list[int]:
    text = str(anchor or "")
    m = re.search(r"(?:slides?|pp?\.?|pages?)\s*(\d+)\s*[-–—]\s*(\d+)", text, flags=re.I)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b and b - a <= 30:
            return list(range(a, b + 1))
    m = re.search(r"(?:slides?|pp?\.?|pages?)\s*(\d+)", text, flags=re.I)
    if m:
        return [int(m.group(1))]
    # Some old Blueprints use '[P1] 22' without the literal word slide.
    m = re.search(r"\[P1\][^0-9]{0,10}(\d+)", text, flags=re.I)
    return [int(m.group(1))] if m else []


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
    cues = ("figure", "diagram", "architecture", "layer", "model", "process", "structure",
            "component", "protection", "threat", "risk", "guideline", "survivability")
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
            best = ranked[0]
            score = _asset_score(best, unit, anchors)
            # Exact source anchor is sufficient; otherwise require semantic evidence.
            if best.slide_number in anchors or score >= 8.0:
                return VisualPlan(
                    visual_type=visual_type,
                    teaching_purpose=purpose,
                    reuse_mode="USE",
                    citation=f"Source visual: [P1] Slide/Page {best.slide_number} · {registry.source_title}",
                    source_visual_available=True,
                    source_slide=best.slide_number,
                    asset=best,
                    focal_elements=(unit.takeaway, unit.student_action),
                )

    if source_backed:
        return VisualPlan(visual_type, purpose, "REDRAW", anchor or "[P1] source-anchored redraw", False, None, None,
                          (unit.takeaway, unit.student_action))
    return VisualPlan(visual_type, purpose, "NEW", "ISCARB pedagogy — original teaching visualization", False, None, None,
                      (unit.takeaway, unit.student_action))


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
