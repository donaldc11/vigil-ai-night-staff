"""Capped OpenAI client (stdlib only). OpenAI is the ONLY model provider. Fictional/redacted data only.
Env: OPENAI_API_KEY (enables), VIGIL_OPENAI_MODEL, VIGIL_OPENAI_BASE_URL, VIGIL_LLM_CAP_USD (default 3.00, hard total),
VIGIL_LLM_RUN_TOKENS (default 1500 per run), VIGIL_OPENAI_PRICE_IN / _OUT (USD per 1M tokens; ESTIMATES used for the cap).
Spend is persisted in VIGIL_LLM_SPEND_FILE (default ~/.vigil_llm_spend.json) so the cap holds across runs and processes."""
import os, json, urllib.request, urllib.error

class LLMUnavailable(Exception): pass

def _cfg():
    return dict(base=os.environ.get("VIGIL_OPENAI_BASE_URL", "https://api.openai.com/v1"), model=os.environ.get("VIGIL_OPENAI_MODEL", "gpt-4o-mini"),
        cap=float(os.environ.get("VIGIL_LLM_CAP_USD", "3.00")), run_tokens=int(os.environ.get("VIGIL_LLM_RUN_TOKENS", "3000")),
        pin=float(os.environ.get("VIGIL_OPENAI_PRICE_IN", "0.15")), pout=float(os.environ.get("VIGIL_OPENAI_PRICE_OUT", "0.60")),
        spend=os.environ.get("VIGIL_LLM_SPEND_FILE", os.path.expanduser("~/.vigil_llm_spend.json")))

def spent(path=None):
    p = path or _cfg()["spend"]
    try:
        with open(p) as f: return float(json.load(f).get("usd_estimate", 0))
    except (OSError, ValueError): return 0.0

def enabled(): return bool(os.environ.get("OPENAI_API_KEY"))

class Budget:
    """Per-run token budget + global dollar cap."""
    def __init__(s): s.c = _cfg(); s.tokens = 0; s.calls = []
    def chat(s, purpose, system, user, max_tokens=150):
        if not enabled(): raise LLMUnavailable("OPENAI_API_KEY not set")
        c = s.c
        if spent(c["spend"]) >= c["cap"]: raise LLMUnavailable(f"global cap ${c['cap']:.2f} reached")
        if s.tokens + max_tokens > c["run_tokens"]: raise LLMUnavailable("per-run token budget exhausted")
        body = json.dumps({"model": c["model"], "max_tokens": max_tokens, "temperature": 0,
                           "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}).encode()
        req = urllib.request.Request(c["base"] + "/chat/completions", body, {"Content-Type": "application/json", "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]})
        try:
            with urllib.request.urlopen(req, timeout=20) as r: d = json.loads(r.read())
        except urllib.error.HTTPError as e: raise LLMUnavailable(f"HTTP {e.code}")
        except Exception as e: raise LLMUnavailable(type(e).__name__)
        u = d.get("usage", {}); pt, ct = int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0))
        usd = (pt * c["pin"] + ct * c["pout"]) / 1e6
        s.tokens += pt + ct
        try:
            total = spent(c["spend"]) + usd   # read BEFORE opening for write (open("w") truncates the file)
            tmp = c["spend"] + ".tmp"
            with open(tmp, "w") as f: json.dump({"usd_estimate": total}, f)
            os.replace(tmp, c["spend"])
        except OSError: pass
        s.calls.append({"purpose": purpose, "model": c["model"], "prompt_tokens": pt, "completion_tokens": ct, "usd_estimate": round(usd, 6)})
        try: return d["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError): raise LLMUnavailable("malformed reply")
