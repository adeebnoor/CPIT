"""Deliver STRESS through the LMS (Blackboard) instead of a public JSON file, for Assignments 3–9.

After Part A is committed, the page asks the student to save the committed Part A record, upload it
to Blackboard, open the new-evidence item that Blackboard releases after that upload (Adaptive
Release), and paste it into the page. The page checks the pasted text against a SHA-256 of the
released text (normalised whitespace and quotes), so the record shows whether the evidence matches
the release. The STRESS text itself is no longer in the repository or on the public site.

Idempotent. Usage (once, with the reveal files still present):  python3 tools/apply_lms_stress.py
It reads each STRESS text, records its hash in curriculum/publication.json and the paper-fidelity
contract (stress_delivery: "lms", stress_text_sha256), rewrites the page's reveal() and removes the
public reveal file. Keep the private STRESS texts for Blackboard; they are not committed.
"""
from __future__ import annotations
import hashlib, json, re, sys, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / 'curriculum/publication.json'
FID = ROOT / 'curriculum/iscarb-paper-fidelity.json'
FIRST = 12
MARK = '/* lms-stress:v1 */'


def norm(t: str) -> str:
    t = unicodedata.normalize('NFC', t).replace(' ', ' ')
    for a, b in (('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'), ('–', '-'), ('—', '-')):
        t = t.replace(a, b)
    return re.sub(r'\s+', ' ', t).strip()


def text_sha(t: str) -> str:
    return hashlib.sha256(norm(t).encode('utf-8')).hexdigest()


# Compact SHA-256 for contexts without crypto.subtle (some file:// or older browsers).
SHA_JS = r"""function lmsSha256Js(s){const b=new TextEncoder().encode(s),K=[1116352408,1899447441,3049323471,3921009573,961987163,1508970993,2453635748,2870763221,3624381080,310598401,607225278,1426881987,1925078388,2162078206,2614888103,3248222580,3835390401,4022224774,264347078,604807628,770255983,1249150122,1555081692,1996064986,2554220882,2821834349,2952996808,3210313671,3336571891,3584528711,113926993,338241895,666307205,773529912,1294757372,1396182291,1695183700,1986661051,2177026350,2456956037,2730485921,2820302411,3259730800,3345764771,3516065817,3600352804,4094571909,275423344,430227734,506948616,659060556,883997877,958139571,1322822218,1537002063,1747873779,1955562222,2024104815,2227730452,2361852424,2428436474,2756734187,3204031479,3329325298];let H=[1779033703,3144134277,1013904242,2773480762,1359893119,2600822924,528734635,1541459225];const l=b.length,n=((l+9+63)>>6)<<6,m=new Uint8Array(n);m.set(b);m[l]=128;const v=new DataView(m.buffer);v.setUint32(n-4,l*8>>>0);v.setUint32(n-8,Math.floor(l/536870912));const w=new Uint32Array(64),r=(x,c)=>(x>>>c)|(x<<(32-c));for(let o=0;o<n;o+=64){for(let i=0;i<16;i++)w[i]=v.getUint32(o+i*4);for(let i=16;i<64;i++){const s0=r(w[i-15],7)^r(w[i-15],18)^(w[i-15]>>>3),s1=r(w[i-2],17)^r(w[i-2],19)^(w[i-2]>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)>>>0}let[a,bb,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const t1=(h+(r(e,6)^r(e,11)^r(e,25))+((e&f)^(~e&g))+K[i]+w[i])>>>0,t2=((r(a,2)^r(a,13)^r(a,22))+((a&bb)^(a&c)^(bb&c)))>>>0;h=g;g=f;f=e;e=(d+t1)>>>0;d=c;c=bb;bb=a;a=(t1+t2)>>>0}H=H.map((x,i)=>(x+[a,bb,c,d,e,f,g,h][i])>>>0)}return H.map(x=>x.toString(16).padStart(8,'0')).join('')}"""

JS = r"""const LMS_STRESS=__CONFIG__;
function lmsNorm(t){t=String(t||'').normalize('NFC').replace(/ /g,' ').replace(/[’‘]/g,"'").replace(/[“”]/g,'"').replace(/[–—]/g,'-');return t.replace(/\s+/g,' ').trim()}
__SHAJS__
async function lmsSha(t){try{if(window.crypto?.subtle){const d=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t));return[...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,'0')).join('')}}catch(e){}return lmsSha256Js(t)}
async function reveal(){__MARK__if(!S.locked||!verifiedCommit||!validLocked(S)){note('A verified Part A commitment is required before the new evidence can be entered.',true);return}if(validStress(S.stress)){buildB(S.stress);return}const L=LMS_STRESS;
$('partB').innerHTML='<section class="card stress" id="lmsStress"><p class="ey">3 · NEW EVIDENCE · FROM BLACKBOARD</p><h2>'+(L.previous?'This earlier edition is closed online':'Receive the new evidence in Blackboard')+'</h2>'+(L.previous?'<p>The new evidence for this earlier edition is no longer published on the site. If you already started this edition, ask your instructor through Blackboard for its new evidence and paste it below. Otherwise use the current edition of '+esc(L.assignment)+'.</p>':'<ol><li><b>Save your committed Part A.</b> <button type="button" id="lmsPartA">Print / save Part A as PDF</button></li><li><b>Upload it in Blackboard</b> to <i>'+esc(L.partA)+'</i>.</li><li><b>Open</b> <i>'+esc(L.item)+'</i>. Blackboard shows it only after your Part A upload.</li><li><b>Copy the whole text</b> and paste it below. Part B opens here.</li></ol>')+'<label class="field-label" for="lmsText">New evidence, pasted from Blackboard</label><textarea id="lmsText" placeholder="Paste the complete new-evidence text here."></textarea><div class="buttons"><button type="button" class="good" id="lmsCheck">Check and continue to Part B</button></div><p id="lmsMsg" role="status" aria-live="polite" class="hint">The page checks that the pasted text matches the released evidence. Your Part A stays committed and read-only.</p></section>';
const pa=$('lmsPartA');if(pa)pa.onclick=()=>{printSheet(false);const st=document.querySelector('#print .draft-stamp');if(st)st.textContent='PART A · COMMITTED · upload this record to Blackboard to receive the new evidence';const old=document.title;document.title=stem()+'-PartA';try{window.print()}finally{setTimeout(()=>document.title=old,800)}};
$('lmsCheck').onclick=async()=>{const raw=$('lmsText').value,n=lmsNorm(raw),msg=$('lmsMsg');if(n.length<=30){msg.textContent='Paste the complete new-evidence text from Blackboard.';return}const ok=(await lmsSha(n))===L.sha;if(!ok&&$('lmsCheck').dataset.warned!==n){$('lmsCheck').dataset.warned=n;msg.textContent='This text does not match the evidence released for '+L.assignment+'. Check that you copied the whole Blackboard item. If you are sure, select the button again: your record will be marked as unverified.';return}const r={chapter:C.chapter,version:C.version,label:ok?'STRESS · new evidence · matches the Blackboard release':'STRESS · new evidence · UNVERIFIED (differs from the Blackboard release)',text:raw.trim(),source:'lms',verified:ok};S.stress=r;S.revealedAt=now();dirty=true;save(false);note(ok?'New evidence verified. Continue with REFIT.':'New evidence recorded as unverified. Continue with REFIT.',!ok);buildB(r)}}
"""

TEXT_SWAPS = [
    ('STRESS will open automatically after your commitment is saved. No code is required. This does not submit anything to the LMS.',
     'You then upload the Part A record to Blackboard, which releases the new evidence. Committing here does not submit anything to the LMS.'),
    ('The new evidence opens automatically after you commit Part A. No unlock code is required.',
     'After you commit Part A, upload the Part A record to Blackboard. Blackboard then releases the new evidence, and you paste it here to continue.'),
    ("note('Part A committed. Continue with the new evidence and REFIT.')",
     "note('Part A committed. Follow the Blackboard steps below to receive the new evidence.')"),
]


def patch_page(path: Path, cfg: dict) -> bool:
    s = path.read_text(encoding='utf-8')
    if MARK in s:
        return False
    a = s.index('async function reveal(){')
    b = s.index('async function commit(){', a)
    js = (JS.replace('__CONFIG__', json.dumps(cfg, ensure_ascii=False)).replace('__SHAJS__', SHA_JS)
          .replace('__MARK__', MARK))
    s = s[:a] + js + s[b:]
    for old, new in TEXT_SWAPS:
        s = s.replace(old, new)
    s, n = re.subn(r'("reveal": |reveal:)\s*("[^"]*"|\'[^\']*\')', lambda m: m.group(1) + ('""' if m.group(2).startswith('"') else "''"), s, count=1)
    if n != 1:
        raise SystemExit(f'{path}: reveal config not found')
    path.write_text(s, encoding='utf-8')
    return True


def main() -> int:
    pub = json.loads(PUB.read_text(encoding='utf-8'))
    fid = json.loads(FID.read_text(encoding='utf-8'))
    number = {a['chapter']: i + 1 for i, a in enumerate(pub['assignments'])}
    removed = []
    for kind in ('assignments', 'previous_assignments'):
        for a in pub[kind]:
            ch = a['chapter']
            if ch < FIRST:
                continue
            sp = ROOT / a['stress_path']
            if a.get('stress_delivery') != 'lms':
                if not sp.is_file():
                    raise SystemExit(f'{sp} is missing and no hash was recorded yet')
                a['stress_text_sha256'] = text_sha(json.loads(sp.read_text(encoding='utf-8'))['text'])
                a['stress_delivery'] = 'lms'
            n = number[ch]
            cfg = {'sha': a['stress_text_sha256'], 'assignment': f'Assignment {n}', 'previous': kind == 'previous_assignments',
                   'partA': f'Assignment {n} · Part A (committed record)', 'item': f'Assignment {n} · New evidence'}
            patch_page(ROOT / a['path'], cfg)
            if sp.is_file():
                sp.unlink(); removed.append(a['stress_path'])
            if a['stress_path'] in pub['iscarb_public_files']:
                pub['iscarb_public_files'].remove(a['stress_path'])
            if kind == 'assignments':
                spec = fid['assignments'][str(ch)]
                spec['stress_delivery'] = 'lms'
                spec['stress_text_sha256'] = a['stress_text_sha256']
    PUB.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    FID.write_text(json.dumps(fid, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'LMS STRESS delivery applied from Chapter {FIRST}; removed {len(removed)} public reveal file(s).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
