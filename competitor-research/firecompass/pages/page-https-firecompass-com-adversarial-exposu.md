---
url: https://firecompass.com/adversarial-exposure-validation-aev/
category: product
title: Adversarial Exposure Validation (AEV) | FireCompass
---

# Adversarial Exposure Validation (AEV) | FireCompass

## Summary
This is FireCompass's product/pillar page for its "Adversarial Exposure Validation" (AEV) offering. It defines AEV as technology that proves exploitability of exposures via live, autonomous attack execution (not simulation or risk scoring), and lays out FireCompass's four core capabilities (surface discovery, AI pentesting with proof-of-exploit, attack-path chaining, and continuous trigger-based cadence), backed by benchmark stats, a comparison table against BAS/manual red teaming, governance/safety controls, analyst recognition, an FAQ, and resource links. Page content is delivered via an embedded custom HTML widget rather than the site's normal template.

## Full content

### Hero
Eyebrow: "Named in Analyst's AEV research 2024, 2025, 2026"

**H1: Adversarial Exposure Validation (AEV) that proves exploitability, not theory**

Autonomous AI agents discover your surface, run real attacks safely, and validate every exposure with a working proof of concept. **It executes the attack. It does not simulate it.**

CTAs: "Book a Demo →" (links to /request-demo/), "Free AI Pen Test →" (links to /start-free-explorer/)

Trust bar: "30+ analyst recognitions" · "100% on XBEN, Acuart & DVWA" · "Fortune 500 customers"

### The definition — What is Adversarial Exposure Validation?
Adversarial Exposure Validation (AEV) is technology that delivers continuous, automated evidence of whether an attack is actually feasible in your environment. It runs real attack techniques against live assets and proves which exposures an attacker could exploit, each with a working proof of concept. AEV does not score risk or simulate a technique. It executes the attack and shows the result.

### Why now — Annual pentesting was built for software that shipped once a quarter.
That world is gone. Teams deploy weekly or daily, and attackers now move at machine speed (links to firecompass.com blog "The Great AI Divide" in cybersecurity). Three structural gaps open the moment testing runs on a calendar:

- **Scope gap — Tested vs attacked (20%):** Most programs test crown-jewel apps and leave shadow apps, forgotten subdomains, and API endpoints untouched. Attackers probe 100% of the surface.
- **Depth gap — Scanner false positives (up to 70%):** Scanners flag issues in isolation. Real attackers chain them. 22% of breaches start with credential abuse, and 20% begin through a peripheral asset.
- **Speed gap — 365d vs a 3-day exploit window:** Many teams still test once a year. Attackers exploit new CVEs in about 3 days. The gap widens with every release you ship.

Callout: "AEV closes the gap by validating exposure from the attacker's side. It does not guess what is risky. **It proves what is exploitable.**"

### How FireCompass delivers AEV — Four capabilities, each tied to a trigger.
A change happens, a test fires. No scheduling, no human in the critical path. Validation runs across web apps, APIs, and infrastructure.

**01 · Closes the Scope gap — Discover the surface attackers actually see**
Build your real attack surface from your name alone, so testing covers what attackers can actually reach.
- Shadow apps and forgotten subdomains surfaced from your name alone
- Leaked credentials on the deep and dark web
- API endpoints pulled from JS files and docs
- Visibility scales from about 20% to over 99% of the surface
Trigger: a new asset or subdomain appears

**02 · Closes the Depth gap — Pentest with proof, not noise**
Agents test like an attacker and confirm what is real, so your team triages exploitable findings, not false alarms.
- OWASP Top 10: 2025 plus business logic abuse
- Authenticated and unauthenticated paths, including MFA flows
- Proof of exploit for every finding, with steps to reproduce
- No exploit, no alert. That gate holds false positives under 2%
Trigger: a deployment or a fresh CVE

**03 · Closes the Depth gap — Chain findings into real attack paths**
A single finding is rarely the breach. Agents connect findings the way real adversaries do in multi-stage red teaming (links to /continuous-automated-red-teaming/), showing true blast radius.
- Credential reuse across services
- App-to-app and app-to-network lateral movement
- Privilege escalation path discovery
- Full MITRE ATT&CK kill-chain automation, no human steering
Trigger: a confirmed, exploitable finding

**04 · Closes the Speed gap — Run on your cadence, not a calendar**
Testing keeps pace with how fast you ship, so the window between a change and its validation closes to near zero.
- Triggered by deployment, CVE, or a new asset
- Matches CI/CD release cadence
- Day-1 CVE validation for new disclosures
- One-click revalidation to confirm fixes
Trigger: your release cadence

Timeline graphic contrasts: "FireCompass — A test every day, on every trigger" (tags: Code push, New asset, New CVE, On demand) vs. "Legacy pentest — One test, then blind for about 365 days."

### Run AEV band — "Run AEV against your own attack surface."
- See shadow apps, subdomains, and exposed APIs discovered from your name alone.
- Watch an agent validate a real finding with a working proof-of-concept exploit.
- Set the triggers that fire a test on every deploy, new asset, and fresh CVE.
CTA: "Free AI Pen Test →" (links to /start-free-explorer/)
Trust line: "No agents to install · Results in minutes · Trusted by Fortune 1000 enterprises"

### Proof, not adjectives — Exploit-validated findings, benchmarked in the open.
Stat cards:
- 100% — XBEN 104/104, Acuart 12/12, DVWA
- <2% — False positives vs 40-70% for scanners
- 10x — Faster: 1 day vs 2+ weeks lead time
- 11x — Cheaper: under $1,000 vs $2,400-$10,000/app

**Case: "One finding became a full compromise"**
- Exposed .git. The agent reconstructed the repo and pulled database credentials from config files.
- Direct DB access blocked. The port was not externally exposed. A scanner stops here.
- Credential reuse to SSH root. The agent tested the same creds against SSH and gained root.
- Internal pivot to data exfiltration. From the server it found private keys, pivoted, and dumped the database.
- No human steering. No predefined playbook. Agents beat our top researchers 60 to 70% of the time in internal evals.

**Case: "Fortune 500: annual program to continuous"** (before → after)
- Cost per app: ~$5,000, manual → Under $1,000
- Lead time: 2+ weeks → 1 day
- Coverage: 200 of 2,000 apps → Near-full surface
- False positives: 70% from scans → Under 2%, PoC-validated

### AEV vs the alternatives — "Most validation tools simulate. AEV executes."
Breach and attack simulation tells you whether a control caught a technique. AEV executes the attack and proves the exposure.

Comparison table (Capability | FireCompass AEV | BAS / control validation | Manual red teaming):
- Validates with a real exploit PoC: Live execution | Simulated technique only | Manual, slow
- Business logic testing: AI-driven | Not supported | Manual only
- Multi-stage attack chaining: Web to API to infra | Limited | Expert-dependent
- Continuous, trigger-driven cadence: On every change | Yes | Annual
- False positive rate: Under 2% | Not applicable, no exploitation | Low but variable
- Cost per app / test: <$1,000 | Tooling plus tuning time | $2,400 to $10,000

Note: Manual red teaming runs 2 or more weeks per engagement at $2,400 to $10,000 per app. BAS measures whether a control detects a technique, not whether the exposure is exploitable.

### Governance & safety — "Validation only works if it is safe to run in production."
A prominent global research and advisory firm says the governance layer is the part the market underestimates most. It is where we built first.
- Scope enforcement. Agents act only within defined boundaries. Nothing tests outside the authorized surface.
- Production-safe execution. Rate limits and control gates keep live systems stable while testing runs.
- Forensic audit trail. Every command, request, and response is timestamped for non-repudiation and review.
- Human-in-the-loop, optional. Run fully autonomous, or keep an expert validating before action.
- Kill switches. Stop any engagement instantly. Control over what agents can and cannot do is the design principle.
- Compliance-ready. The audit trail maps to PCI DSS 4.0, SOC 2 Type II, DORA, and ISO 27001 evidence needs.

### Backed by the industry — "Validated by the analysts who define the category."
- **Analyst** — Named in the 2025 AEV category. Recognized across pen testing and CTEM, and on the Hype Cycle four cycles running.
- **Benchmarks** — 100% · under 2% FPR. XBEN 104/104, Acuart 12/12 PoC-validated, and DVWA, fully autonomous with no human hints.
- **Recognition** — 30+ analyst reports. Across Forrester, IDC, GigaOm and a leading global research firm. GigaOm Radar Leader, 2023. RSAC Innovation Showcase.

Line: "Bruce Schneier, advisor. Trusted by Fortune 1000 enterprises."

### FAQ — "Adversarial Exposure Validation, answered."
- **What is Adversarial Exposure Validation (AEV)?** AEV is technology that delivers continuous, automated evidence of whether an attack is feasible in your environment. It runs real attack techniques against live assets and controls and proves which exposures an attacker could exploit, rather than scoring them by severity.
- **How is AEV different from breach and attack simulation (BAS)?** BAS simulates known techniques and measures whether a control detects them. AEV goes further and executes the attack, confirming exploitability with a working proof of concept. Gartner positions AEV as the successor to BAS, automated pen testing, and red teaming.
- **Does AEV replace penetration testing?** AEV replaces the calendar-based model. Instead of one annual test that covers about 20% of your surface, AEV validates exposure continuously and on triggers such as a deployment or a new CVE, with evidence behind every finding.
- **How does FireCompass keep false positives under 2%?** Every finding is executed safely against the live target and confirmed before it reaches your dashboard. That validation gate holds the false positive rate under 2%, against the 40 to 70% typical of scanners.
- **Is continuous offensive testing safe to run against production?** Yes, when the platform enforces governance. FireCompass applies scope allowlists, rate limiting, an instant kill switch, safe payload enforcement, credential scope guards, RBAC, and append-only audit logs with cryptographic timestamps.
- **How does AEV support CTEM and compliance?** AEV is the validation layer of a CTEM program (links to /continuous-threat-exposure-management/). The audit trail maps to PCI DSS 4.0, SOC 2 Type II, DORA, and ISO 27001 evidence requirements, so you can prove what was tested and how.
- **Does AEV cover APIs and infrastructure, not just web apps?** Yes. FireCompass validates exposure across web apps, APIs (links to /ai-agent-web-application-pen-test/), and infrastructure, and chains findings across them to show the real path an attacker would take.
- **Is there a free way to try AEV?** Yes. FireCompass Explorer gives teams a free, evidence-backed pen test against a business-critical web app, with results in minutes and no agents to install.

### Resources — "For security professionals"
- Reference guide: "The offensive security guide: BAS, CTEM, CART, pen testing, VA, AEV, and COST" — A practical map of the offensive security categories and where AEV fits. (/offensive-security-guide-bas-ctem-cart-pentest-va-aev-cost/)
- Blog: "Continuous Offensive Security Testing Is Becoming a Category. Here's What Most People Will Get Wrong" — What the shift to continuous testing really means, and why validation, not simulation, is the line. (/blog-continuous-offensive-security-testing-cost/)
- Use case: "Agentic web application and API penetration testing" — The agentic platform behind AEV, aligned to OWASP Top 10: 2025. (/ai-agent-web-application-pen-test/)

### Final CTA
Eyebrow: "Hack yourself before AI does"
H2: "Prove what an attacker can actually reach"
"See validated exploits against a business-critical web app, not a list of maybes. Book a session with a FireCompass security expert."
CTA: "Book a Demo →" (/request-demo/)

## Features / claims mentioned
- Autonomous AI agents discover attack surface, run real attacks safely, and validate every exposure with a working proof of concept ("executes the attack, does not simulate it").
- Attack surface discovery from company name alone: shadow apps, forgotten subdomains, leaked credentials on deep/dark web, API endpoints pulled from JS files and docs.
- Automated web/API pentesting aligned to OWASP Top 10: 2025, including business logic abuse and authenticated/unauthenticated paths (including MFA flows).
- Proof-of-exploit generated for every finding, with reproduction steps; "no exploit, no alert" gating policy.
- Multi-stage attack chaining: credential reuse across services, app-to-app and app-to-network lateral movement, privilege escalation path discovery, full MITRE ATT&CK kill-chain automation with no human steering.
- Trigger-based/continuous testing cadence: fires on code push, new asset, new CVE, or on-demand; matches CI/CD release cadence; Day-1 CVE validation; one-click revalidation.
- Governance/safety controls: scope enforcement, production-safe execution (rate limits/control gates), forensic/audit trail with timestamps, optional human-in-the-loop, kill switches, compliance mapping (PCI DSS 4.0, SOC 2 Type II, DORA, ISO 27001).
- "FireCompass Explorer" — free evidence-backed pen test against a business-critical web app, results in minutes, no agents to install.
- Positioned as the successor category to BAS (breach and attack simulation), automated pen testing, and red teaming (attributed to Gartner in FAQ copy).
- Comparison claims FireCompass AEV offers live exploit execution vs. BAS's simulated-technique-only approach and manual red teaming's slow, expert-dependent process.

## Numbers & metrics mentioned
- "30+ analyst recognitions"
- "100% on XBEN, Acuart & DVWA" (also stated as "XBEN 104/104, Acuart 12/12, DVWA")
- Scope gap: "20%" tested vs. attacked (attackers probe 100% of the surface)
- Depth gap: "up to 70%" scanner false positives
- "22% of breaches start with credential abuse"
- "20% begin through a peripheral asset"
- Speed gap: "365d" (annual testing) vs. "a 3-day exploit window" for new CVEs
- Visibility scaling: "about 20% to over 99% of the surface"
- False positive rate: "under 2%" (FireCompass) vs. "40-70%" for scanners
- "10x Faster: 1 day vs 2+ weeks lead time"
- "11x Cheaper: under $1,000 vs $2,400-$10,000/app"
- Fortune 500 case study: cost per app ~$5,000 (manual) → under $1,000; lead time 2+ weeks → 1 day; coverage 200 of 2,000 apps → near-full surface; false positives 70% (scans) → under 2% (PoC-validated)
- "Agents beat our top researchers 60 to 70% of the time in internal evals"
- Comparison table: cost per app/test "<$1,000" (FireCompass) vs. "$2,400 to $10,000" (manual red teaming); manual red teaming runs "2 or more weeks per engagement"
- "GigaOm Radar Leader, 2023"
- "Named in Analyst's AEV research 2024, 2025, 2026" (hero eyebrow)
- "Named in the 2025 AEV category"; "Hype Cycle four cycles running"
- Compliance frameworks referenced: PCI DSS 4.0, SOC 2 Type II, DORA, ISO 27001

## People named
- **Bruce Schneier** — listed as "advisor" to FireCompass.
- No other individual names (founders, researchers, or authors) are mentioned on this page. Analyst firms are referenced generically/anonymized in places ("A prominent global research and advisory firm," "a leading global research firm," "Analyst") alongside named firms Forrester, IDC, and GigaOm, and RSAC (RSA Conference) Innovation Showcase.

## Media found
- Image: `https://firecompass.com/wp-content/uploads/2024/07/logo-1.png` — alt "FireCompass logo" (site header logo; also has a 300px srcset variant `logo-1-300x50.png`)
- Image: `https://firecompass.com/wp-content/uploads/2025/11/Clean-Up-Design-4.png` — alt "FireCompass attack surface discovery across apps, APIs and shadow IT" (product diagram/screenshot for capability 01; also used as the page's og:image)
- Image: `https://firecompass.com/wp-content/uploads/2025/11/Clean-Up-Design-7.png` — alt "FireCompass automated web and API penetration testing with proof of exploit" (product diagram/screenshot for capability 02)
- Image: `https://firecompass.com/wp-content/uploads/2025/11/Clean-Up-Design-6.png` — alt "FireCompass multi-stage red teaming and attack-path chaining" (product diagram/screenshot for capability 03)
- No customer/partner logo images found on this page (customer references are text-only: "Fortune 500 customers," "Trusted by Fortune 1000 enterprises").
- No video or third-party embeds (YouTube/Vimeo/Wistia) found. The only iframe present is a Google Tag Manager noscript tracking iframe: `https://www.googletagmanager.com/ns.html?id=GTM-MPQ67V7` (hidden, 0x0, not content).
- Meta: og:image = `https://firecompass.com/wp-content/uploads/2025/11/Clean-Up-Design-4.png`

## Source
https://firecompass.com/adversarial-exposure-validation-aev/
