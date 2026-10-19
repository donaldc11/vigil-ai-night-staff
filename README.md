# Vigil - AI night staff for funeral homes (hackathon build, FICTIONAL data)

Status is in COMPLIANCE_MATRIX.md. Six workers (Mara intake classification and Faye family-message drafts are OpenAI-assisted, capped at $3 total, every output through lint and Director approval, deterministic fallback; Quinn, Sol, Paige and Lex are deterministic Python) report to one human Director; sensitive actions need an HMAC-bound Director approval. Sponsor adapters report real / simulated / fallback / external per run. n8n is a live workflow round trip; no real call or removal dispatch happens.
Run: python3 vigil.py | python3 tests/test_vigil.py | python3 build_demo.py (writes site/index.html) | env vars in ENV_CHECKLIST.md
