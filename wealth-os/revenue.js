(function(){
  const q=id=>document.getElementById(id);
  const fmt=n=>'SAR '+new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(Number(n||0));
  const dateFmt=d=>new Intl.DateTimeFormat('en-GB',{day:'2-digit',month:'short',year:'numeric'}).format(d);
  function renderRevenueMeta(){
    try{
      if(typeof data==='undefined'||!data||!data.settings)return;
      const s=data.settings||{};
      const salary=q('incomeSalary');
      if(salary) salary.textContent=fmt(s.salary);
      const date=q('incomeSalaryDate');
      if(date){
        const days=Math.max(0,Number(s.days_to_salary||0));
        const next=new Date(); next.setHours(12,0,0,0); next.setDate(next.getDate()+days);
        date.textContent=days===0?'موعد الراتب: اليوم':'الراتب التالي بعد '+new Intl.NumberFormat('en-US').format(days)+' يوم · '+dateFmt(next);
      }
      const total=q('incomeCollectedTotalNote');
      if(total && typeof incomeData!=='undefined') total.textContent='إجمالي المحصل المسجل: '+fmt(incomeData?.summary?.collected_total||0);
      const title=q('pageTitle');
      if(title && q('income')?.classList.contains('active')) title.textContent='الإيرادات';
      const sub=q('pageSubtitle');
      if(sub && q('income')?.classList.contains('active')) sub.textContent='الراتب والإيرادات الأخرى وتواريخ التحصيل';
    }catch(e){console.warn('Revenue UI:',e)}
  }
  try{
    if(typeof renderIncome==='function'){
      const baseRenderIncome=renderIncome;
      renderIncome=function(){ const r=baseRenderIncome.apply(this,arguments); renderRevenueMeta(); return r; };
    }
    if(typeof switchTab==='function'){
      const baseSwitchTab=switchTab;
      switchTab=function(tab){ const r=baseSwitchTab.apply(this,arguments); if(tab==='income') renderRevenueMeta(); return r; };
    }
  }catch(e){console.warn('Revenue hooks:',e)}
  document.querySelectorAll('[data-tab="income"]').forEach(b=>b.innerHTML='<span>↓</span>الإيرادات');
  renderRevenueMeta();
  setTimeout(renderRevenueMeta,500);
  setTimeout(renderRevenueMeta,1800);
})();
