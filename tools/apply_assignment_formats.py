"""Vary the task format for two assignments while keeping the same five criteria, points and fields.

Assignment 6 (Chapter 15) becomes a critique of a colleague's flawed recommendation; Assignment 9
(Chapter 20) becomes a design review of another team's proposal. The material to review is appended to
the scenario text, so it is exported with the student's record. The drafts' flaws come from the supplied
facts only and avoid each chapter's STRESS.

Idempotent:  python3 tools/apply_assignment_formats.py
"""
from __future__ import annotations
import html, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARK = 'data-format="review-v1"'
esc = lambda s: html.escape(s, quote=True)

FORMATS = {
 15: dict(
  kind='Critique a colleague’s recommendation',
  item=('Colleague’s draft recommendation · review it, do not copy it',
        '“Choose Option A for the whole faculty from next term. It already has every booking function we need, so configuration is enough. '
        'Support ending after two years is not a problem for a three-year pilot: we will simply renew. Option B would take too long to finish, '
        'and the team’s knowledge of it does not change that. Total cost is clearly lower for A because it is ready.”'),
  hints={
   'Classify the two reuse approaches and identify the required functions and non-functional constraints.':
    'Classify the two reuse approaches and the required functions and constraints. Then state where the colleague’s draft frames the problem wrongly: scope, lifecycle or requirement.',
   'Compare the options against four relevant reuse-planning factors. Mark each entry supported, unknown or dependent on a condition. Do not invent scores, prices or performance.':
    'Build the comparison the draft skipped: four reuse-planning factors, each marked supported, unknown or dependent on a condition. Flag each claim in the draft that the supplied facts do not support. Do not invent scores, prices or performance.',
   'Identify a lifecycle assumption that must hold and a specific change that would reverse the recommendation.':
    'Identify the lifecycle assumption the draft relies on without evidence, and a specific change that would reverse your own recommendation.',
   'Make a bounded selection or evaluation decision. Identify the owner and the evidence needed to settle one consequential unknown.':
    'Write the recommendation you would sign instead of the draft: a bounded selection or evaluation, its owner, and the evidence that would settle one consequential unknown.'}),
 20: dict(
  kind='Review another team’s design',
  item=('Proposed integration design from the transport team · review it before the pilot',
        '“The dashboard polls the three feeds every minute and shows the latest value from each as live. If a feed fails, the dashboard keeps '
        'showing its last value so the screen never looks empty. Each owner signs a one-page agreement promising 99.9% availability. '
        'Acceptance test: each API returns HTTP 200 with the agreed JSON schema.”'),
  hints={
   'Classify the SoS and identify managerial and operational independence. Name one shared service that creates value for the pilot.':
    'Classify the SoS and identify managerial and operational independence. Name one shared service that creates value for the pilot, and the control over other owners that the proposed design wrongly assumes.',
   'Propose an interface/governance record for two constituents and a staged acceptance test across them. Include ownership, version/freshness assumptions and useful behavior when one feed is absent.':
    'Review the proposed design and replace it with the interface/governance record for two constituents and the staged cross-system acceptance test you would require. Include ownership, version/freshness assumptions and useful behavior when one feed is absent, and name each weakness of the proposal your record fixes.',
   'Recommend pilot, restricted pilot or hold. Name the responsible coordination role, participating owners and evidence needed for the next stage.':
    'Approve the proposed design, approve it with conditions, or reject it for the pilot. Name the responsible coordination role, participating owners and evidence needed for the next stage.'}),
}


def patch(path: Path, n: int) -> bool:
    s = path.read_text(encoding='utf-8')
    if MARK in s:
        return False
    f = FORMATS[n]
    for old, new in f['hints'].items():
        c = s.count(old)
        if c < 2:
            raise SystemExit(f'{path.name}: hint not found twice (label + placeholder): {old[:50]!r} ({c})')
        s = s.replace(old, new)
    old = '<h2>Assessed scenario · fictional teaching case</h2>\n<div id="scenarioText">'
    if s.count(old) != 1:
        raise SystemExit(f'{path.name}: scenario heading not found')
    s = s.replace(old, f'<h2>Assessed scenario · fictional teaching case</h2>\n<p class="hint" {MARK}><b>Task format:</b> {esc(f["kind"])}. The same five criteria apply.</p>\n<div id="scenarioText">')
    a = s.index('<div id="scenarioText">'); b = s.index('</div>', a)
    s = s[:b] + f'<p class="review-item"><b>{esc(f["item"][0])}:</b> {esc(f["item"][1])}</p>' + s[b:]
    path.write_text(s, encoding='utf-8')
    return True


def main() -> int:
    done = [n for n in FORMATS if patch(ROOT / f'lectures/iscarb/Ch{n}-FBR-Student-Assignment.html', n)]
    print('Review formats applied to chapters', done or 'none (already present)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
