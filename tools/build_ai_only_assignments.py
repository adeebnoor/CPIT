from pathlib import Path
from bs4 import BeautifulSoup
import importlib.util, json, re, shutil, hashlib

R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("aiv3",R/"curriculum/ai_assignment_v3.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
DATA=m.DATA; PAPER_URL=m.PAPER_URL; PAPER_TITLE=m.PAPER_TITLE
PUB=R/"curriculum/publication.json"
pub=json.loads(PUB.read_text(encoding="utf-8"))
lecture={x["chapter"]:x for x in pub["lectures"]}
archive=R/"lectures/iscarb/previous-mastery-v2"; archive.mkdir(parents=True,exist_ok=True)

def set_inner(el,html):
    el.clear(); frag=BeautifulSoup(html,"html.parser")
    for x in list(frag.contents): el.append(x)

def set_prompt(soup,field,label,prompt):
    el=soup.select_one("#"+field)
    if not el: return
    sec=el.find_parent("section")
    lab=sec.select_one(".lab")
    if lab and field=="measure": lab.string="A2 · AI ENGINEERING ARTIFACT · 1 POINT"
    lbl=sec.select_one(f'label[for="{field}"]')
    if lbl: lbl.string=label
    hints=[p for p in sec.find_all("p",recursive=False) if "lab" not in p.get("class",[])]
    if hints: set_inner(hints[0],prompt)
    el["placeholder"]=re.sub("<[^>]+>","",prompt).replace("…","...")
for ch,d in DATA.items():
    a_no=d["assignment"]; maxp=d["max_points"]
    path=R/f"lectures/iscarb/Ch{ch}-FBR-Student-Assignment.html"
    if not (archive/path.name).exists(): shutil.copy2(path,archive/path.name)
    soup=BeautifulSoup(path.read_text(encoding="utf-8"),"html.parser")
    soup.html["data-assessment-edition"]="ai-v3"
    soup.title.string=f"Assignment {a_no} · Chapter {ch} · AI-only engineering task"
    style=soup.find("style")
    if style and ".ai-course-mark{" not in style.string:
        style.string += """\n.ai-course-mark{display:inline-flex;align-items:center;gap:10px;margin:0 0 14px;padding:8px 13px 8px 8px;border:1px solid rgba(121,217,218,.55);border-radius:999px;background:linear-gradient(135deg,rgba(121,217,218,.12),rgba(182,170,255,.10))}.ai-course-mark .ai-orb{display:grid;place-items:center;width:42px;height:42px;border-radius:13px;background:linear-gradient(135deg,var(--teal),var(--violet));color:#071014;font-weight:900}.ai-course-mark b{display:block;letter-spacing:.09em;font-size:13px}.ai-course-mark small{display:block;color:var(--dim);font-size:13px}.qeeem-note{border-color:var(--teal)}"""
    header=soup.select_one("header.top")
    header.select_one(".ey").string=f"AFTER-CLASS · CHAPTER {ch} · AI-ONLY"
    ai_mark=BeautifulSoup('''<div class="ai-course-mark"><span class="ai-orb" aria-hidden="true">AI</span><span><b>AI-FIRST · iSCARB</b><small>Engineering judgment for AI-containing systems</small></span></div>''',"html.parser").div
    header.insert(0,ai_mark)
    header.h1.string=d["title"]
    header.select_one(".sub").string="This assignment is only about an AI-containing system. Use the chapter mechanism to make a bounded engineering decision; polished AI text without inspectable reasoning earns no credit."
    chips=header.select(".chip")
    if chips:
        chips[-1].string="AI-containing system · individual judgment"
    flow=header.select(".flow li")
    if flow:
        labels=["AI warm-up","FIT → AI artifact → BOUND → ACT + EVIDENCE","Commit Part A","STRESS → REFIT","Download JSON → Blackboard"]
        for x,t in zip(flow,labels): x.string=t

    warm=soup.select_one("#assignment-learning-path")
    set_inner(warm,f'''<p class="ey">1 · AI WARM-UP · 5 MINUTES · NOT GRADED</p><h2>{d["warm"]}</h2>
    <details class="warmup-answer"><summary>Show / hide the example answer</summary><div class="answer-text">{d["warmanswer"]}</div></details>
    <p class="hint">No written warm-up response is required. The assessed case below is different.</p>
    <details><summary>Exactly what to do</summary><p>1) identify the AI-specific engineering issue; 2) build the chapter artifact; 3) state the boundary and evidence; 4) commit before STRESS; 5) revise the decision; 6) download one JSON file for Blackboard.</p></details>''')

    prep=soup.select_one("#requiredPreparation")
    ai_anchor="CHALLENGE" if ch==10 else "AISYS"
    set_inner(prep,f'''<p class="ey">CURRENT EDITION · AI-ONLY V3</p><h2>Required preparation and research basis</h2>
    <p><b>Before answering:</b> review the chapter's <a href="{lecture[ch]["path"].split("/")[-1]}#{ai_anchor}">AI segment</a> and the named source review already assigned for this chapter.</p>
    <p>The assessed object is an <b>AI-containing system</b>. Generic answers about "software" or "use AI carefully" are insufficient unless you name the mechanism, boundary, evidence and responsible human role.</p>
    <p><b>Research basis:</b> <a href="{PAPER_URL}" target="_blank" rel="noopener">{PAPER_TITLE}</a>. The paper explains why this course assesses defensible engineering judgment rather than polished answer production.</p>
    <p><b>Previous work:</b> <a href="previous-mastery-v2/{path.name}">resume/export the Mastery v2 edition</a> if you already started it. New AI-only work uses a separate local key.</p>''')
    rubric=soup.select_one("#rubric-heading").find_parent("section")
    rubric.select_one("#rubric-heading").string=f"How your AI assignment is assessed · {maxp} points"
    rows=rubric.select("tbody tr")
    if ch==10:
        criteria=[
          ("FIT + AI MECHANISM","Names the relevant dependability property, the shared AI dependency/common cause, and a chapter mechanism that actually constrains the claim."),
          ("BOUND + EVIDENCE","States model/version, operating profile, human-check assumptions and inspectable evidence; proposed or missing evidence is labelled honestly."),
          ("ACT + RESPONSIBILITY","Issues a feasible CONTROL / ADVISORY-ONLY / DISABLE decision with an accountable owner and a control that does not depend on the model being correct."),
          ("STRESS → REFIT","Explains how the new AI evidence affects the original boundary and gives a coherent final decision with remaining uncertainty.")
        ]
    else:
        criteria=[
          ("FIT","Identifies the AI-specific engineering problem accurately and connects it to the chapter mechanism rather than generic AI advice."),
          ("AI ENGINEERING ARTIFACT",d["artifact"]+". The work is technically checkable and uses only supplied facts or clearly labelled proposals."),
          ("BOUND","States the model/version, operating conditions, scope and an observable trigger that would reopen the claim."),
          ("ACT + EVIDENCE","Gives a feasible bounded action, responsible human role and inspectable evidence; measured, derived, proposed and unknown claims are distinguished."),
          ("STRESS → REFIT","Uses the new evidence to retain, revise or replace the original claim and produces a coherent final record.")
        ]
    for row,(name,desc) in zip(rows,criteria):
        cells=row.find_all(["th","td"])
        cells[0].string=f"{name} · 1 point"
        set_inner(cells[1],f"<b>1.0:</b> {desc}<br><b>0.75:</b> Correct core reasoning with one minor missing qualification.<br><b>0.5:</b> Partly correct, but a consequential technical/evidence gap remains.<br><b>0:</b> Missing, materially wrong, generic, or dependent on invented evidence.")
    hint=rubric.select_one(".hint")
    if hint: hint.string="The grader scores the reasoning against this table. Length, fluency and AI-polished wording do not earn points. A submission may be flagged for instructor review when evidence is contradictory or the automated grader is uncertain."
    ex=rubric.select_one("#qualityExample")
    if ex:
        set_inner(ex,f'''<summary>See a complete example before you start</summary>
        <p><b>Different practice example · weak:</b> {d["example_weak"]}</p>
        <p><b>Stronger answer:</b> {d["example_strong"]}</p>
        <p><b>Why stronger:</b> it names the mechanism, boundary, evidence and human responsibility. Do not copy it: your assessed scenario is different.</p>''')

    checklist=next((x for x in soup.select("section.card") if "THIS WEEK · SUBMISSION CHECKLIST" in x.get_text() or (x.find("h2") and x.find("h2").get_text(" ",strip=True)=="Before you start")),None)
    if checklist:
        set_inner(checklist,f'''<p class="ey">ONE SUBMISSION · BLACKBOARD</p><h2>What you submit</h2><ol>
        <li>Read the {maxp}-point rubric and the example above.</li>
        <li>Complete Part A, commit, then complete STRESS → REFIT and human review.</li>
        <li>Click <b>Download Blackboard JSON</b>. This is the required machine-readable file.</li>
        <li>Upload that <b>.json</b> file to the Blackboard assignment. PDF is optional for your own readable copy unless the instructor asks for it.</li>
        <li>Verify the Blackboard receipt. The course website does not claim that Blackboard received your file.</li></ol>
        <p class="hint">One JSON file is enough for grading. Do not paste screenshots or submit an AI chat transcript.</p>''')
    align=soup.select_one("#classroom-assignment-alignment")
    if align:
        set_inner(align,f'''<p class="ey">LECTURE → AI SEGMENT → ASSIGNMENT</p><h2>One AI-containing system, one defensible judgment</h2>
        <p>The lecture teaches the chapter mechanism; the AI segment shows how that mechanism changes when a learned component is inside the system; this assignment transfers the same reasoning to a different AI case.</p>
        <p><b>No extra toolkit report is required.</b> Your submitted evidence is the committed Part A, STRESS response, final decision, source application and human review.</p>
        <nav class="nav"><a href="{lecture[ch]["path"].split("/")[-1]}#{ai_anchor}">Review AI segment</a><a href="{lecture[ch]["path"].split("/")[-1]}#READING">Required source review</a><a href="{PAPER_URL}" target="_blank" rel="noopener">iSCARB paper · Zenodo</a></nav>''')

    scenario=soup.select_one("#scenarioText")
    if scenario: set_inner(scenario,"<p>"+d["scenario"]+"</p>")
    ass=soup.select_one("#assessed-scenario")
    if ass and ass.h2: ass.h2.string="Assessed scenario · AI-containing system"

    set_prompt(soup,"fit","What AI-specific engineering claim governs this decision?",d["fit"])
    if soup.select_one("#measure"):
        set_prompt(soup,"measure","Build the chapter's AI engineering artifact.",d["artifact_prompt"])
    set_prompt(soup,"bound","Where does your AI claim stop?",d["bound"])
    set_prompt(soup,"act","What bounded action should be taken now?",d["act"])
    ev=soup.select_one("#evidence")
    if ev:
        lab=ev.find_parent("section")
        lbl=lab.select_one('label[for="evidence"]')
        if lbl: lbl.string="What inspectable evidence supports or limits that action?"
        hint=lab.select_one("#evidenceHint")
        if hint: hint.string="Name the actual evidence, conditions, version and reviewer. Separate observed/derived evidence from proposed tests or unknowns."
        ev["placeholder"]="Available/derived evidence: ...\nProposed or missing evidence: ...\nVersion/conditions: ...\nReviewer/owner: ..."
    src=soup.select_one("#sourceUse")
    if src:
        sec=src.find_parent("section"); lab=sec.select_one(".lab")
        if lab: lab.string="SOURCE → AI SYSTEM CONNECTION · INCLUDED IN RUBRIC"
        lbl=sec.select_one('label[for="sourceUse"]')
        if lbl: lbl.string="Which assigned source concept constrains your AI-system claim?"
        ps=sec.find_all("p",recursive=False)
        if ps: set_inner(ps[-1],"Give the assigned source slide number, explain the concept in your own words, then state exactly which AI-system assumption, control or boundary it supports.")
        src["placeholder"]="Slide number — source concept — connection to the AI system..."
    tech=soup.select_one("#technical")
    if tech:
        sec=tech.find_parent("section"); lab=sec.select_one(".lab")
        if lab: lab.string="AI MECHANISM CHECK · INCLUDED IN RUBRIC"
        lbl=sec.select_one('label[for="technical"]')
        if lbl: lbl.string="Explain the AI-specific mechanism in 2–3 focused sentences."
        ps=sec.find_all("p",recursive=False)
        if ps: set_inner(ps[-1],d["artifact_prompt"] if ch==10 else "Explain why the AI-specific assumption can fail even when ordinary software/API checks pass, and identify the engineering control or evidence that matters.")
        tech["placeholder"]="AI-specific failure/assumption → engineering mechanism/control → evidence..."
    script=soup.find_all("script")[-1]
    js=script.string or script.get_text()
    cm=re.search(r"const C=(\{.*?\});",js)
    if not cm: raise RuntimeError(f"missing C config ch{ch}")
    c=json.loads(cm.group(1))
    c["version"]=f"2026-09-ch{ch}-ai-v3"
    c["keyBase"]=f"fbr:cpit455:ch{ch}:ai:v3"
    c["reveal"]=f"reveal/r{ch}-ai-v3.json"
    c["scenarioTitle"]=d["title"]+" · AI teaching simulation"
    js=js[:cm.start()]+("const C="+json.dumps(c,ensure_ascii=False,separators=(",",":"))+";")+js[cm.end():]
    ai_cfg={"schema":"cpit455-ai-v3","assignment":a_no,"maxScore":maxp,"paperUrl":PAPER_URL,"paperTitle":PAPER_TITLE}
    insert="\nconst AI3_CONFIG="+json.dumps(ai_cfg,ensure_ascii=False,separators=(",",":"))+";\n"
    pos=js.find("\nconst A=")
    js=js[:pos]+insert+js[pos:]

    js=js.replace("Export, then submit in the LMS","Download JSON, then submit in Blackboard")
    js=js.replace("<li>Review all four rubric criteria.</li><li>Use <b>Print / PDF</b> and save the PDF.</li><li>Open the PDF to check it, then upload it to the LMS.</li><li>Keep the editable .md backup and verify the LMS receipt.</li>",
                  f"<li>Review the {maxp}-point rubric.</li><li>Download <b>Blackboard JSON</b>; this is the required grading file.</li><li>Upload that JSON to the Blackboard assignment and verify the receipt.</li><li>PDF and editable Markdown are optional personal copies unless requested.</li>")
    js=js.replace('<button id="pdf" class="good" disabled>Print / PDF</button><button id="download" disabled>Download final editable .md</button><button id="copy" disabled>Copy final text</button>',
                  '<button id="json" class="good" disabled>Download Blackboard JSON</button><button id="pdf" disabled>Print / PDF copy</button><button id="download" disabled>Download editable .md</button><button id="copy" disabled>Copy final text</button>')
    js=js.replace("['download','copy','pdf'].forEach(x=>$(x).disabled=!ok)","['json','download','copy','pdf'].forEach(x=>$(x).disabled=!ok)")
    js=js.replace("$('download').onclick=downloadFinal;$('copy').onclick=copyFinal;$('pdf').onclick=printFinal;exportState()",
                  "$('json').onclick=downloadJSON;$('download').onclick=downloadFinal;$('copy').onclick=copyFinal;$('pdf').onclick=printFinal;exportState()")
    marker="function downloadFinal(){"
    add="""function submissionJSON(){
 const d=data();
 return {schema:AI3_CONFIG.schema,course:'CPIT-455',assignment:AI3_CONFIG.assignment,chapter:Number(C.chapter),max_score:AI3_CONFIG.maxScore,version:C.version,paper:{title:AI3_CONFIG.paperTitle,url:AI3_CONFIG.paperUrl},student:{name:d.student||'',id:d.sid||ACCESS?.sid||'',section:d.section||''},submitted_at:now(),commit:{id:d.commitId||'',locked_at:d.lockAt||'',stress_revealed_at:d.revealedAt||''},scenario:{title:C.scenarioTitle,text:d.scenario||''},partA:d.partA||{},stress:d.stress||null,boundaryState:d.boundaryState||'',refit:d.refit||'',refitwhy:d.refitwhy||'',finalDecision:d.revised||'',aiUse:d.aiUse||'',humanReview:{name:d.signer||'',attested:!!d.attested},activeMinutes:d.activeMinutes||'',feedbackNote:d.feedbackNote||'',revisionNote:d.revisionNote||''};
}
function downloadJSON(){
 if(valB())return; preserveFirstExport?.();
 let url='';try{const text=JSON.stringify(submissionJSON(),null,2);url=URL.createObjectURL(new Blob([text],{type:'application/json;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=stem()+'.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);$('done').textContent='Blackboard JSON downloaded. Upload this JSON file to the Blackboard assignment and verify the receipt.';}catch(e){if(url)URL.revokeObjectURL(url);$('done').textContent='JSON download failed. Keep this page open and retry.';}
}
"""
    if marker not in js: raise RuntimeError(f"download marker missing ch{ch}")
    js=js.replace(marker,add+marker,1)
    js=js.replace("Submit the checked PDF through the LMS.","Download the Blackboard JSON and submit it through Blackboard. PDF is optional unless requested.")
    js=js.replace("upload it to the LMS","upload the JSON to Blackboard")
    script.string=js
    foot=soup.select_one("footer.foot p")
    if foot: foot.string="Privacy: work stays in this browser until you download it. Blackboard is the official submission/identity record. The required grading artifact is the final JSON file."
    qeeem=BeautifulSoup('''<section class="card qeeem-note" id="qeeem-evaluation"><p class="ey">COURSE EVALUATION · قيّم تجربتك</p><h2>Evaluate professionally and honestly</h2><p>After experiencing the course, please share a credible evaluation on <a href="https://qeeem.com/" target="_blank" rel="noopener">Qeeem</a>. Evaluate the educational experience, not the person. Be truthful, respectful and specific. Your evaluation has no effect on your grade.</p></section>''',"html.parser").section
    soup.main.append(qeeem)
    path.write_text(str(soup),encoding="utf-8")
    reveal=R/f"lectures/iscarb/reveal/r{ch}-ai-v3.json"
    reveal.write_text(json.dumps({"chapter":str(ch),"version":c["version"],"label":"STRESS · new AI evidence","text":d["stress"],"principle":d["refit"]},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# update assignment manifests
assign_path=R/"curriculum/learning-path/assignments.json"
assign=json.loads(assign_path.read_text(encoding="utf-8"))
by_ch={x["chapter"]:x for x in assign}
for ch,d in DATA.items():
    rec=by_ch[ch]; rec["edition"]="ai-v3";rec["version"]=f"2026-09-ch{ch}-ai-v3"
    rec["storage_key"]=f"fbr:cpit455:ch{ch}:ai:v3";rec["stress_path"]=f"lectures/iscarb/reveal/r{ch}-ai-v3.json"
    rec["points"]=d["max_points"];rec["artifact"]=d["artifact"];rec["previous_path"]=f"lectures/iscarb/previous-mastery-v2/Ch{ch}-FBR-Student-Assignment.html"
assign_path.write_text(json.dumps(assign,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
for rec in pub["assignments"]:
    ch=rec["chapter"]; d=DATA[ch]
    rec["edition"]="ai-v3";rec["version"]=f"2026-09-ch{ch}-ai-v3";rec["storage_key"]=f"fbr:cpit455:ch{ch}:ai:v3"
    rec["stress_path"]=f"lectures/iscarb/reveal/r{ch}-ai-v3.json";rec["points"]=d["max_points"];rec["artifact"]=d["artifact"]
    rec["previous_path"]=f"lectures/iscarb/previous-mastery-v2/Ch{ch}-FBR-Student-Assignment.html"
pub["assignment_release"]="20260925-ai-only-v3"
pub["assessment_research_basis"]={"title":PAPER_TITLE,"url":PAPER_URL}
# gateway override: new AI-only titles, instructions and archived resume path
gate=R/"fbr-submission.html"; gs=gate.read_text(encoding="utf-8")
cfg={}
for ch,d in DATA.items():
    old=next(x for x in pub["assignments"] if x["chapter"]==ch)
    cfg[str(ch)]={
      "chapter":str(ch),"ey":f"Chapter {ch} · Assignment {d['assignment']} · AI-only v3",
      "title":d["title"],"intro":"Assess an AI-containing system using the chapter mechanism. One final JSON file is submitted in Blackboard.",
      "time":"35–55 minutes","points":f"{d['max_points']} points","access":old["access_key"],"edition":"ai-v3",
      "assignment":old["path"],"lecture":lecture[ch]["path"],"previous":old["previous_path"],
      "steps":["Review the AI segment and the worked example.","Complete FIT → AI artifact → BOUND → ACT + EVIDENCE.","Commit Part A, then respond to STRESS without rewriting your first judgment.","Complete human review, download Blackboard JSON, and upload that one file to Blackboard."],
      "note":"The website checks completeness; the rubric grader evaluates the submitted JSON. Blackboard remains the official identity and grade record.",
      "ack":"I will submit my own bounded engineering judgment, disclose AI assistance, and keep observed/derived/proposed evidence distinct.",
      "commit":"Part A is frozen before STRESS appears. This preserves the first engineering judgment; it is not Blackboard submission."
    }
override="\nObject.assign(CONFIG,"+json.dumps(cfg,ensure_ascii=False,separators=(",",":"))+");\n"
gs=re.sub(r"\nObject\.assign\(CONFIG,\{.*?\}\);\nconst q=",override+"const q=",gs,flags=re.S)
gate.write_text(gs,encoding="utf-8")

# add research basis to student resource page
cr=R/"course-resources.html"; cs=cr.read_text(encoding="utf-8")
if "22964248" not in cs:
    card=f'''<section class="notice" id="ai-assessment-paper"><h2>Research basis for the AI assignments</h2><p><a href="{PAPER_URL}" target="_blank" rel="noopener">{PAPER_TITLE}</a></p><p>The nine assignments use the paper's core idea: assess a defensible engineering judgment around an AI-containing system, not the polish of the answer alone.</p></section>'''
    cs=cs.replace("</main>",card+"</main>",1)
    cr.write_text(cs,encoding="utf-8")

# add instructor workflow
ig=R/"instructor-guide.html"; ins=ig.read_text(encoding="utf-8")
if "ai-grading-workflow" not in ins:
    block=f'''<section class="notice" id="ai-grading-workflow"><h2>AI-only assignment grading workflow</h2><p><b>Student:</b> solve on the course site → download one JSON → upload JSON to Blackboard. <b>Instructor:</b> download the Blackboard submissions ZIP → run <code>python tools/grade_ai_assignments.py &lt;zip-or-folder&gt;</code> → review only flagged cases → import the generated CSV into the gradebook.</p><p>Blackboard remains the official identity/receipt record. The grader can use OpenAI when <code>OPENAI_API_KEY</code> is set; otherwise it runs validation and creates a review queue without inventing a grade.</p><p><a href="{PAPER_URL}" target="_blank" rel="noopener">Research basis · Zenodo</a></p></section>'''
    ins=ins.replace("</main>",block+"</main>",1)
    ig.write_text(ins,encoding="utf-8")
# machine-readable rubric/key for the batch grader
rubrics={}
for ch,d in DATA.items():
    crit=(["FIT + AI MECHANISM","BOUND + EVIDENCE","ACT + RESPONSIBILITY","STRESS → REFIT"] if ch==10 else ["FIT","AI ENGINEERING ARTIFACT","BOUND","ACT + EVIDENCE","STRESS → REFIT"])
    rubrics[str(ch)]={"assignment":d["assignment"],"max_score":d["max_points"],"title":d["title"],"artifact":d["artifact"],"criteria":crit,
                     "scenario":d["scenario"],"expected_focus":{"fit":d["fit"],"artifact":d["artifact_prompt"],"bound":d["bound"],"act":d["act"],"refit":d["refit"]},
                     "worked_example":{"weak":d["example_weak"],"strong":d["example_strong"]},"paper":{"title":PAPER_TITLE,"url":PAPER_URL}}
(R/"curriculum/ai-assignment-rubrics.json").write_text(json.dumps({"schema":"cpit455-ai-v3","chapters":rubrics},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

# refresh hashes for changed public assets already tracked by publication
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for rec in pub["assignments"]:
    for key in ["path","stress_path"]:
        rel=rec[key]
        pub.setdefault("delivery_asset_sha256",{})[rel]=sha(R/rel)
pub["delivery_asset_sha256"]["fbr-submission.html"]=sha(R/"fbr-submission.html")
pub["delivery_asset_sha256"]["course-resources.html"]=sha(R/"course-resources.html")
pub["delivery_asset_sha256"]["instructor-guide.html"]=sha(R/"instructor-guide.html")
PUB.write_text(json.dumps(pub,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Built AI-only v3 assignments:",sorted(DATA))
