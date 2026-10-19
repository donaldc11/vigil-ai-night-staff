"""Pre-push scan: secrets and real-data patterns. Exit 1 on any hit."""
import re, os, sys
PAT = {"api key-ish": r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
 "known key prefixes": r"\b(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|xox[bp]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,})",
 "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
 "email address": r"[A-Za-z0-9._%+-]+@(?!example\.)[A-Za-z0-9.-]+\.[a-z]{2,}",
 "US phone not 555": r"\b(?!\d{3}[-. ]?555)\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"}
bad = 0
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "out"}]
    for f in files:
        if f.endswith((".db", ".png", ".pptx", ".tgz", ".mp4", ".mp3", ".jpg")) or f == "scan_secrets.py": continue
        p = os.path.join(root, f)
        for i, line in enumerate(open(p, errors="ignore"), 1):
            for n, rx in PAT.items():
                if re.search(rx, line): print(f"{p}:{i}: {n}"); bad += 1
print("CLEAN" if not bad else f"{bad} hits"); sys.exit(1 if bad else 0)
