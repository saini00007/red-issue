# Escape — Competitive Dossier

*Compiled from 20 first-party pages crawled from escape.tech / docs.escape.tech, plus an independent external-research pass (news, funding databases, review sites, GitHub, conference pages, podcasts, job boards). Research date: 2026-09-26.*

---

## Executive summary

Escape (Escape Technologies SAS) is a Paris-founded, AI-native offensive security engineering platform that replaces legacy vulnerability scanners and manual, point-in-time pentests with AI agents that continuously discover, test, and remediate vulnerabilities directly inside customer engineering workflows. Founded in 2020 by CEO Tristan Kalos and CTO Antoine Carossio and launched publicly out of Y Combinator's W23 batch, the company started as a GraphQL/API-focused DAST vendor and has since expanded into a four-part platform: Attack Surface Management (ASM), Business-Logic-Aware DAST, AI Pentesting (branded "Cascade"), and External Network Pentesting, unified by a proprietary, entirely in-house-built detection stack ("zero third-party engines"). Its flagship differentiator is business-logic and authorization testing (BOLA/IDOR, multi-tenant access-control flaws) — a class of vulnerability that traditional injection/XSS-focused DAST and generic LLM agents largely miss — proven via Cascade's multi-agent architecture, which builds a persistent, compounding model of each customer's application and turns every proven finding into a permanent CI/CD regression test. The company has raised roughly $23–24M across a 2023 seed (€3.6M) and a March 2026 Series A ($18M led by Balderton Capital), counts 2,000+ security teams as customers (Sorare, Shine/Société Générale, Neo4j, Visma, DoubleVerify, Arkose Labs, Sigma Computing, Applied Systems, and others), and has an active in-house research team publishing CVEs (e.g., a Keycloak PII-disclosure bug, CVE-2026-17059) and adversarial AI-security research (e.g., jailbreaking a production AI agent, XSS in AI chatbox Markdown renderers). As a competitor, Escape matters because it occupies the fast-growing "agentic pentesting" / continuous offensive security category, competes directly with both traditional DAST vendors (Invicti, StackHawk, Bright Security) and newer AI-pentesting entrants (XBOW, Pentera, Horizon3.ai/NodeZero, Aikido), and backs its marketing claims with published head-to-head benchmarks (against Claude Code/Opus, Aikido, and Xbow on OWASP Juice Shop, Fider, and Photoview) and reputable investors/advisors (Datadog's Olivier Pomel, Tenable's Renaud Deraison, Qualys founder Philippe Langlois).

---

## Company facts

| Attribute | Detail |
|---|---|
| Legal name | Escape Technologies SAS |
| Founded | 2020 |
| Founders | Tristan Kalos (CEO), Antoine Carossio (CTO) |
| HQ | Paris, France (Station F); described in 2026 as operating across "two continents" (Europe and US), with an office in New York in addition to Paris |
| Y Combinator batch | Winter 2023 (W23) |
| Headcount (est.) | ~29 employees per Y Combinator's company page (2026 snapshot); LinkedIn/ZoomInfo listings are ambiguous due to unrelated companies also named "Escape" |
| Compliance | SOC 2 Type II compliant (per external review) |
| Mission | "Offensive security for the teams that are 100x outnumbered" — AI agents that discover, test, and remediate vulnerabilities directly in engineering workflows |

### Founders / key hires (site-stated)
- **Tristan Kalos** — Co-founder & CEO. Site bio: "Ex-AI Researcher, UC Berkeley." External sources add: worked in San Francisco building chatbots/APIs before Escape; motivated to found the company after a client's MongoDB database was hacked/held for ransom (~2017–2018).
- **Antoine Carossio** — Co-founder & CTO. Site bio: "Ex-Security Engineer, Apple." External sources add: also a former penetration tester/security engineer for the French Government; open-source GraphQL security maintainer (e.g., Clairvoyance).
- **Mathieu Rousse** — Head of Engineering. Site bio: "Ex Team Lead Engineering, Datadog." (Not found in external sources — first-party only.)
- **Yohan Testemale** — Technical Account Manager (named as an example employee on the About page).

### Funding table

| Round | Amount | Date | Lead / Investors |
|---|---|---|---|
| Seed | €3.6M (~$3.9M) | June 2023 | Led by **IRIS**; with Frst, Y Combinator, Irregular Expressions, Tiny Supercomputers, Kima Ventures; angels: Philippe Langlois, Mehdi Medjaoui, Roxanne Varza |
| Series A | $18M (€15.4M) | March 10, 2026 | Led by **Balderton Capital**; with Uncorrelated Ventures, IRIS, Y Combinator |
| **Total disclosed** | **~$23–24M** across 3 tranches | — | Crunchbase aggregate; valuation not disclosed anywhere |

### Investors & backers (per Escape's own About page)
**Venture firms:** Balderton Capital ("25-year multistage firm"), IRIS Ventures, Y Combinator, Uncorrelated Ventures ("$750M+ AUM"), Frst.vc, Kima Ventures, Tiny Supercomputer Investment, Irregular Expressions.

**Named individual investors/advisors (first-party, notably richer than external sources found):**
- Olivier Pomel — Datadog Co-founder/CEO
- Renaud Deraison — Tenable Co-founder/CEO
- Philippe Langlois — Qualys founder, P1 Security CEO
- Amit Agarwal — former Datadog CPO & President
- Uri Goldshtein — The Guild founder
- Roxanne Varza — STATION F Director, Sequoia Scout
- Mehdi Medjaoui — ALIAS.dev founder, APIdays
- Victor Coisne — Strapi VP Marketing
- Alexis Monville — Red Hat ex-Chief of Staff to CTO
- Amirhossein Malekzadeh — Logmatic.io Co-founder/CEO
- Sam Hatoum — Xolvio CEO/Founder
- Gabriel-James Safar — Tsuga Co-founder/CEO

**Reconciliation note:** the site names ~12 individual advisors beyond the two the external OSINT pass surfaced (Philippe Langlois, Mehdi Medjaoui, Roxanne Varza) — a good example of the general pattern that the company's own About page is the richer, more current source for people/credibility signal, while external sources are needed for funding amounts/dates and headcount, which the site does not state at all.

---

## Products & full feature list

Escape's site organizes itself around four core products (a fifth, "AI-powered Remediation," is presented on the homepage as a cross-cutting capability rather than a separately sold product).

### 1. Attack Surface Management (ASM)
Positioned against "legacy EASM tools" that only find hosts/ports; Escape claims to map "everything engineers build and expose at the application layer" — APIs, SPAs, and AI applications — in real time.

- **Agentless API Discovery** — maps exposed and internal APIs, including shadow APIs, without requiring an installed agent. Mechanism: subdomain enumeration + AI-powered fingerprinting + OSINT techniques + integration with code repositories (GitHub, GitLab); combined technique set the site calls "agentless technology based on a sophisticated combination of techniques." Deployment is described as adding a domain name to the exploration scope.
- **AI Proof of Exploit & Remediation** — delivers code-level fixes plus proof-of-exploit traces for discovered assets/issues.
- **Automated Asset Mapping** — routes findings to the correct code owners and product teams automatically.
- **Integration Capabilities** — connects with the Wiz cloud risk platform (shares prioritized findings: inventory, vulnerabilities, configuration) and other developer tools (Akamai, AWS, Postman referenced elsewhere on the site).
- **Visage surface scanner** (introduced via the vibe-coding research post) — a lightweight, read-only scanner that harvests frontend artifacts (secrets, routes) without executing destructive actions; feeds results into the ASM inventory and is connected to the DAST scanner.
- Stated results: discovery of an entire API attack surface "within about an hour" (customer quote, Arkose Labs); "30% more assets discovered" than legacy ASM tools; "229% detection increase" cited on the homepage.

### 2. Business-Logic-Aware DAST
Marketed as "THE FIRST Business-Logic-Aware DAST." AI agents discover, test, and remediate vulnerabilities directly in engineering workflows, going beyond legacy injection/XSS-only scanning.

- **Proprietary Business Logic Security Testing (BLST) algorithm** — feedback-driven, adaptive API/graph exploration (as opposed to brute-force scanning), using techniques the site/comparison pages name as "Sourcing Inference" and "Strong Typing Inference" to construct accurate, context-aware test requests.
- **Native GraphQL testing** — 100+ GraphQL-specific tests covering introspection, type-aware payload generation, resolver testing, aliasing/batching attacks, and access-control issues; GraphQL is handled natively rather than as "another HTTP API." REST and GraphQL are supported natively; SOAP and gRPC are covered via the ASM layer.
- **Multi-user / role-based (business logic) testing** — holds multiple simultaneous authenticated user identities/sessions to test authorization boundaries between roles, surfacing BOLA/IDOR and broken access control that single-identity scanners structurally cannot find.
- **AI-powered authentication support** — OAuth 2.0/OAuth, SAML, password, TLS, TOTP MFA, AWS Cognito, JWT, Playwright-based custom login flows; an AI agent auto-detects and fills login fields and pinpoints the exact location of authentication failures for debugging; supports pre-scan "Test Configuration" validation before a full run.
- **Incremental / CI-integrated scanning** — scans only changed endpoints on pull requests; integrates with GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket, CircleCI; open-source, single-binary CLI manages configs/integrations/scan locations; public API (v3, released ~Aug 2025) and MCP support for triggering scans from pipelines.
- **Vulnerability prioritization / "Escape Severity"** — a business-context-aware severity/risk funnel that factors vulnerability type, exploitability, CVSS, and other risk signals; the company explicitly moved away from a pure CVSS-based system (~August 2024).
- **Remediation guidance** — ready-to-merge, framework-specific code fixes, shareable into Jira with pre-filled remediation steps (contrasted against competitors' "generic recommendations").
- Stated results: "+63% more complex true positives" vs. legacy DAST; "≤4% false-positive rate"; "80% time-to-remediation reduction"; "12 hours saved per security engineer per month"; "4 hours saved on daily builds"; supports "50 deploys/week" without becoming a bottleneck; positioned so "one AppSec engineer can cover a 500-person dev org."

### 3. AI Pentesting ("Cascade")
Escape's agentic, continuous penetration-testing engine, launched publicly via a detailed architecture post in June 2026 (though positioning suggests development/rollout began around July 2025 per external sources).

- **Multi-agent harness with a central orchestrator** — replaces an earlier model of fixed, single-purpose agents (one each for XSS, SQLi, IDOR, etc.). Cascade instead creates the specialist agents a target actually needs, on demand.
- **Four agent roles:**
  - *Orchestrator* — plans the engagement, breaks it into tasks, spawns other agents, decides when the engagement is complete, and prioritizes work within scope/users/context/time budget.
  - *Coverage agent* — explores surfaces and proposes follow-up work from coverage gaps, acting as an advisory auditor with no exploitation tools of its own.
  - *Exploitation agents* — focused, dynamically spawned agents for specific jobs (e.g., "SQLi discovery on the reporting API"); run in parallel; stop consuming budget once a task returns.
  - *Reporter agent* — independently reproduces each candidate finding on the live target and collects its own evidence before filing an issue; deliberately isolated from agent-to-agent exploitation messaging so its verification stays independent.
- **Shared coordination substrate** — a shared message bus (seeded topics: recon, xss, sqli, idor, ssrf, auth, rce) and a shared knowledge store let discoveries propagate across the swarm; context flows back through the orchestrator after every step.
- **"Becomes an expert in your business"** — Cascade sits on top of ASM and DAST, so it starts every engagement with the platform's existing model of the customer's attack surface (every API, SPA, host, everything DAST covers) and retains memory of business context across engagements (e.g., that a customer is in healthcare with admin/doctor/patient roles).
- **Multi-user identity testing** — holds several user identities simultaneously, each in an isolated browser session, specifically to answer authorization questions like "can user A read user B's order?"
- **Discovery-first exploitation** — a dedicated discovery agent maps the entire scope before exploitation begins; coverage gaps are actively monitored and closed in real time during the engagement; every discovered endpoint/page/asset is surfaced in results.
- **Proof, not assertion** — every finding ships with the exact request sequence, user scopes involved, a working exploit, reasoning logs (full orchestrator chain-of-thought), and framework-specific remediation guidance.
- **Compounding regression testing** — every proven Cascade finding flows into Escape DAST and becomes a permanent regression test that re-runs on every release/CI build.
- **Black-box and white-box modes** — supports testing without source access (black-box, useful for third-party integrations/regulatory boundaries/supplier assessments) and with source access (white-box, deeper for code-path-dependent bugs); "Whitebox pentesting" was announced as newly available (Jul 31, 2026 blog post).
- **Flexible input/launch** — accepts OpenAPI specs, Postman collections, HAR recordings, Burp exports, prior pentest reports as context; can target multiple assets in one engagement; launchable via public API and MCP as well as the UI; a four-step launch flow (scope URLs → add user accounts → tune context/duration → review & launch).
- Compliance framing: supports PCI-DSS, SOC 2, and ISO 27001 reporting needs.

### 4. External Network Pentesting
- Continuous, internet-facing testing of hosts, ports, and services — "every host, port, and exposed service is probed the way an attacker would," with proof of what's exploitable, followed by a retest.

### AI-powered Remediation (cross-cutting capability, homepage)
- Delivers AI-assisted remediation with real code suggestions tailored to the customer's specific framework; stated as "<1 min code snippet generation."

### Related open-source projects (confirm technical depth; external-sourced)
- **graphql-armor** — security middleware for Apollo/Yoga/Envelop GraphQL servers (site claims 267,101 weekly downloads as of the Research page; external sources cite 100,000+ weekly npm downloads — see Contradictions below).
- **graphinder** — GraphQL endpoint finder via subdomain enumeration.
- **goctopus** — GraphQL discovery/fingerprinting toolbox.
- **awesome-graphql-security** — curated list of GraphQL security tools.
- **graphql-security-academy** — free browser-based GraphQL security learning platform.
- **Clairvoyance** — GraphQL introspection/field-suggestion tool maintained by Antoine Carossio (external source only).

---

## Platform architecture / how it works

- **"Zero third-party engines"** — Escape states all detection technology (DAST engine, ASM discovery, Cascade agentic pentesting) is built entirely in-house rather than licensed or wrapped around third-party scanners.
- **Five active in-house research tracks** (per the Research page), positioned as the technical foundation under all products:
  1. **Code-to-Cloud Security Intelligence** — links static code structure to runtime behavior across microservices, enabling automated asset-to-code-owner mapping and code-aware remediation.
  2. **Agentic Offensive Security** — uses reinforcement learning for autonomous security testing; this is the research track underlying Cascade.
  3. **AI-Powered Vulnerability Remediation** — connects runtime vulnerabilities back to source code for faster, framework-specific fixes.
  4. **Vision AI Authentication** — uses vision-capable AI to automate authentication flows (including CAPTCHA/MFA-gated logins) for dynamic testing without brittle recorded-login scripts.
  5. **Intelligent Asset Correlation** — maps relationships between source repositories and deployed APIs to keep the asset inventory accurate as code changes.
- **Discovery mechanism (ASM):** subdomain enumeration → AI-powered fingerprinting → OSINT reconnaissance → static frontend (JS/HTML) analysis and headless-browser crawling/route enumeration → API discovery via both documented routes and brute-forced common paths. For large-scale research (e.g., the Fortune 1000 study), this pipeline additionally used LLMs plus Abstract Syntax Tree (AST) parsing to auto-generate missing OpenAPI-style specifications for undocumented endpoints (4,547+ specs generated in that study).
- **Testing mechanism (DAST):** a proprietary, "feedback-driven" exploration algorithm builds and refines requests using "Sourcing Inference" and "Strong Typing Inference," rather than brute-force fuzzing — allowing it to reach deeper application/business-logic states, especially in GraphQL and SPA architectures.
- **Testing mechanism (Cascade/AI Pentesting):** orchestrator-centric multi-agent system (detailed under Products above) using reinforcement learning (per the Research page) for autonomous decision-making, dynamically spawned specialist agents with small/modular "skill" prompts (rather than one large fixed prompt), a shared message bus and knowledge store for inter-agent signal sharing, and an independent reporter agent for de-biased verification.
- **Validation methodology:** every finding — from a DAST scan or from Cascade — must be proven with a working exploit/reproducible request chain, not just flagged as a theoretical risk; findings include screenshots/execution logs (DAST) or full reasoning logs and attack chains (Cascade). Escape frames this as differentiating it from "generic scan reports."
- **Deployment model:** agentless (no proxy, no installed agent, no network appliance) — deployment is described as simply adding a domain/target to scope; integrates into CI/CD via a public API, an open-source single-binary CLI, and native pipeline integrations (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket, CircleCI). Also exposes an MCP interface for programmatic/agentic launch of engagements.
- **Integrations:** Wiz (cloud risk/CNAPP — sharing inventory, vulnerabilities, configuration; won Wiz's inaugural WIN Partner Award, 2025, per external sources), AWS (Marketplace listings, ISV Accelerate Program), GitHub, GitLab, Akamai, Postman, Jira.
- **Compliance-oriented output:** maps findings/coverage to 20+ compliance frameworks including PCI-DSS, HIPAA, CRA (Cyber Resilience Act), SOC 2, and ISO 27001; stated as enabling sub-1-minute compliance report generation.

---

## Pricing & packaging

**Not publicly disclosed** — Escape's own pricing page carries no tiers or dollar figures. Its positioning:

- "Automate offensive security lifecycle, without the token burn" — Escape runs ASM, DAST, and AI pentesting "as one continuous program," pitched as flat/predictable billing ("your bill doesn't spike the more you scan") rather than per-scan or per-action billing.
- Custom, scoped pricing: "Talk to our team about scoping pricing to your environment."
- **AWS Marketplace path** — available for purchase against existing AWS committed spend.
- **Channel partners** — "We work with 20+ channel partners worldwide"; named partners from a blog post include ConRes, Myriad360, EverSec, and Technium.

**External-sourced detail (site doesn't disclose these):**
- AWS Marketplace listing shows an Enterprise Plan with three capacity tiers: up to 15, 60, or 120 scanned applications, each with unlimited scan frequency and dedicated technical support; Private Offers available for negotiated pricing.
- An independent review (AppSecSanta) reports a free tier for scanning a single API, with paid pricing scaling by application count, testing-scope depth, and private-location requirements — described as positioned similarly to Bright Security (mid-market tier) rather than XBOW's ~$6,000-per-pentest/credit-pack model.

---

## Customers, case studies & partners

### Named customers (first-party, from case studies / testimonials / logos)
Amp, Sigma Computing, Bridgetech Group, an unnamed European FinTech platform, Applied Systems, DoubleVerify, Arkose Labs, French Football Federation, Sungage Financial, Lightspeed, Shine (Société Générale's online banking subsidiary), Thinkific, Sorare (per external sources — CTO quote about finding flaws "human security auditors have not seen"), Neo4j (external sources), Visma, Schibsted, Miro, ControlUp, Health Equity, Kubra, Cato Networks, PandaDoc, DataVault. BetterHelp, CyberCube Analytics, and Arkose Labs appear in a single external funding writeup (SiliconANGLE) as lower-confidence/single-source.

### Full case-study list (13 published, reverse-chronological)
| Case study | Author | Date | Read time |
|---|---|---|---|
| How Amp got its SOC 2 Type II pentest evidence in hours | Alexandra Charikova | Sep 9, 2026 | 7 min |
| How Escape DAST helped Sigma Computing achieve complete GraphQL API endpoint coverage | Sanjana Iyer | Jul 30, 2026 | 9 min |
| Bridgetech Group — automated evidence for ISO 27001 | Alexandra Charikova | Jun 19, 2026 | 6 min |
| European FinTech Platform — business logic testing at scale | Alexandra Charikova | May 8, 2026 | 6 min |
| Applied Systems — overcoming complex authentication challenges | Alexandra Charikova | Oct 30, 2025 | 4 min |
| AI-Driven Applications Security (feat. DoubleVerify's Seth Kirschner) | Harikiran Nannapaneni | Jul 7, 2025 | 11 min |
| Arkose Labs — deeper business logic testing | Alexandra Charikova & Sanjana Iyer | May 8, 2025 | 4 min |
| DoubleVerify — full API visibility via Wiz + Escape | Alexandra Charikova | Apr 25, 2025 | 8 min |
| French Football Federation — securing online services | Alexandra Charikova | Jul 4, 2024 | 3 min |
| Sungage Financial — GraphQL APIs secured in 1 week | Mia Berthier | Jun 11, 2024 | 3 min |
| Lightspeed — full compliance via GraphQL APIs | Alexandra Charikova | Nov 9, 2023 | 3 min |
| Shine (Société Générale) — banking security enhancement | Alexandra Charikova | Oct 5, 2023 | 4 min |
| Thinkific — enterprise-grade security for federated architecture | Alexandra Charikova | Oct 2, 2023 | 4 min |

### Named testimonial quotes (site)
- **Seth Kirschner**, Sr. AppSec Manager, DoubleVerify: "Escape is really powerful on dynamic scanning and mapping API attack surface to business challenges," and elsewhere credits "the combination of Wiz and Escape" for API discovery/inventory/testing success.
- **Michael Bourgault**, Sr. Security Architect, Arkose Labs: "Within about an hour, we had all our API attack surface scanned," and "Time-to-value ratio is 100% there. Escape DAST is purpose-built to protect APIs."
- **Andrew Orr Erwing**, Security Engineering Manager, Applied Systems: "It gives a good remediation process and steps to reproduce, which makes our team 10 times more efficient for validating vulnerabilities."
- **Daniel Ilies**, IT Security Engineer, Visma: "Escape's IDOR scanning and multi-tenant capabilities set it apart... Support team is incredibly responsive to feedback."
- Unnamed "Team Lead, Offensive Security," global payments & fintech platform (from the Cascade launch post): confirmed a Cascade-found business-logic pricing bug matched an issue they'd separately been chasing manually.
- Unnamed Cyber Security Attack Surface Team Leader at an unnamed global organization: describes monitoring public exposure across a diverse footprint including shadow IT.
- Seth Kirschner is also referenced, in one page, as being at "DataVault" rather than DoubleVerify — see Contradictions below.

### Partners
- **Wiz** — technology/integration partner (CNAPP integration sharing inventory, vulnerabilities, configuration); per external sources, won Wiz's inaugural "WIN" (Wiz Integrations) Partner Award in 2025.
- **AWS** — Marketplace listings ("Business-logic-aware DAST," "AI Pentesting," "Attack Surface Management," "Sherpa by Escape Technology" per external sources); AWS ISV Accelerate Program member.
- **Channel partners** — 20+ worldwide; named examples: ConRes, Myriad360, EverSec, Technium.
- **Anthropic's Cyber Verification Program** — Escape joined to "advance AI-powered offensive security" (blog post, Aug 4, 2026).
- **OpenAI's Trusted Access for Cyber (TAC)** — Escape joined for the same purpose (blog post, Aug 3, 2026).

---

## Key numbers & metrics

| Metric | Value | Date | Source |
|---|---|---|---|
| Security teams using the platform | 2,000+ globally | 2025–2026 (repeated) | escape.tech (homepage, docs.escape.tech), SecurityWeek |
| Customers within 6 months of 2023 launch | 1,000+ organizations | mid-2023 | IRIS.vc (external) |
| Monthly security assessments run | 300,000+ | March 2026 | SiliconANGLE (external, single-source/lower confidence) |
| Fortune 1000 + CAC 40: exposed APIs found | 30,784 total (28,500+ Fortune-1000-specific per external write-up) | Nov 20, 2024 | escape.tech blog ("Fortune 1000 at risk") |
| Fortune 1000 + CAC 40: vulnerabilities found | 107,368 total; 2,038 highly critical (Fortune-1000-specific external figure: 98,800 / 1,830) | Nov 20, 2024 | escape.tech blog |
| Fortune 1000: exposed development APIs | 3,650 | Nov 20, 2024 | escape.tech blog |
| Fortune 1000: exposed API secrets (tokens/keys/creds) | 1,800+ | Nov 20, 2024 | escape.tech blog |
| Subdomains discovered (Fortune 1000 research) | 158,079 | Nov 20, 2024 | escape.tech blog |
| API specs auto-generated via LLM+AST (Fortune 1000 research) | 4,547+ | Nov 20, 2024 | escape.tech blog |
| Vibe-coded app research: assets scanned | 14,600 (5,600 web apps, 1,280 API services, 6,500 hosts, 1,103 schemas) | Oct 29, 2025 | escape.tech blog (methodology post) |
| Vibe-coded app research: vulnerabilities found | 2,038 highly critical (2,000+ headline figure) across 1.4K–5,600 apps (see Contradictions) | Oct 29, 2025 / Mar 2026 | escape.tech blog, tech.eu |
| Vibe-coded app research: exposed secrets | 400+ | Oct 29, 2025 | escape.tech blog |
| Vibe-coded app research: PII exposure instances | 175 | Oct 29, 2025 | escape.tech blog |
| Customer ROI | 393% ROI; security testing cycle cut from 5 days to 5 hours | 2025–2026 | escape.tech (About, AI Pentesting product page), external (single-source corroboration) |
| DAST: more complex true positives vs. legacy DAST | +63% | n/d | escape.tech (product/dast page) |
| DAST: false-positive rate | ≤4% | n/d | escape.tech (product/dast page) |
| DAST: time-to-remediation reduction | 80% | n/d | escape.tech |
| Time saved per security engineer per month | 12 hours | n/d | escape.tech |
| Time saved on daily builds | 4 hours | n/d | escape.tech |
| Homepage: security review cycle improvement | 80% | n/d | escape.tech (home) |
| Homepage: coverage improvement over legacy solutions | 3900% | n/d | escape.tech (home) |
| Homepage: more assets discovered vs. legacy ASM | 30% | n/d | escape.tech (home) |
| Homepage: ASM detection increase | 229% | n/d | escape.tech (home) |
| Application risk reduction within first weeks | 50% | n/d | escape.tech (home) |
| Time to map entire API attack surface | <1 hour | n/d | escape.tech (ASM product page) |
| GraphQL Armor weekly npm downloads | 267,101 (site) vs. 100,000+ (external) — see Contradictions | 2026 | escape.tech (Research page) vs. AppSecSanta |
| GraphQLConf 2023 research: endpoints scanned / issues found | 1,500+ endpoints; 46,000+ security issues/data leaks (~10% critical) | 2023 | GraphQL.org session page (external) |
| Cascade research benchmark: true positives vs. bare frontier model | 3–4× | n/a (ongoing) | escape.tech (Research page) |
| G2 rating | 5.0 / 5.0 | 2026 | G2 (external) |
| Total funding disclosed | ~$23–24M | through Mar 2026 | Crunchbase (external) |
| Estimated headcount | ~29 employees | 2026 | Y Combinator company page (external) |

---

## Research & latest important work

Reverse-chronological, based on the crawled blog index and individual research posts (dates as published on-site; "2026" dates reflect the site's forward-dated blog cadence at crawl time):

1. **"What an External Penetration Test is And How One is Actually Run"** — Antoine Carossio, **Sep 11, 2026** (15 min). Cites Mandiant's M-Trends 2026 (32% of intrusions in 2025 via exploited vulnerabilities). — *Most recent piece at crawl time.*
2. **"How to build a continuous pentesting program"** — Antoine Carossio, Sep 10, 2026 (10 min). Cites Verizon's 2026 DBIR (31% unpatched-flaw entry point, 43-day median time-to-fix).
3. **"How Amp got its SOC 2 Type II pentest evidence in hours"** — Alexandra Charikova, Sep 9, 2026 (7 min). Case study.
4. **"LLM security testing: how to pentest LLMs and MCP servers"** — Antoine Carossio, Aug 26, 2026 (19 min). Maps attacks to the OWASP LLM Top 10; tests vulnerable MCP servers.
5. **"Escape found the same XSS in two AI chatboxes. The vulnerability was in the Markdown renderer."** — Gwendal Mognier & Geoffrey Diederichs, Aug 21, 2026 (7 min). Independent discovery, at two unrelated companies, of a stored XSS via `react-markdown` + `rehype-raw` (no sanitization) exploited through `iframe srcdoc` injection; cross-references CVE-2026-32308 (OneUptime) and CVE-2026-17496 (NoteGen).
6. **"Horizon3.ai alternatives in 2026: Escape vs NodeZero and 4 more tools"** — Alexandra Charikova, Aug 20, 2026 (21 min).
7. **"Introducing Escape's Channel Partners"** — Sanjana Iyer, Aug 20, 2026 (5 min). ConRes, Myriad360, EverSec, Technium.
8. **"Escape vs Pentera: how each one proves exploitability (2026)"** — Alexandra Charikova, Aug 19, 2026 (14 min).
9. **"Pentera Alternatives for Continuous Pentesting: 7 Competitors Compared In-Depth"** — Alexandra Charikova, Aug 19, 2026 (21 min).
10. **"Escape vs StackHawk: full DAST comparison 2026"** — Alexandra Charikova, Aug 14, 2026 (20 min).
11. **"AI vs AI: How Cascade exploited an AI agent in production"** — Yacine Souam, Aug 14, 2026 (4 min). Cascade bypassed a production prompt-injection guardrail via semantic reframing rather than a cleverer payload, exfiltrating a full synthetic system prompt.
12. **"Authenticated scanning behind OAuth, MFA, and CAPTCHA"** — Alexandra Charikova, Aug 12, 2026 (10 min).
13. **"Continuous penetration testing: what it means when the testing never stops"** — Alexandra Charikova, Aug 12, 2026 (10 min). References Anthropic's late-2025 disclosure of the first documented largely-AI-run cyberattack.
14. **"Penetration testing as a service (PTaaS), explained"** — Antoine Carossio, Aug 6, 2026 (10 min).
15. **"Escape joins Anthropic's Cyber Verification Program..."** — Alexandra Charikova, Aug 4, 2026 (2 min).
16. **"Escape joins OpenAI's Trusted Access for Cyber (TAC)..."** — Alexandra Charikova, Aug 3, 2026 (4 min).
17. **"Whitebox pentesting is now available in Escape's AI Pentesting - Cascade"** — Alexandra Charikova, Jul 31, 2026 (3 min).
18. **"Escape Research team found a PII disclosure in Keycloak. It's now CVE-2026-17059."** — Enzo Mongin ("Orionexe"), Jul 31, 2026 (10 min). Broken object-level authorization (CWE-639, CVSS 6.5) in Keycloak's `GET /admin/realms/{realm}/roles/{role-name}/users` endpoint; responsibly disclosed Jul 18 → CVE published Jul 24 → fixed in Keycloak 26.7.0 by Jul 28 → publicly disclosed Jul 31, 2026.
19. **"Automated Penetration Testing: The Complete Guide in 2026"** — Sanjana Iyer, Jul 31, 2026 (14 min).
20. **"7 best continuous penetration testing tools in 2026"** — Sanjana Iyer, Jul 31, 2026 (21 min).
21. **"How Escape DAST helped Sigma Computing achieve complete GraphQL API endpoint coverage"** — Sanjana Iyer, Jul 30, 2026 (9 min). Case study.
22. **"Why does the rise of Agentic AI force security teams to become research-aware?"** — Arnaud Fanthomme, Jul 24, 2026 (8 min). References a Bruce Schneier quote.
23. **"AI pentesting, Mission log: July"** — Sanjana Iyer & Alexandra Charikova, Jul 24, 2026 (6 min). Product updates.
24. **"wp2shell (CVE-2026-63030 + CVE-2026-60137): WordPress pre-auth RCE, now detected by Escape"** — Alexandra Charikova, Jul 21, 2026 (7 min).

**Other notable, undated-on-crawl research referenced site-wide:** "Introducing Cascade: the multi-agent penetration testing that becomes an expert in your business" (byline Alexandra Charikova, Antoine Carossio, Hugo Pucéat; Jun 4, 2026, 15 min) — the deepest architecture write-up, including a real-world pricing-manipulation exploit case study and head-to-head benchmarks (see Platform architecture and table below); "Fortune 1000 at risk: How we discovered 100k vulnerabilities" (Alexandra Charikova, Maxence Lecanu, Quentin Lieumont, Gabriel Marquet; Nov 20, 2024); "Methodology: How we discovered over 2k high-impact vulnerabilities in apps built with vibe coding platforms" (Nohé Hinniger-Foray, Gwendal Mognier, Alexandra Charikova; Oct 29, 2025); "Modern AI-powered Pentesting Tools In-Depth Benchmark" (Cascade vs. Claude Opus 4.7/4.8, Aikido, Xbow, Shannon, Strix, PentAGI — referenced from the Research page, comparison table reproduced below); "Escape vs. Invicti" comparison (Alexandra Charikova, Jun 4, 2026, 18 min).

**Benchmark highlight (from the Cascade launch post) — OWASP Juice Shop:**

| | Cascade (black-box) | Cascade (white-box) | Claude Code/Opus (black-box, best) | Claude Code/Opus (white-box) |
|---|---|---|---|---|
| Total findings | 36 | 49 | 22 | 22 |
| High | 20 | 31 | 11 | 13 |
| Medium | 15 | 17 | 7 | 6 |
| Low | 1 | 1 | 4 | 3 |

Cascade also led an independent Doyensec comparative benchmark against Aikido, Xbow, and Claude Code on two real-world open-source apps (Fider, Photoview), topping all solutions on Photoview white-box (28 findings) and leading on Fider in both modes (20–27 findings).

**Named researchers:** Antoine Carossio (co-founder/CTO, prolific author), Alexandra Charikova (most prolific blog/case-study author), Sanjana Iyer, Gwendal Mognier, Geoffrey Diederichs, Yacine Souam, Enzo Mongin ("Orionexe" — CVE researcher), Arnaud Fanthomme, Hugo Pucéat, Nohé Hinniger-Foray, Maxence Lecanu, Quentin Lieumont, Gabriel Marquet, Mia Berthier, Harikiran Nannapaneni.

**External-only research/talks not found in the crawled pages:** "GraphQL Security Vulnerabilities in the Wild" talk at GraphQLConf 2023 (Kalos & Carossio, YouTube); Nordic APIs Platform Summit 2023 talk (Kalos); API World/CloudX/DataWeek 2025 speaking slot (Kalos). No confirmed DEF CON/Black Hat/BSides mainstage talk was found by either source.

---

## Leadership & team

| Name | Role | Background |
|---|---|---|
| Tristan Kalos | Co-founder & CEO | Ex-AI Researcher, UC Berkeley (site); externally: worked in SF on chatbots/APIs before founding Escape, motivated by a client database ransomware incident (~2017–2018) |
| Antoine Carossio | Co-founder & CTO | Ex-Security Engineer, Apple (site); externally: also a former penetration tester for the French Government; open-source GraphQL security maintainer |
| Mathieu Rousse | Head of Engineering | Ex Team Lead Engineering, Datadog (site only) |
| Yohan Testemale | Technical Account Manager | Named as an example employee (site only) |
| (Research team) | Security Researchers (Mid, Senior, Lead) | Job listings describe a Paris-based research team of at least ~3+ under a "Lead Security Researcher" role (external, job-board sourced) |

No additional named C-suite/VP hires were confirmed by either source beyond the two co-founders and Mathieu Rousse.

---

## News timeline

Reverse-chronological (dates as stated by each source; note the site's blog uses forward-dated 2026 timestamps at crawl time):

| Date | Event | Source |
|---|---|---|
| Sep 11, 2026 | Blog: "What an External Penetration Test is And How One is Actually Run" | escape.tech/blog |
| Sep 10, 2026 | Blog: "How to build a continuous pentesting program" | escape.tech/blog |
| Sep 9, 2026 | Case study: How Amp got SOC 2 Type II pentest evidence in hours | escape.tech/blog |
| Aug 26, 2026 | Blog: LLM/MCP security testing guide (OWASP LLM Top 10) | escape.tech/blog |
| Aug 21, 2026 | Research: Same stored-XSS found in two AI chatboxes' Markdown renderers | escape.tech/blog |
| Aug 20, 2026 | Comparison: "Horizon3.ai alternatives in 2026" | escape.tech/blog |
| Aug 20, 2026 | Announcement: Escape's Channel Partners program introduced | escape.tech/blog |
| Aug 19, 2026 | Comparison: "Escape vs Pentera" | escape.tech/blog |
| Aug 14, 2026 | Comparison: "Escape vs StackHawk" | escape.tech/blog |
| Aug 14, 2026 | Research: Cascade jailbreaks a production AI agent via semantic reframing | escape.tech/blog |
| Aug 12, 2026 | Blog: Authenticated scanning behind OAuth/MFA/CAPTCHA | escape.tech/blog |
| Aug 6, 2026 | Blog: PTaaS explained | escape.tech/blog |
| Aug 4, 2026 | Escape joins Anthropic's Cyber Verification Program | escape.tech/blog |
| Aug 3, 2026 | Escape joins OpenAI's Trusted Access for Cyber (TAC) | escape.tech/blog |
| Jul 31, 2026 | Product update: Whitebox pentesting added to Cascade | escape.tech/blog |
| Jul 31, 2026 | CVE-2026-17059 disclosed publicly (Keycloak PII disclosure, found by Escape Research) | escape.tech/blog |
| Jul 30, 2026 | Case study: Sigma Computing achieves full GraphQL endpoint coverage | escape.tech/blog |
| Jul 24, 2026 | Blog: Agentic AI forces security teams to become "research-aware" | escape.tech/blog |
| Jul 24, 2026 | Product update: "AI pentesting, Mission log: July" | escape.tech/blog |
| Jul 21, 2026 | Product update: wp2shell WordPress pre-auth RCE (CVE-2026-63030 / CVE-2026-60137) now detected | escape.tech/blog |
| Jul 18–28, 2026 | Keycloak CVE-2026-17059 disclosure timeline (report → CVE → fix) | escape.tech/blog |
| Jun 4, 2026 | "Introducing Cascade" architecture post + benchmarks published | escape.tech/blog |
| Jun 4, 2026 | "Escape vs. Invicti" detailed comparison published | escape.tech/blog |
| Mar 10, 2026 | $18M ($15.4M€) Series A announced, led by Balderton Capital | escape.tech/blog; Tech.eu; SecurityWeek; Balderton |
| Mar 2026 | Gide law firm announces it advised Escape on the Series A | Gide (external) |
| Oct 30, 2025 | Case study: Applied Systems — complex authentication challenges | escape.tech/blog |
| Oct 29, 2025 | Research: "State of Security of Vibe Coded Apps" methodology published (2,000+ vulns across 5,600 apps) | escape.tech/blog |
| Jul 2025 (approx.) | AI Pentesting agentic product effectively launched / Wiz "WIN" Partner Award won | Trend Hunter; Security Boulevard (external) |
| Jul 7, 2025 | Case study: AI-Driven Applications Security (feat. DoubleVerify) | escape.tech/blog |
| May 8, 2025 | Case study: Arkose Labs — deeper business logic testing | escape.tech/blog |
| Apr 25, 2025 | Case study: DoubleVerify — full API visibility via Wiz + Escape | escape.tech/blog |
| Nov 20, 2024 | Research: "Fortune 1000 at risk" — 30,784 exposed APIs, 107,368 vulnerabilities | escape.tech/blog; Help Net Security |
| Aug 2024 | Positioning piece: Escape vs. traffic-based API security tools | Security Boulevard (external) |
| Jul 4, 2024 | Case study: French Football Federation | escape.tech/blog |
| Jun 11, 2024 | Case study: Sungage Financial — GraphQL APIs secured in 1 week | escape.tech/blog |
| Feb 2024 | Research: "State of API Security 2024 — The API Secret Sprawl" | Help Net Security (external) |
| Nov 9, 2023 | Case study: Lightspeed — full compliance via GraphQL APIs | escape.tech/blog |
| Oct 5, 2023 | Case study: Shine (Société Générale) | escape.tech/blog; Security Boulevard |
| Oct 2, 2023 | Case study: Thinkific | escape.tech/blog |
| Nov 2023 | GraphQLConf 2023 talk: "GraphQL Security Vulnerabilities in the Wild" | GraphQL.org (external) |
| Jun 2023 | €3.6M ($3.9M) seed round announced, led by IRIS | EU-Startups (external) |
| Winter 2023 | Y Combinator W23 batch; Launch HN post | Hacker News; YC (external) |
| 2020 | Company founded in Paris | escape.tech/about; Nordic APIs (external) |

---

## Media inventory

Organized by page, as captured in the crawl. Escape's site relies heavily on Webflow-hosted CDN images (`cdn.prod.website-files.com`) for product screenshots/diagrams and a Ghost-hosted blog CDN (`escape.tech/blog/content/images/...`) for article art; no native video embeds were found anywhere on the crawled pages — video content is exclusively linked out to YouTube or a third-party webinar platform (getcontrast.io).

### Homepage (escape.tech)
- `hero-aesthetic.svg` — hero graphic
- `asm-escape.webp`, `business-logic-escape-dast.webp`, `ai-pentest2.webp`, `ships code image.webp`, `workflows-escape-dast.webp` — one product screenshot per core product (ASM, DAST, AI Pentesting, Remediation, Automation)
- `compliance-matrix (1).webp` — compliance framework matrix graphic
- `image 343.svg` — Trust Center badge
- Customer/partner logos: Visma, Health Equity, Applied, Miro, Schibsted, Cato Networks, Arkose Labs, DataVault (DV), PandaDoc, G2
- Linked (not embedded): The Elephant in AppSec Podcast — youtube.com/@the-elephant-in-appsec; "Escape Autonomous Pentesting Hype" webinar — watch.getcontrast.io/register/escape-autonomous-pentesting-hype

### About page (escape.tech/about)
- Escape team photo; leadership headshots (Kalos, Carossio, Rousse); various culture/capability imagery; partner/investor logos and advisor headshots (no distinct URLs captured by the crawl for this page specifically)

### Docs home (docs.escape.tech)
- `assets/hero.svg` — documentation hero illustration
- Inline SVG Escape logo mark; `assets/favicon.png`; social glyph icons (LinkedIn, X, Discord, GitHub)

### Product: ASM (escape.tech/product/attack-surface-management)
- `asm-escape.webp` — ASM workflow diagram
- `shadow-apis (1).webp` — shadow-APIs illustration
- `workflow-asm.webp` — automation workflow diagram
- Partner/customer logos: Cato Networks, Kubra, Schibsted, Sensgia, Applied, ControlUp, DoubleVerify, Arkose Labs, Wiz
- Linked webinar: watch.getcontrast.io/register/escape-autonomous-pentesting-hype

### Product: DAST (escape.tech/product/dast)
- `business-logic-escape-dast.webp`, `ships code image.webp`, `workflows-escape-dast.webp`, `auth-dast.webp`, `rbac-escape.webp`, `wiz-dast.webp` — one screenshot per feature area (business logic, remediation, workflows, auth, RBAC, Wiz integration)
- Testimonial headshots: Seth Kirschner, Michael Bourgault; customer logos: Health Equity, Schibsted, Miro, Applied, DoubleVerify (DV_BIG.svg)
- Linked: The Elephant in AppSec Podcast (YouTube); autonomous-pentesting-hype webinar

### Product: AI Pentesting (escape.tech/product/ai-pentesting)
- `pentesting-agents-escape.webp` — product/feature diagram
- `thumb-ai-pentesting.png` — og:image/social share thumbnail
- Partner/customer names referenced: Applied Systems, Health Equity, Schibsted, Miro, ControlUp, Visma

### Blog index (escape.tech/blog/)
- Logo: `White--1-.png`
- Per-article preview images (one per listed post, `.svg`/`.png`, pattern `/blog/content/images/size/w600/YYYY/MM/[slug]`)
- Author avatars for Antoine Carossio, Alexandra Charikova, Sanjana Iyer, Yacine Souam, Enzo Mongin, Arnaud Fanthomme

### "Introducing Cascade" post (Jun 4, 2026)
- `introducing-cascade-1.png` — hero/featured image (also og:image)
- `cascade-architecture-v3--1-.png` — Cascade architecture diagram
- `price-manip-screen.png` — screenshot of the pricing-manipulation exploit case study
- Two in-text benchmark charts (Juice Shop; Fider/Photoview vs. Aikido/Xbow/Claude Code) rendered as data tables/images, exact src not isolated by the crawl

### "Escape found the same XSS in two AI chatboxes" (Aug 21, 2026)
- `two-chatboxes-one-xss.png` — main header image (alt matches title)
- `stored-xss-screenshot--1-.png` — screenshot of the vulnerability reproduced in a customer environment

### "AI vs AI: How Cascade exploited an AI agent in production" (Aug 14, 2026)
- `ai-vs-ai-how-cascade-exploited-ai-agent.png` — hero image (og:image)
- `first_try.png` — screenshot of the first blocked attempt
- `cascade_thinking.png` — screenshot/diagram of Cascade's reasoning
- `cascade_leak_synthetic_system_prompt_full.png` — screenshot of the leaked synthetic system prompt

### Keycloak CVE post (Jul 31, 2026)
- `cve-2026-17059.png` — main article image (og:image)
- `cve-2026-17059-recap.png` — recap diagram
- `image-7.png` — platform screenshot of the detection in action

### "Escape vs Invicti" comparison (Jun 4, 2026)
- `one-scan-escape-info.png` — Escape's categorized findings screenshot
- `vuln-funnel.png` — vulnerability prioritization funnel diagram
- Multiple Invicti product screenshots (auth profile dropdown, GraphQL setup docs, Crawled URLs Report, risk scoring interface, remediation info, enterprise vuln details, API management setup)
- Video: Tella video thumbnail referred to as "Alex's video" — `tella.tv/api/stories/cm19k6ia1000703l5dz3takpt/thumb.gif`; two additional unresolved video labels ("Test scan configuration in Escape," "Example for SSRF vulnerability")

### "Fortune 1000 at risk" research post (Nov 20, 2024)
- `Report---Main-Visual.png` — main report visual (og:image)
- `Report---Infographic-State-of-API-exposure.png` — infographic
- `image.png` — architecture/process diagram
- 4 author headshots (Charikova, Lecanu, Lieumont, Marquet)

### Vibe-coding methodology post (Oct 29, 2025)
- `process-data-collection-escape.png` — data-collection process diagram
- `Screenshot-2025-10-29-at-13.40.56.png` — fingerprinting-method screenshot
- `typical-asm-scanner-structure.png` — typical ASM scanner structure diagram
- `lovable-supabase-integration-schema.png` — Lovable–Supabase integration schema
- `visage-surface-scanner.png` — Visage scanner architecture diagram
- `web-app-asm-scanner-with-lovable.png` — complete discovery schema diagram
- `scanned-assets.png` — scanned-assets breakdown chart

### Careers page (escape.tech/careers)
- `escape-team.webp` — team/office photo
- `How-Amp-got-its-SOC-2-Type-II-pentest-evidence-in-hours.webp`, `escape-pentesting-webinar.png` — featured content thumbnails
- Embedded Ashby job board (client-side rendered, listings not extractable via static fetch): jobs.ashbyhq.com/escape/embed
- Notes the site loads the Plyr.js video-player library, suggesting video content elsewhere on the site not captured by this crawl

### Research page (escape.tech/research)
- `escape_capacity_gap_diagram_light_beige.png` — "capacity gap" diagram/chart
- Multiple uncaptured research-article thumbnails
- Linked: autonomous-pentesting-hype webinar; The Elephant in AppSec podcast (YouTube)

---

## External perception

- **G2**: 5.0/5.0 rating. Reviewers cite strong GraphQL/business-logic detection, efficient and accurate vulnerability detection, good UI/filtering; noted weaknesses include remediation guidance and documentation could be more detailed — a mild tension with Escape's own marketing claim of best-in-class remediation guidance.
- **AppSecSanta** (independent AppSec review site, 2026): positions Escape as "the right pick for teams building API-first applications, especially GraphQL," citing 140+ tests (note: the site itself says "100+ GraphQL-specific tests" — see Contradictions) and BOLA/IDOR detection as a genuine differentiator. Notes pricing is not public and that Escape is less suited to traditional server-rendered web apps. Lists Invicti, Bright Security, StackHawk, Burp Suite Professional, and Akto as alternatives.
- **Gartner**: General "Market Guide for API Protection" commentary on shadow/dormant API risk exists, but no confirmed named inclusion or rating of Escape in a Gartner report was located by external research.
- **AWS Marketplace reviews**: a dedicated reviews page exists for "Escape Attack Surface Management," indicating real customer usage, though specific quotes were not extracted.
- **Community/HN sentiment**: the 2023 Launch HN thread ("Escape (YC W23) – Discover and secure all your APIs") is the clearest community discussion found; no significant independent Reddit discussion was found.
- **Industry recognition**: Wiz's inaugural WIN (Wiz Integrations) Partner Award, 2025, for the Escape⇄Wiz integration (external-sourced; not mentioned on the crawled pages, though the Wiz integration itself is referenced repeatedly on-site).
- **Competitive comparisons (third-party framing)**: an independent market-map newsletter (Cyberflow) characterizes Escape as covering "APIs but at scanner grade, without PoC exploitation depth," contrasting it with FireCompass's Continuous Automated Red Teaming (CART) approach. CB Insights maintains a head-to-head "Escape vs. Traceable AI" comparison page, indicating analysts also treat Traceable as a peer competitor. Escape's own content positions it as "the strongest XBOW alternative in 2026" for continuous, engineering-led AI pentesting (echoed by Security Boulevard).

---

## Strengths & weaknesses (as a competitor)

**Strengths**
- Deep, differentiated technical moat in GraphQL and business-logic/authorization testing (BOLA/IDOR), an area competitors (Invicti, traditional DAST) explicitly and repeatedly (per Escape's own comparison content and G2 reviews) underserve.
- Cascade's multi-agent architecture is unusually well-documented for the category (orchestrator/coverage/exploitation/reporter roles, shared message bus, independent verification step) and is backed by transparent, apples-to-apples-ish benchmarking against a raw frontier model (Claude Code/Opus) and named competitors (Aikido, Xbow) on public benchmark targets.
- Strong compounding product design: proven findings automatically become permanent CI/CD regression tests, tying DAST and AI Pentesting together rather than selling them as siloed one-off products.
- Legitimate, in-house security research output (published CVEs, adversarial AI-agent research, large-scale internet-exposure studies) that functions as both credibility-building marketing and genuine threat intelligence — a flywheel smaller competitors struggle to match.
- Credible investor/advisor bench (Balderton, YC, Datadog's Olivier Pomel, Tenable's Renaud Deraison, Qualys's Philippe Langlois) lending industry credibility beyond typical seed/Series-A-stage security startups.
- Broad, named enterprise-relevant customer base (Visma, DoubleVerify, Applied Systems, Sigma Computing, Société Générale subsidiary) with specific, quantified testimonials rather than generic logos.
- Genuinely agentless, low-friction deployment model (add a domain, no proxy/agent) that lowers adoption friction versus traffic-monitoring-based API security tools.

**Weaknesses / risk factors**
- No public pricing anywhere — a real friction point for smaller prospects and for competitive positioning against vendors with transparent tiers.
- Small team (~29 employees per YC, external estimate) relative to the breadth of the platform being marketed (4 products + research team) — execution risk on so many fronts at once.
- Heavy reliance on Escape's own benchmarks and blog for competitive comparisons (vs. Invicti, StackHawk, Pentera, Horizon3.ai, XBOW); while methodologically detailed, these are vendor-authored and not independently audited except for the Doyensec-sourced Fider/Photoview comparison.
- G2 reviewers flag remediation guidance and documentation quality as weaker points, directly cutting against the marketed strength of "ready-to-merge remediation."
- No confirmed valuation or major analyst-firm (Gartner/Forrester) named ranking, versus larger incumbents like Invicti (now a full ASPM platform after acquiring Kondukto) that bundle DAST+SAST+SCA+container+IaC+secrets scanning — Escape is comparatively narrow in scope (offensive/dynamic testing only), which could be a gap against enterprise buyers wanting a single consolidated platform.
- Heavy narrative dependence on "vibe coding" and AI-agent-security research trend pieces — good marketing hooks, but this is adjacent to, not squarely inside, Escape's core paid product value proposition, and could read as thought-leadership padding rather than product substance to a skeptical buyer.

---

## Open questions / unverified items

- **Exact current headcount** — no single authoritative source; YC's ~29 figure is dated and LinkedIn/ZoomInfo signals are noisy due to unrelated same-named companies.
- **Valuation** — not disclosed in any source found (seed or Series A).
- **Exact list pricing / cost per seat or per asset** — entirely unconfirmed beyond AWS Marketplace capacity tiers (15/60/120 apps) and a reported single-API free tier.
- **AI Pentesting/Cascade launch date** — the crawled site's detailed architecture post is dated June 4, 2026, but external sources describe an "AI Pentesting" launch around July 2025; it's unclear whether Cascade is a rename/major-rebuild of an earlier July-2025 AI-pentesting product or a wholly new June-2026 release. Treat as `unverified` which is authoritative.
- **CVE-2026-17059 exact disclosure page URL** — external research flagged this as "identified via search, page not fetched"; the crawled first-party page fills this gap with full technical detail, so this item is now resolved by the site crawl (see Research & News timeline above), but the fact that external OSINT could not independently corroborate the technical narrative is worth noting for anyone relying on external sources alone.
- **Whether "Sherpa by Escape Technology"** (an AWS Marketplace listing name found by external research) is a current, retired, or renamed product — not mentioned anywhere in the crawled site content.
- **DEF CON / Black Hat / BSides mainstage presence** — no confirmed talk found by either source; treat absence as evidence of a gap in the company's conference visibility, not confirmed non-attendance.
- **Formal analyst coverage** — no confirmed Gartner/Forrester named inclusion or ranking found by either source.
- **"Two continents, one team" (Europe + US)** — the About page states this culture pillar and the Research page lists a New York office alongside Paris, but no external source corroborates a US office, headcount split, or when it was established.

---

## Contradictions between first-party and external sources (flagged)

1. **GraphQL Armor weekly downloads**: Escape's own Research page states **267,101** weekly downloads; an external review (AppSecSanta) cites **100,000+**. These may reflect different snapshot dates (npm download counts fluctuate significantly week to week) rather than a factual conflict, but the magnitude gap (2.5x+) is worth flagging rather than silently reconciling.
2. **GraphQL-specific test count**: Escape's own "Escape vs Invicti" comparison post states "**over 100 GraphQL-specific tests**"; the external AppSecSanta review states "**140+ automated attack scenarios**." Could refer to different scopes (GraphQL-only tests vs. total attack scenarios across the platform) rather than a true contradiction, but the site itself does not use the "140+" figure anywhere in the crawled pages.
3. **Fortune 1000 research headline numbers**: the crawled first-party blog post ("Fortune 1000 at risk") states **30,784 exposed APIs** and **107,368 vulnerabilities** (2,038 highly critical) across Fortune 1000 **and CAC 40** combined, with Fortune-1000-only figures of "over 28,000 exposed APIs" and "1,830 highly critical." The external research profile's Fortune-1000-specific figures (28,500+ exposed APIs; 98,800 vulnerabilities; 1,830 highly critical) are close but not identical (28,500 vs. "over 28,000"; 98,800 vs. an unstated Fortune-1000-only total vulnerability figure in the first-party post). This is very likely due to the external source citing secondary press coverage (Help Net Security) that itself may have rounded or recombined the Fortune-1000-vs-CAC-40 breakdown differently — worth using the first-party post as the source of record.
4. **Vibe-coded-apps research scale**: the first-party methodology post (Oct 29, 2025) states the study scanned **14,600 assets** (5,600 web apps) and found "**2,038 highly critical vulnerabilities and 400+ leaked secrets... across 1.4K vibe-coded applications**" per the report landing page, while the headline figure repeated elsewhere on-site and in external press (Tech.eu, the Series A blog post) is "**2,000+ vulnerabilities across 5,600 apps**." The "1.4K" vs. "5,600" application count is an internal inconsistency across Escape's own pages (report-teaser page vs. methodology page vs. Series A announcement page) — likely "1.4K" refers to a subset with the most severe/PII-exposing findings while "5,600" is the full scanned corpus, but the site does not clarify this itself.
5. **Customer company name for Seth Kirschner**: the DAST and ASM product pages both attribute a Seth Kirschner testimonial to **DoubleVerify** ("Sr. AppSec Manager, DoubleVerify"), consistent with the dedicated DoubleVerify case study; however, the homepage attributes a Seth Kirschner quote to **"Sr. AppSec Manager, DataVault"** instead. This looks like an internal site error (same name, two different company attributions) rather than two different people, but it is flagged here rather than silently corrected.
6. **AI Pentesting benchmark model version**: the Research page states Cascade was benchmarked against "**Claude Opus 4.8**," while the "Introducing Cascade" architecture post (nominally the primary source for the same benchmark) states the comparison baseline was "**Claude Code (running Opus 4.7)**." Both are first-party pages, so this is an internal (not first-party-vs-external) inconsistency — possibly the Research page reflects a later benchmark re-run.

---

## Full source list

### First-party (crawled, escape.tech / docs.escape.tech) — 20 pages
- https://escape.tech
- https://escape.tech/about
- https://escape.tech/pricing
- https://escape.tech/careers
- https://escape.tech/research
- https://escape.tech/state-of-security-of-vibe-coded-apps
- https://escape.tech/product/ai-pentesting
- https://escape.tech/product/attack-surface-management
- https://escape.tech/product/dast
- https://escape.tech/blog/
- https://escape.tech/blog/tag/case-study/
- https://escape.tech/blog/escape-found-the-same-vulnerability-in-two-ai-chatboxes/
- https://escape.tech/blog/escape-raises-18m-series-a/
- https://escape.tech/blog/escape-research-pii-disclosure-keycloak-cve-2026-17059/
- https://escape.tech/blog/escape-vs-invicti/
- https://escape.tech/blog/fortune-1000-at-risk-30k-exposed-apis-100k-vulnerabilities/
- https://escape.tech/blog/how-cascade-exploited-an-ai-agent-in-production/
- https://escape.tech/blog/introducing-cascade-the-multi-agent-penetration-testing/
- https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/
- https://docs.escape.tech/

### External sources
- https://tech.eu/2026/03/10/escape-secures-18m-series-a-to-develop-ai-cybersecurity-agents/
- https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/
- https://fintech.global/2026/03/10/escape-raises-18m-series-a-for-ai-offensive-security/
- https://siliconangle.com/2026/03/10/escape-raises-18m-expand-ai-agent-platform-offensive-security-testing/
- https://securityboulevard.com/2026/03/escape-raises-18m-series-a-to-replace-legacy-scanners-with-ai-agent-driven-discovery-pentesting-and-remediation/
- https://www.crunchbase.com/organization/escape-b74e
- https://www.crunchbase.com/organization/escape-technologies
- https://www.crunchbase.com/organization/escape-tech
- https://www.crunchbase.com/person/tristan-kalos
- https://startupintros.com/orgs/escape
- https://www.iris.vc/articles/escape-raises-eu3-6m-in-seed-to-secure-apis-at-every-development-stage
- https://www.iris.vc/articles/escape-raises-18m-series-a-to-fight-ai-powered-cyberattacks-with-ai-agents
- https://www.eu-startups.com/2023/06/fresh-out-of-y-combinator-paris-based-escape-raises-e3-6-million-in-seed-to-secure-apis-at-every-development-stage/
- https://www.eu-startups.com/2026/03/yc-backed-escape-raises-e15-4m-series-a-led-by-balderton-for-its-ai-powered-offensive-security-engineering-platform/
- https://bebeez.eu/2026/03/10/yc-backed-escape-raises-e15-4m-series-a-led-by-balderton-for-its-ai-offensive-security-engineering-platform/
- https://www.balderton.com/news/escape-raises-18m-series-a-to-fight-ai-powered-cyberattacks-with-ai-agents/
- https://www.gide.com/en/news-insights/gide-advises-escape-on-its-18-million-series-a-funding-round-led-by-balderton/
- https://www.scworld.com/brief/escape-technologies-raises-18-million-for-ai-powered-security-platform
- https://www.thesaasnews.com/news/escape-raises-18-million-in-series-a/
- https://pitchbook.com/profiles/company/442610-29
- https://www.cbinsights.com/company/escape
- https://www.cbinsights.com/compare/escape-vs-traceable
- https://www.ycombinator.com/companies/escape
- https://www.ycombinator.com/launches/I4v-escape-secure-your-graphql-apis
- https://news.ycombinator.com/item?id=39215779
- https://appsecsanta.com/escape
- https://www.g2.com/products/escape/reviews
- https://aws.amazon.com/marketplace/pp/prodview-yffo3s4uoj7zs
- https://aws.amazon.com/marketplace/pp/prodview-b5zhismdnjnpw
- https://aws.amazon.com/marketplace/pp/prodview-botb7xtpafuxe
- https://aws.amazon.com/marketplace/pp/prodview-2dwmxwuc3bf5g
- https://aws.amazon.com/marketplace/reviews/reviews-list/prodview-botb7xtpafuxe
- https://securityboulevard.com/2023/10/case-study-how-escape-enhanced-shines-application-security/
- https://securityboulevard.com/2024/08/reinventing-api-security-why-escape-is-better-than-traditional-traffic-based-tools/
- https://securityboulevard.com/2025/07/escape-honored-with-inaugural-wiz-integrations-win-partner-award/
- https://securityboulevard.com/2026/04/top-xbow-alternatives-in-2026/
- https://www.wiz.io/blog/celebrating-200-wiz-integrations
- https://www.helpnetsecurity.com/2024/02/05/exposed-api-secrets/
- https://www.helpnetsecurity.com/2024/12/12/exposed-apis-issues-video/
- https://mexicobusiness.news/cybersecurity/news/unregulated-industries-leave-sensitive-data-exposed-apis
- https://cyberflow.substack.com/p/offensive-security-market-map-the-rise-of-autonomous-hacking
- https://firecompass.com/external-attack-surface-management/
- https://firecompass.com/attack-surface-management/
- https://www.gartner.com/reviews/market/api-protection
- https://graphql.org/conf/2023/sessions/5bf24cd6483a63e62a2276fe38effb82/
- https://graphql.org/conf/2023/speakers/tristan119/
- https://graphql.org/conf/2023/speakers/antoine.carossio
- https://www.youtube.com/watch?v=hyB2UKsEkqA
- https://www.youtube.com/@escapetechhq
- https://www.youtube.com/@escape-tech
- https://nordicapis.com/speakers/tristan-kalos/
- https://sessionize.com/antoine-carossio/
- https://apiworldcloudxdataweek2025.sched.com/speaker/tristan_kalos.28elzft0
- https://startupsavant.com/startup-savant-podcast/episodes/escape
- https://scalingdevtools.com/podcast/episodes/from-getting-hacked-to-cybersecurity-founders-with-antoine-carossio-and-tristan-kalos-from-escape-tech/transcript
- https://www.trendhunter.com/trends/escape-ai-agents
- https://github.com/Escape-Technologies
- https://github.com/Escape-Technologies/graphql-armor
- https://github.com/Escape-Technologies/graphinder
- https://github.com/Escape-Technologies/goctopus
- https://github.com/Escape-Technologies/awesome-graphql-security
- https://github.com/Escape-Technologies/graphql-security-academy
- https://www.linkedin.com/posts/acarossio_graphql-fieldsuggestion-clairvoyance-activity-7056959872495468544-2cfo
- https://www.linkedin.com/posts/escapetech_dynamic-graphql-api-security-testing-for-activity-7026213139356475392-9oI6
- https://x.com/escapetechHQ
- https://www.welcometothejungle.com/fr/companies/escape/jobs/senior-security-researcher_paris
- https://www.welcometothejungle.com/fr/companies/escape/jobs/security-researcher-mid-level_paris
- https://www.welcometothejungle.com/fr/companies/escape/jobs/lead-security-researcher-ai-appsec_paris
- https://www.welcometothejungle.com/fr/companies/escape/jobs/offensive-security-lead_paris
- https://jobs.stationf.co/companies/escape-technologies-sas
- https://jobs.ashbyhq.com/escape
- https://www.ycombinator.com/companies/escape/jobs/TEjc3IT-senior-front-end-engineer-ai-security-paris
- https://www.ycombinator.com/companies/escape/jobs/wcJZFqw-security-researcher-mid-level-paris-office
- https://www.ycombinator.com/companies/escape/jobs/XIiBxli-ai-engineer-security-research
