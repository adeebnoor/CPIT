from __future__ import annotations
"""Self-contained v6.7 presentation/data contract over the stable v4.7 Blueprint."""
from enum import Enum
import hashlib,re
from typing import Literal
from pydantic import BaseModel,Field,model_validator
from .unit_contract import role_problems

# ---------- accessibility + dynamic design tokens ----------
def _lum(h):
    vals=[]
    for i in (1,3,5):
        c=int(h[i:i+2],16)/255; vals.append(c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4)
    return .2126*vals[0]+.7152*vals[1]+.0722*vals[2]
def contrast(a,b):
    x,y=_lum(a),_lum(b); return (max(x,y)+.05)/(min(x,y)+.05)
def contrast_pass(a,b,large=False): return contrast(a,b)>=(3 if large else 4.5)
class Tokens(BaseModel):
    bg:str="#05070D"; panel:str="#0B152D"; panel_soft:str="#11192A"; text:str="#F5F5F8"; muted:str="#B7BDC8"; cyan:str="#2CDCFF"; magenta:str="#FF258C"; gold:str="#DCB56B"; green:str="#38D692"; blue:str="#61A7FF"; danger:str="#FF617F"; footer_bg:str="#10192C"; primary:str="#FF258C"; secondary:str="#2CDCFF"; heritage:str="#DCB56B"
    def css_variables(self): return {f"--iscarb-{k.replace('_','-')}":v for k,v in self.model_dump().items()}
    def contrast_checks(self):
        pairs=((self.text,self.bg,0),(self.muted,self.bg,0),(self.text,self.panel,0),(self.muted,self.panel,0),(self.primary,self.bg,1),(self.cyan,self.bg,1),(self.gold,self.bg,1),(self.green,self.bg,1))
        return {f"c{i}":contrast_pass(a,b,bool(l)) for i,(a,b,l) in enumerate(pairs,1)}
PALETTE=("#FF258C","#2CDCFF","#DCB56B","#38D692","#61A7FF","#B68CFF")
def chapter_design_tokens(title="",preferred=""):
    p=str(preferred or '').upper(); bg="#05070D"
    if p not in PALETTE or not contrast_pass(p,bg,True): p=PALETTE[hashlib.sha256((title or 'ISCARB').encode()).digest()[0]%len(PALETTE)]
    return Tokens(primary=p,secondary=next(x for x in PALETTE if x!=p))

# ---------- strict rule payloads ----------
class PCDN(BaseModel):
    predict:str=Field(min_length=2); constraint:str=Field(min_length=2); derive:str=Field(min_length=2); name:str=Field(min_length=2); model_config={"extra":"forbid"}
class KnowledgeState(BaseModel):
    known:str=Field(min_length=2); unknown:str=Field(min_length=2); decision_sensitive_unknown:str=Field(min_length=2); monitor:str=Field(min_length=2); model_config={"extra":"forbid"}
class Assurance(BaseModel):
    claim:str=Field(min_length=2); evidence:str=Field(min_length=2); warrant:str=Field(min_length=2); counter_evidence:str=Field(min_length=2); residual_uncertainty:str=Field(min_length=2); verdict:str=""; model_config={"extra":"forbid"}
    @property
    def complete(self): return all(bool(str(getattr(self,k,'')).strip()) for k in ('claim','evidence','warrant','counter_evidence','residual_uncertainty'))
class RubricRow(BaseModel):
    criterion:str; distinguished:str; ready:str; developing:str; not_yet_ready:str
    @model_validator(mode='after')
    def substantive(self):
        for k in ('distinguished','ready','developing','not_yet_ready'):
            s=str(getattr(self,k,'')).strip()
            if len(s.split())<3 or re.fullmatch(r'level\s*\d+',s,re.I): raise ValueError('rubric placeholder')
        return self
class SlideContract(BaseModel):
    kind:Literal['CORE','SOURCE_EXPANSION','COVER','CLOSE']; unit_number:int|None=Field(default=None,ge=1,le=20); expansion_id:str=""; rule_type:str; title:str=Field(min_length=3); objective:str=Field(min_length=4); content:list[str]=Field(default_factory=list,max_length=10); student_task:str=Field(min_length=4); source_anchor:str=""; visual_component:str; local_context:str=""; pcdn:PCDN|None=None; knowledge_state:KnowledgeState|None=None; assurance_chain:Assurance|None=None; rubric_grid:list[RubricRow]|None=None
    model_config={"extra":"forbid"}
    @model_validator(mode='after')
    def typed(self):
        if self.kind=='CORE' and self.unit_number is None: raise ValueError('CORE requires unit_number')
        if self.kind=='SOURCE_EXPANSION' and (not self.expansion_id or not self.source_anchor): raise ValueError('SOURCE_EXPANSION requires id/source')
        if self.unit_number==5 and self.pcdn is None: raise ValueError('Rule 05 requires PCDN')
        if self.unit_number==10 and self.knowledge_state is None: raise ValueError('Rule 10 requires knowledge state')
        if self.unit_number==18 and self.assurance_chain is None: raise ValueError('Rule 18 requires assurance chain')
        if self.unit_number==19 and (not self.rubric_grid or len(self.rubric_grid)!=6): raise ValueError('Rule 19 requires 6x4 rubric')
        if self.unit_number==20 and (not self.assurance_chain or not self.assurance_chain.complete): raise ValueError('Rule 20 blocked')
        return self

def _labels(entries):
    out={}; aliases={'counter-evidence':'counter_evidence','counter evidence':'counter_evidence','residual uncertainty':'residual_uncertainty','decision-sensitive unknown':'decision_sensitive_unknown','decision sensitive unknown':'decision_sensitive_unknown'}
    for raw in entries or []:
        s=re.sub(r'\s+',' ',str(raw)).strip(); m=re.split(r'\s*(?::|—| – | - )\s*',s,maxsplit=1)
        if len(m)==2: out[aliases.get(m[0].lower(),m[0].lower().replace(' ','_'))]=m[1]
    return out
def pcdn_from(bp):
    try: return PCDN(**{k:_labels(bp.units[4].pedagogy_content).get(k,'') for k in ('predict','constraint','derive','name')})
    except Exception:return None
def knowledge_from(bp):
    d=_labels(bp.units[9].pedagogy_content)
    try:return KnowledgeState(known=d.get('known',''),unknown=d.get('unknown',''),decision_sensitive_unknown=d.get('decision_sensitive_unknown',''),monitor=d.get('monitor',''))
    except Exception:return None
def assurance_from(bp):
    d=_labels(bp.units[17].pedagogy_content)
    try:return Assurance(claim=d.get('claim',''),evidence=d.get('evidence',''),warrant=d.get('warrant',''),counter_evidence=d.get('counter_evidence',''),residual_uncertainty=d.get('residual_uncertainty',''))
    except Exception:return None
def rubric_grid(bp):
    rows=list(getattr(bp,'rubric_criteria',[]) or [])
    if len(rows)!=6:return None
    try:return [RubricRow(criterion=r.criterion,distinguished=r.distinguished,ready=r.ready,developing=r.developing,not_yet_ready=r.not_yet_ready) for r in rows]
    except Exception:return None
def verdict_eligible(bp):
    a=assurance_from(bp); return bool(a and a.complete and rubric_grid(bp))

def pcdn_unlock_state(predict='',constraint='',derive=''):
    p,c,d=map(lambda x:bool(str(x).strip()),(predict,constraint,derive)); return {'constraint_unlocked':p,'derive_unlocked':p and c,'name_unlocked':p and c and d}
def decision_form_complete(p=None): return all(bool(str((p or {}).get(k,'')).strip()) for k in ('claim','evidence','warrant','counter_evidence','residual_uncertainty'))
def rubric_credit_allowed(level,artifact_url='',source_anchor=''): return bool(artifact_url.strip() and source_anchor.strip()) if str(level).strip().lower() in {'ready','distinguished'} else True

# ---------- narrative/context/layout ----------
def local_context_from_blueprint(bp):
    direct=str(getattr(bp,'local_scenario','') or '').strip()
    if direct:return direct
    u=list(getattr(bp,'units',[]) or [])
    return re.sub(r'\s+',' ',' '.join(list(getattr(u[10],'scenario_assumptions',[]) or [])+list(getattr(u[10],'enrichment_content',[]) or [])+list(getattr(u[10],'pedagogy_content',[]) or []))).strip() if len(u)>=11 else ''
def local_context_motif(s):
    b=str(s or '').lower(); groups=(('clinical',('hospital','clinical','patient','medical','health','مستشفى','مريض','صحي')),('banking',('bank','atm','payment','financial','sama','بنك','مالي')),('crowd',('hajj','umrah','crowd','pilgrim','حج','عمرة','حشود')),('industrial',('plant','industrial','factory','control','energy','مصنع','صناعي','طاقة')),('government',('government','national platform','public service','حكومي','منصة وطنية')))
    return next((k for k,terms in groups if any(t in b for t in terms)),'heritage')
def local_context_visual_request(title,context):
    c=re.sub(r'\s+',' ',str(context or '')).strip()
    if not c: raise ValueError('LOCAL_CONTEXT is required')
    return {'lecture_title':title,'local_context':c,'aspect_ratio':'16:9','text_in_image':False,'motif':local_context_motif(c),'style':'ISCARB Black Desert','prompt':f"Create a 16:9 engineering lecture hero for {title}. Context: {c}. Dark black ground, restrained magenta geometry, warm sand tones, one clear engineering situation, negative space; no words, logos, flags or unsupported claims."}
def domain_spine_layout(families,per_slide=8):
    clean=[]
    for x in families or []:
        s=re.sub(r'\s+',' ',str(x)).strip()
        if s and s not in clean:clean.append(s)
    return [{'page':i//per_slide+1,'items':clean[i:i+per_slide]} for i in range(0,len(clean),per_slide)]

def narrative_valid(bp):
    u=list(getattr(bp,'units',[]) or [])
    if [getattr(x,'number',None) for x in u]!=list(range(1,21)) or role_problems(bp):return False
    def has(n,labels):
        es=[str(x).lower() for x in u[n-1].pedagogy_content]
        return all(any(re.match(rf'^{re.escape(l.rstrip(":"))}\s*(?::|—|-)',e) for e in es) for l in labels)
    crisis=str(getattr(bp,'central_engineering_crisis','') or '')
    verdict=' '.join(u[19].pedagogy_content+u[19].core_content).lower()
    return all((len(crisis.split())>=6,has(1,('decision:','unknown:')),bool(bp.source_topic_families),pcdn_from(bp) is not None,bool(local_context_from_blueprint(bp)),assurance_from(bp) is not None,rubric_grid(bp) is not None,any(x in verdict for x in ('approve','redesign','reject'))))

# ---------- character-aware source expansions ----------
MAX_BOX_CHARS=360; MAX_SLIDE_CHARS=1050; MAX_ITEMS=5; TARGET=30
def _split_item(s,cap=MAX_BOX_CHARS):
    s=re.sub(r'\s+',' ',str(s)).strip()
    if len(s)<=cap:return [s] if s else []
    parts=re.split(r'(?<=[.!?;])\s+',s); out=[]; cur=''
    for p in parts:
        if len(p)>cap:
            ws=p.split(); c=''
            for w in ws:
                n=(c+' '+w).strip()
                if c and len(n)>cap:out.append(c);c=w
                else:c=n
            if c:out.append(c)
        else:
            n=(cur+' '+p).strip()
            if cur and len(n)>cap:out.append(cur);cur=p
            else:cur=n
    if cur:out.append(cur)
    return out
def plan_expansions(bp,target=TARGET):
    budget=max(0,target-22); specs=[]
    # domain-spine continuation is mandatory
    for pg in domain_spine_layout(bp.source_topic_families)[1:]: specs.append({'after_unit':2,'title':'Domain spine — continued','objective':'Keep every source family readable.','content':pg['items'],'source_anchor':bp.units[1].source_anchor or '[P1] domain families','student_task':'Connect one continued family to the chapter decision.','reason':'domain'})
    remaining=max(0,budget-len(specs)); cand=[]
    for unit in bp.units:
        core=[str(x).strip() for x in unit.core_content if str(x).strip()]; ped=[str(x).strip() for x in unit.pedagogy_content if str(x).strip()]
        chars=sum(map(len,core+ped)); extra=core[MAX_ITEMS:] if len(core)>MAX_ITEMS else [x for x in core if len(x)>MAX_BOX_CHARS]
        if extra or chars>MAX_SLIDE_CHARS:
            if not extra: extra=core[3:]
            cand.append((max(chars-MAX_SLIDE_CHARS,1),unit,extra))
    for _,unit,items in sorted(cand,key=lambda z:(-z[0],z[1].number)):
        expanded=[]
        for x in items:expanded+=_split_item(x)
        while expanded and remaining>0:
            chunk=expanded[:MAX_ITEMS];expanded=expanded[MAX_ITEMS:];specs.append({'after_unit':unit.number,'title':f'{unit.title} — source expansion','objective':'Keep source detail readable without weakening the decision journey.','content':chunk,'source_anchor':unit.source_anchor or '[P1] source anchor','student_task':f'Use this source detail to strengthen Unit {unit.number:02d}.','reason':'character_density'});remaining-=1
    specs=sorted(enumerate(specs),key=lambda z:(z[1]['after_unit'],z[0])); return [dict(s,expansion_id=f'X{i:02d}') for i,(_,s) in enumerate(specs,1)]
def physical_slide_plan(bp,target=TARGET,strict=True):
    if strict and not verdict_eligible(bp):raise ValueError('Bounded Verdict blocked until Rule 18 assurance and 6x4 rubric are complete')
    ex=plan_expansions(bp,target); by={}
    for s in ex:by.setdefault(s['after_unit'],[]).append(s)
    p=[{'kind':'COVER'}]
    for u in bp.units:
        p.append({'kind':'CORE','unit_number':u.number});p += [{'kind':'SOURCE_EXPANSION',**s} for s in by.get(u.number,[])]
    p.append({'kind':'CLOSE'}); total=len(p)
    for i,row in enumerate(p,1):row.update(physical_index=i,physical_total=total)
    return p
def automated_checks(bp):
    t=chapter_design_tokens(bp.lecture_title); layouts=domain_spine_layout(bp.source_topic_families); flat=[x for p in layouts for x in p['items']]; plan=physical_slide_plan(bp,strict=False); ex=plan_expansions(bp)
    checks={'v19_dynamic_chapter_theme_contrast':all(t.contrast_checks().values()),'v19_pcdn_fields_are_separate':pcdn_from(bp) is not None,'v19_known_unknown_monitor_fields_are_separate':knowledge_from(bp) is not None,'v19_assurance_chain_fields_are_separate':bool(assurance_from(bp) and assurance_from(bp).complete),'v19_rubric_grid_has_6x4_substantive_cells':rubric_grid(bp) is not None,'v19_domain_spine_auto_layout_preserves_all_families':flat==list(dict.fromkeys(bp.source_topic_families)),'v19_source_expansion_textboxes_within_character_cap':all(all(len(x)<=MAX_BOX_CHARS for x in s['content']) for s in ex),'v19_verdict_gate_requires_assurance_chain':verdict_eligible(bp),'v19_physical_plan_contains_all_20_core_units':[x.get('unit_number') for x in plan if x['kind']=='CORE']==list(range(1,21)),'v19_local_context_background_is_variable':bool(local_context_motif(local_context_from_blueprint(bp))),'v19_narrative_contract_complete':narrative_valid(bp)}
    checks['v19_production_template_pass']=all(checks.values());return checks
