from __future__ import annotations

import json
import sys
from pathlib import Path

from app.models import Blueprint


TIMES = [4,4,3,4,5,6,7,6,6,5,5,5,5,5,5,4,3,3,3,2]


def make_blueprint() -> Blueprint:
    phases = {**{i:'IFHAM' for i in range(1,6)}, **{i:'MARIS' for i in range(6,11)}, **{i:'ATQAN' for i in range(11,16)}, **{i:'MAYYIZ' for i in range(16,21)}}
    knowledge = {1:'SYSTEM_BEHAVIOR',2:'CONCEPT',3:'CONCEPT',4:'CONCEPT',5:'CONCEPT',6:'TRADE_OFF',7:'ARCHITECTURE',8:'TRADE_OFF',9:'DESIGN_PRINCIPLE',10:'PROCESS',11:'CONCEPT',12:'PROCESS',13:'TRADE_OFF',14:'SYSTEM_BEHAVIOR',15:'PROCESS',16:'ARCHITECTURE',17:'TRADE_OFF',18:'PROCESS',19:'CONCEPT',20:'CONCEPT'}
    titles = {
        1:'The Infusion Pump Failure Crisis',2:'Dependable Systems Domain Spine',3:'Course Learning Outcomes',4:'H-Stack Competencies',5:'First-Principles Dependability',
        6:'Economics of Dependability',7:'Sociotechnical Systems Stack',8:'Regulation and Compliance Trade-offs',9:'Redundancy and Diversity',10:'Dependable Process Review',
        11:'Saudi Operating Context',12:'Accountability and Traceability',13:'Agility and Dependable Processes',14:'Practitioner Workload',15:'Critical AI Literacy',
        16:'Dependability Portfolio',17:'Constraint Mutation',18:'Evidence Policy',19:'Capability Rubric',20:'Bounded Assurance Verdict'
    }
    units=[]
    for i in range(1,21):
        core=[] if i in {3,4,11,14,18,19,20} else [f'[P1] Dependable Systems mechanism for unit {i}', f'[P1] Evidence boundary for unit {i}']
        ped=[f'Engineering decision scaffold for unit {i}']
        if i==14:
            ped=['Identify avoidable cognitive burden introduced by the operating design.']
        if i==15:
            ped=['AI MAY ASSIST — draft or compare candidate reasoning.','AI MUST NOT BE TRUSTED AUTONOMOUSLY — human engineer owns source checking, testing, and final sign-off.']
        if i==18:
            ped=['Claim','Evidence','Warrant','Counter-evidence','Residual uncertainty']
        if i==20:
            ped=['State residual uncertainty before the final bounded verdict.']
        assumptions=['HYPOTHETICAL SAUDI SCENARIO — no national mandate is asserted as fact.'] if i==11 else []
        units.append({
            'number':i,'phase':phases[i],'title':titles[i],
            'engineering_question':f'What dependable-systems decision is required in unit {i}?',
            'core_content':core,'pedagogy_content':ped,'enrichment_content':[],'enrichment_basis':[],
            'scenario_assumptions':assumptions,'knowledge_types':[knowledge[i]],
            'visual_suggestion':'CIMT-native source-first visualization',
            'visual_plan':{'visual_type':f'dependable-{i}','teaching_purpose':'Make the dependable-systems decision visible.','source_visual_available':False,'source_page_or_slide':'','source_url':'','reuse_mode':'REDRAW' if core else 'NEW','citation':'[P1] source-anchored redraw' if core else 'ISCARB visualization','focal_elements':['dependability'],'annotation_plan':[],'visual_evidence_role':'decision support'},
            'student_action':f'Defend the dependable-systems decision for unit {i}.',
            'takeaway':f'Dependability decision {i} is bounded by evidence and uncertainty.',
            'cimtlens':['C'],'clo_ids':['CLO1'],'source_anchor':'[P1] SLIDE 10' if core else '',
            'inherited_requirements':[],'elite_requirements':[],'evidence':f'Decision evidence {i}',
            'contextual_enrichment':False,'verify_before_release':False,'planned_minutes':TIMES[i-1]
        })
    return Blueprint.model_validate({
        'lecture_title':'Chapter 10 — Dependable Systems',
        'engineering_thesis':'Dependability is achieved through bounded engineering mechanisms and evidence.',
        'central_engineering_crisis':'A critical infusion pump shows interacting hardware, software and operational failures.',
        'named_ethical_purpose':'Professional responsibility for dependable operation.',
        'clos':[{'id':f'CLO{i}','statement':f'Analyze dependable-systems capability {i}','evidence_expected':f'Dependability evidence {i}'} for i in range(1,6)],
        'units':units,
        'source_topic_families':['Dependability properties','Sociotechnical systems','Redundancy and diversity','Dependable processes','Formal methods and dependability'],
        'topic_coverage':[{'topic_family':'Dependability properties','source_anchor':'[P1] SLIDES 8-11','first_taught_unit':2,'reinforced_units':[5,16]}],
        'coverage_ledger':[{'coverage_id':'P1-C1','label':'Dependability properties','knowledge_type':'CONCEPT','source_anchor':'[P1] SLIDES 8-11','first_taught_unit':2,'reinforced_units':[5,16],'depth':'DEEP','representation':'domain spine'}],
        'readiness_alignment':[{'gku':'GKU3','sku':'SKU3.1','slo_refs':['SLO3.1.2'],'klo_refs':['KLO2'],'strength':'supporting','rationale':'Dependability analysis evidence','atomicity_evidence':'Unit 16 portfolio evidence','clo_ids':['CLO1'],'evidence_units':[16],'standard_source_pages':[19]}],
        'rubric_criteria':[{'criterion':f'Criterion {i}','distinguished':'Evidence-rich and bounded','ready':'Supported','developing':'Partial','not_yet_ready':'Unsupported','readiness_refs':['SKU3.1']} for i in range(1,7)],
        'release_notes':[],'session_minutes':90,'source_manifest':['[P1] PRIMARY: Dependable Systems'],'deferred_topics':[]
    })


if __name__ == '__main__':
    path = Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/iscarb-v43-blueprint.json')
    path.write_text(make_blueprint().model_dump_json(by_alias=True, indent=2), encoding='utf-8')
    print(path)
