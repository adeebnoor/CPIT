from __future__ import annotations

import re
import sys
from pathlib import Path


def sanitize_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(
        r'<!-- saved from url=\([^)]*\)file:///C:/Users/USER/Downloads/[^>]*-->',
        '<!-- Archived CPIT-455 interactive lecture -->',
        text,
    )
    text = re.sub(
        r'href="file:///C:/Users/USER/Downloads/[^"#]+(#[^"]+)"',
        lambda m: f'href="{m.group(1)}"',
        text,
    )
    path.write_text(text, encoding="utf-8")


def validate_page(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    if "file:///" in text or "C:/Users/" in text:
        errors.append(f"{path}: local Windows file URL remains")
    ids = set(re.findall(r'\bid=["\']([^"\']+)["\']', text))
    for target in re.findall(r'href=["\']#([^"\']+)["\']', text):
        if target and target not in ids:
            errors.append(f"{path}: missing fragment target #{target}")
    return errors


def main() -> int:
    site = Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    slides = site / "slides"
    if not site.exists() or not slides.exists():
        raise SystemExit(f"Expected staged site with slides at {slides}")
    for page in sorted(slides.glob("*.html")):
        sanitize_page(page)
    errors: list[str] = []
    for page in sorted(site.rglob("*.html")):
        errors.extend(validate_page(page))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Static-site hygiene PASS: {len(list(site.rglob('*.html')))} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
