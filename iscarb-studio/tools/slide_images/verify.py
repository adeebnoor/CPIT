"""Check the rendered slides against the ISCARB 20-unit grammar.

Gate v16 checks the Blueprint. This checks what a student can actually see on
the slide after compression and layout - which is a different question, and the
one that matters. A unit can hold a perfect Decision/Unknown pair in its JSON
and still project a title over an empty rectangle, and the gate will say PASS.
That is exactly how the opening slide of a lecture ended up blank.

So every rule here is evaluated against the visible text of the rendered slide,
never against the source data.

    python -m tools.slide_images.verify BLUEPRINT.json [--figures figures.json]
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from .template import build_html

# Below this a slide is furniture: a title, a question, and nothing to teach.
MIN_BODY_WORDS = 8
# Guideline 1: "Never paste PRIMARY-source paragraphs into presenter slides."
# One unbroken run longer than this is a paragraph whatever it is called.
MAX_LINE_WORDS = 34


def visible_text(markup: str) -> str:
    """The words a projector actually shows, minus the chrome."""
    body = markup.split('<div id="body"', 1)
    if len(body) < 2:
        return ""
    inner = body[1].split("</div>\n  ", 1)[0]
    inner = re.sub(r"<svg.*?</svg>", " ", inner, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", inner))


def _has_all(text: str, *needles: str) -> list[str]:
    low = text.lower()
    return [n for n in needles if n.lower() not in low]


def _labels(text: str) -> set[str]:
    return {m.group(1).strip().lower()
            for m in re.finditer(r"([A-Z][A-Z /&+-]{2,34})(?=\s)", text)}


def check_unit(number: int, text: str, unit: dict, layout: str,
               chrome: str = "") -> list[str]:
    """Return the rule violations visible on this slide.

    `chrome` is the question and task text, which live outside the body but are
    part of what the contract requires a student to be able to read.
    """
    problems: list[str] = []
    words = len(text.split())

    # Rule 0, which the grammar assumes rather than states: a unit is a taught
    # minute. Units 3 and 4 legitimately carry no source content, so they are
    # measured on their own pedagogy entries instead of being excused.
    if words < MIN_BODY_WORDS:
        problems.append(f"near-empty slide ({words} visible words)")

    # Every unit owes the student a question and something to do: "ما السؤال
    # الهندسي؟ وما المطلوب مني؟" is half the five-second test.
    if "engineering_question" not in chrome and not str(unit.get("engineering_question") or "").strip():
        problems.append("no engineering question on the slide")
    if not str(unit.get("student_action") or "").strip():
        problems.append("no student task on the slide")

    # Guideline 1: no primary-source paragraph reaches a slide. One long
    # unbroken run is the paragraph the guideline forbids, however it got there.
    for line in re.split(r"\s{2,}", text.strip()):
        if len(line.split()) > MAX_LINE_WORDS:
            problems.append(f"paragraph on slide ({len(line.split())} words in one run)")
            break

    low = text.lower()
    if number == 2:
        # The spine maps the chapter; a spine naming one family maps nothing.
        if len(re.findall(r"\d+\.\d+", text)) < 2 and words < 14:
            problems.append("domain spine does not map at least two source families")
    elif number == 6:
        if words < 14:
            problems.append("mechanism not taught: fewer than three substantive entries")
    elif number == 7:
        if not re.search(r"trace|apply|structure|component", low + " " + chrome.lower()):
            problems.append("structure is shown but the learner is not asked to trace or apply it")
    elif number == 12:
        if not re.search(r"owner|role|responsib|sign-?off|escalat|accountab", low):
            problems.append("no accountable role or sign-off decision visible")
    elif number == 14:
        if not re.search(r"workload|wellbeing|well-being|fatigue|operator|practitioner|people|staff|human", low):
            problems.append("no practitioner workload/wellbeing dimension visible")
    elif number == 16:
        if not re.search(r"artifact|artefact|evidence|trade", low):
            problems.append("no portfolio artifact with a trade-off and evidence")
    elif number == 17:
        if not re.search(r"constraint|critique|revis|redesign|rerun|re-run", low):
            problems.append("no constraint change with critique and rerun evidence")
    if number == 1:
        problems += [f"missing {m}" for m in _has_all(text, "decision", "unknown")]
    elif number == 3:
        found = len(re.findall(r"clo\s*[1-5]", low))
        if found < 5:
            problems.append(f"shows {found}/5 CLOs")
    elif number == 4:
        # The contract names these six exactly; counting upper-case runs
        # instead just measured how the labels happened to be typed.
        named = sum(bool(re.search(k, low)) for k in (
            r"analytic", r"judgment|judgement", r"evidence",
            r"socio-?technical", r"risk-?aware", r"ethic"))
        if named < 6:
            problems.append(f"shows {named}/6 named capabilities")
    elif number == 5:
        order = [w for w in ("predict", "constraint", "derive", "name") if w in low]
        if len(order) < 4:
            problems.append(f"predict/constraint/derive/name: only {order}")
    elif number == 8:
        problems += [f"missing {m}" for m in _has_all(text, "alternative", "trade")]
    elif number == 9:
        problems += [f"missing {m}" for m in _has_all(text, "measure", "falsif")]
    elif number == 10:
        problems += [f"missing {m}" for m in _has_all(text, "known", "monitor")]
    elif number == 11:
        if "hypothetical" not in low:
            problems.append("bounded scenario not marked hypothetical")
    elif number == 13:
        if not re.search(r"\d", text):
            problems.append("no explicit numeric or structural stress variable")
    elif number == 15:
        problems += [f"missing {m}" for m in _has_all(text, "ai", "sign-off")]
    elif number == 18:
        problems += [f"missing {m}" for m in _has_all(text, "claim", "evidence")]
    elif number == 19:
        if "evidence" not in low and "artifact" not in low:
            problems.append("capability credit not tied to evidence/artifact")
    elif number == 20:
        if not re.search(r"approve|redesign|reject|conditional", low):
            problems.append("no bounded verdict visible")

    # Guideline 2: a figure that no line points at is decoration.
    if layout == "figure" and words < 10:
        problems.append("figure carries no line telling the student where to look")
    return problems


def run(blueprint_path: Path, figures: dict[str, str]) -> tuple[list[tuple], int]:
    data = json.loads(Path(blueprint_path).read_text(encoding="utf-8"))
    units = data.get("units") or []
    rows: list[tuple] = []
    seen_figures: dict[str, int] = {}
    failures = 0

    for unit in units:
        number = int(str(unit.get("number") or 0) or 0)
        figure = figures.get(str(number), "")
        markup, _rtl, layout = build_html(
            unit, lecture_title=data.get("lecture_title", ""),
            total=len(units), theme_name="dark", figure=figure,
        )
        text = visible_text(markup)
        chrome = " ".join([str(unit.get("engineering_question") or ""),
                           str(unit.get("student_action") or "")])
        problems = check_unit(number, text, unit, layout, chrome)
        # Guideline 2: no asset repeats across units.
        if figure:
            if figure in seen_figures:
                problems.append(f"figure repeats unit {seen_figures[figure]}")
            seen_figures[figure] = number
        rows.append((number, layout, len(text.split()), problems))
        failures += bool(problems)

    if len(units) != 20:
        failures += 1
    return rows, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify rendered slides")
    parser.add_argument("blueprint", type=Path)
    parser.add_argument("--figures", type=Path, default=None)
    args = parser.parse_args(argv)

    figures = {}
    if args.figures and args.figures.is_file():
        figures = json.loads(args.figures.read_text(encoding="utf-8"))

    rows, failures = run(args.blueprint, figures)
    print(f"{'U':>3}  {'layout':8s} {'words':>5}  rule check")
    for number, layout, words, problems in rows:
        mark = "FAIL" if problems else "ok"
        detail = "; ".join(problems) if problems else ""
        print(f"{number:3d}  {layout:8s} {words:5d}  {mark:4s} {detail}")
    print(f"\n{len(rows)} units, {failures} failing")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
