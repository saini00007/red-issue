# Escape (escape.tech) — External Research Profile

*Compiled from outside sources only (news, funding databases, review sites, GitHub, conference pages, podcasts, job boards). Escape's own website was not used as a source here (crawled separately). Research date: 2026-09-26.*

## Executive Summary

Escape is a Paris, France-based offensive security / API security startup founded in **2020** by **Tristan Kalos** (CEO) and **Antoine Carossio** (CTO), and publicly launched out of **Y Combinator's Winter 2023 (W23) batch**. It started as a GraphQL/API security DAST (dynamic application security testing) tool and has since expanded into a three-product platform: **Attack Surface Management**, **Business-Logic-Aware DAST**, and **AI Pentesting** (agentic, AI-agent-driven penetration testing). The company has raised a **€3.6M ($3.9M) seed round (2023)** and an **$18M ($15.4M€) Series A (March 2026)**, led by **Balderton Capital**, for total disclosed funding of roughly **$23–24M**. Reported customers include Sorare, Shine (Société Générale), and Neo4j, and the company claims 2,000+ security teams as users, SOC 2 Type II compliance, and a Wiz "WIN" integration partner award (2025). Outside reviewers (G2, AppSecSanta) rate it highly for GraphQL and business-logic (BOLA/IDOR) testing versus traditional DAST tools, and third-party comparison content positions it against XBOW (exploit-chaining/PoC depth) and FireCompass (attack-surface/CART) in the fast-growing "agentic pentesting" / offensive security market. Team size is estimated at ~29 employees per Y Combinator's company page (LinkedIn listings vary and are noisy due to many unrelated "Escape" companies).

**Biggest research gaps:** no confirmed valuation figure, no confirmed total headcount from a single authoritative source, no public list pricing, no confirmed analyst-firm (Gartner/Forrester) formal ranking or named report inclusion, and no strong evidence of DEF CON/Black Hat/BSides mainstage talks (only GraphQLConf, Nordic APIs, API World/CloudX/DataWeek were confirmed).

---

## 1. Company Overview

| Attribute | Detail | Source |
|---|---|---|
| Founded | 2020 | [Nordic APIs](https://nordicapis.com/speakers/tristan-kalos/), [YC](https://www.ycombinator.com/companies/escape) |
| HQ | Paris, France (Station F) | [Jobs at Station F](https://jobs.stationf.co/companies/escape-technologies-sas), [SecurityWeek](https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/) |
| Y Combinator batch | Winter 2023 (W23) | [YC company page](https://www.ycombinator.com/companies/escape) |
| Headcount (est.) | ~29 employees (YC page); some LinkedIn/ZoomInfo listings show "11-50" but are ambiguous (multiple unrelated "Escape" companies exist) | [YC](https://www.ycombinator.com/companies/escape), [WebSearch of LinkedIn listings] |
| Mission/positioning | "Offensive security for the teams that are 100x outnumbered" — AI agents that discover, test, and remediate vulnerabilities directly in engineering workflows, replacing legacy scanners and manual pentests | [YC](https://www.ycombinator.com/companies/escape), [Tech.eu](https://tech.eu/2026/03/10/escape-secures-18m-series-a-to-develop-ai-cybersecurity-agents/) |
| Compliance | SOC 2 Type II compliant | [AppSecSanta review](https://appsecsanta.com/escape) |
| Founder 1 | **Tristan Kalos**, Co-founder & CEO. Software engineer / ML researcher background at UC Berkeley; prior work in San Francisco building chatbots/APIs; motivated by having a client's MongoDB database hacked/ransomed (~2017-2018) | [Scaling DevTools podcast](https://scalingdevtools.com/podcast/episodes/from-getting-hacked-to-cybersecurity-founders-with-antoine-carossio-and-tristan-kalos-from-escape-tech/transcript), [Nordic APIs](https://nordicapis.com/speakers/tristan-kalos/) |
| Founder 2 | **Antoine Carossio**, Co-founder & CTO. Former security engineer / penetration tester for the French Government (French National Cybersecurity Agency, ANSSI-adjacent) and Apple; open-source maintainer (e.g., Clairvoyance) | [WebSearch bio summary], [Sessionize profile] |
| How founders met | UC Berkeley (MBA program), recognized complementary skills | [Scaling DevTools podcast transcript](https://scalingdevtools.com/podcast/episodes/from-getting-hacked-to-cybersecurity-founders-with-antoine-carossio-and-tristan-kalos-from-escape-tech/transcript) |

### Funding History

| Round | Amount | Date | Investors |
|---|---|---|---|
| Seed | €3.6M (~$3.9M) | June 2023 | Led by **IRIS**; with **Frst**, **Y Combinator**, **Irregular Expressions**, **Tiny Supercomputers**, **Kima Ventures**; angels incl. Philippe Langlois, Mehdi Medjaoui, Roxanne Varza | [IRIS](https://www.iris.vc/articles/escape-raises-eu3-6m-in-seed-to-secure-apis-at-every-development-stage), [EU-Startups](https://www.eu-startups.com/2023/06/fresh-out-of-y-combinator-paris-based-escape-raises-e3-6-million-in-seed-to-secure-apis-at-every-development-stage/) |
| Series A | $18M (€15.4M) | March 10, 2026 | Led by **Balderton Capital**; with **Uncorrelated Ventures**, and existing investors **IRIS** and **Y Combinator** | [Tech.eu](https://tech.eu/2026/03/10/escape-secures-18m-series-a-to-develop-ai-cybersecurity-agents/), [SecurityWeek](https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/), [Balderton](https://www.balderton.com/news/escape-raises-18m-series-a-to-fight-ai-powered-cyberattacks-with-ai-agents/), [EU-Startups](https://www.eu-startups.com/2026/03/yc-backed-escape-raises-e15-4m-series-a-led-by-balderton-for-its-ai-powered-offensive-security-engineering-platform/) |
| **Total disclosed** | **~$23–24M** across 3 rounds (Crunchbase aggregate; includes smaller unlabeled tranches) | — | — | [Crunchbase](https://www.crunchbase.com/organization/escape-b74e) |

Valuation was **not disclosed** in any source found (marked `unverified`). Legal counsel Gide advised Escape on the Series A. [Gide](https://www.gide.com/en/news-insights/gide-advises-escape-on-its-18-million-series-a-funding-round-led-by-balderton/)

---

## 2. Products & Features (as described by outside sources)

Per third-party reviews (notably [AppSecSanta's 2026 review](https://appsecsanta.com/escape)) and press coverage, Escape's platform comprises three product lines:

| Product | Description | Source |
|---|---|---|
| **Attack Surface Management (ASM)** | Continuous discovery/visibility of APIs, apps, and cloud assets across code and cloud environments using subdomain enumeration, AI-powered fingerprinting, and OSINT techniques | [WebSearch summary of escape blog via Crunchbase/other coverage], [AWS Marketplace listing](https://aws.amazon.com/marketplace/pp/prodview-botb7xtpafuxe) |
| **Business-Logic-Aware DAST** | API-native dynamic scanning (agentless, no proxy/agent needed) running 140+ automated attack scenarios/tests, focused on OWASP API Top 10, BOLA/IDOR, and access-control/business-logic flaws rather than only injection/XSS; native GraphQL support (introspection, type-aware payloads, resolver testing); multi-user/session testing to find authorization boundary violations between roles; incremental scanning of only changed endpoints in PRs; CI/CD integrations (GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket, CircleCI) | [AppSecSanta](https://appsecsanta.com/escape), [G2 reviews](https://www.g2.com/products/escape/reviews) |
| **AI Pentesting** | Agentic, continuous penetration testing launched ~July 2025; multi-agent architecture — an orchestrator/coordinator agent holds pentest state, delegates to specialized agents that perform assessments, reporting, and context-handling, using sandboxed tools; aims to find multi-step attack chains "the way a human pentester would" at CI-pipeline scale | [Trend Hunter](https://www.trendhunter.com/trends/escape-ai-agents), [Balderton news](https://www.balderton.com/news/escape-raises-18m-series-a-to-fight-ai-powered-cyberattacks-with-ai-agents/), arxiv context on agentic-pentesting architectures (general field, not Escape-specific) |

**Architecture/approach**, per outside sources:
- "Feedback-driven API exploration" approach for deeper testing than brute-force scanning ([YC company page](https://www.ycombinator.com/companies/escape)).
- Agentless, no traffic-monitoring/proxy required, contrasted against traditional traffic-based API security tools ([Security Boulevard](https://securityboulevard.com/2024/08/reinventing-api-security-why-escape-is-better-than-traditional-traffic-based-tools/)).
- Handles complex auth flows: OAuth 2.0, AWS Cognito, JWT, MFA ([AppSecSanta](https://appsecsanta.com/escape)).
- Public API (v3, Aug 2025) and CLI for orchestrating scans and configuration ([escape.tech blog referenced via search results, not fetched directly per task instructions]).

### Related open-source projects (GitHub, confirms technical focus)
- **graphql-armor** — security middleware for Apollo/Yoga/Envelop GraphQL servers; reviewers cite 100,000+ weekly npm downloads ([AppSecSanta](https://appsecsanta.com/escape), [GitHub](https://github.com/Escape-Technologies/graphql-armor))
- **graphinder** — GraphQL endpoint finder via subdomain enumeration ([GitHub](https://github.com/Escape-Technologies/graphinder))
- **goctopus** — GraphQL discovery/fingerprinting toolbox ([GitHub](https://github.com/Escape-Technologies/goctopus))
- **awesome-graphql-security** — curated list of GraphQL security tools ([GitHub](https://github.com/Escape-Technologies/awesome-graphql-security))
- **graphql-security-academy** — free browser-based GraphQL security learning platform ([GitHub](https://github.com/Escape-Technologies/graphql-security-academy))
- **Clairvoyance** — GraphQL introspection/field-suggestion tool Carossio maintains ([LinkedIn post reference](https://www.linkedin.com/posts/acarossio_graphql-fieldsuggestion-clairvoyance-activity-7056959872495468544-2cfo))

---

## 3. Pricing / Packaging

Escape does **not publish list prices**. Reported structure (`unverified` exact numbers):

- AWS Marketplace lists an **Enterprise Plan with three capacity tiers**: up to 15 apps, up to 60 apps, or up to 120 apps, each with unlimited scan frequency and dedicated technical support. [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-yffo3s4uoj7zs)
- AWS Marketplace Private Offers available for negotiated pricing. [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-yffo3s4uoj7zs)
- AppSecSanta review notes a **free tier for scanning a single API**, with paid cost scaling by application count, testing-scope depth, and private-location requirements; positions Escape's pricing as comparable to Bright Security (mid-market tier), i.e., "platform pricing aligned to scope" rather than per-action billing (contrasted with XBOW's ~$6,000-per-pentest or credit-pack model). [AppSecSanta](https://appsecsanta.com/escape)

---

## 4. Customers, Case Studies, Partners, Integrations

| Customer/Partner | Detail | Source |
|---|---|---|
| **Shine** (Société Générale's online banking subsidiary) | Case study: federated GraphQL system merging REST APIs; used Escape to find/fix vulnerabilities | [Security Boulevard case study](https://securityboulevard.com/2023/10/case-study-how-escape-enhanced-shines-application-security/) |
| **Sorare** | CTO Adrien Montfort quoted: "Escape was able to find and help us fix security flaws that human security auditors have not seen." | [IRIS seed article](https://www.iris.vc/articles/escape-raises-eu3-6m-in-seed-to-secure-apis-at-every-development-stage) |
| **Neo4j** | Listed as a customer (no dedicated case study found) | [IRIS](https://www.iris.vc/articles/escape-raises-eu3-6m-in-seed-to-secure-apis-at-every-development-stage) |
| BetterHelp, PandaDoc, CyberCube Analytics, Arkose Labs | Named as customers in one SiliconANGLE funding writeup — **could not cross-confirm on a second independent source**, flagged as lower-confidence | [SiliconANGLE](https://siliconangle.com/2026/03/10/escape-raises-18m-expand-ai-agent-platform-offensive-security-testing/) |
| **Wiz** | Technology/integration partner; Escape won Wiz's inaugural "WIN" (Wiz Integrations) Partner Award in 2025 for its Wiz⇄Escape DAST integration sharing prioritized findings (inventory, vulnerabilities, configuration) | [Security Boulevard](https://securityboulevard.com/2025/07/escape-honored-with-inaugural-wiz-integrations-win-partner-award/), [Wiz blog on 200+ integrations](https://www.wiz.io/blog/celebrating-200-wiz-integrations) |
| AWS | Marketplace listings: "Escape - Business-logic-aware DAST," "Escape AI Pentesting," "Escape Attack Surface Management," "Sherpa by Escape Technology"; AWS ISV Accelerate Program member | [AWS Marketplace search results] |
| CI/CD ecosystem | GitHub Actions, GitLab CI, Jenkins, Azure DevOps, Bitbucket, CircleCI integrations (per review) | [AppSecSanta](https://appsecsanta.com/escape) |
| Scale (customer count) | "2,000+ security teams" using the platform (widely repeated across 2025-2026 press) | [SecurityWeek](https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/), [AppSecSanta](https://appsecsanta.com/escape) |

---

## 5. Key Numbers / Metrics Publicized

| Metric | Value | Date | Source |
|---|---|---|---|
| Customers within 6 months of 2023 launch | 1,000+ organizations | mid-2023 | [IRIS](https://www.iris.vc/articles/escape-raises-eu3-6m-in-seed-to-secure-apis-at-every-development-stage) |
| Current customer base | 2,000+ security teams globally | 2025-2026 (repeated) | [SecurityWeek](https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/) |
| Monthly security assessments run | 300,000+ | March 2026 | [SiliconANGLE](https://siliconangle.com/2026/03/10/escape-raises-18m-expand-ai-agent-platform-offensive-security-testing/) (lower confidence, single source) |
| Fortune 1000 exposure research | 28,500+ exposed APIs; 98,800 vulnerabilities found; 1,830 highly critical | Nov 20, 2024 ("State of API Exposure" report) | [Help Net Security](https://www.helpnetsecurity.com/2024/12/12/exposed-apis-issues-video/), [Escape PDF hosted on HubSpot](https://26857953.fs1.hubspotusercontent-eu1.net/hubfs/26857953/State%20of%20API%20Exposure%202024%20-%20Escape.pdf) |
| Vibe-coded/AI-built app research | 2,000+ high-impact vulnerabilities found across 5,600 publicly available apps built with AI coding tools; 175 cases of personal-data exposure | cited in March 2026 Series A coverage | [Tech.eu](https://tech.eu/2026/03/10/escape-secures-18m-series-a-to-develop-ai-cybersecurity-agents/) |
| Industry stat cited by Escape research | 57% of organizations suffered an API-related breach in past 2 years | 2024 | [Help Net Security](https://www.helpnetsecurity.com/2024/02/05/exposed-api-secrets/) |
| Customer ROI claim | One customer reported 393% ROI, cutting security testing cycle from 5 days to 5 hours | 2025/2026 | [WebSearch summary, AI Pentesting coverage] (single-source, unverified) |
| G2 rating | 5.0 / 5.0 | as of search date (2026) | [G2](https://www.g2.com/products/escape/reviews) |
| graphql-armor npm downloads | 100,000+ weekly | 2026 | [AppSecSanta](https://appsecsanta.com/escape) |
| Team size | 29 employees | 2026 (YC page snapshot) | [YC](https://www.ycombinator.com/companies/escape) |

---

## 6. Research Output, CVEs, Talks, Notable Researchers

| Item | Detail | Date | Source |
|---|---|---|---|
| CVE-2026-17059 | Escape's research team ("Orionexe") found and reported a PII-disclosure vulnerability in Keycloak (`GET /roles/{role}/users` leaking user PII); reported to Keycloak team July 18, 2026; CVE published July 24, 2026; fixed July 28, 2026 | July 2026 | [WebSearch of escape.tech blog post title/summary — content not fetched] |
| GraphQL Security Vulnerabilities in the Wild | Talk by Antoine Carossio & Tristan Kalos at **GraphQLConf 2023**, presenting research scanning 1,500+ GraphQL endpoints, finding 46,000+ security issues/data leaks (~10% critical) | 2023 | [GraphQL.org session page](https://graphql.org/conf/2023/sessions/5bf24cd6483a63e62a2276fe38effb82/), [YouTube](https://www.youtube.com/watch?v=hyB2UKsEkqA) |
| Nordic APIs Platform Summit 2023 | Tristan Kalos presented; bio states he has also spoken at Forum InCyber, APIdays, and other software/security conferences | 2023 | [Nordic APIs](https://nordicapis.com/speakers/tristan-kalos/) |
| API World + CloudX + DataWeek 2025 | Tristan Kalos scheduled speaker | 2025 | [Sched.com](https://apiworldcloudxdataweek2025.sched.com/speaker/tristan_kalos.28elzft0) |
| DEF CON / Black Hat / BSides | No confirmed mainstage Escape talk found in this research pass | — | `unverified` |
| OWASP | No confirmed named Escape talk found | — | `unverified` |
| Antoine Carossio open-source work | Maintainer/contributor to Clairvoyance (GraphQL introspection tool) | ongoing | [LinkedIn post](https://www.linkedin.com/posts/acarossio_graphql-fieldsuggestion-clairvoyance-activity-7056959872495468544-2cfo) |
| "State of API Exposure" research report | Independent large-scale scan of Fortune 1000 API exposure | Nov 2024 | [Help Net Security](https://www.helpnetsecurity.com/2024/12/12/exposed-apis-issues-video/) |
| "The API Secret Sprawl" / State of API Security 2024 | Research on exposed API secrets/tokens in major tech | Feb 2024 | [Help Net Security](https://www.helpnetsecurity.com/2024/02/05/exposed-api-secrets/) |

Academic field context (not Escape's own publications, but relevant adjacent research on the "AI agent pentesting" category Escape competes in): *Know Your Agent: Reconnaissance-Driven Pentesting of AI Agents* ([arXiv 2607.19837](https://arxiv.org/abs/2607.19837)); *Toward Secure AI-Powered Penetration Testing Agents* ([arXiv 2609.16694](https://arxiv.org/abs/2609.16694)); *PentestAgent* ([arXiv 2411.05185](https://arxiv.org/pdf/2411.05185)). No arXiv paper authored by Escape/Kalos/Carossio was found.

---

## 7. Leadership & Key Team

| Name | Role | Background | Source |
|---|---|---|---|
| Tristan Kalos | Co-founder & CEO | ML researcher/software engineer, UC Berkeley; worked in San Francisco on chatbots/APIs before Escape; motivated by a client database being hacked/held for ransom (~2017-2018) | [Scaling DevTools transcript](https://scalingdevtools.com/podcast/episodes/from-getting-hacked-to-cybersecurity-founders-with-antoine-carossio-and-tristan-kalos-from-escape-tech/transcript), [Nordic APIs](https://nordicapis.com/speakers/tristan-kalos/) |
| Antoine Carossio | Co-founder & CTO | Former penetration tester/security engineer for the French Government and for Apple; GraphQL security researcher; open-source maintainer | [Sessionize](https://sessionize.com/antoine-carossio/), [GraphQL.org speaker page](https://graphql.org/conf/2023/speakers/antoine.carossio) |
| (Research team) | Security Researchers (Mid-level, Senior, Lead) | Job listings describe a research team of at least ~3+ researchers under a "Lead Security Researcher" role as of 2026, based in Paris | [Welcome to the Jungle listings](https://www.welcometothejungle.com/fr/companies/escape/jobs/lead-security-researcher-ai-appsec_paris) |

No other named C-suite/VP hires were confirmed from outside sources (`unverified` beyond the two co-founders).

---

## 8. Chronological News / Announcement Timeline

| Date | Headline | Source |
|---|---|---|
| 2020 | Company founded (Paris) | [Nordic APIs](https://nordicapis.com/speakers/tristan-kalos/) |
| Winter 2023 | Y Combinator W23 batch; Launch HN post | [Hacker News](https://news.ycombinator.com/item?id=39215779), [YC launch](https://www.ycombinator.com/launches/I4v-escape-secure-your-graphql-apis) |
| June 2023 | €3.6M ($3.9M) seed round announced, led by IRIS | [EU-Startups](https://www.eu-startups.com/2023/06/fresh-out-of-y-combinator-paris-based-escape-raises-e3-6-million-in-seed-to-secure-apis-at-every-development-stage/) |
| October 2023 | Shine (Société Générale) case study published | [Security Boulevard](https://securityboulevard.com/2023/10/case-study-how-escape-enhanced-shines-application-security/) |
| Nov 2023 | GraphQLConf 2023 talk: "GraphQL Security Vulnerabilities in the Wild" | [GraphQL.org](https://graphql.org/conf/2023/sessions/5bf24cd6483a63e62a2276fe38effb82/) |
| Feb 2024 | "State of API Security 2024 — The API Secret Sprawl" research covered | [Help Net Security](https://www.helpnetsecurity.com/2024/02/05/exposed-api-secrets/) |
| Aug 2024 | "Reinventing API security" positioning piece vs. traffic-based tools | [Security Boulevard](https://securityboulevard.com/2024/08/reinventing-api-security-why-escape-is-better-than-traditional-traffic-based-tools/) |
| Nov 20, 2024 | "State of API Exposure" Fortune 1000 research report released | [Help Net Security](https://www.helpnetsecurity.com/2024/12/12/exposed-apis-issues-video/) |
| ~2025 | Escape joins AWS ISV Accelerate Program; lists on AWS Marketplace | [AWS Marketplace listings] |
| July 2025 | Wiz Integrations (WIN) inaugural Partner Award won by Escape | [Security Boulevard](https://securityboulevard.com/2025/07/escape-honored-with-inaugural-wiz-integrations-win-partner-award/) |
| July 2025 | AI Pentesting agentic product launched (multi-agent architecture) | [Trend Hunter](https://www.trendhunter.com/trends/escape-ai-agents) |
| Aug 2025 | Public API v3 released (post-ASM platform restructure) | [WebSearch of product-updates post title] |
| Dec 2025 | Product update: "Test Configuration" pre-scan validation feature | [WebSearch of product-updates post title] |
| July 18-28, 2026 | Escape researcher reports Keycloak PII-disclosure bug → CVE-2026-17059 | [escape.tech blog title via search] |
| March 10, 2026 | $18M / €15.4M Series A announced, led by Balderton Capital | [Tech.eu](https://tech.eu/2026/03/10/escape-secures-18m-series-a-to-develop-ai-cybersecurity-agents/), [SecurityWeek](https://www.securityweek.com/escape-raises-18-million-to-automate-pentesting/), [Balderton](https://www.balderton.com/news/escape-raises-18m-series-a-to-fight-ai-powered-cyberattacks-with-ai-agents/), [SiliconANGLE](https://siliconangle.com/2026/03/10/escape-raises-18m-expand-ai-agent-platform-offensive-security-testing/), [fintech.global](https://fintech.global/2026/03/10/escape-raises-18m-series-a-for-ai-offensive-security/) |
| March 2026 | Gide law firm announces it advised Escape on the Series A | [Gide](https://www.gide.com/en/news-insights/gide-advises-escape-on-its-18-million-series-a-funding-round-led-by-balderton/) |

---

## 9. Notable Videos / Talks / Podcasts / Webinars

| Title | Type | URL |
|---|---|---|
| GraphQL Security Vulnerabilities in the Wild — Antoine Carossio & Tristan Kalos, Escape (GraphQLConf 2023) | Conference talk (YouTube) | [youtube.com/watch?v=hyB2UKsEkqA](https://www.youtube.com/watch?v=hyB2UKsEkqA) |
| Startup Savant Podcast — Escape founders on getting hacked → founding the company | Podcast | [startupsavant.com/startup-savant-podcast/episodes/escape](https://startupsavant.com/startup-savant-podcast/episodes/escape) |
| Scaling DevTools Podcast — "From getting hacked to cybersecurity founders" with Antoine Carossio & Tristan Kalos | Podcast (with transcript) | [scalingdevtools.com/podcast/.../transcript](https://scalingdevtools.com/podcast/episodes/from-getting-hacked-to-cybersecurity-founders-with-antoine-carossio-and-tristan-kalos-from-escape-tech/transcript) |
| Escape YouTube channel (@escapetechhq) | Channel (webinars/demos) | [youtube.com/@escapetechhq](https://www.youtube.com/@escapetechhq) |
| Escape Tech YouTube channel | Channel | [youtube.com/@escape-tech](https://www.youtube.com/@escape-tech) |
| Launch HN: Escape (YC W23) – Discover and secure all your APIs | Community discussion | [news.ycombinator.com/item?id=39215779](https://news.ycombinator.com/item?id=39215779) |

Note: several webinar titles ("Automating Offensive Security with AI," "Securing AI-driven applications with DAST," "Doing More With Less," "Building your Product Security Roadmap") were found referenced in third-party search indexing but the pages themselves are hosted on escape.tech and were not fetched per task scope; listed as identified-but-unverified in detail.

---

## 10. External Perception: Reviews, Analyst Coverage, Sentiment

- **G2**: 5.0/5 rating; reviewers cite strong GraphQL/business-logic detection, efficient vulnerability detection, accurate findings, good UI/filtering; noted weaknesses include remediation guidance and documentation could be more detailed. [G2](https://www.g2.com/products/escape/reviews)
- **AppSecSanta (independent AppSec review site), 2026**: Positions Escape as "the right pick for teams building API-first applications, especially GraphQL," citing 140+ tests and BOLA/IDOR detection as a genuine differentiator; notes pricing is not public and Escape is less suited to traditional server-rendered web apps. Lists Invicti, Bright Security, StackHawk, Burp Suite Professional, and Akto as alternatives. [AppSecSanta](https://appsecsanta.com/escape)
- **Gartner**: General Gartner "Market Guide for API Protection" commentary on shadow/dormant API risk was found, but **no confirmed named inclusion or rating of Escape** in a Gartner report was located in this pass (`unverified`). [Gartner Peer Insights — API Protection market](https://www.gartner.com/reviews/market/api-protection)
- **AWS Marketplace reviews**: A dedicated "Escape Attack Surface Management" reviews page exists on AWS Marketplace, indicating real customer usage/reviews there, though specific quotes were not extracted in this pass. [AWS Marketplace reviews](https://aws.amazon.com/marketplace/reviews/reviews-list/prodview-botb7xtpafuxe)
- **Community/Reddit/HN sentiment**: The 2023 Launch HN thread is the clearest community discussion found; broader Reddit threads specifically about Escape.tech were not found in this pass (`unverified`/likely low volume). [Hacker News](https://news.ycombinator.com/item?id=39215779)
- **Industry recognition**: Wiz's inaugural WIN (Wiz Integrations) Partner Award, 2025, for the Escape⇄Wiz integration. [Security Boulevard](https://securityboulevard.com/2025/07/escape-honored-with-inaugural-wiz-integrations-win-partner-award/)

---

## 11. Competitive Comparisons (as framed by third parties)

| Comparison | Framing (third-party) | Source |
|---|---|---|
| **Escape vs. XBOW** | Escape positioned as purpose-built for continuous business-logic testing across APIs/web apps with predictable "platform" pricing; XBOW positioned as stronger on exploit-chaining/adversarial PoC depth, priced per-pentest (~$6,000+) or via credit packs. A market blog (Escape's own "XBOW Alternatives" content, echoed by Security Boulevard) frames Escape as "the strongest XBOW alternative in 2026" for continuous, engineering-led AI pentesting | [Security Boulevard reprint](https://securityboulevard.com/2026/04/top-xbow-alternatives-in-2026/) |
| **Escape vs. FireCompass** | An independent market-map newsletter (Cyberflow) characterizes Escape as covering "APIs but at scanner grade, without PoC exploitation depth," implicitly contrasting with FireCompass's Continuous Automated Red Teaming (CART)/EASM approach which validates discovered risk via active exploitation (FireCompass claims ~98% accuracy) | [Cyberflow market-map substack](https://cyberflow.substack.com/p/offensive-security-market-map-the-rise-of-autonomous-hacking), [FireCompass EASM](https://firecompass.com/external-attack-surface-management/) |
| **Escape vs. traditional DAST (Invicti, Bright Security, StackHawk, Burp Suite Pro, Akto)** | AppSecSanta frames Escape as the specialist choice for API-heavy/GraphQL architectures vs. these broader/general-purpose DAST tools | [AppSecSanta](https://appsecsanta.com/escape) |
| **Escape vs. traffic-based API security tools** (e.g., traditional API security posture tools that rely on traffic monitoring) | Escape/Security Boulevard content argues traffic-based tools miss vulnerabilities that active, agentless DAST testing catches | [Security Boulevard](https://securityboulevard.com/2024/08/reinventing-api-security-why-escape-is-better-than-traditional-traffic-based-tools/) |
| **CB Insights comparison page** | CB Insights maintains a head-to-head comparison page "Escape vs. Traceable AI," indicating Traceable (API security/observability) is also treated as a peer/competitor in analyst databases | [CB Insights](https://www.cbinsights.com/compare/escape-vs-traceable) |

Note: no direct third-party "Escape vs. Escape.tech" comparison exists (the task's own list included "Escape.tech" as a competitor name, which is this same company under research); it is not a distinct competitor.

---

## Sources

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
