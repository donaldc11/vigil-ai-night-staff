# Vigil - AI night staff for funeral homes (hackathon build, FICTIONAL data)

One human Director, six AI employees (Mara Intake, Quinn Quoter, Sol Scheduler, Paige Paperwork, Faye Family Liaison, Lex Compliance Logger), each reporting to the Director.
Loop: request -> delegate -> act -> check -> human approval -> report -> improve (see demo.html).
All 10 sponsor tools appear as LOCAL MOCK adapters (sponsors.py), labeled SIMULATED. No network, keys, signups, or real data.
Run: `python3 vigil.py`, `python3 build_demo.py` (writes demo.html). Tests in tests/.
Rules built in: inbound only, recording disclosure, GPL-based quotes, no arrangement-making (licensed staff only), human approves family message and dispatch.

## Review scope
Fictional data only. Prelint reviews this PR against PRELINT_REVIEW_SPEC.md.
