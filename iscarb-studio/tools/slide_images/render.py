"""Render ISCARB blueprint JSON to shareable slide images.

    python -m tools.slide_images.render BLUEPRINT.json --out DIR [--format png|jpg]
                                        [--scale 2] [--units 1,7,19]

Why a headless browser and not an image model: the words on these slides are
the lecture's primary source. A diffusion model asked to draw the slide invents
letterforms; a browser lays out the exact string the JSON holds. The template
owns the identity, the JSON owns the words, and the screenshot is a faithful
capture of both -- so the same input always produces the same image.

Scale is a device pixel ratio, not a resize: --scale 2 renders the 1920x1080
stage at 3840x2160 with real subpixel type, which is what "high resolution"
has to mean for text.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .identity import GEOMETRY
from .verify import check_unit, visible_text
from .template import FIT_SCRIPT, build_html


def _load_units(blueprint: dict, wanted: set[int] | None) -> list[dict]:
    units = list(blueprint.get("units") or [])
    if wanted:
        units = [u for u in units if int(str(u.get("number") or 0) or 0) in wanted]
    return units


def render(blueprint_path: Path, out_dir: Path, *, fmt: str = "png",
           scale: int = 2, wanted: set[int] | None = None,
           quality: int = 92, theme_name: str = "dark",
           figures: dict[int, str] | None = None,
           strict: bool = True) -> list[Path]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:  # pragma: no cover - environment guard
        raise SystemExit(
            "playwright is required: pip install playwright && playwright install chromium"
        )

    blueprint = json.loads(Path(blueprint_path).read_text(encoding="utf-8"))
    units = _load_units(blueprint, wanted)
    if not units:
        raise SystemExit("no units selected")
    lecture_title = str(blueprint.get("lecture_title") or "")
    total = len(blueprint.get("units") or units)

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    shrunk: list[str] = []
    layouts: dict[str, int] = {}
    violations: list[tuple[int, list[str]]] = []

    # CI images and sandboxes often ship a Chromium that Playwright's own
    # version pin does not match. Honour an explicit binary before failing with
    # "run playwright install", which is not something a build container can do.
    launch: dict = {"args": ["--font-render-hinting=none"]}
    binary = os.getenv("ISCARB_CHROMIUM", "").strip()
    if binary:
        launch["executable_path"] = binary

    with sync_playwright() as pw:
        browser = pw.chromium.launch(**launch)
        page = browser.new_page(
            viewport={"width": GEOMETRY.width, "height": GEOMETRY.height},
            device_scale_factor=scale,
        )
        for unit in units:
            number = int(str(unit.get("number") or 0) or 0)
            markup, _rtl, layout = build_html(
                unit, lecture_title=lecture_title, total=total,
                theme_name=theme_name, figure=(figures or {}).get(number, ""),
            )
            layouts[layout] = layouts.get(layout, 0) + 1
            # The grammar is checked here, against the markup about to be
            # photographed, so a deck cannot be exported while quietly breaking
            # a rule its Blueprint satisfies. That gap is what put a blank
            # opening slide and a figure with no obligations into a "passing"
            # deck.
            chrome = " ".join([str(unit.get("engineering_question") or ""),
                               str(unit.get("student_action") or "")])
            broken = check_unit(number, visible_text(markup), unit, layout, chrome)
            if broken:
                violations.append((number, broken))
            page.set_content(markup, wait_until="load")
            # Fonts must be resident before measuring, or shrink-to-fit measures
            # a fallback face and picks the wrong size for the real one.
            page.evaluate("document.fonts.ready")
            fit = page.evaluate(FIT_SCRIPT)
            if fit.get("overflow"):
                shrunk.append(f"unit {number:02d} still overflows at minimum size")
            elif fit.get("bodyPx") and fit["bodyPx"] < 24:
                shrunk.append(f"unit {number:02d} shrank to {fit['bodyPx']}px")

            suffix = "jpg" if fmt == "jpg" else "png"
            target = out_dir / f"unit_{number:02d}.{suffix}"
            if suffix == "jpg":
                page.screenshot(path=str(target), type="jpeg", quality=quality)
            else:
                page.screenshot(path=str(target), type="png")
            written.append(target)
        browser.close()

    print("  layouts: " + ", ".join(f"{k}={v}" for k, v in sorted(layouts.items())),
          file=sys.stderr)
    if violations:
        print(f"  GRAMMAR: {len(violations)} unit(s) break the 20-unit contract",
              file=sys.stderr)
        for number, broken in violations:
            print(f"    unit {number:02d}: {'; '.join(broken)}", file=sys.stderr)
        if strict:
            raise SystemExit(
                f"refusing to ship: {len(violations)} unit(s) break the contract"
            )
    else:
        print("  GRAMMAR: 20/20 units satisfy the contract on the rendered slide",
              file=sys.stderr)
    for note in shrunk:
        print(f"  note: {note}", file=sys.stderr)
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ISCARB JSON -> slide images")
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--out", type=Path, default=Path("slide_images"))
    parser.add_argument("--format", dest="fmt", choices=("png", "jpg"), default="png")
    parser.add_argument("--scale", type=int, default=2, help="device pixel ratio")
    parser.add_argument("--quality", type=int, default=92, help="jpg quality")
    parser.add_argument("--units", default="", help="comma-separated unit numbers")
    parser.add_argument("--theme", choices=("light", "dark"), default="dark")
    parser.add_argument("--no-strict", dest="strict", action="store_false",
                        help="report contract breaks instead of refusing to ship")
    parser.add_argument("--figures", type=Path, default=None,
                        help='JSON map {"7": "/path/figure.png"} of P1 figures')
    args = parser.parse_args(argv)

    wanted = {int(x) for x in args.units.split(",") if x.strip().isdigit()} or None
    figures = {}
    if args.figures and args.figures.is_file():
        figures = {int(k): v for k, v in
                   json.loads(args.figures.read_text(encoding="utf-8")).items()}
    files = render(args.blueprint, args.out, fmt=args.fmt, scale=args.scale,
                   wanted=wanted, quality=args.quality, theme_name=args.theme,
                   figures=figures, strict=args.strict)
    print(f"{len(files)} image(s) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
