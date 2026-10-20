# Rules-compliance matrix (Universal Celebration Hackathon, rules as read from Discord #rules by Instinct; judging criteria NOT published)
Status key: REAL = invoked and answered; LOCAL = our own real code, no vendor; SIMULATED = no integration; EXTERNAL = repo-side evidence link only; FALLBACK = real path failed. Updated per run by vigil.summary().

| Rule / checklist item | Evidence | Status |
|---|---|---|
| Solo or team up to 4 humans | 1 human Director | MET |
| AI-native company, humans + AI as co-founders/employees | vigil.py STAFF + Director | MET |
| 5+ AI employees, each with role, outputs, reporting line | 6 agents in vigil.STAFF, all report to Director; outputs: intake record, quote, .ics, paperwork.json, lint verdict, ledger | MET. All six are LLM-driven (gpt-4o-mini, real calls, $3 hard cap): Mara classifies, Quinn picks price-list items, Sol picks the overnight plan, Paige picks forms, Faye drafts the message, Vera gives an advisory second opinion. Each decision is enum-validated with a deterministic fallback. Gates, prices (from the GPL), callback time, lint and Director approval are deterministic code. Voice: OpenAI TTS clips (AI-generated), portraits: Masky |
| Full loop: request, delegate, act, check, report, improve | vigil.run trace phases; tests TestLoop.test_full_loop | MET |
| Human approval points for launch/sensitive actions | Director.decide + hmac Approval; tests TestGates (7 tests) | MET, enforced in code |
| Honest labeling of simulated steps | adapters.Result.mode per call; vigil.summary(); demo.html per-sponsor mode; tests TestHonesty/TestAdapters | MET |
| Use EVERY sponsor tool meaningfully | adapters.registry() has 12 entries, each called in a run; see per-tool below | PARTIAL |
| Each link via supported APIs/connectors | n8n webhook, RocketRide SDK, Celesto SDK, Snyk CLI paths written | PARTIAL, see below |
| Pitch to investors | PITCH.md, Vigil_deck.pptx, DEMO_SCRIPT.md | MET |
| Public GitHub repo (Masky prize) | Public repo https://github.com/donaldc11/vigil-ai-night-staff; scan_secrets.py = CLEAN gate before every push | MET |

## Per sponsor (as of this build)
| Tool | Job in Vigil | Code path | Status now |
|---|---|---|---|
| n8n | dispatch workflow on approved first call | adapters.N8n POST webhook to a live n8n cloud workflow (tests use a local stub) | REAL: live workflow round trip; it does not move a real removal team |
| Prelint | compliance review of agent spec/PR | repo-side; operator links evidence | EXTERNAL: PR https://github.com/donaldc11/vigil-ai-night-staff/pull/1 (evidence link only). Local lint.py is ours, not Prelint |
| Tenki | CI on a Tenki runner, plus a sandbox VM that re-runs Vera's compliance lint | .github/workflows/ci.yml (commit 4e02559, green run) and adapters.TenkiSandbox (creates a VM on the Eazy workspace, uploads lint.py, runs it, compares to the local verdict, closes the VM) | REAL: sandbox call verified live 2026-10-19 (verdict agreed with local). CI is repo-side evidence: https://github.com/donaldc11/vigil-ai-night-staff/actions/runs/39311833386 |
| Snyk | dependency vulnerability scan on pinned deps; real findings (exit 1) block dispatch, runs before the approval gates | REAL | e2e 11:24: scan ran via Snyk API, exit 0 (no vulns), Snyk CLI v1.1308. Gate logic also tested with a test double |
| RocketRide | intake pipeline | adapters.RocketRide via the Python SDK against a self-hosted RocketRide engine (open-source server v3.5.0-prerelease, linux-x64 binary from the rocketride-org/rocketride-server releases, run on localhost) | REAL (self-hosted engine, not RocketRide Cloud): vigil_intake.pipe (webhook, parse, response_text) ran live; the engine accepted the call text and returned it parsed. Only this one step runs through RocketRide; the rest of the Vigil flow does not |
| Celesto | sandbox-validate paperwork | adapters.Celesto: creates a live sandbox (free trial), writes paperwork.json there, checks its sha256 matches ours, deletes the sandbox | REAL (live call verified 2026-10-19; the sandbox has no python so the check is a hash match, not a schema validation) |
| BAND | channel for agent updates | adapters.Band via band-sdk, fresh room per run | REAL (verified live, see e2e files) |
| Masky | avatar | VIGIL_MASKY_API_KEY, VIGIL_MASKY_CONV_SLUG | REAL (read-back): build-time Masky API call finds the Vigil avatar and a rendered speak-mode video turn (0 credits charged). Portraits and clips were hand-generated in Masky; only this call is live |
| PromptQL, Flatkey | ledger queries / model API gateway | none | SIMULATED, no runtime API call. PromptQL: 3/3 answers verified by hand in the PromptQL workspace on the pasted fictional price list and ledger. Flatkey is a model gateway, not a key vault |
| Paritok | context compression gateway between Vigil and OpenAI | adapters.Paritok + local `paritok proxy` on the hosted GPU server (key accepted); Vigil's OpenAI calls routed through it | REAL (3 requests passed through, verified via /stats). Caveat: prompts are tiny, so tokens saved = 0. It is in the path, not saving anything yet |

| Glasser (not an adapter in the loop) | one bounded public web_research query for a funeral-home prospect list, never contacting anyone | integrations/glasser_prospects.py, evidence in data/glasser_prospects.json | REAL one-off call: COMPLETED, charge $0.0011 of the $1 balance. Business names were scrubbed from the saved evidence (fictional-data repo). The adapter in the loop does a live free balance check with the key and attaches this recorded run (the research query itself ran once, not per case) |
