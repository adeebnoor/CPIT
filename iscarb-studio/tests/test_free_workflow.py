"""A zero-API authoring loop must be real, source-preserving and audit-honest."""
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.free_workflow import resolve_mode, FREE_MODEL
from app.gemini_service import GeminiService, GeminiQuotaPaused
from tests.test_quota_failover import service_for, quota, request
from tests.test_v44_release import ROOT, LECTURE, source


def test_no_api_is_the_default_and_arbitrary_models_are_rejected():
    assert resolve_mode("") == "source-only"
    assert resolve_mode("source-only") == "source-only"
    for mode in ("free", "auto", "gemini-3.6-flash", "gemini-3.5-flash", FREE_MODEL):
        assert resolve_mode(mode) == "free"
    with pytest.raises(ValueError):
        resolve_mode("paid-only-model")


def test_free_mode_never_fans_out_after_quota_or_stage_preference():
    service = service_for([quota()])
    service.model = "free"
    assert service._models_for("gemini-3.7-flash") == [FREE_MODEL]
    with pytest.raises(GeminiQuotaPaused):
        request(service)
    with pytest.raises(RuntimeError, match="quota is exhausted"):
        request(service)
    service.client.models.generate_content.assert_called_once()
    assert service.client.models.generate_content.call_args.kwargs["model"] == FREE_MODEL


def test_upload_quota_is_not_repeated_in_later_stages(tmp_path):
    service = service_for([])
    service._uploaded = {}
    service.client.files = SimpleNamespace(upload=Mock(side_effect=quota()))
    for path in (tmp_path / "P1.pdf", tmp_path / "S1.pdf"):
        with pytest.raises(GeminiQuotaPaused, match="source upload"):
            service._upload(path)
    service.client.files.upload.assert_called_once()
    service._backoff.assert_not_called()


def test_free_profile_is_local_and_quota_is_actionable(source):
    from app import main
    from app.models import JobState
    from app.source_bundle import SourceBundle, SourceItem
    job = JobState(id="a" * 32, status="queued", progress=0, message="")
    bundle = SourceBundle([SourceItem("primary", "P1", LECTURE.name, LECTURE)])
    with patch.object(main, "load_job", return_value=job), patch.object(main, "save_job"), patch.object(main, "prune_expired"), patch.object(main, "GeminiService") as remote:
        remote.return_value.partial_blueprint = None
        remote.return_value.generate_blueprint.side_effect = GeminiQuotaPaused("source upload")
        main._compile(job.id, bundle, "free", 1)
        remote.return_value.profile_source.assert_not_called()
        remote.return_value.generate_blueprint.assert_called_once()
    assert job.status == "blocked" and "FREE-TIER LIMIT" in job.message
    assert not job.audit.overall_pass
    assert "locally to save" in job.source_profile.source_warnings[0]


def test_served_free_workflow_keeps_source_and_runs_checks_without_api():
    # Legacy bootstrap mutates shared app objects; verify the served app in a
    # clean process and temporary storage, not against a stale imported route.
    code = r'''
import io, tempfile, json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
import pymupdf
from pptx import Presentation
from app import start_v440 as live, storage, free_workflow
source=Path('../lectures/cimt/CPIT455-class2-NooR.pdf').resolve().read_bytes()
with tempfile.TemporaryDirectory() as td:
    root=Path(td); uploads=root/'uploads'; uploads.mkdir(); jobs=root/'jobs'; jobs.mkdir(); exports=root/'exports'; exports.mkdir()
    with patch.object(storage,'JOBS',jobs), patch.object(live.engine,'UPLOADS',uploads), patch.object(live,'UPLOADS',uploads), patch.object(free_workflow,'UPLOADS',uploads), patch.object(live.engine,'EXPORTS',exports), patch.object(live.engine,'prune_expired'), patch.object(live.engine,'GeminiService') as remote, patch.object(live.engine.executor,'submit',side_effect=lambda fn,*args:fn(*args)):
        c=TestClient(live.app)
        h=c.get('/api/health').json(); assert h['default_model']=='source-only' and h['default_api_calls']==0
        assert c.post('/api/compile',data={'model':'paid-model'}).status_code==400
        assert c.post('/api/compile',data={'model':'free'}).status_code==400
        response=c.post('/api/compile',files={'primary_lecture':('source.pdf',source,'application/pdf')})
        assert response.status_code==200,response.text
        jid=response.json()['job_id']; base='/api/jobs/'+jid
        job=c.get(base).json(); assert job['status']=='blocked' and job['model']=='source-only'
        assert len(job['blueprint']['units'])==20 and not job['audit']['overall_pass']
        prompt=c.get(base+'/authoring-prompt')
        assert prompt.status_code==200 and 'attachment' in prompt.headers['content-disposition']
        for text in ('OUTPUT JSON SCHEMA','P1-P11','Refinement-based','20','REVIEW DRAFT'):
            assert text in prompt.text,text
        bp=job['blueprint']; bp['lecture_title']='Faculty-edited dependable systems'; bp['source_manifest']=['Untrusted replacement']
        imported=c.post(base+'/import-blueprint',files={'blueprint_file':('edited.json',json.dumps(bp),'application/json')})
        assert imported.status_code==200,imported.text
        new_id=imported.json()['job_id']; assert new_id!=jid
        new_base='/api/jobs/'+new_id; edited=c.get(new_base).json()
        assert edited['blueprint']['lecture_title']==bp['lecture_title']
        assert edited['blueprint']['source_manifest']==job['source_manifest']
        assert edited['source_profile']==job['source_profile']
        assert edited['status']=='blocked' and not edited['audit']['overall_pass']
        assert edited['deterministic_checks'] and 'v15_complete_20_unit_grammar' in edited['deterministic_checks']
        assert c.get(base).json()['blueprint']['lecture_title']!='Faculty-edited dependable systems'
        assert c.get(new_base+'/export/source-pdf').content==source
        assert c.get(new_base+'/authoring-prompt').status_code==200
        # Both drafts retain all source figures and produce readable 20-page
        # review exports for this representative source.
        for prefix in (base,new_base):
            response=c.get(prefix+'/export/presenter-pdf')
            assert response.status_code==200,response.text
            doc=pymupdf.open(stream=response.content,filetype='pdf'); assert len(doc)==20
            assert 'REVIEW DRAFT' in doc[0].get_text()
            for page in doc:
                assert all(x0>=0 and y0>=0 and x1<=page.rect.width+1 and y1<=page.rect.height+1 for x0,y0,x1,y1,*_ in page.get_text('words'))
            ppt=c.get(prefix+'/export/pptx'); assert ppt.status_code==200,ppt.text
            assert len(Presentation(io.BytesIO(ppt.content)).slides)==20
        duplicate=json.loads(json.dumps(bp)); duplicate['units'][1]['number']=1
        assert c.post(base+'/import-blueprint',files={'blueprint_file':('bad.json',json.dumps(duplicate),'application/json')}).status_code==400
        assert c.post(base+'/import-blueprint',files={'blueprint_file':('bad.json','{}','application/json')}).status_code==400
        (uploads/jid/'P1__source.pdf').unlink()
        assert c.get(base+'/authoring-prompt').status_code==409
        assert c.get(new_base+'/authoring-prompt').status_code==200
        remote.assert_not_called()
print('Free source -> prompt -> import -> local gates -> PDF/PPTX: PASS; API calls=0')
'''
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
