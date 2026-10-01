---
url: https://firecompass.com/shipped-to-the-browser-how-firecompasss-agentic-ai-penetration-testing-found-api-keys-and-signing-secrets-hardcoded-into-client-side-code-across-ten-independent-programs/
category: research
title: Shipped to the Browser: How FireCompass's Agentic AI Penetration Testing Found API Keys and Signing Secrets Hardcoded Into Client-Side Code Across Ten Independent Programs
---
# Shipped to the Browser: How FireCompass's Agentic AI Penetration Testing Found API Keys and Signing Secrets Hardcoded Into Client-Side Code Across Ten Independent Programs

## Summary
This FireCompass research blog post reports on a study where FireCompass's agentic AI penetration testing platform surfaced 12 candidate secret/API-key exposure findings across ten independent client programs, of which 7 were validated. The findings fall into four recurring patterns: unrestricted third-party API keys (e.g., Maps Platform), hardcoded signing secrets (JWT/HMAC) enabling forged authentication, internal application secrets shipped to the browser, and over-scoped third-party content/search delivery tokens. The post walks through a three-stage validation model (Detect → Validate → Controlled Exploit) and closes with root-cause analysis and remediation guidance for organizations.

## Full content

### From Candidate Signal to Program-Validated Exposure
The piece frames the investigation as moving from raw candidate signals (12 total) to confirmed, program-validated exposures (7), with the remainder closed as informative, triaged, pending review, or identified as duplicates across programs.

### The Twelve Findings
A table of all 12 findings is presented, covering the finding name, its pattern category, the affected industry, its triage status (New, Triaged, Pending Review, Duplicate, Informative), and severity rating.

### The Client-Side Trust Gap Behind Every Secret Leak
Organizations commonly operate under the misconception that "not shown in the UI" equals "not retrievable by the client." The post describes the pattern as flowing: Origin → Embed → Deliver → Read → Result, with secrets becoming visible through browser developer tools, JavaScript source maps, or decompiled/unminified bundle code.

### From Anomaly to Proof: A Three-Stage Validation Model
1. **Detect** – Identify candidate secrets present in shipped/client-side code.
2. **Validate** – Confirm the secret is live (active) and unrestricted (not scoped/limited).
3. **Controlled Exploit** – Prove real-world impact through a single, bounded exploitation action, avoiding unnecessary or damaging actions.

### How the Pattern Played Out Across Four Mechanisms

**Pattern 1: Unrestricted Third-Party API Keys Exposed in Frontend Code (3 findings)**
Includes cases such as unrestricted third-party Maps API keys exposed in frontend code (two independent instances, in Financial Services/Money Transfer), a Google Maps API key disclosed via a configuration endpoint (Financial Services/Payments Technology), and an unrestricted Google Maps API key exposed in a distributor locator page (Consumer Goods/Personal Care).

**Pattern 2: Hardcoded Signing Secrets Enable Forged Authentication (4 findings)**
Includes a hardcoded JWT signing secret in public JavaScript enabling forged bearer tokens (Semiconductor/Technology Hardware), a hardcoded HMAC signing secret in public JavaScript enabling unauthorized data enumeration (Media/Publishing), a public JavaScript source map exposing a hardcoded token and full frontend source (Food & Beverage/CPG), and an exposed signing secret in JavaScript enabling unauthenticated event forgery (Internet/E-Commerce & Gaming Conglomerate).

**Pattern 3: Internal Application Secrets Shipped to the Browser, Recurring Within One Organization (2 findings)**
Includes a client-exposed internal application secret enabling unauthorized configuration API access, and a hardcoded webhook token in a public JS bundle enabling unauthenticated message injection — both attributed to the same Internet/E-Commerce & Gaming Conglomerate organization, indicating a recurring organizational habit rather than an isolated incident.

**Pattern 4: Over-Scoped Third-Party Content and Search Delivery Tokens (3 findings)**
Includes an over-scoped content-delivery API token exposing unreleased promotional codes (Gaming/Interactive Entertainment), an over-scoped content-delivery API token exposing non-public marketplace content (Fintech/Consumer Lending), and an exposed third-party search platform bearer token enabling unauthorized document access (Financial Services/Insurance & Retirement).

### Why This Matters
Discusses the real-world consequences of these exposure classes: forged authentication, unauthorized data access, and reputational/financial risk from leaked secrets reaching production frontend code.

### Root Cause
Attributes the recurring pattern to a fundamental client-side trust gap: developers and organizations treating client-side code as private or hidden, when in fact anything shipped to the browser is retrievable by any user.

### Remediation and Key Lessons for Organizations
- Never ship server-to-server credentials to the browser.
- Scope and restrict third-party API keys by referrer, IP address, and quota.
- Rotate any secret found in shipped code immediately upon discovery.
- Strip source maps from production builds or gate them behind authentication.
- Scope third-party tokens to exactly the content/functionality needed — nothing more.
- Correlate findings across products/programs within an organization to identify recurring insecure habits (as seen with the same organization appearing twice in Pattern 3).

### Lessons Learned
Reiterates that these are not one-off mistakes but recurring, systemic patterns across industries and even within the same organization, underscoring the need for continuous, automated detection rather than one-time audits.

### How FireCompass's Agentic AI Penetration Testing Identified and Exploited These Bugs
Describes how FireCompass's agentic AI platform autonomously performed the detect-validate-exploit workflow across the ten programs to surface and confirm these findings, positioned as a demonstration of the platform's autonomous red-teaming capability at scale.

## Features / claims mentioned
- Agentic AI penetration testing platform that autonomously detects, validates, and (in a controlled/bounded way) exploits vulnerabilities.
- Three-stage validation methodology: Detect → Validate → Controlled Exploit.
- Ability to correlate findings across multiple programs/products to surface recurring organizational security habits (not just isolated bugs).
- Coverage across ten independent client programs / multiple industries in a single research effort.
- Claimed positioning as autonomous/agentic red teaming and Attack Surface Management (ASM), per author's bio.
- "Free AI Pen Test" call-to-action offered on the page.

## Numbers & metrics mentioned
- "12" secret/API key exposure candidates surfaced in total
- "7" program-validated findings
- "5" closed informative findings
- "10" distinct programs affected
- "4" confirmed duplicates
- "3" findings triaged, pending review, or newly reported
- Severity breakdown: 1 critical (8%), 3 high (25%), 5 medium (42%), 3 unrated (25%)
- Publication date: 24 Aug 2026
- 12 findings detailed in the results table, spanning industries: Semiconductor/Technology Hardware, Media/Publishing, Gaming/Interactive Entertainment, Financial Services/Money Transfer (x2 duplicate instances), Fintech/Consumer Lending, Internet/E-Commerce & Gaming Conglomerate (appears twice), Financial Services/Insurance & Retirement, Financial Services/Payments Technology, Consumer Goods/Personal Care, Food & Beverage/CPG

## People named
- **Sanket Kakde** — Author; Director Offensive Security | Security Architect | Offensive Security Researcher | Red Teamer | Attack Surface Management (ASM) | Autonomous Red Teaming & Penetration Testing

## Media found
- `https://firecompass.com/wp-content/uploads/2024/07/logo-1.png` — FireCompass site logo
- `https://firecompass.com/wp-content/uploads/2026/08/FC_Blog_ExposedSecrets_Cover_v12x-1024x538.png` — article cover image
- `https://firecompass.com/wp-content/uploads/2026/08/FC_Blog_ExposedSecrets_img1_SeverityDistribution.png` — severity distribution chart/diagram
- `https://firecompass.com/wp-content/uploads/2026/08/FC_Blog_ExposedSecrets_img2_AgenticPlatformBenefits.png` — agentic platform benefits diagram
- `https://firecompass.com/wp-content/uploads/2026/07/Sanket.jpg` — author headshot photo
- `https://firecompass.com/wp-content/uploads/2026/09/FC_Widget_HackerOne1_CISO_US_v3.png` — promotional/product widget image
- `https://firecompass.com/wp-content/uploads/2026/05/FC_BlogFeatured_google-grpc-switchblade_v11-768x403.png` — related blog post image (gRPC/MCP topic)
- `https://firecompass.com/wp-content/uploads/2025/12/Inotiv-Ransomware-Attack-768x401.jpg` — related blog post image (Inotiv ransomware topic)
- Social share icons for ChatGPT, Perplexity, Grok, Gemini, Claude (no distinct media URLs captured)
- No video/embed URLs (YouTube, Vimeo, Wistia, etc.) were found on the page.
- og:image URL was not explicitly captured/available from the fetch.

## Source
https://firecompass.com/shipped-to-the-browser-how-firecompasss-agentic-ai-penetration-testing-found-api-keys-and-signing-secrets-hardcoded-into-client-side-code-across-ten-independent-programs/
