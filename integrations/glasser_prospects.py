"""One bounded Glasser web_research call: public funeral-home business info for a prospect list. Never contacts anyone.
Run once; saves evidence to data/glasser_prospects.json (business names and URLs were scrubbed afterwards; only the count, status and charge are kept). Key: GLASSER_API_KEY (vault only)."""
import os, json, uuid, urllib.request, sys
KEY = os.environ["GLASSER_API_KEY"]; B = "https://api.glasser.ai"
def call(method, path, body=None, idem=None):
    h = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json", "User-Agent": "vigil-hackathon/1.0"}
    if idem: h["idempotency-key"] = idem
    r = urllib.request.Request(B + path, json.dumps(body).encode() if body is not None else None, h, method=method)
    with urllib.request.urlopen(r, timeout=90) as x: return json.loads(x.read())
if __name__ == "__main__":
    bal0 = call("GET", "/v1/balance"); print("balance before:", bal0)
    run = call("POST", "/v1/solutions/gtm/web_research", {"query": "independent funeral homes in Sacramento California, public business websites", "country": "US", "language": "en", "limit": 5, "metadata": {"purpose": "vigil hackathon prospect list, public info only"}}, str(uuid.uuid4()))
    print("status:", run.get("status"), "charge_usd:", run.get("charge_usd"), "provider_http:", (run.get("provider_response") or {}).get("http_status"))
    bal1 = call("GET", "/v1/balance"); print("balance after:", bal1)
    json.dump({"status": run.get("status"), "charge_usd": run.get("charge_usd"), "run_url": run.get("run_url"), "output": run.get("output"), "balance_before": bal0, "balance_after": bal1}, open("data/glasser_prospects.json", "w"), indent=1)
