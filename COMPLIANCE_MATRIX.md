# Rules-compliance matrix (Universal Celebration Hackathon, rules as read from Discord #rules by Instinct; judging criteria NOT published)
Status key: REAL = invoked and answered; LOCAL = our own real code, no vendor; SIMULATED = labeled mock; PENDING = depends on key/account not yet landed. Updated per run by vigil.summary().

| Rule / checklist item | Evidence | Status |
|---|---|---|
| Solo or team up to 4 humans | 1 human Director | MET |
| AI-native company, humans + AI as co-founders/employees | vigil.py STAFF + Director | MET |
| 5+ AI employees, each with role, outputs, reporting line | 6 agents in vigil.STAFF, all report to Director; outputs: intake record, quote, .ics, paperwork.json, lint verdict, ledger | MET. Mara and Faye are OpenAI-assisted (gpt-4o-mini, real calls, $3 hard cap, deterministic fallback, lint + approval on every output); Quinn, Sol, Paige, Lex are deterministic code, not LLM agents |
| Full loop: request, delegate, act, check, report, improve | vigil.run trace phases; tests TestLoop.test_full_loop | MET |
| Human approval points for launch/sensitive actions | Director.decide + hmac Approval; tests TestGates (7 tests) | MET, enforced in code |
| Honest labeling of simulated steps | adapters.Result.mode per call; vigil.summary(); demo.html per-sponsor mode; tests TestHonesty/TestAdapters | MET |
| Use EVERY sponsor tool meaningfully | adapters.registry() has 11 entries, each called in a run; see per-tool below | PARTIAL |
| Each link via supported APIs/connectors | n8n webhook, RocketRide SDK, Celesto SDK, Snyk CLI paths written | PARTIAL, see below |
| Pitch to investors | PITCH.md, Vigil_deck.pptx (needs refresh for real/sim), DEMO_SCRIPT.md | MET (refresh pending) |
| Public GitHub repo (Masky prize) | approval relayed by main, original voice note not verified by builder; scan_secrets.py = CLEAN gate | PENDING push (credits agent owns account) |

## Per sponsor (as of this build)
| Tool | Job in Vigil | Code path | Status now |
|---|---|---|---|
| n8n | dispatch workflow on approved first call | adapters.N8n POST webhook; tested vs local stub (not n8n) | SIMULATED until VIGIL_N8N_WEBHOOK_URL set; then REAL |
| Prelint | compliance review of agent spec/PR | repo-side; operator links evidence | SIMULATED until PR review URL exists -> EXTERNAL. Local lint.py is ours, not Prelint |
| Tenki | CI runs the test suite | repo-side evidence URL | SIMULATED -> EXTERNAL |
| Snyk | dependency vulnerability scan on pinned deps; real findings (exit 1) block dispatch, runs before the approval gates | REAL | e2e 11:24: scan ran via Snyk API, exit 0 (no vulns), Snyk CLI v1.1308. Gate logic also tested with a test double |
| RocketRide | intake pipeline | adapters.RocketRide via SDK; needs an engine (no Docker here) and a .pipe file | SIMULATED; integrations/vigil_intake.pipe is written but NOT verified against a live engine |
| Celesto | sandbox-validate paperwork | adapters.Celesto: creates a live sandbox (free trial), writes paperwork.json there, checks its sha256 matches ours, deletes the sandbox | REAL (live call verified 2026-10-19; the sandbox has no python so the check is a hash match, not a schema validation) |
| BAND, PromptQL, Flatkey, Paritok, Masky | channel / ledger queries / key gateway / metering / avatar | none | SIMULATED; no verified API built |
