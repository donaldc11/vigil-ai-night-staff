"""Sponsor adapters. Each call returns a Result whose mode is exactly one of:
  real       - we invoked the vendor and it answered (evidence recorded)
  simulated  - no key/config or no verified API; nothing left the machine
  fallback   - real path was configured but failed; mock used instead (error recorded)
  external   - vendor ran repo-side (PR/CI); we only link evidence supplied by the operator
Config comes from env vars (keys are never written to disk or logs)."""
import os, json, shutil, subprocess, urllib.request, asyncio
from dataclasses import dataclass, field, asdict

@dataclass
class Result:
    sponsor: str; action: str; mode: str; reason: str = ""; evidence: dict = field(default_factory=dict)
    def d(self): return asdict(self)

class Adapter:
    name = "?"; job = ""; env = (); sim_reason = "no verified API integration built yet"
    def configured(self): return all(os.environ.get(e) for e in self.env)
    def real(self, action, payload): raise NotImplementedError
    def call(self, action, payload=None):
        payload = payload or {}
        if not self.env:
            return Result(self.name, action, "simulated", self.sim_reason)
        if not self.configured():
            return Result(self.name, action, "simulated", "not configured: set " + ", ".join(self.env))
        try:
            return Result(self.name, action, "real", evidence=self.real(action, payload))
        except Exception as e:
            return Result(self.name, action, "fallback", f"real path failed: {type(e).__name__}: {str(e)[:160]}")

class N8n(Adapter):
    name = "n8n"; job = "workflow round trip: webhook sends a dispatch ticket to a live n8n workflow (it does not move a real removal team)"; env = ("VIGIL_N8N_WEBHOOK_URL",)
    def real(self, action, p):
        req = urllib.request.Request(os.environ["VIGIL_N8N_WEBHOOK_URL"], json.dumps(p).encode(), {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as r:
            if not 200 <= r.status < 300: raise RuntimeError(f"HTTP {r.status}")
            body = json.loads(r.read() or b"{}")
        if body.get("case_id") != p.get("case_id"): raise RuntimeError("workflow did not echo case_id (wrong or inactive workflow)")
        return {"http_status": r.status, "ticket": {k: body.get(k) for k in ("case_id", "removal_team", "dispatched_at")}}

class RocketRide(Adapter):
    name = "RocketRide"; job = "run the intake pipeline on the call text"; env = ("VIGIL_ROCKETRIDE_URI", "VIGIL_ROCKETRIDE_PIPE")
    def real(self, action, p):
        from rocketride import RocketRideClient
        async def go():
            async with RocketRideClient(uri=os.environ["VIGIL_ROCKETRIDE_URI"], auth=os.environ.get("VIGIL_ROCKETRIDE_KEY", "")) as c:
                t = await c.use(filepath=os.environ["VIGIL_ROCKETRIDE_PIPE"])
                res = await c.send(t["token"], p.get("text", ""))
                return {"result_keys": sorted(res)[:8] if isinstance(res, dict) else str(type(res))}
        return asyncio.run(asyncio.wait_for(go(), 30))

class Celesto(Adapter):
    name = "Celesto"; job = "validate generated paperwork inside an isolated sandbox"; env = ("CELESTO_API_KEY",)
    def real(self, action, p):
        import uuid
        from celesto import Computer
        from celesto.sdk.client import _CelestoClient as CelestoClient
        cl = CelestoClient(api_key=os.environ["CELESTO_API_KEY"])
        c = None
        try:
            # the live API now requires an Idempotency-Key on create; SDK 0.0.14 Computer() does not send one, so create via the client
            info = cl.computers._request("POST", "/computers", json_body={}, headers={"Idempotency-Key": str(uuid.uuid4())})
            c = Computer.get(info["id"], client=cl)
            import time
            for _ in range(40):  # wait until the sandbox finishes creating
                st = str(cl.computers.get(info["id"]).get("status", "")).lower()
                if st in ("running", "ready", "active"): break
                if st in ("failed", "error"): raise RuntimeError("sandbox status " + st)
                time.sleep(2)
            import hashlib
            body = p.get("json", "{}"); want = hashlib.sha256(body.encode()).hexdigest()
            # the scratch sandbox has no python: write the paperwork file there and check its sha256 matches ours
            out = c.run("cat > /tmp/paperwork.json <<'VIGIL_EOF'\n" + body + "\nVIGIL_EOF\nhead -c -1 /tmp/paperwork.json | sha256sum")
            res = str(out)
            if want not in res: raise RuntimeError("sandbox hash did not match paperwork: " + res[:100])
            ex = out.get("exit_code") if isinstance(out, dict) else None
            if ex not in (None, 0): raise RuntimeError(f"sandbox exit code {ex}")
            return {"sandbox_result": res[:200], "exit_code": ex, "computer_id": info["id"]}
        finally:
            try:
                if c: c.delete()
            except Exception: pass
            try: cl.close()
            except Exception: pass

class Snyk(Adapter):
    name = "Snyk"; job = "dependency vulnerability scan; real findings (exit 1) block dispatch"; env = ("SNYK_TOKEN",)
    def real(self, action, p):
        b = os.environ.get("VIGIL_SNYK_BIN") or shutil.which("snyk")
        if not b: raise RuntimeError("snyk CLI not installed (set VIGIL_SNYK_BIN)")
        cmd = [b, "test", "--file=requirements.txt", "--json"] + (["--command=" + os.environ["VIGIL_SNYK_PYTHON"]] if os.environ.get("VIGIL_SNYK_PYTHON") else [])
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=p.get("dir", os.path.dirname(os.path.abspath(__file__))))
        if r.returncode > 1: raise RuntimeError("snyk error: " + (r.stdout or r.stderr)[:120])
        return {"exit_code": r.returncode, "ok": r.returncode == 0, **({"error": r.stdout[:150]} if r.returncode > 1 else {})}

class Band(Adapter):
    name = "BAND"; job = "post case updates into a BAND room with the Director as a participant"
    env = ("VIGIL_BAND_API_KEY", "VIGIL_BAND_PY")
    def real(self, action, p):
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "integrations", "band_post.py")
        r = subprocess.run([os.environ["VIGIL_BAND_PY"], script], input=json.dumps({"text": p.get("text", "Vigil case update")}),
                           capture_output=True, text=True, timeout=45, env=os.environ)
        if r.returncode != 0: raise RuntimeError("band_post failed: " + (r.stderr.strip().splitlines() or ["?"])[-1][:140])
        ev = json.loads(r.stdout.strip().splitlines()[-1])
        if not ev.get("room"): raise RuntimeError("no room id in reply")
        return ev

class RepoSide(Adapter):
    """Prelint / Tenki run on a GitHub repo, not via a call we make. Real only as linked evidence."""
    def __init__(s, name, job, env): s.name, s.job, s._env = name, job, env
    env = ()
    def call(self, action, payload=None):
        url = os.environ.get(self._env)
        if url: return Result(self.name, action, "external", "ran repo-side; evidence URL supplied by operator", {"url": url})
        return Result(self.name, action, "simulated", f"repo-side tool, no run evidence (set {self._env})")

class TenkiSandbox(RepoSide):
    """Tenki: if TENKI_API_KEY is set, Vera's compliance lint is re-run inside a disposable Tenki sandbox VM and must agree with the local verdict.
    Otherwise it falls back to repo-side evidence (CI runner link) or simulated."""
    def call(self, action, payload=None):
        if not (os.environ.get("TENKI_API_KEY_EAZY") or os.environ.get("TENKI_API_KEY")): return super().call(action, payload)
        try:
            return Result(self.name, action, "real", evidence=self.sandbox(payload or {}))
        except Exception as e:
            return Result(self.name, action, "fallback", f"real path failed: {type(e).__name__}: {str(e)[:160]}")
    def sandbox(self, p):
        from tenki_sandbox import Sandbox
        import lint as L
        here = os.path.dirname(os.path.abspath(__file__)); msg = p.get("msg", "")
        sb = Sandbox.create(api_key=os.environ.get("TENKI_API_KEY_EAZY") or os.environ["TENKI_API_KEY"], name="vigil-vera-lint", wait=True, max_duration=300)
        try:
            sb.fs.write_text("/home/tenki/lint.py", open(os.path.join(here, "lint.py")).read())
            sb.fs.write_text("/home/tenki/msg.txt", msg)
            r = sb.exec("python3", "-c", "import json,lint;print(json.dumps(lint.lint(open('msg.txt').read())))", cwd="/home/tenki", timeout=60)
            if r.exit_code != 0: raise RuntimeError("sandbox exit %s: %s" % (r.exit_code, r.stderr_text[:100]))
            remote = json.loads(r.stdout_text.strip().splitlines()[-1])
        finally:
            try: sb.close()
            except Exception: pass
        local = L.lint(msg)
        if remote != local: raise RuntimeError("sandbox lint verdict differs from local: %s vs %s" % (remote, local))
        return {"sandbox_lint_issues": remote, "agrees_with_local": True, "ran_in": "Tenki Sandbox VM", "ci_run_url": os.environ.get("VIGIL_TENKI_EVIDENCE_URL", "")}

class Glasser(Adapter):
    name = "Glasser"; job = "bounded public web research for a funeral-home prospect list (one recorded query, never contacts anyone)"; env = ("GLASSER_API_KEY",)
    def real(self, action, p):
        here = os.path.dirname(os.path.abspath(__file__)); ev = json.load(open(os.path.join(here, "data", "glasser_prospects.json")))
        if ev.get("status") != "COMPLETED": raise RuntimeError("recorded research run is not COMPLETED")
        req = urllib.request.Request("https://api.glasser.ai/v1/balance", headers={"Authorization": "Bearer " + os.environ["GLASSER_API_KEY"], "User-Agent": "vigil-hackathon/1.0"})
        bal = json.loads(urllib.request.urlopen(req, timeout=15).read())   # live, free call proving the key works now
        return {"live_balance_check_usd": bal.get("available_usd"), "recorded_research_run": {"status": ev["status"], "charge_usd": ev["charge_usd"], "results": len((ev.get("output") or {}).get("results", []))}}

class Paritok(Adapter):
    name = "Paritok"; job = "context compression gateway sitting between Vigil and the OpenAI API (prompts here are tiny, so savings are ~0; we label that)"; env = ("VIGIL_PARITOK_URL",)
    def real(self, action, p):
        base = os.environ["VIGIL_PARITOK_URL"].rstrip("/")
        if not os.environ.get("VIGIL_OPENAI_BASE_URL", "").startswith(base): raise RuntimeError("OpenAI calls are not routed through the Paritok gateway")
        get = lambda path: json.loads(urllib.request.urlopen(base + path, timeout=10).read())
        h, s = get("/health"), get("/stats")
        if h.get("status") != "ok" or not s.get("total_requests"): raise RuntimeError("gateway up but no request passed through it")
        return {"gateway_version": h.get("version"), "requests_through_gateway": s["total_requests"], "tokens_saved": s.get("tokens_saved", 0), "input_tokens_original": s.get("input_tokens_original", 0)}

class Plain(Adapter):
    def __init__(s, name, job, sim_reason=None):
        s.name, s.job = name, job
        if sim_reason: s.sim_reason = sim_reason

def registry():
    return {a.name: a for a in [N8n(), RocketRide(), Celesto(), Snyk(),
        RepoSide("Prelint", "PR compliance review of the agent spec", "VIGIL_PRELINT_EVIDENCE_URL"),
        TenkiSandbox("Tenki", "CI runner for the test suite (repo-side) and a sandbox VM that re-runs Vera's compliance lint", "VIGIL_TENKI_EVIDENCE_URL"),
        Band(), Paritok(), Glasser(), Plain("PromptQL", "natural-language ledger queries", "3/3 verified answers in PromptQL workspace on the pasted price list and ledger; no runtime API call"),
        Plain("Flatkey", "model API / failover gateway (not a key vault)"), Plain("Masky", "avatar portraits for the six agents", "six portraits generated in Masky (real assets); no runtime API call")]}
