"""Never ship a clipped review artifact merely because release is blocked."""
from unittest.mock import patch
import pytest
from app.presenter_v44 import (
    PresenterLayoutError, preflight_layout, export_presenter_pdf,
    export_presenter_pptx, render_presenter_preview, text_layout,
)
from tests.test_v44_release import source


@pytest.mark.parametrize("exporter", [export_presenter_pdf, export_presenter_pptx])
def test_overflow_is_rejected_before_creating_a_file(source, tmp_path, exporter):
    _, original = source
    bp = original.model_copy(deep=True)
    bp.units[5].core_content = ["Complete source statement. " * 3000]
    bp.units[5].pedagogy_content = []
    path = tmp_path / "must-not-exist"
    with patch("app.presenter_v44.plans_for_blueprint_v42", return_value=[None]*20):
        with pytest.raises(PresenterLayoutError, match="units 6"):
            exporter(bp, path)
    assert not path.exists()


@pytest.mark.parametrize("field", ["core_content", "title"])
def test_preview_uses_the_same_horizontal_overflow_guard(source, field):
    _, original = source
    bp = original.model_copy(deep=True)
    setattr(bp.units[5], field, ["X" * 2000] if field == "core_content" else "X" * 2000)
    with patch("app.presenter_v44.plans_for_blueprint_v42", return_value=[None]*20):
        with pytest.raises(PresenterLayoutError, match="units 6"):
            render_presenter_preview(bp)


def test_dense_spacing_preserves_every_label_and_statement():
    items = [(f"Source item {n}", "A complete technical statement with all its source detail preserved.") for n in range(30)]
    blocks, _, fits = text_layout(items)
    assert fits
    rendered = " ".join(" ".join(b.lines) for b in blocks)
    for label, body in items:
        assert label in rendered and body in rendered
    assert all(b.y + len(b.lines)*b.size*1.22 <= 444 for b in blocks)


def test_source_fragment_packing_never_drops_words_or_crosses_labels():
    from app.presenter_v44 import compact_source_fragments
    items = [("", f"Source fragment number {n}") for n in range(20)]
    items.insert(8, ("IMPORTANT EXAMPLE", "All original example details remain intact."))
    packed = compact_source_fragments(items)
    assert len(packed) < len(items)
    assert ("IMPORTANT EXAMPLE", "All original example details remain intact.") in packed
    text = " ".join(body for _, body in packed)
    assert all(body in text for _, body in items)


def test_production_api_reports_layout_repair_instead_of_server_error():
    import subprocess, sys
    code = '''from fastapi.testclient import TestClient
from app.start_v440 import app
from app.presenter_v44 import PresenterLayoutError
@app.get('/test-layout-rejection')
def rejected():
    raise PresenterLayoutError('Presenter cannot fit units 6')
r=TestClient(app).get('/test-layout-rejection')
assert r.status_code==422
assert r.json()['code']=='presenter_layout_requires_repair'
'''
    subprocess.run([sys.executable, '-c', code], check=True, capture_output=True, text=True, timeout=30)
