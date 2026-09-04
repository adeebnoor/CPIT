import os
import base64
import lzma
from pathlib import Path
import uvicorn

# Production safety: never fetch unrelated public-web/Wikipedia imagery for lecture slides.
os.environ.setdefault("ISCARB_DISABLE_PUBLIC_IMAGES", "1")

ROOT = Path(__file__).resolve().parent
PRESENTER = ROOT / "app" / "presenter_v67_prod.py"
if not PRESENTER.exists():
    chunks = sorted(ROOT.glob("presenter_v67_prod.xz.b64.*"))
    if not chunks:
        raise RuntimeError("ISCARB v6.7 presenter payload is missing")
    payload = "".join(p.read_text(encoding="ascii").strip() for p in chunks)
    PRESENTER.write_bytes(lzma.decompress(base64.b64decode(payload)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.home_v670:app", host="0.0.0.0", port=port, reload=False)
