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
