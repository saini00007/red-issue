---
url: https://escape.tech/blog/escape-found-the-same-vulnerability-in-two-ai-chatboxes/
category: research
title: Escape found the same XSS in two AI chatboxes. The vulnerability was in the Markdown renderer.
---

# Escape found the same XSS in two AI chatboxes. The vulnerability was in the Markdown renderer.

## Summary
This Escape blog post (published Aug 21, 2026, by Gwendal Mognier and Geoffrey Diederichs) describes how Escape's AI pentesting agent independently discovered identical stored cross-site scripting (XSS) vulnerabilities in two separate companies' AI chatbox implementations. Both systems rendered Markdown with raw HTML enabled (via `react-markdown` + `rehype-raw`) without sanitization, allowing an `<iframe srcdoc="...">` payload to execute arbitrary script. The post explains the technical mechanism, cites related CVEs in other Markdown/Mermaid renderers, and gives hardening recommendations, backed by industry vulnerability statistics.

## Full content

### Overview
Escape's AI pentesting agent discovered identical stored cross-site scripting (XSS) vulnerabilities in two separate companies' AI chatbox implementations. Both systems rendered Markdown with raw HTML enabled and lacked proper sanitization.

### Key Vulnerability Details

**How It Was Found:**
The agent identified that both systems used `react-markdown` with the `rehype-raw` plugin enabled without sanitization. The renderer configuration included:
- remark-gfm plugin
- rehype-raw plugin
- No DOMPurify, rehype-sanitize, or equivalent protections

**Technical Mechanism:**
The vulnerability exploited the `srcdoc` attribute on iframes. Unlike `src`, which is URL-filtered, `srcdoc` contains raw HTML documents. Payloads like `<iframe srcdoc="<script>alert(document.domain)</script>">` execute because `srcdoc` content parses as a new document without sandbox restrictions.

**Why It's Stored, Not Self-XSS:**
- Chat transcripts are shared via links
- Support escalations expose conversations to administrators
- Model outputs can be rendered in dashboards and tickets
- Privileged users access attacker-controlled markup

### Affected Rendering Extensions
Referenced vulnerabilities:
- **CVE-2026-32308** (OneUptime): Mermaid renderer at `securityLevel: "loose"` injected via `innerHTML`
- **CVE-2026-17496** (NoteGen): `markdown-it` with `html: true` in Tauri webview

### Hardening Recommendations
1. Remove raw HTML rendering — Delete `rehype-raw` plugin; tables/links/code blocks work without it
2. Sanitize after rehype-raw — Use `rehype-sanitize` with an allowlist approach, never a denylist
3. Enumerate attributes carefully — Disallow `srcdoc`, `action`, `on*` handlers; force `sandbox` on iframes
4. Treat rendering extensions as HTML generators — Syntax highlighters, KaTeX, Mermaid reopen security gaps
5. Implement Content Security Policy — Remove `unsafe-inline`, restrict `img-src`, `form-action`, `frame-src`
6. Move API keys — Remove from global config objects in pages
7. Verify at each render point — Test with payloads on the actual origin

### Related content links (footer cards)
- "Two critical vulnerabilities, one AI pentester: how Cascade found an unauthenticated RCE"
- "How Escape AI pentesting exploited SSRF in LiteLLM"
- "Introducing Cascade: multi-agent penetration testing"
- "What an External Penetration Test is And How One is Actually Run"
- "How to build a continuous pentesting program"
- "How Amp got its SOC 2 type II pentest evidence in hours"

## Features / claims mentioned
- Escape's AI pentesting agent can independently discover stored XSS vulnerabilities in production AI chatbox implementations across different customers.
- The agent identifies specific unsafe library/plugin combinations (`react-markdown` + `rehype-raw` without sanitization).
- The agent demonstrates working exploit payloads (e.g., iframe `srcdoc` injection) rather than just flagging theoretical risk.
- Escape frames vulnerable Markdown rendering as a recurring, systemic class of bug across AI chat products, not a one-off.
- Provides concrete hardening/remediation guidance (removing rehype-raw, sanitization allowlists, CSP, attribute enumeration, API key handling).

## Numbers & metrics mentioned
- "31% of breaches" — unpatched flaws now the most common entry point (cited to Verizon 2026 DBIR)
- "32% of intrusions in 2025" — exploiting vulnerabilities (cited to Mandiant M-Trends 2026)
- "Median time to fix vulnerabilities: 43 days"
- CVE-2026-32308 (OneUptime)
- CVE-2026-17496 (NoteGen)
- Publication date: Aug 21, 2026

## People named
- Gwendal Mognier — author (role not further specified beyond author byline)
- Geoffrey Diederichs — author (role not further specified beyond author byline)

## Media found
- Image: `/blog/content/images/size/w2000/2026/08/two-chatboxes-one-xss.png` — main featured/header image (alt text matches article title)
- Image: `/blog/content/images/2026/08/stored-xss-screenshot--1-.png` — screenshot showing the vulnerability reproduced in a customer environment
- Additional thumbnail images accompany the related-article footer cards (dimensions vary; specific src/alt not itemized by the fetch)
- No YouTube, Vimeo, Wistia, or other video/embed URLs found on the page
- og:image: not explicitly confirmed distinct from the main featured image above (likely same as `/blog/content/images/size/w2000/2026/08/two-chatboxes-one-xss.png`, but not independently verified)

## Source
https://escape.tech/blog/escape-found-the-same-vulnerability-in-two-ai-chatboxes/
