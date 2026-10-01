---
url: https://escape.tech/blog/introducing-cascade-the-multi-agent-penetration-testing/
category: blog_post
title: Introducing Cascade: the multi-agent penetration testing that becomes an expert in your business
---
# Introducing Cascade: the multi-agent penetration testing that becomes an expert in your business

## Summary
Escape announces Cascade, a multi-agent AI penetration testing engine built on top of its Attack Surface Management (ASM) and DAST platform. Unlike one-off automated pentest tools that produce a static report, Cascade builds a persistent, compounding model of a customer's business/application context, tests using multiple simultaneous user identities to find authorization flaws, proves every finding with a working exploit, and feeds proven findings into Escape DAST as permanent regression tests. The post also shares benchmark results against Claude Code (Opus 4.7), Aikido, and Xbow on OWASP Juice Shop, Fider, and Photoview, and a real-world case study of a pricing-manipulation vulnerability found on a customer's platform.

## Full content

### Introduction
Most automated pentesting tools treat your application like a stranger. It shows up, runs a bunch of tests against whatever endpoint it's pointed at, and leaves a report. It doesn't know that your "admin" can act on behalf of a "doctor," that a "patient" should never see another patient's records, or that your pricing logic lives across three services that only break when you test them together.

Cascade is different. It's the multi-agent pentest engine inside Escape, and because it sits on top of everything the platform already knows about your attack surface, it doesn't start from zero. It starts as something closer to an in-house pentester who has read your docs, mapped your APIs, and watched your last ten releases. Every engagement makes it more expert in your business. Every finding it proves becomes a test your DAST can re-run forever.

This is the deep-assessment layer of an offensive security program, built to run continuously inside the engineering processes, not as a yearly one-off cost.

This release was shaped directly by Escape's design partners; feedback is invited to help Cascade improve.

By-line: Alexandra Charikova, Antoine Carossio, Hugo Pucéat — Jun 4, 2026 • 15 min read

### Why we changed the approach
Over the last two years, automated pentesting got faster, cheaper, and, thanks to frontier AI, genuinely deeper. Agents can now reason about an application the way a tester does, chain multi-step exploits, and find logic flaws that traditional vulnerability scanning never could. That's real progress, and the whole industry is better for it.

But almost all of it still optimizes for the same deliverable: a pentest report. Point a tool at a target, get a PDF, satisfy the compliance requirement. The test arrives knowing nothing about your org, runs once, and leaves nothing behind.

A report is not a program. The security teams Escape works with don't need another document sitting in a backlog. They need offensive security that runs the way engineering runs — continuous, contextual, and compounding.

The hard part has always been running a test that understands your application well enough to find the vulnerabilities that only exist because of how you built it: business logic, privilege escalation across user roles — the findings a good human pentester gets to in week three, not the ones a generic scanner gets in the first hour.

So the gap Escape set out to close was never just depth. The gap was context and continuity.

Escape's research team rebuilt its pentesting engine around two ideas:
- First: an autonomous test is only as good as its context, so it gives it the full picture of your attack surface.
- Second: depth and scale aren't a trade-off if the engine that finds the vulnerability hands it to a system that can re-test it on every release. That's Cascade, and it's why it lives next to ASM and DAST instead of off to the side.

### What makes Cascade different

**It becomes an expert in your business**
Cascade runs on the same platform as Escape ASM and DAST, so it starts every engagement with a continuous model of your entire attack surface: every API, SPA, and host discovery has been found, and everything DAST already covers. It can also integrate with existing security, cloud, and developer tools to sharpen the picture and adapt its tests to how your systems actually work.

So a Cascade engagement isn't an isolated test — it compounds. Escape's updated architecture keeps a memory of what's relevant to you across engagements: for example, that you work in healthcare and have admin, doctor, and patient roles with different access levels, that your docs contain real-looking data, that one service handles payments. The more Cascade tests, the more it knows.

**It tests as multiple users at once**
Cascade holds several user identities at the same time, each in its own isolated browser session. That's the only way to answer "can user A read user B's order?" and it's how broken object-level authorization and privilege escalation become findable. Single-identity scanners structurally can't ask that question.

**Your entire attack surface is assessed**
Most AI pentesting tools focus on exploitation, but the best exploit agent is useless if it misses half your application. Cascade builds on years of DAST expertise to solve this at the root: a dedicated discovery agent systematically maps the entire scope before exploitation begins, feeding everything back into the platform context so no endpoint, page, or asset is left untested. Coverage gaps are actively monitored and closed in real time during exploitation. Every API endpoint, webpage, and asset discovered is surfaced in the results so customers can see exactly what was assessed.

**Every finding is proven, then re-tested forever**
Every Cascade finding ships with proof: the exact request sequence, the user scopes involved, the working exploit, and framework-specific remediation guidance. Findings flow into Escape DAST, becoming an unlimited regression test that re-runs on every release inside CI/CD.

### How Cascade works

**Cascade's architecture**
Cascade is a multi-agent harness with an orchestrator at the center. It replaces the earlier model of separate, single-purpose agents (one each for XSS, SQLi, IDOR, and so on). Instead of a fixed agent list, Cascade creates the specialists a target actually needs, on demand. Cascade agents don't carry one giant prompt — they load modular skills: focused playbooks scoped to the task in front of them, so each agent's context stays small and relevant.

Powered by Attack Surface Management knowledge: Cascade starts from everything the platform already knows. When Escape ASM discovers an asset, it fingerprints it (e.g., a Next.js app behind Cloudflare on AWS, using Auth0) and hands Cascade the full context: the URL, linked API services, schemas, tech stack, and scope rules. The orchestrator then models your application: it crawls the app, learns its business logic, and maps the APIs behind it.

Coordinated, agentic exploitation: the orchestrator holds the state of the engagement and decides what to test next. Beneath it, agents do the work a pentest team would: recon, gaining access, probing business logic, exploiting — each with the tooling a human reaches for, like a service to test for SSRF or a mailbox to verify emails.

The Cascade harness is built from four roles:
- **Orchestrator**: plans the engagement, breaks it into tasks, spawns other agents, and decides when the engagement is complete. Coordinates the swarm and prioritizes work within the configured scope, users, context, and time budget.
- **Coverage agent**: explores the surfaces and plays the role of an advisory auditor that proposes follow-up work from coverage gaps. Has no exploitation tools of its own.
- **Exploitation agents**: focused agents the orchestrator creates for a specific job (e.g. "SQLi discovery on the reporting API", "XSS validation", "auth testing across tenants"). Created dynamically, run in parallel; stop consuming budget once a task returns.
- **Reporter agent**: receives candidate findings from exploitation agents and independently reproduces each one on the live target, collecting its own evidence before filing an issue. Deliberately isolated from exploitation agent-to-agent messaging so its verification stays independent.

Exploitation agents coordinate through a shared message bus (seeded with topics such as recon, xss, sqli, idor, ssrf, auth, and rce) and a shared knowledge store, so signal discovered by one agent reaches the rest of the swarm quickly. Context flows back through the orchestrator after every step, and one agent's discovery shapes what the next one tries.

When Cascade finds something, it proves it: reasoning logs capture the orchestrator's full chain of thought at every step, and attack chains lay out the reproducible path — not "we observed exposed PII," but "here is exactly how user A read user B's order," request by request.

Remediate and re-test: every finding ships with framework-specific remediation, then flows back to the asset in ASM and becomes a regression test in Escape DAST that runs on every build.

Launching an engagement takes four steps: scope target URLs, add user accounts (a second account typically uncovers 30–50% more issues by unlocking multi-user testing that finds IDORs and BOLAs), optionally fine-tune context and duration, then review and launch with one click. Users can bring OpenAPI specs, Postman collections, HAR recordings, Burp exports, additional context, and previous pentest reports for agents to use, point one engagement at multiple assets at once, or launch from their own pipelines via Escape's public API and MCP.

### Real-world impact
Escape pointed Cascade at one customer's application — the external-facing pricing surface of a consumer platform with a web app and campaign APIs behind it. It found a business-logic flaw no payload-injection scanner would catch: the pricing API accepted a negative quantity for a paid product extra and applied it in server-side calculations, producing negative prices on an unauthenticated, internet-facing endpoint.

How it reasoned through the attack:
- It pulled a live campaign identifier from a public endpoint, with no authentication, confirming the pricing workflow could be exercised by anyone.
- It fetched a real product to establish the normal price (€22.99) and confirmed the "extra pages" field was a quantity-based add-on with a positive per-unit charge. Public API docs only ever showed positive examples.
- It submitted a quantity of -50 to the single-product pricing endpoint. The service applied it in the normal calculation path and returned negative totals with a 201 Created.
- It reproduced the same flaw through the bulk pricing route, then ran a control test: it tried injecting a price field directly, which was rejected ("the key base_price is not a valid extra for this product"). Because arbitrary price fields are rejected while negative quantities are accepted and calculated, Cascade could prove this was a genuine server-side pricing-logic failure. Cascade handed over the working exploit and affected endpoints (single and bulk), and shipped remediation across three layers: input validation, hardening the pricing function itself, and a final response-layer invariant.

Customer quote: "The results from the AI pentesting actually caught something interesting. Even through my own testing, when I was trying to validate how transfers operated, that was something I was running into as well. It's nice to know the scan is recognizing this kind of gap in business logic." — Team Lead, Offensive Security, global payments & fintech platform

### How Cascade compares

**OWASP Juice Shop**
Escape tested Cascade against OWASP Juice Shop (industry-standard benchmark) and compared it directly against Claude Code (running Opus 4.7) as a raw AI baseline. Cascade was tested in black-box (no source access) and white-box (with source access) modes.

Number of findings by severity on Juice Shop:
| | Cascade (black-box) | Cascade (white-box) | Claude Code (black-box, best result) | Claude Code (white-box) |
|---|---|---|---|---|
| Total | 36 | 49 | 22 | 22 |
| High | 20 | 31 | 11 | 13 |
| Medium | 15 | 17 | 7 | 6 |
| Low | 1 | 1 | 4 | 3 |

Cascade detected 49 vulnerabilities in white-box mode: more than 2x the findings of Claude Code (22). Even in black-box mode, Cascade (36) outperforms Claude Code's best result.

**Real-world applications: Fider & Photoview**
To benchmark against more realistic targets, Escape used two open-source applications — Fider and Photoview — from an independent comparative study published by Doyensec, which assessed multiple AI pentesting solutions on the same targets. Cascade was benchmarked against the solutions in that report, and again against Claude Code. Note: critical and high findings were merged for consistency since compared solutions don't share a unified definition of "critical".

Number of findings by severity on Fider:
| | Cascade (black-box) | Cascade (white-box, best result) | Aikido (white-box) | Xbow (white-box) | Claude Code (white-box) |
|---|---|---|---|---|---|
| Total | 20 | 27 | 17 | 18 | 7 |
| High | 4 | 4 | 3 | 3 | 1 |
| Medium | 11 | 12 | 6 | 7 | 3 |
| Low | 5 | 11 | 8 | 8 | 3 |

Number of findings by severity on Photoview:
| | Cascade (black-box) | Cascade (white-box, best result) | Aikido (white-box) | Xbow (white-box) | Claude Code (white-box) |
|---|---|---|---|---|---|
| Total | 12 | 28 | 24 | 5 | 7 |
| High | 7 | 7 | 6 | 2 | 2 |
| Medium | 2 | 9 | 9 | 2 | 1 |
| Low | 3 | 12 | 9 | 1 | 4 |

On Fider, Cascade leads across the board in both modes, finding 20-27 total vulnerabilities. On Photoview, Cascade (white-box) tops all solutions with 28 findings. Escape said it would provide the complete benchmark "in a week."

**Black-box vs. white-box**
Cascade supports both modes. On Fider, the gap between black-box and white-box is low (15 vs. 16 HIGH+MEDIUM). On Photoview, white-box mode unlocks a significant uplift (12 → 28), reflecting how source code access can reveal deeper, code-path-dependent vulnerabilities in certain application architectures. Escape frames black-box Cascade as a strong option for environments where source access is restricted (third-party integrations, strict regulatory boundaries, supplier assessments), while white-box goes deeper when source can be shared.

### Looking ahead
APIs and web apps are where Cascade starts. Escape is expanding its exploitation agents' library on a steady cadence, deepening cross-asset and multi-user reasoning, and giving customers more visibility into what Cascade understood about their application.

### Get started
Cascade is positioned as the only AI pentester built to be part of a program rather than sold as a one-off transaction: context-aware because it sits next to ASM, compounding because it remembers your business, and continuous because every finding it proves becomes a test within DAST that runs on the next release. Call to action: "Book a demo with our product experts."

## Features / claims mentioned
- Multi-agent pentest engine ("Cascade") built on top of Escape's ASM and DAST platform
- Starts every engagement with a continuous model of the entire attack surface (every API, SPA, host discovery, everything DAST covers)
- Integrates with existing security, cloud, and developer tools
- Retains memory of business context across engagements (compounding, not a one-off transaction)
- Holds multiple simultaneous user identities, each in its own isolated browser session, to test authorization issues (BOLA/IDOR, privilege escalation)
- Dedicated discovery agent systematically maps the entire scope before exploitation begins
- Coverage gaps actively monitored and closed in real time during exploitation
- Fully auditable coverage: every API endpoint, webpage, and asset discovered is surfaced in results
- Every finding ships with a working exploit, request sequence, user scopes involved, and framework-specific remediation guidance
- Findings flow into Escape DAST as unlimited regression tests that re-run on every release/CI/CD build
- Orchestrator-centered multi-agent harness with dynamically spawned specialist agents (replacing fixed single-purpose agents like XSS/SQLi/IDOR bots)
- Agents load modular "skills" (focused playbooks) rather than one large prompt
- Four agent roles: Orchestrator, Coverage agent, Exploitation agents, Reporter agent
- Reporter agent independently reproduces findings, isolated from exploitation-agent messaging, for independent verification
- Shared message bus (topics: recon, xss, sqli, idor, ssrf, auth, rce) and shared knowledge store among exploitation agents
- Reasoning logs capture orchestrator's full chain of thought
- Attack chains document exact reproducible request-by-request paths
- No YAML, no test toggles, no templates to maintain — four-step launch (scope URLs, add user accounts, tune context/duration, review & launch)
- Supports importing OpenAPI specs, Postman collections, HAR recordings, Burp exports, additional context, previous pentest reports
- Can target multiple assets in one engagement
- Can be launched via public API and MCP, bypassing the UI
- Supports both black-box (no source access) and white-box (with source access) testing modes

## Numbers & metrics mentioned
- "Jun 4, 2026" — publish date
- "15 min read"
- "a second account typically uncovers 30–50% more issues" (multi-user testing benefit)
- Juice Shop benchmark: Cascade black-box total 36 (High 20, Medium 15, Low 1); Cascade white-box total 49 (High 31, Medium 17, Low 1); Claude Code best-result/black-box total 22 (High 11, Medium 7, Low 4); Claude Code white-box total 22 (High 13, Medium 6, Low 3)
- "Cascade detected 49 vulnerabilities in white-box mode: more than 2x the findings of Claude Code (22)"
- "Even in black-box mode, Cascade (36) outperforms Claude Code's best result"
- Fider benchmark: Cascade black-box total 20 (High 4, Medium 11, Low 5); Cascade white-box (best result) total 27 (High 4, Medium 12, Low 11); Aikido white-box total 17 (High 3, Medium 6, Low 8); Xbow white-box total 18 (High 3, Medium 7, Low 8); Claude Code white-box total 7 (High 1, Medium 3, Low 3)
- "On Fider ... finding 20-27 total vulnerabilities"
- Photoview benchmark: Cascade black-box total 12 (High 7, Medium 2, Low 3); Cascade white-box (best result) total 28 (High 7, Medium 9, Low 12); Aikido white-box total 24 (High 6, Medium 9, Low 9); Xbow white-box total 5 (High 2, Medium 2, Low 1); Claude Code white-box total 7 (High 2, Medium 1, Low 4)
- "Cascade (white-box) tops all solutions with 28 findings"
- "On Fider, the gap between black-box and white-box is low (15 vs. 16 HIGH+MEDIUM)"
- "On Photoview, white-box mode unlocks a significant uplift (12 → 28)"
- Example vulnerability: normal product price "€22.99"
- Example vulnerability: submitted quantity "-50" causing negative pricing, service returned "201 Created"
- "We'll provide the complete benchmark in a week"

## People named
- Alexandra Charikova — co-author (byline), role not otherwise specified
- Antoine Carossio — co-author (byline); also appears as author on other linked blog posts on the page
- Hugo Pucéat — co-author (byline)
- Quoted customer: "Team Lead, Offensive Security, global payments & fintech platform" (name not given, role/title only)
- Sanjana Iyer — author credit appearing in a related-posts section image (not part of this article's byline)

## Media found
- https://escape.tech/blog/content/images/2026/03/White--1-.png — Escape logo ("Escape - Application Security & Offensive Security Blog"), site header logo
- /blog/content/images/size/w100/2026/06/alexandra-photo.png — author profile photo, alt "Alexandra Charikova"
- /blog/content/images/size/w100/2026/03/1771951542692.png — author profile photo, alt "Antoine Carossio"
- /blog/content/images/size/w100/2026/06/1600001496898.jpeg — author profile photo, alt "Hugo Pucéat"
- /blog/content/images/size/w2000/2026/06/introducing-cascade-1.png (srcset up to 2000w) — hero/featured image, alt matches article title (this is also the og:image)
- https://escape.tech/blog/content/images/2026/06/cascade-architecture-v3--1-.png — diagram, likely "Cascade architecture" illustration (kg-image, in-article)
- https://escape.tech/blog/content/images/2026/06/price-manip-screen.png — screenshot, likely of the price-manipulation vulnerability example described in the case study
- /blog/content/images/size/w600/2026/09/External-penetration-testing--1---1-.svg — related-post card image, alt "What an External Penetration Test is And How One is Actually Run" (SVG illustration, not part of this article body)
- /blog/content/images/size/w100/2026/03/1771951542692.png — author profile photo (Antoine Carossio), reused in related-posts section
- /blog/content/images/size/w600/2026/07/Top-continuous-pentesting-tools.svg — related-post card image, alt "Top continuous penetration testing tools with expert review" (not part of this article body)
- /blog/content/images/size/w100/2024/11/me.jpeg — author profile photo, alt "Sanjana Iyer" (related-posts section, not this article's author)
- /blog/content/images/size/w600/2026/06/ai-pentesting-tools-benchmark.png — related-post card image, alt "Modern AI-powered Pentesting Tools In-Depth benchmark" (not part of this article body)
- https://px.ads.linkedin.com/collect/?pid=5420812&fmt=gif — 1x1 LinkedIn ads tracking pixel (not content)
- iframe: https://www.googletagmanager.com/ns.html?id=GTM-MDMBJH6V — Google Tag Manager noscript iframe (not content)
- No YouTube/Vimeo/Wistia video embeds were found on the page. The two chart images referenced in text ("AI pentesting benchmark on Juice Shop", "on Fider: Cascade vs. Aikido, Xbow & Claude Code", "on Photoview: Cascade vs. Aikido, Xbow & Claude Code") appear to be rendered as data tables/charts in the live page but their image src could not be isolated from the fetched HTML with certainty.

## Source
https://escape.tech/blog/introducing-cascade-the-multi-agent-penetration-testing/
