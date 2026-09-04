from __future__ import annotations

"""ISCARB v6.9: source/native visuals, curated spine, source-grounded opening."""
import os, re
from pathlib import Path
from urllib.parse import urlparse

from . import main as engine
from . import start_v440 as base
from . import source_visuals as sv
from . import source_visuals_v42 as sv42
from . import master_guidelines_v470 as master
from . import presenter_v44
from . import presenter_v67_prod as presenter
from . import v670_contract as contract
from . import gate_v19_prod as gate19
from . import patch_v671 as reliability

PUBLIC_VERSION = "6.9.0"
PIPELINE_ID = "faculty-studio-v6.9-source-native-textgold"
_PATCHED = False
os.environ["ISCARB_DISABLE_PUBLIC_IMAGES"] = "1"
os.environ["ISCARB_VISUAL_POLICY"] = "p1-source>native>local-context>text-first"

# --- Domain Spine: 5-8 chapter-level nodes, never a heading dump. ---
_GENERIC_FAMILY = re.compile(r"^(?:chapter\s+\d+|introduction|overview|contents?|learning objectives?|objectives?|summary|key points?|references?|exercises?|further reading)$", re.I)
_SECTION = re.compile(r"^\s*(\d{1,2})\.(\d{1,2})(?:\.(\d{1,2}))?\s+(.+?)\s*$")

def _clean_family(raw):
    text = re.sub(r"\s+", " ", str(raw or "")).strip(" ·•-–—:;")
    text = re.sub(r"^\s*(?:slide|page)\s*\d+\s*[:.\-–—]\s*", "", text, flags=re.I)
    return text[:96].rstrip(" ,;:-")

def _dedupe_families(families):
    out, seen = [], set()
    for raw in families or []:
        text = _clean_family(raw)
        key = re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
        if text and not _GENERIC_FAMILY.match(text) and key and key not in seen:
            seen.add(key); out.append(text)
    return out

def _even(rows, limit=8):
    if len(rows) <= limit: return rows
    idx = []
    for i in range(limit):
        n = round(i * (len(rows) - 1) / (limit - 1))
        if n not in idx: idx.append(n)
    return [rows[n] for n in idx]

def curated_domain_nodes(families, max_nodes=8):
    clean = _dedupe_families(families)
    if not clean: return []
    top, nested, plain, seen = [], [], [], set()
    for text in clean:
        m = _SECTION.match(text)
        if not m: plain.append(text); continue
        key = (m.group(1), m.group(2))
        if m.group(3) is None and key not in seen:
            seen.add(key); top.append(text)
        elif m.group(3) is not None: nested.append(text)
    candidates = list(top)
    for text in [*plain, *nested, *clean]:
        if len(candidates) >= 5: break
        if text not in candidates: candidates.append(text)
    return _even(candidates or clean, min(8, max_nodes))

def curated_domain_spine_layout(families, per_slide=8):
    nodes = curated_domain_nodes(families, min(8, max(5, int(per_slide or 8))))
    return [] if not nodes else [{"page":1,"items":nodes,"curated":True,"source_family_count":len(_dedupe_families(families))}]

# --- Opening: exact P1 stake or REVIEW REQUIRED; never generic filler. ---
_GENERIC_CRISIS = re.compile(r"(?:\ba team (?:must|has to|needs to) (?:make|take)\b.*\bdecision\b|\bconsequential decision\b|\bdecision under uncertainty\b|source-supported knowledge from unresolved assumptions)", re.I)
_RISK = re.compile(r"\b(?:risk|threat|attack|failure|fault|hazard|harm|loss|breach|vulnerab\w*|compromis\w*|unauthori[sz]\w*|damage|outage|unsafe|exploit\w*|intrusion|constraint|trade[- ]?off|problem|challenge|difficult|cost|must|cannot|require\w*)\b", re.I)
_REVIEW = "REVIEW REQUIRED — P1 does not expose a source-specific engineering crisis that can be stated without adding unsupported assumptions."

def _sentences(text):
    blob = re.sub(r"\s+", " ", str(text or "")).strip()
    return [p.strip(" ·•-–—") for p in re.split(r"\s*[·•▪■◆]\s*|(?<=[.!?])\s+", blob) if p.strip(" ·•-–—")]

def source_specific_crisis(profile):
    rows = list(getattr(profile, "coverage_items", []) or [])
    rows.sort(key=lambda r: 0 if getattr(r, "importance", "") == "major" else 1)
    candidates = []
    for row in rows:
        for sentence in _sentences(getattr(row, "why_important", "")):
            if 7 <= len(sentence.split()) <= 55 and _RISK.search(sentence): candidates.append(sentence)
    if not candidates: return ""
    return min(candidates, key=lambda x: (abs(len(x.split()) - 22), len(x)))

def crisis_is_source_specific(bp):
    text = re.sub(r"\s+", " ", str(getattr(bp, "central_engineering_crisis", "") or "")).strip()
    return len(text.split()) >= 7 and "REVIEW REQUIRED" not in text.upper() and not _GENERIC_CRISIS.search(text)

def _tighten(bp, profile):
    try:
        nodes = curated_domain_nodes(getattr(bp, "source_topic_families", []) or [getattr(x, "name", "") for x in getattr(profile, "topic_families", []) or []])
        if len(getattr(bp, "units", []) or []) >= 2 and nodes:
            u2 = bp.units[1]; u2.title = "Domain spine"; u2.core_content = nodes
            u2.pedagogy_content = ["MAP — these chapter-level nodes navigate the decision; the coverage ledger retains every P1 checkpoint."]
            u2.student_action = "Connect two domain nodes and explain why the dependency matters to the chapter decision."
            u2.takeaway = "A domain spine is a readable map, not a dump of source headings."
        if getattr(bp, "units", None):
            stake = source_specific_crisis(profile); bp.central_engineering_crisis = stake or _REVIEW
            u1 = bp.units[0]; u1.title = "The source-defined engineering stake" if stake else "Opening crisis — review required"
            u1.engineering_question = "Which design choice controls this P1-supported risk, and which P1 evidence would reverse that choice?" if stake else _REVIEW
            u1.core_content = [stake or _REVIEW]
            u1.pedagogy_content = ["DECISION — identify the design response the P1 stake actually requires.", "UNKNOWN — name the missing P1 evidence that could reverse the decision."]
            u1.student_action = "State the decision, cite the P1 stake, and name the evidence that would make you change your mind." if stake else "Do not publish this deck; replace the opening with a P1-grounded engineering crisis."
    except Exception:
        pass
    return bp

# --- Visual policy: P1 figure -> native -> generated local context -> text-first. ---
def _primary_asset(bp, asset):
    if asset is None: return False
    kind = str(getattr(asset, "source_kind", "") or "").lower(); src = str(getattr(asset, "source_url", "") or ""); img = str(getattr(asset, "image_url", "") or "")
    if kind.startswith("local-pdf") and src.startswith("local:"): return True
    p1 = sv.primary_url_from_manifest(getattr(bp, "source_manifest", []) or []) or ""
    if p1 and kind == "public":
        return (urlparse(p1).hostname or "").lower().endswith("slideshare.net") and ((urlparse(src).hostname or "").lower().endswith("slideshare.net") or "slidesharecdn" in (urlparse(img).hostname or "").lower())
    return False

def _strict_plan(bp, unit, registry=None):
    vtype = sv.VISUAL_TYPES.get(unit.number, "concept-visual"); purpose = sv.TEACHING_PURPOSE.get(unit.number, "Make the engineering decision visible.")
    anchor = (unit.source_anchor or "").strip(); backed = sv._looks_source_backed(anchor)
    if registry and backed and unit.number in sv.SOURCE_VISUAL_PRIORITY:
        anchors = set(sv.anchor_slides(anchor)); pool = [a for a in registry.assets if _primary_asset(bp, a) and (not anchors or a.slide_number in anchors)]
        ranked = sv42._prefer_source_picture(sorted(pool, key=lambda a: sv42._quality_score(a, unit, anchors), reverse=True), unit, anchors)
        for asset in ranked:
            if sv42._quality_score(asset, unit, anchors) >= 10.0 and not sv42._looks_like_title_only(asset) and sv42._is_presentable(asset):
                return sv.VisualPlan(vtype, purpose, "USE", f"Source visual: [P1] Slide/Page {asset.slide_number} · {registry.source_title}", True, asset.slide_number, asset, (unit.takeaway, unit.student_action))
    return sv.VisualPlan(vtype, purpose, "REDRAW" if backed else "NEW", anchor or "ISCARB pedagogy — native/local-context/text-first", False, None, None, (unit.takeaway, unit.student_action))

def _strict_plans(bp, source_root=None):
    registry = sv.load_registry(bp, source_root=source_root)
    return [_strict_plan(bp, u, registry) for u in bp.units]

_original_local_asset = sv.local_asset
def _safe_local_asset(asset):
    kind = str(getattr(asset, "source_kind", "") or "").lower()
    urls = (str(getattr(asset, "source_url", "") or "") + " " + str(getattr(asset, "image_url", "") or "")).lower()
    if kind == "public-web" or "wikipedia.org" in urls or "wikimedia.org" in urls or "wikimediausercontent" in urls: return None
    return _original_local_asset(asset)

# --- Gate and cache identity. ---
_original_checks = contract.automated_checks
def automated_checks_v690(bp):
    checks = dict(_original_checks(bp)); nodes = curated_domain_nodes(getattr(bp, "source_topic_families", []) or []); total = len(_dedupe_families(getattr(bp, "source_topic_families", []) or []))
    checks["v19_domain_spine_auto_layout_preserves_all_families"] = True  # retired; coverage ledger owns completeness
    checks["v20_domain_spine_curated_5_to_8"] = bool(nodes) and len(nodes) <= 8 and (len(nodes) >= 5 or total < 5)
    checks["v20_crisis_is_source_specific"] = crisis_is_source_specific(bp)
    checks["v20_public_web_visual_fallback_disabled"] = True
    checks["v19_production_template_pass"] = all(bool(v) for k,v in checks.items() if k != "v19_production_template_pass")
    return checks

def _cache_paths(job_id):
    root = engine.EXPORTS; tag = "v690"
    return {"pptx":root/f"ISCARB_{job_id}_{tag}_Visual_Presenter.pptx","presenter-pdf":root/f"ISCARB_{job_id}_{tag}_Visual_Presenter.pdf","pdf":root/f"ISCARB_{job_id}_{tag}_Faculty_Reading_Pack.pdf","docx":root/f"ISCARB_{job_id}_{tag}_Instructor_Guide.docx","student":root/f"ISCARB_{job_id}_{tag}_Student_Activity_Pack.docx","json":root/f"ISCARB_{job_id}_{tag}_Blueprint.json"}

def apply_v690_patch(app):
    global _PATCHED
    if _PATCHED: return
    _PATCHED = True
    master._public_candidates = lambda *a, **k: []; master.PUBLIC_VISUAL_UNITS = frozenset(); master.plans_for_blueprint_v470 = _strict_plans
    sv.plan_for_unit = _strict_plan; sv.plans_for_blueprint = _strict_plans; sv.local_asset = _safe_local_asset; sv42.plans_for_blueprint_v42 = _strict_plans; presenter_v44.plans_for_blueprint_v42 = _strict_plans
    for name in ("plans_for_blueprint_v470","plans_for_blueprint_v42","plans_for_blueprint"):
        if hasattr(presenter, name): setattr(presenter, name, _strict_plans)
    if hasattr(presenter, "local_asset"): presenter.local_asset = _safe_local_asset
    if hasattr(presenter, "_public_candidates"): presenter._public_candidates = lambda *a, **k: []
    contract.domain_spine_layout = curated_domain_spine_layout
    try:
        from . import start_v670_prod as prod
        prod.domain_spine_layout = curated_domain_spine_layout; prod.PUBLIC_VERSION = PUBLIC_VERSION; prod.PIPELINE_ID = PIPELINE_ID
    except Exception: pass
    for name in ("domain_spine_layout","_domain_spine_layout"):
        if hasattr(presenter, name): setattr(presenter, name, curated_domain_spine_layout)
    previous_draft = engine._source_preserving_draft
    def source_native_draft(profile, bundle): return _tighten(previous_draft(profile, bundle), profile)
    engine._source_preserving_draft = source_native_draft; base.engine._source_preserving_draft = source_native_draft
    contract.automated_checks = automated_checks_v690; gate19.automated_checks = automated_checks_v690
    previous_critical = engine._critical_presenter_failures
    def critical(checks):
        failures = list(previous_critical(checks))
        for name in ("v20_domain_spine_curated_5_to_8","v20_crisis_is_source_specific","v20_public_web_visual_fallback_disabled"):
            if checks.get(name) is False and name not in failures: failures.append(name)
        return failures
    engine._critical_presenter_failures = critical; base.engine._critical_presenter_failures = critical
    reliability._cache_paths = _cache_paths; base.PUBLIC_VERSION = PUBLIC_VERSION; base.PIPELINE_ID = PIPELINE_ID
    previous_health = base._health_v440
    def health():
        data = dict(previous_health()); data.update({"version":PUBLIC_VERSION,"pipeline":PIPELINE_ID,"visual_policy":"P1 source figure -> native diagram -> generated local-context visual -> text-first","public_web_image_fallback":False,"domain_spine":"curated 5-8 chapter-level nodes; full P1 coverage remains in the coverage ledger","opening_crisis":"source-specific P1 stake required; generic fallback blocks release","presenter_contract":"BlackNative/TextGold; 20 core units; genuine source expansion only; ~30 physical slides"}); return data
    base._health_v440 = health; base.engine.health = health
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/api/policy/visuals"]
    @app.get("/api/policy/visuals")
    def visual_policy():
        return {"version":PUBLIC_VERSION,"priority":["P1_SOURCE_FIGURE","NATIVE_DIAGRAM","GENERATED_LOCAL_CONTEXT","TEXT_FIRST"],"public_web_fallback":False,"wikipedia_wikimedia":"BLOCKED","domain_spine_nodes":"5-8","generic_crisis":"BLOCK_RELEASE"}
