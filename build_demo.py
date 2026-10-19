"""Builds site/index.html: an interactive REPLAY of two recorded runs (approve branch, deny branch). Sponsor modes are as recorded."""
import json, os, datetime, vigil, adapters
CALL = "Hi, my father just passed at home. We think he wanted cremation. Call me at 916-555-0142."
NOW = datetime.datetime(2026, 10, 20, 2, 10)   # simulated clock: a 2:10 AM call
yes = vigil.run(CALL, vigil.Director(lambda g, c, x: True), now=NOW)
no = vigil.run(CALL, vigil.Director(lambda g, c, x: False), now=NOW)
COL = ["#6b8cae", "#8a6bae", "#ae8a6b", "#6bae8a", "#ae6b7e", "#7e7e7e"]
def calls(r): return [dict(sponsor=c["sponsor"], action=c["action"], mode=c["mode"].upper(), reason=c["reason"]) for c in r["sponsor_calls"]]
import base64
AV = {"Mara": "mara", "Quinn": "quinn", "Sol": "sol", "Paige": "paige", "Faye": "faye", "Vera": "vera"}
IMG = {k: "data:image/jpeg;base64," + base64.b64encode(open(f"avatars/{v}.jpg", "rb").read()).decode() for k, v in AV.items()}
data = json.dumps({"home": vigil.GPL["home"], "img": IMG, "voice": {k: v for k, v in {"Mara": "mara", "Quinn": "quinn", "Sol": "sol", "Paige": "paige", "Faye": "faye", "Vera": "vera"}.items()}, "office": {"Mara": "Front office", "Faye": "Front office", "Quinn": "Back office", "Sol": "Back office", "Paige": "Back office", "Vera": "Back office"}, "staff": [{"name": n, "role": r, "color": COL[i]} for i, (n, r) in enumerate(vigil.STAFF)],
    "yes": {"trace": yes["trace"], "calls": calls(yes), "outcome": yes["outcome"]}, "no": {"trace": no["trace"], "calls": calls(no), "outcome": no["outcome"]},
    "ts": datetime.datetime.now().strftime("%b %d %Y %H:%M local")})
page = """<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>Vigil - AI night staff (FICTIONAL demo)</title><style>
body{font:15px system-ui;margin:0;background:#12151a;color:#e8e8e8}header{padding:16px 24px;background:#1b2028}
.banner{background:#7a4b00;color:#fff;padding:8px 24px;font-weight:600}
main{display:grid;grid-template-columns:260px 1fr 340px;gap:16px;padding:16px}@media(max-width:900px){main{grid-template-columns:1fr}}
.card{background:#1b2028;border-radius:10px;padding:12px;margin-bottom:10px}
.av{display:inline-block;width:34px;height:34px;border-radius:50%;object-fit:cover;margin-right:8px;vertical-align:middle;background:#555}.pl{background:#2a3340;color:#e8e8e8;border:0;border-radius:6px;padding:2px 8px;cursor:pointer}.handoff{border-left:3px solid #4aa3ff;background:#161c24;padding:6px 10px;margin:4px 0 4px 18px;border-radius:6px}.bigav{width:64px;height:64px;border-radius:12px;object-fit:cover;float:left;margin-right:10px}.cap{color:#9aa;font-size:11px}
.msg{border-left:4px solid #444;padding:8px 12px;margin:8px 0;background:#1b2028;border-radius:6px}
.approval{border-color:#e0b000}.check{border-color:#4aa3ff}.request{border-color:#ccc}.improve{border-color:#55d68a}
.tag{font-size:11px;text-transform:uppercase;opacity:.7}button{padding:10px 18px;border:0;border-radius:8px;font-weight:700;cursor:pointer;margin-right:8px}
.go{background:#55d68a}.deny{background:#e06060;color:#fff}small{opacity:.75}.REAL{color:#55d68a}.EXTERNAL{color:#4aa3ff}.FALLBACK{color:#e0b000}</style>
<div class=banner>FICTIONAL DATA. This page REPLAYS two recorded runs (recorded __TS__, simulated clock 2:10 AM). Sponsor modes are as recorded: REAL / EXTERNAL / SIMULATED / FALLBACK. No real call is placed, no real person is involved.</div>
<header><b>Vigil</b> - AI night staff for funeral homes &middot; <span id=home></span> &middot; <button class=go id=play>Start the 2:10 AM call</button></header>
<main><div><h3>Org chart</h3><div class=card><b>Director (human)</b><br><small>approves family messages and dispatch</small></div><div id=staff></div>
<div class=card><small>Six LLM-driven agents (OpenAI gpt-4o-mini, $3 cap): each makes one decision plus a short in-character line. The gates, prices, callback time and approvals are deterministic code, and the Director (human) approves. Front office: Mara, Faye. Back office: Quinn, Sol, Paige, Vera. Avatars and voices are AI-generated and fictional.</small></div></div>
<div><h3>Night desk</h3><div id=feed></div></div>
<div><h3>Sponsor tools (as recorded)</h3><div id=calls></div></div></main>
<script>const VP=location.pathname.endsWith('demo.html')?'site/voice/':'voice/';const D=__DATA__;home.textContent=D.home;
const col=Object.fromEntries(D.staff.map(s=>[s.name,s.color]));
staff.innerHTML=D.staff.map(s=>`<div class=card><img class=bigav src="${D.img[s.name]}" alt="${s.name}"><b>${s.name}</b> ${s.role}<br><small>reports to Director</small><br><span class=cap>${D.office[s.name]} &middot; LLM-driven (gpt-4o-mini)</span><br><button class=pl onclick="sayit('${s.name}',this)">&#9654; voice</button> <span class=cap>avatar: Masky (AI, fictional) &middot; voice: OpenAI TTS (AI-generated)</span><div style=clear:both></div></div>`).join('');
let au=null;function sayit(n,b){if(au)au.pause();au=new Audio(VP+D.voice[n]+".mp3");au.play();}
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function card(t){if(t.phase=='handoff')return `<div class="msg handoff"><span class=tag>handoff</span> <b>${esc(t.msg)}</b><br><small>passes: ${esc((t.fields||[]).join(', '))} &middot; ${esc(t.evidence||'')}</small></div>`;let ex=t.quote?`<br><small>`+Object.entries(t.quote).map(([k,v])=>esc(k.replace(/_/g,' '))+': $'+v).join(' | ')+`</small>`:'';
return `<div class="msg ${t.phase}"><span class=tag>${t.phase}</span><br><img class=av src="${D.img[t.who]||''}" alt=""><b>${t.who}</b>: ${esc(t.msg)}${ex}</div>`}
function showCalls(list){calls.innerHTML=list.map(c=>`<div class=card><b>${c.sponsor}</b> <small>${c.action} [<span class=${c.mode}>${c.mode}</span>]</small><br><small>${esc(c.reason||'')}</small></div>`).join('')}
let i=0,branch=null;const A=D.yes.trace;const gate=A.findIndex(t=>t.phase=='approval');
function step(){if(i<gate){feed.insertAdjacentHTML('beforeend',card(A[i++]));showCalls(D.yes.calls.slice(0,Math.ceil(i*D.yes.calls.length/A.length)));setTimeout(step,800);return}
feed.insertAdjacentHTML('beforeend',`<div class="msg approval"><span class=tag>approval needed</span><br><b>Director</b>: Approve sending the family message and dispatching the removal team?<br><br><button class=go id=ap>Approve</button><button class=deny id=dn>Deny</button></div>`);
ap.onclick=()=>fin('yes');dn.onclick=()=>fin('no')}
function fin(b){ap.disabled=dn.disabled=true;const T=D[b].trace;let j=gate;showCalls(D[b].calls);
(function n(){if(j>=T.length)return;feed.insertAdjacentHTML('beforeend',card(T[j++]));setTimeout(n,700)})()}
play.onclick=()=>{feed.innerHTML='';i=0;step()};</script>"""
page = page.replace("__DATA__", data).replace("__TS__", json.loads(data)["ts"])
os.makedirs("site", exist_ok=True)
for p in ("site/index.html", "demo.html"):
    with open(p, "w") as f: f.write(page)
print("built", yes["outcome"], no["outcome"], "gate index", [t["phase"] for t in yes["trace"]].index("approval"))
