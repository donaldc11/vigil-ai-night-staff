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
    name = "?"; job = ""; env = ()
    def configured(self): return all(os.environ.get(e) for e in self.env)
    def real(self, action, payload): raise NotImplementedError
    def call(self, action, payload=None):
        payload = payload or {}
        if not self.env:
            return Result(self.name, action, "simulated", "no verified API integration built yet")
        if not self.configured():
            return Result(self.name, action, "simulated", "not configured: set " + ", ".join(self.env))
        try:
            return Result(self.name, action, "real", evidence=self.real(action, payload))
        except Exception as e:
            return Result(self.name, action, "fallback", f"real path failed: {type(e).__name__}: {str(e)[:160]}")

class N8n(Adapter):
    name = "n8n"; job = "dispatch workflow: webhook fires the first-call on-call workflow"; env = ("VIGIL_N8N_WEBHOOK_URL",)
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
        from celesto import Computer
        c = Computer(api_key=os.environ["CELESTO_API_KEY"])
        try:
            out = c.run("python3 -c \"import json,sys;json.loads(sys.stdin.read() or '{}');print('ok')\" <<'EOF'\n" + p.get("json", "{}") + "\nEOF")
            return {"sandbox_result": str(out)[:200]}
        finally:
            try: c.close()
            except Exception: pass

class Snyk(Adapter):
    name = "Snyk"; job = "dependency/code security scan gate"; env = ("SNYK_TOKEN",)
    def real(self, action, p):
        b = os.environ.get("VIGIL_SNYK_BIN") or shutil.which("snyk")
        if not b: raise RuntimeError("snyk CLI not installed (set VIGIL_SNYK_BIN)")
        r = subprocess.run([b, "test", "--file=requirements.txt", "--json"], capture_output=True, text=True, timeout=120, cwd=p.get("dir", "."))
        if r.returncode > 1: raise RuntimeError("snyk error: " + (r.stdout or r.stderr)[:120])
        return {"exit_code": r.returncode, "ok": r.returncode == 0, **({"error": r.stdout[:150]} if r.returncode > 1 else {})}

class RepoSide(Adapter):
    """Prelint / Tenki run on a GitHub repo, not via a call we make. Real only as linked evidence."""
    def __init__(s, name, job, env): s.name, s.job, s._env = name, job, env
    env = ()
    def call(self, action, payload=None):
        url = os.environ.get(self._env)
        if url: return Result(self.name, action, "external", "ran repo-side; evidence URL supplied by operator", {"url": url})
        return Result(self.name, action, "simulated", f"repo-side tool, no run evidence (set {self._env})")

class Plain(Adapter):
    def __init__(s, name, job): s.name, s.job = name, job

def registry():
    return {a.name: a for a in [N8n(), RocketRide(), Celesto(), Snyk(),
        RepoSide("Prelint", "PR compliance review of the agent spec", "VIGIL_PRELINT_EVIDENCE_URL"),
        RepoSide("Tenki", "CI runner for the test suite", "VIGIL_TENKI_EVIDENCE_URL"),
        Plain("BAND", "shared agent/human channel"), Plain("PromptQL", "natural-language ledger queries"),
        Plain("Flatkey", "credential gateway"), Plain("Paritok", "usage metering"), Plain("Masky", "avatar for Faye")]}
