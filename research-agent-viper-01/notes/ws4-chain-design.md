# WS-4 — Chaining State Machine Design (research-agent-viper-01)

Sources: A (capabilities.py, chain/floor.py, chain/service.py, escalation.py, ledger/service.py). DESIGN ONLY — capability labels, no payloads.

## Current chain mechanism (as-built, code-verified)
- Capability enum (11): internal_http, db_read, credential, session, rce, cross_principal_read, file_read, metadata_access, cloud_storage, pii_read, redirect (capabilities.py:22-33).
- Static GRANTS map: confirmed vuln_class → capabilities (capabilities.py:38-72; 24 classes grant).
- Static ENABLES map: capability → vuln_classes reachable/worse (capabilities.py:77-88).
- HIGH_IMPACT gates escalation (capabilities.py:96-98).
- Chain floor: deterministic follow-on probes from a confirmed primitive — SSRF→IMDS metadata / bucket-list, LFI→secret-file, redirect→SSRF(OOB), credential→reopen classes (chain/floor.py:232-404). Fires ≤40 hops/run (floor.py:102), dedup by (cap,url,param) seen-set across waves.
- Escalation: rebuild graph, find new HIGH caps, reopen unlocked classes, spawn capability-aware wave whose prompt gets "You now HAVE `cap` via finding 'title' (endpoint)" (father.py:1658-1725, 1520-1548).
- executed_chain finding writer composes prose PoC from source+hop (chain/floor.py:204-228).

## Gap (the H3 defect, precisely)
"Capability" is RECOMPUTED from vuln_class each time; there is no persisted capability-token carrying (a) the proof artifact refs, (b) preconditions met, (c) which cells it unlocks, (d) replay recipe. Hop N+1 gets PROSE (title+endpoint line in a prompt), not a typed artifact; its own output is a fresh standalone finding, not linked as evidence-of-next-hop. Graph rows (chain_node/chain_edge) carry rationale strings, not evidence references (chain/service.py build_graph).

## Proposed: Capability Token Contract (flag `SCANNER_CHAIN_TOKENS`, default OFF)
1. **Token entity** (`chain_token` table; or JSONL `/work/capabilities.jsonl` first): `{token_id, capability, origin_finding_id, evidence_ids[], scope_host, acquired_at, ttl, state}` where state ∈ {held, consumed, expired, revoked(scope-loss)}.
2. **Mint**: a finding flips a cell to `confirmed` (machine-proof only; ties into oracle_first) → mint tokens from GRANTS[class] with `evidence_ids = finding.evidence_ids`. Deterministic, no LLM.
3. **Consume**: when Father spawns an escalation/batch wave, unlocked cells are claimed WITH their enabling tokens; the worker task receives the token's evidence artifact paths (not prose), persisting the hop's output evidence_ids back onto the edge.
4. **Edge materialization**: chain_edge rows gain `source_token_id, target_finding_id, proof_kind ∈ {oob_callback, inband_diff, render_execution, replay_match}` + `replay_recipe_id` (pointer into evidence objects, executable by finalize for re-proof).
5. **Report narrative**: `render chain = path over tokens: "we found X (E#12) → granted SESSION (T#3) → proved Y (E#27)"`, yielding the buyer story "we found X, which proved Y, which enabled Z" with artifact-level links.
Buyer-visible outcome: an Executed-Chain section where every hop carries replayable evidence, not a graph diagram.

## Failure/termination semantics
- Tokens bounded per scan (`SCANNER_CHAIN_TOKEN_CAP`, default e.g. 64); TTL = scan lifetime; scope-loss revokes (host dropped from scope).
- Reuses existing convergence: each (cap,url,param) hop still fires once (seen-set), PLUS each token is consumed once per target class set.
- Flag OFF ⇒ today's GRANTS/ENABLES + prose path, byte-identical.
