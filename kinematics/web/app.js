'use strict';
let level, state, currentLesson = 'describe', tab = 'journey', activeBoss = null;
let saveTimer, timer;
let page = 'course', catalogue;
const $ = (q, root = document) => root.querySelector(q);
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, data) {
  const res = await fetch(path, data === undefined ? {cache:'no-store'} : {method:'POST', headers:{'Content-Type':'application/json','X-Local-Request':'1'},body:JSON.stringify(data)});
  const result = await res.json();
  if (!res.ok) throw new Error(result.error || 'The request could not be completed.');
  return result;
}
function toast(message) { $('#toast').textContent=message;$('#toast').classList.add('visible');setTimeout(()=>$('#toast').classList.remove('visible'),3500); }
function updateProgress() {
  const n=Object.values(state.checks).filter(x=>x.correct===x.total).length;
  $('#xp').textContent=`✦ ${state.xp} XP`;
  $('#progress-count').textContent=`${n} / 6`;
  $('#progress-bar').style.width=`${100*n/6}%`;
  $('#sidebar-progress').textContent=`${n} of 6 checkpoints complete`;
  $('#lesson-nav').innerHTML=level.lessons.map((l,i)=>`<button class="lesson-link ${l.id===currentLesson && tab==='learn'?'selected':''}" data-lesson="${l.id}"><span class="lesson-number ${state.completed.includes(l.id)?'done':''}">${state.completed.includes(l.id)?'✓':String(i+1).padStart(2,'0')}</span><span>${esc(l.title)}<small>${l.optional?'Optional extension':`${l.minutes} min · ${l.checkpoint && state.checks[l.checkpoint] && state.checks[l.checkpoint].correct===state.checks[l.checkpoint].total?'Practiced':'Learn & practice'}`}</small></span>${l.optional?'<span class="tiny">↗</span>':''}</button>`).join('');
}
function sourceChips(refs) {
  return refs.map(([id,page])=>`<button class="source-chip" data-source="${id}" data-page="${page}"><span>▤</span> ${esc(level.sources[id].title)} · p. ${page} ↗</button>`).join('');
}
function render() {
  document.body.dataset.section=tab;
  clearInterval(timer);
  window.scrollTo({top:0,behavior:'instant'});
  updateShell();
  updateProgress();
  window.dispatchEvent(new Event('page-context-changed'));
  if(page!=='level')return renderPortal();
  document.querySelectorAll('[data-tab]').forEach(b=>{const selected=b.dataset.tab===tab;b.classList.toggle('active',selected);b.setAttribute('aria-current',selected?'page':'false');});
  if(tab==='learn')renderLesson();
  if(tab==='practice')renderPractice();
  if(tab==='boss')renderBoss();
  if(tab==='review')renderReview();
  if(tab==='journey'){renderJourney();mountPublishedPacks();}
}
function renderLesson() {
  const l=level.lessons.find(l=>l.id===currentLesson), index=level.lessons.indexOf(l);
  $('#content').innerHTML=`<div class="study-layout"><article class="lesson-card"><div class="card-meta"><span>UNIT ${String(index+1).padStart(2,'0')} <span class="meta-dot">·</span> ${l.minutes} MIN READ</span><span class="pill">${l.optional?'Optional · not scored':'Teaching draft'}</span></div><h2>${esc(l.title)}</h2><p class="lesson-subtitle">${esc(l.subtitle)}</p><div class="objective"><span>YOUR GOAL</span>${esc(l.objective)}</div>${l.body.map(p=>`<p class="lesson-body">${esc(p)}</p>`).join('')}<div class="formula-box">${l.formulas.map(f=>`<div>${esc(f)}</div>`).join('')}</div><section class="example"><h3>A concrete example</h3><p>${esc(l.example)}</p><small>Authored teaching example · review pending</small></section><div class="source-list"><span class="eyebrow">CHECK THE ORIGINAL</span>${sourceChips(l.references)}</div><div class="lesson-actions"><button class="button secondary" data-action="complete" data-id="${l.id}">${state.completed.includes(l.id)?'✓ Read':'Mark as read'}</button>${l.checkpoint?`<button class="button primary checkpoint-button" data-action="go-practice" data-id="${l.checkpoint}">Try the checkpoint <span>→</span></button>`:`<button class="button primary" data-tab="boss">Try the level boss →</button>`}</div>${index<level.lessons.length-1?`<button class="next-link" data-lesson="${level.lessons[index+1].id}">Next: ${esc(level.lessons[index+1].title)} →</button>`:''}</article><aside class="study-aside"><div class="aside-card reminder"><div class="aside-symbol">↗</div><h3>Keep an eye on this</h3><p>${esc(l.pitfall)}</p></div><div class="aside-card"><div class="eyebrow">YOUR WORKING NOTES</div><h3>Make it click.</h3><label for="notes" class="sr-only">Private local study notes</label><textarea id="notes" placeholder="A question, an intuition, a step to revisit…" maxlength="12000">${esc(state.notes)}</textarea><button class="text-button" data-action="save-notes">Save note ↗</button><p class="small muted">Saved for this browser session on this Mac. No AI processing.</p></div>${l.id==='projectile'?motionLab():`<div class="aside-card quiet-card"><span class="small">ALREADY FEELING READY?</span><h3>Take the short route.</h3><p>Jump straight to a checkpoint or challenge. Reading every unit is optional.</p><button class="text-button" data-tab="boss">Explore the boss →</button></div>`}</aside></div>`;
  if(l.id==='projectile')drawTrajectory();
}
function motionLab(){return `<div class="aside-card"><div class="eyebrow">MOTION LAB</div><h3>Change the launch.</h3><svg id="trajectory" viewBox="0 0 260 140" role="img" aria-label="Projectile path with no air resistance"></svg><label for="launch-angle">Launch angle <strong id="angle-value">45°</strong></label><input id="launch-angle" type="range" min="10" max="80" value="45"><p class="small muted">v₀ = 20 m/s · g = 9.8 m/s²<br>Equal launch and landing heights.</p><div id="lab-result" class="small"></div></div>`;}
function drawTrajectory(){const input=$('#launch-angle');if(!input)return;const angle=Number(input.value),a=angle*Math.PI/180,v=20,g=9.8,T=2*v*Math.sin(a)/g,R=v*Math.cos(a)*T;let d='';for(let i=0;i<=50;i++){const t=T*i/50,x=v*Math.cos(a)*t,y=v*Math.sin(a)*t-0.5*g*t*t;d+=`${i?'L':'M'}${(15+x*5.5).toFixed(2)},${(125-y*5.5).toFixed(2)} `;}$('#trajectory').innerHTML=`<path d="M10 125H250 M15 130V10" class="lab-axis"/><path d="${d}" class="lab-path"/>`;$('#angle-value').textContent=`${angle}°`;$('#lab-result').textContent=`Range ${R.toFixed(1)} m · flight time ${T.toFixed(2)} s`;}
function inputs(q, prefix='', answers={}) {return `<div class="answer-grid">${q.fields.map(f=>`<label>${esc(f.label)}<span class="answer-input"><input name="${prefix}${f.id}" value="${esc(answers[f.id] ?? '')}" inputmode="decimal" autocomplete="off" placeholder="Your value" aria-label="${esc(f.label)} in ${esc(f.unit)}"><span>${esc(f.unit)}</span></span></label>`).join('')}</div>`;}
function renderPractice(){
  $('#content').innerHTML=`<div class="section-heading"><div><div class="eyebrow">TEST AN IDEA, FIND A GAP</div><h2>Your checkpoints</h2><p>Enter numbers in the displayed units. Hints are welcome; assisted practice is recorded separately.</p></div><span class="pill">Numeric feedback · draft guides</span></div><div class="checkpoint-list">${Object.entries(level.checkpoints).map(([id,q],i)=>{const result=state.checks[id];return `<article class="checkpoint-card" id="${id}"><div class="card-meta"><span>CHECKPOINT ${String(i+1).padStart(2,'0')}</span>${result?`<span class="pill ${result.correct===result.total?'green':''}">${result.correct}/${result.total} values · ${result.assisted?'assisted':'no hints'}</span>`:''}</div><h3>${esc(q.title)}</h3><p>${esc(q.prompt)}</p><form data-check="${id}">${inputs(q)}<div class="form-actions"><button type="button" class="text-button" data-hint="${id}">Give me a hint</button><button class="button primary" type="submit">Check my answer →</button></div></form><div class="hint-box" id="hint-${id}" hidden></div><div id="feedback-${id}" class="feedback" aria-live="polite"></div><details class="provenance"><summary>Question provenance</summary><p>${esc(q.provenance)}</p></details><div class="question-signal"><label class="sr-only" for="signal-${id}">Question feedback category</label><select id="signal-${id}"><option value="unclear_wording">The wording is unclear</option><option value="missing_theory">I need more theory</option><option value="wrong_reference">The reference may be wrong</option></select><button class="text-button" data-report-question="${id}">Flag for reviewer</button></div></article>`;}).join('')}</div>`;
}
function renderBoss(){
  if(activeBoss)return renderAttempt();
  const previous=state.bosses.filter(b=>b.submitted);
  $('#content').innerHTML=`<section class="boss-intro"><div class="boss-emblem">↗</div><div class="eyebrow">THE LEVEL BOSS</div><h2>The motion challenge</h2><p>${esc(level.boss.intro)}</p><div class="boss-facts"><span>2 tasks</span><span>7 answer values</span><span>Projectiles + circular motion</span></div><div class="mode-grid"><article><span class="mode-icon">◎</span><h3>Practice mode</h3><p>Take your time. Ask for staged hints, then review the worked feedback after submission.</p><button class="button primary" data-start="practice">Start practice →</button></article><article><span class="mode-icon">◷</span><h3>Exam simulation</h3><p>25 minutes. No hints or feedback until final submission. Answers autosave; this is not proctored.</p><button class="button secondary" data-start="simulation">Start simulation →</button></article></div>${previous.length?`<div class="attempt-history"><h3>Your previous attempts</h3>${previous.map(b=>`<button class="history-row" data-resume="${b.id}"><span>${b.mode==='simulation'?'Exam simulation':'Practice'}</span><span>${b.grade.correct}/${b.grade.total} values <span class="muted">· review →</span></span></button>`).join('')}</div>`:''}</section>`;
}
function renderAttempt(){
  const b=activeBoss;
  $('#content').innerHTML=`<div class="attempt-toolbar"><button class="text-button" data-action="leave-boss">← Challenge overview</button><span class="pill">${b.mode==='simulation'?'Exam simulation':'Practice mode'}${b.submitted?' · submitted':''}</span>${b.mode==='simulation'&&!b.submitted?'<strong id="countdown" role="timer"></strong>':''}</div>${b.submitted?`<div class="result-banner"><div class="eyebrow">ATTEMPT COMPLETE</div><h2>${b.grade.correct} of ${b.grade.total} values correct</h2><p>${b.grade.correct/b.grade.total>=0.8?'A useful readiness signal. Review the reasoning before moving on.':'Use the worked feedback to choose a focused retry.'} This checks final numeric values, not complete reasoning or official mastery.${b.grade.expired?' Time expired; your last saved answers were assessed.':''}</p></div>`:''}<form id="boss-form"><div class="checkpoint-list">${level.boss.questions.map(q=>{const feedback=b.feedback?.find(f=>f.id===q.id);return `<article class="checkpoint-card"><h3>${esc(q.title)}</h3><p>${esc(q.prompt)}</p>${inputs(q,q.id+'.',b.answers[q.id]||{})}${!b.submitted&&b.mode==='practice'?`<button type="button" class="text-button" data-boss-hint="${q.id}">Give me a hint</button><div class="hint-box" id="boss-hint-${q.id}" hidden></div>`:''}${feedback?`<div class="feedback ${feedback.correct===feedback.total?'success':''}"><strong>${feedback.correct}/${feedback.total} values correct</strong><p>${esc(q.solution||feedback.solution)}</p>${fieldFeedback(q,feedback)}</div>`:''}<details class="provenance"><summary>Question provenance</summary><p>${esc(q.provenance)}</p></details></article>`;}).join('')}</div>${!b.submitted?`<div class="submit-bar"><span id="autosave-status" class="muted small">Your answers will autosave as you type.</span><button class="button primary" type="submit">Submit the whole attempt →</button></div>`:'<div class="form-actions"><button type="button" class="button secondary" data-action="leave-boss">Return to challenge overview</button><button type="button" class="button primary" data-tab="practice">Practice a gap →</button></div>'}</form>`;
  if(b.submitted)$('#boss-form').querySelectorAll('input').forEach(i=>i.disabled=true);
  if(!b.submitted&&b.mode==='simulation'){
    const tick=()=>{const left=Math.max(0,Math.ceil(b.deadline-Date.now()/1000));$('#countdown').textContent=`${Math.floor(left/60)}:${String(left%60).padStart(2,'0')} left`;if(!left){clearInterval(timer);submitBoss(true).catch(e=>toast(e.message));}};
    tick();if(!b.submitted)timer=setInterval(tick,1000);
  }
}
function fieldFeedback(q,g){return `<ul class="field-results">${g.fields.map(f=>`<li class="${f.correct?'right':'wrong'}">${f.correct?'✓':'↺'} ${esc(q.fields.find(x=>x.id===f.id).label)}: ${f.correct?'within tolerance':'revisit'}</li>`).join('')}</ul>`;}
function renderReview(){
  $('#content').innerHTML=`<article class="lesson-card review-card"><div class="eyebrow">REVIEWER WORKSPACE</div><h2>A clear boundary around the draft.</h2><p>Only kinematics has been constructed. These are authored teaching notes and adapted questions based on your course files. Nothing is labeled professor-approved.</p><ul class="review-list">${level.review_notes.map(n=>`<li>${esc(n)}</li>`).join('')}</ul><h3>What this version can do</h3><p>Read seven units, view selected original lecture pages, work through six checkpoints, save notes, earn limited XP and complete a two-task boss. Progress is stored locally for this browser's session cookie.</p><h3>Report an ambiguity</h3><form id="report-form"><label for="report">Which question or explanation needs attention?</label><textarea id="report" required maxlength="2000" placeholder="Describe the item and what seems unclear…"></textarea><button class="button secondary">Save a local review issue →</button></form><p class="small muted">This saves a local record. It does not send email or notify a professor.</p></article>`;
}
async function showSource(id,page){const d=$('#source-dialog');$('#source-title').textContent=`${level.sources[id].title} · page ${page}`;$('#source-error').textContent='';const img=$('#source-image');img.onerror=()=>{$('#source-error').textContent='The page preview is unavailable. Run the source preparation command in the README.';};img.src=`/source/${encodeURIComponent(id)}/${Number(page)}`;d.showModal();}
function collect(form){return Object.fromEntries(new FormData(form).entries());}
function bossAnswers(){const flat=collect($('#boss-form')),answers={};for(const q of level.boss.questions){answers[q.id]={};for(const f of q.fields)answers[q.id][f.id]=flat[q.id+'.'+f.id]||'';}return answers;}
async function saveBoss(){if(!activeBoss||activeBoss.submitted||!$('#boss-form'))return;const answers=bossAnswers(),result=await api('/api/boss/save',{id:activeBoss.id,answers});activeBoss.answers=answers;if(result.submitted){activeBoss=result;state=await api('/api/state');render();}else if($('#autosave-status'))$('#autosave-status').textContent='Saved on this Mac.';}
async function submitBoss(expired=false){
  if(!activeBoss||activeBoss.submitted)return;
  clearTimeout(saveTimer);clearInterval(timer);
  const button=$('#boss-form button[type="submit"]');if(button)button.disabled=true;
  try{const b=await api('/api/boss/submit',{id:activeBoss.id,answers:bossAnswers()});activeBoss=b;state=b.state;render();toast(expired?'Time finished. Saved work assessed.':'Attempt saved. Your feedback is ready.');}
  catch(e){if(button)button.disabled=false;throw e;}
}
document.addEventListener('click',async e=>{
  const b=e.target.closest('button');if(!b)return;
  try{
    if(b.dataset.tab){if(activeBoss&&!activeBoss.submitted&&$('#boss-form'))await saveBoss();tab=b.dataset.tab;render();return;}
    if(b.dataset.lesson){currentLesson=b.dataset.lesson;tab='learn';render();return;}
    if(b.dataset.source)return await showSource(b.dataset.source,b.dataset.page);
    if(b.id==='close-source')return $('#source-dialog').close();
    if(b.dataset.action==='complete'){state=await api('/api/complete',{id:b.dataset.id});render();toast('Marked as read. Checkpoints provide separate practice evidence.');}
    if(b.dataset.action==='go-practice'){tab='practice';render();$('#'+b.dataset.id).scrollIntoView({behavior:'smooth',block:'start'});}
    if(b.dataset.action==='save-notes'){state.notes=$('#notes').value;await api('/api/notes',{notes:state.notes});toast('Note saved on this Mac.');}
    if(b.dataset.hint){const r=await api('/api/hint',{id:b.dataset.hint});const box=$('#hint-'+b.dataset.hint);box.hidden=false;box.textContent=r.hint;}
    if(b.dataset.start){b.disabled=true;try{activeBoss=await api('/api/boss/start',{mode:b.dataset.start});render();}catch(error){b.disabled=false;throw error;}}
    if(b.dataset.resume){activeBoss=await api('/api/boss/'+b.dataset.resume);render();}
    if(b.dataset.bossHint){const r=await api('/api/boss/hint',{id:activeBoss.id,question:b.dataset.bossHint});const box=$('#boss-hint-'+b.dataset.bossHint);box.hidden=false;box.textContent=r.hint;}
    if(b.dataset.action==='leave-boss'){if(!activeBoss.submitted)await saveBoss();activeBoss=null;state=await api('/api/state');render();}
  }catch(error){toast(error.message);}
});
document.addEventListener('submit',async e=>{
  const form=e.target;
  if(!form.dataset.check&&!['boss-form','report-form'].includes(form.id))return;
  e.preventDefault();
  try{
    if(form.dataset.check){const button=$('button[type="submit"]',form);button.disabled=true;try{const id=form.dataset.check,r=await api('/api/check',{id,answers:collect(form)});state=r.state;updateProgress();const box=$('#feedback-'+id);box.className='feedback '+(r.correct===r.total?'success':'');box.innerHTML=`<strong>${r.correct}/${r.total} values correct${r.assisted?' · assisted practice':''}</strong>${fieldFeedback(level.checkpoints[id],r)}<p>${esc(r.misconception)}</p><details><summary>Review the worked feedback</summary><p>${esc(r.solution)}</p></details><p class="small muted">Numeric checks against draft guides. No full reasoning assessment.</p>`;}finally{button.disabled=false;}}
    if(form.id==='boss-form')await submitBoss();
    if(form.id==='report-form'){await api('/api/report',{text:$('#report').value,item:'kinematics-review'});form.reset();toast('Review issue saved locally.');}
  }catch(error){toast(error.message);}
});
document.addEventListener('input',e=>{
  if(e.target.id==='launch-angle')drawTrajectory();
  if(e.target.closest('#boss-form')&&activeBoss&&!activeBoss.submitted){clearTimeout(saveTimer);if($('#autosave-status'))$('#autosave-status').textContent='Saving…';saveTimer=setTimeout(()=>saveBoss().catch(error=>toast(error.message)),500);}
});
async function init(){
  // Establish the session cookie before fetching session-specific data.
  level=await api('/api/level');state=await api('/api/state');
  catalogue=await api('/api/course');
  readRoute();
  const pending=state.bosses.filter(b=>!b.submitted).sort((a,b)=>b.started-a.started)[0];
  if(pending){activeBoss=await api('/api/boss/'+pending.id);tab='boss';}
  render();
  if(page==='studio')await loadStudio();if(page==='agents'||page==='work')await loadAgents();
}
