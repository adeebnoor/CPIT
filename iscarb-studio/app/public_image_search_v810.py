from __future__ import annotations

"""ISCARB v8.1 public visual intelligence.

The engine searches licensed public image providers only when a generated Unit
has no suitable P1 visual and an external visual has a real cognitive job.
External visuals are contextual enrichment, never P1 evidence.

Provider notes:
- Pexels and Pixabay use their own permissive content licenses, not CC0.
- Unsplash uses the Unsplash license and its API requires hotlinking; therefore it
  is disabled for export/proxy use by default.
- Openverse aggregates CC/public-domain metadata but does not itself verify every
  license record. ISCARB preserves the license metadata and landing-page link so
  an instructor can audit reuse.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import hashlib
import json
import math
import os
import re
import sqlite3
import time
from typing import Any
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from . import learning_experience as learning
from .url_source import _validate_public_url

VERSION = "8.1.0"
DATA_ROOT = Path(__file__).resolve().parent.parent / "data"
CACHE_ROOT = DATA_ROOT / "public_visual_cache"
CACHE_ROOT.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_BYTES = int(os.getenv("ISCARB_PUBLIC_IMAGE_MAX_MB", "8")) * 1024 * 1024
SEARCH_TIMEOUT = float(os.getenv("ISCARB_PUBLIC_IMAGE_TIMEOUT", "4.0"))
CACHE_TTL = int(os.getenv("ISCARB_PUBLIC_IMAGE_CACHE_TTL", "86400"))
MIN_WIDTH = int(os.getenv("ISCARB_PUBLIC_IMAGE_MIN_WIDTH", "1024"))
MIN_HEIGHT = int(os.getenv("ISCARB_PUBLIC_IMAGE_MIN_HEIGHT", "768"))
DEFAULT_PROVIDERS = ["openverse", "pexels", "pixabay"]
ALLOWED_IMAGE_TYPES = {"metaphorical", "technical", "real-world", "conceptual"}

STOP = {
    "the","and","for","with","from","into","that","this","what","which","how","why",
    "unit","engineering","software","system","systems","student","students","lecture",
    "source","primary","chapter","your","you","are","was","were","will","may","must",
    "should","can","could","would","have","has","had","about","using","used","use",
}

TECHNICAL_CUES = {
    "architecture","diagram","model","flow","pipeline","stack","layer","network",
    "security","cybersecurity","ai","algorithm","data","protocol","formal","verification",
    "reliability","dependability","redundancy","diversity","risk","process","interface",
}
REAL_WORLD_CUES = {
    "hospital","airport","factory","water","desalination","bank","city","vehicle","operator",
    "team","incident","control room","server room","datacenter","deployment","operations",
}
METAPHOR_CUES = {
    "quote","paradox","illusion","trust","understanding","human","weakest","tension","trade-off",
    "dilemma","responsibility","failure","uncertainty","conflict","why simple","cannot solve",
}


@dataclass(frozen=True)
class SearchBrief:
    image_type: str
    keywords: tuple[str, ...]
    queries: tuple[str, ...]
    cognitive_job: str
    source: str = "LLM-shaped Unit context with deterministic fallback"


@dataclass(frozen=True)
class ImageCandidate:
    provider: str
    provider_id: str
    image_url: str
    thumbnail_url: str
    landing_url: str
    width: int
    height: int
    title: str
    creator: str
    creator_url: str
    license_code: str
    license_label: str
    license_url: str
    created_at: str
    delivery_mode: str = "proxy"
    download_tracking_url: str = ""
    score: float = 0.0
    semantic_score: float = 0.0
    semantic_method: str = "lexical"
    quality_score: float = 0.0
    license_score: float = 0.0
    diversity_score: float = 0.0
    recency_score: float = 0.0

    @property
    def attribution(self) -> str:
        creator = self.creator.strip() or self.provider
        return f"Source: {self.provider} · {creator} · {self.license_label}".strip()


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def _tokens(value: str) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+/#_.-]{2,}", _clean(value).lower())
    out: list[str] = []
    for word in words:
        if word in STOP or word in out:
            continue
        out.append(word)
    return out


def _unit_context(unit: Any) -> str:
    return " ".join([
        _clean(getattr(unit, "title", "")),
        _clean(getattr(unit, "engineering_question", "")),
        _clean(getattr(unit, "visual_suggestion", "")),
        _clean(getattr(unit, "student_action", "")),
        _clean(getattr(unit, "takeaway", "")),
        " ".join(_clean(x) for x in (getattr(unit, "core_content", []) or [])),
        " ".join(_clean(x) for x in (getattr(unit, "pedagogy_content", []) or [])),
    ])


def _visual_plan_hints(unit: Any) -> tuple[str, list[str]]:
    plan = getattr(unit, "visual_plan", None)
    image_type = _clean(getattr(plan, "visual_type", "")).lower() if plan else ""
    focal = [_clean(x) for x in (getattr(plan, "focal_elements", []) or []) if _clean(x)] if plan else []
    return image_type, focal


def _classify_type(context: str, hinted: str = "") -> str:
    h = hinted.lower()
    if h in ALLOWED_IMAGE_TYPES:
        return h
    low = context.lower()
    tok = set(_tokens(low))
    if any(cue in low for cue in METAPHOR_CUES):
        return "metaphorical"
    if tok & TECHNICAL_CUES:
        return "technical"
    if tok & REAL_WORLD_CUES:
        return "real-world"
    return "conceptual"


def build_search_brief(unit: Any) -> SearchBrief:
    """Turn LLM-authored Unit semantics into a bounded 3-5 query search plan.

    The lecture generator already produces title/question/task/visual_plan through
    Gemini when model mode is enabled. This function does not spend another model
    call; it converts those semantic outputs into provider-safe search queries.
    Source-only mode falls back to deterministic keywords.
    """
    context = _unit_context(unit)
    hinted_type, focal = _visual_plan_hints(unit)
    image_type = _classify_type(context, hinted_type)
    keywords: list[str] = []
    for value in [*focal, *_tokens(context)]:
        for token in _tokens(value):
            if token not in keywords:
                keywords.append(token)
        if len(keywords) >= 8:
            break
    if not keywords:
        keywords = ["engineering", "decision"]

    core = " ".join(keywords[:4])
    queries: list[str] = []
    if image_type == "metaphorical":
        queries.extend([
            f"{core} conceptual metaphor",
            f"{core} human technology tension",
            f"{core} decision dilemma",
        ])
    elif image_type == "technical":
        queries.extend([
            f"{core} technical architecture",
            f"{core} engineering diagram",
            f"{core} system visualization",
        ])
    elif image_type == "real-world":
        queries.extend([
            f"{core} real world engineering",
            f"{core} operations environment",
            f"{core} professional context",
        ])
    else:
        queries.extend([
            f"{core} conceptual illustration",
            f"{core} engineering concept",
            f"{core} decision visualization",
        ])
    if len(keywords) >= 6:
        queries.append(" ".join(keywords[:6]))
    visual_suggestion = _clean(getattr(unit, "visual_suggestion", ""))
    if visual_suggestion:
        q = " ".join(_tokens(visual_suggestion)[:7])
        if q:
            queries.append(q)
    deduped: list[str] = []
    for q in queries:
        q = _clean(q)
        if q and q.lower() not in {x.lower() for x in deduped}:
            deduped.append(q)
    queries = deduped[:5]

    jobs = {
        "metaphorical": "Make the learner interpret the metaphor and state how it changes the engineering judgment.",
        "technical": "Make the learner locate a technical element, relation, or boundary and connect it to the decision.",
        "real-world": "Make the learner identify a real operating constraint visible in the image and test transfer of the source concept.",
        "conceptual": "Make the learner map the abstract visual to a source-backed claim and identify where the analogy stops.",
    }
    return SearchBrief(image_type, tuple(keywords[:8]), tuple(queries), jobs[image_type])


def _init_db() -> None:
    with learning._connect() as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS selected_images (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              image_url TEXT NOT NULL,
              lecture_id TEXT NOT NULL,
              slide_id TEXT NOT NULL,
              provider TEXT NOT NULL,
              license_label TEXT NOT NULL,
              attribution TEXT NOT NULL DEFAULT '',
              metadata_json TEXT NOT NULL DEFAULT '{}',
              timestamp REAL NOT NULL,
              UNIQUE(lecture_id, slide_id)
            );
            CREATE INDEX IF NOT EXISTS idx_selected_images_url ON selected_images(image_url);
            CREATE TABLE IF NOT EXISTS public_visual_search_cache (
              cache_key TEXT PRIMARY KEY,
              payload_json TEXT NOT NULL,
              created_at REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS visual_search_settings (
              scope TEXT PRIMARY KEY,
              payload_json TEXT NOT NULL,
              updated_at REAL NOT NULL
            );
            """
        )


_init_db()


def default_settings() -> dict[str, Any]:
    configured = []
    if os.getenv("PEXELS_API_KEY", "").strip():
        configured.append("pexels")
    if os.getenv("PIXABAY_API_KEY", "").strip():
        configured.append("pixabay")
    # Openverse works with conservative unauthenticated usage and is retained as
    # the no-key provider. Unsplash is not in the default export-safe pool.
    providers = ["openverse", *[p for p in configured if p != "openverse"]]
    return {
        "enabled": os.getenv("ISCARB_ENABLE_PUBLIC_IMAGES", "1") == "1",
        "providers": providers or DEFAULT_PROVIDERS,
        "max_queries": 5,
        "max_candidates_per_provider": 6,
        "min_width": MIN_WIDTH,
        "min_height": MIN_HEIGHT,
        "minimum_score": 0.56,
        "allow_unsplash_web_only": os.getenv("ISCARB_ALLOW_UNSPLASH_HOTLINK", "0") == "1",
        "clip_mode": os.getenv("ISCARB_CLIP_MODE", "off").lower(),
        "ai_fallback_enabled": os.getenv("ISCARB_ENABLE_AI_IMAGE_FALLBACK", "0") == "1",
    }


def get_settings(scope: str = "global") -> dict[str, Any]:
    base = default_settings()
    with learning._connect() as con:
        row = con.execute("SELECT payload_json FROM visual_search_settings WHERE scope=?", (scope,)).fetchone()
    if row:
        try:
            custom = json.loads(row["payload_json"])
            if isinstance(custom, dict):
                base.update(custom)
        except Exception:
            pass
    providers = [p for p in (base.get("providers") or []) if p in {"openverse","pexels","pixabay","unsplash"}]
    base["providers"] = providers or ["openverse"]
    return base


def save_settings(body: dict[str, Any], scope: str = "global") -> dict[str, Any]:
    allowed = {
        "enabled","providers","max_queries","max_candidates_per_provider","min_width","min_height",
        "minimum_score","allow_unsplash_web_only","clip_mode","ai_fallback_enabled",
    }
    current = get_settings(scope)
    for key, value in body.items():
        if key in allowed:
            current[key] = value
    current["max_queries"] = max(1, min(5, int(current.get("max_queries", 5))))
    current["max_candidates_per_provider"] = max(1, min(10, int(current.get("max_candidates_per_provider", 6))))
    current["minimum_score"] = max(0.0, min(1.0, float(current.get("minimum_score", .56))))
    current["min_width"] = max(320, min(4096, int(current.get("min_width", MIN_WIDTH))))
    current["min_height"] = max(240, min(2160, int(current.get("min_height", MIN_HEIGHT))))
    current["clip_mode"] = str(current.get("clip_mode", "off")).lower() if str(current.get("clip_mode", "off")).lower() in {"off","local"} else "off"
    current["providers"] = [p for p in (current.get("providers") or []) if p in {"openverse","pexels","pixabay","unsplash"}]
    with learning._connect() as con:
        con.execute(
            "INSERT INTO visual_search_settings(scope,payload_json,updated_at) VALUES(?,?,?) "
            "ON CONFLICT(scope) DO UPDATE SET payload_json=excluded.payload_json,updated_at=excluded.updated_at",
            (scope, json.dumps(current, ensure_ascii=False), time.time()),
        )
    return current


def _json_get(url: str, headers: dict[str, str] | None = None, timeout: float = SEARCH_TIMEOUT) -> dict[str, Any]:
    safe = _validate_public_url(url)
    req = Request(safe, headers={"User-Agent": "ISCARB-Lecture-Studio/8.1", "Accept": "application/json", **(headers or {})})
    with urlopen(req, timeout=timeout) as resp:
        if int(getattr(resp, "status", 200) or 200) >= 400:
            raise RuntimeError(f"Provider returned HTTP {getattr(resp, 'status', '?')}")
        data = resp.read(2_000_000)
    payload = json.loads(data.decode("utf-8", errors="replace"))
    return payload if isinstance(payload, dict) else {}


def _search_openverse(query: str, limit: int) -> list[ImageCandidate]:
    params = urlencode({"q": query, "page_size": min(20, limit), "mature": "false"})
    data = _json_get(f"https://api.openverse.org/v1/images/?{params}")
    out: list[ImageCandidate] = []
    for row in data.get("results") or []:
        if not isinstance(row, dict):
            continue
        license_code = _clean(row.get("license")).lower()
        if license_code not in {"cc0","pdm","by","by-sa","by-nc","by-nc-sa"}:
            continue
        url = _clean(row.get("url"))
        thumb = _clean(row.get("thumbnail")) or url
        if not url:
            continue
        out.append(ImageCandidate(
            provider="Openverse",
            provider_id=_clean(row.get("id")) or hashlib.sha256(url.encode()).hexdigest()[:16],
            image_url=url,
            thumbnail_url=thumb,
            landing_url=_clean(row.get("foreign_landing_url")) or _clean(row.get("detail_url")),
            width=int(row.get("width") or 0), height=int(row.get("height") or 0),
            title=_clean(row.get("title")), creator=_clean(row.get("creator")), creator_url=_clean(row.get("creator_url")),
            license_code=license_code, license_label=("Public Domain" if license_code == "pdm" else "CC0" if license_code == "cc0" else f"CC {license_code.upper()}"),
            license_url=_clean(row.get("license_url")), created_at=_clean(row.get("created_on")),
        ))
    return out[:limit]


def _search_pexels(query: str, limit: int) -> list[ImageCandidate]:
    key = os.getenv("PEXELS_API_KEY", "").strip()
    if not key:
        return []
    params = urlencode({"query": query, "per_page": min(20, limit), "orientation": "landscape"})
    data = _json_get(f"https://api.pexels.com/v1/search?{params}", {"Authorization": key})
    out: list[ImageCandidate] = []
    for row in data.get("photos") or []:
        src = row.get("src") or {}
        url = _clean(src.get("large2x") or src.get("large") or src.get("original"))
        if not url:
            continue
        out.append(ImageCandidate(
            provider="Pexels", provider_id=str(row.get("id") or hashlib.sha256(url.encode()).hexdigest()[:16]),
            image_url=url, thumbnail_url=_clean(src.get("medium")) or url, landing_url=_clean(row.get("url")),
            width=int(row.get("width") or 0), height=int(row.get("height") or 0), title=_clean(row.get("alt")),
            creator=_clean(row.get("photographer")), creator_url=_clean(row.get("photographer_url")),
            license_code="pexels", license_label="Pexels License", license_url="https://www.pexels.com/license/", created_at="",
        ))
    return out[:limit]


def _search_pixabay(query: str, limit: int) -> list[ImageCandidate]:
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        return []
    params = urlencode({
        "key": key, "q": query, "image_type": "photo", "orientation": "horizontal",
        "safesearch": "true", "per_page": max(3, min(20, limit)),
    })
    data = _json_get(f"https://pixabay.com/api/?{params}")
    out: list[ImageCandidate] = []
    for row in data.get("hits") or []:
        url = _clean(row.get("largeImageURL") or row.get("webformatURL"))
        if not url:
            continue
        out.append(ImageCandidate(
            provider="Pixabay", provider_id=str(row.get("id") or hashlib.sha256(url.encode()).hexdigest()[:16]),
            image_url=url, thumbnail_url=_clean(row.get("previewURL")) or url, landing_url=_clean(row.get("pageURL")),
            width=int(row.get("imageWidth") or 0), height=int(row.get("imageHeight") or 0), title=_clean(row.get("tags")),
            creator=_clean(row.get("user")), creator_url="", license_code="pixabay", license_label="Pixabay Content License",
            license_url="https://pixabay.com/service/license-summary/", created_at="",
        ))
    return out[:limit]


def _search_unsplash(query: str, limit: int) -> list[ImageCandidate]:
    key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
    if not key:
        return []
    params = urlencode({"query": query, "per_page": min(20, limit), "orientation": "landscape"})
    data = _json_get(f"https://api.unsplash.com/search/photos?{params}", {"Authorization": f"Client-ID {key}"})
    out: list[ImageCandidate] = []
    for row in data.get("results") or []:
        urls = row.get("urls") or {}; links = row.get("links") or {}; user = row.get("user") or {}
        url = _clean(urls.get("regular"))
        if not url:
            continue
        out.append(ImageCandidate(
            provider="Unsplash", provider_id=_clean(row.get("id")) or hashlib.sha256(url.encode()).hexdigest()[:16],
            image_url=url, thumbnail_url=_clean(urls.get("small")) or url, landing_url=_clean(links.get("html")),
            width=int(row.get("width") or 0), height=int(row.get("height") or 0), title=_clean(row.get("alt_description") or row.get("description")),
            creator=_clean(user.get("name")), creator_url=_clean((user.get("links") or {}).get("html")),
            license_code="unsplash", license_label="Unsplash License", license_url="https://unsplash.com/license", created_at=_clean(row.get("created_at")),
            delivery_mode="hotlink", download_tracking_url=_clean(links.get("download_location")),
        ))
    return out[:limit]


def _provider_search(provider: str, query: str, limit: int, settings: dict[str, Any]) -> list[ImageCandidate]:
    p = provider.lower()
    if p == "openverse":
        return _search_openverse(query, limit)
    if p == "pexels":
        return _search_pexels(query, limit)
    if p == "pixabay":
        return _search_pixabay(query, limit)
    if p == "unsplash" and settings.get("allow_unsplash_web_only"):
        return _search_unsplash(query, limit)
    return []


def _semantic_lexical(brief: SearchBrief, candidate: ImageCandidate) -> float:
    target = set(brief.keywords)
    hay = set(_tokens(" ".join([candidate.title, candidate.provider, candidate.creator])))
    if not target:
        return .45
    overlap = len(target & hay) / max(1, len(target))
    phrase = " ".join(brief.keywords[:4]).lower()
    bonus = .18 if phrase and phrase in candidate.title.lower() else 0.0
    return max(0.0, min(1.0, .28 + overlap * .72 + bonus))


_CLIP = {"model": None, "processor": None, "failed": False}

def _download_bytes(url: str, max_bytes: int = MAX_IMAGE_BYTES, timeout: float = SEARCH_TIMEOUT) -> tuple[bytes, str]:
    safe = _validate_public_url(url)
    req = Request(safe, headers={"User-Agent":"ISCARB-Lecture-Studio/8.1","Accept":"image/avif,image/webp,image/png,image/jpeg,*/*;q=0.5"})
    with urlopen(req, timeout=timeout) as resp:
        final = _validate_public_url(resp.geturl())
        ctype = (resp.headers.get_content_type() or "application/octet-stream").lower()
        if not ctype.startswith("image/"):
            raise ValueError("The selected asset is not an image.")
        data = resp.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("The selected image exceeds the configured size limit.")
        return data, final


def _semantic_clip(brief: SearchBrief, candidate: ImageCandidate) -> float | None:
    """Optional local CLIP reranker.

    It is intentionally lazy. Free Render instances should keep CLIP mode off;
    a production worker can install torch+transformers and set
    ISCARB_CLIP_MODE=local. The response metadata always discloses whether CLIP
    actually ran, so a lexical fallback is never misrepresented as CLIP.
    """
    if _CLIP["failed"]:
        return None
    try:
        if _CLIP["model"] is None:
            import torch  # type: ignore
            from transformers import CLIPModel, CLIPProcessor  # type: ignore
            _CLIP["model"] = CLIPModel.from_pretrained(os.getenv("ISCARB_CLIP_MODEL", "openai/clip-vit-base-patch32"))
            _CLIP["processor"] = CLIPProcessor.from_pretrained(os.getenv("ISCARB_CLIP_MODEL", "openai/clip-vit-base-patch32"))
        from PIL import Image
        import torch  # type: ignore
        raw, _ = _download_bytes(candidate.thumbnail_url or candidate.image_url, max_bytes=3*1024*1024)
        image = Image.open(BytesIO(raw)).convert("RGB")
        text = " ".join(brief.keywords[:8]) or "engineering educational visual"
        processor = _CLIP["processor"]; model = _CLIP["model"]
        inputs = processor(text=[text], images=[image], return_tensors="pt", padding=True)
        with torch.no_grad():
            output = model(**inputs)
        value = float(output.logits_per_image[0][0].item())
        # CLIP logits are unbounded; squash to 0..1 for the weighted ranker.
        return 1.0 / (1.0 + math.exp(-value / 12.0))
    except Exception:
        _CLIP["failed"] = True
        return None


def _quality_score(candidate: ImageCandidate, settings: dict[str, Any]) -> float:
    w, h = max(0, candidate.width), max(0, candidate.height)
    if w and h:
        min_w = int(settings.get("min_width", MIN_WIDTH)); min_h = int(settings.get("min_height", MIN_HEIGHT))
        resolution = min(1.0, min(w / max(1,min_w), h / max(1,min_h)))
        ratio = w / max(1,h)
        aspect = 1.0 if 1.25 <= ratio <= 2.1 else .65 if 1.0 <= ratio <= 2.5 else .35
        return round(.78 * resolution + .22 * aspect, 4)
    # Unknown dimensions are allowed but cannot win the quality criterion.
    return .42


def _license_score(candidate: ImageCandidate) -> float:
    code = candidate.license_code.lower()
    if code in {"cc0","pdm"}: return 1.0
    if code in {"by","by-sa"}: return .92
    if code in {"by-nc","by-nc-sa"}: return .76
    if code in {"pexels","pixabay"}: return .88
    if code == "unsplash": return .74
    return 0.0


def _recency_score(candidate: ImageCandidate) -> float:
    text = candidate.created_at
    if not text:
        return .5
    m = re.search(r"(20\d{2})", text)
    if not m:
        return .5
    age = max(0, datetime.now(timezone.utc).year - int(m.group(1)))
    return 1.0 if age <= 5 else .65 if age <= 10 else .35


def _used_urls() -> set[str]:
    with learning._connect() as con:
        rows = con.execute("SELECT image_url FROM selected_images").fetchall()
    return {str(r["image_url"]) for r in rows}


def score_candidate(brief: SearchBrief, candidate: ImageCandidate, settings: dict[str, Any], used: set[str]) -> ImageCandidate:
    semantic_method = "lexical"
    semantic = None
    if str(settings.get("clip_mode", "off")).lower() == "local":
        semantic = _semantic_clip(brief, candidate)
        if semantic is not None:
            semantic_method = "clip"
    if semantic is None:
        semantic = _semantic_lexical(brief, candidate)
    quality = _quality_score(candidate, settings)
    license_s = _license_score(candidate)
    diversity = 0.0 if candidate.image_url in used else 1.0
    recency = _recency_score(candidate)
    total = .40*semantic + .25*quality + .20*license_s + .10*diversity + .05*recency
    return ImageCandidate(**{
        **asdict(candidate), "score": round(total,4), "semantic_score": round(semantic,4),
        "semantic_method": semantic_method, "quality_score": quality, "license_score": license_s,
        "diversity_score": diversity, "recency_score": recency,
    })


def _cache_key(job_id: str, unit_no: int, brief: SearchBrief, settings: dict[str, Any]) -> str:
    raw = json.dumps({"j":job_id,"u":unit_no,"q":brief.queries,"p":settings.get("providers"),"clip":settings.get("clip_mode")}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()


def _cache_get(key: str) -> dict[str, Any] | None:
    with learning._connect() as con:
        row = con.execute("SELECT payload_json,created_at FROM public_visual_search_cache WHERE cache_key=?", (key,)).fetchone()
    if not row or time.time() - float(row["created_at"]) > CACHE_TTL:
        return None
    try:
        payload = json.loads(row["payload_json"])
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _cache_put(key: str, payload: dict[str, Any]) -> None:
    with learning._connect() as con:
        con.execute(
            "INSERT INTO public_visual_search_cache(cache_key,payload_json,created_at) VALUES(?,?,?) "
            "ON CONFLICT(cache_key) DO UPDATE SET payload_json=excluded.payload_json,created_at=excluded.created_at",
            (key, json.dumps(payload, ensure_ascii=False), time.time()),
        )


def _selected(job_id: str, unit_no: int) -> dict[str, Any] | None:
    with learning._connect() as con:
        row = con.execute("SELECT metadata_json FROM selected_images WHERE lecture_id=? AND slide_id=?", (job_id, str(unit_no))).fetchone()
    if not row:
        return None
    try:
        payload = json.loads(row["metadata_json"])
        return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _remember(job_id: str, unit_no: int, candidate: ImageCandidate, payload: dict[str, Any]) -> None:
    with learning._connect() as con:
        con.execute(
            "INSERT INTO selected_images(image_url,lecture_id,slide_id,provider,license_label,attribution,metadata_json,timestamp) VALUES(?,?,?,?,?,?,?,?) "
            "ON CONFLICT(lecture_id,slide_id) DO UPDATE SET image_url=excluded.image_url,provider=excluded.provider,license_label=excluded.license_label,attribution=excluded.attribution,metadata_json=excluded.metadata_json,timestamp=excluded.timestamp",
            (candidate.image_url, job_id, str(unit_no), candidate.provider, candidate.license_label, candidate.attribution, json.dumps(payload, ensure_ascii=False), time.time()),
        )


def public_visual_for_unit(job: Any, unit_no: int, p1_visual_exists: bool = False) -> dict[str, Any]:
    unit = next((u for u in job.blueprint.units if int(u.number) == int(unit_no)), None)
    if unit is None:
        return {"status":"not_found"}
    if p1_visual_exists:
        return {"status":"p1_preferred", "reason":"A source-backed P1 visual is already mapped; public search is suppressed."}
    existing = _selected(str(job.id), unit_no)
    if existing:
        existing["cached_selection"] = True
        return existing

    settings = get_settings(str(job.id))
    if not settings.get("enabled"):
        return {"status":"disabled"}
    brief = build_search_brief(unit)
    key = _cache_key(str(job.id), unit_no, brief, settings)
    cached = _cache_get(key)
    if cached and cached.get("status") in {"selected","fallback"}:
        if cached.get("status") == "selected" and isinstance(cached.get("candidate"), dict):
            try:
                c = ImageCandidate(**cached["candidate"])
                _remember(str(job.id), unit_no, c, cached)
            except Exception:
                pass
        return cached

    used = _used_urls()
    candidates: dict[str, ImageCandidate] = {}
    errors: list[str] = []
    providers = settings.get("providers") or ["openverse"]
    max_queries = int(settings.get("max_queries",5)); per_provider = int(settings.get("max_candidates_per_provider",6))
    started = time.monotonic()
    for query in brief.queries[:max_queries]:
        if time.monotonic() - started > max(SEARCH_TIMEOUT, 3.0):
            break
        for provider in providers:
            if time.monotonic() - started > max(SEARCH_TIMEOUT, 3.0):
                break
            try:
                for c in _provider_search(str(provider), query, per_provider, settings):
                    candidates.setdefault(c.image_url, c)
            except Exception as exc:
                errors.append(f"{provider}: {type(exc).__name__}")

    ranked = [score_candidate(brief, c, settings, used) for c in candidates.values() if _license_score(c) > 0]
    ranked.sort(key=lambda c: c.score, reverse=True)
    chosen = next((c for c in ranked if c.score >= float(settings.get("minimum_score",.56)) and c.diversity_score > 0), None)
    if chosen:
        payload = {
            "status":"selected", "version":VERSION, "brief":asdict(brief), "candidate":asdict(chosen),
            "image_url": f"/api/learning/{job.id}/public-visual-image/{unit_no}",
            "source_anchor": f"External visual · {chosen.provider}",
            "source_footer": chosen.attribution,
            "license_url": chosen.license_url, "landing_url": chosen.landing_url,
            "interaction_prompt": brief.cognitive_job,
            "ranking_weights": {"semantic":.40,"quality":.25,"license":.20,"diversity":.10,"recency":.05},
            "clip_used": chosen.semantic_method == "clip",
            "license_guard": "Licensed reuse metadata preserved; instructor should audit the linked source when required by policy.",
            "provider_errors": errors[:6],
        }
        _remember(str(job.id), unit_no, chosen, payload)
        _cache_put(key, payload)
        return payload

    fallback = {
        "status":"fallback", "version":VERSION, "brief":asdict(brief),
        "fallback": {
            "kind": "ai-generator-ready" if settings.get("ai_fallback_enabled") else "open-icon",
            "note": "No sufficiently licensed/relevant public image cleared the ranking gate. Do not insert an arbitrary web image.",
            "icon": "image_search_off",
        },
        "clip_used": False,
        "provider_errors": errors[:6],
    }
    _cache_put(key, fallback)
    return fallback


def selected_candidate(job_id: str, unit_no: int) -> ImageCandidate | None:
    payload = _selected(job_id, unit_no)
    if not payload or payload.get("status") != "selected" or not isinstance(payload.get("candidate"), dict):
        return None
    try:
        return ImageCandidate(**payload["candidate"])
    except Exception:
        return None


def cached_image_path(job_id: str, unit_no: int) -> Path | None:
    candidate = selected_candidate(job_id, unit_no)
    if candidate is None:
        return None
    if candidate.delivery_mode == "hotlink":
        return None
    digest = hashlib.sha256(candidate.image_url.encode()).hexdigest()[:20]
    existing = list(CACHE_ROOT.glob(f"{job_id}-{unit_no}-{digest}.*"))
    if existing:
        return existing[0]
    raw, _ = _download_bytes(candidate.image_url)
    # Derive extension from magic bytes rather than untrusted URL suffix.
    ext = ".jpg"
    if raw.startswith(b"\x89PNG\r\n\x1a\n"): ext = ".png"
    elif raw[:4] in {b"RIFF"}: ext = ".webp"
    elif raw[:3] == b"GIF": ext = ".gif"
    path = CACHE_ROOT / f"{job_id}-{unit_no}-{digest}{ext}"
    path.write_bytes(raw)
    return path


def selected_image_history(limit: int = 100) -> list[dict[str, Any]]:
    with learning._connect() as con:
        rows = con.execute(
            "SELECT image_url,lecture_id,slide_id,provider,license_label,attribution,timestamp FROM selected_images ORDER BY timestamp DESC LIMIT ?",
            (max(1,min(500,int(limit))),),
        ).fetchall()
    return [dict(r) for r in rows]
