# research-agent-mako-02

- **AI_NAME:** research-agent-mako-02
- **Base research folder:** C:\Users\ASUS\Desktop\abhdeii\autocan\improvment-research\research-agent-mako-02
- **Mission:** Abhedi Red architecture audit & design (MASTER RESEARCH DIRECTIVE, FINAL)
- **Mode:** READ-ONLY research, evidence-backed. No payloads, no exploit steps. All writes confined to this folder only.
- **Branch of record:** feat/alpha-observability (directive cites `1c5551d`; working-tree HEAD is `f75608f` — delta is docs-only; audit runs against the working tree per R2 code-is-ground-truth).
- **Sources confirmed available:** A codebase (`../`), B `../competitor-research/`, C live server (`ssh abhedi`, READ-ONLY; live scan `84aea81a7e43` observed), D public web.
- **Method:** distributed swarm via the Workflow tool. Gating honored: WS-1 + WS-3 first → WS-2/4/5/6 → WS-7 synthesis last. Every claim carries an Evidence Ledger row: `[CODE] file:line | [QUERY] cmd+result | [COMPETITOR] file | [DOC] section | [INFER]`. Confidence: HIGH/MEDIUM/LOW/UNVERIFIED.
- **Competitive stance:** win on accuracy, proof quality (real file:line + live-server [QUERY] rows), and mechanism-level recommendations (module + flag + buyer outcome). No fabrication.
- **Started:** 2026-10-01

## Folder map
- `ws1_throughput/` — scan-time attribution, ranked throughput defects
- `ws2_telemetry/` — forensics from ledger/oob/agent logs (aggregate)
- `ws3_competitor/` — competitor mechanism extraction + market gap
- `ws4_chain_statemachine/` — chain state machine + proof-carry design
- `ws5_intelligence_layer/` — per-tick planner contract + plan gate
- `ws6_surface_browser/` — browser worker contract + oracle designs
- `ws7_synthesis/` — final deliverable (Section 9 structure)
- `evidence/` — raw [QUERY] outputs, aggregated metrics (secrets redacted)
- `notes/` — working notes, plan, running log
