"""Builds site/index.html: an interactive REPLAY of two recorded runs (approve branch, deny branch). Sponsor modes are as recorded."""
import json, os, datetime, vigil, adapters
CALL = "Hi, my father just passed at home. We think he wanted cremation. Call me at 916-555-0142."
NOW = datetime.datetime(2026, 10, 20, 2, 10)   # simulated clock: a 2:10 AM call
yes = vigil.run(CALL, vigil.Director(lambda g, c, x: True), now=NOW)
no = vigil.run(CALL, vigil.Director(lambda g, c, x: False), now=NOW)
COL = ["#6b8cae", "#8a6bae", "#ae8a6b", "#6bae8a", "#ae6b7e", "#7e7e7e"]
def detail(c):
    e = c.get("evidence") or {}; s = c["sponsor"]
    if c["mode"] != "real" and c["mode"] != "external": return c["reason"]
    if s == "Tenki": return "Vera's compliance lint re-run inside a Tenki sandbox VM; verdict matched the local lint" if c["mode"] == "real" else "CI run on a Tenki runner (repo-side link)"
    if s == "Celesto": return "paperwork JSON written into a Celesto sandbox and hash-checked"
    if s == "n8n": return "dispatch ticket round trip through a live n8n workflow"
    if s == "Snyk": return "dependency scan, exit code %s" % e.get("exit_code")
    if s == "BAND": return "case update posted to a BAND room"
    if s == "Paritok": return "OpenAI calls routed through the Paritok gateway (%s requests; tokens saved: %s)" % (e.get("requests_through_gateway"), e.get("tokens_saved"))
    if s == "Glasser": return "live balance check plus one recorded research run ($%s)" % (e.get("recorded_research_run", {}).get("charge_usd"))
    if s == "Masky": return "queried the Masky API: Vigil avatar found and a speak-mode video turn rendered (0 credits charged); portraits and clips were hand-generated in Masky"
    if s == "RocketRide": return "ran vigil_intake.pipe on a live self-hosted RocketRide engine (open-source server); the engine accepted the call text and returned it parsed"
    if s == "Prelint": return "PR review ran repo-side (link)"
    return c["reason"]
def calls(r): return [dict(sponsor=c["sponsor"], action=c["action"], mode=c["mode"].upper(), reason=detail(c), link=((c.get("evidence") or {}).get("url") or (c.get("evidence") or {}).get("ci_run_url") or "")) for c in r["sponsor_calls"]]
import base64
AV = {"Mara": "mara", "Quinn": "quinn", "Sol": "sol", "Paige": "paige", "Faye": "faye", "Vera": "vera"}
IMG = {k: "data:image/jpeg;base64," + base64.b64encode(open(f"avatars/{v}.jpg", "rb").read()).decode() for k, v in AV.items()}

import llm, lint as _lint, json as _json
TEMPLATE_WORDS = {"opener": "Hello, this is the director from Maple Grove. I am calling about your father. I am so sorry for your loss.", "lines": ["I am so sorry. Thank you for calling us tonight.", "There is no rush on anything. We can go at your pace.", "Is there someone with you right now?", "When you are ready, we will go through the next steps together."]}
def words_for_call():
    """Faye proposes optional prompts; Vera's deterministic call-lines lint filters them. Source is recorded honestly."""
    src, raw, rejected, calls = "template", None, 0, []
    try:
        bud = llm.Budget()
        r = bud.chat("faye_call_words", "You are Faye, a warm family liaison at a funeral home, quietly preparing optional prompts for the funeral director, who is an experienced professional. Reply with ONLY JSON: {\"opener\": str, \"lines\": [4 str]}. Write in the first person as the director calling a family back at 7:00 AM; the caller's father died at home overnight and the family leaned toward cremation. The opener starts with 'Good morning, this is the director from Maple Grove.' and gently acknowledges the loss. The 4 lines are short, human and unhurried: one that acknowledges the loss, one that says there is no rush, one that asks if someone is with them, one that invites them to share about their father if they wish. Each under 130 characters. No promises, no prices or packages, no euphemisms like sleeping or better place, no arrangements, no coaching tone.", "Write the opener and lines.", max_tokens=260)
        d = _json.loads(r[r.index("{"):r.rindex("}") + 1])
        ops = [d.get("opener", "")] + list(d.get("lines", []))
        good = [x for x in ops if not _lint.lint_call_line(x)]
        rejected = len(ops) - len(good)
        if d.get("opener") in good and len(good) >= 4:
            raw = {"opener": d["opener"], "lines": [x for x in good if x != d["opener"]][:4]}; src = "model"; calls = bud.calls
    except Exception as e:
        src = "template"
    out = raw or TEMPLATE_WORDS
    assert all(not _lint.lint_call_line(x) for x in [out["opener"]] + out["lines"])
    return dict(out, source=src, rejected=rejected, model=(calls[0]["model"] if calls else None))
WORDS = words_for_call()
print("words for call source:", WORDS["source"], "rejected by lint:", WORDS["rejected"])
data = json.dumps({"words": WORDS, "home": vigil.GPL["home"], "img": IMG, "voice": {k: v for k, v in {"Mara": "mara", "Quinn": "quinn", "Sol": "sol", "Paige": "paige", "Faye": "faye", "Vera": "vera"}.items()}, "office": {"Mara": "Front office", "Faye": "Front office", "Quinn": "Back office", "Sol": "Back office", "Paige": "Back office", "Vera": "Back office"}, "staff": [{"name": n, "role": r, "color": COL[i]} for i, (n, r) in enumerate(vigil.STAFF)],
    "yes": {"trace": yes["trace"], "calls": calls(yes), "outcome": yes["outcome"]}, "no": {"trace": no["trace"], "calls": calls(no), "outcome": no["outcome"]},
    "ts": datetime.datetime.now().strftime("%b %d %Y %H:%M local")})
page = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_template.html")).read()
page = page.replace("__DATA__", data).replace("__TS__", json.loads(data)["ts"])
import sys
_m = [c["mode"] for c in yes["sponsor_calls"]]
_need = (int(os.environ.get("VIGIL_MIN_REAL", "0" if os.environ.get("VIGIL_ALLOW_SIM") else "9")), int(os.environ.get("VIGIL_MIN_EXTERNAL", "0" if os.environ.get("VIGIL_ALLOW_SIM") else "1")))
print("recorded modes: real", _m.count("real"), "external", _m.count("external"), "simulated", _m.count("simulated"), "fallback", _m.count("fallback"))
if _m.count("real") < _need[0] or _m.count("external") < _need[1] or _m.count("fallback"):
    sys.exit("BUILD GUARD: recorded modes regressed (need real>=%d external>=%d fallback=0); nothing written. Check keys / leftover sandboxes." % _need)
os.makedirs("site", exist_ok=True)
import shutil, html
os.makedirs("site/img", exist_ok=True)
for v in AV.values(): shutil.copy(f"avatars/{v}.jpg", f"site/img/{v}.jpg")
BLURB = {"Mara": "Answers the call, gently, and hands a structured brief to the back office.", "Quinn": "Quotes from the General Price List. Prices always come from the list, never the model.", "Sol": "Plans the overnight callback and the removal team's standby.", "Paige": "Pre-fills the paperwork and leaves the family's own fields blank.", "Faye": "Writes the careful family message, bound to the Director's approval.", "Vera": "Checks every word for compliance and keeps the books: quoted, not invoiced."}
team = "".join('<div class=ta data-n="%s" data-role="%s" data-off="%s" data-img="%s">%s</div>' % (n, html.escape(dict(vigil.STAFF)[n]), "Front office" if n in ("Mara", "Faye") else "Back office", AV[n], html.escape(BLURB[n])) for n in AV)
rows = {}
for c in yes["sponsor_calls"]: rows.setdefault(c["sponsor"], c)
score = "".join("<div class='sr %s'><span class=d></span><b>%s</b><span class=w>%s</span><em>%s</em></div>" % (c["mode"].upper(), html.escape(s), html.escape(detail(c)), c["mode"].upper()) for s, c in sorted(rows.items(), key=lambda kv: ({"real": 0, "external": 1}.get(kv[1]["mode"], 2), kv[0])))
modes = [c["mode"] for c in rows.values()]
tally = "<div class=tal>" + "".join("<div class=%s><b>%d</b>%s</div>" % (m.upper(), modes.count(m), m.upper()) for m in ("real", "external", "simulated", "fallback") if modes.count(m)) + "</div><div class=bar>" + "".join("<i class=%s style='flex:%d'></i>" % (m.upper(), modes.count(m)) for m in ("real", "external", "simulated", "fallback") if modes.count(m)) + "</div>"
land = open("site_landing.html").read().replace("__TEAM__", team).replace("__TALLY__", tally).replace("__SCORE__", score)
open("site/index.html", "w").write(land)
for p in ("site/dashboard.html", "demo.html"):
    with open(p, "w") as f: f.write(page)
# GitHub Pages publishes docs/. Keep generated content in sync with site/.
shutil.copytree("site", "docs", dirs_exist_ok=True)
print("built", yes["outcome"], no["outcome"], "gate index", [t["phase"] for t in yes["trace"]].index("approval"))
