import os
import base64
import lzma
from pathlib import Path
import uvicorn

# Authoritative curriculum baseline: user-approved Golden v6.6 lecture model.
os.environ.setdefault("ISCARB_DISABLE_PUBLIC_IMAGES", "1")
os.environ.setdefault("ISCARB_VISUAL_POLICY", "p1-source>native>local-context>text-first")
os.environ.setdefault("ISCARB_BUILD_ID", "7.3.0-golden-v660-universal-meta-gates")

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    if not chunks:
        raise RuntimeError("ISCARB presenter payload is missing")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

# GOLDEN MASTER LOCK — full-curriculum baseline.
# Universal meta-gates apply to every course. Stricter domain profiles activate
# only when relevant (e.g. dependability/reliability/safety/security).
# ZTM visual experiments remain in the repository but are deliberately inactive.
from app.home_v670 import app
from app.patch_v725_golden_v660 import apply_v725_golden_v660_patch
from app.patch_v726_timebox_tasks import apply_v726_timebox_tasks_patch
from app.patch_v727_local_case_scaffold import apply_v727_local_case_scaffold_patch
from app.patch_v728_peer_review_decision_boxes import apply_v728_peer_review_decision_boxes_patch
from app.patch_v729_editor_gates import apply_v729_editor_gates_patch
from app.patch_v730_universal_meta_gates import apply_v730_universal_meta_gates_patch

apply_v725_golden_v660_patch(app)
apply_v726_timebox_tasks_patch(app)
apply_v727_local_case_scaffold_patch(app)
apply_v728_peer_review_decision_boxes_patch(app)
apply_v729_editor_gates_patch(app)
apply_v730_universal_meta_gates_patch(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
