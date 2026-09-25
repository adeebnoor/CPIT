"""Validate the explicit ISCARB public release without regenerating lectures."""
from __future__ import annotations
import base64, hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "curriculum/publication.json"
CURRENT_PAGES = ["iscarb.html", "student-guide.html", "course-resources.html", "instructor-guide.html",
                 "download.html", "fbr-submission.html", "index.html", "404.html"]
WITHDRAWN_ROUTE = re.compile(
    r"Ch10-Dependable-Systems-(?:Faculty(?:-Rich)?|Final100)\.html",
    re.I,
)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.links=[]; self.dependencies=[]; self.standalone=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag=="html": self.standalone=attrs.get("data-iscarb-standalone")=="1"
        if "id" in attrs: self.ids.append(attrs["id"])
        if tag=="a": self.links.append(attrs.get("href", ""))
        if tag in ("script","img","iframe","audio","video","source") and attrs.get("src"):
            self.dependencies.append(attrs["src"])
        if tag=="link" and attrs.get("rel") in ("stylesheet","preload","modulepreload"):
            self.dependencies.append(attrs.get("href", ""))

def publication(): return json.loads(CATALOG.read_text(encoding="utf-8"))

TEXT_EXT={'.html','.htm','.js','.css','.json','.md','.txt','.py','.yml','.yaml','.cjs','.mjs'}
def canonical_sha(path):
    p=Path(path); b=p.read_bytes()
    if p.suffix.lower() in TEXT_EXT: b=b.replace(b'\r\n',b'\n')
    return hashlib.sha256(b).hexdigest()

def audit(root=ROOT):
    root=Path(root); spec=publication(); errors=[]
    if spec.get("automatic_generation") is not False:
        errors.append("Automatic generation must stay disabled for reviewed ISCARB releases.")
    lecture_chapters=[x.get("chapter") for x in spec.get("lectures", [])]
    assignment_chapters=[x.get("chapter") for x in spec.get("assignments", [])]
    expected = [10,11,12,13,14,15,16,17,20]
    if lecture_chapters != expected or assignment_chapters != expected:
        errors.append("The authorized nine-chapter release requires one lecture and assignment per supplied chapter.")
    allowed=set(spec.get("iscarb_public_files", []))
    # Shared assets are explicitly allowlisted and hashed. Externalization does not
    # remove the immutable-byte or source-figure fidelity checks.
    asset_hashes=spec.get("delivery_asset_sha256", {})
    for name, digest in asset_hashes.items():
        ap=(root/name).resolve()
        if not ap.is_relative_to(root.resolve()) or name not in allowed:
            errors.append(f"Unapproved delivery asset: {name}")
        elif not ap.is_file() or canonical_sha(ap)!=digest:
            errors.append(f"Delivery asset is missing or changed: {name}")
    # Immutable lectures: exact bytes, local dependencies and original figures.

    for lecture in spec.get("lectures", []):
        ch=lecture.get("chapter"); path=root/lecture["path"]
        if not path.is_file(): errors.append(f"Missing approved lecture: {lecture['path']}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=lecture.get("source_sha256"):
            errors.append(f"Chapter {ch} lecture does not match its authorized reviewed source.")
        source=path.read_text(encoding="utf-8"); parsed=Page(); parsed.feed(source)
        if len(parsed.ids)!=len(set(parsed.ids)): errors.append(f"Chapter {ch} lecture has duplicate static element IDs.")
        for url in parsed.dependencies:
            if url.startswith("data:"): continue
            u=urlsplit(url)
            ap=(path.parent/unquote(u.path)).resolve()
            if u.scheme or u.netloc or not ap.is_relative_to(root.resolve()):
                errors.append(f"Chapter {ch} unapproved runtime dependency: {url}"); continue
            name=ap.relative_to(root.resolve()).as_posix()
            if name not in asset_hashes or name not in allowed:
                errors.append(f"Chapter {ch} runtime dependency lacks an approved hash: {url}")
        try:
            match=re.search(r'<script id="lecture-data" type="application/json">([\s\S]*?)</script>', source)
            if not match: raise ValueError("Missing explicit lecture-data")
            data=json.loads(match.group(1)); keys=[v['id'] for v in data['slides']]
            if len(keys)!=20 or len(set(keys))!=20 or keys!=lecture['core_keys']:
                errors.append(f"Chapter {ch} must expose exactly 20 unique reviewed classroom slides.")
            if len(data['objectives'])!=5 or len(data['quiz'])!=5:
                errors.append(f"Chapter {ch} needs five objectives and five formative items.")
            if [v['no'] for v in data['stations']]!=[1,2,3] or any(v['at'] not in keys for v in data['stations']):
                errors.append(f"Chapter {ch} must have three reachable classroom stations.")
            if [v['no'] for v in data['rules']]!=list(range(1,21)):
                errors.append(f"Chapter {ch} canonical rule numbering is incomplete.")
            tools={'UNITS','READING','COVERAGE','RULES','TOOLS','CARD','HSTACK','PREDICT','BRIDGE','MONITOR','LOCAL','PRACTICE','WELLBEING','AI','EVIDENCE','RUBRIC','READINESS','PORTFOLIO','QUIZ','CALCULATOR','HELP','NOTES'}
            if any(k not in keys and k not in tools for v in data['rules'] for k in v['targets']):
                errors.append(f"Chapter {ch} contains an unreachable canonical-rule target.")
            if any(k not in keys for g in data['groups'] for k in g['units']):
                errors.append(f"Chapter {ch} source coverage points to a missing classroom unit.")
            study=(root/lecture['study_path']).read_text(encoding='utf-8')
            source_ids={int(n) for n in re.findall(r'id="source-slide-(\d+)"',study)}
            if source_ids!=set(range(1,lecture['source_slide_count']+1)):
                errors.append(f"Chapter {ch} original source ledger has a gap.")
            for v in data['slides']+[{'figure':data['brand']}]:
                if not v.get('figure'): continue
                ip=(path.parent/v['figure']).resolve()
                if not ip.is_relative_to(root.resolve()) or ip.relative_to(root.resolve()).as_posix() not in asset_hashes:
                    errors.append(f"Chapter {ch} source image not integrity checked: {v['figure']}")
            previous=root/lecture['previous_lecture_path']
            if canonical_sha(previous)!=lecture['previous_lecture_sha256']:
                errors.append(f"Chapter {ch} previous lecture draft-recovery page changed.")
            images=re.findall(r"data:image/(?:png|jpe?g|webp);base64,([A-Za-z0-9+/=]+)",previous.read_text(encoding='utf-8'))
            preserved=[hashlib.sha256(base64.b64decode(v,validate=True)).hexdigest() for v in images]
            if sorted(preserved)!=sorted(lecture['preserved_embedded_image_sha256']):
                errors.append(f"Chapter {ch} original embedded source images were removed or modified.")
        except (KeyError,ValueError,OSError,TypeError) as exc:
            errors.append(f"Chapter {ch} reviewed data or source integrity error: {exc}")
        if re.search(r"(?:kaspersky-labs|gc\.kis\.|file:///|C:/Users/)",source,re.I): errors.append(f"Chapter {ch} contains an injected browser resource or local path.")
        if re.search(r"@import\b|url\(\s*['\"]?(?:https?:)?//",source,re.I): errors.append(f"Chapter {ch} CSS depends on a remote resource.")
        try:
            images=re.findall(r"data:image/(?:png|jpe?g|webp);base64,([A-Za-z0-9+/=]+)",source)
            hashes=[hashlib.sha256(base64.b64decode(img,validate=True)).hexdigest() for img in images]
            if sorted(hashes)!=sorted(lecture.get("embedded_image_sha256",[])):
                errors.append(f"Embedded images changed or were removed from Chapter {ch}.")
        except (ValueError,TypeError) as exc: errors.append(f"Chapter {ch} invalid embedded image: {exc}")
    # Explicit directory allowlist prevents stale/withdrawn lessons from shipping.
    directory=root/"lectures/iscarb"
    for old in directory.glob("*.html"):
        if old.relative_to(root).as_posix() not in allowed: errors.append(f"Withdrawn lecture/assignment remains: {old.relative_to(root)}")
    for name in ("reveal","split"):
        if not (directory/name).exists(): continue
        for payload in (directory/name).rglob("*"):
            if payload.is_file() and payload.relative_to(root).as_posix() not in allowed:
                errors.append(f"Withdrawn assignment or lecture payload remains: {payload.relative_to(root)}")
    for name in allowed:
        if not (root/name).is_file(): errors.append(f"Missing approved public file: {name}")
    # Assignment integrity and commit-then-reveal separation.
    for assignment in spec.get("assignments", []):
        ch=assignment.get("chapter"); ap=root/assignment["path"]; sp=root/assignment["stress_path"]
        if not ap.is_file(): errors.append(f"Missing Chapter {ch} assignment."); continue
        a=ap.read_text(encoding="utf-8"); page=Page(); page.feed(a)
        if not page.standalone: errors.append(f"Chapter {ch} assignment must retain standalone styling.")
        if len(page.ids)!=len(set(page.ids)): errors.append(f"Chapter {ch} assignment has duplicate static IDs.")
        for token in (assignment.get("storage_key"),assignment.get("access_key"),assignment.get("stress_path").split("lectures/iscarb/")[-1],assignment.get("version")):
            if token and token not in a: errors.append(f"Chapter {ch} assignment is missing required identity token: {token}")
        previous=root/assignment.get('previous_path',assignment['path'])
        if not previous.is_file(): errors.append(f"Chapter {ch} must preserve the previous assignment edition for draft recovery.")
        if assignment.get("edition")=="ai-v3":
            expected_points=4 if ch==10 else 5
            if assignment.get("points")!=expected_points: errors.append(f"Chapter {ch} AI-only assignment has the wrong point total.")
            for marker in ('data-assessment-edition="ai-v3"','AI-ONLY','Download Blackboard JSON','22964248'):
                if marker.lower() not in a.lower(): errors.append(f"Chapter {ch} AI-only assignment is missing required marker: {marker}")
        if sp.is_file():
            try:
                stress=json.loads(sp.read_text(encoding="utf-8"))
                if str(stress.get("chapter"))!=str(ch) or stress.get("version")!=assignment.get("version") or not stress.get("text"):
                    errors.append(f"Invalid Chapter {ch} STRESS payload.")
                if stress.get("text") and stress["text"] in a: errors.append(f"Chapter {ch} STRESS must not be included in the initial assignment HTML.")
            except ValueError: errors.append(f"Invalid Chapter {ch} STRESS JSON.")
    # Current page references and local links.
    pages=CURRENT_PAGES+[name for name in allowed if name.endswith(".html")]
    for name in pages:
        page=root/name
        if not page.is_file(): errors.append(f"Missing current route: {name}"); continue
        text=page.read_text(encoding="utf-8")
        if WITHDRAWN_ROUTE.search(text): errors.append(f"{name}: active reference to withdrawn lecture or assignment.")
        links=Page(); links.feed(text)
        for href in links.links:
            target=urlsplit(href)
            if target.scheme or target.netloc or not target.path: continue
            part=unquote(target.path)
            destination=root/part[len("/CPIT/"):] if part.startswith("/CPIT/") else page.parent/part
            if part.startswith("/") and not part.startswith("/CPIT/"): continue
            if not destination.exists(): errors.append(f"{name}: missing local link {href}")
    return errors

def main():
    errors=audit(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
    if errors: print("\n".join(errors),file=sys.stderr); return 1
    print("PASS: Nine chapters, progressive assignments, reveal payloads, exact lecture/source/asset bytes, 20/5/3 classroom structure, and current links are valid.")
    return 0
if __name__=="__main__": raise SystemExit(main())
