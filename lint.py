"""Local compliance linter (real code, ours; not the Prelint product)."""
import re
RULES = [
 ("recording_disclosure", lambda t: re.search(r"may be recorded|is being recorded", t, re.I), "missing recording disclosure"),
 ("no_arrangements", lambda t: not re.search(r"\bwe (will|can|have) (arrange|schedule the service|book)|sign here|contract|you (owe|must pay)", t, re.I), "arrangement-making or payment-demand language"),
 ("no_medical_legal_advice", lambda t: not re.search(r"legal advice|medical advice|you should sue|diagnos", t, re.I), "legal/medical advice"),
 ("no_price_guarantee", lambda t: not re.search(r"guarantee|lowest price|final price", t, re.I), "price guarantee language"),
 ("length", lambda t: 0 < len(t) <= 600, "message empty or too long"),
]
def lint(text):
    if not isinstance(text, str): return ["not text"]
    return [msg for _, ok, msg in RULES if not ok(text)]

CALL_RULES = [
 ("no_promise", lambda t: not re.search(r"\bpromise|guarantee|everything will be|it will be (ok|okay|fine|alright)|don'?t worry|i assure|nothing to worry", t, re.I), "promise or false reassurance"),
 ("no_price_pressure", lambda t: not re.search(r"\$|\bprice|\bcost|\bpackage|discount|afford|\bdeal\b|\bpay\b|payment|budget|\bfee", t, re.I), "price talk on a condolence call"),
 ("no_misleading_euphemism", lambda t: not re.search(r"sleeping|better place|resting in|God needed|for a reason|passed on to|gone to|lost him|lost her|lost your", t, re.I), "euphemism that can mislead"),
 ("no_arrangements", lambda t: not re.search(r"\bwe (will|can|have) (arrange|schedule the service|book)|sign here|contract", t, re.I), "arrangement-making language"),
 ("no_medical_legal_advice", lambda t: not re.search(r"legal advice|medical advice|diagnos|cause of death", t, re.I), "legal/medical advice"),
 ("length", lambda t: 0 < len(t) <= 170, "line empty or too long"),
]
def lint_call_line(text):
    """Vera's check for the optional 'Words for the call' prompts the Director may use. Deterministic."""
    if not isinstance(text, str): return ["not text"]
    return [msg for _, ok, msg in CALL_RULES if not ok(text)]
