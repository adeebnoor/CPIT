# CPIT · ISCARB Faculty Studio

This repository contains the CPIT-455 teaching archive and the active **ISCARB Faculty Studio v4.4.0**.

## Project map
- `index.html`, `cimt.html`, `imam.html`, `iscarb.html`: public GitHub Pages surfaces.
- `slides/`, `lectures/`: preserved teaching/source archive.
- `iscarb-studio/`: FastAPI application deployed to Render.
- `iscarb-studio/run.py`: active entry point (`app.start_v440:app`).
- `iscarb-studio/app/start_v*.py` and `gate_v*.py`: intentional composition chain; do not bulk-delete these versioned modules.
- `tools/sanitize_static_site.py`: public archive sanitizer and fragment validator.

## Local verification
```bash
cd iscarb-studio
python -m unittest discover -s tests -v
python -m compileall -q app tests
python run.py
```

GitHub Pages publishes only the static teaching archive. Render serves the dynamic Faculty Studio. `render.yaml` requests commit-triggered auto-deploy from `main`; the deploy workflow can optionally force a deploy using a Render hook/API credential when configured.
