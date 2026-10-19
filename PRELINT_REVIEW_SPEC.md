# Vigil agent charter and compliance spec (for Prelint review on a PR)
All data fictional. Vigil answers first calls for a funeral home outside business hours, behind one human Director.

## Scope rules (rules 2-8 have tests in tests/test_vigil.py; rule 1 holds by construction: no outbound call or messaging code exists)
1. Inbound calls only. Vigil never initiates contact with a family.
2. Every family-facing message includes a recording disclosure ("This call may be recorded"). Enforced by lint.py rule recording_disclosure.
3. No arrangement-making, contracts, signing, or payment demands. Licensed staff only. Rule no_arrangements.
4. No legal or medical advice. Rule no_medical_legal_advice.
5. Prices are informational, taken only from data/gpl.json (the General Price List), never guaranteed. Rule no_price_guarantee and test_quote_matches_gpl.
6. Two actions require human approval bound to exact content, case and gate: send_family_message, dispatch_removal_team. Enforced by vigil.require(); see TestGates.
7. Personal data: phone numbers are redacted to last 4 in logs and ledger. Inputs are capped (2000 chars) and control characters stripped.
8. Sponsor integrations report their true mode (real, simulated, fallback, external) on every run; nothing is claimed real unless the vendor answered.

## Roles (all report to the Director)
Mara intake, Quinn quoter, Sol scheduler, Paige paperwork, Faye family liaison, Lex compliance logger.

## Review requests
Check the spec against lint.py, vigil.py and the tests: are rules 1-8 actually enforced, and which are weak? Flag any wording in FAMILY_MSG that could read as arranging services or a price promise.
