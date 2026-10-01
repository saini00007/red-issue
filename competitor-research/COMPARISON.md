# XBOW vs. FireCompass vs. Escape — Cross-Company Comparison

*Compiled September 26, 2026, from the three companion dossiers in this folder (`xbow/dossier.md`, `firecompass/dossier.md`, `escape/dossier.md`), which themselves reconcile each company's own site content against independent OSINT (funding databases, news, review sites, academic papers). Figures below carry forward each dossier's own sourcing and caveats — self-reported vendor claims are marked as such.*

## Executive summary

XBOW, FireCompass, and Escape are three venture-backed startups selling AI agents that autonomously find and — their common core claim — *prove* exploitable vulnerabilities, positioning themselves as the successor to point-in-time manual pentesting and to legacy DAST/vulnerability-scanner tooling. All three share the same rhetorical spine: agentic (not single-prompt) architectures, multi-stage validation/proof steps to suppress false positives, exploit chaining across findings, and continuous/CI-integrated delivery rather than an annual engagement. Beyond that shared category, they differ sharply in scope, scale, and go-to-market: **XBOW** is the best-capitalized and most enterprise-scaled of the three (~$270M raised, $1B+ valuation, 100+ customers, marquee investors NVIDIA/Samsung/Accenture/SentinelOne), focused tightly on web-application and API exploitation with the deepest public proof of real-world impact (Microsoft/Bing/Exim CVEs, a $250K Chrome bounty, #1 HackerOne US ranking). **FireCompass** is the broadest single platform — attack-surface discovery plus web/API/**network** pentesting plus red-team-style lateral-movement chaining in one SKU — but is a fraction of XBOW's size (~$30M raised) and leans hardest into self-reported, occasionally internally-inconsistent marketing numbers with the thinnest independent review base of the three. **Escape** is the smallest and most specialized (~$23-24M raised, ~29 employees), built from a GraphQL/API-security DAST heritage into a genuine technical differentiator in **business-logic and authorization testing (BOLA/IDOR)** that generalist scanners and even XBOW/FireCompass's broader platforms don't foreground as sharply, and is the only one of the three with a transparent, third-party-adjacent (Doyensec) head-to-head benchmark against named rivals. The category as a whole is young, well-funded, and still short on truly independent (non-vendor-sourced) validation — a theme that recurs across all three dossiers.

## Feature-by-feature comparison matrix

| Capability | XBOW | FireCompass | Escape |
|---|---|---|---|
| Autonomous AI exploitation (not just detection) | ✅ Five-stage Learn→Map→Coordinate→Attack→Prove pipeline; "thousands of agents" attack in parallel [^x1] | ✅ "No exploit, no alert" gating; live exploit execution, not simulation [^f1] | ✅ Cascade multi-agent engine (orchestrator/coverage/exploitation/reporter roles) [^e1] |
| Exploit validation / proof-of-exploit | ✅ Independent "validator" agents (LLM + programmatic checks, e.g. headless-browser XSS confirmation) [^x1] | ✅ Four-stage validation pipeline (hypothesis→live execution→signature evaluation→evidence); claims <2% false positives [^f2] | ✅ Independent "Reporter" agent re-reproduces every finding before filing; ≤4% false-positive rate on DAST [^e2] |
| Multi-step exploit/attack-path chaining | ✅ Chains discrete bugs into full attack paths (e.g. Moderna: API key→SQLi→IDOR in <18h) [^x2] | ✅ Credential reuse, app-to-app, app-to-network **and app-to-identity/AD** lateral movement; MITRE ATT&CK-aligned graph [^f3] | ✅ Business-logic/authorization chains (multi-identity sessions), findings compound into CI regression tests [^e3] |
| Attack-surface discovery / EASM | ⚠️ Newest capability (Autonomous Exposure Management, announced Sept 2026); not yet the core product [^x3] | ✅ Core, mature capability ("NextGen EASM"); passive+active recon, ~20%→99% surface visibility claim [^f4] | ✅ Agentless API/SPA/AI-app discovery incl. shadow APIs; "30% more assets" claim [^e4] |
| Web-app pentesting | ✅ Core, most-proven capability | ✅ Core capability | ✅ Core capability (via DAST + Cascade) |
| API security testing (REST/GraphQL) | ⚠️ API layer exists (REST API to trigger/retrieve assessments) but not a distinct GraphQL specialism [^x4] | ✅ Named capability, part of unified platform | ✅ **Deepest specialism**: 100+ GraphQL-specific tests, native GraphQL handling, originating product line [^e5] |
| Network / infrastructure pentesting | ❌ Not offered — web apps and APIs only, no stated network/AD testing [^x5] | ✅ Explicit product line (Infrastructure PT Agent); differentiator vs. XBOW [^f5] | ✅ "External Network Pentesting" product (hosts/ports/services) [^e6] |
| Business-logic / authorization (BOLA/IDOR) testing | ⚠️ Chains include IDOR examples but not marketed as a distinct methodology | ⚠️ "Business-logic abuse" named as covered, not a headline specialism | ✅ **Flagship differentiator** — proprietary BLST algorithm, multi-user/role-based testing built specifically for this [^e5] |
| Native-code / memory-safety vulnerability research | ⚠️ Emerging R&D track ("XBOW Native"); company's own post says LLMs "not quite ready" for hardened real-world targets [^x6] | ❓ Not described | ❓ Not described |
| Continuous / scheduled / CI-CD-triggered testing | ✅ Via API, webhooks, scheduler | ✅ Weekly/on-demand/CI-aligned cadence; Day-1 CVE validation | ✅ Incremental PR-triggered scans; native CI integrations (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket, CircleCI) |
| Reporting format / evidence | ✅ Full "case file": attack path, working exploit, decision log, remediation guidance | ✅ Reproduction steps, request/response pairs, ready-to-run Python PoC, audit trail | ✅ Request sequence, user scopes, working exploit, full reasoning logs, framework-specific fixes |
| CI/CD & ecosystem integrations | ✅ Jira, Microsoft Security Copilot/Sentinel, webhooks, AWS/Google/Oracle/Microsoft marketplaces | ⚠️ Fewer named integrations; no confirmed cloud-marketplace listing found independently [^f6] | ✅ Wiz (CNAPP), AWS Marketplace, GitHub/GitLab/Jenkins/Azure DevOps/Bitbucket/CircleCI, Jira, MCP interface |
| Compliance-framework mapping | ✅ "40+ frameworks"; SOC 2, ISO 27001, ISO 42001, HIPAA, GDPR, PCI DSS, NIS 2 badges | ✅ PCI DSS 4.0, SOC 2 Type II, DORA, ISO 27001 (AEV); PCI DSS/ISO 27001/OSFI/FISMA/HIPAA (EASM) | ✅ 20+ frameworks incl. PCI-DSS, HIPAA, CRA, SOC 2, ISO 27001 |
| Human-in-the-loop / hybrid options | ⚠️ Governance/audit logging, but positioned as fully autonomous; own research shows autonomous agent losing to human researcher on hardened target [^x6] | ✅ Explicit PTaaS line keeps human researchers in loop for compliance-grade attestation; optional human-in-the-loop mode | ✅ Optional human-in-the-loop mode; white-box (source-assisted) and black-box modes both offered |
| Deployment model | ✅ Managed SaaS (console + API); multi-region (US/EU/Singapore) for data residency | ✅ Agentless SaaS (minutes) or internal appliance (<1 hour) | ✅ Agentless SaaS only (add a domain to scope; no proxy/appliance) |
| Self-serve / freemium entry tier | ✅ "Pentest On-Demand," fixed-price, self-serve (Nov 2025) | ✅ "Explorer" credit-metered freemium tier (4,000 credits/yr) | ⚠️ Free tier reported only by an independent review (AppSecSanta, single-API scan); not confirmed on Escape's own site [^e7] |
| Public pricing transparency | ❌ Enterprise: none; self-serve tiers only via inconsistent 3rd-party trackers ($4K–$8K/test) | ❌ No price list; internally inconsistent credit/dollar figures on own site | ❌ No public pricing; only AWS Marketplace tier sizes (15/60/120 apps) known externally |
| Public benchmark / leaderboard proof | ✅ HackerOne #1 US (contested by critics as reputation artifact); MSRC #1 autonomous; XBOW's own 104-task benchmark now self-disclaimed as outdated [^x7] | ✅ 100/104 (96.15%) XBEN, 12/12 Acuart, full DVWA — all self-reported; HackerOne top-3 (Apr–Jul 2026) | ✅ Cascade benchmarks vs. Claude Code/Opus, Aikido, XBOW on Juice Shop/Fider/Photoview; partially corroborated by independent Doyensec test [^e8] |
| Independent / academic corroboration | ⚠️ Third-party arXiv papers (MAPTA, "Baselines Before Architecture") replicate XBOW's own benchmark, with mixed implications for its moat | ❓ None found — no academic paper or neutral teardown | ⚠️ Doyensec-run comparison exists but methodology/independence not fully verified in dossier |
| CVEs credited to company research | ✅ Multiple: Microsoft (CVSS 9.8), Bing (x2), Exim (CVE-2026-45185); $250K Chrome bounty | ❌ None found — publishes CVE roundups/commentary only, not original discoveries | ✅ Keycloak PII disclosure (CVE-2026-17059); WordPress pre-auth RCE detection (CVE-2026-63030/60137) |
| Total funding raised | ~$237–270M | ~$30–30.5M | ~$23–24M |
| Review-site presence | ❓ No G2/PeerSpot/Capterra pages found | ⚠️ Thin — only 3 G2 reviews | ✅ 5.0/5.0 on G2 (small sample, strongest rating of the three) |

[^x1]: xbow.com/platform — Learn/Map/Coordinate/Attack/Prove pipeline, validator agents.
[^x2]: xbow.com/customer-stories/moderna.
[^x3]: xbow.com/blog "Introducing Autonomous Exposure Management," Sept 24, 2026.
[^x4]: xbow.com/api.
[^x5]: FireCompass comparison content, cited in xbow dossier weaknesses section.
[^x6]: xbow.com/blog/dead-letter-cve-2026-45185-xbow-found-rce-exim.
[^x7]: xbow.com/blog/top-1-how-xbow-did-it; xbow.com/blog/benchmarks (editor's-note disclaimer).
[^f1]: firecompass.com/ai-agent-web-application-pen-test/.
[^f2]: firecompass.com/adversarial-exposure-validation-aev/.
[^f3]: firecompass.com homepage; firecompass.com/firecompass-agentic-ai-platform/.
[^f4]: firecompass.com/external-attack-surface-management/.
[^f5]: firecompass.com/firecompass-agentic-ai-platform/ (Infra PT Agent, Enterprise Pilot tier).
[^f6]: FireCompass dossier, Customers/Partners section — "no standalone AWS/Azure/GCP marketplace listing found."
[^e1]: escape.tech/blog/introducing-cascade, June 4 2026.
[^e2]: escape.tech/product/dast.
[^e3]: escape.tech/product/ai-pentesting.
[^e4]: escape.tech/product/attack-surface-management.
[^e5]: escape.tech/product/dast — BLST algorithm, GraphQL-native testing.
[^e6]: escape.tech (External Network Pentesting product page).
[^e7]: AppSecSanta independent review, cited in Escape dossier Pricing section.
[^e8]: escape.tech/blog/introducing-cascade — Juice Shop table and Doyensec-referenced Fider/Photoview results.

## Positioning & target customer comparison

- **XBOW** pitches itself as the enterprise-grade, "proof not noise" replacement/supplement for manual pentesting at large, security-mature organizations — its case studies (Moderna, Seznam, Superhuman, a top-5 US bank) and channel partners (Accenture Cyber.AI, AWS/Azure/Google/Oracle marketplaces, Samsung Korea reseller) target big-enterprise buyers already running formal AppSec/SecOps programs, with a self-serve on-ramp (Pentest On-Demand) added later to reach smaller teams. Its newest move (Autonomous Exposure Management) signals ambition to own whole-portfolio, credential-less exposure management at enterprise scale — directly encroaching on FireCompass's traditional territory.
- **FireCompass** pitches breadth and cost-replacement: "one platform" spanning discovery, web/API/network pentesting, and red-team-style chaining, aimed at budget-holders who want to retire multiple point tools (DAST + ASM + BAS + manual red team) and multiple annual vendor contracts at once. Its comparison content and pricing framing (cost-per-app vs. manual pentest, vs. DAST) is explicitly built for a CISO/procurement audience doing vendor consolidation math, and its EC-Council partnership (a certification/training body) suggests a GTM motion reaching mid-market and channel-resold accounts, not just top-tier enterprise.
- **Escape** pitches deep specialization for API-first, engineering-led organizations — teams shipping GraphQL/REST APIs fast (SaaS, fintech, ad-tech) who need business-logic and authorization testing that generalist DAST and broader "exposure management" platforms underserve. Its "offensive security for the teams that are 100x outnumbered" framing and lightweight, agentless, CI/PR-triggered deployment target engineering-embedded AppSec practitioners at growth-stage companies rather than large, process-heavy enterprise security organizations — though its investor bench (Datadog, Tenable, Qualys founders) and named customers (Visma, Société Générale subsidiary, DoubleVerify) show it can and does land larger accounts.

## Funding & scale comparison

| Company | Founded | Total funding | Key investors | Headcount | Headline metric |
|---|---|---|---|---|---|
| XBOW | Jan 2024 (site JSON-LD elsewhere says 2023 — unresolved) | ~$237M (as of Series C) to ~$270M incl. extension; $1B+ valuation (Mar 2026) | Sequoia Capital, Altimeter Capital, DFJ Growth, Northzone, NVIDIA (NVentures), Samsung Ventures, Accenture Ventures, SentinelOne S Ventures | ~250–300 (external estimates; not disclosed by XBOW) | #1 on HackerOne's US leaderboard (June 2025); 100–150+ customers |
| FireCompass | 2019 | ~$30–30.5M | NetApp Excellerator (seed), Cervin Ventures & Athera Venture Partners (Series A), EC-Council ($20M+ corporate/venture round, Sep 2025) | Conflicting estimates: 11–50 (LinkedIn) to 87–92 (Tracxn) to 51–200 (Wellfound) | 104/104 on XBEN benchmark; top-3 HackerOne US leaderboard (self-reported) |
| Escape | 2020 | ~$23–24M | IRIS (seed), Balderton Capital (Series A, lead), Y Combinator; advisors incl. Datadog's Olivier Pomel, Tenable's Renaud Deraison | ~29 (Y Combinator company page, 2026) | 2,000+ security teams using the platform; 5.0/5.0 G2 rating |

XBOW is roughly **9–11x** better capitalized than FireCompass and Escape combined, and has scaled headcount to an order of magnitude larger than Escape's ~29-person team, despite being the youngest of the three companies by founding date (2024 vs. 2019 and 2020).

## Research & credibility comparison

| Signal | XBOW | FireCompass | Escape |
|---|---|---|---|
| Public benchmark disclosure | Yes — but company itself now disclaims its original 75%/85% benchmark numbers as "outdated" | Yes — 100/104 XBEN, 12/12 Acuart, full DVWA, all self-reported | Yes — Juice Shop + Doyensec-referenced Fider/Photoview vs. named rivals (Claude Code/Opus, Aikido, XBOW) |
| Real-world CVE credits | Strongest of the three: Microsoft CVSS 9.8, two Bing RCEs, Exim unauthenticated RCE, $250K Google Chrome full-chain bounty | None found — publishes CVE *roundups*, not its own discoveries | Keycloak PII-disclosure CVE (CVE-2026-17059); credited detection of WordPress pre-auth RCE CVEs |
| Bug-bounty leaderboard result | #1 US HackerOne leaderboard (June 2025) — contested by independent researchers (Utku Şen, Rawsec, Hacker News) as a volume/reputation artifact, not proof of novel bug-hunting skill | Top-3 US HackerOne leaderboard (Apr–Jul 2026 live experiment) — reported by FireCompass itself; external figures on acceptance rate (12.7%) and duplicate rate (38.7%) are less flattering than the ranking alone suggests | Not applicable — Escape does not run a public bug-bounty leaderboard experiment |
| Independent academic engagement | Two independent arXiv papers use XBOW's own public benchmark; one finds a generic coding agent solves a comparable share of tasks (70–81/104), casting some doubt on XBOW's proprietary-orchestration moat | None found | Doyensec-run comparative benchmark is the closest of the three to a neutral third-party validation, though methodology/independence isn't fully documented |
| Analyst-firm coverage | Informal only — practitioner mentions at a Gartner summit; no formal Gartner/Forrester report found | Most extensive claimed analyst footprint ("30+ recognitions": Forrester, IDC, GigaOm Radar Leader) — but the aggregate "30+" figure is itself self-reported and not independently retrievable | None confirmed — no named Gartner/Forrester inclusion found |
| Own candor about limitations | Notably high — company's own blog post concedes its fully autonomous agent lost to a human researcher on a hardened, realistic target ("I don't think LLMs alone are quite ready...") | Low — marketing is uniformly upbeat; site shows internal inconsistencies (false-positive rate, Hype Cycle counts) rather than self-critique | Moderate — G2 reviewers (not the company) flag remediation-guidance/documentation gaps that cut against Escape's own "best-in-class remediation" claim |
| Independent critique volume | Highest — multiple named critics (Utku Şen, Rawsec, viehgroup.com, Hacker News threads) directly challenge the HackerOne-ranking narrative | Moderate — mostly aggregator-level "occasional false positives" complaints; no single high-profile critical piece found | Lowest — G2 is broadly positive (5.0/5.0); no dedicated critical piece found in either dossier |

## Numbers at a glance

| Metric | XBOW | FireCompass | Escape |
|---|---|---|---|
| Founded | Jan 2024 | 2019 | 2020 |
| Total funding | ~$237–270M | ~$30–30.5M | ~$23–24M |
| Valuation | $1B+ (Mar 2026, external only) | Not disclosed | Not disclosed |
| Headcount | ~250–300 (external est.) | 11–200 (conflicting est.) | ~29 |
| Customers / users | "150+ security teams" / "100+ customers" (conflicting) | Anonymized case studies only; no total disclosed | 2,000+ security teams |
| False-positive rate claim | Near-zero via validator agents (no single % stated) | <2% | ≤4% (DAST) |
| Public benchmark headline | HackerOne #1 US (Jun 2025); own 104-task benchmark now disclaimed | 100/104 (96.15%) XBEN; 104/104 with retries | Cascade beat Claude Code/Opus 36 vs. 22 findings (Juice Shop, black-box) |
| CVEs credited | Microsoft (CVSS 9.8), 2x Bing, Exim, Chrome $250K bounty | None found | Keycloak (CVE-2026-17059), WordPress (2 CVEs) |
| Pricing transparency | None (enterprise); inconsistent 3rd-party self-serve tiers ($4K–$8K/test) | None; internally inconsistent credit figures | None; only AWS Marketplace tier sizes known |
| Review-site rating | No G2/PeerSpot page found | G2: 3 reviews only | G2: 5.0/5.0 |
| Scope breadth | Web apps + APIs (network/AD explicitly excluded) | Web + API + network + AD lateral movement (broadest) | Web + API (GraphQL specialist) + network |

## Strengths & gaps of each, relative to the other two

**XBOW**
- *Strengths relative to FireCompass and Escape:* Far deeper pockets and enterprise channel leverage (NVIDIA, Samsung, Accenture as both investors and go-to-market partners); the strongest, most independently-corroborated real-world exploit evidence (named CVEs in Microsoft/Bing/Exim, a $250K Chrome bounty) rather than benchmark-only claims; the most mature compliance/governance framing (40+ frameworks, explicit ISO 42001 AI-governance badge).
- *Gaps relative to FireCompass and Escape:* Narrowest technical scope of the three — no network, cloud-misconfiguration, or Active Directory lateral-movement testing that FireCompass offers natively, and no GraphQL/business-logic specialism as sharp as Escape's. Its headline HackerOne ranking is the single most publicly, credibly contested claim of any of the three companies' benchmark stories.

**FireCompass**
- *Strengths relative to XBOW and Escape:* Broadest single-platform scope (discovery + web/API/network pentesting + red-team chaining in one SKU), useful for buyers wanting to consolidate multiple point tools; longest operating history in the "continuous automated red teaming" category (2020 patent, category-creating positioning) and a resold/certification-body distribution channel via EC-Council.
- *Gaps relative to XBOW and Escape:* By far the thinnest independent validation of the three — no CVEs credited, no academic corroboration, only 3 G2 reviews, and multiple internally inconsistent figures on its own site (credit/pricing math, false-positive-rate ranges, Hype Cycle counts) that a careful buyer would notice. Smallest, least certain headcount and least capitalized of the three despite being the oldest company.

**Escape**
- *Strengths relative to XBOW and FireCompass:* The only one of the three with a genuine, well-documented technical specialism (business-logic/authorization/GraphQL testing) that the other two treat as a feature among many rather than a core differentiator; the only one with an independent (Doyensec) head-to-head benchmark result; highest G2 rating; credible technical-investor bench (Datadog, Tenable, Qualys founders) signaling peer-level industry validation.
- *Gaps relative to XBOW and FireCompass:* Smallest team and lowest funding of the three, executing across four product lines simultaneously — a real execution-risk contrast with XBOW's much larger, better-funded team; no network/infrastructure-pentesting depth to match FireCompass, and no real-world CVE portfolio as large or headline-grabbing as XBOW's (Microsoft/Bing-scale finds); like the others, has no public pricing.

## Market takeaways

1. **"Proof of exploit" has become table stakes, not a differentiator.** All three companies now lead with near-identical language — autonomous agents, exploit validation, sub-single-digit-percent false positives, chained multi-stage attack paths — meaning a new entrant cannot win on this framing alone; the real fights are happening one layer down, in scope breadth (FireCompass), specialist depth (Escape), and evidentiary credibility (XBOW).
2. **Independent verification is the market's biggest unmet need.** All three dossiers converge on the same finding: nearly every headline claim (benchmark scores, false-positive rates, leaderboard rankings) is self-reported, and even outlets that "cover" these results are usually republishing vendor press releases rather than independently re-testing them. A new entrant that ships a genuinely third-party-audited benchmark, a CREST/OSCP-style certification, or an open, reproducible evaluation methodology would occupy real whitespace.
3. **Scope consolidation is the direction of travel.** XBOW is expanding from single-app pentesting into whole-portfolio "Autonomous Exposure Management" — directly toward FireCompass's traditional territory — while FireCompass already spans discovery-through-red-team, and Escape is layering ASM and network testing onto its DAST/API core. The market is converging on "one agentic platform covers discovery + testing + validation + continuous re-testing," which raises the bar for any new entrant trying to launch as a point solution.
4. **Business-logic/authorization testing remains a genuine, underserved gap that most competitors treat as secondary.** Only Escape has built its architecture specifically around BOLA/IDOR and multi-tenant authorization flaws — a vulnerability class that is hard for pattern-matching scanners (and, per external critique of XBOW, even some "AI" pentesting tools) to find. A new entrant could differentiate by going deeper still on this class, or on adjacent classes like race conditions and complex multi-step business-logic abuse that even Escape's own dossier flags as only partially covered industry-wide.
5. **Pricing opacity is universal and a real point of customer friction.** None of the three companies publishes real enterprise pricing; all gate it behind sales conversations or leave only inconsistent, sometimes self-contradictory, credit/tier figures. A new entrant with genuinely transparent, self-serve pricing (not just a freemium teaser tier) could differentiate sharply with the mid-market and SMB segment all three currently underserve with real price clarity.
6. **Human-in-the-loop is being repositioned as a feature, not an admission of limitation.** FireCompass sells PTaaS explicitly for compliance-grade human attestation; Escape offers an optional human-in-the-loop mode; even XBOW's own most technically candid post shows its fully autonomous agent losing to a human researcher on a hardened target. A new entrant could lean into a credible "hybrid-by-design" positioning — autonomous at scale, human-verified for the compliance-critical/production-critical last mile — rather than treating full autonomy as the only credible endpoint.
7. **Capital intensity increasingly determines category leadership.** XBOW's ~9–11x funding advantage over the other two has bought it deeper enterprise channel partnerships (NVIDIA, Samsung, Accenture) and a much larger public CVE/bounty portfolio in a short time. A new entrant without comparable capital will likely need to win through specialization (Escape's playbook) or platform breadth at lower cost (FireCompass's playbook) rather than by competing on paid-marketing and channel scale directly against XBOW.
