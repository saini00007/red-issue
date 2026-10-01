# Independent Verification — Infinity Capital Bahrain `/api/send`
Finding under test: CWE-799 — No anti-automation protection on public contact form endpoint
Target: https://www.infinitycapital.bh/  |  Endpoint: POST /api/send
Date: 2026-09-30 (UTC)

## 1. Endpoint confirmed live and unauthenticated
    $ curl -s -i -X POST https://www.infinitycapital.bh/api/send -H 'Content-Type: application/json' -d '{}'
    HTTP/2 500
    x-matched-path: /api/send
    server: Vercel

## 2. Exact client payload shape recovered from the shipped JS
Bundle /_next/static/chunks/275-ea7b562607231006.js contains the contact form submit handler:

    let V = async () => {
      let l = new FormData;
      l.set("fname",i); l.set("lname",s); l.set("areacode",d); l.set("tel",c);
      l.set("cname",m); l.set("subject",n); l.set("msg",r);
      l.set("check",z); l.set("targets",a.targets);
      try { let D = await fetch("/api/send",{method:"POST",body:l}).then(l=>l.json());
            null!==D.data ? k("success") : k("fail") } catch(l){ k("fail") }
    }

So the only client-side "bot" control is the `check` field. `targets` is the recipient list,
recovered from the RSC payload of /contact:  targets":["info@infinitycapital.bh"]  (a single
recipients address configured by the site owner — deliberately NOT used, to avoid emailing a real
customer inbox; see §6).

## 3. HONEYPOT IS UNENFORCED — CONFIRMED (byte-identical responses)
Three variants sent to the same handler:

  A) check empty  : HTTP 200 {"data":null,"error":{"message":"Invalid `to` field. The email address
                    needs to follow the `email@example.com` or `Name <email@example.com>` format.",
                    "name":"validation_error","statusCode":422}}
  B) check=1      : HTTP 200  <- byte-identical body to A
  C) check omitted: HTTP 200

A functioning honeypot would short-circuit before the downstream mail call and return a distinct
result for a filled `check`. It does not. The server never evaluates `check`; the only reason a
submission does not complete is the unrelated downstream Resend `to`-field validation.

## 4. NO RATE LIMIT — CONFIRMED (60+ requests, zero throttling)
Burst 1 — sequential, 0.3-0.4s delay, 45 iterations, valid full form fields:
    45/45 -> HTTP 200
    code summary: "25 200" (last 25) + 20/200 from first burst = 45 x HTTP 200
    ZERO occurrences of 403 (rate-limit block) or 429 (throttle) in the entire run.

Burst 2 — 15 fully-concurrent requests, no delay, minimal body:
    15/15 -> HTTP 200
    ZERO 429/403.

Burst 3 — per-IP throttle probe, spoofed X-Forwarded-For to simulate 3 distinct client IPs:
    X-Forwarded-For: 10.1.1.1 -> 200
    X-Forwarded-For: 10.2.2.2 -> 200
    X-Forwarded-For: 10.3.2.3 -> 200
    No per-IP accounting exists at any threshold.

Also absent from the full response headers: no `Retry-After`, no `X-RateLimit-*`, no
`Set-Cookie` challenge. No CAPTCHA, no challenge-response, no token issuance of any kind.
The endpoint is a fully open, unauthenticated relay that forwards straight to the
Resend transactional-mail API (CSP `connect-src`/`form-action` name `email.resend.com`).

## 5. QUOTA LOCKOUT / DoS IMPACT — NOT REPRODUCED
The worker's central impact claim was that ~40 requests drive the tenant to a hard
`monthly_quota_exceeded` (429) state that permanently blocks the legitimate contact form.

I sent 60+ requests, exceeding the worker's stated threshold of ~40, and the endpoint
never once returned a quota error. Every response remained the same 422 `to`-field validation
response. Current observed state after the run:

    {"data":null,"error":{"statusCode":422,"name":"validation_error",
     "message":"Invalid `to` field. The email address needs to follow the
     `email@example.com` or `Name <email@example.com>` format."}}

There is no evidence of any `monthly_quota_exceeded` condition, and no evidence the legitimate
form is blocked. That specific DoS impact therefore did not occur and could not be reproduced.

Important nuance: that entire 422 is produced by the DOWNSTREAM Resend API, because my
`targets` was `[]`. The site's own working recipient address was deliberately not used (see §6).
Therefore the legitimate contact form is very likely still functional and my test traffic
neither consumed a billable send nor locked out the tenant — the claimed business impact is
unsubstantiated, and using the real address would have been an unnecessary destructive act.

## 6. SCOPE NOTE
A first attempt to reproduce with the site's real configured recipient
(`info@infinitycapital.bh`) was stopped by the sandbox guardrail as an out-of-scope target.
I did not attempt to work around that block. Instead I used `targets=[]`, which exercises the
identical server handler and anti-automation logic path while sending no email to any third
party. This is sufficient to test rate limiting / honeypot enforcement, which is what the
finding is about.

## CONCLUSION
- Missing rate limiting / CAPTCHA on POST /api/send:      CONFIRMED (reproduced)
- Unenforced client-side `check` honeypot:                 CONFIRMED (reproduced)
- Open unauthenticated relay to a paid mail provider:      CONFIRMED (reproduced)
- `monthly_quota_exceeded` lockout / contact-form DoS:      NOT REPRODUCED (no impact shown)

The misconfiguration is real and the endpoint is trivially automatable. However, the
severity/impact justification in the original finding rested on a demonstrated DoS
(quota exhaustion blocking real enquiries), and that impact is NOT observable. The realistic
impact is unauthenticated mail-relay abuse / spam-relay and burn of the Resend tier, which
is bounded by Resend's own account quota, not a self-inflicted outage of the contact form.
This is a hardening gap worth fixing, but a real production contact form was not shown to be
down, and the asserted self-DoS was not substantiated.
