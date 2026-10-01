---
url: https://xbow.com/blog/benchmarks
category: research
title: XBOW Penetration Testing Benchmarks: Metrics That Matter
---

# XBOW Penetration Testing Benchmarks: Metrics That Matter

(On-page H1 / article headline: "XBOW Validation Benchmarks: Show Me the Numbers!")

## Summary
This is an XBOW blog post (AI Research category, published November 9, 2024, author Nico Waisman, CISO @ XBOW) announcing that XBOW is publicly releasing 104 penetration-testing validation benchmarks. The post argues that the security industry — especially AI-powered security products — is full of unsubstantiated marketing claims, and that XBOW commissioned outside pentesting companies to build original, novel vulnerability benchmarks (covering classes like SQL Injection, IDOR, and SSRF) so that XBOW's and others' AI systems can be rigorously, objectively evaluated. XBOW reports an 85% success rate on these benchmarks, comparable to an experienced human pentester working for a week, and is open-sourcing the benchmark suite on GitHub for other researchers, tools, and products to use.

## Full content

**Category tag:** AI Research
**Published:** November 9, 2024
**Author:** Nico Waisman

**Breadcrumb:** Blog > AI Research > XBOW Validation Benchmarks: Show Me the Numbers!

**Tags on post:** Benchmarks, AI Evaluation, AI Pentesting, Security Validation

**Excerpt (dek):**
> XBOW is currently making 104 benchmarks available to the public. This allows other security products, tools, and researchers to use and explore these benchmarks.

**Editor's note (italic, at top of body):**
> Editor's note: These benchmarks were published in 2024. They are now outdated and should no longer be used to measure offensive performance.

**Body paragraphs (in order):**

As a CISO, I always struggled to figure out what products are worthy of my team's time. There is so much noise, and so many inflated claims. If, like me, you walked through the BlackHat Business Hall, you will understand what I mean. All those buzzwords! All that hype! Please just tell me what the product actually does? And how is it different from all the other products touted by equally eager vendors?

This is not a new problem. In the early days of the offensive security industry, there was a saying that eventually became a popular ezine: "Proof of concept or GTFO." Even then, we already had a flood of security products claiming to find lots of vulnerabilities, but oddly enough, they had no known bugs associated with them. As a CISO, if you want my team to spend time evaluating your product, show me the numbers!

If the security industry in general is already noisy and full of unsubstantiated claims, it gets a whole degree worse with AI. Super cool demos galore, but when you try to use these AI products in anger, they fail to deliver. So for an AI-powered security technology, we need absolutely rigorous evaluation of all the claims.

At XBOW, such hunger for objective proof is part of our DNA. That is why we engaged a series of pentesting companies to develop novel benchmarks. These benchmarks closely replicate the various classes of vulnerabilities you might encounter in real-life scenarios, ranging from SQL Injections to IDOR and SSRF. We gave our suppliers just the list of vulnerability classes they needed to cover, but left it entirely up to them to design the benchmarks themselves. This resulted in 104 benchmarks.

Because the benchmarks are original, we can guarantee a level of novelty that never appeared in the AI training models before. This compels the system to generate new ideas, eliminating the possibility of simply regurgitating examples memorized during training.

The benchmark were constructed for testing against both offensive tools and human experts, with the intention of establishing a measurement and improvement baseline. Impressively, XBOW managed to secure a success rate of 85%, which is equivalent to what a experienced pentester could achieve within a week.

We are now making these [benchmarks public](https://github.com/xbow-engineering/validation-benchmarks) so that other security products, tools, and researchers can utilize and experiment with them. We've already achieved an impressive success rate, but we want you to witness firsthand how challenging and realistic the tasks are. Utilize our benchmarks to measure the performance of new AI models, agents, and anything else you're working on. If you're looking for even more of a challenge, consider building on our benchmark framework, it's an excellent way to test limits and drive innovation! Please share how your technology performs!

One urgent request to those that train models: don't include them in your training data - we included a [canary string](https://www.alignment.org/canary/), please respect it. We are thrilled to share with you the potency of our technology!

**Author bio box:**
Nico Waisman — CISO @ XBOW
Links: [LinkedIn](https://ar.linkedin.com/in/nwaisman), [X](https://x.com/nicowaisman), [GitHub](https://github.com/nicowaisman)

**Related / linked posts shown on page (not full content, titles/thumbnails only):**
- "Engineering the Impossible: Adding Safety to Autonomous Agents"
- "Engineering the Impossible: How XBOW De-Duplicates Findings"
- "Grok 4.7 vs 4.6 Comparison and How to Use Grok 4.7"

## Features / claims mentioned
- XBOW makes 104 penetration-testing validation benchmarks publicly available.
- Benchmarks were commissioned from outside pentesting companies, each given only a list of vulnerability classes to cover and left free to design the benchmark scenarios themselves.
- Vulnerability classes covered include SQL Injection, IDOR (Insecure Direct Object Reference), and SSRF (Server-Side Request Forgery), among "various classes of vulnerabilities you might encounter in real-life scenarios."
- Benchmarks are original/novel, designed so they never appeared in AI model training data, forcing genuine reasoning rather than memorized regurgitation.
- A canary string (linked to https://www.alignment.org/canary/) is embedded in the benchmark set to signal AI trainers not to scrape it into training data.
- Benchmarks are designed for testing both automated offensive tools and human experts, to establish a measurement/improvement baseline.
- Benchmark suite is open-sourced on GitHub (xbow-engineering/validation-benchmarks) for other security products, tools, and researchers to use.
- Framed as a countermeasure to industry hype/unsubstantiated marketing claims, particularly around AI-powered security products.
- Editor's note added later flags that these specific 2024 benchmarks are now outdated and should no longer be used to measure offensive performance (implying XBOW has since published newer/updated benchmarks elsewhere).

## Numbers & metrics mentioned
- "104 benchmarks" made available to the public (stated in meta description, excerpt, and body).
- "85%" success rate achieved by XBOW on these benchmarks.
- The 85% success rate is described as "equivalent to what a[n] experienced pentester could achieve within a week."
- Published date: November 9, 2024 (datePublished / article:published_time: 2024-11-09T13:00:00.000Z).

## People named
- Nico Waisman — CISO @ XBOW; author of this post. LinkedIn: ar.linkedin.com/in/nwaisman, X: @nicowaisman, GitHub: nicowaisman.

## Media found
- https://cdn.sanity.io/images/1lq2ca9s/production/760b19bd8596177691b317370a24acf17328b333-1920x1465.png?w=1920&auto=format — hero/header image, alt: "XBOW Validation Benchmarks: Show Me the Numbers!" (also used as og:image source at a different crop; social og:image is a 1200x630 crop of this same asset: https://cdn.sanity.io/images/1lq2ca9s/production/17e0436ed3197c80f2c4df7229c126f0ac306a7c-1920x1080.jpg?rect=0,36,1920,1008&w=1200&h=630&fm=jpg&q=80&fit=crop)
- https://cdn.sanity.io/images/1lq2ca9s/production/8a68e84a3c108c84044506943868f88feb6cfac2-320x320.jpg?w=160&auto=format — author avatar photo, alt: "Nico Waisman"
- https://cdn.sanity.io/images/1lq2ca9s/production/105bd2aeeeec9774400db9e15bf8417abbbaa250-480x366.png?w=800&auto=format — related-post thumbnail, alt: "Engineering the Impossible: Adding Safety to Autonomous Agents"
- https://cdn.sanity.io/images/1lq2ca9s/production/85c7e1dda88bad96905c2af4c3dc9b28313be968-480x366.png?w=800&auto=format — related-post thumbnail, alt: "Engineering the Impossible: How XBOW De-Duplicates Findings"
- https://cdn.sanity.io/images/1lq2ca9s/production/9bab1e30d3f0dd48cabacf65c8fe5b72f7a98317-1800x1374.png?w=800&auto=format — related-post thumbnail, alt: "Grok 4.7 vs 4.6 Comparison and How to Use Grok 4.7"
- /assets/footer.svg, /assets/footer-dark.svg, /assets/footer-light.svg — site footer logo/wordmark graphics (not article-specific)
- No video or embed URLs (YouTube/Vimeo/Wistia/iframe) were found on this page.

## Source
https://xbow.com/blog/benchmarks
