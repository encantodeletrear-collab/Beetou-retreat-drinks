#!/usr/bin/env python3
"""Build the GitHub Pages site (Firebase version) from page.html."""
import os, re, sys

SRC = os.path.join(os.path.dirname(__file__), 'page.html')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
os.makedirs(OUT, exist_ok=True)
h = open(SRC, encoding='utf-8').read()

FB = '10.12.2'
head_extra = f'''<link rel="manifest" href="__MANIFEST__">
<meta name="theme-color" content="#F1ECE2">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="__APPNAME__">
<link rel="apple-touch-icon" href="__ICON__">
<link rel="icon" type="image/png" href="icon-192.png">
<script src="https://www.gstatic.com/firebasejs/{FB}/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/{FB}/firebase-auth-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/{FB}/firebase-firestore-compat.js"></script>
<script src="config.js"></script>
'''
h = h.replace('<title>比比家飲料舖</title>', '<title>__TITLE__</title>\n' + head_extra, 1)

# ---- order submission ----
h = h.replace(
    "function api(fn,arg){return new Promise((res,rej)=>google.script.run.withSuccessHandler(res).withFailureHandler(rej)[fn](arg))}",
    r'''/* ---------- Firebase ---------- */
let fdb=null,fauth=null;
try{if(window.FIREBASE_CONFIG&&FIREBASE_CONFIG.apiKey){firebase.initializeApp(FIREBASE_CONFIG);fdb=firebase.firestore();fauth=firebase.auth()}}catch(e){console.error(e)}
async function submitOrder(o){
  if(!fdb)throw new Error('not configured');
  const n=await fdb.runTransaction(async tx=>{
    const cref=fdb.doc('meta/counter');const c=await tx.get(cref);
    const n=(c.exists?c.data().n:0)+1;tx.set(cref,{n});
    tx.set(fdb.collection('orders').doc(),{n,no:String(n).padStart(4,'0'),name:o.name,pickup:o.pickup,items:o.items,cups:o.items.reduce((a,it)=>a+it.qty,0),done:false,at:firebase.firestore.FieldValue.serverTimestamp()});
    return n});
  return {ok:true,no:String(n).padStart(4,'0')};
}''', 1)
old_call = "try{res=await api('submitOrder',{name,pickup:`${hh}:${mm}`,items:cart.map(it=>({zh:byId[it.drinkId].zh+(it.tea?'（'+it.tea+'）':''),qty:it.qty,honey:it.sugar,ice:it.ice,note:it.note||''}))})}catch(err){res=null}"
assert old_call in h
h = h.replace(old_call, "try{res=await submitOrder({name,pickup:`${hh}:${mm}`,items:cart.map(it=>({zh:(byId[it.drinkId].zh+(it.tea?'（'+it.tea+'）':'')).slice(0,40),qty:it.qty,honey:it.sugar,ice:it.ice,note:(it.note||'').slice(0,30)}))})}catch(err){console.error(err);res=null}")

# ---- admin ----
s = h.index('/* ---------- 後台'); e = h.index('/* ---------- chrome ---------- */')
admin = r'''/* ---------- 後台 ---------- */
let allOrders=[],adminFilter='pending',unsub=null,adminMsg='',adminUser=null,adminBusy=false;
function openAdmin(){$('adminVeil').hidden=false;document.body.style.overflow='hidden';renderAdmin()}
function closeAdmin(){$('adminVeil').hidden=true;document.body.style.overflow=''}
function listen(){
  if(unsub)unsub();
  unsub=fdb.collection('orders').orderBy('at','desc').limit(300).onSnapshot(snap=>{
    allOrders=snap.docs.map(d=>{const o=d.data({serverTimestamps:'estimate'});return {...o,id:d.id,atMs:o.at?o.at.toMillis():Date.now()}});
    adminMsg='';$('pendCount').textContent=allOrders.filter(o=>!o.done).length;
    if(!$('adminVeil').hidden)renderAdmin();
    if(window.START_ADMIN)notifyNew(snap);
  },err=>{adminMsg=err.code==='permission-denied'?'這個帳號沒有後台權限':'讀取失敗：'+err.message;renderAdmin()});
}
let firstSnap=true;
function notifyNew(snap){
  if(firstSnap){firstSnap=false;return}
  const added=snap.docChanges().filter(c=>c.type==='added').length;
  if(added){toast(`收到 ${added} 筆新訂單`);try{navigator.vibrate&&navigator.vibrate(200)}catch(e){}}
}
if(fauth)fauth.onAuthStateChanged(u=>{adminUser=u;if(u){$('adminBtn').hidden=false;listen()}else{if(unsub)unsub();unsub=null;allOrders=[]}if(!$('adminVeil').hidden)renderAdmin()});
function renderAdmin(){
  const head=`<div style="display:flex;justify-content:space-between;align-items:baseline;padding:28px max(24px,env(safe-area-inset-right,0px)) 16px 24px;border-bottom:1px solid var(--rule)"><h2 style="font-family:var(--display);font-weight:400;font-size:22px;letter-spacing:.2em;margin:0">後台</h2>${window.START_ADMIN?'':'<button type="button" class="close" id="closeAdmin">close ×</button>'}</div>`;
  if(!fauth){$('adminVeil').innerHTML=`<aside class="admin">${head}<p style="padding:24px" class="note-warn">資料庫還沒設定完成。</p></aside>`;return}
  if(!adminUser){$('adminVeil').innerHTML=`<aside class="admin" role="dialog" aria-modal="true" aria-label="後台">${head}
    <form id="loginForm" style="padding:24px;display:flex;flex-direction:column;gap:12px;max-width:340px">
      <label class="f">Email<input type="text" inputmode="email" id="lgEmail" autocomplete="username"></label>
      <label class="f">密碼<input type="password" id="lgPw" autocomplete="current-password" style="width:100%;font:inherit;font-size:14px;border:1px solid var(--rule);background:var(--sheet);padding:10px 12px;color:var(--ink);border-radius:2px"></label>
      ${adminMsg?`<div class="note-warn">${esc(adminMsg)}</div>`:''}
      <button type="submit" class="primary" ${adminBusy?'disabled':''}>${adminBusy?'登入中…':'登入後台'}</button></form></aside>`;return}
  const pend=allOrders.filter(o=>!o.done);const list=adminFilter==='pending'?pend:allOrders;
  const tally={};pend.forEach(o=>(o.items||[]).forEach(it=>{const k=it.zh+' · '+it.ice;tally[k]=(tally[k]||0)+it.qty}));
  const fmt=ts=>{const d=new Date(ts);return `${d.getMonth()+1}/${d.getDate()} ${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`};
  $('adminVeil').innerHTML=`<aside class="admin" role="dialog" aria-modal="true" aria-label="後台">${head}
    <div style="flex:1;overflow-y:auto;padding:12px max(24px,env(safe-area-inset-right,0px)) 24px 24px">
      <div class="chips">${chip('af','pending',`待處理 ${pend.length}`,adminFilter==='pending')}${chip('af','all',`全部 ${allOrders.length}`,adminFilter==='all')}</div>
      ${adminMsg?`<div class="note-warn" style="margin-top:10px">${esc(adminMsg)}</div>`:''}
      ${pend.length?`<div class="tally"><span style="color:var(--ink-soft)">待做</span>${Object.entries(tally).map(([k,v])=>`<span>${esc(k)} <b>×${v}</b></span>`).join('')}</div>`:''}
      ${list.length?list.map(o=>`<div class="ord ${o.done?'done':''}">
        <div class="h"><span class="n">No.${esc(o.no)}</span><span class="who">${esc(o.name)}</span><span class="t">${fmt(o.atMs)} 下單 · ${esc(o.pickup)} 取餐</span></div>
        <ul>${(o.items||[]).map(it=>`<li>${esc(it.zh)} × ${it.qty} <small>${esc([it.honey,it.ice,it.note].filter(Boolean).join(' · '))}</small></li>`).join('')}</ul>
        <div class="chips"><button type="button" class="chip" data-oid="${esc(o.id)}">${o.done?'改回待處理':'標記完成'}</button>${o.done?`<button type="button" class="chip" data-del="${esc(o.id)}">刪除</button>`:''}</div>
      </div>`).join(''):`<div class="empty"><p>${adminFilter==='pending'?'目前沒有待處理的訂單':'還沒有人點餐'}</p></div>`}
      <p style="font-size:12.5px;color:var(--ink-soft);margin-top:20px">新訂單會自動出現。<button type="button" class="close" id="logout" style="font-size:12.5px">登出</button></p>
    </div></aside>`;
}
let delArm=null;
$('adminVeil').addEventListener('submit',async e=>{e.preventDefault();
  const em=$('lgEmail').value.trim(),pw=$('lgPw').value;if(!em||!pw)return;
  adminBusy=true;adminMsg='';renderAdmin();
  try{await fauth.signInWithEmailAndPassword(em,pw)}catch(err){adminMsg='Email 或密碼不正確'}
  adminBusy=false;renderAdmin()});
$('adminVeil').addEventListener('click',async e=>{
  if(e.target.id==='adminVeil'&&!window.START_ADMIN||e.target.id==='closeAdmin')return closeAdmin();
  if(e.target.id==='logout'){await fauth.signOut();return}
  const f=e.target.closest('.chip[data-g="af"]');if(f){adminFilter=f.dataset.v;renderAdmin();return}
  const b=e.target.closest('[data-oid]');
  if(b){b.disabled=true;const o=allOrders.find(x=>x.id===b.dataset.oid);
    try{await fdb.collection('orders').doc(o.id).update({done:!o.done})}catch(err){toast('更新失敗，請再試一次');b.disabled=false}return}
  const d=e.target.closest('[data-del]');
  if(d){if(delArm!==d.dataset.del){delArm=d.dataset.del;d.textContent='再按一次刪除';setTimeout(()=>{if(delArm===d.dataset.del){delArm=null;d.textContent='刪除'}},3000);return}
    delArm=null;try{await fdb.collection('orders').doc(d.dataset.del).delete()}catch(err){toast('刪除失敗')}}
});
$('adminBtn').addEventListener('click',openAdmin);
if(location.hash==='#admin'||window.START_ADMIN){$('adminBtn').hidden=false;openAdmin()}
window.addEventListener('hashchange',()=>{if(location.hash==='#admin'){$('adminBtn').hidden=false;openAdmin()}});
if('serviceWorker' in navigator){window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}))}

'''
h = h[:s] + admin + h[e:]
assert 'google.script' not in h

def page(title, appname, manifest, icon, admin):
    x = h.replace('__TITLE__', title).replace('__APPNAME__', appname).replace('__MANIFEST__', manifest).replace('__ICON__', icon)
    if admin:
        x = x.replace('/* ---------- Firebase ---------- */', 'window.START_ADMIN=true;\n/* ---------- Firebase ---------- */', 1)
        x = x.replace('.admin{width:min(620px,100%)', '.admin{width:100%', 1)
    return x

open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page('比比家飲料舖', '比比家', 'manifest.webmanifest', 'icon-180.png', False))
open(os.path.join(OUT, 'admin.html'), 'w', encoding='utf-8').write(page('比比家後台', '比比家後台', 'manifest-admin.webmanifest', 'icon-admin-180.png', True))
print('built', OUT)
