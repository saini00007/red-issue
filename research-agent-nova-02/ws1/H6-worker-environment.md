# H6 — Worker environment is under-specified → context bloat + duplicated work

**Audit mode:** READ-ONLY code audit of `C:\Users\ASUS\Desktop\abhdeii\autocan`.
**Hypothesis under test:** *"The worker container's world (skills, /work layout, inter-process
signaling) is under-specified and causes context bloat and duplicated work."*
**Sub-claims:** (a) under-specified `/work` world · (b) context bloat · (c) duplicated work.

**Tag legend** — `[CODE] file:line` = read directly in this repo · `[MEASURE]` = value produced by
running repo code read-only in this session · `[INFER]` = reasoned from code, not directly observed ·
`[UNVERIFIED]` = could not be established from the repo.

---

## 1. Verdict summary

| Sub-claim | Verdict | One-line reason |
|---|---|---|
| **(a) `/work` world is under-specified** | **PARTIAL (confirmed on contract, refuted on "chaos")** | No typed artifact contract exists anywhere (`WORK_ARTIFACTS`/`Artifacts`/`WorkLayout` = not found in repo); every path is a string literal; the only prose contract (`AGENTS.md`) is **not baked into the container image**; two prompts issue *contradictory* instructions for the same files. But the world is **bounded**: every shared artifact has explicit caps and one canonical regenerated view (`scan_brief.md`). |
| **(b) causes context bloat** | **CONFIRMED (mechanism), bounded (magnitude)** | Worker prompt = 17,504-char methodology system block + ~1.1k OOB block `[MEASURE]`, plus task-side brief (up to 13,198 chars `[MEASURE]`) + up to ~9,300 chars of inlined skill body `[MEASURE]`; the brief is **delivered twice** (inline in task *and* as `read_file("/work/scan_brief.md")`); reprompts re-feed the whole transcript. The code itself names this "the context-bloat guard CLAUDE.md warns about" `[CODE] agents_runtime.py:206,214` — i.e. bloat is a *known, patched-around* property, not a non-issue. |
| **(c) causes duplicated work** | **PARTIAL** | Cell-level coordination is real and strong (`SELECT … FOR UPDATE SKIP LOCKED` + lease + attempt cap) `[CODE] ledger/service.py:1349-1441`, so "workers duplicate work because nothing coordinates them" is **refuted at the cell layer**. Duplication survives *below* that layer: no probe/command dedup across workers (dedup cache is per-run, read-only-only) `[CODE] agents_runtime.py:255-263,496,609-614`; `record_coverage` carries **no claim/worker ownership** `[CODE] agents_runtime.py:687-702`; the re-sync idempotency guard omits `attempted`/`na` so terminal cells can be re-opened `[CODE] ledger/service.py:970-971`; the `prior_methods` handoff is **advisory prompt text only** `[CODE] ledger/service.py:1429-1441` → `father.py:360-371`. |

**Overall H6: PARTIAL-CONFIRMED.** The environment is *under-specified as a contract* (a),
that under-specification *does* produce measurable prompt bloat (b, confirmed), and duplication is
real but **not** caused by absent coordination — it is caused by (i) the absence of a claim
*identity* in what workers write back, (ii) a reopen hole in the resolve guard, and (iii) an
advisory-only blackboard (c).

---

## 2. Sub-claim (a) — is the `/work` world under-specified?

### 2.1 No typed contract — searched, not found
| Search (repo-wide) | Result |
|---|---|
| `WORK_ARTIFACTS\|ARTIFACT_\|class WorkLayout\|LAYOUT` in `src/` | **No files found** `[CODE grep]` |
| Dedicated `/work` layout section in `docs/APPLICATION_CONTEXT.md` | **None** — only incidental inline mentions (lines 70, 144, 155, 317) `[CODE grep]` |
| `AGENTS.md` baked into agent image | **No** — `docker/agent/Dockerfile` COPYs only `pyproject.toml`, `uv.lock`, `src/`, `docker/agent/*.sh`, `skills/`, `entrypoint.sh` (lines 20,23,34,40,55,60); no `AGENTS.md`, no `docs/` `[CODE]` |
| `/work` contract in `docker/agent/entrypoint.sh` | Only volume/symlink mechanics (lines 4-9, 13-30); no file inventory `[CODE]` |

So the *only* document that describes `/work` (`AGENTS.md:11-15`, prose: `GOAL.md`,
`findings.jsonl`, `decisions.log`, `notes/`, `scripts/`, `tool_outputs/`) **never reaches the
worker container.** What the worker actually gets is (1) prose embedded in the system/task prompts
and (2) whatever it discovers by globbing.

### 2.2 The contract is scattered literals, with writers/readers spread across 20+ modules
`findings.jsonl` alone is referenced at (writers first):

- **Writers:** `agents_runtime.py:663-682` (`write_finding` tool, no `target` key emitted),
  `tools/files.py:59` (append-only guard for `write_file`), `exploit_floor.py:2411`,
  `recon_floor.py:710,758`, `chain/floor.py:220`, `oob/service.py:522`, `browser_ingest.py:294`,
  `ingest_findings.py:364` (`sync_zap` appends), `entrypoint.py:653` (`.touch`),
  plus the single-agent path writing it ad-hoc from the model via `Write`/bash `[INFER]`.
- **Readers:** `ledger/service.py:1051`, `ingest_findings.py:180-207,377`, `scan_brief.py:256`,
  `father.py:573,909,944`, `chain/service.py:53`, `finalize.py:144,774,951`,
  `agents_runtime.py:287-288`, `close_sweep.py:65`, `poller.py:1341`, `api/routes/scans.py:331`,
  `planner/specialist.py:132`, `hooks/stop_gate.py:110`, `claude_sdk.py:34` `[CODE]`.

`ledger_updates.jsonl` is symmetric (`agents_runtime.py:702`, `exploit_floor.py:2372`,
`tools/files.py:59`, `ledger/service.py:1052`, `scan_brief.py:257`, `finalize.py:832`,
`poller.py:1397`, `agents_runtime.py:1015`, `planner/specialist.py:133` `[CODE]`).

**There is no single module that enumerates these**, so "who may write what" is enforced only by
convention + two partial guards (`tools/files.py:59` append-only set).

### 2.3 Contract drift is handled reactively, by ad-hoc tolerance
- The methodology prompt tells agents to key coverage on **`element`**; the resolver must accept
  `endpoint` as an alias or "every agent-authored coverage line is silently counted unmatched"
  `[CODE] ledger/service.py:933-936` (comment written *after* the bug).
- `write_finding` emits **no `target`**, so the ingest parser is deliberately "lenient on
  `target` since the agent often forgets to include it" `[CODE] ingest_findings.py:193-195` vs
  `agents_runtime.py:666-681`.
- Validation of `findings.jsonl` is two `obj.get()` truthiness checks + a severity normalizer,
  **no schema type** `[CODE] ingest_findings.py:196-206`; `rejected.jsonl` mirrors it with a
  different required key (`reason`) `[CODE] ingest_findings.py:210-230`.

### 2.4 Two subsystems give contradictory instructions for the same shared file
| Source | Instruction |
|---|---|
| `engine/methodology.py:62-64` (fleet worker system prompt) | "**NEVER** write `findings.jsonl` or `ledger_updates.jsonl` with [write_file] — it **truncates** and, **under the fleet, workers share one file, so a write wipes other workers' results**. Use `write_finding`/`record_coverage`." |
| `planner/specialist.py:40-42` (planner specialist prompt) | "…then **append a line to `/work/ledger_updates.jsonl`** … Confirmed vulns go to **`/work/findings.jsonl`**." |

Same artifact, two prompts, opposite channels (tool vs shell append) `[CODE]`. This is the sharpest
single piece of evidence for (a): the shared-file hazard is *known* (it is written down as a warning
in one prompt) yet the other prompt still routes the model at the raw file.

### 2.5 What stops this from being unbounded (refutation side of "PARTIAL")
- One **canonical, regenerated, capped** view exists and is rebuilt each wave:
  `scan_brief.write_scan_brief` `[CODE] scan_brief.py:249-292`, called at
  `father.py:1266,1504,1558,1709,1781`, `context.py:201`.
- Hard caps on it: `_MAX_ENDPOINTS=30, _MAX_OPEN_CELLS=12, _MAX_FINDINGS=20, _MAX_TARGETS=10,
  _MAX_DIGEST=25, _MAX_OPERATOR_CONTEXT=1500` `[CODE] scan_brief.py:30-43`.
- Worklist capped at `_WORKLIST_MAX = 12` `[CODE] father.py:173,358`.
- `write_file` **cannot** truncate the shared JSONLs: `_APPEND_ONLY = {"findings.jsonl",
  "ledger_updates.jsonl"}` `[CODE] tools/files.py:59` — i.e. the hazard the methodology prompt
  warns about is already mitigated in the engine path (the warning is partly stale; the specialist
  path has no such guard).

**(a) = PARTIAL.** Under-specified as a *contract*: confirmed (no schema, no in-image doc,
contradictory prompts, alias/leniency patches). Under-specified as *unbounded chaos*: refuted —
the world is explicitly capped and single-sourced through `scan_brief.md`.

---

## 3. Sub-claim (b) — does it cause context bloat?

### 3.1 Measured component sizes `[MEASURE]` (repo code, run read-only this session)

| Component | Value | Source |
|---|---|---|
| `DEEP_OFFENSIVE_VAPT` (fleet worker system prompt) | **17,504 chars** (≈4.4k tokens) | `methodology.py:13` |
| OOB instruction block appended to instructions | ≈1.1k chars | `agents_runtime.py:920-929` |
| Per-phase inlined skill block (header + bodies) | ≈**9,300 chars/group** (cap: `_SKILL_BLOCK_CHARS=9000`, per-skill `max(1200, 9000/len(names))`) | `father.py:182-183,274-293` |
| `skills/` catalog on disk | **70 files, 647,328 bytes** | `skills/**` |
| `scan_brief` synthetic worst case | **13,198 chars** | `scan_brief.build_scan_brief` |
| `scan_brief` minimal | **719 chars** | same |
| Open-cells worklist | ≤12 lines (`_WORKLIST_MAX`) | `father.py:173,358-372` |
| Single-agent orchestrator system prompt | **22,809 chars** (≈5.7k tokens) | `orchestrator.build_orchestrator_prompt` |
| builtin playbook prompts | 22,990 / 26,355 chars | `orchestrator.BUILTIN_PLAYBOOK_PROMPTS` |

**Rough per-worker prompt envelope** `[INFER, from the measured parts]`: ≈17.5–19k chars system +
≈1–13k brief + ≈9.3k skills + ≈1.5k worklist/capability ≈ **30–43k chars ≈ 8–11k tokens per task**,
re-sent on every dispatch.

### 3.2 The bloat is structural, not incidental
1. **The brief is delivered twice.** `write_scan_brief()` returns the string and `_task_for`
   **prepends it** to the task `[CODE] father.py:597-613,1266,1277-1280`; the *same* system prompt
   simultaneously orders `read_file("/work/scan_brief.md") "before anything else"`
   `[CODE] methodology.py:17-21`. `scan_brief.py:10` documents the inline prepend; the
   file-read entry point `read_scan_brief()` is **dead code in production**
   `[CODE CLAUDE.md:98 → scan_brief.py:267-295]`. So the worker carries the brief inline *and* is
   told to fetch it again.
2. **Skill bodies are inlined, not progressively disclosed, on the fleet path.** `CLAUDE.md:118-122`
   advertises "~600 tokens system prompt; only YAML frontmatter loads at startup", but
   `_skills_block` **slices SKILL.md bodies straight into the task**
   `[CODE father.py:274-293]`. The single-agent path's progressive-disclosure claim does not
   describe the engine workers.
3. **Reprompts re-send everything.** "Each reprompt re-feeds the FULL prior transcript
   (`result.to_input_list()`)" with only a per-tool-output cap of `_REPLAY_TOOL_OUTPUT_CAP=4000`
   `[CODE agents_runtime.py:212-235]`, up to `max_reprompts` default 6
   `[CODE agents_runtime.py:809]` × `max_turns` default 40 `[CODE agents_runtime.py:326-331]`.
   The comment states outright that accumulated bodies "balloon the context window".
4. **The repo calls this out as bloat, twice, in code:**
   - `agents_runtime.py:206` — "_CONTENT_CAP … the context-bloat guard CLAUDE.md warns about"
   - `agents_runtime.py:214` — "…balloon the context window (the bloat CLAUDE.md warns of)"
5. **Prompt cost is an operational parameter.** `docker-compose.override.yml:30` —
   `SCANNER_ENGINE_BATCH_MAX_CELLS: "6"  # … amortizes GLM's re-sent prompt across more cells
   (2 was too small for a non-caching model)` `[CODE]`: cells are batched specifically to amortize
   a prompt that is re-sent per batch.
6. **Only the single-agent path has a token-based reset** (`_CONTEXT_RESET_TOKENS = 150_000`
   `[CODE] entrypoint.py:122-133`); the engine worker path bounds itself by *turn/reprompt counts*
   only `[CODE] agents_runtime.py:809,326-331` — no token-budget reset exists there
   `[CODE grep: no MAX_PROMPT / prompt_budget in src]`.

**Mitigations that cap (but do not remove) the bloat:** brief caps (`scan_brief.py:30-43`),
`_SKILL_BLOCK_CHARS=9000` (`father.py:183`), `_WORKLIST_MAX=12` (`father.py:173`),
`_CONTENT_CAP=8000` (`agents_runtime.py:210`), `_REPLAY_TOOL_OUTPUT_CAP=4000`
(`agents_runtime.py:218`), `handle_output` head-spill to `tool_outputs/` with an on-disk pointer
(`tools/output.py:51-75`), `_MAX_SECTION=4000` verbatim cap per untrusted brief section
(`boss.py:100`).

**(b) = CONFIRMED.** The bloat mechanism is present, quantified, self-documented in code, and only
*bounded* by caps — the caps are themselves evidence that the unbounded form was observed.

---

## 4. Sub-claim (c) — does it cause duplicated work?

### 4.1 What coordination DOES exist (refutes the strong form)
- `claim_cells` claims a disjoint batch in one transaction with
  `SELECT … FOR UPDATE SKIP LOCKED`, stamps `claimed_by` + `lease_expires_at`, bumps `attempts`,
  and requires `applicable = true AND state IN ('untested','testing') AND attempts < cap`
  `[CODE ledger/service.py:1349-1441,1393-1416]`. Its own docstring: "the S4 keystone that kills
  worker overlap by construction."
- Releases/leases: `release_cells` (`service.py:1444`), `release_cells_by_ids` (`:1476`),
  attempt cap folded into terminal `attempted` (`:1450,1460-1461,1551-1559`).
- Family-scoped claiming for the escalation wave `claim_family_cells`
  `[CODE engine/attack_surface.py:123]`, used at `father.py:1701-1703` (guarded by
  `hasattr(...)`), alongside `claim_cells:115`, `claim_cell:39`, `release_cells:152`,
  `release_cells_by_ids:162`.
- **Findings** are deduped at DB level: `dedup_hash` + merge key check before insert, logged
  `finding.duplicate_skipped` `[CODE tools/findings.py:397-410]`.
- Redis is used for **tool-slot concurrency** (global semaphore, Lua acquire/release,
  `release_all_for_scan`) and API throttling — not for work distribution
  `[CODE global_semaphore.py, workers_sem.py]`.

### 4.2 Where duplication survives — 4 concrete mechanisms

**(c1) `record_coverage` carries no claim identity.** The line written is exactly
`{endpoint, vuln_class, state, methods, evidence, reason?}` — **no `cell_id`, no `worker_id`, no
lease token** `[CODE agents_runtime.py:687-702]`. `claim_cells` *returns* `cell_id`
(`service.py:1415,1436`) but the coverage tool never consumes it, so resolution is by
`endpoint+vuln_class` string match only `[CODE ledger/service.py:946-950]`. Any worker can (and the
prompt tells it to) write coverage for any cell — including one another worker currently holds.
Consequence: cross-worker writes are indistinguishable from the holder's, and unmatched identities
are dropped as `unmatched` `[CODE service.py:947-950]`.

**(c2) The re-sync guard omits terminal states → re-open → re-work.** The idempotency guard skips
only `("confirmed","tested_clean","blocked","pending_oracle","pending_human")`
`[CODE ledger/service.py:970-971]`. Any later `sync_from_work` pass (poller/salvage/stop-gate paths
`[CODE service.py:964-967,1041-1060]`) whose replayed line fails the redundancy/probe/oracle gates
sets `cell.state = "testing"` `[CODE service.py:1004,1018,1023]` — and `claim_cells` accepts
`'testing'` `[CODE service.py:1399]`. Terminal `attempted`/`na` cells (written only by SQL paths,
`service.py:1460-1461,1492-1493,1559`) are therefore reopenable, and each reopen costs a fresh
`attempts+1` until the cap. Neither the loader (`_load_cells_with_identity` filters on `scan_id`
only — no `applicable`, no state) nor the update loop carries an `applicable` check
`[CODE service.py:700-710, 930-1028]`.

**(c3) No probe/command-level dedup — only per-run, read-only-only.** `_shell_seen` is a dict
**inside the tool-builder closure** (per worker run) `[CODE agents_runtime.py:496,609-614]`, and its
eligible set is `cat/ls/grep/head/tail/…` only; "a NAMED probe/exploit (curl, nmap, sqlmap, …) must
NEVER be cached" `[CODE agents_runtime.py:255-263]`. Two workers handed overlapping endpoints
re-run identical probes by design; there is no cross-worker probe ledger.

**(c4) The anti-duplication handoff is advisory prompt text.** `claim_cells` returns
`prior_methods` + `attempt` ("the last worker's effort carried forward") `[CODE service.py:1429-1441]`
and `_worklist` renders "[attempt N; prior workers tried: … go DEEPER …]"
`[CODE father.py:360-371]`. Nothing enforces it — the receiving model may ignore the line. Same for
the `prior_methods`/blackboard concept at `father.py:363`.

**Amplifiers (mechanism-adjacent):**
- `findings.jsonl` + `ledger_updates.jsonl` are **re-read in full on every sync pass**
  `[CODE service.py:1051-1053]`; dedup is per-row at insert, so CPU/log cost is O(lines × passes)
  even when 0 rows land.
- `run_shell` results are **never** shared between workers (only `_shell_seen` within one run).

### 4.3 Peer-measured magnitude (secondary, from WS-2 in this workspace)
`improvment-research/research-agent-nova-02/ws2/WS-2-telemetry-forensics.md` reports, from volume
forensics `[QUERY, peer]`: 9,105 ledger-update lines; **61–84% of endpoints re-written on the four
big scans** (max 80 writes for one endpoint); `"state":"attempted"`/`"na"` authored **0 times** by
agents (terminal states are SQL-written only); 117 inapplicable cells live in `testing`.
This audit did **not** re-run those queries `[UNVERIFIED by me]`, but independently **re-derived the
underlying code mechanism** (c2) at `ledger/service.py:970-971` + `:1004`.

**(c) = PARTIAL.** Coordination at the cell-claim layer is present and strong (refutes "no
signaling ⇒ duplication"); duplication persists because coverage/finding writes are **anonymous**,
the resolve guard **reopens** terminal cells, probes are **not** shared, and the cross-worker
blackboard is **advisory**.

---

## 5. Inter-process signaling (as asked by H6's framing)

Workers are **asyncio tasks inside one container**, not separate processes:
`FleetManager.run_all`/`run_pool` `[CODE engine/fleet.py:121,124]`. Signaling available:

| Channel | Used for | Not used for | Source |
|---|---|---|---|
| **Postgres** | work distribution (`SKIP LOCKED` claims), status polling, findings/evidence, `tool_invocations` | message bus | `ledger/service.py:1349`, `scheduler/poller.py` |
| **Redis** | global tool-slot semaphore (Lua acquire/release, `release_all_for_scan`), API throttle, **UI-only** pub/sub | worker↔worker work queue (no `blpush`/`xadd` queue found for dispatch) `[CODE grep]` | `global_semaphore.py`, `ws/events.py`, `telemetry.py:74` |
| **Shared `/work` volume** | blackboard JSONLs, `scan_brief.md`, `recon.json`, `tool_outputs/`, `close.json` marker | atomic coordination | `entrypoint.sh:4-30`, `worker.py:552-556` |
| **Signals** | `SIGTERM → grace → SIGKILL`, `close.json` dropped **before** SIGTERM so the wave loop can close-sweep | — | `poller.py:985-1001,1049-1089` |
| **`logs/agent.log`** | written by the **control plane** at teardown from `docker logs`, not by the worker process | live signaling | `poller.py:1442-1463`, `worker.py:552-555` |

Signaling exists and is layered; what is missing is any *contract* tying a worker's output records
back to the claim it was working under (see c1).

---

## 6. Evidence table

| # | Claim | Evidence (tag) |
|---|---|---|
| E1 | No typed `/work` artifact contract in repo | grep `WORK_ARTIFACTS\|Artifacts\|WorkLayout\|LAYOUT` → no files `[CODE]` |
| E2 | The prose contract never enters the container | `docker/agent/Dockerfile:20,23,34,40,55,60` COPY list lacks `AGENTS.md`/`docs/` `[CODE]` |
| E3 | `/work` setup is only symlink + perms | `docker/agent/entrypoint.sh:4-30` `[CODE]` |
| E4 | Artifacts are scattered literals (20+ modules) | findings.jsonl hits: `agents_runtime.py:663,288`; `ledger/service.py:1051`; `scan_brief.py:256`; `finalize.py:144,774,951`; `poller.py:1341`; `api/routes/scans.py:331`; `exploit_floor.py:2411`; `oob/service.py:522` … `[CODE]` |
| E5 | Contract drift patched by ad-hoc tolerance | `ledger/service.py:933-936` (`element` alias), `ingest_findings.py:193-206` (lenient `target`), `ingest_findings.py:210-230` (`reason` for rejected) `[CODE]` |
| E6 | Contradictory instructions for the same file | `engine/methodology.py:62-64` vs `planner/specialist.py:40-42` `[CODE]` |
| E7 | Append-only guard exists only for `write_file` | `engine/tools/files.py:59` `[CODE]` |
| E8 | Brief is canonical + capped | `scan_brief.py:30-43,249-292`; callers `father.py:1266,1504,1558,1709,1781`, `context.py:201` `[CODE]` |
| E9 | Worklist capped | `father.py:173,358-372` `[CODE]` |
| E10 | System prompt 17,504 chars | `methodology.py:13` `[MEASURE]` |
| E11 | Skills inlined into task, ≤9,000 chars/phase | `father.py:182-183,274-293` (per-skill `max(1200, 9000/n)`) `[CODE]`, block ≈9,300 chars `[MEASURE]` |
| E12 | Brief sizes | worst 13,198 / minimal 719 chars `[MEASURE scan_brief.build_scan_brief]` |
| E13 | Brief delivered twice (inline + `read_file` order) | `father.py:597-613,1266,1277-1280` + `methodology.py:17-21` `[CODE]`; `read_scan_brief()` dead `[CODE CLAUDE.md:98, scan_brief.py:267-295]` |
| E14 | Progressive disclosure claim doesn't hold on fleet path | `CLAUDE.md:118-122` vs `father.py:274-293` `[CODE]` |
| E15 | Reprompt re-feeds full transcript; caps only per-output | `agents_runtime.py:212-235` (`_REPLAY_TOOL_OUTPUT_CAP=4000`), `:809` (6), `:326-331` (40) `[CODE]` |
| E16 | Code names the bloat explicitly | `agents_runtime.py:206,214` `[CODE]` |
| E17 | Prompt re-send is an operational knob | `docker-compose.override.yml:30` `[CODE]` |
| E18 | No token-budget reset on engine path | grep `MAX_PROMPT\|prompt_budget\|max_prompt` in `src/` → only `finalize_enrich.py:36,415-417,513` `[CODE]`; reset exists only in `entrypoint.py:122-133` `[CODE]` |
| E19 | Cell claims are atomic & disjoint | `ledger/service.py:1349-1441` (`FOR UPDATE SKIP LOCKED`, lease, attempts, `applicable`, `state IN (...)`) `[CODE]` |
| E20 | Coverage writes carry no claim identity | `agents_runtime.py:687-702` (no `cell_id`/`worker_id`) vs `service.py:1415,1436` (cell_id returned but unused) `[CODE]` |
| E21 | Resolve guard reopens terminal cells | `service.py:970-971` (guard list) + `:1004,1018,1023` (sets `testing`) + `service.py:1399` (claimable) `[CODE]` |
| E22 | Terminal states are SQL-written only | `service.py:1460-1461,1492-1493,1559` `[CODE]` |
| E23 | No cross-worker probe dedup | `agents_runtime.py:255-263,496,609-614` `[CODE]` |
| E24 | Cross-worker handoff is advisory text | `service.py:1429-1441` → `father.py:360-371` `[CODE]` |
| E25 | Findings deduped at DB only | `tools/findings.py:397-410` `[CODE]` |
| E26 | Full-file re-read each sync | `service.py:1051-1053` `[CODE]` |
| E27 | Signals: SIGTERM/grace/SIGKILL + `close.json` first | `poller.py:985-1001,1049-1089` `[CODE]` |
| E28 | `logs/agent.log` written by control plane at teardown | `poller.py:1442-1463`, `worker.py:552-555` `[CODE]` |
| E29 | Workers = asyncio tasks in one container | `engine/fleet.py:121,124` `[CODE]` |
| E30 | `AGENTS.md` documents only 5–6 of the paths (and not in-container) | `AGENTS.md:11-15` `[CODE]` |

---

## 7. Evidence Ledger

| Claim | Source | Confidence | Notes |
|---|---|---|---|
| No typed artifact contract exists | grep across `src/` (E1) | High | Negative result; searched `WORK_ARTIFACTS`, `Artifacts`, `WorkLayout`, `LAYOUT` |
| Worker container never sees `AGENTS.md`/`docs/` | `docker/agent/Dockerfile` COPY list (E2) | High | Absence-of-file proof from image definition |
| Two prompts contradict each other on `ledger_updates.jsonl` | `methodology.py:62-64` vs `specialist.py:40-42` (E6) | High | Both are literal prompt strings in code |
| Fleet worker system prompt = 17,504 chars | `len(DEEP_OFFENSIVE_VAPT)` (E10) | High | `[MEASURE]`, reproducible |
| Skills block ≈9,300 chars/phase | `_skills_block` sizing + builder (E11) | High | Cap constant `9000` is code; measured per-group output |
| Brief worst-case 13,198 chars | `build_scan_brief(synthetic)` (E12) | Medium | Synthetic input; real scans sit lower (minimal 719) |
| Brief is double-delivered | task prepend + system prompt order (E13) | High | Both sides are code; the *cost* of the second read is `[INFER]` |
| Progressive-disclosure claim doesn't describe fleet path | `CLAUDE.md` vs `father.py:274-293` (E14) | High | Doc-vs-code divergence |
| Engine path has no token-budget reset | grep result (E18) | Medium | Negative grep; could exist in an SDK-level config not in `src/` `[UNVERIFIED]` |
| Cell claims are atomic/disjoint | `service.py:1349-1441` (E19) | High | SQL read directly |
| Coverage writes are anonymous | `agents_runtime.py:687-702` (E20) | High | Field list read directly |
| Resolve guard can reopen `attempted`/`na` | `service.py:970-971` + `:1004` + `:1399` (E21) | High | Mechanism proven in code; *frequency in production* is `[INFER]`/peer `[QUERY]` |
| No cross-worker probe dedup | `agents_runtime.py:255-263,496` (E23) | High | Cache scope + allow-list read directly |
| Handoff is advisory only | `service.py:1429-1441` → `father.py:360-371` (E24) | High | No code path enforces the rendered advice |
| 61–84% endpoint rewrite rate | WS-2 peer forensics (§4.3) | Medium | `[QUERY]` by peer, **not re-run here** — cited as corroboration only |
| Prompt cost drove a batching default | `docker-compose.override.yml:30` (E17) | High | Comment + value in shipped config |
| No work-dispatch queue in Redis | grep for queue ops (§5) | Medium | Negative grep; pub/sub + semaphore confirmed present |

---

## 8. Not found in repo (negative results)

1. Any artifact schema/type module for `/work` (`WORK_ARTIFACTS`, `WorkLayout`, `Artifacts`) — none.
2. Any `MAX_PROMPT`/`prompt_budget`/`max_prompt` token ceiling for engine workers — none in `src/`
   (only `finalize_enrich._MAX_PROMPT_ITEMS = 60`, an unrelated item cap).
3. `AGENTS.md` or `docs/` inside the agent image — none.
4. A dedicated `/work` layout section in `docs/APPLICATION_CONTEXT.md` — none.
5. `read_scan_brief()` production callers — dead code (`CLAUDE.md:98`).
6. Cross-worker probe/command dedup store — none (only per-run `_shell_seen`).
7. A Redis/queue-based work-dispatch bus — none (claims are DB `SKIP LOCKED`).

---

## 9. Limits of this audit

- All sizing numbers are **character counts from code**, not live token counts or live API payloads;
  token figures are `chars/4` estimates `[INFER]`.
- Production rewrite/reclaim *rates* come from the peer WS-2 `[QUERY]` report and were **not**
  re-executed here (read-only constraint on live volumes) `[UNVERIFIED by me]`.
- The single-agent (reprompt) path and the engine (fleet) path behave differently (skills discovery,
  context reset, brief handling); verdicts above apply primarily to the **engine fleet path**, which
  is what "worker container" denotes for current scans (`docker-compose.override.yml:1-5`,
  `worker.py:224-229`).

---

## 10. Final summary (10 lines)

1. **H6 verdict: PARTIAL-CONFIRMED** — (a) PARTIAL, (b) CONFIRMED, (c) PARTIAL.
2. The `/work` world has **no typed contract**: no schema module exists, paths are string literals
   spread across 20+ files, and the only prose spec (`AGENTS.md:11-15`) is **not in the container
   image** (`docker/agent/Dockerfile:20-60`).
3. Contract drift is handled reactively — an `element`/`endpoint` alias patch
   (`ledger/service.py:933-936`) and a deliberately "lenient" `target` (`ingest_findings.py:193-195`).
4. The sharpest under-specification: `methodology.py:62-64` forbids writing the shared JSONLs (it
   "wipes other workers' results") while `planner/specialist.py:40-42` orders exactly that append.
5. Context bloat is real and self-documented: 17,504-char system block `[MEASURE]` + ≈9,300-char
   inlined skills + a brief up to 13,198 chars **delivered twice** (inline + `read_file` order at
   `methodology.py:17-21`).
6. Reprompts re-send the full transcript (`agents_runtime.py:212-235`), capped only per tool output
   (4,000 chars, 6 reprompts, 40 turns) — and code comments literally call this "the context-bloat
   guard CLAUDE.md warns about" (`:206,:214`).
7. Duplication is **not** caused by absent coordination: cell claims are atomic
   (`FOR UPDATE SKIP LOCKED` + lease + attempt cap, `ledger/service.py:1349-1441`).
8. It *is* caused by three gaps: coverage writes carry **no claim identity**
   (`agents_runtime.py:687-702`), the resolve guard **omits `attempted`/`na`** so terminal cells
   reopen as claimable `testing` (`service.py:970-971,1004,1399`), and cross-worker dedup does not
   exist below the cell layer (per-run read-only cache only, `:255-263,496`).
9. The anti-duplication blackboard (`prior_methods`/attempt) is **advisory prompt text only**
   (`service.py:1429-1441` → `father.py:360-371`), which the WS-2 peer forensics corroborates with
   61–84% endpoint rewrite rates (peer `[QUERY]`, not re-run here).
10. **Fixable surface:** a typed `/work` artifact contract shipped in the image, coverage lines
    carrying `cell_id`/`worker_id`, extending the resolve guard to all terminal states, and a
    cross-worker probe ledger would each close one verified gap without changing orchestration.
