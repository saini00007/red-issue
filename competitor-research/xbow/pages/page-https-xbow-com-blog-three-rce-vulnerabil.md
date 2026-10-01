---
url: https://xbow.com/blog/three-rce-vulnerabilities-in-microsoft-identified-xbow
category: research
title: Three Critical RCE Vulnerabilities in Microsoft Software Identified Autonomously by XBOW
---
# Three Critical RCE Vulnerabilities in Microsoft Software Identified Autonomously by XBOW

## Summary
XBOW's autonomous AI offensive security platform was credited in the March 2026 Microsoft Patch Tuesday release with discovering three critical remote code execution (RCE) vulnerabilities in Microsoft Cloud products — the first time, per the post, that an autonomous AI has found critical vulnerabilities in Microsoft Cloud without source code access. The post (dated April 2, 2026, tagged "Security Research") frames this as a milestone showing AI-driven pentesting can now accelerate real-world exploit discovery at a pace that rivals or exceeds experienced human researchers, cites press coverage from TechRepublic and Krebs on Security, and thanks the Microsoft security team (MSRC) for its coordinated disclosure process. No technical details of the vulnerabilities are shared, out of respect for Microsoft's request to protect customers until the risk window has passed.

## Full content

**Blog / Security Research**

### Three Critical RCE Vulnerabilities in Microsoft Software Identified Autonomously by XBOW
Security Research · April 2, 2026

For the first time, autonomous AI uncovered critical RCE vulnerabilities in Microsoft Cloud, demonstrating how AI-driven pentesting is accelerating real-world exploit discovery.

On the offensive side of security, Tuesdays were always an exciting time for researchers: the moment Microsoft would release its patches, and part of my work, or a colleague's, would finally become public. Sometimes after months of waiting. It was, in large measure, a way to gauge the state of the art in exploitation.

This month's Patch Tuesday was different.

For the very first time in history, an autonomous AI found critical vulnerabilities in Microsoft Cloud. Not simple bugs in isolated products, but complex vulnerabilities in large-scale production systems, found without source code access. The kind of findings that take experienced researchers weeks to develop.

This is exactly the kind of result the XBOW autonomous offensive security platform is built to deliver: identifying deep, non-obvious security weaknesses in real-world environments, with real impact and real CVEs, at a speed never seen before.

XBOW was credited in the March 2026 Patch Tuesday release with CVE-2026-21536, a critical remote code execution vulnerability in the Microsoft Devices Pricing Program, flagged as one of the most severe issues in the release. Two more followed: CVE-2026-32194 and CVE-2026-32191, both critical RCEs in Bing with potential for SYSTEM-level privileges.

It's no secret that attackers are already leveraging AI. Defenders now need to move just as fast. The industry is noticing. Journalist Aminu Abdullahi wrote in TechRepublic that the findings mark a shift in the arms race between researchers and hackers, as AI can now find complex software vulnerabilities entirely on its own. Ben McCarthy, lead cybersecurity engineer at Immersive, told Krebs on Security that while Microsoft has already patched the issues, the real signal is the speed: AI-driven discovery of complex vulnerabilities is accelerating, and it's not going away.

We want to thank the Microsoft security team, who handled these issues the way a security-mature organization should. The MSRC has continued to emphasize protecting customers through clear security testing rules of engagement, coordinated vulnerability disclosure, and transparent guidance. With these recent findings, the company moved quickly to investigate and remediate.

As is often the case with serious vulnerabilities, we are not sharing technical details at this time. That was the right call for customer protection, and we respect Microsoft's request to keep those specifics private until the risk window is fully behind us. We hope to share more about the research in the future.

**Tags:** Vulnerability Research, Vulnerability Disclosure, Remote Code Execution, Microsoft Security, Application Security

**Author:** Nico Waisman — CISO @ XBOW (LinkedIn: https://ar.linkedin.com/in/nwaisman, X: https://x.com/nicowaisman, GitHub: https://github.com/nicowaisman)

**Related Posts (sidebar, not this article's own content):**
- Security Research — August 17, 2026 — "The European Central Bank Just Made Autonomous Offensive Security a Board-Level Problem" — Julian Totzek-Hallhuber
- Security Research — July 23, 2026 — "A Shell Is Worth a Thousand Images: Bing Images RCEs" — Nico Waisman
- Security Research — June 9, 2026 — "How CISOs Can Close the AI Security Gap Before It Widens: A Practical Framework" — Suzanne Ciccone

## Features / claims mentioned
- XBOW is described as an "autonomous offensive security platform" built to identify "deep, non-obvious security weaknesses in real-world environments, with real impact and real CVEs, at a speed never seen before."
- Claimed to be the first time in history an autonomous AI found critical vulnerabilities in Microsoft Cloud.
- Vulnerabilities found were "complex vulnerabilities in large-scale production systems, found without source code access" — described as "the kind of findings that take experienced researchers weeks to develop."
- Positioned as evidence that "AI-driven pentesting is accelerating real-world exploit discovery."
- Frames the broader narrative as an "arms race" where attackers already leverage AI and "defenders now need to move just as fast."
- Credits Microsoft's MSRC for handling disclosure "the way a security-mature organization should," citing "clear security testing rules of engagement, coordinated vulnerability disclosure, and transparent guidance."
- States XBOW is deliberately withholding technical details out of respect for Microsoft's request, "until the risk window is fully behind us," with a promise to "share more about the research in the future."

## Numbers & metrics mentioned
- "CVE-2026-21536" — critical RCE vulnerability in the Microsoft Devices Pricing Program, flagged as "one of the most severe issues in the release."
- "CVE-2026-32194" and "CVE-2026-32191" — two additional critical RCEs in Bing, both with "potential for SYSTEM-level privileges."
- "March 2026 Patch Tuesday release" — the disclosure event referenced.
- "April 2, 2026" — publication date of this blog post.
- Three total critical RCE vulnerabilities credited to XBOW in this cycle (per the post title and body).

## People named
- **Nico Waisman** — CISO @ XBOW (author of this post; also credited as author of the related post "A Shell Is Worth a Thousand Images: Bing Images RCEs")
- **Aminu Abdullahi** — journalist, TechRepublic (quoted/cited commentary on the findings)
- **Ben McCarthy** — Lead Cybersecurity Engineer at Immersive (quoted in Krebs on Security)

People named only in "Related Posts" sidebar (not part of this article's content): Julian Totzek-Hallhuber, Suzanne Ciccone.

## Media found
- Image: `https://cdn.sanity.io/images/1lq2ca9s/production/0b36143a7660e6497db2c8f1b7b2f6d2ba800676-1920x1465.png` (served via `/_next/image` proxy) — alt: "Three Critical RCE Vulnerabilities in Microsoft Software Identified Autonomously by XBOW" — hero/header image for this article.
- Image: `https://cdn.sanity.io/images/1lq2ca9s/production/8a68e84a3c108c84044506943868f88feb6cfac2-320x320.jpg` — alt: "Nico Waisman" — author headshot.
- Image: `https://cdn.sanity.io/images/1lq2ca9s/production/1a9353b107416eeeb363fdea8b10f1666d02e1b2-1920x1465.png` — alt: "The European Central Bank" — thumbnail for related post.
- Image: `https://cdn.sanity.io/images/1lq2ca9s/production/febb3ac3e3fd79423b45f738e5efbb3c46be70ad-1920x1465.png` — alt: "A Shell Is Worth a Thousand Images: Bing Images RCEs" — thumbnail for related post.
- Image: `https://cdn.sanity.io/images/1lq2ca9s/production/61a5df5512dcd889524344a1b13bd7aa87318fa4-1920x1465.png` — alt: "How CISOs can close the AI security gap before it widens: A practical framework" — thumbnail for related post.
- Image (logo, decorative): `/assets/footer-light.svg`, `/assets/footer-dark.svg`, `/assets/footer.svg` — site footer logos (no alt text).
- og:image (meta tag): `https://cdn.sanity.io/images/1lq2ca9s/production/931e0afd2133d07434e05f5225f8e889a4859453-720x378.png?w=1200&h=630&fm=jpg&q=80&fit=crop`
- No video or embed URLs (YouTube, Vimeo, Wistia, iframe) were found on the page.

## Source
https://xbow.com/blog/three-rce-vulnerabilities-in-microsoft-identified-xbow
