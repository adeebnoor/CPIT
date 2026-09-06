(function(){
  const q=id=>document.getElementById(id);
  function ensureInvestmentQuickAdd(){
    const types=document.querySelector('.qa-types'); if(!types||types.querySelector('[data-qa-type="investment"]'))return;
    types.classList.add('plus-five');
    const b=document.createElement('button');b.type='button';b.dataset.qaType='investment';b.textContent='استثمار';types.appendChild(b);
    b.addEventListener('click',()=>{
      types.querySelectorAll('[data-qa-type]').forEach(x=>x.classList.toggle('active',x===b));
      const d=q('qaDynamic');if(!d)return;
      const rows=(typeof investmentData!=='undefined'&&investmentData?.rows)||[];
      d.innerHTML=`<div class="qa-field"><label>المركز الاستثماري</label><select id="qaInvestmentId">${rows.map(x=>`<option value="${String(x.id).replace(/"/g,'&quot;')}" data-value="${Number(x.market_value_sar||0)}">${String(x.platform||'')} — ${String(x.asset||'')}</option>`).join('')}</select></div><div class="qa-field hero"><label>القيمة الحالية بالريال</label><input id="qaInvestmentValue" inputmode="decimal" placeholder="0.00"></div><p class="qa-warning">تحديث القيمة يعيد حساب المحفظة السائلة/المقيدة ومؤشرات التقاعد. لا ينشئ استثمارًا جديدًا ولا يتجاوز بوابة الأمان.</p>`;
      const sel=q('qaInvestmentId'),val=q('qaInvestmentValue');const sync=()=>{const o=sel?.selectedOptions?.[0];if(o&&val)val.value=Number(o.dataset.value||0).toFixed(2)};sel?.addEventListener('change',sync);sync();setTimeout(()=>val?.focus(),80);
    });
    const form=q('qaForm');
    form?.addEventListener('submit',async e=>{
      const active=document.querySelector('[data-qa-type].active')?.dataset.qaType;
      if(active!=='investment')return;
      e.preventDefault();e.stopImmediatePropagation();
      const submit=e.submitter;if(submit)submit.disabled=true;
      try{const id=q('qaInvestmentId')?.value,value=Number(q('qaInvestmentValue')?.value);if(!id||value<0||!Number.isFinite(value))throw new Error('اختر الاستثمار وأدخل قيمة صحيحة');await extra('investment',{method:'PATCH',body:JSON.stringify({id,market_value_sar:value})});q('quickAddModal')?.classList.add('hidden');await loadAll();}
      catch(err){alert(err?.message||String(err))}finally{if(submit)submit.disabled=false}
    },true);
  }
  function improveRevenueLabel(){const el=q('revGrand')?.previousElementSibling;if(el)el.textContent='إجمالي الإيرادات الإضافية المخططة';const note=q('revGrandNote');if(note)note.textContent='لا يشمل الراتب الشهري؛ المؤكد + المتوقع مع بقاء المتوقع خارج السيناريو الآمن';}
  function init(){ensureInvestmentQuickAdd();improveRevenueLabel()}
  setTimeout(init,400);setTimeout(init,1400);
  const baseSwitch=switchTab;switchTab=function(tab){const r=baseSwitch(tab);setTimeout(init,80);return r};
  const baseLoad=loadAll;loadAll=async function(){const r=await baseLoad();setTimeout(init,80);return r};
})();