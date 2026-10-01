# WS-7 · Architecture Synthesis & Improvement Plan

## 1. Core Architecture Improvements (Ranked by Blast Radius)

| Rank | Architecture Improvement | Module & Flag | Problem Solved | Buyer-Visible Outcome |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Mandatory Progress Watchdog & Default Batch Dispatch** | `father.py:530,1898`, `SCANNER_ENGINE_STUCK_WINDOW_S=120`, `SCANNER_ENGINE_BATCH_DISPATCH=true` | Eliminates 15-hour scan stalls (`1f5fe7c8`); replaces synchronous `gather` wave barriers with rolling pool. | Scan turnaround drops from 15h to <35m; 100% elimination of runaway hangs. |
| **2** | **End Finalize Mass-Retirement (Honest Coverage Accounting)** | `finalize.py:454-468`, `SCANNER_FINALIZE_RETIRE_UNREACHED=false` | Stops marking 7,371 untested cells as "attempted" with 0 attempts. Unprobed surface is accurately reported as `untested`. | Transparent, trustworthy coverage reports; stops false "100% completed" claims on 20% actual coverage. |
| **3** | **Model Egress Error Interception & Circuit Breaker (F3)** | `agents_runtime.py:699,893`, `httpx` response hook | Captures and logs 429 rate-limits and 500 errors. Automatically sheds concurrency when provider degrades. | Eliminates hidden stalls; triggers immediate fallback to backup model seats. |
| **4** | **Live Capability-Token Handoff Pipeline** | `chain/tokens.py` (new), `father.py:1520`, `tenant.findings` schema | Replaces post-hoc graph guessing with real machine-usable capability token passing from Hop N to Hop N+1. | Verifiable multi-stage attack chains in reports ("found X -> proved Y -> accessed Z"). |
| **5** | **OOB Noise Isolation & Correlation Scoping** | `oob/service.py:120-160`, `interactsh` polling filter | Filters out worker self-health probes and unpurged cross-scan buffer noise before creating findings. | Zero false-positive SSRF findings on control probes (`(no target - control only)`). |

---

## 2. Feature Add-Ons (Ranked by Buyer-Visible Proof Value)

| Rank | Feature Add-On | Target Surface | Mechanism | Buyer Value |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Stateful SPA & Multi-Identity Browser Worker** | Client-side SPAs, B2B SaaS | Exposes `/session/{new,act,snapshot,har}` in `browser_server.py`. Persists auth states to test BOLA/IDOR. | Proves complex business logic and client authorization flaws that scanners miss. |
| **2** | **Deterministic GraphQL & WebSocket Oracles** | GraphQL APIs, Real-time WebSockets | Deterministic introspection/field auth parser and CSWSH handshake verifier in `exploit_floor.py`. | Closes modern API vulnerability cells with machine proof instead of LLM prose. |
| **3** | **Continuous Regression Test Exporter** | CI/CD Pipelines | Exports confirmed finding PoCs into reproducible, standalone `pytest`/`curl` regression test suites. | Matches Escape's compounding regression moat; locks in remediation verification. |
| **4** | **Semantic Finding Deduplication & Clustering** | All targets | Deduplicates findings on `(vuln_class, affected_endpoint, root_cause_hash)` rather than title string. | Eliminates 6x duplicate email-relay findings on `/api/send`. Clean, executive reports. |

---

## 3. Explicit "Do Not Build" List (With Concrete Reasons)

1. **DO NOT BUILD: Recursive Agent Hierarchies (Managers managing managers)**
   - *Reason:* Multiplying agent layers exponentially balloons uncached prompt tokens (already at 140:1 in:out ratio), increases latency, and creates un-auditable coordination deadlock. A flat pool governed by a single bounded Father tick is strictly superior.
2. **DO NOT BUILD: Agent-to-Agent Free-Form Chat Messaging**
   - *Reason:* Unstructured chat between workers creates hallucination spirals and non-deterministic state drift. Coordination must flow strictly through the deterministic ledger and structured capability tokens.
3. **DO NOT BUILD: Vector DB / Semantic Memory for Scan State (pgvector)**
   - *Reason:* Vulnerability verification is exact, discrete, and relational. Semantic similarity search cannot prove that an auth token is valid or that an SQL injection payload fired. PostgreSQL relational tables (`ledger_cell`, `findings`, `capability_tokens`) provide exact deterministic guarantees.
4. **DO NOT BUILD: ZAP as a Core Primary Vulnerability Detector**
   - *Reason:* Legacy DAST scanners generate 40%+ false positive noise. ZAP should only serve as an optional early recon signal provider; it must never directly confirm or close ledger cells without deterministic exploit verification.
5. **DO NOT BUILD: Intercepting Proxy as the Central Coordination Substrate**
   - *Reason:* Running all worker traffic through a heavy local proxy introduces TLS interception fragility, socket bottlenecks, and complex state synchronization. Standard toolserver egress with selective HAR capture on confirmed proof paths is lighter and more resilient.

---

## 4. Implementation Tickets (Module-Level, Flag-Gated, No Exploit Steps)

### Ticket T1: Roll Out Rolling Batch Pool & Active Stuck Watchdog
* **Target Modules:** `src/scanner/agent_runtime/engine/father.py`, `src/scanner/config.py`.
* **Flag Gate:** `SCANNER_ENGINE_BATCH_DISPATCH=true`, `SCANNER_ENGINE_STUCK_WINDOW_S=120`.
* **Changes:** Set batch pool dispatch as default; enable progress-driven watchdog with 120s window. Hook `on_done` cell release on every worker finish.
* **Verification:** Unit test simulating worker stall verifies worker is preempted within 120s and its cells re-queued.

### Ticket T2: Stop Finalize Untested Cell Mass-Retirement
* **Target Modules:** `src/scanner/agent_runtime/finalize.py`.
* **Flag Gate:** `SCANNER_FINALIZE_RETIRE_UNREACHED=false` (Default OFF).
* **Changes:** Remove the bulk update of `state='untested'` cells to `'attempted'` with reason `'unreached'`. Untested cells remain in `untested` state so scan summaries honestly report unfinished scope.
* **Verification:** Finalize integration test confirms open cells retain `untested` status in database and report.

### Ticket T3: Implement Capability-Token State Machine for Exploit Chaining
* **Target Modules:** `src/scanner/agent_runtime/chain/tokens.py` (new), `src/scanner/agent_runtime/chain/service.py`, `src/scanner/agent_runtime/engine/father.py`.
* **Flag Gate:** `SCANNER_CHAIN_TOKENS_ENABLED=true` (Default OFF).
* **Changes:** Add `CapabilityToken` dataclass and persistence in `/work/tokens/`. Inject token paths and structured credentials into Hop N+1 worker shard. Update `findings` schema with `parent_finding_id`.
* **Verification:** Mock chaining test confirms Hop 2 receives Hop 1 token artifact and produces linked finding with `parent_finding_id`.

### Ticket T4: Multi-Step Interactive Browser Worker API
* **Target Modules:** `docker/browser/browser_server.py`, `src/scanner/agent_runtime/tools/browser.py`.
* **Flag Gate:** `SCANNER_BROWSER_INTERACTIVE=true` (Default OFF).
* **Changes:** Implement `/session/new`, `/session/act`, `/session/snapshot`, and `/session/auth/dump` endpoints. Enable cookies and localStorage persistence.
* **Verification:** Playwright integration test navigates mock two-user SPA and detects BOLA state transition.

### Ticket T5: Filter OOB Local Control Probes & Interactsh Buffer Scoping
* **Target Modules:** `src/scanner/agent_runtime/oob/service.py`.
* **Flag Gate:** `SCANNER_OOB_FILTER_CONTROLS=true` (Default ON).
* **Changes:** Filter incoming OOB callbacks against worker egress IPs and designated control canary IDs. Only callbacks initiated by external target servers are admitted as SSRF evidence.
* **Verification:** Mock test verifying worker self-curl to OOB domain is discarded from `findings.jsonl`.
