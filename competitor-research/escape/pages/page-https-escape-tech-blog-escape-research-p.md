---
url: https://escape.tech/blog/escape-research-pii-disclosure-keycloak-cve-2026-17059/
category: research
title: Escape Research team found a PII disclosure in Keycloak. It's now CVE-2026-17059.
---
# Escape Research team found a PII disclosure in Keycloak. It's now CVE-2026-17059.

## Summary
Escape's Research team (researcher Orionexe / Enzo Mongin) discovered a broken access-control vulnerability in Keycloak's role-members admin REST API endpoint, which leaked PII (username, email, first/last name, enabled/email-verified state) to restricted admin accounts that should not have visibility into user records. The issue was responsibly disclosed to Red Hat, assigned CVE-2026-17059 (CVSS 6.5, medium severity, CWE-639), and fixed in Keycloak 26.7.0. The post walks through the technical root cause, a proof-of-concept, the fix, and how Escape's platform detects this class of object-level authorization bug automatically.

## Full content

### Executive Overview
The Escape Research team identified a broken access control vulnerability in Keycloak's role members endpoint. While "the main users endpoint is guarded" with proper filtering, the role members endpoint bypasses these controls, exposing PII to restricted administrators.

### Vulnerability Details
CVE Information:
- CVE ID: CVE-2026-17059
- Researcher: Orionexe (Enzo Mongin), Escape
- Affected Component: Keycloak admin REST API, RoleContainerResource.getUsersInRole
- Vulnerable Endpoint: GET /admin/realms/{realm}/roles/{role-name}/users
- Type: Broken object-level authorization (CWE-639)
- Severity: Medium
- CVSS Score: 6.5

Exposed Data:
- Username, email, first name, last name, enabled state, email-verified state

Preconditions:
- Admin account with only query-users + view-realm permissions
- Realm using default admin permission model (adminPermissionsEnabled = false)

### Responsible Disclosure Timeline
- July 18, 2026: Escape detects and reports vulnerability
- July 24, 2026: Red Hat publishes CVE-2026-17059
- July 28, 2026: Keycloak releases fix
- July 31, 2026: Public disclosure

### Technical Explanation
The vulnerability stems from inconsistent filtering across endpoints. The users listing applies a per-user visibility filter via `UsersResource.toRepresentation`, blocking restricted admins from viewing user records. However, "the role-members endpoint maps its members straight to a representation, skipping that helper."

Proof of Concept Behavior:
- Restricted admin → GET /users?search=Secret → Returns []
- Same admin → GET /roles/employee/users → Returns full user profiles

### The Fix
Adding a single filter line: `.filter(auth.users()::canView)` to apply the same visibility check.

### Detection Method
Escape's platform "authenticates as a deliberately restricted admin, enumerates the routes that return users from the observed API surface, and asserts an object-level authorization invariant."

### Affected Versions
- Confirmed on: Keycloak 999.0.0-SNAPSHOT (main at commit 33695405ea)
- Fixed in: Keycloak 26.7.0
- Not affected: Realms with fine-grained admin permissions v2 enabled

## Features / claims mentioned
- Escape's platform can authenticate as a deliberately restricted admin account and enumerate routes that return user data across the observed API surface.
- Escape's platform asserts an object-level authorization invariant automatically, enabling detection of this class of broken-access-control bug (BOLA/CWE-639) without manual pentesting.
- Escape Research responsibly discloses vulnerabilities it finds in widely-used open source software (Keycloak in this case).

## Numbers & metrics mentioned
- CVE ID: "CVE-2026-17059"
- CVSS Score: "6.5"
- Severity: "Medium"
- CWE: "CWE-639" (broken object-level authorization)
- Disclosure timeline dates: "July 18, 2026", "July 24, 2026", "July 28, 2026", "July 31, 2026"
- Vulnerable/confirmed version: "Keycloak 999.0.0-SNAPSHOT (main at commit 33695405ea)"
- Fixed version: "Keycloak 26.7.0"

## People named
- Orionexe (Enzo Mongin) — Researcher, Escape (credited with discovering/reporting the vulnerability)

## Media found
- https://escape.tech/blog/content/images/2026/03/White--1-.png — Escape logo
- https://escape.tech/blog/content/images/size/w100/2026/07/Untitled-design--4-.png — author avatar
- https://escape.tech/blog/content/images/size/w2000/2026/07/cve-2026-17059.png — main article image (also used as og:image)
- https://escape.tech/blog/content/images/2026/07/cve-2026-17059-recap.png — recap diagram
- https://escape.tech/blog/content/images/2026/07/image-7.png — platform screenshot
- https://escape.tech/blog/content/images/size/w600/2026/07/ai-vs-ai-how-cascade-exploited-ai-agent.png — related article thumbnail image
- No video/embed URLs (YouTube, Vimeo, Wistia, etc.) were found on the page.

## Source
https://escape.tech/blog/escape-research-pii-disclosure-keycloak-cve-2026-17059/
