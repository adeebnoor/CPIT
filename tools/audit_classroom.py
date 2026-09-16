"""Validate the explicit ISCARB public release without regenerating lectures."""
from __future__ import annotations
import base64, hashlib, json, re, sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "curriculum/publication.json"
CURRENT_PAGES = ["iscarb.html", "student-guide.html", "course-resources.html",
                 "download.html", "fbr-submission.html", "index.html", "404.html"]
WITHDRAWN_ROUTE = re.compile(
    r"Ch(?:12|13|14|15|16|17|20)-[^\s\"'<>]*\.html|"
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

def audit(root=ROOT):
    root=Path(root); spec=publication(); errors=[]
    if spec.get("automatic_generation") is not False:
        errors.append("Automatic generation must stay disabled for reviewed ISCARB releases.")
    lecture_chapters=[x.get("chapter") for x in spec.get("lectures", [])]
    assignment_chapters=[x.get("chapter") for x in spec.get("assignments", [])]
    if lecture_chapters != [10,11] or assignment_chapters != [10,11]:
        errors.append("This release must authorize Chapters 10 and 11, each with one reviewed assignment.")
    allowed=set(spec.get("iscarb_public_files", []))
    # Immutable lectures: exact bytes and embedded figures are audited.
    for lecture in spec.get("lectures", []):
        ch=lecture.get("chapter"); path=root/lecture["path"]
        if not path.is_file(): errors.append(f"Missing approved lecture: {lecture['path']}"); continue
        if hashlib.sha256(path.read_bytes()).hexdigest()!=lecture.get("source_sha256"):
            errors.append(f"Chapter {ch} lecture does not match its authorized reviewed source.")
        source=path.read_text(encoding="utf-8"); parsed=Page(); parsed.feed(source)
        if len(parsed.ids)!=len(set(parsed.ids)): errors.append(f"Chapter {ch} lecture has duplicate static element IDs.")
        if any(not url.startswith("data:") for url in parsed.dependencies): errors.append(f"Chapter {ch} lecture has a non-embedded runtime dependency.")
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
        if ch==10 and "fbr:cpit455:ch10:prod:v4" not in a: errors.append("Chapter 10 must preserve legacy draft recovery.")
        if ch==11:
            if assignment.get("points")!=5 or "MEASURE · 1 POINT" not in a or "20,000" not in a:
                errors.append("Assignment 2 must preserve the five-point progressive rubric and measurement step.")
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
    print("PASS: Chapters 10 and 11, progressive assignments, reveal payloads, exact lecture bytes, and current links are valid.")
    return 0
if __name__=="__main__": raise SystemExit(main())
