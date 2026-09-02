from __future__ import annotations

"""ISCARB v4.6.12: source-first visuals, public-image fallback, leaner canvas."""

import hashlib, json, mimetypes, re
from pathlib import Path
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

from . import source_visuals as sv
from . import presenter_v44 as pv
from . import deterministic_blueprint_fallback as db
from . import faculty_outputs as fo

PUBLIC_WEB_KIND = "public-web"
PUBLIC_VISUAL_UNITS = {1, 4, 8, 10, 11, 13, 14, 15, 16, 17, 18, 20}


def _words(text: str, limit: int = 34) -> str:
    bits = re.sub(r"\s+", " ", str(text or "")).strip().split()
    return " ".join(bits[:limit])


def _first_source_line(profile) -> str:
    for item in getattr(profile, "coverage_items", []) or []:
        text = str(getattr(item, "why_important", "") or "").strip()
        if len(text.split()) >= 10:
            return _words(text, 32)
    return ""


def _public_query(bp, unit) -> str:
    raw = f"{bp.lecture_title} {unit.title} {unit.engineering_question}"
    raw = re.sub(r"\b\d+(?:\.\d+)*\b", " ", raw)
    raw = re.sub(r"[^A-Za-z0-9\s-]", " ", raw)
    stop = {"engineering","software","system","systems","source","unit","lecture","what","which","that","this","from","with","into"}
    words = [w for w in raw.split() if len(w) >= 4 and w.lower() not in stop]
    return " ".join(words[:8]).strip()


def _public_asset(bp, unit):
    query = _public_query(bp, unit)
    if not query:
        return None
    cache = sv._cache_dir("wikimedia:" + query)
    meta = cache / "manifest.json"
    data = None
    if meta.exists():
        try: data = json.loads(meta.read_text(encoding="utf-8"))
        except Exception: pass
    if data is None:
        url = (
            "https://en.wikipedia.org/w/api.php?action=query&format=json&generator=search"
            f"&gsrsearch={quote_plus(query)}&gsrlimit=6&prop=pageimages|info|extracts"
            "&piprop=thumbnail&pithumbsize=1600&inprop=url&exintro=1&explaintext=1"
        )
        try:
            req = Request(url, headers={"User-Agent":"ISCARB-Visual-Lecture-Engine/2.2","Accept":"application/json"})
            with urlopen(req, timeout=10) as resp: data = json.loads(resp.read(sv.MAX_VISUAL_BYTES).decode("utf-8","ignore"))
            meta.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        except Exception:
            return None
    pages = list(((data or {}).get("query") or {}).get("pages", {}).values())
    keys = sv._keywords(unit)
    def score(page):
        blob = (str(page.get("title") or "") + " " + str(page.get("extract") or "")).lower()
        return sum(3 for k in keys if k in blob) + (5 if (page.get("thumbnail") or {}).get("source") else 0)
    for page in sorted(pages, key=score, reverse=True):
        thumb = (page.get("thumbnail") or {}).get("source")
        if not thumb: continue
        title = str(page.get("title") or query)
        full = str(page.get("fullurl") or ("https://en.wikipedia.org/wiki/" + title.replace(" ", "_")))
        return sv.VisualAsset(0, str(thumb), title, full, "", PUBLIC_WEB_KIND, 0.0, ())
    return None


def _download_public(asset):
    cache = sv._cache_dir(asset.source_url or asset.image_url)
    ext = Path(urlparse(asset.image_url).path).suffix.lower()
    if ext not in {".jpg",".jpeg",".png",".webp"}: ext = ".jpg"
    path = cache / ("web-asset" + ext)
    if path.exists() and path.stat().st_size > 1000: return path
    try:
        safe = sv._validate_public_url(asset.image_url)
        req = Request(safe, headers={"User-Agent":"ISCARB-Visual-Lecture-Engine/2.2","Accept":"image/*"})
        with urlopen(req, timeout=12) as resp:
            host = (urlparse(resp.geturl()).hostname or "").lower()
            if not any(host.endswith(x) for x in ("upload.wikimedia.org","wikimedia.org","wikipedia.org")): return None
            data = resp.read(sv.MAX_VISUAL_BYTES + 1)
            if not 1000 < len(data) <= sv.MAX_VISUAL_BYTES: return None
            ctype = (resp.headers.get_content_type() or "").lower()
            if not ctype.startswith("image/"): return None
            guessed = mimetypes.guess_extension(ctype) or ext
            if guessed in {".jpe",".jpeg"}: guessed = ".jpg"
            path = cache / ("web-asset" + guessed)
            path.write_bytes(data)
            return path
    except Exception:
        return None


def install():
    original_score = sv._asset_score
    def score(asset, unit, anchors):
        value = original_score(asset, unit, anchors)
        if asset.source_kind == getattr(sv, "FIGURE_KIND", "local-pdf-figure"): value += 12
        elif asset.source_kind == getattr(sv, "PICTURE_KIND", "local-pdf-picture"): value += 9
        elif asset.source_kind == "local-pdf" and asset.visual_area_ratio < .12: value -= 8
        return value
    sv._asset_score = score

    original_plan = sv.plan_for_unit
    def plan(bp, unit, registry=None):
        candidate = original_plan(bp, unit, registry)
        if candidate.reuse_mode == "USE": return candidate
        if unit.number in PUBLIC_VISUAL_UNITS:
            asset = _public_asset(bp, unit)
            if asset:
                return sv.VisualPlan(candidate.visual_type, candidate.teaching_purpose, "USE",
                    f"Illustrative public image · {asset.alt_text} · {asset.source_url}", False, None, asset,
                    (unit.takeaway, unit.student_action))
        return candidate
    sv.plan_for_unit = plan

    original_local = sv.local_asset
    def local(asset):
        if getattr(asset, "source_kind", "") == PUBLIC_WEB_KIND:
            return _download_public(asset)
        return original_local(asset)
    sv.local_asset = local
    pv.local_asset = local

    path_attr = "visual_path" if hasattr(pv, "visual_path") else "exact_source_path"
    original_exact = getattr(pv, path_attr)
    def exact(unit, plan_):
        if plan_ and getattr(getattr(plan_, "asset", None), "source_kind", "") == PUBLIC_WEB_KIND:
            return local(plan_.asset)
        return original_exact(unit, plan_)
    setattr(pv, path_attr, exact)

    original_caption = pv.source_caption
    def caption(unit, plan_):
        asset = getattr(plan_, "asset", None) if plan_ else None
        if asset is not None and getattr(asset, "source_kind", "") == PUBLIC_WEB_KIND:
            return f"Illustrative public image · {asset.alt_text} · {asset.source_url}"
        return original_caption(unit, plan_)
    pv.source_caption = caption

    original_build = db.build_deterministic_blueprint
    def build(profile):
        bp = original_build(profile)
        u = bp.units[0]
        if not u.core_content:
            line = _first_source_line(profile)
            if line: u.core_content = [line]
        return bp
    db.build_deterministic_blueprint = build

    original_pdf = fo.export_detailed_pdf
    def detailed(bp, out):
        copy = bp.model_copy(deep=True)
        for u in copy.units:
            u.student_action = _words(u.student_action, 34)
            u.takeaway = _words(u.takeaway, 34)
            u.source_anchor = _words(u.source_anchor, 22)
            ev = str(u.evidence or "")
            if "PRESERVED SOURCE DETAIL (speaker notes):" in ev:
                ev = ev.split("PRESERVED SOURCE DETAIL (speaker notes):", 1)[0].strip() + " Preserved overflow remains in presenter notes."
            u.evidence = _words(ev, 34)
        return original_pdf(copy, out)
    fo.export_detailed_pdf = detailed
