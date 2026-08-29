# CPIT / ISCARB architecture

The repository intentionally has two delivery surfaces. **GitHub Pages** serves the static CPIT/CIMT/IMAM/ISCARB archive. **Render** serves the dynamic FastAPI Faculty Studio.

The active runtime is `iscarb-studio/run.py -> app.start_v430:app`. v4.3 composes earlier tested start/gate modules rather than duplicating them; those versioned modules remain active dependencies. The compile path source-locks P1, profiles coverage, generates exactly 20 units for a 90-minute session, applies deterministic and semantic gates, then exposes Presenter Preview, PPTX, Presenter PDF, Faculty Reading Pack, Instructor Guide, Student Activity Pack, and Blueprint JSON.

GitHub Pages staging copies only public HTML/CSS/slides/lectures and sanitizes archived local-file links. Runtime data, secrets, compiled Python, workflows, and application source are excluded from the Pages artifact.

Render deployment uses `render.yaml` with `branch: main` and `autoDeployTrigger: commit`. Optional GitHub secrets `RENDER_DEPLOY_HOOK_URL` or `RENDER_API_KEY` + `RENDER_SERVICE_ID` may force a deployment; otherwise CI waits for Render auto-deploy and verifies `/api/health`.
