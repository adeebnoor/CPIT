from __future__ import annotations

import shutil
import unittest
from pathlib import Path
from zipfile import ZipFile

from pypdf import PdfReader

from app.cimt_native_v43 import export_cimt_presenter_pdf_v43, export_cimt_presenter_pptx_v43
from app.source_visuals_v42 import plans_for_blueprint_v42
from tests.v43_fixture import make_blueprint


class ArchivedCIMTRegressionTests(unittest.TestCase):
    """Keep the learner-facing renderer tied to the real CPIT-455 CIMT archive.

    Synthetic fixtures are useful for deterministic layout tests, but they cannot
    prove that the renderer actually preserves an information-bearing source
    figure. This regression uses the archived Dependable Systems lecture that is
    published in the same repository and verifies that source-native teaching
    visuals survive into both presenter exports.
    """

    def test_real_dependable_systems_source_visuals_survive_presenter_exports(self):
        repo_root = Path(__file__).resolve().parents[2]
        source = repo_root / "lectures" / "cimt" / "CPIT455-class2-NooR.pdf"
        self.assertTrue(source.exists(), source)

        upload_dir = repo_root / "iscarb-studio" / "data" / "uploads" / "_archived_cimt_qa"
        upload_dir.mkdir(parents=True, exist_ok=True)
        uploaded = upload_dir / "P1__CPIT455-class2-NooR.pdf"
        shutil.copy2(source, uploaded)

        bp = make_blueprint()
        bp.source_manifest = ["[P1] PRIMARY: CPIT455-class2-NooR.pdf"]

        # These mappings are deliberately grounded in the preserved CIMT deck,
        # not invented by the fixture: overview/take-home, properties, cost curve,
        # sociotechnical stack, redundancy/diversity, and dependable-process table.
        source_slides = {2: 3, 5: 5, 6: 6, 7: 8, 9: 9, 10: 10}
        for unit in bp.units:
            slide_no = source_slides.get(unit.number)
            unit.source_anchor = f"[P1] SLIDE {slide_no}" if slide_no else ""

        try:
            plans = plans_for_blueprint_v42(bp)
            selected = {u.number: p.source_slide for u, p in zip(bp.units, plans) if p.reuse_mode == "USE"}
            for unit_no, slide_no in source_slides.items():
                self.assertEqual(selected.get(unit_no), slide_no, (unit_no, selected))

            out = Path("/tmp/iscarb-v43-qa")
            out.mkdir(parents=True, exist_ok=True)
            pptx = out / "Dependable_Systems_CIMT_RealSource_v43.pptx"
            pdf = out / "Dependable_Systems_CIMT_RealSource_v43.pdf"
            export_cimt_presenter_pptx_v43(bp, pptx)
            export_cimt_presenter_pdf_v43(bp, pdf)

            self.assertGreater(pptx.stat().st_size, 250_000)
            self.assertGreater(pdf.stat().st_size, 100_000)
            self.assertEqual(len(PdfReader(str(pdf)).pages), 20)
            with ZipFile(pptx) as zf:
                slides = [n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
                media = [n for n in zf.namelist() if n.startswith("ppt/media/")]
                self.assertEqual(len(slides), 20)
                self.assertGreaterEqual(len(media), 6)
        finally:
            shutil.rmtree(upload_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
