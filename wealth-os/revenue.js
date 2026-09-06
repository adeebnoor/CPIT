(function(){
  const REV=ROOT+'/wealth-revenue-api';
  let revData={rows:[],summary:{},categories:[],years:[],current_year:new Date().getFullYear()};
  let currentEdit=null;
  const q=id=>document.getElementById(id);

  function upgradeRevenueDom(){
    if(!document.querySelector('link[href*="revenue.css"]')){const l=document.createElement('link');l.rel='stylesheet';l.href='./revenue.css?v=2';document.head.appendChild(l)}
    const sec=q('income'); if(sec && !q('incomeStatusFilter')) sec.innerHTML=`
      <div class="page-head"><div><h1>الإيرادات</h1><p>مرتبطة مباشرة بمحرك الخطة: المؤكد يدخل السيناريو الآمن، المتوقع لا يدخل، والمحصل يُزال من المستقبل.</p></div><button id="showAddIncome" class="btn primary">+ إضافة إيراد</button></div>
      <div class="summary-grid four"><div class="stat-card"><span>الراتب الشهري الأساسي</span><b id="incomeSalary">—</b><small id="incomeSalaryDate">—</small></div><div class="stat-card"><span>محصل هذا الشهر</span><b id="incomeCollectedMonth">—</b><small id="incomeCollectedTotalNote">—</small></div><div class="stat-card warning"><span>مؤكد خلال 2026</span><b id="incomeConfirmed">—</b><small id="incomeConfirmedAllNote">—</small></div><div class="stat-card muted"><span>متوقع خلال 2026</span><b id="incomeExpected">—</b><small id="incomeExpectedAllNote">—</small></div></div>
      <div id="addIncomePanel" class="form-card hidden"><div class="form-grid revenue-form-grid"><label class="field"><span>الوصف</span><input id="incomeDescription"></label><label class="field"><span>المبلغ</span><input id="incomeAmount" inputmode="decimal"></label><label class="field"><span>التاريخ المتوقع</span><input id="incomeDate" type="date"></label><label class="field"><span>الفئة</span><input id="incomeCategory" placeholder="مثال: أبحاث، استثمار، دخل إضافي"></label><label class="field"><span>الحالة</span><select id="incomeCertainty"><option value="expected">متوقع</option><option value="confirmed">مؤكد</option><option value="excluded">مستبعد من الخطة</option></select></label></div><div class="form-actions"><button id="addIncomeBtn" class="btn primary">حفظ وربط بالخطة</button><button id="cancelAddIncome" class="btn">إلغاء</button></div></div>
      <div class="revenue-controls"><div class="toolbar revenue-toolbar"><input id="incomeSearch" placeholder="بحث في المصدر أو الفئة"><select id="incomeStatusFilter"><option value="all">كل الحالات</option><option value="collected">محصل</option><option value="confirmed">مؤكد</option><option value="expected">متوقع</option><option value="excluded">مستبعد</option></select><select id="incomeYearFilter"><option value="all">كل السنوات</option></select><select id="incomeCategoryFilter"><option value="all">كل الفئات</option></select><select id="incomeSort"><option value="date">الأقرب تاريخًا</option><option value="date_desc">الأبعد/الأحدث</option><option value="amount_desc">الأعلى مبلغًا</option><option value="amount_asc">الأقل مبلغًا</option></select></div><div class="revenue-filter-note" id="incomeFilterNote">يعرض كل الإيرادات</div></div>
      <div class="table-card"><table><thead><tr><th>التاريخ</th><th>المصدر</th><th>الفئة</th><th>المبلغ</th><th>الحالة</th><th>التحصيل الفعلي</th><th>الإجراء</th></tr></thead><tbody id="incomeRows"></tbody></table></div>`;
    if(!q('incomeEditModal')){const m=document.createElement('div');m.id='incomeEditModal';m.className='modal hidden';m.innerHTML=`<div class="modal-card revenue-edit-card"><div class="modal-head"><h3>تعديل الإيراد</h3><button id="closeIncomeEdit" class="icon-btn">×</button></div><input type="hidden" id="editIncomeId"><div class="revenue-edit-grid"><label class="field"><span>الوصف</span><input id="editIncomeDescription"></label><label class="field"><span>المبلغ</span><input id="editIncomeAmount" inputmode="decimal"></label><label class="field"><span>التاريخ</span><input id="editIncomeDate" type="date"></label><label class="field"><span>الفئة</span><input id="editIncomeCategory"></label><label class="field"><span>الحالة</span><select id="editIncomeStatus"><option value="expected">متوقع</option><option value="confirmed">مؤكد</option><option value="collected">محصل</option><option value="excluded">مستبعد</option></select></label><label class="field"><span>تاريخ التحصيل عند اختيار محصل</span><input id="editIncomeActualDate" type="date"></label></div><div class="form-actions"><button id="saveIncomeEdit" class="btn primary">حفظ التعديل</button><button id="deleteIncomeEdit" class="btn revenue-delete">حذف الإيراد</button></div><div class="revenue-system-note">أي تعديل هنا يعيد حساب الخطة، فجوة السيولة، والاستعداد للتقاعد من نفس جدول الأحداث.</div></div>`;document.body.appendChild(m)}
  }
  upgradeRevenueDom();
  const fmt=n=>'SAR '+new Intl.NumberFormat('en-US',{minimumFractionDigits:0,maximumFractionDigits:2}).format(Number(n||0));
  const escR=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const n=v=>Number(v||0);
  const normR=s=>String(s??'').toLowerCase();
  const catAr={
    'Special income':'دخل إضافي','Research':'أبحاث','Hill Compound':'استثمار الهيل',
    'Investment distribution':'توزيعات استثمارية','Investment maturity':'استحقاق استثمار',
    'Research groups':'مجموعات بحثية','Asset sale':'بيع أصل','Aseel':'أصيل'
  };
  function descAr(x){
    const s=String(x||'');
    if(s.startsWith('Deferred Sep income:'))return 'دخل سبتمبر المؤجل — هوندا 7,500 + براء 5,000 + تحصيل 5,200 + نهاية الشهر 3,500';
    if(s==='Summer teaching')return 'التدريس الصيفي';
    if(s.includes('Research income — Oct 2026'))return 'دخل أبحاث — أكتوبر 2026';
    if(s.includes('Research income — Jan 2027'))return 'دخل أبحاث — يناير 2027';
    if(s==='Hill Compound capital return')return 'استرداد رأس مال الهيل';
    if(s==='Hill Compound expected profit')return 'ربح الهيل المتوقع';
    if(s.includes('15k special fund maturity'))return 'استحقاق الصندوق الخاص';
    if(s.includes('Research groups entitlement'))return 'استحقاق مجموعات البحث';
    if(s.includes('fully withheld against 45k annual advance'))return 'توزيع ربعي 44,000 — محتجز بالكامل مقابل سلفة 45,000';
    if(s.includes('1k withheld; 43k net cash received'))return 'توزيع ربعي 44,000 — المحتجز 1,000، الصافي 43,000';
    if(s.includes('Quarterly distribution from 90k investment program'))return 'توزيع ربعي من برنامج استثمار 90,000';
    if(s.includes('Jeddah investment sale target'))return 'هدف بيع استثمار جدة 300,000 — التاريخ غير محدد ولا يدخل التوقع';
    if(s.includes('No distribution — investment cycle ended'))return 'لا يوجد توزيع — انتهت دورة الاستثمار في سبتمبر 2029';
    if(s.includes('Aseel sukuk collection'))return 'تحصيل صك أصيل';
    return s||'—';
  }
  function statusOf(x){if(x.status)return x.status;if(x.actual_date)return 'collected';if(x.include_confirmed)return 'confirmed';if(x.include_base)return 'expected';return 'excluded'}
  function statusLabel(s){return s==='collected'?'محصل':s==='confirmed'?'مؤكد':s==='expected'?'متوقع':'مستبعد'}
  function statusTag(s){return `<span class="rev-status ${s}">${statusLabel(s)}</span>`}
  function dateAr(s){return s?String(s).slice(0,10):'غير مجدول'}
  async function revReq(action,opts={}){
    const headers={'content-type':'application/json'}; if(token)headers.authorization='Bearer '+token;
    const r=await fetch(REV+'/'+action,{...opts,headers}); let x={}; try{x=await r.json()}catch{}
    if(r.status===401)throw new Error('unauthorized'); if(!r.ok)throw new Error(x.error||'تعذر تنفيذ العملية'); return x;
  }
  function populateFilters(){
    const yf=q('incomeYearFilter'),cf=q('incomeCategoryFilter'); if(!yf||!cf)return;
    const prevY=yf.value||'all',prevC=cf.value||'all';
    yf.innerHTML='<option value="all">كل السنوات</option>'+revData.years.map(y=>`<option value="${y}">${y}</option>`).join('');
    cf.innerHTML='<option value="all">كل الفئات</option>'+revData.categories.map(c=>`<option value="${escR(c)}">${escR(catAr[c]||c)}</option>`).join('');
    if(prevY==='all' && revData.years.includes(revData.current_year)) yf.value=String(revData.current_year); else yf.value=[...yf.options].some(o=>o.value===prevY)?prevY:'all';
    cf.value=[...cf.options].some(o=>o.value===prevC)?prevC:'all';
  }
  function filteredRows(){
    let arr=[...(revData.rows||[])]; const search=normR(q('incomeSearch')?.value),st=q('incomeStatusFilter')?.value||'all',yr=q('incomeYearFilter')?.value||'all',cat=q('incomeCategoryFilter')?.value||'all',sort=q('incomeSort')?.value||'date';
    if(search)arr=arr.filter(x=>normR([x.description,x.category,x.property_name,x.economic_id].join(' ')).includes(search));
    if(st!=='all')arr=arr.filter(x=>statusOf(x)===st);
    if(yr!=='all')arr=arr.filter(x=>String(x.event_date||'').slice(0,4)===yr);
    if(cat!=='all')arr=arr.filter(x=>String(x.category||'')===cat);
    const d=x=>String(x.actual_date||x.event_date||'9999-12-31');
    arr.sort((a,b)=>sort==='date_desc'?d(b).localeCompare(d(a)):sort==='amount_desc'?n(b.amount)-n(a.amount):sort==='amount_asc'?n(a.amount)-n(b.amount):d(a).localeCompare(d(b)));
    return arr;
  }
  function renderSummary(){
    const s=revData.summary||{},settings=(typeof data!=='undefined'&&data?.settings)||{};
    if(q('incomeSalary'))q('incomeSalary').textContent=fmt(settings.salary);
    if(q('incomeSalaryDate'))q('incomeSalaryDate').textContent=(settings.days_to_salary||0)+' يوم حتى الراتب القادم';
    if(q('incomeCollectedMonth'))q('incomeCollectedMonth').textContent=fmt(s.collected_this_month);
    if(q('incomeCollectedTotalNote'))q('incomeCollectedTotalNote').textContent='إجمالي المحصل المسجل: '+fmt(s.collected_total);
    if(q('incomeConfirmed'))q('incomeConfirmed').textContent=fmt(s.confirmed_current_year);
    if(q('incomeConfirmedAllNote'))q('incomeConfirmedAllNote').textContent='إجمالي المؤكد في كامل الخطة: '+fmt(s.confirmed_all);
    if(q('incomeExpected'))q('incomeExpected').textContent=fmt(s.expected_current_year);
    if(q('incomeExpectedAllNote'))q('incomeExpectedAllNote').textContent='إجمالي المتوقع في كامل الخطة: '+fmt(s.expected_all)+' — لا يدخل السيناريو الآمن';
  }
  function renderRevenue(){
    renderSummary(); const arr=filteredRows(),body=q('incomeRows'); if(!body)return;
    body.innerHTML=arr.length?arr.map(x=>{const st=statusOf(x);return `<tr data-rev-id="${escR(x.id)}"><td>${dateAr(x.event_date)}</td><td><b>${escR(descAr(x.description))}</b><small class="subline">${escR(x.economic_id||'')}</small></td><td>${escR(catAr[x.category]||x.category||'—')}</td><td class="amount">${fmt(x.amount)}</td><td>${statusTag(st)}</td><td>${x.actual_date?dateAr(x.actual_date):'—'}</td><td><div class="rev-actions">${st!=='collected'&&st!=='excluded'?`<button class="rev-btn collect" data-rev-collect="${escR(x.id)}">تحصيل</button>`:''}<button class="rev-btn" data-rev-edit="${escR(x.id)}">تعديل</button><button class="rev-btn delete" data-rev-delete="${escR(x.id)}">حذف</button></div></td></tr>`}).join(''):'<tr><td colspan="7" class="empty">لا توجد إيرادات تطابق الفلاتر</td></tr>';
    const total=arr.reduce((z,x)=>z+n(x.amount),0),note=q('incomeFilterNote'); if(note)note.textContent=`${arr.length} سجل · إجمالي المعروض ${fmt(total)} · الفلترة لا تغيّر الخطة، التعديل والحذف فقط يغيّرانها`;
  }
  async function loadRevenue(){
    try{revData=await revReq('list');populateFilters();renderRevenue()}catch(e){if(e.message!=='unauthorized')console.warn('Revenue load',e)}
  }
  function openEdit(id){
    const x=(revData.rows||[]).find(r=>r.id===id); if(!x)return; currentEdit=x;
    q('editIncomeId').value=x.id;q('editIncomeDescription').value=x.description||'';q('editIncomeAmount').value=x.amount??'';q('editIncomeDate').value=x.event_date||'';q('editIncomeCategory').value=x.category||'';q('editIncomeStatus').value=statusOf(x);q('editIncomeActualDate').value=x.actual_date||'';q('incomeEditModal').classList.remove('hidden');
  }
  async function refreshSystem(){
    await baseLoadAll(); await loadRevenue(); if(typeof loadAudit==='function')try{await loadAudit()}catch{}
  }
  async function createRevenue(e){
    e.preventDefault();e.stopImmediatePropagation();const description=q('incomeDescription').value.trim(),amount=n(q('incomeAmount').value),event_date=q('incomeDate').value||null,category=q('incomeCategory').value.trim()||'Special income',status=q('incomeCertainty').value;
    if(!description||amount<0){alert('أدخل وصفًا ومبلغًا صحيحًا');return}
    await revReq('create',{method:'POST',body:JSON.stringify({description,amount,event_date,category,status})});q('addIncomePanel').classList.add('hidden');q('incomeDescription').value='';q('incomeAmount').value='';q('incomeDate').value='';q('incomeCategory').value='';await refreshSystem();
  }
  async function saveEdit(){
    if(!currentEdit)return;const status=q('editIncomeStatus').value,payload={id:currentEdit.id,description:q('editIncomeDescription').value.trim(),amount:n(q('editIncomeAmount').value),event_date:q('editIncomeDate').value||null,category:q('editIncomeCategory').value.trim()||'Special income',status,actual_date:q('editIncomeActualDate').value||null};
    await revReq('update',{method:'PATCH',body:JSON.stringify(payload)});q('incomeEditModal').classList.add('hidden');currentEdit=null;await refreshSystem();
  }
  async function deleteRevenue(id){
    const x=(revData.rows||[]).find(r=>r.id===id);if(!x)return;if(!confirm('حذف الإيراد «'+descAr(x.description)+'»؟ سيتم حذفه من محرك الخطة والتقاعد أيضًا، مع بقاء أثره في سجل التدقيق.'))return;await revReq('delete',{method:'DELETE',body:JSON.stringify({id})});await refreshSystem();
  }
  async function collectRevenue(id){
    const x=(revData.rows||[]).find(r=>r.id===id);if(!x)return;const amount=prompt('المبلغ الذي تم تحصيله فعليًا',String(x.amount??''));if(amount===null)return;const actual_date=prompt('تاريخ التحصيل YYYY-MM-DD',new Date().toISOString().slice(0,10));if(actual_date===null)return;await revReq('collect',{method:'POST',body:JSON.stringify({id,amount:n(amount),actual_date})});await refreshSystem();
  }
  const baseLoadAll=loadAll;
  loadAll=async function(){await baseLoadAll();await loadRevenue()};
  const baseSwitchTab=switchTab;
  switchTab=function(tab){const r=baseSwitchTab(tab);if(tab==='income'){if(q('pageTitle'))q('pageTitle').textContent='الإيرادات';if(q('pageSubtitle'))q('pageSubtitle').textContent='إدارة كاملة وربط مباشر بالخطة والتقاعد';loadRevenue()}return r};
  document.querySelectorAll('[data-tab="income"]').forEach(b=>b.innerHTML='<span>↓</span>الإيرادات');
  q('showAddIncome')?.addEventListener('click',()=>{q('addIncomePanel').classList.remove('hidden');q('incomeDate').value=new Date().toISOString().slice(0,10);q('incomeDescription').focus()});
  q('cancelAddIncome')?.addEventListener('click',()=>q('addIncomePanel').classList.add('hidden'));
  q('addIncomeBtn')?.addEventListener('click',createRevenue,true);
  ['incomeSearch'].forEach(id=>q(id)?.addEventListener('input',renderRevenue));
  ['incomeStatusFilter','incomeYearFilter','incomeCategoryFilter','incomeSort'].forEach(id=>q(id)?.addEventListener('change',renderRevenue));
  q('incomeRows')?.addEventListener('click',e=>{const c=e.target.closest('[data-rev-collect]'),ed=e.target.closest('[data-rev-edit]'),del=e.target.closest('[data-rev-delete]');if(c)collectRevenue(c.dataset.revCollect);else if(ed)openEdit(ed.dataset.revEdit);else if(del)deleteRevenue(del.dataset.revDelete)});
  q('closeIncomeEdit')?.addEventListener('click',()=>q('incomeEditModal').classList.add('hidden'));
  q('saveIncomeEdit')?.addEventListener('click',saveEdit);
  q('deleteIncomeEdit')?.addEventListener('click',()=>currentEdit&&deleteRevenue(currentEdit.id));
  setTimeout(loadRevenue,350);setTimeout(loadRevenue,1400);
})();
