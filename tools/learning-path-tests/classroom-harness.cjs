// DOM checks only. Geometry and actual HTTP/local-storage behavior are tested
// separately in check-classroom-http.py with Chromium and a real origin.
const fs=require('fs'),path=require('path'),{JSDOM,VirtualConsole}=require('jsdom');
const root=path.resolve(__dirname,'../..');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
function load(c,opts={}){
 const errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>{if(!/navigation|window\.scrollTo/.test(e.message))errors.push(e.message)});
 const dom=new JSDOM(read(c.path),{url:'https://adeebnoor.github.io/CPIT/'+c.path,runScripts:'dangerously',pretendToBeVisual:true,virtualConsole:vc,beforeParse(w){
  w.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});w.scrollTo=()=>{};w.confirm=()=>opts.confirm!==false;w.print=()=>{};w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=()=>{};
  w.localStorage.setItem('assignment-draft-sentinel','unchanged');
  for(const [k,v]of Object.entries(opts.saved||{}))w.localStorage.setItem(k,v);
  if(opts.blockStorage)Object.defineProperty(w,'localStorage',{get(){throw Error('Storage unavailable')}});
 }});dom.window.eval(read('lectures/iscarb/runtime/classroom-v3.js'));return {dom,w:dom.window,d:dom.window.document,api:dom.window.iscarb,errors};
}
function put(x,k,v){const e=x.d.querySelector('[data-field="'+k+'"]');if(!e)throw Error('Missing field '+k);e.value=v;e.dispatchEvent(new x.w.Event('input',{bubbles:true}));}
module.exports={root,read,load,put};
