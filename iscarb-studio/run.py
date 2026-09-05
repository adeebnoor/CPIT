import os
import base64
import lzma
from pathlib import Path
import uvicorn

# Production safety stays on: source figures first, never unrelated public-web imagery.
os.environ.setdefault("ISCARB_DISABLE_PUBLIC_IMAGES", "1")
os.environ.setdefault("ISCARB_VISUAL_POLICY", "p1-source>native>local-context>text-first")
os.environ.setdefault("ISCARB_BUILD_ID", "7.2.9-golden-v660-ztm")

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    if not chunks:
        raise RuntimeError("ISCARB presenter payload is missing")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

# GOLDEN MASTER learning grammar + permanent classroom fixes.
from app.home_v670 import app
from app.patch_v725_golden_v660 import apply_v725_golden_v660_patch
from app.patch_v726_timebox_tasks import apply_v726_timebox_tasks_patch
from app.patch_v727_local_case_scaffold import apply_v727_local_case_scaffold_patch
from app.patch_v728_peer_review_decision_boxes import apply_v728_peer_review_decision_boxes_patch
from app.patch_v729_ztm_theme import apply_v729_ztm_theme_patch
from app.patch_v7291_ztm_finish import apply_v7291_ztm_finish_patch

apply_v725_golden_v660_patch(app)
apply_v726_timebox_tasks_patch(app)
apply_v727_local_case_scaffold_patch(app)
apply_v728_peer_review_decision_boxes_patch(app)
apply_v729_ztm_theme_patch(app)
apply_v7291_ztm_finish_patch(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
