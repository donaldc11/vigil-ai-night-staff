# Vigil: env vars that flip adapters from SIMULATED to REAL
Set in the shell or a gitignored .env that is exported before running. Never commit values. Reports never contain key values (tested).

| Env var | Unlocks | Counts as REAL when | How to check |
|---|---|---|---|
| VIGIL_N8N_WEBHOOK_URL | n8n dispatch | workflow answers 2xx and echoes case_id (import integrations/n8n_vigil_dispatch.json, activate, use the PRODUCTION webhook URL) | run vigil.py; summary lists n8n under REAL |
| VIGIL_ROCKETRIDE_URI, VIGIL_ROCKETRIDE_PIPE, (VIGIL_ROCKETRIDE_KEY for cloud) | RocketRide intake pipeline | engine connects, pipe loads, send() returns | verified 2026-10-19 against a self-hosted engine (open-source server binary, localhost:5565); the SDK needs any non-empty auth string locally |
| CELESTO_API_KEY | Celesto sandbox validates paperwork JSON | sandbox run returns | key from Celesto account |
| SNYK_TOKEN, VIGIL_SNYK_BIN (or snyk on PATH) | Snyk scan gate | `snyk test` exits 0 or 1 (vulns) rather than erroring | CLI at /tmp/snykrun/node_modules/.bin/snyk in the build box |
| VIGIL_PRELINT_EVIDENCE_URL | Prelint | counts as EXTERNAL (not REAL): link to the PR review on the GitHub repo, app installed, spec in PRELINT_REVIEW_SPEC.md | open the link, confirm a completed review |
| VIGIL_TENKI_EVIDENCE_URL | Tenki | EXTERNAL: link to a CI run of tests/test_vigil.py on Tenki runners | open the link |
| BAND_API_KEY (linked to an agent) | BAND room posts | room created and message posted | REAL in the recorded run |
| VIGIL_PARITOK_URL (local `paritok proxy`), VIGIL_OPENAI_BASE_URL pointing at it | Paritok gateway | OpenAI calls pass through it (/stats) | REAL (tokens saved 0 on tiny prompts) |
| GLASSER_API_KEY, TENKI_API_KEY_EAZY | Glasser balance check, Tenki sandbox lint | vendor answers | REAL |
| Masky | VIGIL_MASKY_API_KEY, VIGIL_MASKY_CONV_SLUG | read-only API call at build | REAL (read-back) |
| Flatkey | VIGIL_FLATKEY_API_KEY | one cheap chat call at build | REAL (connectivity check) |
| PromptQL | none | no runtime API built | stays SIMULATED |

Rules: a tool is only called REAL if we invoked it and it answered; EXTERNAL = ran repo-side, evidence link only; FALLBACK = configured but failed. Count in the recorded run (12 sponsors): REAL 10 (Flatkey gateway call, n8n, Snyk, BAND, Celesto, Paritok, Glasser, Tenki, RocketRide on a self-hosted engine, Masky read-back), EXTERNAL 1 (Prelint), SIMULATED 1 (PromptQL). Snyk also needs VIGIL_SNYK_PYTHON (a python with the pinned deps installed) and a token Snyk accepts; BAND needs a key that is linked to an agent.

## OpenAI (all six agents)
- OPENAI_API_KEY (vault only). Optional: VIGIL_LLM_CAP_USD (default 3.00, persisted in ~/.vigil_llm_spend.json), VIGIL_LLM_RUN_TOKENS (3000), VIGIL_OPENAI_MODEL.
- Without a key the agents run deterministic code and are labeled "off". Cost in the report is an ESTIMATE from token counts.
