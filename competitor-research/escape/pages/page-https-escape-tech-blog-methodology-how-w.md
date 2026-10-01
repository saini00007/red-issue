---
url: https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/
category: research
title: Methodology: How we discovered over 2k high-impact vulnerabilities in apps built with vibe coding platforms
---
# Methodology: How we discovered over 2k high-impact vulnerabilities in apps built with vibe coding platforms

## Summary
This Escape research blog post details the methodology behind a large-scale security study of applications built with "vibe coding" platforms (Lovable, Base44, Create.xyz, Vibe Studio, Bolt.new). Escape's team scanned over 14,600 assets (5,600 web apps, 1,280 API services, 6,500 hosts, 1,103 schemas) and found more than 2,000 vulnerabilities, 400+ exposed secrets, and 175 instances of exposed PII. The post walks through data gathering, attack surface scanning (including a new "Visage" scanner), surface extraction/modeling, dynamic security testing, and data cleanup/verification steps used to produce the findings.

## Full content

### Introduction
The research targeted "vibe-coded applications" — apps built on platforms like Lovable.dev, Base44.com, and Create.xyz that let non-developers deploy full-stack applications without writing code. The concern driving the research is that inexperienced users building and shipping these apps can introduce significant security risks.

### Data Gathering Strategy
- Retrieved 4,000 applications from launched.lovable.dev
- Expanded the dataset using: lovable.dev, base44.com, vibe-studio.ai, bolt.new, create.xyz
- Performed subdomain enumeration and developed three fingerprinting methods for detecting Lovable-based apps
- Used Shodan indexing and Reddit community scraping (r/lovable, r/base44)
- Applied multi-stage curation: deduplication, reachability checks (HTTP 200–399 status codes), and filtering of non-functional pages

**Platform coverage in the dataset:**
- Lovable: ~4,000+ applications
- Base44: ~159
- Create.xyz: ~449
- Vibe Studio and Bolt.new: smaller samples

**Acknowledged biases:**
- Sampling bias from launch directories and community postings
- Temporal bias from one-time data collection
- Platform imbalance favoring Lovable deployments

### Attack Surface Scanning
Escape's Attack Surface Management (ASM) scanner mapped all exposed hosts, web apps, and APIs. The process included:
- Asset validation and reachability checks
- Fingerprinting and metadata collection (WAF, cloud provider, framework, GeoIP)

**Discovery techniques:**
- Domain and host discovery via subdomain enumeration
- Web crawling and route enumeration using headless browsers
- Static frontend analysis of JavaScript and HTML
- API discovery through documented routes and brute-forcing common paths

**Lovable–Supabase integration finding:**
Researchers identified anonymous JWT tokens exposed in JavaScript bundles linked to PostgREST APIs. While Supabase auto-generates RESTful APIs, "default security rules are permissive for development" and require Row-Level Security (RLS) policies for production use. The platform can assist in generating RLS policies, but manual review remains essential, especially for less experienced developers.

### Visage Surface Scanner
Escape introduced "Visage," a lightweight, read-only scanner built to harvest frontend artifacts without executing destructive actions. It analyzes source code and frontend responses to identify secrets and routes, feeding findings back into the ASM inventory. It is integrated into the ASM web app scanner and connected to Escape's API-focused Business Logic Security Testing Scanner.

### Surface Extraction & Modeling
Assets were organized per application, including:
- Hosts and subdomains
- Web application entry points and client routes
- REST/GraphQL/WebSocket endpoints with request/response shapes
- Authentication and session management endpoints
- Third-party integrations (Supabase, analytics, storage)

### Security Testing & Dynamic Analysis
Escape applied targeted DAST (dynamic application security testing) techniques configured in "passive" mode to avoid destructive operations, high-volume brute force, or disruptive payloads. The team attempted automated registration agents to provision accounts and execute comprehensive scans.

**Key observations:**
- "Most vulnerabilities were exposed without authentication."
- "Results understate the true risk" because passive-mode scanning was used; full scanning capabilities would likely surface additional, higher-severity vulnerabilities.

### Data Cleanup & Verification
- Automatic deduplication and normalization by the Escape platform
- Pattern-based filtering to distinguish genuine credentials from placeholders
- Safe live validation of tokens against non-destructive requests
- Replay-based validation of authentication weaknesses
- Manual spot-checks of representative findings
- Conservative scope: only high-confidence findings were retained

## Features / claims mentioned
- Escape's Attack Surface Management (ASM) scanner can map all exposed hosts, web apps, and APIs for a target set.
- ASM scanning includes fingerprinting/metadata collection: WAF, cloud provider, framework, GeoIP.
- Discovery techniques include subdomain enumeration, headless-browser web crawling/route enumeration, static frontend JS/HTML analysis, and API discovery via documented routes and path brute-forcing.
- New "Visage" scanner: lightweight, read-only, non-destructive; harvests frontend artifacts to identify secrets and routes; feeds results into ASM inventory; integrated with Escape's API-focused Business Logic Security Testing Scanner.
- Escape's Business Logic Security Testing Scanner is API-focused.
- Dynamic security testing (DAST) can run in a "passive" mode to avoid destructive operations, brute force, or disruptive payloads.
- Automated registration agents were used to provision accounts for scanning purposes.
- Supabase (used by Lovable-built apps) auto-generates RESTful APIs from database schemas via PostgREST; default security rules are permissive for development and require manual Row-Level Security (RLS) configuration for production security.
- Supabase's platform can assist in generating RLS policies, but manual review is still needed.
- Data cleanup pipeline includes deduplication/normalization, pattern-based credential filtering, safe non-destructive live validation, replay-based auth-weakness validation, and manual spot-checks.

## Numbers & metrics mentioned
- "5,600+ publicly available applications" analyzed
- "2,000+ vulnerabilities" identified
- "400+ exposed secrets" discovered
- "175 instances of PII" found (medical records, IBANs, phone numbers, emails)
- "14,600 assets" scanned total
- Asset breakdown: "5,600 web applications", "1,280 API services", "6,500 hosts", "1,103 schemas"
- "4,000 applications" retrieved from launched.lovable.dev
- Platform sample sizes: Lovable "~4,000+", Base44 "~159", Create.xyz "~449"
- HTTP reachability filter: status codes "200–399"
- Publication date: "October 29, 2025"
- Read time: "10 min read"

## People named
- Nohé Hinniger-Foray — author/researcher
- Gwendal Mognier — author/researcher
- Alexandra Charikova — author/researcher
- Yacine Souam — author of related article "AI vs AI: How Cascade exploited an AI agent in production" (Aug 14, 2026)
- Enzo Mongin — author of related article on a Keycloak PII disclosure / CVE-2026-17059 (Jul 31, 2026)
- Arnaud Fanthomme — author of related article "Why does the rise of Agentic AI force security teams to become research-aware?" (Jul 24, 2026)

## Media found
- Image (banner/og:image): https://escape.tech/blog/content/images/size/w2000/2026/06/Article-banner-template--4-.png — article banner
- Image: https://escape.tech/blog/content/images/2025/10/process-data-collection-escape.png — diagram of the data collection process
- Image: https://escape.tech/blog/content/images/2025/10/Screenshot-2025-10-29-at-13.40.56.png — screenshot related to fingerprinting methods
- Image: https://escape.tech/blog/content/images/2025/10/typical-asm-scanner-structure.png — diagram of typical ASM scanner structure
- Image: https://escape.tech/blog/content/images/2025/10/lovable-supabase-integration-schema.png — schema diagram of Lovable-Supabase integration
- Image: https://escape.tech/blog/content/images/2025/10/visage-surface-scanner.png — diagram of the Visage Surface Scanner structure
- Image: https://escape.tech/blog/content/images/2025/10/web-app-asm-scanner-with-lovable.png — diagram of complete discovery schema
- Image: https://escape.tech/blog/content/images/2025/10/scanned-assets.png — diagram/chart of scanned assets breakdown
- Author photos: multiple small contributor headshot images referenced (no individual URLs captured)
- No video/embed (YouTube, Vimeo, Wistia, etc.) URLs were found on the page.

## Source
https://escape.tech/blog/methodology-how-we-discovered-vulnerabilities-apps-built-with-vibe-coding/
