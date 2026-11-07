'use strict';
let tutorOpen=false,tutorBusy=false,tutorMessages=[],tutorStatus=null,tutorCheckpoint=null,tutorPending=null;
const tutorHost=document.createElement('div');tutorHost.id='tutor-host';
tutorHost.innerHTML=`<button id="tutor-launcher" class="tutor-launcher" aria-expanded="false" aria-controls="tutor-panel"><span aria-hidden="true">✦</span><span>Ask your tutor<small>A little help. A big leap.</small></span><span class="tutor-launch-arrow" aria-hidden="true">↗</span></button><section id="tutor-panel" class="tutor-panel" role="region" aria-label="Your learning tutor" hidden><header class="tutor-header"><span class="tutor-avatar" aria-hidden="true">✦</span><div><h2>Your learning tutor</h2><span>Curious questions welcome.</span></div><button id="tutor-close" type="button" aria-label="Close tutor">×</button></header><div class="tutor-context"><span class="tutor-context-dot"></span><span id="tutor-context-label">Physics I · course overview</span></div><div class="tutor-options"><label for="tutor-language">Explain in</label><input id="tutor-language" value="English" maxlength="50" list="tutor-languages" aria-label="Explanation language"><datalist id="tutor-languages"><option>English</option><option>Italian</option><option>Turkish</option><option>Spanish</option><option>French</option><option>Arabic</option><option>Chinese</option></datalist><span>English source terms</span></div><div id="tutor-messages" class="tutor-messages" role="log" aria-label="Tutor conversation" aria-live="polite"></div><div id="tutor-error" class="tutor-error" role="alert" hidden></div><form id="tutor-form"><label class="sr-only" for="tutor-message">Ask your tutor</label><textarea id="tutor-message" required maxlength="2500" rows="2" placeholder="Ask about this page, a concept, or a tricky step…"></textarea><div class="tutor-compose-bottom"><span id="tutor-meter">Low-cost mode · no background calls</span><button id="tutor-send" type="submit" aria-label="Send question">↑</button></div></form><p class="tutor-privacy">AI explanations can be wrong. Questions + selected course context go to OpenAI. Notes and other students’ chats stay private.</p></section>`;
document.body.append(tutorHost);
function tutorContext(){const work=typeof page==='string'&&page==='work'&&typeof agentData!=='undefined'?agentData?.records.find(r=>r.id===selectedWork):null;const workCheckpoint=work?.payload.question;const source=$('#source-dialog')?.open?$('#source-image').getAttribute('src').split('/'):null;return {source:source?{id:source[2],page:Number(source[3])}:null,course:typeof studioId==='string'?studioId:null,page:typeof page==='string'?(page==='agents'?'studio':page==='work'?'level':page):'course',section:page==='work'?'practice':typeof tab==='string'?tab:'journey',lesson:workCheckpoint&&level?.checkpoints[workCheckpoint]?.lesson|| (typeof currentLesson==='string'?currentLesson:'describe'),checkpoint:workCheckpoint&&level?.checkpoints[workCheckpoint]?workCheckpoint:tutorCheckpoint,work:work?.id||null};}
function updateTutorContext(){
 const context=tutorContext();let label='Physics I · course overview';
 if(context.page==='studio')label='Course studio · draft setup';
 if(context.page==='level'){
  const lesson=level?.lessons.find(l=>l.id===context.lesson);
  label=context.section==='learn'?`Kinematics · ${lesson?.title||'Theory'}`:context.section==='practice'?`Kinematics · ${context.checkpoint?level?.checkpoints[context.checkpoint]?.title:'Checkpoints'}`:context.section==='boss'?'Kinematics · level boss':context.section==='journey'?'Kinematics · level map':'Kinematics · review';
 }
 $('#tutor-context-label').textContent=label;
}
function tutorText(text){return esc(text).replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>').split(/\n\n+/).map(p=>`<p>${p.replace(/\n/g,'<br>')}</p>`).join('');}
function renderTutorMessages(){
 const list=$('#tutor-messages');
 list.innerHTML=`<div class="tutor-welcome"><span>LET’S MAKE IT CLICK</span><h3>A question is a good start.</h3><p>I can help with the page you’re viewing, explain a concept in your language, or guide a practice step.</p><div class="tutor-suggestions"><button type="button" data-tutor-suggest="Explain the main idea on this page with a simple example.">Explain this page ↗</button><button type="button" data-tutor-suggest="Ask me one short question to see what I already understand about this topic.">Check my understanding ↗</button></div></div>${tutorMessages.map(m=>`<article class="tutor-turn"><div class="tutor-user">${tutorText(m.question)}</div><div class="tutor-answer"><span class="tutor-answer-label">✦ ${m.blocked?'SIMULATION IN PROGRESS':m.execution==='offline'?'OFFLINE COURSE NOTES':'YOUR TUTOR'}</span>${tutorText(m.answer)}${m.citations?.length?`<div class="tutor-citations"><span>Evidence · authority labeled below</span>${m.citations.map(c=>c.authority==='collective'&&!c.url?`<small>Reviewed cohort FAQ · supplement</small>`:`<button type="button" ${c.url?`data-evidence-url="${esc(c.url)}" data-evidence-title="${esc(c.title)}"`:`data-source="${esc(c.source)}" data-page="${c.page}"`}>▤ ${esc(c.title)}${c.page?` · p. ${c.page}`:''} · ${c.authority==='collective'?'Supplement':'Lecture'} ↗</button>`).join('')}</div>`:'<small class="tutor-authority">General guidance · no official excerpt cited</small>'}</div></article>`).join('')}${tutorBusy?'<div class="tutor-thinking" role="status"><span>✦</span> Finding a clear way through…</div>':''}`;
 list.scrollTop=list.scrollHeight;
}
async function openTutor(){
 tutorOpen=true;$('#tutor-error').hidden=true;$('#tutor-panel').hidden=false;$('#tutor-launcher').hidden=true;$('#tutor-launcher').setAttribute('aria-expanded','true');updateTutorContext();
 try{const r=await api('/api/tutor');tutorStatus=r.status;tutorMessages=r.messages;renderTutorMessages();$('#tutor-meter').textContent=`Low-cost mode · $${r.status.spent_usd.toFixed(4)} / $${r.status.session_cap_usd.toFixed(2)}`;if(r.status.execution==='offline')$('#tutor-meter').textContent='Offline preview · paid calls disabled';if(!r.status.available)throw new Error('Tutor not enabled. Check your project .env configuration.');}
 catch(e){$('#tutor-error').textContent=e.message;$('#tutor-error').hidden=false;}
 $('#tutor-message').focus();
}
function closeTutor(){tutorOpen=false;$('#tutor-panel').hidden=true;$('#tutor-launcher').hidden=false;$('#tutor-launcher').setAttribute('aria-expanded','false');$('#tutor-launcher').focus();}
$('#tutor-launcher').addEventListener('click',openTutor);$('#tutor-close').addEventListener('click',closeTutor);
window.addEventListener('page-context-changed',()=>{tutorCheckpoint=null;updateTutorContext();if(tutorOpen&&typeof activeBoss!=='undefined'&&activeBoss?.mode==='simulation'&&!activeBoss.submitted){tutorMessages=[];renderTutorMessages();}});
document.addEventListener('focusin',e=>{const form=e.target.closest('form[data-check]');if(form){tutorCheckpoint=form.dataset.check;updateTutorContext();}});
document.addEventListener('click',e=>{const b=e.target.closest('[data-tutor-suggest]');if(b){$('#tutor-message').value=b.dataset.tutorSuggest;$('#tutor-message').focus();}const cp=e.target.closest('[data-action="go-practice"]');if(cp){tutorCheckpoint=cp.dataset.id;updateTutorContext();}if(e.target.closest('[data-source],#close-source'))updateTutorContext();});
$('#tutor-message').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('#tutor-form').requestSubmit();}});
$('#tutor-panel').addEventListener('keydown',e=>{if(e.key==='Escape')closeTutor();});
$('#tutor-form').addEventListener('submit',async e=>{
 e.preventDefault();if(tutorBusy)return;
 const message=$('#tutor-message').value.trim();if(!message)return;
 const payload={message,context:tutorContext(),language:$('#tutor-language').value.trim()||'English'};
 // Retrying an identical message uses its ID; a timed-out request cannot double-bill.
 const fingerprint=JSON.stringify(payload);if(!tutorPending||tutorPending.fingerprint!==fingerprint)tutorPending={fingerprint,id:crypto.randomUUID()};
 tutorBusy=true;$('#tutor-send').disabled=true;$('#tutor-error').hidden=true;renderTutorMessages();
 try{const result=await api('/api/tutor/messages',{...payload,id:tutorPending.id});tutorMessages.push(result);$('#tutor-message').value='';tutorPending=null;
  const r=await api('/api/tutor');tutorStatus=r.status;$('#tutor-meter').textContent=r.status.execution==='offline'?'Offline preview · paid calls disabled':`Low-cost mode · $${r.status.spent_usd.toFixed(4)} / $${r.status.session_cap_usd.toFixed(2)}`;
 }catch(error){$('#tutor-error').textContent=error.message;$('#tutor-error').hidden=false;}
 finally{tutorBusy=false;$('#tutor-send').disabled=false;renderTutorMessages();}
});
renderTutorMessages();
