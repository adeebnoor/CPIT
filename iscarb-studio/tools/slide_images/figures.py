"""Extract the figure region from a source PDF page, or refuse.

The presenter pipeline hands a slide a whole rendered page. On a page that is
mostly a diagram that is nearly right; on a chapter opener it puts a book cover
on the slide, and on a text page it puts a wall of unreadable body copy behind
a lecture. Both look like "the source figure" to a grader and teach nothing.

So a page is not a figure until it proves it is one. This module finds the
drawn region on the page - embedded raster images plus vector drawings, which
is what a typeset figure actually is - and returns it only when that region is
substantial, is not the full page, and is not a decorative strip. Everything
else returns nothing, and the caller draws a diagram instead. Refusing is the
useful answer: a unit with no figure is better served by a drawn one.

    python -m tools.slide_images.figures SOURCE.pdf BLUEPRINT.json --out DIR
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

# A figure has to earn the canvas. Below this share of the page it is an inline
# icon or a rule, not something a room can read from the back.
MIN_AREA_SHARE = 0.10
# At or above this share the "figure" is the page itself, which is how a text
# page and a chapter opener both slip through as art.
MAX_AREA_SHARE = 0.78
# A long thin band is a decorative edge strip or a running rule.
MIN_ASPECT, MAX_ASPECT = 0.45, 6.0
# Rendered at this zoom a book figure's own labels stay legible on a 4K slide.
ZOOM = 3.0
# Breathing room around the crop so a caption or an arrowhead is not shaved off.
PAD = 20


def _anchor_pages(anchor: str) -> list[int]:
    text = str(anchor or "").replace("–", "-").replace("—", "-")
    found: list[int] = []
    for match in re.finditer(r"(?:slides?|pages?|pp?\.)\s*(\d+)(?:\s*-\s*(\d+))?", text, re.I):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start:
            start, end = end, start
        if end - start > 30:
            continue
        found.extend(n for n in range(start, end + 1) if n not in found)
    return found


# Every page in a print-ready PDF carries one near-page-size rectangle - the
# trim box or page background. Unioned blindly it reports a 93% "figure" on a
# page of pure prose, which is how a text page ends up on a slide as art.
PAGE_FURNITURE_SHARE = 0.60


def _clusters(rects, pymupdf, gap: float = 26.0):
    """Group rectangles that touch or nearly touch into single regions.

    A typeset figure is dozens of separate strokes and boxes; a page of prose is
    dozens of scattered rules. Clustering separates the two: the figure's parts
    merge into one large region, the page furniture stays small and apart.
    """
    groups: list = []
    for rect in sorted(rects, key=lambda r: -abs(r.get_area())):
        grown = rect + (-gap, -gap, gap, gap)
        hit = None
        for group in groups:
            if grown.intersects(group):
                hit = group
                break
        if hit is None:
            groups.append(pymupdf.Rect(rect))
        else:
            groups[groups.index(hit)] = hit | rect
    return groups


def figure_box(page, pymupdf):
    """Return the page's figure region, or None when the page has no figure."""
    page_area = abs(page.rect.get_area()) or 1.0
    candidates = []

    for info in page.get_image_info():
        rect = pymupdf.Rect(info["bbox"])
        share = abs(rect.get_area()) / page_area
        if 0.008 < share < PAGE_FURNITURE_SHARE:
            candidates.append(rect)
    # Vector figures carry no embedded image at all; their strokes are the
    # figure. Without this a box-and-arrow diagram is invisible to extraction.
    for drawing in page.get_drawings():
        rect = pymupdf.Rect(drawing["rect"])
        share = abs(rect.get_area()) / page_area
        if 0.0015 < share < PAGE_FURNITURE_SHARE:
            candidates.append(rect)

    if not candidates:
        return None

    best = None
    for group in _clusters(candidates, pymupdf):
        share = abs(group.get_area()) / page_area
        if not (MIN_AREA_SHARE <= share <= MAX_AREA_SHARE):
            continue
        if group.height <= 0 or group.width <= 0:
            continue
        if not (MIN_ASPECT <= group.width / group.height <= MAX_ASPECT):
            continue
        if best is None or abs(group.get_area()) > abs(best.get_area()):
            best = group
    return best


# A figure is many drawn parts carrying few words each: a diagram's boxes and
# arrows, a table's cells. Prose in a ruled callout is the inverse - a couple of
# rectangles around hundreds of words - and that is precisely what keeps landing
# on slides as "the source figure". Measured on the Sommerville chapter these
# two numbers separate every figure from every text block on the page; they are
# a heuristic tuned on one book, so widen them only against fresh examples.
MIN_PARTS = 12
MAX_WORDS_PER_PART = 12.0


def _is_figure_like(page, box, pymupdf) -> bool:
    parts = [r for r in (pymupdf.Rect(d["rect"]) for d in page.get_drawings())
             if r.intersects(box)]
    parts += [r for r in (pymupdf.Rect(i["bbox"]) for i in page.get_image_info())
              if r.intersects(box)]
    if len(parts) < MIN_PARTS:
        return False
    words = sum(1 for w in page.get_text("words") if pymupdf.Rect(w[:4]).intersects(box))
    return words / len(parts) <= MAX_WORDS_PER_PART


def extract(pdf: Path, pages: list[int], out_dir: Path, tag: str) -> tuple[str, int]:
    import pymupdf

    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf))
    try:
        for number in pages:
            if not (1 <= number <= doc.page_count):
                continue
            page = doc[number - 1]
            box = figure_box(page, pymupdf)
            if box is None or not _is_figure_like(page, box, pymupdf):
                continue
            clip = (box + (-PAD, -PAD, PAD, PAD)) & page.rect
            pix = page.get_pixmap(matrix=pymupdf.Matrix(ZOOM, ZOOM), clip=clip, alpha=False)
            target = out_dir / f"{tag}_p{number:03d}.png"
            pix.save(str(target))
            return str(target), number
    finally:
        doc.close()
    return "", 0


def build_map(pdf: Path, blueprint: Path, out_dir: Path) -> dict[str, str]:
    """Assign each usable figure to the unit that points at it most narrowly.

    Neighbouring units overlap in anchored pages, so first-come assignment gave
    a figure to whichever unit happened to be earlier - a chapter-framing unit
    with a twelve-page anchor could take the diagram belonging to the unit that
    actually teaches it. Claiming by narrowest anchor puts each figure on the
    slide whose source span is most specifically about it.
    """
    import pymupdf

    data = json.loads(Path(blueprint).read_text(encoding="utf-8"))
    claims: dict[int, list[tuple[int, int]]] = {}   # page -> [(span, unit)]
    for unit in data.get("units") or []:
        number = int(str(unit.get("number") or 0) or 0)
        pages = _anchor_pages(unit.get("source_anchor") or "")
        for page_number in pages:
            claims.setdefault(page_number, []).append((len(pages), number))

    doc = pymupdf.open(str(pdf))
    usable: list[tuple[int, int, int]] = []          # (span, unit, page)
    try:
        for page_number, bidders in claims.items():
            if not (1 <= page_number <= doc.page_count):
                continue
            page = doc[page_number - 1]
            box = figure_box(page, pymupdf)
            if box is None or not _is_figure_like(page, box, pymupdf):
                continue
            span, unit_number = min(bidders)
            usable.append((span, unit_number, page_number))
    finally:
        doc.close()

    figures: dict[str, str] = {}
    taken: set[int] = set()
    # Guideline 2 forbids reusing one asset across units, so a unit keeps only
    # its best page and every page is spent once.
    for _span, unit_number, page_number in sorted(usable):
        if unit_number in taken:
            continue
        path, _page = extract(pdf, [page_number], out_dir, f"u{unit_number:02d}")
        if path:
            figures[str(unit_number)] = path
            taken.add(unit_number)
    return figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract P1 figure regions")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--out", type=Path, default=Path("figures"))
    parser.add_argument("--map", dest="map_path", type=Path, default=None)
    args = parser.parse_args(argv)

    figures = build_map(args.pdf, args.blueprint, args.out)
    target = args.map_path or (args.out / "figures.json")
    target.write_text(json.dumps(figures, indent=1), encoding="utf-8")
    print(f"{len(figures)} figure(s) -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
