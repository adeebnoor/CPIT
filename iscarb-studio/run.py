import os
import base64
import lzma
from pathlib import Path
import uvicorn

# Production safety: never fetch unrelated public-web/Wikipedia imagery for lecture slides.
os.environ.setdefault("ISCARB_DISABLE_PUBLIC_IMAGES", "1")
os.environ.setdefault("ISCARB_VISUAL_POLICY", "p1-source>native>local-context>text-first")
os.environ.setdefault("ISCARB_BUILD_ID", "7.2.3")

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    if not chunks:
        raise RuntimeError("ISCARB presenter payload is missing")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

# Import the complete production application first, then install the final
# cognitive-budget / AI-era pedagogy, clean polish, and kickoff-aware source mode.
from app.home_v670 import app
from app.patch_v721_pedagogy_ai import apply_v721_pedagogy_ai_patch
from app.patch_v722_final_polish import apply_v722_final_polish
from app.patch_v723_kickoff_mode import apply_v723_kickoff_patch

apply_v721_pedagogy_ai_patch(app)
apply_v722_final_polish(app)
apply_v723_kickoff_patch(app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
