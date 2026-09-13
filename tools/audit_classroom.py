"""Validate the approved public release without generating lessons.

The uploaded Chapter 10 is the authoring source. Historical curriculum data must
never silently regenerate it or re-publish withdrawn lessons and assignments.
"""
from __future__ import annotations
import base64
import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "curriculum/publication.json"
CURRENT_PAGES = ["iscarb.html", "student-guide.html", "course-resources.html",
                 "download.html", "fbr-submission.html", "index.html", "404.html"]
WITHDRAWN_ROUTE = re.compile(
    r"Ch(?:11|12|13|14|15|16|17|20)-[^\s\"'<>]*\.html|"
    r"Ch10-(?:FBR-Student-Assignment|Dependable-Systems-(?:Faculty(?:-Rich)?|Final100))\.html",
    re.I,
)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.dependencies = []
        self.standalone = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.standalone = attrs.get("data-iscarb-standalone") == "1"
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag in ("script", "img", "iframe", "audio", "video", "source") and attrs.get("src"):
            self.dependencies.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in ("stylesheet", "preload", "modulepreload"):
            self.dependencies.append(attrs.get("href", ""))

def publication():
    return json.loads(CATALOG.read_text(encoding="utf-8"))

def audit(root=ROOT):
    """Return release errors for either the source tree or its staged copy."""
    root = Path(root)
    spec = publication()
    errors = []
    if spec.get("automatic_generation") is not False:
        errors.append("Automatic generation must stay disabled during the instructor reset.")
    if spec.get("assignments") != [] or [x.get("chapter") for x in spec.get("lectures", [])] != [10]:
        return errors + ["This release authorizes only Chapter 10 and no assignments."]
    lecture = spec["lectures"][0]
    path = root / lecture["path"]
    if not path.is_file():
        return errors + [f"Missing approved lecture: {lecture['path']}"]
    source = path.read_text(encoding="utf-8")
    parsed = Page()
    parsed.feed(source)
    if not parsed.standalone:
        errors.append("Chapter 10 must retain its standalone marker and own design.")
    if len(parsed.ids) != len(set(parsed.ids)):
        errors.append("Chapter 10 has duplicate static element IDs.")
    if any(not url.startswith("data:") for url in parsed.dependencies):
        errors.append("Chapter 10 has a non-embedded runtime dependency.")
    if re.search(r"(?:kaspersky-labs|gc\.kis\.|file:///|C:/Users/)", source, re.I):
        errors.append("Chapter 10 contains an injected browser resource or local file path.")
    if re.search(r"@import\b|url\(\s*['\"]?(?:https?:)?//", source, re.I):
        errors.append("Chapter 10 CSS depends on a remote resource.")
    try:
        images = re.findall(r"data:image/(?:png|jpe?g|webp);base64,([A-Za-z0-9+/=]+)", source)
        hashes = [hashlib.sha256(base64.b64decode(img, validate=True)).hexdigest() for img in images]
        if sorted(hashes) != sorted(lecture["embedded_image_sha256"]):
            errors.append("The eight images from the approved attachment were changed or removed.")
    except (ValueError, TypeError) as exc:
        errors.append(f"Invalid embedded image: {exc}")
    directory = root / "lectures/iscarb"
    allowed = set(spec["iscarb_public_files"])
    for old in directory.glob("*.html"):
        if old.relative_to(root).as_posix() not in allowed:
            errors.append(f"Withdrawn lecture/assignment remains: {old.relative_to(root)}")
    for name in ("reveal", "split"):
        if any(p.is_file() for p in (directory / name).rglob("*")):
            errors.append(f"Withdrawn assignment or lecture payload remains: lectures/iscarb/{name}")
    for name in allowed:
        if not (root / name).is_file():
            errors.append(f"Missing approved public file: {name}")
    pages = CURRENT_PAGES + [name for name in allowed if name.endswith(".html")]
    for name in pages:
        page = root / name
        if not page.is_file():
            errors.append(f"Missing current route: {name}")
            continue
        text = page.read_text(encoding="utf-8")
        if WITHDRAWN_ROUTE.search(text):
            errors.append(f"{name}: active reference to withdrawn lecture or assignment.")
        links = Page()
        links.feed(text)
        for href in links.links:
            target = urlsplit(href)
            if target.scheme or target.netloc or not target.path:
                continue
            part = unquote(target.path)
            destination = root / part[len("/CPIT/"):] if part.startswith("/CPIT/") else page.parent / part
            if part.startswith("/") and not part.startswith("/CPIT/"):
                continue
            if not destination.exists():
                errors.append(f"{name}: missing local link {href}")
    return errors

def main():
    errors = audit(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("PASS: approved standalone Chapter 10, eight preserved images, current links, no withdrawn lessons or assignments.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
