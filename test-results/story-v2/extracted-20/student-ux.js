(()=>{'use strict';
const button=document.getElementById('exportProgress'),input=document.getElementById('progressImport'),status=document.getElementById('progressBackupStatus');
const allowed=k=>k&&((k.startsWith('iscarb-'))||(k.startsWith('fbr:cpit455:')));
const say=t=>{if(status)status.textContent=t};
document.getElementById('restoreProgress')?.addEventListener('click',()=>input?.click());
button?.addEventListener('click',()=>{try{
 const items={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(allowed(k))items[k]=localStorage.getItem(k)}
 const data={schema:'cpit455-progress-backup-v1',created_at:new Date().toISOString(),items};
 const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),a=document.createElement('a');
 a.href=URL.createObjectURL(blob);a.download='cpit455-progress-backup-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500);say('Backup downloaded.');
}catch{say('Backup could not be created in this browser.')}});
input?.addEventListener('change',async()=>{const file=input.files?.[0];if(!file)return;try{
 const data=JSON.parse(await file.text());if(data?.schema!=='cpit455-progress-backup-v1'||!data.items)throw Error('schema');
 let n=0;for(const [k,v] of Object.entries(data.items)){if(allowed(k)&&typeof v==='string'){localStorage.setItem(k,v);n++}}
 say('Restored '+n+' saved items. Reloading…');setTimeout(()=>location.reload(),500);
}catch{say('This is not a valid CPIT-455 progress backup.')}finally{input.value=''}});
})();
