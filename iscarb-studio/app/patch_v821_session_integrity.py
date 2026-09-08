from __future__ import annotations

"""ISCARB v8.2.1 — session integrity for ephemeral Render deployments.

The free Render service has no persistent disk. A browser can therefore retain a
job id and fully rendered result DOM after the container holding that job has
restarted. This patch makes the server version authoritative and makes the
browser prove that a saved job still exists before presenting it as resumable.
"""

import inspect
from typing import Any

from fastapi.responses import HTMLResponse

BUILD_ID = "8.2.1-session-integrity"
PUBLIC_VERSION = "8.2.1 · ACADEMIC CONTRACT"

SESSION_CSS = r"""
<style id="iscarb-v821-session-integrity">
html.iscarb-session-checking #result{visibility:hidden!important}
#iscarbSessionNotice{display:none;margin:18px auto;max-width:1320px;padding:14px 16px;border:1px solid rgba(220,181,107,.36);border-left:4px solid #dcb56b;border-radius:10px;background:#17120d;color:#e9dfd1;font-size:13px;line-height:1.5}
#iscarbSessionNotice.show{display:block}
#iscarbSessionNotice strong{color:#dcb56b}
#iscarbSessionNotice a{display:inline-block;margin-left:10px;color:#2cdcff;font-weight:800;text-decoration:none}
</style>
"""

SESSION_JS = r"""
<script id="iscarb-v821-session-runtime">
(function(){
  'use strict';
  const STORAGE_KEY='iscarb.job.v44';
  const VERSION='8.2.1 · ACADEMIC CONTRACT';
  let checking=false;
  let lastChecked=0;
  let deadJob='';

  function savedJob(){
    try{
      const id=localStorage.getItem(STORAGE_KEY)||'';
      return /^[a-f0-9-]{16,64}$/i.test(id)?id:'';
    }catch(_){return '';}
  }
  function clearSavedJob(id){
    try{ if(!id || localStorage.getItem(STORAGE_KEY)===id) localStorage.removeItem(STORAGE_KEY); }catch(_){}
  }
  function setVersion(){
    document.querySelectorAll('.version').forEach(el=>el.textContent=VERSION);
  }
  function notice(){
    let box=document.getElementById('iscarbSessionNotice');
    if(box) return box;
    box=document.createElement('div');
    box.id='iscarbSessionNotice';
    const host=document.querySelector('main')||document.querySelector('.page')||document.body;
    const first=host.firstElementChild;
    if(first) host.insertBefore(box,first); else host.appendChild(box);
    return box;
  }
  function hideDeadWorkspace(id){
    deadJob=id||deadJob;
    clearSavedJob(id);
    document.documentElement.classList.remove('iscarb-session-checking');
    const result=document.getElementById('result');
    if(result) result.hidden=true;
    const status=document.getElementById('status');
    if(status) status.hidden=true;
    const retry=document.getElementById('retryPoll');
    if(retry) retry.hidden=true;
    const error=document.getElementById('error');
    if(error) error.textContent='';
    const box=notice();
    box.innerHTML='<strong>Previous workspace expired.</strong> The Render container restarted, so the old server-side lecture files no longer exist. The stale results and download links have been removed. <a href="#upgrade">Build this lecture again →</a>';
    box.classList.add('show');
  }
  function keepWorkspace(){
    document.documentElement.classList.remove('iscarb-session-checking');
    const box=document.getElementById('iscarbSessionNotice');
    if(box) box.classList.remove('show');
  }
  async function validate(force){
    const id=savedJob();
    if(!id || checking) { document.documentElement.classList.remove('iscarb-session-checking'); return; }
    const now=Date.now();
    if(!force && now-lastChecked<30000) return;
    checking=true; lastChecked=now;
    try{
      const response=await fetch('/api/jobs/'+encodeURIComponent(id),{cache:'no-store',headers:{'Accept':'application/json'}});
      if(response.status===404){ hideDeadWorkspace(id); return; }
      if(response.ok){ deadJob=''; keepWorkspace(); return; }
      // Server/transient failures do not destroy a potentially valid workspace.
      document.documentElement.classList.remove('iscarb-session-checking');
    }catch(_){
      document.documentElement.classList.remove('iscarb-session-checking');
    }finally{ checking=false; }
  }
  function prime(){
    setVersion();
    if(savedJob()) document.documentElement.classList.add('iscarb-session-checking');
    validate(true);
  }

  // bfcache and long-lived tabs are the important cases: a deployment can occur
  // without a full browser reload, leaving an otherwise convincing dead result.
  window.addEventListener('pageshow',()=>validate(true));
  document.addEventListener('visibilitychange',()=>{if(!document.hidden) validate(true);});
  window.addEventListener('focus',()=>validate(false));
  setInterval(()=>{if(!document.hidden) validate(false);},60000);

  // If the user has a stale result visible from an old live tab, validate before
  // a download/preview click. A dead job is blocked instead of returning raw JSON.
  document.addEventListener('click',function(event){
    const a=event.target && event.target.closest ? event.target.closest('a[href]') : null;
    if(!a) return;
    const href=a.getAttribute('href')||'';
    const match=href.match(/\/api\/jobs\/([a-f0-9-]{16,64})(?:\/|$)|\/learn\/([a-f0-9-]{16,64})(?:[/?#]|$)|\/instructor\/([a-f0-9-]{16,64})(?:[/?#]|$)/i);
    const id=match && (match[1]||match[2]||match[3]);
    if(id && deadJob && id===deadJob){
      event.preventDefault();
      event.stopPropagation();
      hideDeadWorkspace(id);
    }
  },true);

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',prime,{once:true});
  else prime();
})();
</script>
"""


def _server_version(html: str) -> str:
    """Make the HTML response truthful even before client JS runs."""
    replacements = (
        ("7.2.0 · CLEAN · IT-WIDE", PUBLIC_VERSION),
        ("7.2.0 · IT-WIDE", PUBLIC_VERSION),
        ("7.2.0 · IT-wide · Multi-source · Gate v15", PUBLIC_VERSION),
        ("8.2.0 · ACADEMIC CONTRACT", PUBLIC_VERSION),
    )
    for old, new in replacements:
        html = html.replace(old, new)
    return html


def _decorate(html: str) -> str:
    html = _server_version(html)
    if "iscarb-v821-session-integrity" not in html:
        html = html.replace("</head>", SESSION_CSS + "\n</head>", 1)
    if "iscarb-v821-session-runtime" not in html:
        html = html.replace("</body>", SESSION_JS + "\n</body>", 1)
    return html


async def _call(endpoint, *args, **kwargs):
    value = endpoint(*args, **kwargs)
    if inspect.isawaitable(value):
        value = await value
    return value


def apply_v821_session_integrity_patch(app) -> None:
    if getattr(app.state, "iscarb_v821_patched", False):
        return
    app.state.iscarb_v821_patched = True

    home_routes = [
        r for r in app.router.routes
        if getattr(r, "path", None) == "/" and "GET" in (getattr(r, "methods", set()) or set())
    ]
    if not home_routes:
        raise RuntimeError("ISCARB v8.2.1 could not find the production home route")
    previous = home_routes[-1].endpoint
    app.router.routes[:] = [r for r in app.router.routes if getattr(r, "path", None) != "/"]

    @app.get("/", include_in_schema=False)
    async def session_safe_home():
        response = await _call(previous)
        if isinstance(response, HTMLResponse):
            html = response.body.decode(response.charset or "utf-8")
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers["X-ISCARB-Session-Integrity"] = BUILD_ID
            headers["X-ISCARB-Public-Version"] = PUBLIC_VERSION
            return HTMLResponse(_decorate(html), status_code=response.status_code, headers=headers)
        if isinstance(response, str):
            return HTMLResponse(_decorate(response), headers={
                "X-ISCARB-Session-Integrity": BUILD_ID,
                "X-ISCARB-Public-Version": PUBLIC_VERSION,
            })
        return response

    @app.get("/api/session-policy", include_in_schema=False)
    def session_policy() -> dict[str, Any]:
        return {
            "build_id": BUILD_ID,
            "persistent_server_storage": False,
            "browser_resume_requires_server_validation": True,
            "stale_job_behavior": "clear browser pointer, hide dead outputs, require recompile",
            "validation_events": ["page load", "pageshow", "tab visibility", "window focus", "60-second foreground heartbeat"],
        }
