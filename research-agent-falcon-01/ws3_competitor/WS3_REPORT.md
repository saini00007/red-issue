# WS-3 · Competitor & Market Gap Analysis

## Question List & Diagnostic Findings

### Q1: What mechanisms do competitors ship for chained exploitation, deterministic validation, and client-side proof?
* **Chained Exploitation Mechanisms:**
  - **XBOW:** Operates a 5-stage loop (Learn -> Map -> Coordinate -> Attack -> Prove). Attack agents are short-lived and task-specific; when a primitive is unlocked (e.g. WAF bypass or exposed credential), the coordinator updates the attack-surface graph and dispatches specialized follow-on agents armed with the newly discovered capability token (`competitor-research/xbow/dossier.md:41-47,81`). Demonstrated in Moderna case study: exposed credential -> API routing bypass -> SQLi -> IDOR within 18 hours (`xbow/dossier.md:105`).
  - **FireCompass:** Uses a dedicated "chain agent" on top of its patented CART engine (`competitor-research/firecompass/dossier.md:46,80`). Holds an internal state store across specialized sub-agents (surface mapping, recon, credential handling, lateral movement), executing credential reuse and app-to-network/Active Directory lateral pivots aligned to MITRE ATT&CK (`firecompass/dossier.md:91,105`).
  - **Escape:** Employs the "Cascade" multi-agent architecture with a shared pub/sub message bus (topics: `recon`, `xss`, `sqli`, `idor`, `ssrf`, `auth`, `rce`) and a shared knowledge store (`competitor-research/escape/dossier.md:90-96`). Multi-identity testing holds multiple authenticated browser sessions concurrently to test BOLA/IDOR state transitions (`escape/dossier.md:98`).
  - **Abhedi Red (autocan):** Implements a two-tier chaining mechanism: (1) `run_chain_floor()` (`father.py:1914`, `src/scanner/agent_runtime/chain/floor.py`) which hardcodes deterministic next-hop probes (SSRF -> AWS/GCP metadata, LFI -> config/env secrets), and (2) `run_escalation()` (`father.py:1922`, `escalation.py`) which reopens ledger classes based on high-level `Capability` enums. However, it currently lacks an explicit capability-token handoff passing Hop N's raw proof artifact into Hop N+1's execution environment.

* **Deterministic Validation Mechanisms:**
  - **XBOW:** Dispatches independent "validator" agents (distinct from attack agents) combining programmatic checks (e.g. headless browser confirming JavaScript payload execution) and LLM-based verification to enforce "proof not noise" (`competitor-research/xbow/dossier.md:46,82`).
  - **FireCompass:** Enforces a 4-stage pipeline: `hypothesis -> live execution -> signature evaluation -> evidence assembly` (`competitor-research/firecompass/dossier.md:45,92`). Findings require match against a deterministic exploitation signature ("no exploit, no alert") to claim <2% false positives.
  - **Escape:** Spawns an independent "Reporter" agent completely isolated from exploitation message bus traffic to eliminate confirmation bias (`competitor-research/escape/dossier.md:95`). The Reporter re-executes the candidate request chain on the live target and collects its own evidence before filing.
  - **Abhedi Red (autocan):** Aligns with the core thesis "LLM proposes, deterministic oracle disposes":
    1. Deterministic exploit floor (`exploit_floor.py`): Weapon sweeps run deterministic pattern/diff oracles.
    2. OOB service (`oob/service.py`): Correlates out-of-band DNS/HTTP interactions with per-scan tokens.
    3. Finalize A1 Verifier (`finalize.py:344-367`): Independent second-pass model re-executes PoC curl commands against the live toolserver before marking `verified=true`.

* **Client-Side Proof Mechanisms:**
  - **XBOW:** Headless browser automation executing payloads in real DOM contexts for DOM-XSS (`competitor-research/xbow/dossier.md:48`); SimHash content hashing and screenshot imagehash for visual deduplication (`xbow/dossier.md:53,83`).
  - **FireCompass:** Generates ready-to-run Python PoC scripts and captures literal request/response transcripts with cryptographic audit logging (`competitor-research/firecompass/dossier.md:45,106`).
  - **Escape:** Multi-identity Playwright browser sessions, HAR recording slices, and Vision-AI for solving MFA/complex authentication flows (`competitor-research/escape/dossier.md:81,129`).
  - **Abhedi Red (autocan):** Headless Chromium container (`docker/browser/browser_server.py`) instrumented for DOM-XSS hook capture; HAR-slicing for API findings (`finalize.py:310`).

---

### Q2: Which buyer-visible proof standards do reports demonstrate?
* **XBOW:**
  - "Full case file" per finding: complete chained attack path, runnable exploit code, audit log of agent decisions, framework-specific remediation (`competitor-research/xbow/dossier.md:49`).
  - Public proof: #1 HackerOne US leaderboard, MSRC #1 autonomous ranking, named CVE credits in Microsoft, Bing, and Exim (`xbow/dossier.md:128-140`).
* **FireCompass:**
  - Ready-to-run Python PoC scripts, literal request/response pairs, visual MITRE ATT&CK attack path mapping, cryptographic timestamped audit trail (`competitor-research/firecompass/dossier.md:45,106`).
* **Escape:**
  - Request sequences, user scopes, working exploit payloads, full reasoning logs (orchestrator chain-of-thought), framework-specific code fixes, and automated translation of findings into permanent CI/CD regression tests (`competitor-research/escape/dossier.md:100-101`).
* **Abhedi Red (autocan):**
  - Finding record (`findings.jsonl`, `report.json`, `report.html`): CWE ID, CVSS score, reproduction curl command, verified flag, verification method, gained access, prerequisite access, and linked evidence objects.

---

## Capability-Comparison Table (Mechanisms)

| Capability Dimension | XBOW | FireCompass | Escape | Abhedi Red (Current `autocan`) | Key Gap / Opportunity for Abhedi Red |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Exploit Chaining** | Dynamic Coordinator re-tasking short-lived attack agents on newly mapped attack surfaces (`xbow/dossier.md:45`) | Dedicated Chain Agent executing lateral pivots (app -> network -> AD) on persistent state store (`firecompass/dossier.md:91`) | Cascade shared pub/sub bus + multi-identity browser sessions (`escape/dossier.md:95`) | Hardcoded floor hops (`floor.py`) + class re-opening (`escalation.py`) without artifact handoff | **Lacks capability-token state machine**: Hop N cannot pass extracted secrets/tokens into Hop N+1 execution context. |
| **False-Positive Suppression** | Independent Validator agents (LLM + programmatic headless checks) (`xbow/dossier.md:48`) | 4-stage signature evaluation pipeline ("no exploit, no alert") (`firecompass/dossier.md:92`) | Isolated Reporter agent independently re-executing on target (`escape/dossier.md:95`) | Deterministic exploit floor + OOB token correlation + A1 verifier | **Strong verification foundation**, but OOB correlation lacks noise filtering (interactsh buffer pollution). |
| **Client-Side / SPA Depth** | Headless browser DOM-XSS execution check + screenshot dedup (`xbow/dossier.md:48,83`) | Live request/response capture + Python PoC scripts (`firecompass/dossier.md:45`) | Playwright multi-user sessions, HAR slicing, Vision-AI login flows (`escape/dossier.md:81,129`) | Browser server with DOM-XSS hook + HAR slicing in finalize | **No multi-step SPA state-change engine**: Browser server cannot navigate multi-step client workflows. |
| **Business-Logic / Auth Testing** | Context-driven attack agents; IDOR examples in case studies (`xbow/dossier.md:47`) | Multi-Stage Hunting Playbooks covering credential reuse (`firecompass/dossier.md:74`) | Proprietary BLST algorithm with strong typing & sourcing inference (`escape/dossier.md:78`) | Auth bootstrap (`auth_bootstrap.py`) creates 2 accounts; logic workers test curl sequences | **No deterministic business-logic oracle**: Relies on LLM self-judgment; coupon/referral abuse lacks oracles. |
| **Continuous Integration & Regression** | REST API, webhooks, Jira, Microsoft Sentinel integration (`xbow/dossier.md:59-63`) | Weekly/CI cadence, 1-click fix revalidation (`firecompass/dossier.md:47`) | Cascade findings automatically convert into permanent CI regression tests (`escape/dossier.md:101`) | Finalize report generation (`report.json`), scan resume support | **No regression test emission**: Findings do not export into runnable test suites (e.g. pytest/k6/curl suites). |

---

## WS-3 Evidence Ledger

| Claim | Source (type + location) | Confidence | Notes |
| :--- | :--- | :--- | :--- |
| XBOW uses 5-stage loop and independent validator agents for proof | [COMPETITOR] `competitor-research/xbow/dossier.md:41-48` | HIGH | Learn -> Map -> Coordinate -> Attack -> Prove. |
| XBOW chained WAF bypass -> API key -> SQLi -> IDOR in Moderna case study | [COMPETITOR] `competitor-research/xbow/dossier.md:47,105` | HIGH | Multi-stage chain across 30-40 internal apps in under 18 hours. |
| FireCompass uses 4-stage validation pipeline and claims <2% false positives | [COMPETITOR] `competitor-research/firecompass/dossier.md:45,92` | HIGH | Hypothesis -> live execution -> signature evaluation -> evidence assembly. |
| Escape Cascade uses isolated Reporter agent and shared pub/sub bus | [COMPETITOR] `competitor-research/escape/dossier.md:90-96` | HIGH | Topics: recon, xss, sqli, idor, ssrf, auth, rce; Reporter isolated from bus. |
| Escape converts proven findings into permanent CI/CD regression tests | [COMPETITOR] `competitor-research/escape/dossier.md:101` | HIGH | Findings flow into Escape DAST for every CI build. |
| Abhedi Red chaining relies on hardcoded floor probes and capability class reopen | [CODE] `src/scanner/agent_runtime/chain/floor.py:15-60`, `father.py:1914-1922` | HIGH | SSRF->metadata, LFI->config; no token artifact passing between hops. |
