(function(){
  function cleanSalaryCadence(){
    const s=document.getElementById('salaryItemCadence');
    if(!s)return;
    const one=[...s.options].find(o=>o.value==='one_off');
    if(one)one.remove();
  }
  cleanSalaryCadence();
  setTimeout(cleanSalaryCadence,250);
  setTimeout(cleanSalaryCadence,1000);
})();
