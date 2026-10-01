# WS-1 Throughput & Scan-Time Audit — Evidence Notes (agent: research-agent-lynx-01)

## Code facts (branch feat/alpha-observability, HEAD == 1c5551d for src/docker; verified git diff --stat = 0 lines)

### Wave-loop skeleton (father.py run() 1727-1930)
recon.run -> _ensure_auth (auth bootstrap worker, default ON) -> while True:
  1. _materialize_surface (DB: ingest inventory + materialize cells) [father.py:1766, 837-850]
  2. _sync_work_to_db (ingest findings.jsonl -> DB + sync_from_work resolve + census + dedup) [father.py:1767-1770, 888-967]
  3. wrap_up break [1773]
  4. _sample_open + _write_recon_json + write_scan_brief (full /work re-read each wave) [1775-1781]
  5. _boss_tick (gated OFF by default) [1787]
  6. progress measurement: _unresolved_reading + _distinct_confirmed_count [1793-1811]
  7. _is_complete (count_open + count_applicable: second loads ALL cells joined) [1817]
  8. Governor.decide -> quiescence: break only if decision=="partial" AND NOT _has_claimable() [1841-1852]
  9. pending discovered targets -> wave_targets; elif wave < max_waves(3) -> deepen; else break [1853-1867]
  10. _claim_worklist(worker_id="wave{N}") -> reclaim_expired_leases + claim_cells(limit=fanout*12) + board [1874, 1178-1198]
  11. build_specs (one worker per phase-group per target) [1876-1886]
  12. batch_dispatch gated (default OFF) -> _run_batch_pool(run_pool + preempt + on_done-release); else legacy _run_floor_and_fleet (fleet.run_all = gather) [1898-1901]
  13. ran_a_wave=True; wrap_up break [1902-1909]
  14. _run_chain_floor (gated OFF) [1914]
  15. _run_channel_sequences (gated OFF) [1917]
  16. _run_escalation (default ON) [1922]
after loop: _spawn_smoke_workers unless complete/drain [1927-1928]

### Key timing constants (all verified)
- SCANNER_ENGINE_WORKER_WALL_S default 5400 = 90 min per-worker hang guard [fleet.py:28]
- gather barrier: run_all = asyncio.gather over ALL specs -> wave waits for slowest worker (up to 90 min) [fleet.py:121-122]
- run_pool (rolling slots + preempt + on_done release) ONLY behind scanner_engine_batch_dispatch (default False) [fleet.py:124-161; father.py:1898; config.py:437]
- max_waves default 3 [father.py:427]
- escalation re-loop default ON, max 3 rounds, EACH spawns a full build_specs gather (up to 90 min/round) [father.py:1658-1725, 479-484]
- SCANNER_ENGINE_SYNC_INTERVAL_S default 120 [config.py:384]
- fanout default 6 [config.py:377]
- Governor runaway wall 21600s = 6h default (ON), invocations off [context.py:102-116]
- attempt cap 3 -> terminal 'attempted' on release/lease-reclaim [ledger/service.py:1237-1247, 1444-1473]
- lease = wall+600s = 100 min default [ledger/service.py:1232-1234]
- COMPLETE_RATIO 0.98 [ledger/service.py:1181]
- WATCHDOG_STALE_SECONDS 180 [poller.py:111]
- OOB provisioning caps 60s start + 30s self-test [run.py:99-100]

### Claim/release mechanics
- claim_cells: SELECT FOR UPDATE SKIP LOCKED, stamps claimed_by=worker_id, state=testing, attempts+1 [ledger/service.py:1349-1441]
- release_cells(worker_id): WHERE claimed_by=:worker AND state IN (untested,testing) [1444-1473]
- release_cells_by_ids(cell_ids): WHERE cell_id=ANY(...) [1476-1505]
- B1 historical bug CONFIRMED in code comments: batch cells claimed under "wave{N}" but released by batch worker_id -> 0 rows freed; patched via _batch_cells dict + release_cells_by_ids [father.py:774-777, 1345-1362; ledger/service.py:1476-1483]
- LEGACY path (batch_dispatch OFF = default): wave claims under "wave{N}", NO on_done release exists in run_all path -> unresolved claimed cells stranded until lease expiry (~100 min) unless lease expired; reclaim_expired_leases only clears PAST-lease cells [father.py:1874, 1189-1190; fleet.py:121-122]
- escalation path: claims under esc_wid, releases by same esc_wid (consistent) [father.py:1698-1723]

### Historical incidents documented in code comments
- "12h runaway": recon expansion unbounded (inserted>0 always progress) [father.py:436, 447]; fixes flag-gated default OFF (_recon_expansion_rounds, _expansion_budget) [father.py:430-450]
- "600s thrash": flat batch budget killed weak models with 0 resolved [father.py:517-521, 1380-1383]; batch budget + stuck window now default 0 = disabled
- "resolve.update_unmatched — the biggest hidden leak in the 12h runaway" [father.py:110, 949]
- OOB start burned ~7 min (poll loop past deadline) [run.py:96-98]
- Governor budget "reading a hardcoded 0 before this was wired" [fleet.py:44-46]

### Quiescence
- father._has_claimable: FAIL-CLOSED (error -> True -> keep working) [father.py:1428-1441]
- BUT: if governor decision=="partial" AND claimable>0 -> falls through to claim+dispatch; loop STILL breaks at max_waves (else: break, father.py:1866-1867) even with claimable cells remaining -> untested remainder at budget exhaustion
- quiescence break (partial + not claimable) works only within wave budget

### Resolve/close invariants (ledger/service.py)
- tested_clean requires >=2 distinct methods AND >=1 evidence (or weapon_swept) [991-1009]
- confirmed requires evidence/proof only when oracle_first ON (default OFF) [896-911, 205-227]
- idempotency guard: never downgrade resolved/pending cells [970-971]
- C1 collision fix: full-identity list matching (url + api_operation resolve together) [785-819]
- unmatched updates/findings logged+skipped (update_unmatched) [947-950]

### Poller
- _watchdog_once: for EACH cell stuck 'testing' >180s -> publish scan.method_switch event PER CELL + bump last_progress [poller.py:1126-1173]
  -> flood: 34,796 method_switch events in scanner-cp logs (observed); ALSO bumps last_progress which the father's stuck-detection reads (cells_last_progress) -> cross-component interference neutering stuck-detection when enabled
- publish_event = Redis pub/sub + debug log line each [ws/events.py:29-39]
- poller scan close: SIGTERM -> grace -> SIGKILL; kill_scan_containers idempotent [poller.py:942-980]
- 53 worker_runs rows stuck "running" all-time (killed workers never closed) [DB query]

## Server telemetry (ssh abhedi, 2026-09-30/10-01, READ-ONLY)
- Containers: scanner-cp, scanner-postgres(+pgbouncer), scanner-redis, scanner-frontend, logging-proxy, browser-*, toolserver-*, zap-*, scanner-agent-84aea81a7e43 (LIVE scan running), vulnerableapp target
- Volume: abhedi_red_scanner_data -> /var/lib/docker/volumes/.../_data (host ls permission denied for admin; readable via docker exec scanner-cp, mounted /var/lib/scanner)
- Scan status distribution (tenant_xbow.scans): cancelled 19, completed 18, failed 4, partial 1, running 1
- method_switch flood: 34,796 events (first 19:36:57 for scan 38c703c0, flooding for 84aea81a); ~10-23 events per 5s window
- Live scan 84aea81a (started 20:08, 2h+): recon 214s; exploitation running; ledger: 6248 na + 1704 testing + 941 tested_clean + 321 untested + 18 confirmed + 5 blocked (~9237 cells); findings 42; evidence_object 38; chain_node 39; chain_edge 58
- Completed scan a0e78406 (~21 min wall 19:53-20:14, operator close at 20:08): recon 108s; workers: auth-bootstrap-bunny ok 97s 0/0; batch0-b-0/1/3 partial 121s 0 findings 0 resolved; b-2/b-7 partial 241s; b-4/b-5/b-6 "running" FOREVER (never closed - killed at close without worker_runs close); exploit-floor ok 0s 4 findings
- a0e78406 ledger: 1184 na + 154 attempted + 57 blocked + 3 confirmed, 0 tested_clean, 0 untested; ALL 154 attempted cells have evidence_ids = EMPTY (has_ev=f)
- a0e78406 ledger_updates.jsonl (101 lines): blocked 100, tested_clean 1 -> ~43 blocked declarations unmatched (100 updates vs 57 blocked cells) - silent-discard leak confirmed in live data
- agent_messages: 84aea81a: 69 msgs, 30 agents, max_turn 7, tokens 0/0 (engine path records NO token usage); a0e78406: 2 msgs 2 agents max_turn 1 tokens_in 1,141,543 (single-agent path records tokens)
- worker_runs ALL-TIME: error 578 (avg 139s), partial 75 (avg 281s), ok 267 (avg 1465s=24min, max 6685s=1h51m), running 53 (never closed)
- Worker error top: "ChatCompletion response has no choices (possible provider error payload)" = 471 (DOMINANT); 429 rate limits ~91; "preempted: worker backstop 0s exceeded" 13 + "worker wall cap 0s exceeded" 3 (SCANNER_ENGINE_WORKER_WALL_S=0 misconfiguration period -> wait_for(timeout=0) instant death; 0 not treated as disabled in fleet.py:12-28)
- OOB: 84aea81a has 317 interactions + 740 registry entries (OOB plumbing WORKS); a0e78406 has 5 interactions
- exploit-floor worker_run: dur 0s, findings 4 (floor runs in-process, not a real container)
