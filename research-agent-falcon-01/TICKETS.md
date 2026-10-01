# falcon-01 · WS-7 implementation tickets (module + flag; NO exploit steps)

Convention: T-ID · module(s) · flag (default OFF unless noted) · buyer outcome · evidence refs · done-gate.
All read-only-safe; none alters behavior when its flag is off (D4).

T-01 Floor work-stealing release · src/scanner/agent_runtime/engine/exploit_floor.py (drain end, per family) ·
SCANNER_FLOOR_RELEASE (OFF) · frees ~1.6k stranded cells/wave → faster scans, less expiry-attempted ·
LEDGER C3,Q3 · gate: stranded-lease count → ~0 on validation scan.
T-02 Legacy-path release + lease scoping · src/scanner/ledger/service.py (per-claim lease override) +
engine/father.py (on_done on run_all path) · SCANNER_LEGACY_RELEASE (OFF) · same outcome class as T-01 for
non-batch deploys · LEDGER C2,C8 · gate: wave-claimed cells re-claimable next wave.
T-03 Recon-triggered oracle packs · engine/recon_floor.py (witness) + engine/exploit_floor.py (drain gates) ·
SCANNER_GRAPHQL_AUTHZ / AUTH_ORACLES / CHANNEL_ORACLES / AI_REDTEAM (all OFF; two-layer AI gate kept) ·
oracle-closed cells carry proof_capsule → honest verified · LEDGER C29-C32,C39,C42 · gate: enabled-class cells
close with capsule + verification_status, never prose-only.
T-04 Boss tick enablement · engine/father.py:_boss_tick + plan_gate.py (cell-mapping rule) + playbooks/*.yaml
(weights) · SCANNER_ENGINE_BOSS (OFF) · live-board targeting, fewer duplicate dispatches · LEDGER C17,C18 ·
gate: claim-bias follows board; planner-down run byte-identical to prior plan.
T-05 Stale running-row reap · src/scanner/scheduler/poller.py · SCANNER_WORKERUN_REAP (default ON, marks
rows terminal past wall+margin; never deletes evidence) · honest Fleet view ·
LEDGER Q4 · gate: zero stale running rows post-scan.
T-06 Per-worker /work namespacing · src/scanner/scheduler/worker.py (spawn paths) · SCANNER_WORKER_NS (OFF) ·
triage speed, no behavior change · LEDGER Q11 (H6 note) · gate: zero new root-level probe files.
T-07 F3 observability hook · engine/runtimes/agents_runtime.py (transport event-hook, log-only) ·
SCANNER_MODEL_ERROR_LOG (default ON, telemetry only) · platform sees 429/5xx the proxy saw · LEDGER P1 ·
gate: rate-limit events in worker telemetry.
T-08 Capability tokens · chain/service.py + chain/floor.py + engine/father.py:_capability_context ·
SCANNER_CHAIN_TOKENS (OFF) · artifact-linked chains, verified-chain count up · LEDGER C20-C23 · gate: hop-2
findings reference hop-1 token ids; chain_node.attrs populated.
T-09 Executed-chain report bucket ON · config.py:249-254 + reporting.service · SCANNER_EXECUTED_CHAIN_FINDINGS
(OFF→ON per profile) · buyer attack story in report · LEDGER C39 · gate: bucket non-empty iff executed hops exist.
T-10 Proof-type enum promotion · db/models/tenant.py (read evidence_object.method) + api/schemas.py +
report builder · SCANNER_PROOF_TYPES (OFF) · case-file proof standard · LEDGER C24 · gate: report shows
per-finding proof type + verifier source.
T-11 Browser /act + /snapshot + gallery · docker/browser/browser_server.py + findings evidence binding ·
SCANNER_BROWSER_ACT (OFF) · new SPA proof class · LEDGER C27-C28 · gate: two-identity SPA authz proven on
validation target.
T-12 Deferred-confirm + two-identity BOLA packs · oob.service + exploit_floor · SCANNER_DEFERRED_CONFIRMATION /
SCANNER_TWO_IDENTITY_AUTHZ (OFF) · second-order + authz proof depth · LEDGER C39 · gate: deferred findings
carry reconcile provenance; BOLA findings carry planted-canary refs.

Explicitly NOT ticketed (D6): recursive hierarchies, generation-counter, agent-chat messaging, pgvector memory,
ZAP-as-detector, proxy-as-substrate, findings parent-column migration (see FINAL_REPORT §8).
