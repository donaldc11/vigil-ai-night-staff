# Vigil: env vars that flip adapters from SIMULATED to REAL
Set in the shell or a gitignored .env that is exported before running. Never commit values. Reports never contain key values (tested).

| Env var | Unlocks | Counts as REAL when | How to check |
|---|---|---|---|
| VIGIL_N8N_WEBHOOK_URL | n8n dispatch | workflow answers 2xx and echoes case_id (import integrations/n8n_vigil_dispatch.json, activate, use the PRODUCTION webhook URL) | run vigil.py; summary lists n8n under REAL |
| VIGIL_ROCKETRIDE_URI, VIGIL_ROCKETRIDE_PIPE, (VIGIL_ROCKETRIDE_KEY for cloud) | RocketRide intake pipeline | engine connects, pipe loads, send() returns | pipe is UNVERIFIED and has no response node yet |
| CELESTO_API_KEY | Celesto sandbox validates paperwork JSON | sandbox run returns | key from Celesto account |
| SNYK_TOKEN, VIGIL_SNYK_BIN (or snyk on PATH) | Snyk scan gate | `snyk test` exits 0 or 1 (vulns) rather than erroring | CLI at /tmp/snykrun/node_modules/.bin/snyk in the build box |
| VIGIL_PRELINT_EVIDENCE_URL | Prelint | counts as EXTERNAL (not REAL): link to the PR review on the GitHub repo, app installed, spec in PRELINT_REVIEW_SPEC.md | open the link, confirm a completed review |
| VIGIL_TENKI_EVIDENCE_URL | Tenki | EXTERNAL: link to a CI run of tests/test_vigil.py on Tenki runners | open the link |
| BAND, PromptQL, Flatkey, Paritok, Masky | none yet | no verified API built; need docs or key + endpoint from the credits agent | stay SIMULATED |

Rules: a tool is only called REAL if we invoked it and it answered; EXTERNAL = ran repo-side, evidence link only; FALLBACK = configured but failed. Count today: REAL 1 (n8n), EXTERNAL 1 (Prelint), SIMULATED 9/11. Snyk also needs VIGIL_SNYK_PYTHON (a python with the pinned deps installed) and a token Snyk accepts; BAND needs a key that is linked to an agent.
