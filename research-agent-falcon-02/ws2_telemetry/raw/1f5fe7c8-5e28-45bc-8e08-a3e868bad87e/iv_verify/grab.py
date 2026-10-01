#!/usr/bin/env python3
"""Extract client-side contact form logic: payload shape, fields, sanitize(), honeypot."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from probe import req

os.makedirs("js", exist_ok=True)

st, h, contact = req("/contact")
open("contact.html", "w").write(contact)
print("contact status", st, "len", len(contact))

# inline next data / form markup hints
for m in re.finditer(r'(targets|subject|sender|from_?email|company|message|check|api/send|resend)', contact, re.I):
    s = max(0, m.start()-120)
    print("---HIT---", contact[s:m.end()+160].replace("\n", " ")[:320])

chunks = sorted(set(re.findall(r'src="(/_next/static/[^"]+\.js)"', contact)))
print("\nCHUNKS:", len(chunks))
for c in chunks:
    name = "js/" + c.rsplit("/", 1)[-1]
    if os.path.exists(name):
        continue
    s2, h2, t2 = req(c)
    open(name, "w").write(t2)
    print("  got", c, s2, len(t2))
