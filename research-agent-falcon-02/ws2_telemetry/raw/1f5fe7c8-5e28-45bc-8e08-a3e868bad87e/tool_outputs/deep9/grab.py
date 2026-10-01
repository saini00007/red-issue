#!/usr/bin/env python3
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from real import fetch, save

for path, name in [("/contact", "contact.html"), ("/", "home.html"), ("/404", "404.html")]:
    st, b, h = fetch(path, tries=40)
    print("==", path, st, len(b) if b else 0)
    if b:
        save(name, b)
        txt = b.decode(errors="replace")
        # form fields
        for m in re.finditer(r'<(form|input|textarea|select|button)[^>]*>', txt, re.I):
            print("  TAG:", m.group(0)[:300])
        for m in re.finditer(r'(action|method|name|type|placeholder|id)\s*=\s*"([^"]{0,80})"', txt, re.I):
            pass
        for kw in ("resend", "/api/", "fetch(", "formAction", "name=\""):
            for m in re.finditer(re.escape(kw), txt, re.I):
                print("  KW", kw, "->", txt[max(0,m.start()-120):m.start()+180].replace("\n"," "))
                break
