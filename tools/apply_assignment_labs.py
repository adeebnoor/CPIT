"""Add the small executable lab to Assignments 3–5 (Chapters 12–14), the same way Assignments 7–8 carry it.

Each lab is a deterministic teaching model in curriculum/learning-path/labs.js with a baseline and a
corrected version. The student predicts, writes JSON test cases, runs both models, and the execution
record is frozen with Part A and exported. The lab sits inside the existing artifact and rubric (no new
points). Models avoid each chapter's STRESS facts beyond what the scenario already states.

Idempotent:  python3 tools/apply_assignment_labs.py
"""
from __future__ import annotations
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / 'curriculum/publication.json'
LABS = (ROOT / 'curriculum/learning-path/labs.js').read_text(encoding='utf-8')
esc = lambda s: html.escape(str(s), quote=True)

SPEC = {
 12: dict(title='Fail-safe decision tests',
  instructions='Write at least three cases. Each case is a JSON object with name, frames (an ordered list of camera frames: empty, occupied or missing) and expectedAction (close or hold). The controller has been asked to close after the last frame. Include a case ending with an occupied frame, one ending with an empty frame, and at least one case outside the recorded daylight conditions, using a missing frame. Predict what each model does before running it.',
  code='// The controller has been asked to close the barrier after the listed frames.\n// It decides from the latest frame only.\n// Baseline: closes unless the latest frame shows the zone occupied.\n// Corrected (fail-safe): closes only when the latest frame positively shows an empty zone.\n// "missing" means no usable image: low light, rain, a covered lens or a dropped frame.\n// No timing, power supply, mechanics or real sensor data is modelled.',
  shape='[{"name":"my case","frames":["YOUR","FRAMES"],"expectedAction":"close or hold"}]'),
 13: dict(title='Server-side access tests',
  instructions='Write at least three cases. Each case is a JSON object with name, actor (student:ID or staff:GROUP), object (project:OWNER@GROUP), path (ui or api) and expected (allow or deny). A student may access only their own project; staff may access only projects in their assigned group. Include an allowed and a forbidden request on the api path. Predict each decision before running.',
  code='// One request is decided at a time.\n// Rule: a student may access a project they own; staff may access projects in their assigned group.\n// Baseline: the rule is applied only where the interface lists links (path "ui");\n//           the API serves any project identifier it receives.\n// Corrected: the server checks the actor against the object on every path.\n// No sessions, logs, network or real accounts are modelled.',
  shape='[{"name":"my case","actor":"student:YOUR_ID","object":"project:OWNER@GROUP","path":"api","expected":"allow or deny"}]'),
 15: dict(title='Evidence-only fit check',
  instructions='Write at least four cases. Each case is a JSON object with name, option (A or B), requirement (booking, recurring, export-api, support-3-years or peak-load) and expected (met, gap or unknown). Check both options and include at least one requirement the supplied facts do not settle. Predict what each model reports before running. Use the result to test the claims in the colleague’s draft.',
  code='// The facts are exactly those in the scenario, nothing more.\n// Baseline ("brochure reading"): anything not shown to be a gap counts as met.\n// Corrected ("evidence only"): a requirement the supplied facts do not settle stays unknown.\n// No prices, workloads, supplier negotiations or real products are modelled.',
  shape='[{"name":"my case","option":"A or B","requirement":"YOUR_REQUIREMENT","expected":"met, gap or unknown"}]'),
 20: dict(title='Feed display tests',
  instructions='Write at least three cases. Each case is a JSON object with name, feed (security, transport or facilities), minutesSinceUpdate (whole minutes), available (true or false) and expectedDisplay (live, stale or unavailable). The pilot proposes an agreed freshness limit of 5 minutes. Include an unavailable feed and an available feed older than the limit. Predict what each model shows before running. Use the result in your review of the proposed design.',
  code='// One display decision per feed.\n// Baseline (the proposed design): every feed shows its last value as live.\n// Corrected: an unavailable feed is shown as unavailable; a feed older than the\n//            agreed limit (5 minutes, proposed) is shown as stale; otherwise live.\n// No networks, owners, schedules or AI models are modelled.',
  shape='[{"name":"my case","feed":"YOUR_FEED","minutesSinceUpdate":YOUR_MINUTES,"available":true,"expectedDisplay":"live, stale or unavailable"}]'),
 14: dict(title='Outage fallback tests',
  instructions='Write at least two cases. Each case is a JSON object with name, events (in order), expectedLookups (current, stale or missing for each lookup, in order) and expectedLost (how many changes are lost). Events: refresh, outage, recover, change:ID and lookup:ID. Include a case with a change and a lookup during the outage. Predict the lookups and losses before running.',
  code='// One central pickup list. While the central server is up, "refresh" replaces the desk\'s local copy.\n// "change:ID" updates a pickup; "lookup:ID" asks what the desk can see at that moment.\n// current = the desk sees the latest change; stale = an older version; missing = nothing for that ID.\n// Baseline: during an outage the desk reads the local copy, and new changes are lost.\n// Corrected: during an outage changes go on the controlled paper log; the desk reads the local copy\n//            plus the paper log; "recover" reconciles the paper log into the central list.\n// No devices or staff workload are modelled.',
  shape='[{"name":"my case","events":["refresh","outage","change:YOUR_ID","lookup:YOUR_ID","recover"],"expectedLookups":["current, stale or missing"],"expectedLost":YOUR_EXPECTATION}]'),
}
LABELS = '"labPrediction": "LAB PREDICTION", "labCases": "EXECUTABLE TEST CASES", "labEvidence": "LOCAL EXECUTION RECORD"'
HINT = 'The executable log replaces prose about hypothetical test execution. '


def markup(n: int) -> str:
    s = SPEC[n]
    return (f'<section class="card" id="practical"><p class="ey">SMALL EXECUTABLE LAB · PART OF THE EXISTING ARTIFACT</p><h2>{esc(s["title"])}</h2><p>{esc(s["instructions"])}</p>'
            '<p>Budget 15–20 minutes within the assignment. The run log replaces a paragraph describing hypothetical execution. Keep your actual failures; explain any wrong prediction. Passing tests is not an automatic grade.</p>'
            f'<details><summary>Inspect the teaching-model rules</summary><pre style="white-space:pre-wrap">{esc(s["code"])}</pre></details>'
            '<label for="labPrediction" class="field-label">Predict what each model will do and why.</label><textarea id="labPrediction" placeholder="My expected difference, and the concept that explains it…"></textarea>'
            '<label for="labCases" class="field-label">Write your executable test cases as JSON.</label><p class="hint">Replace the uppercase placeholders; they are a schema illustration, not runnable answers.</p>'
            f'<textarea id="labCases" spellcheck="false" placeholder="{esc(s["shape"])}" style="font:16px/1.5 monospace;min-height:200px"></textarea>'
            '<div class="buttons"><button type="button" data-lab-mode="baseline">Run baseline model</button><button type="button" data-lab-mode="corrected">Run corrected model</button></div>'
            '<p id="labStatus" role="status" aria-live="polite">Both runs are required; this is an offline teaching model.</p><pre id="labOutput" style="white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.5 monospace"></pre>'
            '<label for="labEvidence" class="field-label">Local execution record · included in export</label><textarea id="labEvidence" readonly style="min-height:140px" placeholder="Generated after a local run. Changing the test cases clears this record."></textarea></section>')


def patch(path: Path, n: int) -> bool:
    s = path.read_text(encoding='utf-8')
    if 'id="practical"' in s:
        return False
    def one(old, new, count=1):
        nonlocal s
        if s.count(old) != count:
            raise SystemExit(f'{path.name}: expected {count}× {old[:60]!r}, found {s.count(old)}')
        s = s.replace(old, new)
    # 1. lab section right after the FIT card
    m = re.search(r'<section class="card fit">.*?</section>', s, re.S)
    s = s[:m.end()] + markup(n) + s[m.end():]
    # 2. Part A fields, labels and the lab requirement
    one('"sourceUse", "technical"],M=', '"sourceUse", "technical", "labPrediction", "labCases", "labEvidence"],M=')
    if LABELS not in s:  # older generated pages already carry the lab labels
        one('"technical": "TRANSFER CHECK"}', '"technical": "TRANSFER CHECK", ' + LABELS + '}', count=3)
    one('"lab": false};', '"lab": true};')
    one('Keep the complete written response to about 180–260 focused words; use compact tables or notation. Include the source application and transfer answer in that budget. ',
        'Keep the complete written response to about 180–260 focused words; use compact tables or notation. Include the source application and transfer answer in that budget. ' + HINT)
    # 3. the teaching model, inlined like Assignments 7–8, and mounted after boot
    one('<div class="print" id="print"></div>\n</main>\n<script>', '<div class="print" id="print"></div>\n</main>\n<script>' + LABS + '</script><script>')
    one('\nboot();\n', f'\nboot();\nStudyLab.mount({n});\n')
    path.write_text(s, encoding='utf-8')
    return True


INLINE = re.compile(r"<script>/\* Deterministic teaching models\..*?module\.exports=StudyLab;\n?</script>", re.S)


def sync_inline(path: Path) -> bool:
    """Keep every page's inline copy of the teaching models identical to curriculum/learning-path/labs.js."""
    s = path.read_text(encoding='utf-8')
    new = INLINE.sub(lambda m: '<script>' + LABS + '</script>', s, count=1)
    if new != s:
        path.write_text(new, encoding='utf-8'); return True
    return False


def main() -> int:
    pub = json.loads(PUB.read_text(encoding='utf-8'))
    done = []
    for a in pub['assignments']:
        if a['chapter'] in SPEC:
            if patch(ROOT / a['path'], a['chapter']):
                done.append(a['chapter'])
            a['practical'] = True
        if a.get('practical'):
            sync_inline(ROOT / a['path'])
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Executable labs added to chapters', done or 'none (already present)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
