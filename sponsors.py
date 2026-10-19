"""Sponsor adapters. EVERY adapter here is a LOCAL MOCK (SIMULATED). No network, no keys.
Each lists the real integration point it would swap to. Nothing here calls a vendor."""
SPONSORS = {
 "n8n":       "workflow orchestration: the request->delegate->act->check->report flow runs as one n8n workflow",
 "RocketRide":"agent pipeline runner for the Intake->Quoter->Scheduler chain",
 "Prelint":   "compliance linting of every outbound message and quote before it leaves",
 "Masky":     "avatar and face for each AI employee (family-facing human face)",
 "BAND":      "shared channel where AI employees and the human director talk",
 "PromptQL":  "natural-language queries over the case ledger",
 "Flatkey":   "one key vault/gateway for model and tool credentials",
 "Tenki":     "CI runners that test the agents on every change",
 "Snyk":      "dependency and code security scan gate before deploy",
 "Paritok":   "usage metering and budget cap per agent",
}
LOG = []
def call(sponsor, action, **kw):
    assert sponsor in SPONSORS
    rec = {"sponsor": sponsor, "action": action, "mode": "SIMULATED", "detail": kw}
    LOG.append(rec); return rec
