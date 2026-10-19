"""Vigil: AI night staff for funeral homes. Fictional data only. See adapters.py for real/simulated modes."""
import re, os, json, hmac, hashlib, secrets, sqlite3, time, datetime
import adapters, lint as L

HERE = os.path.dirname(os.path.abspath(__file__))
GPL = json.load(open(os.path.join(HERE, "data", "gpl.json")))
STAFF = [("Mara","Intake"),("Quinn","Quoter"),("Sol","Scheduler"),("Paige","Paperwork"),("Faye","Family Liaison"),("Lex","Compliance Logger")]
MAX_INPUT = 2000
_SECRET = secrets.token_bytes(32)
GATES = ("send_family_message", "dispatch_removal_team")

class GateError(Exception): pass

class Approval:
    """Only Director.decide() mints these; actions verify them. Forging needs the per-process secret."""
    def __init__(s, gate, case_id, digest, sig): s.gate, s.case_id, s.digest, s.sig = gate, case_id, digest, sig
def _sig(gate, case_id, digest): return hmac.new(_SECRET, f"{gate}|{case_id}|{digest}".encode(), hashlib.sha256).hexdigest()
def _digest(content): return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

class Director:
    """The human. decide(gate, case_id, content) -> bool. Default policy: decline (safe)."""
    def __init__(s, policy=None): s.policy = policy or (lambda gate, case_id, content: False)
    def decide(s, gate, case_id, content):
        ok = bool(s.policy(gate, case_id, content))
        d = _digest(content)
        return Approval(gate, case_id, d, _sig(gate, case_id, d)) if ok else None

def require(gate, case_id, content, approval):
    if approval is None or approval.gate != gate or approval.case_id != case_id: raise GateError(f"no valid approval for {gate}")
    if not hmac.compare_digest(approval.sig, _sig(gate, case_id, _digest(content))) or approval.digest != _digest(content):
        raise GateError(f"approval for {gate} does not match content")

def clean(text):
    if not isinstance(text, str): return None
    t = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", " ", text).strip()
    return t[:MAX_INPUT] if t else None

PHONE = r"(\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})"
def redact(t): return re.sub(PHONE, lambda m: (" " if m.group(1)[0].isspace() else "") + "***-***-" + re.sub(r"\D", "", m.group(1))[-4:], t)

def intake(text):
    first = bool(re.search(r"\b(passed|died|death|just lost|passed away|deceased)\b", text, re.I))
    pref = "cremation" if re.search(r"cremat", text, re.I) else "burial" if re.search(r"\b(burial|bury|buried)\b", text, re.I) else "unknown"
    m = re.search(r"\b(\+?1?[\s.-]?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4})\b", text)
    phone_last4 = re.sub(r"\D", "", m.group(1))[-4:] if m else None
    return {"first_call": first, "preference": pref, "callback_last4": phone_last4}

def quote(pref):
    k = {"cremation": "direct_cremation", "burial": "immediate_burial"}.get(pref)
    items = GPL["items"]
    return {n: items[n] for n in ([k] if k else []) + [x for x in items if x != k][:2]}

def paperwork(case_id, info):
    return {"case_id": case_id, "forms": ["death certificate worksheet", "burial/cremation permit checklist", "SSA notice draft", "VA notice draft"],
            "prefilled": {"preference": info["preference"]}, "blank_for_family": ["legal name", "date/place of death", "SSN", "next of kin"]}

def schedule(now):
    cb = (now + datetime.timedelta(days=1)).replace(hour=7, minute=0, second=0, microsecond=0)
    return {"callback": cb.isoformat(), "ics": "BEGIN:VCALENDAR\nVERSION:2.0\nBEGIN:VEVENT\nSUMMARY:Family callback (FICTIONAL)\nDTSTART:%s\nEND:VEVENT\nEND:VCALENDAR\n" % cb.strftime("%Y%m%dT%H%M%S")}

class Ledger:
    def __init__(s, path=":memory:"):
        s.db = sqlite3.connect(path); s.db.execute("CREATE TABLE IF NOT EXISTS events(case_id TEXT, ts REAL, who TEXT, phase TEXT, msg TEXT)")
    def add(s, case_id, who, phase, msg): s.db.execute("INSERT INTO events VALUES(?,?,?,?,?)", (case_id, time.time(), who, phase, msg)); s.db.commit()
    def rows(s, case_id): return s.db.execute("SELECT who,phase,msg FROM events WHERE case_id=? ORDER BY rowid", (case_id,)).fetchall()
    def count(s): return s.db.execute("SELECT count(*) FROM events").fetchone()[0]

FAMILY_MSG = "Thank you for calling. This call may be recorded. We are so sorry for your loss. A director will call you at 7:00 AM."

def run(call_text, director=None, ledger=None, outdir=None, reg=None, now=None, case_id=None):
    director = director or Director(); ledger = ledger or Ledger(); reg = reg or adapters.registry()
    now = now or datetime.datetime.now(); case_id = case_id or "c" + secrets.token_hex(4)
    trace, calls = [], []
    local_real = set()
    def step(who, phase, msg, **kw):
        trace.append({"who": who, "phase": phase, "msg": msg, **kw}); ledger.add(case_id, who, phase, msg)
    def use(name, action, payload=None):
        r = reg[name].call(action, payload); calls.append(r.d()); return r
    raw = clean(call_text); text = raw
    step("Caller", "request", redact(text) if text else "(empty or invalid input)")
    if text is None:
        step("Mara", "delegate", "Rejected: empty or non-text input. No action taken."); return _finish(case_id, trace, calls, local_real, "rejected", outdir)
    info = intake(text); local_real.add("Mara: rule-based intake")
    rr = use("RocketRide", "intake_pipeline", {"text": redact(text)})
    step("Mara", "delegate", f"first_call={info['first_call']} preference={info['preference']}. Routing to Quinn, Sol, Paige.", **info)
    if not info["first_call"]:
        step("Lex", "report", "Non-urgent call logged. No dispatch, no arrangements discussed."); local_real.add("Lex: ledger (sqlite)")
        return _finish(case_id, trace, calls, local_real, "non_urgent", outdir)
    q = quote(info["preference"]); use("PromptQL", "price_query"); use("Paritok", "meter"); local_real.add("Quinn: GPL price lookup from data/gpl.json")
    step("Quinn", "act", "Prepared GPL price range (informational, not a contract).", quote=q)
    sc = schedule(now); local_real.add("Sol: callback .ics generated")
    step("Sol", "act", f"Proposed 7:00 AM callback ({sc['callback']}).")
    pw = paperwork(case_id, info); local_real.add("Paige: paperwork packet JSON")
    use("Flatkey", "get_key"); cel = use("Celesto", "validate_paperwork", {"json": json.dumps(pw)})
    step("Paige", "act", "Pre-filled paperwork packet; family-only fields left blank.", paperwork=pw)
    issues = L.lint(FAMILY_MSG); local_real.add("Lex: local compliance lint")
    use("Prelint", "review_spec")
    step("Lex", "check", "Compliance lint passed." if not issues else f"BLOCKED: {issues}", issues=issues)
    if issues: return _finish(case_id, trace, calls, local_real, "blocked_by_lint", outdir)
    # approval gates: each action is only reachable with a matching Approval
    a1 = director.decide("send_family_message", case_id, {"msg": FAMILY_MSG})
    a2 = director.decide("dispatch_removal_team", case_id, {"callback": sc["callback"], "preference": info["preference"]}) if a1 else None
    if not (a1 and a2):
        step("Director", "approval", "Director declined. Nothing sent, nothing dispatched."); return _finish(case_id, trace, calls, local_real, "declined", outdir)
    step("Director", "approval", "Director approved family message and removal dispatch.")
    require("dispatch_removal_team", case_id, {"callback": sc["callback"], "preference": info["preference"]}, a2)
    n8 = use("n8n", "dispatch_workflow", {"case_id": case_id, "preference": info["preference"], "callback": sc["callback"]})
    step("Sol", "act", "Dispatch workflow triggered.")
    require("send_family_message", case_id, {"msg": FAMILY_MSG}, a1); use("Masky", "avatar")
    step("Faye", "act", "Approved message recorded for delivery (no real call or text is placed in this build).", message=FAMILY_MSG)
    use("Snyk", "scan"); use("Tenki", "ci"); use("BAND", "post")
    step("Lex", "report", "Case logged: disclosure given, approvals, quote shown."); step("Mara", "improve", "Intake checklist: confirm spelling of the deceased's name once, early.")
    return _finish(case_id, trace, calls, local_real, "completed", outdir, artifacts={"paperwork.json": json.dumps(pw, indent=1), "callback.ics": sc["ics"], "family_message.txt": FAMILY_MSG})

def _finish(case_id, trace, calls, local_real, outcome, outdir, artifacts=None):
    report = {"case_id": case_id, "outcome": outcome, "trace": trace, "sponsor_calls": calls, "local_real": sorted(local_real),
        "sponsors_real": sorted({c["sponsor"] for c in calls if c["mode"] == "real"}),
        "sponsors_external": sorted({c["sponsor"] for c in calls if c["mode"] == "external"}),
        "sponsors_fallback": sorted({c["sponsor"] for c in calls if c["mode"] == "fallback"}),
        "sponsors_simulated": sorted({c["sponsor"] for c in calls if c["mode"] == "simulated"})}
    if outdir:
        d = os.path.join(outdir, case_id); os.makedirs(d, exist_ok=True)
        for n, c in (artifacts or {}).items(): _w(os.path.join(d, n), c)
        _w(os.path.join(d, "report.json"), json.dumps(report, indent=1))
    return report

def _w(p, c):
    with open(p, "w") as f: f.write(c)

def summary(r):
    return (f"Case {r['case_id']}: {r['outcome']}\n  REAL (sponsor, invoked): {r['sponsors_real'] or 'none'}\n  EXTERNAL (repo-side evidence): {r['sponsors_external'] or 'none'}\n"
            f"  FALLBACK (real failed): {r['sponsors_fallback'] or 'none'}\n  SIMULATED sponsors: {r['sponsors_simulated'] or 'none'}\n  Local real code: {r['local_real']}\n")
if __name__ == "__main__":
    import sys
    t = " ".join(sys.argv[1:]) or "Hi, my father just passed at home. We think he wanted cremation. Call me at 916-555-0142."
    print(summary(run(t, Director(lambda g, c, x: True), outdir="out")))
