(function(){
  const V22=ROOT+'/wealth-v22-api';
  const q=id=>document.getElementById(id);
  const money0=n=>'SAR '+new Intl.NumberFormat('en-US',{maximumFractionDigits:0}).format(Number(n||0));
  const money2=n=>'SAR '+new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(Number(n||0));
  const pct1=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(Number(n||0))+'%';
  const escV=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let v22=null;

  async function req(){
    const r=await fetch(V22+'/summary',{headers:{authorization:'Bearer '+token,'content-type':'application/json'}});
    let x={}; try{x=await r.json()}catch{}
    if(!r.ok) throw new Error(x.error||'تعذر تحميل التحليل المالي');
    return x;
  }

  function ensure(){
    const dash=q('dashboard'); if(!dash||q('v22FinancialPanel')) return;
    const wrap=document.createElement('section');wrap.id='v22FinancialPanel';wrap.className='v22-financial-panel';
    wrap.innerHTML=`
      <div class="v22-section-head"><div><span>من محرك AdeebFamily v22</span><h2>الصحة المالية ومسار الـ12 شهر</h2><p>تم تكييف الخوارزميات القديمة مع أرقام Excel v26؛ لا تغيّر المرجع المالي.</p></div><span id="v22Source" class="v22-source">v26 + v22</span></div>
      <div class="v22-grid">
        <article class="card v22-health-card">
          <div class="v22-card-title"><div><h3>درجة الصحة المالية</h3><small>سيولة · دين · تقاعد · ادخار · تنويع</small></div><div id="v22HealthRing" class="v22-ring"><div><b id="v22HealthScore">—</b><span>/100</span></div></div></div>
          <div id="v22HealthSummary" class="v22-health-summary">جارٍ التحليل...</div>
          <div id="v22HealthFactors" class="v22-health-factors"></div>
        </article>
        <article class="card v22-cash-card">
          <div class="v22-card-title"><div><h3>توقع السيولة 12 شهر</h3><small>FALLBACK فقط — Expected لا يدخل</small></div><span id="v22CashBadge" class="v22-mini">—</span></div>
          <div id="v22CashChart" class="v22-cash-chart"></div>
          <div id="v22CashMonths" class="v22-cash-months"></div>
        </article>
        <article class="card v22-growth-card">
          <div class="v22-card-title"><div><h3>محرك بناء الثروة</h3><small>ينمو بعد الأمان وليس قبله</small></div><span id="v22Gate" class="v22-gate">—</span></div>
          <div class="v22-growth-hero"><span>المحفظة السائلة</span><div><b id="v22LiquidNow">—</b><i>←</i><b id="v22Liquid50">—</b></div><small id="v22GrowthMultiple">—</small></div>
          <div class="v22-growth-grid"><div><span>تغطية التقاعد</span><b id="v22RetCov">—</b></div><div><span>أكبر فجوة</span><b id="v22MaxGap">—</b></div></div>
          <div id="v22GrowthAdvice" class="v22-growth-advice">—</div>
        </article>
      </div>`;
    const anchor=q('decisionBanner')||dash.firstChild;
    const cc=q('dailyCommandCenter');
    if(cc&&cc.nextSibling) dash.insertBefore(wrap,cc.nextSibling); else if(anchor) dash.insertBefore(wrap,anchor); else dash.prepend(wrap);
  }

  function renderHealth(){
    const h=v22?.health||{},score=Number(h.overall||0);q('v22HealthScore').textContent=Math.round(score);
    const ring=q('v22HealthRing'); if(ring) ring.style.setProperty('--health',Math.max(0,Math.min(100,score)));
    const sum=q('v22HealthSummary'); if(sum){sum.className='v22-health-summary '+String(h.status||'');sum.textContent=(h.summary||'—')+' · الأولوية: '+(h.priority||'—')}
    const factors=h.factors||[];q('v22HealthFactors').innerHTML=factors.map(x=>`<div class="v22-factor"><div><span>${escV(x.label)}</span><b>${Math.round(Number(x.score||0))}</b></div><div class="v22-factor-track"><i style="width:${Math.max(0,Math.min(100,Number(x.score||0)))}%"></i></div><small>${escV(x.detail||'')}</small></div>`).join('');
  }

  function renderCash(){
    const rows=v22?.cashflow||[];if(!rows.length){q('v22CashChart').innerHTML='<div class="empty">لا توجد بيانات</div>';return}
    const vals=rows.map(r=>Number(r.end_cash||0));const max=Math.max(...vals.map(Math.abs),1),w=720,h=190,p=18,zero=h/2;
    const pts=vals.map((v,i)=>`${p+i*(w-2*p)/Math.max(1,vals.length-1)},${zero-(v/max)*(zero-p)}`).join(' ');
    let bars='';rows.forEach((r,i)=>{const net=Number(r.total_income||0)-Number(r.total_outflows||0),x=p+i*(w-2*p)/Math.max(1,rows.length-1),bh=Math.min(55,Math.abs(net)/Math.max(1,Math.max(...rows.map(z=>Math.abs(Number(z.total_income||0)-Number(z.total_outflows||0))))) *55);bars+=`<rect x="${x-4}" y="${net>=0?zero-bh:zero}" width="8" height="${bh}" rx="3" class="${net>=0?'pos':'neg'}"/>`});
    q('v22CashChart').innerHTML=`<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none"><line x1="${p}" x2="${w-p}" y1="${zero}" y2="${zero}" class="zero"/>${bars}<polyline points="${pts}" class="cash-line" fill="none"/><circle cx="${w-p}" cy="${zero-(vals.at(-1)/max)*(zero-p)}" r="5" class="cash-dot"/></svg>`;
    const monthNames=['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'];
    q('v22CashMonths').innerHTML=rows.map(r=>{const d=new Date(String(r.month)+'T00:00:00Z'),gap=Number(r.gap||0);return `<div class="${gap>0?'gap':''}"><span>${monthNames[d.getUTCMonth()]}</span><b>${money0(r.end_cash)}</b>${gap>0?`<em>فجوة ${money0(gap)}</em>`:''}</div>`}).join('');
    const gaps=rows.filter(r=>Number(r.gap||0)>0);q('v22CashBadge').textContent=gaps.length?gaps.length+' شهر ضغط':'بدون فجوة 12 شهر';q('v22CashBadge').className='v22-mini '+(gaps.length?'warn':'ok');
  }

  function renderGrowth(){
    const g=v22?.growth||{};q('v22LiquidNow').textContent=money0(g.current_liquid);q('v22Liquid50').textContent=money0(g.projected_liquid);q('v22GrowthMultiple').textContent='نمو متوقع '+new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(Number(g.multiple||0))+'× حتى عمر 50';q('v22RetCov').textContent=pct1(Number(g.retirement_coverage||0)*100);q('v22MaxGap').textContent=money0(g.max_gap);const gate=String(g.investment_gate||'LOCKED'),el=q('v22Gate');el.textContent=gate==='OPEN'?'الاستثمار مفتوح':'الاستثمار مقفل';el.className='v22-gate '+(gate==='OPEN'?'open':'locked');q('v22GrowthAdvice').textContent=gate==='OPEN'?'الفائض الجديد يتوزع وفق قواعد v26 بعد حماية السيولة.':'أغلق فجوة السيولة أولاً. لا تموّل الاستثمار ببطاقة أو قرض ولا ترفع نمط المعيشة بعد انتهاء القرض.';
  }

  function render(){if(!v22)return;ensure();q('v22Source').textContent='Excel v26 + خوارزميات v22';renderHealth();renderCash();renderGrowth()}
  async function load(){if(!token)return;try{v22=await req();render()}catch(e){console.warn('v22 panel',e)}}
  ensure();
  const baseLoad=loadAll;loadAll=async function(){const r=await baseLoad();await load();return r};
  if(token)setTimeout(load,250);
  setInterval(()=>{if(document.visibilityState==='visible'&&token)load()},5*60*1000);
})();