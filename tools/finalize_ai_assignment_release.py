from pathlib import Path
from bs4 import BeautifulSoup
import importlib.util,json,re,hashlib

R=Path(__file__).resolve().parents[1]
sp=importlib.util.spec_from_file_location("aiv3",R/"curriculum/ai_assignment_v3.py")
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
D=m.DATA; PAPER_URL=m.PAPER_URL; PAPER_TITLE=m.PAPER_TITLE
PUB=R/"curriculum/publication.json"
pub=json.loads(PUB.read_text(encoding="utf-8"))
lect={x["chapter"]:x for x in pub["lectures"]}
ass={x["chapter"]:x for x in pub["assignments"]}

# Ch16/17: remove the legacy non-AI teaching labs from the new AI-only assignments.
for ch in (16,17):
    p=R/f"lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html"
    soup=BeautifulSoup(p.read_text(encoding="utf-8"),"html.parser")
    practical=soup.select_one("#practical")
    if practical: practical.decompose()
    for sc in list(soup.find_all("script")):
        txt=sc.string or sc.get_text()
        if "var StudyLab=" in txt: sc.decompose()
    sc=soup.find_all("script")[-1]; js=sc.string or sc.get_text()
    js=re.sub(r'const A=\[[^\]]*\],M=', 'const A=["fit","measure","bound","act","evidence","sourceUse","technical"],M=', js, count=1)
    js=re.sub(r'const V2_CONFIG=(\{.*?\});',lambda x:x.group(0).replace('"lab": true','"lab": false'),js,count=1)
    js=js.replace("The executable log replaces prose about hypothetical test execution. ","")
    js=js.replace("Use your executed test log above. Explain one observed difference between models and one limit of the model; revise an incorrect prediction explicitly. The log replaces prose about tests you might run.","")
    sc.string=js
    p.write_text(str(soup),encoding="utf-8")
    ass[ch]["practical"]=False

# Canonical gateway manifest.
gateway={}
for ch,d in D.items():
    a=ass[ch]
    gateway[str(ch)]={
      "chapter":str(ch),"ey":f"Chapter {ch} · Assignment {d['assignment']} · AI-only v3",
      "title":d["title"],"intro":"Assess an AI-containing system using the chapter mechanism. Submit one machine-readable JSON file in Blackboard.",
      "time":"35–55 minutes","points":f"{d['max_points']} points","access":a["access_key"],"edition":"ai-v3",
      "assignment":a["path"],"lecture":lect[ch]["path"],"previous":a["previous_path"],
      "steps":["Review the chapter AI segment and the worked example.","Complete FIT → AI artifact → BOUND → ACT + EVIDENCE.",
               "Commit Part A, then respond to the new STRESS evidence.","Complete human review, download Blackboard JSON, and upload that one file to Blackboard."],
      "note":"Blackboard is the official identity and submission record. The website creates the grading artifact; the rubric grader evaluates its engineering reasoning.",
      "ack":"I will submit my own bounded engineering judgment, disclose AI assistance, and distinguish observed, derived, proposed and unknown evidence.",
      "commit":"Part A is frozen before STRESS appears. This preserves the first judgment; it is not Blackboard submission."
    }
(R/"curriculum/learning-path/gateway.json").write_text(json.dumps(gateway,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
# Hub: make the assessment change visible before students open an assignment.
hp=R/"iscarb.html"; h=BeautifulSoup(hp.read_text(encoding="utf-8"),"html.parser")
workflow=h.select_one("#workflow")
if workflow:
    stages=workflow.find_all("div",recursive=False)
    if len(stages)>=3:
        stages[2].h3.string="Apply to an AI-containing system"
        stages[2].p.string="Use the chapter mechanism on a new AI case, download one grading JSON, and upload that file to Blackboard."
notice=h.select_one("#mastery-update")
if notice:
    notice.h2.string="AI-only assignments · one grading artifact"
    notice.p.string="All nine after-class assignments now assess an AI-containing system. Each page shows a worked example and the exact rubric before the assessed case. Students submit one JSON file to Blackboard; PDF is optional unless requested."
gen=h.select_one("#genai-release")
if gen:
    ps=gen.find_all("p")
    if ps:
        ps[0].clear(); ps[0].append(BeautifulSoup("<b>Lecture + assignment alignment:</b> every chapter includes a GenAI segment, and its assignment now tests the same engineering mechanism on a different AI-containing system.","html.parser"))
    if len(ps)>1: ps[1].string="Lecture release 20260926-genai-v12 · Assignment release 20260925-ai-only-v3. Lecture slide counts and course points remain unchanged."
for ch,d in D.items():
    art=h.select_one(f"#chapter-{ch}")
    if not art: continue
    meta=art.select_one(".meta")
    if meta:
        spans=meta.find_all("span")
        if len(spans)>=2: spans[1].string=f"Assignment {d['assignment']}: AI-only · {d['title']}"
hp.write_text(str(h),encoding="utf-8")

# Student guide: one workflow, no PDF ambiguity, and no legacy non-AI lab requirement.
gp=R/"student-guide.html"; g=BeautifulSoup(gp.read_text(encoding="utf-8"),"html.parser")
scope=g.select_one("#assessment-scope")
if scope:
    scope.h2.string="Required study + AI-only assignment: exact scope"
    ol=scope.find("ol")
    if ol:
        items=[
          "Review the named source selections and the chapter AI segment before the assignment.",
          "Read the worked example and rubric first. The example teaches quality; it is not the assessed case.",
          "Apply one assigned source concept to the AI-containing system, then make a bounded engineering decision.",
          "Commit Part A before STRESS, revise the decision, complete human review, and download the Blackboard JSON."
        ]
        for li,t in zip(ol.find_all("li",recursive=False),items): li.clear();li.append(t)
    for p in scope.find_all("p"):
        txt=p.get_text(" ",strip=True)
        if "Use about 180" in txt: p.string="Keep answers compact and technical. A table, calculation or structured artifact may replace prose. The grader rewards mechanism, boundary, evidence and accountability—not length or fluency."
        elif "Initial planning budget:" in txt: p.string="Initial planning budget: approximately 35–55 active minutes total, including required preparation and the AI-only assignment. Report actual time; this planning target does not affect the grade."
        elif "Submit once through Blackboard" in txt: p.string="Submit once through Blackboard: upload the JSON produced by the assignment page. Blackboard is the official identity and receipt record. PDF/Markdown are optional personal copies unless the instructor requests them."
students=g.select_one("#students")
if students:
    lis=students.select("ol.steps > li")
    if len(lis)>=5:
        lis[3].clear();lis[3].append("Complete the AI-only assignment. Preserve the initial judgment, reveal STRESS, then justify RETAIN, REVISE or REPLACE.")
        lis[4].clear();lis[4].append("Review and submit. Declare AI assistance, download Blackboard JSON and upload that one file to the Blackboard assignment.")
cons=next((x for x in g.select("section") if x.h2 and x.h2.get_text(strip=True)=="What stays consistent"),None)
if cons:
    ps=cons.find_all("p")
    if ps: ps[0].string="CRISIS → MAP → TRADE-OFF → EVIDENCE → VERDICT remains the reasoning thread. Every after-class task is now an AI-containing system and keeps the familiar FIT → AI ARTIFACT → BOUND → ACT + EVIDENCE → STRESS → REFIT sequence."
gp.write_text(str(g),encoding="utf-8")

# Course resources: make the AI-only assessment scope explicit and keep the research link visible.
rp=R/"course-resources.html"; rs=BeautifulSoup(rp.read_text(encoding="utf-8"),"html.parser")
for sec in rs.select("section"):
    h2=sec.find("h2")
    if not h2: continue
    title=h2.get_text(" ",strip=True)
    if title=="Course-outcome map":
        for row in sec.select("tbody tr"):
            cells=row.find_all("td")
            if cells and cells[0].get_text(strip=True)=="11" and len(cells)>=4:
                cells[3].string="Test design and verification reasoning are practised in AI-containing cases; broader testing-strategy implementation and the separate Code Coverage topic remain incomplete."
    if title=="Assignments and assessment":
        ps=sec.find_all("p",recursive=False)
        if ps:
            ps[0].string="Assignment 1 remains 4 points; Assignments 2–9 remain 5 points. All nine current assignments are AI-only engineering cases and use the same visible quarter-point rubric levels (1, 0.75, 0.5, 0)."
        if len(ps)>1:
            ps[1].string="Each task assesses an AI-containing system using the chapter mechanism: reliability, safety, security, resilience, reuse, component contracts, distributed effects or systems-of-systems governance. Blackboard is the official submission and grade record; students upload one machine-readable JSON file."
    if title=="NCAAA, Jaheziah and iSCARB":
        ps=sec.find_all("p",recursive=False)
        if ps:
            ps[-1].string="The iSCARB toolkit and AI-only assignments make reasoning, evidence, boundaries, human responsibility and revision visible. They support course learning; they do not establish an official national item-weight or accreditation mapping."
rp.write_text(str(rs),encoding="utf-8")

# Instructor guide: remove legacy non-AI lab wording and document the automated Blackboard workflow.
ip=R/"instructor-guide.html"; ins=BeautifulSoup(ip.read_text(encoding="utf-8"),"html.parser")
for sec in ins.select("section"):
    h2=sec.find("h2")
    if not h2: continue
    title=h2.get_text(" ",strip=True)
    if title=="Mark the mechanism and the evidence":
        ps=sec.find_all("p",recursive=False)
        if ps:
            ps[0].string="Assignment 1 remains 4 points; Assignments 2–9 remain 5 points. Every current assignment is an AI-containing system. Score the chapter mechanism, AI-specific failure/assumption, boundary, inspectable evidence, accountable role and the quality of the post-STRESS revision—not fluency or length."
        if len(ps)>1:
            ps[1].string="Use the published levels consistently: 1 for correct connected reasoning; 0.75 for one minor qualification gap; 0.5 for a consequential technical/evidence gap; 0 for missing, materially wrong, generic or invented evidence. A justified RETAIN may earn full credit when the original boundary still holds."
    if title=="Two executable tasks within the existing assignments":
        h2.string="One structured AI artifact per chapter"
        ps=sec.find_all("p",recursive=False)
        if ps:
            ps[0].string="Each assignment uses a different AI engineering artifact: dependability decision, reliability calculation, safety requirement/checker, RAG authorization test, AI-independent recovery path, hosted-vs-local reuse comparison, component contract, idempotency design, or cross-owner AI feed contract."
        if len(ps)>1:
            ps[1].string="Students may use tables, calculations, contracts or event sequences instead of long prose. The artifact must remain inspectable and must distinguish supplied/derived facts from proposed tests or unknown evidence."
    if title=="Check workload and learning before claiming success":
        ps=sec.find_all("p",recursive=False)
        if ps:
            ps[0].string="Initial planning budget is about 35–55 active minutes including preparation. Use reported time to shorten low-value writing if the median repeatedly exceeds the target; do not treat these estimates as measured learning outcomes."
flow=ins.select_one("#ai-grading-workflow")
if flow:
    ps=flow.find_all("p",recursive=False)
    if ps:
        ps[0].clear(); ps[0].append(BeautifulSoup("<b>Student:</b> solve on the course site → download one JSON → upload JSON to Blackboard. <b>Instructor:</b> download the Blackboard submissions ZIP → drag it onto <code>tools/GRADE_BLACKBOARD_AI.bat</code> (or run the Python grader) → inspect <code>review_queue.csv</code> → approve proposed scores → import the approved gradebook.", "html.parser"))
    if len(ps)>1:
        ps[1].string="Blackboard remains the official identity/receipt record. The grader uses GPT-5.6 Terra by default when OPENAI_API_KEY is available; otherwise it validates submissions and creates a review queue without inventing grades. AI scores are recommendations until instructor approval."
ip.write_text(str(ins),encoding="utf-8")

# Hub: expose the paper next to the assignment release notice.
hp=R/"iscarb.html"; hs=BeautifulSoup(hp.read_text(encoding="utf-8"),"html.parser")
notice=hs.select_one("#mastery-update")
if notice and not notice.find("a",href=PAPER_URL):
    p=hs.new_tag("p"); a=hs.new_tag("a",href=PAPER_URL,target="_blank",rel="noopener"); a.string="Research basis · iSCARB AI-containing systems paper on Zenodo"; p.append(a); notice.append(p)
hp.write_text(str(hs),encoding="utf-8")

# Fix relative links inside archived Mastery v2 pages now that they live one directory deeper.
archive=R/"lectures/iscarb/previous-mastery-v2"
for ch in D:
    ap=archive/f"Ch{ch}-FBR-Student-Assignment.html"
    if not ap.exists(): continue
    t=ap.read_text(encoding="utf-8")
    t=t.replace('href="../../iscarb.html"','href="../../../iscarb.html"')
    t=re.sub(r'href="(Ch\d+-[^\"]+\.html(?:#[^\"]*)?)"',r'href="../\1"',t)
    t=re.sub(r'href="previous/([^\"]+)"',r'href="../previous/\1"',t)
    t=t.replace("fetch(C.reveal", "fetch(C.reveal.startsWith('../')?C.reveal:'../'+C.reveal")
    ap.write_text(t,encoding="utf-8")

# Publication allowlist: publish current AI STRESS plus the immediately previous assignment pages for recovery.
allowed=set(pub.get("iscarb_public_files",[]))
for ch in D:
    allowed.add(f"lectures/iscarb/reveal/r{ch}-ai-v3.json")
    allowed.add(f"lectures/iscarb/previous-mastery-v2/Ch{ch}-FBR-Student-Assignment.html")
pub["iscarb_public_files"]=sorted(allowed)
pub["student_submission_version"]="20260925-ai-only-v3"
pub["assignment_release"]="20260925-ai-only-v3"
for rec in pub["assignments"]:
    rec["practical"]=False
# Root pages are staged explicitly, not part of the ISCARB delivery-asset allowlist.
for root_name in ("fbr-submission.html","course-resources.html","instructor-guide.html","student-guide.html","iscarb.html"):
    pub.get("delivery_asset_sha256",{}).pop(root_name,None)
TEXT_EXT={'.html','.htm','.js','.css','.json','.md','.txt','.py','.yml','.yaml','.cjs','.mjs'}
def sha(rel):
    p=R/rel; b=p.read_bytes()
    if p.suffix.lower() in TEXT_EXT: b=b.replace(b'\r\n',b'\n')
    return hashlib.sha256(b).hexdigest()
for rec in pub["assignments"]:
    pub["delivery_asset_sha256"][rec["path"]]=sha(rec["path"])
    pub["delivery_asset_sha256"][rec["stress_path"]]=sha(rec["stress_path"])
    pub["delivery_asset_sha256"][rec["previous_path"]]=sha(rec["previous_path"])
PUB.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# Keep learning-path assignment metadata consistent with publication.
ap=R/"curriculum/learning-path/assignments.json"
arr=json.loads(ap.read_text(encoding="utf-8"))
for x in arr: x["practical"]=False
ap.write_text(json.dumps(arr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print("Finalized AI-only assignment release and public allowlist.")
