import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';

// Static publication builder: public split-delivery pages must not depend on runtime fetch.
const root = process.cwd();
const lec = path.join(root, 'lectures', 'iscarb');

function read(rel){ return fs.readFileSync(path.join(root, rel), 'utf8'); }
function write(rel, txt){ fs.writeFileSync(path.join(root, rel), txt, 'utf8'); }

function loadPatch(prefix){
  const encoded = [1,2,3]
    .map(i => read(`lectures/iscarb/split/${prefix}.patch.${i}.txt`).trim())
    .join('');
  const json = zlib.gunzipSync(Buffer.from(encoded, 'base64')).toString('utf8');
  return JSON.parse(json);
}

function applyPatches(source, patches, label){
  let out = source;
  patches.forEach(([oldText,newText], idx) => {
    const first = out.indexOf(oldText);
    if(first < 0) throw new Error(`${label}: patch ${idx+1} did not match`);
    if(out.indexOf(oldText, first+1) >= 0) throw new Error(`${label}: patch ${idx+1} is ambiguous`);
    out = out.slice(0, first) + newText + out.slice(first + oldText.length);
  });
  return out;
}

function buildFaculty(baseFile, outFile, patchPrefix, label){
  const base = read(`lectures/iscarb/${baseFile}`);
  const out = applyPatches(base, loadPatch(patchPrefix), label);
  if(out.includes('DecompressionStream') || out.includes("fetch('./")){
    throw new Error(`${label}: generated faculty file still contains runtime split-loader code`);
  }
  write(`lectures/iscarb/${outFile}`, out);
  console.log(`${label}: wrote ${out.length} chars -> ${outFile}`);
}

function buildCh11Student(){
  let x = read('lectures/iscarb/Ch10-FBR-Student-Assignment.html');
  const replacements = [
    ['Chapter 10 · Dependable Systems','Chapter 11 · Reliability Engineering'],
    ['A coastal desalination control upgrade went live at 22:14 during peak demand. Pump P-204 is throwing intermittent high-pressure alarms. The backup train switches over automatically. At shift handover, an operator silenced a repeating alarm to read the log. The regulator’s file says the system is safe under normal operation; tonight is not normal operation.','A supplier clause promises “99.9% reliability” for a critical software service. The number has reached a contract review, but the clause does not state the failure event, operational profile, observation window, repair-time assumption, or whether degraded operation counts as available.'],
    ['Which dependability property or engineering mechanism should govern the decision now, and why is it fit for this professional use?','Which reliability metric or requirement form should govern this use, and why is it fit for the failure mode and decision being made?'],
    ['State the professional action or artifact you would actually produce now (for example: hold/continue/revert decision, requirement, architecture change, monitoring action, or signed recommendation).','Write the actual reliability clause, monitor, test condition, or process requirement you would place into the engineering artifact.'],
    ['What concrete evidence would make this action defensible to another engineer, operator, regulator, or reviewer?','What measurement, log, test, observation window, or signed evidence would make the requirement defensible?'],
    ['A post-deployment dependency check shows that both RO trains rely on the same pressure transmitter used by the alarm logic. The two trains are physically separate, but the sensed condition that triggers protection is not independent.','After the clause is drafted, the vendor changes the definition of “available” so that degraded mode counts as available. The numerical target can remain 99.9%, but the operational meaning of the number has changed.'],
    ['The new fact may leave the underlying knowledge true while changing whether the current action is still fit for use.','Do not change the clause merely because something changed. Decide whether this change crosses the applicability boundary you stated.'],
    ['If your response is REVISE or REPLACE, write the revised signed engineering decision / architecture or monitoring change. If RETAIN, state why the original artifact remains fit.','If your response is REVISE or REPLACE, write the revised measurable reliability clause / monitor / process requirement. If RETAIN, state why the original artifact remains fit.'],
    ['fbr-assignment-ch10-v1','fbr-assignment-ch11-v1'],
    ['Ch10_FBR_','Ch11_FBR_']
  ];
  for(const [a,b] of replacements){
    if(!x.includes(a)) throw new Error(`Ch11 student: replacement source missing: ${a.slice(0,80)}`);
    x = x.split(a).join(b);
  }
  if(x.includes("fetch('./Ch10-FBR-Student-Assignment.html")) throw new Error('Ch11 student: runtime wrapper survived');
  write('lectures/iscarb/Ch11-FBR-Student-Assignment.html', x);
  console.log(`Ch11 student: wrote ${x.length} chars`);
}

buildFaculty('Ch10-Dependable-Systems.html','Ch10-Dependable-Systems-Faculty.html','ch10-faculty','Ch10 faculty');
buildFaculty('Ch11-Reliability-Engineering.html','Ch11-Reliability-Engineering-Faculty.html','ch11-faculty','Ch11 faculty');
buildCh11Student();
