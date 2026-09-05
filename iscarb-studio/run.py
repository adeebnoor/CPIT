import os
import base64
import lzma
from pathlib import Path
import uvicorn

# Production safety stays on: source figures first, never unrelated public-web imagery.
os.environ.setdefault("ISCARB_DISABLE_PUBLIC_IMAGES", "1")
os.environ.setdefault("ISCARB_VISUAL_POLICY", "p1-source>native>local-context>text-first")
os.environ.setdefault("ISCARB_BUILD_ID", "7.2.5-golden-v660")

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    if not chunks:
        raise RuntimeError("ISCARB presenter payload is missing")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

# GOLDEN MASTER LOCK — the user-approved v660 Balanced30 lecture grammar.
# Keep the mature source parsing / safety fixes already inside home_v670, but do
# NOT install the later v721-v724 pedagogy, kickoff, or presenter specializations.
# Those layers changed the visual/narrative model away from the approved deck.
from app.home_v670 import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
