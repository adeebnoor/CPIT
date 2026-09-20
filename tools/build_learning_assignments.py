"""Extend the reviewed A2 commit/reveal engine with chapter-specific transfer tasks."""
from pathlib import Path
from bs4 import BeautifulSoup
import importlib.util,json,re
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/f'curriculum/learning-path/{name}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
A=load('assignments').ASSIGNMENTS;C=load('spec').CHAPTERS
BASE=(ROOT/'lectures/iscarb/Ch11-FBR-Student-Assignment.html').read_text()
def contents(el,markup):
 el.clear();frag=BeautifulSoup(markup,'html.parser')
 for x in list(frag.contents):el.append(x)
records=[];gateway={}
for n,a in A.items():
 i=list(C).index(n)+1;slug=C[n]['slug'];title=C[n]['title'];soup=BeautifulSoup(BASE,'html.parser')
 oldscript=soup.find('script').string;soup.find('script').decompose()
 for st in soup.find_all(string=True):
  if st.parent.name=='style':continue
  t=str(st).replace('Assignment 2',f'Assignment {i}').replace('ASSIGNMENT 2',f'ASSIGNMENT {i}').replace('Chapter 11',f'Chapter {n}').replace('CHAPTER 11',f'CHAPTER {n}').replace('Reliability Engineering',title).replace('35–45 minutes',a['minutes']+' minutes')
  if t!=str(st):st.replace_with(t)
 soup.title.string=f'Assignment {i} · Chapter {n} · {title}'
 for link in soup.find_all('a',href=True):link['href']=link['href'].replace('Ch11-Reliability-Engineering.html',f'Ch{n}-{slug}.html')
 soup.h1.string=a['title'];soup.select_one('header .sub').string='Use the familiar decision-and-evidence sequence. This chapter focuses on '+a['artifact'].lower()+'. Make the initial decision before seeing the new evidence.'
 warm=soup.select_one('#assignment-learning-path');contents(warm,f'<p class="ey">1 · WARM-UP · 5 MINUTES · NOT GRADED</p><h2>{a["warm"]}</h2><details class="warmup-answer"><summary>Show / hide warm-up answer</summary><p>{a["warmanswer"]}</p></details><p class="hint">No written warm-up response is required.</p><details><summary>Lecture guide</summary><p>{a["source"]}</p><p>FIT identifies the relevant problem. {a["step"]} builds this chapter’s artifact. BOUND states the limits. ACT + EVIDENCE records the action, owner and verification. STRESS then tests your reasoning before REFIT.</p></details>')
 scenario=soup.select_one('#scenarioText');contents(scenario,'<p>'+a['scenario']+'</p>');soup.select_one('#assessed-scenario h2').string='Assessed scenario · fictional teaching case'
 for p in soup.select('#assessed-scenario p'):
  if 'Aim for' in p.get_text():p.string='Aim for 300–450 focused words overall, using a small table or clear notation where useful. No external experiment or production-system access is required. Cite at least one relevant lecture unit or original source slide. Any additional test, threshold or result must be identified as proposed or unknown.'
 texts={'fit':('A1 · FIT · 1 POINT','What problem governs the decision?',a['fit']),'measure':('A2 · '+a['step']+' · 1 POINT','Build the chapter artifact.',a['measure']),'bound':('A3 · BOUND · 1 POINT','Under what conditions does the claim hold?',a['bound']),'act':('A4 · ACT + EVIDENCE · 1 POINT','What action do you recommend now?',a['act'])}
 for field,(label,heading,prompt) in texts.items():
  sec=soup.select_one('#'+field).find_parent('section');lab=sec.select_one('.lab')
  if lab:lab.string=label
  headingel=sec.select_one('h2')
  if headingel:headingel.string=heading
  fl=sec.select_one('label[for="'+field+'"]')
  if fl:fl.string=heading
  ps=sec.find_all('p',recursive=False)
  for p in ps:
   if 'lab' not in p.get('class',[]):p.string=prompt;break
  soup.select_one('#'+field)['placeholder']=prompt
 # Field prompts may be attached to hints instead of direct paragraphs in the original template.
 for field,(_,heading,prompt) in texts.items():
  el=soup.select_one('#'+field);sec=el.find_parent('section')
  hints=[p for p in sec.find_all('p') if 'lab' not in p.get('class',[])]
  if hints:hints[0].string=prompt
  else:el.insert_before(BeautifulSoup('<p>'+prompt+'</p>','html.parser'))
 if soup.select_one('label[for="evidence"]'):soup.select_one('label[for="evidence"]').string='What evidence supports the action, and what still needs verification?'
 rows=soup.select('.rubric tbody tr') or soup.select('.rubric tr')[1:]
 criteria=[('FIT','Defines the chapter-specific problem accurately, distinguishes facts from assumptions and connects it to the proposed action.'),(a['step'],a['measurecrit']),('BOUND','States relevant operating assumptions, scope and an observable trigger to reconsider the claim.'),('ACT + EVIDENCE','Gives a feasible bounded action, named responsibility and inspectable evidence, while distinguishing completed from proposed verification.'),('REFIT','Explains how the new evidence affects the initial claim and justifies RETAIN, REVISE or REPLACE with a coherent final record.')]
 for row,(name,desc) in zip(rows,criteria):
  cells=row.find_all(['td','th']);contents(cells[0],name+' · 1 point');contents(cells[1],'<b>1:</b> '+desc+'<br><b>0.75:</b> Sound reasoning with one minor omission.<br><b>0.5:</b> Partly correct, with a consequential gap.<br><b>0:</b> Missing, materially incorrect or based on invented evidence.')
 for el in soup.find_all(['p','div']):
  if not el.find_all(['section','table','div']) and 'The increase from Assignment 1' in el.get_text():el.string='Five points use the same familiar structure. The chapter artifact changes; the LMS determines how assignment points contribute to the course grade.'
 align=next((d for d in soup.find_all('details') if 'ETEC' in d.get_text() or 'جاهزية' in d.get_text()),None)
 if align:contents(align,'<summary>Learning-outcome alignment</summary><p>This task supports supplied syllabus CLO '+', '.join(map(str,C[n]['clo']))+'. It practises disciplinary knowledge, engineering skills and accountable decisions. It is course-written practice, not an official national readiness assessment or an approved item-weight mapping.</p>')
 for li in soup.select('.flow li'):
  if 'MEASURE' in li.get_text():li.string='FIT → '+a['step']+' → BOUND → ACT + EVIDENCE'
 version=f'2026-09-ch{n}-path-v1';key=f'fbr:cpit455:ch{n}:path:v1';access=f'fbr:access:ch{n}:path:v1';reveal=f'reveal/r{n}-path-v1.json'
 script=oldscript.replace("chapter:'11'",f"chapter:'{n}'").replace("title:'Reliability Engineering'",'title:'+json.dumps(title)).replace("version:'2026-09-assignment2-v1'",f"version:'{version}'").replace("scenarioTitle:'University payment authorization · teaching simulation'",'scenarioTitle:'+json.dumps(title+' · teaching simulation')).replace('fbr:cpit455:ch11:a2:v1',key).replace('fbr:access:ch11:a2:v1',access).replace('reveal/r11-a2-v1.json',reveal).replace("String(r.chapter)==='11'",f"String(r.chapter)==='{n}'").replace('chapter=11',f'chapter={n}')
 script=script.replace('Assignment 2',f'Assignment {i}').replace('Chapter 11',f'Chapter {n}').replace('Reliability Engineering',title).replace('CPIT455_A2_CH11_',f'CPIT455_A{i}_CH{n}_').replace('Final reliability decision','Final engineering decision').replace('FINAL RELIABILITY DECISION','FINAL ENGINEERING DECISION').replace('Metric/requirement and conditions','Artifact, requirements and conditions')
 script=script.replace("x.toUpperCase()","(x==='measure'?"+json.dumps(a['step'])+":x.toUpperCase())")
 # Same commit/reveal behavior, task-specific stress question and final record.
 script=script.replace('What STRESS changes…',a['refit'])
 sc=soup.new_tag('script');sc.string=script;soup.body.append(sc)
 filename=f'lectures/iscarb/Ch{n}-FBR-Student-Assignment.html'
 final=str(soup).replace('One simple calculation is required.','Use a small table or clear notation for the chapter artifact.').replace('supporting your metric/mechanism','supporting your artifact and mechanism').replace('MEASURE',a['step']).replace('calculation and reasoning','artifact and reasoning').replace('final reliability','final engineering')
 (ROOT/filename).write_text(final)
 (ROOT/'lectures/iscarb'/reveal).write_text(json.dumps({'chapter':str(n),'version':version,'label':'STRESS · new evidence','text':a['stress']},indent=2))
 records.append(dict(chapter=n,path=filename,stress_path='lectures/iscarb/'+reveal,edition=f'chapter{n}-path-v1',version=version,storage_key=key,access_key=access,points=5,artifact=a['artifact']))
 gateway[str(n)]=dict(chapter=str(n),ey=f'Chapter {n} · After class · Assignment {i}',title=a['title'],intro='Apply '+title.lower()+' in a fictional transfer case. '+a['artifact']+'.',time=a['minutes']+' minutes',points='5 points',access=access,edition=f'chapter{n}-path-v1',assignment=filename,lecture=f'lectures/iscarb/Ch{n}-{slug}.html',steps=['Try the short ungraded warm-up.','Record FIT → '+a['step']+' → BOUND → ACT + EVIDENCE.','Commit Part A, then review the new STRESS evidence.','Defend RETAIN, REVISE or REPLACE; disclose AI use, review and export your work for the LMS.'],note='The workflow stays familiar. This chapter practises '+a['artifact'].lower()+'. Completing fields is not an automatic grade.',ack='I will record my initial decision before revealing new evidence and explain my own reasoning.',commit='Part A is saved and frozen before STRESS appears. Part B remains editable. This is a teaching sequence, not secure examination software or LMS submission.')
 print('CH',n,a['step'],len(script))
(ROOT/'curriculum/learning-path/assignments.json').write_text(json.dumps(records,indent=2))
(ROOT/'curriculum/learning-path/gateway.json').write_text(json.dumps(gateway,indent=2))
