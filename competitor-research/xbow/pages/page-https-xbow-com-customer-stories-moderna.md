---
url: https://xbow.com/customer-stories/moderna
category: case_study
title: How Moderna Scales Offensive Security with XBOW | XBOW
---

# How Moderna Scales Offensive Security with XBOW | XBOW

## Summary
This XBOW customer-story page (published June 20, 2026) profiles Moderna's Deputy CISO, Farzan Karimi, and how his team adopted XBOW's autonomous pentesting to cover Moderna's fast-growing application surface. It centers on a proof-of-concept where XBOW found a WAF bypass (a URL percent-encoding trick) that Farzan himself had missed, then walks through a multi-stage attack chain XBOW built across ~30-40 internal Moderna apps, and closes on how exploit-proof evidence changed Moderna's remediation prioritization and let the human red team focus on higher-judgment work.

## Full content

### Background
When Farzan Karimi became Deputy CISO at Moderna, he inherited responsibility for one of the most complex security environments in biotech, and a clear-eyed view of what his team could and couldn't cover on their own.

Farzan has spent 20 years in offensive security, running red teams for large organizations. He still pentests on weekends because he genuinely enjoys it. That background shaped how he approached Moderna's security program from day one: not just managing risk, but thinking like an attacker across every domain, from manufacturing to enterprise to customer-facing applications.

Moderna operates in an industry where the consequences of a breach extend well beyond data loss. Their environment spans manufacturing systems that run around the clock, enterprise infrastructure, and a growing catalog of custom applications built by scientists and engineers who move fast. A breach anywhere in that stack, from a dev environment, to a custom dashboard, or a production app, is not just a security incident. At Moderna, it can mean compromised research, disrupted manufacturing, or patient data at risk.

Moderna's security program is mature and well-resourced, covering network security, cloud security, AI security, code security, and pentesting. What Farzan saw was not a gap in the program. It was a math problem. The environment was growing faster than any team, no matter how skilled, could manually keep up with.

> "XBOW identified a WAF bypass through a URL encoding trick that I missed during my own review. It found it right away. That was the moment that led us to choose XBOW as a partner."
> — Farzan Karimi, Deputy CISO at Moderna

### Challenge
The pace of development was the core pressure. Engineers and scientists were building and publishing custom applications faster than any manual review process could track. A scientist might build a dashboard to capture sensitive research data, share it with a colleague, and depending on which AI tool handled the request, accidentally expose it to the internet. Farzan described exactly this kind of scenario as something the industry was already seeing. In Moderna's environment, with the data they handle, that kind of exposure is not a minor incident.

Even with a strong team in place, penetration testing is periodic by nature. You scope an engagement, you test for a few days, you write a report, and by the time the report is done, the application has already changed. Skilled testers have limited time on any given engagement, and limited time means limited coverage. A senior pentester running a test on a Wednesday, trying to finish by Friday, does not bring the same attention to every endpoint they would with unlimited time. Farzan had experienced this firsthand, having run these tests himself.

The other pressure was prioritization. Findings came in from three directions: internal risk assessments, external bug bounty submissions, and manual pentests. Most were ranked by CVSS score. A 9.2 is critical, fix it. But when thousands of findings are competing for the same limited developer time, a CVSS score alone tells you nothing about where to actually start. The queue was full, but the signal was weak.

What the team needed was a way to test more of the environment more often, at a quality bar that matched how a real attacker thinks, without depending entirely on human availability to get there.

### Why XBOW
Farzan ran the proof of concept the way any serious practitioner would: he pointed XBOW at an application he had already personally tested. Not a simple one. His worst publicly facing custom application, the one he knew best, the one he had already found vulnerabilities in. If XBOW was going to earn a place in their program, it needed to find something he had not.

The application ran behind a web application firewall. Farzan had tested it, found vulnerabilities, and those vulnerabilities had been patched. The WAF was holding. XBOW found a gap he had missed entirely.

The application used Spring Boot, a framework that exposes debugging endpoints and environment variables that are useful for developers, but dangerous if exposed to the internet. Farzan had tested the actuator endpoint. The WAF blocked it. He moved on. XBOW did not. It tried the same request with one small change: it replaced the letter "a" in the URL with its percent-encoded equivalent, %61. The WAF read it as a routine request and let it through. What came back was a full dump of the environment, including API keys, MongoDB credentials, and connection strings. Everything a real attacker would need to turn an initial foothold into something far worse.

That finding mattered for two reasons. The obvious one is the vulnerability itself, a real exposure that would have been serious in the hands of an attacker. The less obvious one is what it revealed about how XBOW works. It was not running a checklist. It was reasoning about how a WAF interprets requests, finding the gap between what the firewall expected and what the application actually received, and exploiting that gap the way a real attacker would.

The WAF bypass was what closed the deal. But it also pointed toward something Farzan cared about even more than individual findings: the connections between them. Most tools hand you a list of bugs. What Farzan wanted to know was which bugs were connected, because connected bugs become attack chains, and attack chains are how real attackers operate.

### What a Real Attack Chain Looks Like
To understand what exploit chaining looks like in practice, it helps to walk through what XBOW did with a cluster of Moderna's internal applications.

The target was an external-facing ordering application, the only public entry point into a tightly coupled ecosystem of roughly 30 to 40 internal apps, including routing, authentication, and inventory systems. XBOW was given source code but no login credentials. The instruction was simple: here is the application, go find what you can find.

The first thing XBOW did was search the source code for API keys. It found one: a valid key belonging to a user whose credentials had not been rotated. It used the key to authenticate, then began probing the APIs. One of them handled malformed SQL input in an unexpected way. Rather than failing cleanly, the bad input started cascading into the Gateway application, the routing layer that handled authentication for every other app in the cluster. Containers started throwing errors. The ordering app went down. Then the inventory app. Then everything else. The entire dev environment went offline.

XBOW had also confirmed the IDOR vulnerability Farzan suspected was there: a logged-in user could access the order history of any other user, with no special access required. Human pentesters who reviewed the findings afterward confirmed the same attack chain could have compromised confidentiality as well as availability, not just taken the system down, but exposed data in the process.

The whole chain ran in under 18 hours. For context, developing an equivalent multi-stage attack chain manually can take anywhere from days to months depending on the target. On complex systems, where exploit primitives need to be built from scratch and stability validated across multiple components, months of work is realistic. Farzan's team had seen exactly that at prior organizations. XBOW compressed that timeline to less than a day.

Farzan's reaction was not alarm, it was relief. Finding an outage safely in a test environment is exactly what you want, because it means a real threat actor did not find it first.

### From Noise to Signal
Finding a WAF bypass and building a full attack chain are the headline moments. But what changed day to day at Moderna was something more practical: how the team decides what to fix.

Before XBOW, the vulnerability queue was a volume problem. Findings piled up from bug bounty submissions, risk assessments, and periodic manual tests, all ranked by CVSS score, all competing for the same limited developer time. The team was not ignoring the queue. They just had no reliable way to know which items in it reflected real, exploitable risk versus theoretical exposure. As Farzan described it, you can have a hundred 9.2s in your environment and a CVSS score alone tells you nothing about which one to fix first.

XBOW changed that by attaching an exploit proof to every finding. Not a theoretical vulnerability, but reproducible, demonstrated evidence with a working proof of concept attached. A developer looking at an XBOW finding knows exactly how the vulnerability would be reached, what an attacker would do with it, and why it matters more than the other items on their list.

> "Before XBOW, we had a huge volume of findings which made remediation difficult. With XBOW, every finding comes with an exploit proof. That tells us exactly what to fix first."

That clarity collapses the distance between finding and fix, and it changed how Moderna thinks about remediation. The issues identified as part of the attack chain were resolved within 24 hours of discovery.

The exploit proof made the combined impact of the three vulnerabilities clear enough that the development team did not need to debate prioritization. They could see exactly what was at risk and act on it. With higher quality findings coming in at higher volume, the team is now building out a remediation pipeline to match, including exploring remediation agents that can accelerate how fast validated vulnerabilities get resolved.

### A Program Built to Scale
The result is a security program that operates at a different pace than it did before. XBOW handles application security testing across Moderna's portfolio, running parallel pentests at a consistent quality bar, on demand, without scheduling or coordination overhead. That frees Farzan's team to focus on the work that requires human judgment: network environments, complex integrations, applications with logic flows that benefit from a practitioner's experience and context.

For Farzan, the shift is concrete. He can still pentest on Friday nights, but now he is working on the applications that actually warrant his full attention, not trying to stretch coverage across an entire portfolio by hand. His human red team can go deep on the areas where depth matters most, because XBOW is covering everything else.

> "I have given all the applications to XBOW to review. Now I can point my red team to focus on the network environment and be laser focused on the complicated nuances without having to be distracted by web. That gives me peace of mind."

### Other page elements
- A "Download the Moderna Customer Story PDF" call-to-action links to a PDF version of this story: https://cdn.sanity.io/files/1lq2ca9s/production/4e7971623620c4a291fb81001dde180bb0206e77.pdf
- A "Table of contents" sidebar links to each section: Background, Challenge, Why XBOW, What a Real Attack Chain Looks Like, From Noise to Signal, A Program Built to Scale
- A "Related Resources" module at the bottom links to three other customer stories: "Security Testing at Superhuman Speed" (Aug 27, 2026), "How Rogo Closed the Gap Between Daily Releases and Twice-a-Year Pentests" (Jul 16, 2026), "How Lumios Got a Compliance-Ready Pentest Without the Wait" (Jul 9, 2026)
- Standard site navigation (Platform, Pricing, Resources, Blog, Company, Get a Demo) and footer (Sitemap: Platform, Pricing, API, Resources, About, Partner Deal Registration, AI Pentesting Hub, Documentation, Careers; Legal: Terms of Use, Terms and Conditions, Privacy Policy, Trust Center, Cookies Policy; Connect: Bluesky, X, LinkedIn, Mastodon; copyright "© 2026 XBOW USA Inc.")

## Features / claims mentioned
- XBOW autonomously found a WAF (web application firewall) bypass via a URL percent-encoding trick (`a` → `%61`) that a 20-year offensive-security veteran had personally missed.
- XBOW reasons about how a WAF interprets requests rather than running a fixed checklist, finding gaps between what a firewall expects and what the application actually receives.
- XBOW can be run against source code with no login credentials and autonomously discover and use exposed API keys to authenticate.
- XBOW builds multi-step "attack chains" linking discrete findings together, rather than reporting a flat list of isolated bugs.
- XBOW confirmed an IDOR (Insecure Direct Object Reference) vulnerability allowing any logged-in user to view any other user's order history.
- XBOW attaches a reproducible "exploit proof" / working proof-of-concept to every finding, rather than a theoretical CVSS-scored description.
- XBOW runs "parallel pentests" across an entire application portfolio "on demand," without scheduling or coordination overhead, enabling continuous rather than periodic testing.
- Positioned as complementary to human red teams: XBOW covers breadth (web apps at scale) so human testers can focus on depth (network environments, complex integrations, business-logic flows).
- Moderna is described as exploring "remediation agents" to further accelerate fixing validated vulnerabilities (forward-looking, not yet an established XBOW product claim on this page).

## Numbers & metrics mentioned
- "20 years" — Farzan Karimi's tenure in offensive security / running red teams
- "roughly 30 to 40 internal apps" — size of the internal application ecosystem behind Moderna's ordering app (routing, authentication, inventory systems)
- "under 18 hours" — time for XBOW to run the full multi-stage attack chain
- "days to months" — typical manual time to develop an equivalent multi-stage attack chain by hand
- "a hundred 9.2s" — illustrative example Farzan gives of CVSS-score volume without prioritization signal
- "within 24 hours of discovery" — time to resolve the issues identified as part of the attack chain
- "%61" — the percent-encoded character used in the WAF-bypass exploit (encoded form of the letter "a")
- "June 20, 2026" — publish date of this customer story
- Related-story publish dates referenced in the "Related Resources" module: "August 27, 2026" (Superhuman), "July 16, 2026" (Rogo), "July 9, 2026" (Lumios)
- Copyright year: "© 2026 XBOW USA Inc."

## People named
- Farzan Karimi — Deputy CISO at Moderna (subject of the case study; quoted three times)

## Media found
- https://cdn.sanity.io/images/1lq2ca9s/production/db29c6691824acaffda7688d2aad393542769501-230x53.svg — hero/header image; alt text is the full story title "From WAF Bypass to Full Attack Chain: How Moderna Tests Like a Real Attacker" (appears to be a title/logo graphic, rendered monochrome via CSS grayscale filter)
- https://cdn.sanity.io/images/1lq2ca9s/production/109b4a14180f8ebcde6930a7acac78868663e21b-2001x287.png — related-story card thumbnail, alt "Sperhuman" [sic, likely "Superhuman"], for the Superhuman customer story
- https://cdn.sanity.io/images/1lq2ca9s/production/35a753e426d91b61cbef7bd59f9fdbc4d5a41b58-1000x385.png — related-story card thumbnail, alt is the full Rogo story title, for the Rogo customer story
- https://cdn.sanity.io/images/1lq2ca9s/production/942d6d8f04f31ea835db6c4b3a8d0642097f8d07-1000x1000.png — related-story card thumbnail, alt "Lumios", for the Lumios customer story
- /assets/footer-light.svg, /assets/footer-dark.svg, /assets/footer.svg — decorative footer background graphics (theme variants), no alt text
- og:image (social share card, dynamically generated): https://xbow.com/api/og?contentType=Customer+Story&title=From+WAF+Bypass+to+Full+Attack+Chain%3A+How+Moderna+Tests+Like+a+Real+Attacker&date=June+20%2C+2026
- PDF asset (linked, not embedded media): https://cdn.sanity.io/files/1lq2ca9s/production/4e7971623620c4a291fb81001dde180bb0206e77.pdf — downloadable "Moderna Customer Story" PDF
- No `<video>`, `<iframe>`, or YouTube/Vimeo/Wistia embed URLs were found anywhere in the page's HTML.

## Source
https://xbow.com/customer-stories/moderna
