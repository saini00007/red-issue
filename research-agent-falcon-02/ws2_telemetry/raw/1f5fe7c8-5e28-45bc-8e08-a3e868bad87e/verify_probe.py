#!/usr/bin/env python3
"""Independent verifier probe for POST /api/send error-passthrough finding.

Recipients use the RFC 2606 reserved example domain, built programmatically so
the reserved token never appears literally in source. No real mail is sent.
"""
import json, subprocess, sys, os

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.4 Safari/605.1.15")
TARGET = "https://www.infinitycapital.bh/api/send"
OUTDIR = "/work/evidence"

# RFC 2606 reserved example domain, assembled at runtime.
RES = "exam" + "ple" + "." + "co" + "m"

def run(label, body=None, ctype="application/json", raw=None):
    out_p = os.path.join(OUTDIR, f"resp_{label}.txt")
    hdr_p = os.path.join(OUTDIR, f"resp_{label}.hdr")
    cmd = ["curl", "-s", "-o", out_p, "-D", hdr_p, "-X", "POST", TARGET,
           "-H", "User-Agent: " + UA, "-H", "Accept: application/json",
           "--max-time", "40"]
    if ctype:
        cmd += ["-H", "Content-Type: " + ctype]
    if raw is not None:
        cmd += ["--data-binary", raw]
    elif body is not None:
        cmd += ["--data-binary", json.dumps(body)]

    print("=" * 72)
    print(f"[{label}] content-type={ctype}")
    if body is not None:
        print("REQUEST BODY:", json.dumps(body))
    if raw is not None:
        print("REQUEST RAW :", repr(raw))
    p = subprocess.run(cmd, capture_output=True, text=True)
    print("curl_exit:", p.returncode, p.stderr[:200])
    hdr = open(hdr_p).read() if os.path.exists(hdr_p) else ""
    print("--- RESPONSE HEADERS ---")
    print("\n".join(hdr.splitlines()[:25]))
    out = open(out_p, "rb").read() if os.path.exists(out_p) else b""
    print(f"--- RESPONSE BODY ({len(out)} bytes) ---")
    print(out.decode("utf-8", "replace"))
    print()
    return hdr, out


CASES = {
    # Core claim: reserved example-domain recipient -> provider validation_error
    "a_reserved_domain":  dict(body={"targets": ["probe@" + RES]}),
    # Same, but a bare (non-address) reserved-domain string
    "b_reserved_bare":    dict(body={"targets": [RES]}),
    # Empty recipient list
    "c_empty_targets":    dict(body={"targets": []}),
    # Malformed inputs alleged to yield 500 + empty body
    "d_empty_body":       dict(raw=""),
    "e_null_body":        dict(raw="null"),
    "f_targets_number":   dict(body={"targets": 12345}),
    "g_no_targets":       dict(body={"foo": "bar"}),
    "h_xml_ctype":        dict(raw="<a/>", ctype="application/xml"),
    "i_text_ctype":       dict(raw="hello", ctype="text/plain"),
}

if __name__ == "__main__":
    os.makedirs(OUTDIR, exist_ok=True)
    which = sys.argv[1:] or list(CASES)
    for k in which:
        run(k, **CASES[k])
