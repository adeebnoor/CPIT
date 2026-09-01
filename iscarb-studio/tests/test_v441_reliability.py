"""Regressions from the first real v4.4 production lecture."""
import time
from unittest.mock import patch
import pytest

from app.gemini_service import GeminiService, is_transient_model_failure
from app.gate_v15 import _unit5_contract, _teaching_contract
from app.models import JobState
from app.presenter_v44 import teaching_items
from tests.test_v44_release import source, LECTURE


def test_timeout_is_an_outage_not_a_programming_error():
    assert is_transient_model_failure(TimeoutError("request exceeded deadline"))
    assert not is_transient_model_failure(AttributeError("missing units"))


def test_exhausted_job_budget_never_starts_another_request():
    service=object.__new__(GeminiService)
    service._deadline=time.monotonic()-1
    with pytest.raises(TimeoutError):
        service._remaining_seconds()


def test_unit10_review_does_not_require_invented_primary_claims(source):
    _,bp=source
    u=bp.units[9].model_copy(deep=True)
    u.core_content=[]
    u.source_anchor=''
    assert _teaching_contract(u)
    u.pedagogy_content=['Known', 'Unknown', 'Monitor']
    assert not _teaching_contract(u)


def test_prediction_in_visible_first_step_counts(source):
    _,bp=source
    u=bp.units[4].model_copy(deep=True)
    u.engineering_question='How will the system behave under these constraints?'
    assert _unit5_contract(u)
    u.pedagogy_content=['PREDICT:', 'CONSTRAINT:', 'DERIVE:', 'NAME:']
    assert not _unit5_contract(u)


def test_opening_and_prediction_never_lose_source_explanation(source):
    _,bp=source
    for i in [0,4]:
        u=bp.units[i].model_copy(deep=True)
        u.core_content=['A complete source fact that must remain visible.']
        assert any('complete source fact' in body for _,body in teaching_items(bp,u))


def test_source_only_finishes_without_model_and_preserves_every_checkpoint(source):
    from app import main
    from app.source_bundle import SourceBundle,SourceItem
    _,bp=source
    bundle=SourceBundle(items=[SourceItem('primary','P1',LECTURE.name,LECTURE,LECTURE.name)],lecture_focus='',session_minutes=90)
    saved=[]
    job=JobState(id='source-only-test',status='queued',progress=0,message='')
    with patch.object(main,'load_job',return_value=job), patch.object(main,'save_job',side_effect=lambda j:saved.append(j.model_copy(deep=True))), patch.object(main,'GeminiService') as remote, patch.object(main,'prune_expired'):
        main._compile(job.id,bundle,'source-only',0)
    remote.assert_not_called()
    assert job.status=='blocked' and job.progress==100
    assert len(job.blueprint.units)==20
    assert not job.audit.overall_pass
    assert all(any(r.coverage_id==x.id for r in job.blueprint.coverage_ledger) for x in job.source_profile.coverage_items if x.importance=='major')
    assert any(j.blueprint for j in saved)


def test_active_audit_exports_a_review_snapshot_and_original_source():
    # Bootstrap in isolation: legacy releases share and mutate the app object.
    import subprocess,sys
    from tests.test_v44_release import ROOT
    code='''
import io,tempfile,shutil
from pathlib import Path
from unittest.mock import patch
import pymupdf
from pptx import Presentation
from fastapi.testclient import TestClient
from app import start_v440 as live
from app.models import JobState
from app.source_bundle import SourceBundle,SourceItem
from app.source_profile_fallback import build_deterministic_source_profile
from app.deterministic_blueprint_fallback import build_deterministic_blueprint
source=Path('../lectures/cimt/CPIT455-class2-NooR.pdf').resolve()
bundle=SourceBundle(items=[SourceItem('primary','P1',source.name,source,source.name)],lecture_focus='',session_minutes=90)
bp=build_deterministic_blueprint(build_deterministic_source_profile(bundle))
job=JobState(id='qa',status='auditing',progress=70,message='Review running',blueprint=bp)
with tempfile.TemporaryDirectory() as td:
    root=Path(td); (root/'qa').mkdir()
    shutil.copyfile(source,root/'qa'/'P1__source.pdf')
    with patch.object(live,'UPLOADS',root),patch.object(live.engine,'load_job',return_value=job),patch.object(live.engine,'EXPORTS',root):
        c=TestClient(live.app)
        pdf=c.get('/api/jobs/qa/export/presenter-pdf')
        assert pdf.status_code==200
        doc=pymupdf.open(stream=pdf.content,filetype='pdf')
        assert len(doc)==20
        assert 'REVIEW DRAFT' in doc[0].get_text()
        for page in doc:
            assert all(x0>=0 and y0>=0 and x1<=page.rect.width+1 and y1<=page.rect.height+1 for x0,y0,x1,y1,*_ in page.get_text('words'))
        ppt=c.get('/api/jobs/qa/export/pptx')
        assert ppt.status_code==200 and len(Presentation(io.BytesIO(ppt.content)).slides)==20
        original=c.get('/api/jobs/qa/export/source-pdf')
        assert original.content==source.read_bytes()
        assert not list(root.glob('*Visual_Presenter.*')) # response cleanup
'''
    subprocess.run([sys.executable,'-c',code],cwd=ROOT,check=True,capture_output=True,text=True,timeout=90)
