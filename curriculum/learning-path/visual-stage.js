/* Paginated visual presentation on top of the preserved iSCARB interaction engine.
 * CSS columns reflow complete content into addressable pages. No scale-to-fit,
 * line clamps, scrollbar hiding, wheel hijacking or content truncation is used.
 */
(function(){
'use strict';
var story=LECTURE.visualStory;if(!story)return;
var states=new Map(),overlays=new Map(),oldGo=go,oldOpen=openOv,oldClose=closeOv,oldFit=fit;
var resizePending=false,sourceTarget=null,initializing=true,resume=null;
try{resume=JSON.parse(localStorage.getItem(KEY+'-visual-location-v3')||'null')}catch(e){}
function el(tag,cls,text){var n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;return n;}
function plain(value){var n=el('div');n.innerHTML=T(value||'');return n.textContent.trim();}
function flowOf(state){return state.mode==='overview'&&state.summary?state.summary:state.details;}
function active(){var ov=document.querySelector('.ov.on');return ov?overlays.get(ov.id):states.get(cur);}
function transformTables(root){
 root.querySelectorAll('table').forEach(function(table){
  var rows=Array.from(table.rows),heads=[];if(rows[0]&&rows[0].querySelector('th'))heads=Array.from(rows.shift().cells).map(function(c){return c.textContent.trim()});
  var replacement=el('div','v3-table');replacement.setAttribute('role','list');
  rows.forEach(function(row){var card=el('section','v3-table-row'),dl=el('dl');card.setAttribute('role','listitem');Array.from(row.cells).forEach(function(cell,i){dl.append(el('dt','',heads[i]||'Column '+(i+1)));var dd=el('dd');while(cell.firstChild)dd.append(cell.firstChild);dl.append(dd)});card.append(dl);replacement.append(card)});
  table.replaceWith(replacement);
 });
 // Comparison grids have visual column headers; retain that mapping in each card.
 root.querySelectorAll('.cmp').forEach(function(cmp){cmp.style.display='block';});
}
function toolbar(state){
 var bar=el('div','v3-toolbar'),mode=el('button','v3-mode','Details'),local=el('div','v3-local');mode.type='button';
 mode.hidden=!state.summary;mode.setAttribute('aria-label','Show full explanation');
 mode.onclick=function(){state.mode=state.mode==='overview'?'details':'overview';state.page=0;show(state);};
 var prev=el('button','','‹'),label=el('span','v3-page-label'),next=el('button','','›');
 prev.type=next.type='button';prev.setAttribute('aria-label','Previous page within this unit');next.setAttribute('aria-label','Next page within this unit');
 prev.onclick=function(){setPage(state,state.page-1)};next.onclick=function(){setPage(state,state.page+1)};
 local.append(prev,label,next);bar.append(mode,local);state.toolbar=bar;state.modeButton=mode;state.pageLabel=label;state.pagePrev=prev;state.pageNext=next;return bar;
}
function countPages(width,contentWidth,gap){return Math.max(1,Math.ceil((contentWidth+gap-1)/(width+gap)));}
function persist(state){if(initializing||state.index===undefined||state.index!==cur)return;try{localStorage.setItem(KEY+'-visual-location-v3',JSON.stringify({key:U[state.index].k,mode:state.mode,page:state.page}));}catch(e){}}
function measure(state){
 var flow=flowOf(state);if(!flow)return;
 var width=state.window.clientWidth||1000,gap=40;flow.style.setProperty('--page-width',width+'px');flow.style.width=width+'px';
 flow.style.setProperty('--page-height',(state.window.clientHeight||480)+'px');
 state.stride=width+gap;state.pages=countPages(width,flow.scrollWidth||width,gap);state.page=Math.min(Math.max(0,state.page),state.pages-1);
 flow.style.transform='translateX('+(-state.page*state.stride)+'px)';
 state.pageLabel.textContent='Page '+(state.page+1)+' / '+state.pages;state.pagePrev.disabled=state.page===0;state.pageNext.disabled=state.page>=state.pages-1;
 state.modeButton.textContent=state.mode==='overview'?'Details':'Visual overview';state.modeButton.setAttribute('aria-label',state.mode==='overview'?'Show full explanation':'Return to visual overview');
 if(state.index!==undefined){var u=U[state.index],total=U.filter(function(x){return x.route===u.route}).length,pos=U.filter(function(x,i){return i<=state.index&&x.route===u.route}).length;
  if(state.index===cur){document.getElementById('progT').textContent=(u.route==='core'?'Concept ':u.route==='study'?'Study ':'Tool ')+pos+' / '+total;updateLectureControls();}}
}
function show(state){
 if(state.summary)state.summary.hidden=state.mode!=='overview';state.details.hidden=state.mode==='overview'&&!!state.summary;
 measure(state);persist(state);
}
function setPage(state,page){if(!state)return;state.page=Math.max(0,Math.min(page,state.pages-1));show(state);var live=document.getElementById('tLive');if(live)live.textContent='Page '+(state.page+1)+' of '+state.pages;}
function focusPage(state,target){
 if(!state||!target||!target.isConnected)return;
 if(state.summary&&!state.summary.contains(target)){state.mode='details';show(state)}
 var f=flowOf(state),r=target.getClientRects()[0],fr=f.getBoundingClientRect();
 if(r&&state.stride)setPage(state,Math.floor((r.left-fr.left+2)/state.stride));
}
function diagram(nodes,kind){
 var d=el('div','v3-diagram '+(kind==='flow'?'flow':'compare'));d.style.setProperty('--node-count',Math.min(nodes.length,5));d.setAttribute('role','group');d.setAttribute('aria-label',kind==='flow'?'Concept sequence':'Concept comparison');
 nodes.forEach(function(n){var box=el('div','v3-node');box.append(el('strong','',n[0]));if(n[1])box.append(el('span','',n[1]));d.append(box)});return d;
}
function copySvg(svg,suffix){
 var copy=svg.cloneNode(true),ids={};copy.querySelectorAll('[id]').forEach(function(n){ids[n.id]=n.id+'-'+suffix;n.id=ids[n.id]});
 copy.querySelectorAll('*').forEach(function(n){Array.from(n.attributes).forEach(function(a){var value=a.value;Object.keys(ids).forEach(function(id){value=value.replaceAll('url(#'+id+')','url(#'+ids[id]+')');if(value==='#'+id)value='#'+ids[id]});if(value!==a.value)n.setAttribute(a.name,value)})});
 copy.setAttribute('role','img');return copy;
}
function buildSummary(state){
 var u=U[state.index],spec=story.units[u.k],out=state.summary;if(!out)return;out.replaceChildren();
 if(u.k==='READING'){
  var intro=el('p','','Before the assignment and next discussion. Calendar dates are in Blackboard.');out.append(intro);
  LECTURE.study.readings.forEach(function(r){var card=el('section','v3-reading'),h=el('h2','',r[0]),p=el('p','','Required source slides '+r[1]+'–'+r[2]),links=el('div','lp-actions');
   for(var number=r[1];number<=r[2];number++){var b=el('button','lp-btn','Slide '+number);b.type='button';b.dataset.sourceSlide=number;links.append(b)}card.append(h,p,links);out.append(card);
  });var actions=el('div','lp-actions'),check=el('button','lp-btn','Check the five objectives');check.dataset.jump='PREP';actions.append(check);out.append(actions);return;
 }
 if(u.k==='TITLE'||u.k==='START'){
  var c=el('section','v3-case'),opening=story.opening;c.append(el('div','v3-case-label',u.k==='TITLE'?'ISCARB · PROFESSOR ADEEB NOOR':'FICTIONAL TEACHING CASE'));
  c.append(el('h2','',u.k==='TITLE'?plain(LECTURE.title):opening.headline));c.append(el('p','',u.k==='TITLE'?opening.headline:opening.case));
  if(u.k==='START')c.append(el('p','v3-decision',opening.question));
  var route=el('div','v3-mini-route');(u.k==='TITLE'?['See the problem','Explain the mechanism','Test your thinking','Defend a decision']:opening.nodes).forEach(function(t){route.append(el('span','',t))});c.append(route);
  if(u.k==='TITLE'){var a=el('div','lp-actions'),start=el('button','lp-btn','Start the case');start.dataset.jump='START';a.append(start);c.append(a)}
  if((state.window.clientWidth&&state.window.clientWidth<560)||(state.window.clientHeight&&state.window.clientHeight<480)){c.classList.add('v3-case-pages')}out.append(c);return;
 }
 if(!spec)return;
 var image=typeof FIG!=='undefined'&&FIG[spec.visual],native=null;
 if(!image&&['props','layers','rd'].includes(spec.visual))native=state.details.querySelector('.figwrap svg');
 var windowHeight=state.window.clientHeight||480,width=state.window.clientWidth||1000;
 // Split the diagram into labelled pages on compact screens instead of shrinking it.
 var maxNodes=width<560?Math.max(1,Math.min(3,Math.floor((windowHeight-110)/78))):5;
 var chunks=[];if(image||native)chunks=[spec.nodes];else for(var i=0;i<spec.nodes.length;i+=maxNodes)chunks.push(spec.nodes.slice(i,i+maxNodes));
 chunks.forEach(function(nodes,part){
  var page=el('section','v3-summary'),picture=el('div','v3-picture');
  if(image){picture.classList.add('has-source');var img=el('img');img.src=image;img.alt=plain(u.title)+'. '+spec.nodes.map(function(n){return n.join(': ')}).join('; ');picture.append(img)}
  else if(native){picture.classList.add('has-source');var svg=copySvg(native,'visual-'+state.index);svg.setAttribute('aria-label',plain(u.title));picture.append(svg)}
  else picture.append(diagram(nodes,spec.visual));
  page.append(picture,el('p','v3-takeaway',spec.takeaway+(chunks.length>1?' ('+(part+1)+'/'+chunks.length+')':'')));out.append(page);
  if(windowHeight<230){page.classList.add('v3-compact-summary');}
 });
}
function prepareSlide(u,i){
 var slide=deck.querySelector('[data-i="'+i+'"]'),fitEl=slide.querySelector('.fit'),area=slide.querySelector('.area'),top=slide.querySelector('.top');
 if(!top){top=el('div','top');fitEl.prepend(top)}
 var title=top.querySelector('h1');if(!title){title=el('h1');top.prepend(title)}
 title.textContent=u.k==='TITLE'?'A decision you can explain':u.k==='START'?'Start with the problem':u.k==='END'?'Before the assignment':plain(u.title||LECTURE.title);
 var sub=top.querySelector('.sub');var windowEl=el('div','v3-window'),details=el('div','v3-flow'),summary=null;
 details.dataset.view='explanation';if(sub){sub.classList.remove('sub');details.append(sub)}
 while(area.firstChild)details.append(area.firstChild);
 var task=fitEl.querySelector(':scope > .taskstrip');if(task){task.classList.remove('taskstrip');task.classList.add('v3-task');details.append(task)}
 transformTables(details);
 details.querySelectorAll('.lp-source-section').forEach(function(section){section.open=true;});
 var state={index:i,window:windowEl,details:details,page:0,pages:1,mode:'details',stride:1040};
 if(u.k==='TITLE'||u.k==='START'||u.k==='READING'||story.units[u.k]){summary=el('div','v3-flow');summary.dataset.view='overview';state.summary=summary;state.mode='overview';windowEl.append(summary)}
 windowEl.append(details);area.replaceWith(windowEl);fitEl.append(toolbar(state));states.set(i,state);
 var ribbon=fitEl.querySelector('.lp-ribbon');if(ribbon){var step=u.k==='TITLE'?'START':u.k==='START'?'SEE':u.k.startsWith('CHECK')?'TEST':u.k==='APPLY'?'DECIDE':u.k==='END'?'TRANSFER':u.route==='core'?'EXPLAIN':u.route==='study'?'PREPARE':'EXPLORE';ribbon.append(el('span','v3-step',step));}
 if(summary)buildSummary(state);show(state);
}
U.forEach(prepareSlide);
[['prevBtn','Previous page or concept'],['nextBtn','Next page or concept']].forEach(function(item){var button=document.getElementById(item[0]);button.setAttribute('aria-label',item[1]);button.title=item[1];});
function directionAvailable(dir){var route=U[cur].route;for(var j=cur+dir;j>=0&&j<U.length;j+=dir)if(U[j].route===route&&!U[j].showIf)return true;return false;}
updateLectureControls=function(){var s=states.get(cur);document.getElementById('prevBtn').disabled=(!s||s.page===0)&&!directionAvailable(-1);document.getElementById('nextBtn').disabled=(!s||s.page>=s.pages-1)&&!directionAvailable(1);};
go=function(i,force){
 var s=states.get(cur),dir=i>cur?1:-1;
 if(!force&&s&&((dir>0&&s.page<s.pages-1)||(dir<0&&s.page>0))){setPage(s,s.page+dir);return;}
 oldGo(i,force);s=states.get(cur);if(s){s.page=0;show(s);if(!force&&dir<0)setPage(s,s.pages-1);}
};
function layout(){var s=states.get(cur);if(s){if(s.summary)buildSummary(s);show(s)}var ov=document.querySelector('.ov.on');if(ov&&overlays.has(ov.id))show(overlays.get(ov.id));}
fit=function(){oldFit();layout()};fitSlide=function(){var s=states.get(cur);if(s)measure(s)};
function schedule(){if(resizePending)return;resizePending=true;requestAnimationFrame(function(){resizePending=false;layout();if(sourceTarget){var target=sourceTarget;sourceTarget=null;focusPage(states.get(cur),target)}});}
window.addEventListener('resize',schedule);document.addEventListener('fullscreenchange',schedule);document.addEventListener('load',function(e){if(e.target.tagName==='IMG')schedule()},true);
if(typeof ResizeObserver!=='undefined'){var observer=new ResizeObserver(schedule);observer.observe(deck);}
// Preserve existing quiz, text-entry and reveal listeners; only reflow their result.
document.addEventListener('click',function(e){
 var answer=e.target.closest('[data-answer-toggle],[data-qanswer]');
 if(answer){var id=answer.dataset.answerToggle||answer.dataset.qanswer,box=document.querySelector('[data-answer-box="'+id+'"],[data-qanswer-box="'+id+'"]');if(box&&!box.hidden)sourceTarget=box;schedule();}
 var b=e.target.closest('[data-source-slide]');if(b){var section=document.getElementById('source-slide-'+b.dataset.sourceSlide);if(section){sourceTarget=section;schedule()}}
 if(e.target.closest('#checkPrep'))schedule();
});
document.addEventListener('toggle',function(e){if(e.target.matches('.lp-source-section')){sourceTarget=e.target;schedule()}},true);
document.addEventListener('focusin',function(e){var s=active();if(s&&flowOf(s).contains(e.target))focusPage(s,e.target)});
document.addEventListener('iscarb-source-focus',function(e){sourceTarget=document.getElementById('source-slide-'+e.detail);schedule()});
function prepareOverlay(id){
 var ov=document.getElementById(id),win=ov.querySelector('.oscroll');if(!win)return;
 var existing=overlays.get(id);if(existing&&existing.details.isConnected){show(existing);return;}
 var tools=ov.querySelector('.tools');if(tools)tools.remove();ov.querySelectorAll('.v3-overlay-footer').forEach(function(n){n.remove()});
 var flow=el('div','v3-flow');while(win.firstChild)flow.append(win.firstChild);win.append(flow);transformTables(flow);
 var state={window:win,details:flow,mode:'details',page:0,pages:1,stride:1040};var footer=el('div','v3-overlay-footer');if(tools)footer.append(tools);footer.append(toolbar(state));ov.append(footer);overlays.set(id,state);show(state);
}
openOv=function(id){oldOpen(id);document.querySelector('.lp-top').inert=true;prepareOverlay(id);};
closeOv=function(id){oldClose(id);document.querySelector('.lp-top').inert=false;};
// A downloaded copy is initialized again when opened. Remove generated chrome
// so it cannot accumulate duplicate navigation or nested pagination containers.
var originalDownloadText=downloadText;
downloadText=function(text,name,type){
 if(type==='text/html'){
  var copy=new DOMParser().parseFromString(text,'text/html');
  copy.querySelectorAll('.lp-top,.lp-zoom').forEach(function(n){n.remove()});
  copy.querySelectorAll('.ov').forEach(function(ov){
   var footer=ov.querySelector('.v3-overlay-footer'),tools=footer&&footer.querySelector('.tools');
   if(tools)ov.append(tools);if(footer)footer.remove();
   ov.querySelectorAll('.v3-flow').forEach(function(flow){flow.replaceWith.apply(flow,Array.from(flow.childNodes))});
  });
  text='<!doctype html>\n'+copy.documentElement.outerHTML;
  name='Ch'+LECTURE.path.chapter+'-iSCARB-with-work.html';
 }
 return originalDownloadText(text,name,type);
};
document.addEventListener('keydown',function(e){var ov=document.querySelector('.ov.on');if(!ov||/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)||e.ctrlKey||e.metaKey||e.altKey)return;var s=overlays.get(ov.id);if(s&&(e.key==='PageDown'||e.key==='PageUp')){e.preventDefault();setPage(s,s.page+(e.key==='PageDown'?1:-1));}},true);
// Small, testable pagination contract; dimensions come from the browser at runtime.
window.ISCARB_PAGES={count:countPages,current:function(){var s=active();return s?{page:s.page,pages:s.pages,mode:s.mode,key:U[cur].k}:null;},refresh:layout,goPage:function(n){setPage(active(),n)},explain:function(){var s=states.get(cur);if(s&&s.summary){s.mode='details';s.page=0;show(s)}}};
// Hash links take priority. Old per-unit bookmarks continue to work unchanged.
if(resume&&location.hash.slice(1)===resume.key){var s=states.get(cur);if(s){s.mode=resume.mode==='details'?'details':s.summary?'overview':'details';s.page=Math.max(0,Number(resume.page)||0)}}
initializing=false;layout();
})();
