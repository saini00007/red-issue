# WS-1 · Throughput & scan-time audit — question list + evidence table

## Questions → answers (one line each, full proof in LEDGER C1-C12, Q1-Q4)
1. Where do waves spend time? Dispatch + worker tool-time dominate; sync is concurrent background
(father.py:1100,1397); claim/materialize single txns; floor concurrent with tail-await.
2. Claim/release worker_id mismatch → zero-row releases? YES on batch path by construction, documented in
code (service.py:1477-1483), fixed via by-ids; legacy run_all has NO release call; floor NEVER releases.
3. Quiescence reads fail open? NO — fail closed (False / True), break needs ran_a_wave && saw_open.
4. 90-min wall dominates? NO — last-resort backstop (fleet.py:12-28); stuck-watchdog + plateau stop first.
5. Terminal attempted cells? Via attempt-cap absorb (service.py:1556-1570) + finalize retire of unprobed
remainder (finalize.py:444-467, gate default ON); 321 untested + 1704 leased remain on latest scan.

## Time-attribution table
| Stage | Mechanism | Share | Source |
|---|---|---|---|
| materialize | per-wave ingest, idempotent dedup | small | father.py:1766, ledger 611-697 |
| sync | background create_task, throttled, best-effort | overhead, non-gating | father.py:1077-1106,969-1075 |
| claim | 1 atomic CTE txn/wave (+1/floor family) | negligible | service.py:1393-1418 |
| dispatch | pool rolling live; legacy gather barrier | DOMINANT (structure) | fleet.py:121-161 |
| floor | concurrent, tail-await, 1500/500s budgets | secondary, bounded | father.py:1228-1243 |
| worker tools | 5418 calls/scan, curl 49.5% | DOMINANT (clock) | [QUERY] ws2b.sql |
| finalize | single terminal pass + A1 verifier | one-shot | run.py:341-366 |

## Ranked defects by blast radius
1. Floor never releases (~1.6k cells stranded/scan) — exploit_floor.py (no release_*), [QUERY] Q3.
2. Legacy run_all never releases (whole-wave leases to ~100-min expiry) — father.py:1898-1901.
3. B1 batch zero-row release — FIXED via by-ids (service.py:1477-1483; father.py:1358-1362).
4. batch_satisfied({})==True + cell_states hiccup→{} can preempt healthy worker — batch.py:64-68.
5. 0.98 complete ratio + stop_on_probe widen "complete" — service.py:1181-1200,1144-1148.
6. 3 stale running worker_runs (GC gap) — [QUERY] Q4.
