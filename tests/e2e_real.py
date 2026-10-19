"""End-to-end run with whatever real tools are configured via env. Prints honest modes. Exit 1 if an expected-real tool is not real.
Usage: VIGIL_N8N_WEBHOOK_URL=... python3 tests/e2e_real.py n8n [snyk ...]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import vigil
expect = [a.lower() for a in sys.argv[1:]]
r = vigil.run("Hi, my father just passed at home. We think he wanted cremation. Call me at 916-555-0142.", vigil.Director(lambda g, c, x: True), outdir="out")
print(vigil.summary(r))
for c in r["sponsor_calls"]:
    if c["mode"] != "simulated": print(c["sponsor"], c["mode"], json.dumps(c["evidence"]) if c["evidence"] else c["reason"])
real = {s.lower() for s in r["sponsors_real"]}
missing = [e for e in expect if e not in real]
print("EXPECTED REAL:", expect, "MISSING:", missing, "OUTCOME:", r["outcome"])
sys.exit(1 if missing or r["outcome"] != "completed" else 0)
