'use strict';
let currentUser=null;
let adminSetupToken=new URLSearchParams(location.hash.slice(1)).get('token')||'';
if(location.pathname==='/setup'&&location.hash)history.replaceState({},'','/setup');
function setIdentity(user){
 currentUser=user;document.body.dataset.auth=user?'signed-in':'guest';document.body.dataset.role=user?.role||'';
 document.querySelectorAll('[data-admin-only]').forEach(el=>el.hidden=user?.role!=='admin');
 if(!user)return;
 $('#auth-screen').hidden=true;
 $('#profile-avatar').textContent=user.name.split(/\s+/).map(s=>s[0]).slice(0,2).join('').toUpperCase();
 $('#profile-avatar').title=user.name+' · '+user.role;
 $('#account-role').textContent=user.role==='admin'?'ADMIN':'STUDENT';
 if($('#tutor-language'))$('#tutor-language').value=user.language;
}
async function loadIdentity(){
 const r=await api('/api/auth');setIdentity(r.user);
 if(!r.user){renderAuth();return false;}
 return true;
}
function guardRoute(){
 if((page==='studio'||page==='agents')&&currentUser.role!=='admin'){
  history.replaceState({},'','/course/physics-1');readRoute();render();toast('This workspace is only available to the administrator.');return false;
 }
 return true;
}
function renderAuth(){
 const mode=location.pathname==='/register'?'register':location.pathname==='/setup'?'setup':'login';
 const signup=mode!=='login',setup=mode==='setup';
 document.title=(setup?'Set up your admin account':signup?'Join your class':'Welcome back')+' · Fieldnotes';
 document.body.dataset.auth='guest';
 const host=$('#auth-screen');host.hidden=false;
 host.innerHTML=`<main class="auth-layout"><section class="auth-story"><a class="brand" href="/login"><span class="brand-mark">φ</span><span>fieldnotes<span class="brand-sub">A LITTLE MOMENTUM, EVERY DAY.</span></span></a><div><span class="auth-kicker">PHYSICS I · YOUR NEXT CHAPTER</span><h1>Big ideas.<br>Small steps.<br><em>Your momentum.</em></h1><p>A learning path that meets you where you are.<br>Bring your curiosity. Keep your progress.</p><div class="auth-orbit" aria-hidden="true"><span>↗</span><i></i><b>v = Δr / Δt</b></div></div><p class="auth-footer">English sources. Explanations in your language.</p></section><section class="auth-form-panel"><div class="auth-form-card"><span class="eyebrow">${setup?'PRIVATE ADMIN SETUP':signup?'JOIN THE COHORT':'YOUR LEARNING CONTINUES'}</span><h2>${setup?'Your teaching workspace.':signup?'Make room for discovery.':'Good to see you again.'}</h2><p>${setup?'Create the only administrator account. This private link works once.':signup?'Create your student account and start exploring Physics I.':'Sign in for your saved progress, private notes, and tutor.'}</p>${!setup?`<nav class="auth-tabs" aria-label="Account access"><a class="${!signup?'active':''}" href="/login">Sign in</a><a class="${signup?'active':''}" href="/register">Student registration</a></nav>`:''}<form id="account-form" data-mode="${mode}"><div id="account-error" class="account-error" role="alert" hidden></div>${signup?'<label>Your name<input name="name" autocomplete="name" required maxlength="80" placeholder="What should we call you?"></label>':''}<label>Email<input type="email" name="email" autocomplete="username" required maxlength="254" placeholder="you@example.com"></label><label>Password<input type="password" name="password" autocomplete="${signup?'new-password':'current-password'}" required ${signup?'minlength="12"':''} maxlength="128" placeholder="${signup?'At least 12 characters':'Your password'}"></label>${signup?'<label>Confirm password<input type="password" name="confirm_password" autocomplete="new-password" required minlength="12" maxlength="128"></label><label>Explain concepts in<input name="language" value="English" maxlength="50" required list="profile-languages"></label><datalist id="profile-languages"><option>English</option><option>Italian</option><option>Turkish</option><option>Spanish</option><option>French</option><option>Arabic</option><option>Chinese</option></datalist>':''}<button type="submit" class="button primary">${setup?'Create my admin account':signup?'Create student account':'Sign in'} <span>↗</span></button></form><p class="auth-account-note">${setup?'Administrator access is provisioned privately and cannot be selected during student registration.':signup?'All new registrations are students. Your work and tutor history belong to your account.':'This prototype stores accounts locally on this Mac.'}</p></div></section></main>`;
 if(setup&&!adminSetupToken){$('#account-error').hidden=false;$('#account-error').textContent='Open your private setup link from the local account_setup.py command. Administrator access cannot be claimed here without that link.';$('button[type="submit"]',host).disabled=true;}
}
function renderProfile(){
 const u=currentUser,admin=u.role==='admin';
 $('#content').innerHTML=`<section class="profile-hero"><div><div class="hero-kicker"><span></span> YOUR ACCOUNT</div><h1>Hello, <em>${esc(u.name.split(/\s+/)[0])}.</em></h1><p>Your pace. Your preferences. Your progress, wherever you sign in.</p></div><div class="profile-medallion">${esc($('#profile-avatar').textContent)}<span>${admin?'ADMIN':'STUDENT'}</span></div></section><div class="profile-grid"><section class="studio-panel"><div class="eyebrow">THE BASICS</div><h2>Make it yours.</h2><form id="profile-form" class="profile-form"><label>Your name<input name="name" value="${esc(u.name)}" required maxlength="80" autocomplete="name"></label><label>Email<input value="${esc(u.email)}" type="email" readonly><small>Your sign-in email</small></label><label>Explanation language<input name="language" value="${esc(u.language)}" maxlength="50" required></label><div class="profile-access"><span>${admin?'✦':'↗'}</span><div><strong>${admin?'Administrator':'Student'}</strong><p>${admin?'You manage course materials, review content, and publish learning packs.':'Explore lessons, take checkpoints, ask your tutor, and keep your working private.'}</p></div></div><p id="profile-message" role="status"></p><button class="button primary" type="submit">Save profile ↗</button></form></section><div><section class="studio-panel profile-progress"><div class="eyebrow">YOUR MOMENTUM</div><h2>Every step counts.</h2><strong>${state.xp}<small> XP earned</small></strong><p>${Object.values(state.checks).filter(c=>c.correct===c.total).length} of 6 Kinematics checkpoints complete.</p><button class="button secondary" data-route="/levels/kinematics">Continue learning ↗</button></section><section class="studio-panel password-panel"><div class="eyebrow">ACCOUNT SECURITY</div><h2>Change password</h2><form id="password-form" class="profile-form"><label>Current password<input name="current_password" type="password" autocomplete="current-password" required maxlength="128"></label><label>New password<input name="password" type="password" autocomplete="new-password" minlength="12" maxlength="128" required></label><label>Confirm new password<input name="confirm_password" type="password" autocomplete="new-password" minlength="12" maxlength="128" required></label><p class="small muted">Changing your password signs out your other sessions.</p><p id="password-message" role="status"></p><button class="button secondary" type="submit">Update password</button></form></section></div></div>${admin?'<section class="studio-panel student-roster"><div class="eyebrow">YOUR CLASSROOM</div><h2>Registered students</h2><p class="small muted">Student accounts have no course studio or publishing access.</p><div id="student-roster">Loading students…</div></section>':''}`;
 if(admin)loadStudentRoster();
}
async function loadStudentRoster(){
 try{const r=await api('/api/admin/students');const host=$('#student-roster');if(!host)return;
 host.innerHTML=r.students.length?`<div class="roster-scroll"><table><thead><tr><th>Name</th><th>Email</th><th>Explanation language</th><th>Role</th></tr></thead><tbody>${r.students.map(s=>`<tr><td>${esc(s.name)}</td><td>${esc(s.email)}</td><td>${esc(s.language)}</td><td>Student</td></tr>`).join('')}</tbody></table></div>`:'<div class="empty-roster">Your cohort starts here. Students can register at <a href="/register">/register</a>.</div>';
 }catch(e){if($('#student-roster'))$('#student-roster').textContent=e.message;}
}
document.addEventListener('submit',async e=>{
 const form=e.target;if(!['account-form','profile-form','password-form'].includes(form.id))return;
 e.preventDefault();const button=$('button[type="submit"]',form),data=Object.fromEntries(new FormData(form));button.disabled=true;
 const message=form.id==='account-form'?$('#account-error'):form.id==='profile-form'?$('#profile-message'):$('#password-message');message.hidden=true;
 try{
  if((form.id==='password-form'||form.dataset.mode!=='login'&&form.id==='account-form')&&data.password!==data.confirm_password)throw new Error('The passwords do not match.');
  delete data.confirm_password;
  if(form.id==='account-form'){
   if(form.dataset.mode==='setup')data.token=adminSetupToken;
   await api('/api/auth/'+form.dataset.mode,data);adminSetupToken='';location.replace('/course/physics-1');
  }else if(form.id==='profile-form'){
   const r=await api('/api/profile',data);setIdentity(r.user);$('.profile-hero h1').innerHTML=`Hello, <em>${esc(r.user.name.split(/\s+/)[0])}.</em>`;$('.profile-medallion').innerHTML=`${esc($('#profile-avatar').textContent)}<span>${r.user.role==='admin'?'ADMIN':'STUDENT'}</span>`;message.textContent='Profile saved. Your tutor will use your preferred language.';message.hidden=false;
  }else{await api('/api/profile/password',data);form.reset();message.textContent='Password updated. Other sessions have been signed out.';message.hidden=false;}
 }catch(error){message.textContent=error.message;message.hidden=false;}
 finally{button.disabled=false;}
});
document.addEventListener('click',async e=>{
 const button=e.target.closest('[data-sign-out]');if(!button)return;
 button.disabled=true;
 try{await api('/api/auth/logout',{});location.replace('/login');}catch(error){toast(error.message);button.disabled=false;}
});
window.addEventListener('pageshow',e=>{if(e.persisted)location.reload();});
