'use strict';
// Illustrations stay native SVG: crisp, lightweight and no external asset calls.
function worldArt(number, live=false){
 const n=Number(number), palettes=['#7650df','#427dcb','#dc8754','#4a9a86','#6c65c5','#c38542','#479cb3','#d16f76','#9080bd'];
 const color=palettes[(n-1)%palettes.length];
 const motifs=[
  '<path d="M64 104Q125 6 211 73" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="5 7"/><path d="M162 50l24-11-10 24-1-15z" fill="#e9ff9c"/><circle cx="209" cy="73" r="9" fill="#ffbd6b"/>',
  '<path d="M97 86l21-42 38 19-21 42z" fill="#c5e9ff"/><path d="M141 49l38-22m-14 1 14-1-6 13" fill="none" stroke="#fcdb93" stroke-width="5"/>',
  '<path d="M60 72q15-45 30 0t30 0 30 0 30 0 30 0" fill="none" stroke="#f8e8bd" stroke-width="5"/>',
  '<circle cx="103" cy="72" r="24" fill="#c4f4dc"/><circle cx="164" cy="69" r="18" fill="#ffcb86"/><path d="M82 36l25 9m45 55 25 8" stroke="white" stroke-width="3"/>',
  '<ellipse cx="140" cy="72" rx="70" ry="29" transform="rotate(-22 140 72)" fill="none" stroke="#cecaff" stroke-width="3"/><circle cx="140" cy="72" r="25" fill="#e9dbff"/><circle cx="199" cy="45" r="8" fill="#f5cb7f"/>',
  '<circle cx="137" cy="70" r="33" fill="#f1d6ae" stroke="#fff" stroke-width="4"/><path d="M137 37v66m-33-33h66m-56-23 47 47m0-47-47 47" stroke="#a57546" stroke-width="3"/>',
  '<path d="M60 65q15-16 30 0t30 0 30 0 30 0 30 0M60 85q15-16 30 0t30 0 30 0 30 0 30 0" fill="none" stroke="#d6faff" stroke-width="5"/>',
  '<path d="M129 38v46a18 18 0 1 0 20 0V38a10 10 0 0 0-20 0z" fill="#ffe0bc"/><path d="M139 50v49" stroke="#df6f70" stroke-width="7"/>',
  '<path d="M97 88V47h66v41z" fill="none" stroke="#eee4ff" stroke-width="5"/><path d="M110 38l13 8-13 7m40 28-13 8 13 7" fill="none" stroke="#ffe0a0" stroke-width="4"/>'
 ];
 return `<div class="world-art ${live?'world-live':''}" aria-hidden="true"><svg viewBox="0 0 280 166"><ellipse cx="140" cy="139" rx="100" ry="16" fill="${color}" opacity=".12"/><path d="M39 98 139 62 241 98 141 143Z" fill="${color}"/><path d="M39 98v18l102 37v-10z" fill="${color}" opacity=".78"/><path d="M141 143v10l100-37V98z" fill="${color}" opacity=".55"/><path d="M53 96 139 66 227 96 141 127Z" fill="white" opacity=".12"/><g class="world-motif">${motifs[(n-1)%motifs.length]}</g><path d="M54 39v12m-6-6h12m168 65v10m-5-5h10" stroke="${color}" stroke-width="2"/><circle cx="218" cy="31" r="3" fill="#e9ad65"/></svg></div>`;
}
function renderJourney(){
 const done=id=>Boolean(state.checks[id]&&state.checks[id].correct===state.checks[id].total);
 $('#content').innerHTML=`<section class="journey-intro"><div><div class="eyebrow">LEVEL 01 · KINEMATICS</div><h1>Your mission: master motion.</h1><p>Choose your route. Read, practice, or head straight to the boss.</p></div><div class="journey-legend"><span><i></i> Theory</span><span><i></i> Checkpoint</span><span><i></i> Boss</span></div></section><div class="journey-world"><div class="journey-sky" aria-hidden="true"><span>✦</span><span>✧</span><span>✦</span></div><div class="journey-route">${level.lessons.filter(l=>!l.optional).map((l,i)=>`<article class="journey-stage"><div class="stage-landscape">${worldArt(i+1,true)}</div><div class="stage-copy"><span class="stage-index">STAGE ${String(i+1).padStart(2,'0')}</span><h3>${esc(l.title)}</h3><p>${esc(l.subtitle)}</p><div class="stage-buttons"><button class="theory-node ${state.completed.includes(l.id)?'cleared':''}" data-lesson="${l.id}"><span>${state.completed.includes(l.id)?'✓':'▤'}</span> Theory <small>${l.minutes} min</small></button><span class="stage-connector" aria-hidden="true">···</span><button class="checkpoint-node ${done(l.checkpoint)?'cleared':''}" data-action="go-practice" data-id="${l.checkpoint}"><span>${done(l.checkpoint)?'✓':'⚑'}</span> Checkpoint ${i+1}<small>${done(l.checkpoint)?'Complete':'Practice · +XP'}</small></button></div></div></article>`).join('')}<article class="journey-boss"><div class="boss-crown" aria-hidden="true">♜</div><div><span class="stage-index">FINAL ENCOUNTER</span><h3>The motion challenge</h3><p>Projectiles + circular motion. Practice freely or try a timed simulation.</p></div><button class="button primary" data-tab="boss">Challenge the boss ↗</button></article><button class="optional-stage" data-lesson="coordinates">✧ Side quest: polar & cylindrical coordinates <span>Optional →</span></button></div></div>`;
}
