from __future__ import annotations

"""Source-aware visual planning for ISCARB Presenter v2.

This layer is deliberately deterministic and optional. It never changes the
technical content of a Blueprint. When a public SlideShare P1 exposes slide
images, the planner can use a relevant source slide as the dominant teaching
visual with explicit citation. If no safe/relevant source visual is available,
Presenter rendering falls back to the existing ISCARB diagram grammar.
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

from bs4 import BeautifulSoup

from .models import Blueprint, LectureUnit
from .url_source import _download, _validate_public_url

APP_ROOT = Path(__file__).resolve().parent
CACHE_ROOT = APP_ROOT.parent / "data" / "source_visual_cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)
MAX_VISUAL_BYTES = 4 * 1024 * 1024
MAX_SLIDES = 80


@dataclass(frozen=True)
class VisualAsset:
    slide_number: int
    image_url: str
    alt_text: str
    source_url: str


@dataclass(frozen=True)
class VisualRegistry:
    source_url: str
    source_title: str
    assets: tuple[VisualAsset, ...]


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
    1: "incident-scene",
    2: "domain-map",
    3: "capability-evidence-path",
    4: "six-lens-model",
    5: "predict-derive-reveal",
    6: "mechanism-diagram",
    7: "architecture-diagram",
    8: "tradeoff-decision-matrix",
    9: "claim-test-falsification",
    10: "uncertainty-map",
    11: "context-system-map",
    12: "accountability-map",
    13: "trend-implication-map",
    14: "workload-recovery-map",
    15: "ai-permissibility-gate",
    16: "mission-brief",
    17: "constraint-mutation",
    18: "claim-evidence-warrant",
    19: "performance-ladder",
    20: "assurance-case-tree",
}

TEACHING_PURPOSE = {
    1: "Expose the failure before naming the mechanism.",
    2: "Show the complete technical territory of the primary lecture.",
    3: "Make capability promises traceable to evidence.",
    4: "Force the learner to inspect the same decision through six human-engineering lenses.",
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

# These units most often benefit from a source figure/architecture/process image.
SOURCE_VISUAL_PRIORITY = {6, 7, 8, 9, 12, 13}

_STOP = {
    "the", "and", "for", "with", "from", "into", "that", "this", "what", "which",
    "how", "why", "unit", "engineering", "software", "system", "systems", "security",
    "design", "source", "student", "students", "lecture", "using", "used", "use",
}


def _cache_dir(url: str) -> Path:
    key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
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


def _candidate_image_url(img) -> str:
    values = [
        img.get("data-full"), img.get("data-normal"), img.get("data-src"),
        img.get("data-lazy-src"), img.get("src"), img.get("srcset"),
    ]
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
    cache = _cache_dir(url)
    manifest_path = cache / "manifest.json"
    if manifest_path.exists():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            assets = tuple(VisualAsset(**x) for x in data.get("assets", []))
            if assets:
                return VisualRegistry(data.get("source_url", url), data.get("source_title", "SlideShare lecture"), assets)
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
        assets.append(VisualAsset(len(assets) + 1, image_url, alt, final_url))
        if len(assets) >= MAX_SLIDES:
            break

    if not assets:
        return None
    registry = VisualRegistry(final_url, title, tuple(assets))
    manifest_path.write_text(json.dumps({
        "source_url": final_url,
        "source_title": title,
        "assets": [asdict(x) for x in assets],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return registry


def load_registry(bp: Blueprint) -> VisualRegistry | None:
    url = primary_url_from_manifest(bp.source_manifest)
    if not url:
        return None
    host = (urlparse(url).hostname or "").lower()
    if "slideshare.net" not in host:
        return None
    return _build_slideshare_registry(url)


def anchor_slides(anchor: str) -> list[int]:
    text = str(anchor or "")
    nums: list[int] = []
    # SLIDE 7, SLIDES 7-12, P1 7–12
    m = re.search(r"(?:slides?|pp?\.?|pages?)\s*(\d+)\s*[-–—]\s*(\d+)", text, flags=re.I)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if a <= b and b - a <= 30:
            return list(range(a, b + 1))
    m = re.search(r"(?:slides?|pp?\.?|pages?)\s*(\d+)", text, flags=re.I)
    if m:
        return [int(m.group(1))]
    return nums


def _keywords(unit: LectureUnit) -> set[str]:
    raw = " ".join([unit.title, unit.engineering_question, *unit.core_content[:4]])
    words = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{3,}", raw.lower()))
    return {w for w in words if w not in _STOP}


def _asset_score(asset: VisualAsset, unit: LectureUnit, anchors: set[int]) -> float:
    alt = asset.alt_text.lower()
    kws = _keywords(unit)
    overlap = sum(1 for w in kws if w in alt)
    score = overlap * 4.0
    if asset.slide_number in anchors:
        score += 14.0
    # Favor likely diagram/process/architecture slides over long bullet slides.
    cues = ("figure", "diagram", "architecture", "layer", "model", "process", "structure", "component", "protection", "system")
    score += sum(2.0 for cue in cues if cue in alt)
    n = len(asset.alt_text)
    if 45 <= n <= 420:
        score += 3.0
    elif n > 900:
        score -= 5.0
    return score


def plan_for_unit(bp: Blueprint, unit: LectureUnit, registry: VisualRegistry | None = None) -> VisualPlan:
    visual_type = VISUAL_TYPES.get(unit.number, "concept-visual")
    purpose = TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip()
    has_p1 = "P1" in anchor.upper()
    registry = registry if registry is not None else load_registry(bp)

    if registry and unit.number in SOURCE_VISUAL_PRIORITY and has_p1:
        anchors = set(anchor_slides(anchor))
        ranked = sorted(registry.assets, key=lambda a: _asset_score(a, unit, anchors), reverse=True)
        if ranked and _asset_score(ranked[0], unit, anchors) >= (9.0 if anchors else 6.0):
            asset = ranked[0]
            return VisualPlan(
                visual_type=visual_type,
                teaching_purpose=purpose,
                reuse_mode="USE",
                citation=f"Source visual: [P1] Slide {asset.slide_number} · {registry.source_title}",
                source_visual_available=True,
                source_slide=asset.slide_number,
                asset=asset,
                focal_elements=(unit.takeaway, unit.student_action),
            )

    if has_p1:
        return VisualPlan(
            visual_type=visual_type,
            teaching_purpose=purpose,
            reuse_mode="REDRAW",
            citation=anchor or "[P1] source-anchored redraw",
            focal_elements=(unit.takeaway, unit.student_action),
        )
    return VisualPlan(
        visual_type=visual_type,
        teaching_purpose=purpose,
        reuse_mode="NEW",
        citation="ISCARB pedagogy — original teaching visualization",
        focal_elements=(unit.takeaway, unit.student_action),
    )


def plans_for_blueprint(bp: Blueprint) -> list[VisualPlan]:
    registry = load_registry(bp)
    return [plan_for_unit(bp, unit, registry) for unit in bp.units]


def local_asset(asset: VisualAsset) -> Path | None:
    cache = _cache_dir(asset.source_url)
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
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"
