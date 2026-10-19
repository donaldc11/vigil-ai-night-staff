# Vigil - AI night staff for funeral homes (hackathon build, FICTIONAL data)

Status is in COMPLIANCE_MATRIX.md. Six LLM-driven agents (OpenAI gpt-4o-mini, $3 hard cap; each makes one enum-validated decision plus a short in-character line; gates, prices, callback time and approvals are deterministic code). Front office: Mara, Faye. Back office: Quinn, Sol, Paige, Lex report to one human Director; sensitive actions need an HMAC-bound Director approval. Sponsor adapters report real / simulated / fallback / external per run. n8n is a live workflow round trip; no real call or removal dispatch happens.
Run: python3 vigil.py | python3 tests/test_vigil.py | python3 build_demo.py (writes site/index.html) | env vars in ENV_CHECKLIST.md
