---
url: https://xbow.com/blog/top-1-how-xbow-did-it
category: research
title: The Road to Top 1: How XBOW Did It
---

# The Road to Top 1: How XBOW Did It

> Note: the HTML `<title>` tag for this page is "How XBOW Ranked #1 in Autonomous Penetration Testing | XBOW"; the on-page H1 heading is "The Road to Top 1: How XBOW Did It". Meta description: "Learn how XBOW achieved #1 performance in autonomous penetration testing by validating real exploits and outperforming human pentesters in speed and accuracy." Published: June 24, 2025 (dateTime 2025-06-24T12:00:00.000Z). Blog category tag on page: "Company News".

## Summary
This XBOW company blog post explains how their fully autonomous AI penetration-testing agent reached the #1 spot on HackerOne's US bug-bounty leaderboard — the first time an autonomous pentester has done so. It walks through XBOW's benchmarking history (CTF challenges → custom real-world benchmark → open-source zero-day discovery → live black-box bug bounty programs), the infrastructure they built to scope and prioritize hundreds of thousands of HackerOne targets, their "validator" system for confirming vulnerabilities and cutting false positives, and detailed results/statistics from running XBOW across public and private bug bounty programs. It closes with a teaser of upcoming technical write-ups and a pitch for XBOW as an enterprise product.

## Full content

### (Intro)
For the first time in bug bounty history, an autonomous penetration tester has reached the top spot on the US leaderboard.

Our path to reaching the top ranks on HackerOne began with rigorous benchmarking. Since the early days of XBOW, we understood how crucial it was to measure our progress, and we did that in two stages:

- First we tested XBOW with existing CTF challenges (from well-known providers like PortSwigger and Pentesterlab), then quickly moved on and built our own unique benchmark that simulates real-world scenarios—ones never used to train LLMs before. The results were encouraging, but still these were artificial exercises.
- The logical next step, therefore, was to focus on discovering zero-day vulnerabilities in open source projects, which led to many exciting findings. Some of these were reported on this blog before: in every case, we gave the AI access to source code, simulating a white-box pentest. While our paying customers were enthusiastic about XBOW's capabilities, the community raised a key question: How would XBOW perform in real, black-box production environments? We took up that challenge, choosing to compete in one of the largest hacker arenas, where companies serve as the ultimate judges by verifying and triaging vulnerabilities themselves.

### Dogfooding AI in Bug Bounties
XBOW is a fully autonomous AI-driven penetration tester. It requires no human input, operates much like a human pentester, but can scale rapidly, completing comprehensive penetration tests in just a few hours.

When building AI software, having precise benchmarks to keep pushing the limit of what's possible, is essential. But when some of those benchmarks evolve into real-world environments, it's a developer's dream come true.

Discovering bugs in structured benchmarks and open source projects was a fantastic starting point. However, nothing can truly prepare you for the immense diversity of real-world environments, which span from cutting-edge technologies to 30-year-old legacy systems. No number of design partners can offer that breadth of system variety as that level of unpredictability is nearly impossible to simulate.

To bridge that gap, we started dogfooding XBOW in public and private bug bounty programs hosted on HackerOne. We treated it like any external researcher would: no shortcuts, no internal knowledge—just XBOW, running on its own.

HackerOne offers this unique opportunity, and as XBOW discovered and reported vulnerabilities across multiple programs, we soon found ourselves climbing the H1 ranks.

### Scaling Discovery and Scoping capabilities
Our first challenge was scaling. While XBOW can easily scan thousands of web apps simultaneously, HackerOne hosts hundreds of thousands of potential targets. As a startup with limited resources, even when we focused on specific vulnerability classes, we still needed to be strategic. That's why we built infrastructure on top of XBOW to help us identify the high-value targets and prioritize those that would maximize our return on investment.

We started by consuming bug bounty program scopes and policies, but this information isn't always machine-readable. With a combination of large language models and some manual curation, we managed to parse through them—with a few hiccups. (At one point, we were officially removed from a program that didn't allow "automatic scanners.")

With the domains ingested into our database, and a bit of "magic" to expand subdomains, we built a scoring system to highlight the most interesting targets. This scoring criteria covered a broad range of signals, including target appearance, presence of WAFs and other protections, HTTP status codes, redirect behavior, authentication forms, number of reachable endpoints, underlying technologies, and more.

Domain deduplication quickly became essential in large programs, it is common to encounter cloned or staging environments (e.g. stage0001-dev.example.com). Once a vulnerability is found in one, similar issues are likely to exist across others. To stay efficient, we used SimHash to detect content-level similarity and leveraged a headless browser to capture website screenshots and then applied imagehash techniques to assess visual similarity analysis, allowing us to group assets and focus our efforts on unique, high-impact targets.

### Automated Vulnerability Discovery
AI can be remarkably effective at discovering a broad range of vulnerabilities—but the real challenge isn't always detection, it's precision. Automation has long struggled with false positives, and nowhere is this more evident than in vulnerability scanning. Tools that flag dozens of irrelevant issues often create more work than they save. When AI enters the equation, the stakes grow even higher: models can generalize well, but verifying technical edge cases is a different game entirely.

To ensure accuracy, we developed the concept of validators, automated peer reviewers that confirm each vulnerability XBOW uncovers. Sometimes this process leverages a large language model; in other cases, we build custom programmatic checks. For example, to validate Cross-Site Scripting findings, a headless browser visits the target site to verify that the JavaScript payload was truly executed. (don't miss Brendan Dolan-Gavitt's BlackHat presentation on AI agents for Offsec)

### XBOW's Real-World Impact
Running XBOW across a wide range of public and private programs yielded results that exceeded our expectations—not just in volume, but in consistency and quality.

Over time, XBOW reported thousands of validated vulnerabilities, many of them affecting high-profile targets from well-known companies. These findings weren't just theoretical; every submission was confirmed by the program owners and triaged as real, actionable security issues.

The most public signal of progress came from the HackerOne leaderboard. Competing alongside thousands of human researchers, XBOW climbed to the top position in the US ranking. That wasn't our original goal, and indeed was surprising since we didn't have a buffer of untriaged reports from previous quarters—but it became a useful benchmark to track real-world performance and collect traces to reinforce our models.

XBOW submitted nearly 1,060 vulnerabilities. All findings were fully automated, though our security team reviewed them pre-submission to comply with HackerOne's policy on automated tools. It was a unique privilege to wake up each morning and review creative new exploits.

To date, bug bounty programs have resolved 130 vulnerabilities, while 303 were classified as Triaged (mostly by VDP programs that acknowledged the issue but did not proceed to resolution). In addition, 33 reports are currently marked as new, and 125 remain pending review by program owners.

Across all submissions, 208 were marked as duplicates, 209 as informative and 36 as not applicable (most of them self-closed by our team). Interestingly, many of these informative vulnerabilities came from programs with specific constraints such as policies excluding third-party vulnerabilities or disallowing certain classes like Cache Poisoning.

XBOW identified a full spectrum of vulnerabilities including: Remote Code Execution, SQL Injection, XML External Entities (XXE), Path Traversal, Server-Side Request Forgery (SSRF), Cross-Site Scripting, Information Disclosures, Cache Poisoning, Secret exposure, and more.

Over the past 90 days alone, the vulnerabilities submitted were classified as 54 critical, 242 high, 524 medium, and 65 low severity issues by program owners. Notably, around 45% of XBOW's findings are still awaiting resolution, highlighting the volume and impact of the submissions across live targets.

XBOW's path to the top involved uncovering a wide range of interesting and impactful vulnerabilities. Among them was a previously unknown vulnerability in Palo Alto's GlobalProtect VPN solution, affecting over 2,000 hosts. Throughout this process, XBOW consistently demonstrated its ability to adapt to edge cases and develop creative strategies for complex exploitation scenarios entirely on its own.

In the spirit of transparency, and in accordance with the rules and regulations of POC || GTFO, our security team will be publishing a series of blog posts over the coming weeks, showcasing some of our favorite technical discoveries by XBOW.

XBOW is an enterprise solution. If your company would like a demo, email us at info@xbow.com.

### Related Posts (linked, not part of this article's body)
- Blackhat 2026: Hacking the Past. Hacking the Future. (dated August 14, 2026)
- GPT-5.5: Democratizing Cyber Capabilities (dated April 23, 2026)
- Taking the Top Autonomous Hacker in the US to New Heights: XBOW Raises $75M Series B (dated March 20, 2026)

## Features / claims mentioned
- XBOW is a "fully autonomous AI-driven penetration tester" requiring no human input.
- Operates like a human pentester but scales rapidly — completes comprehensive penetration tests "in just a few hours."
- First autonomous penetration tester to reach #1 on HackerOne's US leaderboard.
- Benchmarking progression: CTF challenges (PortSwigger, Pentesterlab) → custom real-world benchmark (novel scenarios not used to train LLMs) → zero-day discovery in open-source projects (white-box, source-code access) → live black-box bug bounty programs (no internal knowledge, treated like an external researcher).
- Can "easily scan thousands of web apps simultaneously."
- Built custom infrastructure on top of XBOW to identify and prioritize high-value targets across HackerOne's hundreds of thousands of potential targets.
- Used LLMs plus manual curation to parse bug bounty program scopes/policies (not always machine-readable).
- Built a target scoring system based on: target appearance, presence of WAFs/protections, HTTP status codes, redirect behavior, authentication forms, number of reachable endpoints, underlying technologies, and more.
- Domain deduplication using SimHash (content-level similarity) and a headless browser + imagehash techniques (visual similarity) to group cloned/staging assets and avoid duplicate effort.
- "Validators" — automated peer reviewers (sometimes LLM-based, sometimes custom programmatic checks) confirm each vulnerability before reporting, reducing false positives. Example given: headless-browser verification that an XSS JavaScript payload actually executed.
- All findings fully automated; XBOW's internal security team reviewed submissions pre-submission only to comply with HackerOne's policy on automated tools.
- Discovered a previously unknown vulnerability in Palo Alto's GlobalProtect VPN affecting 2,000+ hosts.
- Was once removed from a bug bounty program that disallowed "automatic scanners."
- XBOW is positioned/sold as an enterprise solution (demo available via email).
- Company states it will publish further technical write-ups of specific findings on its blog, "in accordance with the rules and regulations of POC || GTFO."

## Numbers & metrics mentioned
- "nearly 1,060" vulnerabilities submitted by XBOW
- 130 vulnerabilities resolved by bug bounty programs (to date)
- 303 vulnerabilities classified as "Triaged"
- 33 reports currently marked as "new"
- 125 reports pending review by program owners
- 208 submissions marked as duplicates
- 209 submissions marked as informative
- 36 submissions marked as not applicable
- Past 90 days severity breakdown: 54 critical, 242 high, 524 medium, 65 low severity issues
- "around 45%" of XBOW's findings still awaiting resolution
- 1 vulnerability in Palo Alto GlobalProtect VPN affecting "over 2,000 hosts"
- Publish date of this article: June 24, 2025
- Related post: XBOW raised a "$75M Series B" (title of a linked related post, dated March 20, 2026 — not detailed in this article's body)
- Related post dated August 14, 2026 (Blackhat 2026 post)
- Related post dated April 23, 2026 (GPT-5.5 post)

## People named
- Nico Waisman — CISO @ XBOW (listed as article author; author profile link `/authors/nico-waisman`)
- Brendan Dolan-Gavitt — mentioned re: a BlackHat presentation on "AI agents for Offsec" (role not stated on this page)

## Media found
- `https://cdn.sanity.io/images/1lq2ca9s/production/0d0837b1e61bfeff9caa47e3ca4511bd63f658a9-1920x1465.png` (served via `/_next/image`) — alt: "The Road to Top 1: How XBOW Did It" (hero/header image for the article)
- `https://cdn.sanity.io/images/1lq2ca9s/production/f1f75325b5673b9049e6b3b56e9cca05fce514b9-1000x515.jpg` — alt: "Autonomous penetration tester has reached the top spot on the US leaderboard." (in-article illustration, likely leaderboard-related graphic)
- `https://cdn.sanity.io/images/1lq2ca9s/production/a733aec7f24b8f87b94b479138325b9541f061ac-1000x722.jpg` — alt: "Every submission was confirmed by the program owners and triaged as real, actionable security issues" (chart/screenshot)
- `https://cdn.sanity.io/images/1lq2ca9s/production/c1a3afc2a9722833920fd470df4df2bebf0f87ac-1000x829.jpg` — alt: "33 reports are currently marked as new, and 125 remain pending review by program owners." (chart/screenshot of report status breakdown)
- `https://cdn.sanity.io/images/1lq2ca9s/production/b92cc5a75b6989cea44bd4b734880c5e5100c8a1-1000x829.jpg` — alt: "Vulnerabilities submitted were classified as 54 critical, 242 high, 524 medium, and 65 low severity issues" (chart/screenshot of severity breakdown)
- `https://cdn.sanity.io/images/1lq2ca9s/production/8a68e84a3c108c84044506943868f88feb6cfac2-320x320.jpg` — alt: "Nico Waisman" (author headshot)
- `https://cdn.sanity.io/images/1lq2ca9s/production/d8db267b4e6327913da9b0d6292c0bafbb7527ef-1920x1465.png` — alt: "Black Hat 2026: Hacking the Past, Hacking the Future" (related-post thumbnail)
- `https://cdn.sanity.io/images/1lq2ca9s/production/a139aacf7188c411eb43f40b4e9811ad113c218a-1920x1465.png` — alt: "GPT-5.5: Democratizing Cyber Capabilities" (related-post thumbnail)
- `https://cdn.sanity.io/images/1lq2ca9s/production/1a05f218f124ec330c78f311c993fbc725c7860f-1920x1465.png` — alt: "Taking the Top Hacker in the US to New Heights: XBOW Raises $75M Series B" (related-post thumbnail)
- `/assets/footer-light.svg`, `/assets/footer-dark.svg`, `/assets/footer.svg` — no alt text (site footer logo/wordmark, theme variants)
- og:image (social share image): `https://cdn.sanity.io/images/1lq2ca9s/production/434ec9c09c98a9451547cb0f6709d58a29059835-1920x1080.jpg`
- No `<video>`, `<iframe>`, or embedded YouTube/Vimeo/Wistia content found on the page.

## Source
https://xbow.com/blog/top-1-how-xbow-did-it
