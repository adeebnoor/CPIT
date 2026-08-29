from __future__ import annotations
import re
from pathlib import Path
R=Path(__file__).resolve().parents[1]

def patch(path, old, new):
    p=R/path; t=p.read_text(encoding='utf-8')
    if old in t: p.write_text(t.replace(old,new,1),encoding='utf-8'); return
    if new not in t: raise SystemExit(f'patch anchor missing: {path}')

# Public archive/version.
for n in ('cimt.html','imam.html'):
    p=R/n; p.write_text(p.read_text(encoding='utf-8').replace('index.html#frameworks','index.html#evolution'),encoding='utf-8')
p=R/'iscarb.html'; t=p.read_text(encoding='utf-8').replace('?v=3.3','?v=4.3.0').replace('v3.3 Original Identity','v4.3.0 · CIMT-native'); p.write_text(t,encoding='utf-8')

# Quota-safe source profiling, preserving current GitHub fallback implementation.
p=R/'iscarb-studio/app/main.py'; t=p.read_text(encoding='utf-8')
imp='from .source_profile_fallback import build_deterministic_source_profile\n'
if imp not in t:
    a='from .gemini_service import GeminiService\n';
    if a not in t: raise SystemExit('main import anchor missing')
    t=t.replace(a,a+imp,1)
old='        profile = service.profile_source(bundle)\n'
new='''        try:\n            profile = service.profile_source(bundle)\n        except Exception as exc:\n            if not _is_quota_error(exc):\n                raise\n            profile = build_deterministic_source_profile(bundle, str(exc))\n'''
if new not in t:
    if old not in t: raise SystemExit('main profile anchor missing')
    t=t.replace(old,new,1)
p.write_text(t,encoding='utf-8')

# Preserve edge-to-edge CIMT figures and make Presenter mobile-safe.
p=R/'iscarb-studio/app/cimt_native_v43.py'; t=p.read_text(encoding='utf-8')
old='            box = (int(w * 0.035), int(h * 0.17), int(w * 0.965), int(h * 0.925))'
new='''            # Preserve edge-to-edge source labels; crop title/footer only vertically.\n            box = (0, int(h * 0.17), w, int(h * 0.925))'''
if old in t: t=t.replace(old,new,1)
elif 'box = (0, int(h * 0.17), w, int(h * 0.925))' not in t: raise SystemExit('crop anchor missing')
old='@media(max-width:850px){{.deck{{grid-template-columns:1fr}}.rail{{display:none}}.slide{{width:96vw}}.visual{{height:calc(100% - 120px)}}}}'
new='@media(max-width:850px){{html,body,.deck,.stage{{max-width:100%;overflow-x:hidden}}.deck{{grid-template-columns:minmax(0,1fr)}}.rail{{display:none}}.stage{{padding:8px;min-width:0}}.slide{{width:calc(100vw - 16px);max-width:calc(100vw - 16px);min-width:0;padding-left:18px;padding-right:18px}}.head,.visual,.slide>*{{min-width:0}}.corner{{left:18px;width:calc(100% - 36px)}}.foot{{left:22px;right:22px}}.decision{{left:24px;right:24px}}.visual{{height:calc(100% - 120px)}}.bulletList article{{grid-template-columns:8px minmax(72px,28%) minmax(0,1fr)}}.tableList article{{grid-template-columns:minmax(88px,34%) minmax(0,1fr)}}.stack{{padding-left:12px;padding-right:12px}}.argument{{padding-left:8px;padding-right:8px}}.compare section{{padding-left:8px;padding-right:8px}}.tree{{padding-left:8px;padding-right:8px}}.context{{gap:14px}}.chain{{gap:6px}}.timeline{{gap:10px}}.burden{{gap:12px;padding-left:4px;padding-right:4px}}.verdict>div{{margin-left:8px;margin-right:8px;gap:10px}}}}'
if old in t: t=t.replace(old,new,1)
elif new not in t: raise SystemExit('presenter media anchor missing')
p.write_text(t,encoding='utf-8')

# Faculty Studio intrinsic-width mobile fixes.
p=R/'iscarb-studio/app/static/index_v410.html'; t=p.read_text(encoding='utf-8')
repls=[
('.compiler{display:grid;grid-template-columns:1.4fr .6fr;gap:14px}.box{border:1px solid #49382c;background:linear-gradient(180deg,#14110e,#0d0b09);border-radius:17px;padding:22px}', '.compiler{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr);gap:14px}.compiler>*{min-width:0}.box{min-width:0;max-width:100%;overflow-wrap:anywhere;border:1px solid #49382c;background:linear-gradient(180deg,#14110e,#0d0b09);border-radius:17px;padding:22px}'),
('input,textarea,select{width:100%;border:1px solid #4a3a2f;background:#0b0908;color:var(--ink);padding:12px;border-radius:8px;font:inherit;font-size:.76rem;outline:none}', 'input,textarea,select{width:100%;max-width:100%;min-width:0;border:1px solid #4a3a2f;background:#0b0908;color:var(--ink);padding:12px;border-radius:8px;font:inherit;font-size:.76rem;outline:none}input[type=file]{overflow:hidden;text-overflow:ellipsis}.field{min-width:0}'),
('@media(max-width:980px){.hero,.compiler{grid-template-columns:1fr}.sourceGrid{grid-template-columns:1fr 1fr}.trust{grid-template-columns:1fr 1fr}.links{display:none}.assets,.gates{grid-template-columns:1fr 1fr}}@media(max-width:620px){.sourceGrid,.grid2,.trust,.assets,.gates{grid-template-columns:1fr}.hero{padding-top:44px}.hero h1{font-size:3.65rem}.wrap{padding:0 16px}.version{display:none}}', '@media(max-width:980px){.hero,.compiler{grid-template-columns:minmax(0,1fr)}.sourceGrid{grid-template-columns:1fr 1fr}.trust{grid-template-columns:1fr 1fr}.links{display:none}.assets,.gates{grid-template-columns:1fr 1fr}}@media(max-width:620px){html,body{max-width:100%;overflow-x:hidden}.sourceGrid,.grid2,.trust,.assets,.gates{grid-template-columns:minmax(0,1fr)}.hero{padding-top:44px}.hero h1{font-size:clamp(2.85rem,15vw,3.65rem)}.wrap{padding:0 16px;max-width:100%}.box{padding:18px 14px}.version{display:none}}')]
for a,b in repls:
    if a in t: t=t.replace(a,b,1)
    elif b not in t: raise SystemExit('studio CSS anchor missing')
p.write_text(t,encoding='utf-8')

# Remove archived local Windows URLs at source.
for p in (R/'slides').glob('*.html'):
    t=p.read_text(encoding='utf-8',errors='replace')
    t=re.sub(r'<!-- saved from url=\([^)]*\)file:///C:/Users/USER/Downloads/[^>]*-->','<!-- Archived CPIT-455 interactive lecture -->',t)
    t=re.sub(r'href="file:///C:/Users/USER/Downloads/[^"#]+(#[^"]+)"',lambda m:f'href="{m.group(1)}"',t)
    p.write_text(t,encoding='utf-8')

# Delete accidentally tracked compiled bytecode.
for p in R.rglob('*.pyc'): p.unlink(missing_ok=True)
# Remove one-shot bootstrap from final tree.
(R/'.github/workflows/one-shot-full-fix.yml').unlink(missing_ok=True)
(R/'tools/apply_full_production_fix.py').unlink(missing_ok=True)
print('bootstrap fixes applied')
