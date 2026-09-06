const AUDIT_URL='https://hwuintdzmozamnmgtfly.supabase.co/functions/v1/wealth-safety-audit';
let safetyAudit=null;
const auditMoney=n=>'SAR '+new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(Number(n||0));
const auditPct=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(Number(n||0)*100)+'%';
function auditStatusAr(s){return s==='PASS'?'سليم':s==='WARN'?'تنبيه':'يحتاج إجراء'}
function auditClass(s){return s==='PASS'?'pass':s==='WARN'?'warn':'fail'}
async function loadSafetyAudit(){
  const tok=localStorage.getItem('wealth_session')||'';if(!tok)return;
  try{
    const r=await fetch(AUDIT_URL,{headers:{authorization:'Bearer '+tok,'content-type':'application/json'}});const x=await r.json();if(!r.ok)throw new Error(x.error||'تعذر التدقيق');safetyAudit=x;renderSafetyAudit(x);
  }catch(e){const o=document.getElementById('auditOverall');if(o){o.textContent='تعذر الفحص';o.className='audit-overall caution'}const v=document.getElementById('auditVerdict');if(v)v.textContent='تعذر تشغيل فحص السلامة الآن: '+(e.message||e)}
}
function renderSafetyAudit(x){const m=x.metrics||{};const overall=document.getElementById('auditOverall');if(overall){overall.textContent=x.overall==='PASS'?'النظام سليم':x.overall==='CAUTION'?'سليم مع تنبيه':'إجراء مطلوب';overall.className='audit-overall '+(x.overall==='PASS'?'pass':x.overall==='CAUTION'?'caution':'action')}
  const source=document.getElementById('sourceBadge');if(source&&typeof data!=='undefined'&&data?.settings){source.textContent='v26 · '+(data.settings.scenario_view==='FALLBACK'?'آمن':'استكشافي')}
  const put=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
  put('auditGap',auditMoney(m.max_fallback_gap));put('auditGapDate',m.max_gap_month?'ذروة الضغط '+String(m.max_gap_month).slice(0,7):'لا توجد فجوة');put('auditMonthlyClosure',auditMoney(m.additional_monthly_gap_closure));put('auditGrowth',new Intl.NumberFormat('en-US',{maximumFractionDigits:1}).format(m.liquid_growth_multiple||0)+'×');put('auditGrowthDetail',auditMoney(m.current_liquid)+' ← '+auditMoney(m.projected_liquid_at_50));put('auditRetirementCoverage',auditPct(m.retirement_coverage));put('auditRetirementIncome',auditMoney(m.retirement_income)+' من '+auditMoney(m.retirement_target));put('auditRisk',auditPct(m.high_risk_pct));
  const verdict=document.getElementById('auditVerdict');if(verdict){const deficit=Number(m.max_fallback_gap||0);const cov=Number(m.retirement_coverage||0);verdict.className='audit-verdict '+(x.overall==='PASS'?'pass':x.overall==='ACTION_REQUIRED'?'action':'');verdict.textContent=deficit>0?`النظام يبني الثروة، لكنه لا يضمن صفر عجز بعد: توجد فجوة مؤكدة فقط قدرها ${auditMoney(deficit)}. لذلك يبقى الاستثمار الجديد محجوبًا، ويجب إغلاق هذه الفجوة بدخل/بيع أصل/إعادة جدولة مؤكدة قبل اعتبار الخطة آمنة بالكامل. تغطية التقاعد الحالية ${(cov*100).toFixed(1)}%.`:'لا توجد فجوة السيناريو الآمن حالياً، ويمكن للنظام توجيه الفائض إلى بناء الثروة مع استمرار حماية السيولة.'}
  const checks=document.getElementById('auditChecks');if(checks)checks.innerHTML=(x.checks||[]).map(c=>`<div class="audit-check"><div class="audit-check-head"><strong>${c.title}</strong><span class="audit-chip ${auditClass(c.status)}">${auditStatusAr(c.status)}</span></div><p>${c.detail}</p></div>`).join('');
}
setTimeout(loadSafetyAudit,900);
document.getElementById('refreshBtn')?.addEventListener('click',()=>setTimeout(loadSafetyAudit,450));
document.getElementById('syncNowBtn')?.addEventListener('click',()=>setTimeout(loadSafetyAudit,450));
setInterval(()=>{if(!document.hidden&&localStorage.getItem('wealth_session'))loadSafetyAudit()},120000);