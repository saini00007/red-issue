#!/usr/bin/env python3
"""Independent recon of the contact page for the /api/send endpoint."""
import re, sys, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
BASE = "https://www.infinitycapital.bh"


def get(path, tries=6):
    last = None
    for i in range(tries):
        req = urllib.request.Request(BASE + path, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            last = (e.code, body, dict(e.headers))
            print("  [%s] attempt %d HTTP %d len=%d" % (path, i + 1, e.code, len(body)))
            if e.code == 200:
                return last
            time.sleep(4)
        except Exception as e:
            print("  err", e)
            time.sleep(3)
    return last


code, html, hdrs = get("/contact")
print("STATUS:", code, "LEN:", len(html) if html else 0)
if not html:
    sys.exit(1)
open("/work/verify_contact.html", "w").write(html)

print("\n=== <form> tags ===")
for m in re.findall(r"<form[^>]*>", html):
    print(m[:400])

print("\n=== /api/ references ===")
print(sorted(set(re.findall(r"/api/[A-Za-z0-9_/\-]+", html))))

print("\n=== field names in page ===")
for f in ("targets", "subject", "msg", "cname", "check", "fname", "lname", "areacode", "tel"):
    print("  %s: %d" % (f, html.count(f)))

print("\n=== response headers (selected) ===")
for k in ("content-security-policy", "set-cookie", "x-matched-path", "server", "content-type"):
    if k in hdrs:
        print("  %s: %s" % (k, hdrs[k][:600]))
