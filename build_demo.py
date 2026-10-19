import json, vigil, adapters
rep = vigil.run("Hi, my father just passed at home. We think he wanted cremation. Call me at 916-555-0142.", vigil.Director(lambda g,c,x: True))
trace = rep["trace"]; calls = [dict(sponsor=c["sponsor"],action=c["action"],mode=c["mode"].upper(),reason=c["reason"]) for c in rep["sponsor_calls"]]
COL=["#6b8cae","#8a6bae","#ae8a6b","#6bae8a","#ae6b7e","#7e7e7e"]
staff = [{"name":n,"role":r,"reports":"Director","color":COL[i],"tools":[]} for i,(n,r) in enumerate(vigil.STAFF)]
data = json.dumps({"home":vigil.GPL["home"],"trace":trace,"staff":staff,"calls":calls,"sponsors":{a.name:a.job for a in adapters.registry().values()},"local":rep["local_real"]})
page = """<!doctype html><meta charset=utf-8><title>Vigil demo</title><style>
body{font:15px system-ui;margin:0;background:#12151a;color:#e8e8e8}header{padding:16px 24px;background:#1b2028}
.banner{background:#7a4b00;color:#fff;padding:8px 24px;font-weight:600}
main{display:grid;grid-template-columns:300px 1fr 320px;gap:16px;padding:16px}
.card{background:#1b2028;border-radius:10px;padding:12px;margin-bottom:10px}
.av{display:inline-block;width:34px;height:34px;border-radius:50%;text-align:center;line-height:34px;font-weight:700;color:#fff;margin-right:8px;vertical-align:middle}
.msg{border-left:4px solid #444;padding:8px 12px;margin:8px 0;background:#1b2028;border-radius:6px}
.approval{border-color:#e0b000}.check{border-color:#4aa3ff}.request{border-color:#ccc}.improve{border-color:#55d68a}
.tag{font-size:11px;text-transform:uppercase;opacity:.7}button{padding:10px 18px;border:0;border-radius:8px;background:#55d68a;font-weight:700;cursor:pointer}
small{opacity:.7}</style>
<div class=banner>FICTIONAL DATA. Each sponsor card shows its true mode for this run (REAL / SIMULATED / FALLBACK / EXTERNAL). No real call is placed, no real person.</div>
<header><b>Vigil</b> - AI night staff for funeral homes &middot; <span id=home></span> &middot; <button id=play>Play the loop</button></header>
<main><div><h3>Org chart</h3><div class=card><b>Director (human, approves sensitive actions)</b></div><div id=staff></div></div>
<div><h3>Night desk (request, delegate, act, check, approve, report, improve)</h3><div id=feed></div></div>
<div><h3>Sponsor tools (mode per this run)</h3><div id=calls></div></div></main>
<script>const D=__DATA__;home.textContent=D.home;
const col=Object.fromEntries(D.staff.map(s=>[s.name,s.color]));
staff.innerHTML=D.staff.map(s=>`<div class=card><span class=av style=background:${s.color}>${s.name[0]}</span><b>${s.name}</b> ${s.role}<br><small>reports to ${s.reports}</small></div>`).join('');
let i=0;function next(){if(i>=D.trace.length)return;const t=D.trace[i++];
let extra=t.quote?`<br><small>`+Object.entries(t.quote).map(([k,v])=>k.replace(/_/g,' ')+': $'+v).join(' | ')+`</small>`:'';
feed.insertAdjacentHTML('beforeend',`<div class="msg ${t.phase}"><span class=tag>${t.phase}</span><br><span class=av style="background:${col[t.who]||'#555'}">${t.who[0]}</span><b>${t.who}</b>: ${t.msg}${extra}</div>`);
calls.innerHTML=D.calls.slice(0,Math.min(D.calls.length,Math.ceil(i*D.calls.length/D.trace.length))).map(c=>`<div class=card><b>${c.sponsor}</b> <small>${c.action} [${c.mode}]</small><br><small>${c.reason}</small></div>`).join('');
setTimeout(next,900)}
play.onclick=()=>{feed.innerHTML='';i=0;next()};</script>"""
open("demo.html","w").write(page.replace("__DATA__",data))
