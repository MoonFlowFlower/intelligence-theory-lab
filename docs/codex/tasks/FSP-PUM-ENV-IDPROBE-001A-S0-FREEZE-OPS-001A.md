# FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A — S0 freeze ceremony, operational card

stage: P0.2 / ledger: L-002 (P0.2 AUTHORIZED-QUEUED; this card executes the pending S0 step)

STATUS: READY FOR EXECUTION (Codex, host-side session on the Windows machine, repo at `D:\Project\AIProject\MyProject\intelligence-theory-lab`). Operator should be reachable during the session for two sign-offs (§6 step 2, §8).

Session bootstrap prompt for Codex:
> Read `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md` and execute it exactly. It is an operational instantiation of stage S0 of `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md`. Stop at any stop condition and report. Do not touch anything related to the running TLGP rung1 job.

## 1. Task id

FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A

## 2. Problem definition

Execute stage S0 (T0.1 + T0.2) of the N0 execution plan: put the entire uncommitted FSP governance stack into git history in one scoped Track-F commit, author `frozen_design.json` with zero TBD fields, and establish canonical shas with a 3-way identity check, so that N0 implementation (S1+) can start against frozen, read-only rule sources.

This card adds NO new protocol. Governing sources, read-only during execution:

- `docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md` (the card, incl. R1)
- `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md` (the constitution)
- `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md` §S0 (the plan)

If any instruction below appears to CONTRADICT those sources, stop and report — do not resolve the conflict yourself. (Two known ambiguities are resolved in §5/§6 below with rationale; those resolutions were prepared by the auditor and require no further judgment.)

## 3. Current stage / layer

Governance operation (engineering implementation layer). Produces no experimental evidence, moves no claim. Hypothesis / baseline / ablation / trace-replay: N/A — this is a freeze ceremony, not an experiment. The acceptance gate (§9) replaces them.

## 4. Preconditions and environment facts (verified 2026-07-01 by auditor)

1. HEAD was `b812552` on branch `codex/meta-theory-scaffold` at card-writing time. HEAD MAY legitimately advance if Track T banks rung1 results first — HEAD position is NOT a precondition and NOT a stop condition. Only staged-set discipline (§7.2) is. If HEAD advanced: verify the new commits are Track-T-scoped (`git show --stat <sha>`; no FSP files), then remove from the §7.2 allowlist any path already committed by Track T (e.g. CLAUDE.md) and note the removal in freeze_record.json.
2. `.git/index.lock` handling — DISAMBIGUATION PROTOCOL (replaces the original one-liner; added after run-1 stop):
   a. Enumerate live git processes WITH command line and creation time: PowerShell `Get-CimInstance Win32_Process -Filter "Name='git.exe'" | Select-Object ProcessId,CreationDate,CommandLine` (or `wmic process where "name='git.exe'" get processid,creationdate,commandline`).
   b. If a git process exists: check its creation time. If it predates the current session by hours AND the index/staged set is not changing (`git --no-optional-locks diff --cached --name-only` twice, 60s apart, identical), it is a hung/leftover process → operator kills it, then proceed to (d).
   c. If it is recent/active: identify the owner (ask the Track-T Codex session whether it issued the command). If Track T is banking rung1: WAIT for its ceremony to complete its own scoped commit, then verify per §4.1 and proceed to (d). If no session claims the process → treat as (b).
   d. Only when zero live git processes remain: inspect `git --no-optional-locks diff --cached --name-only`; if anything is staged, `git reset` (unstages only, working tree untouched), re-verify empty; then delete the stale `.git/index.lock`; then proceed.
   e. Never delete the lock while any git process is live.
3. The TLGP rung1 FULL_RUN job is writing large artifact files into the working tree right now (`artifacts/.../FULL_RUN/trace.jsonl`, `val_curves.jsonl`, …). These are Track T. Any of them entering the staged set is a mixed-commit governance failure.
4. ~700 tracked files show as modified due to CRLF/LF presentation churn only (`git diff --ignore-cr-at-eol` is empty for them). Do not stage them; do not be alarmed by them.
5. CLAUDE.md REAL diff (ignoring EOL) must be exactly ONE additive bullet: the `MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md` line in the contracts list. KNOWN TRAP: the Cowork sandbox's bash view of CLAUDE.md is truncated mid-file (ends at "Claude mus"). The host file is complete. You are on the host, so you should see the full file — VERIFY: the file must end with the Preflight Audit Rule section including the six-item graph-cache challenger list (`graph_lookup … episodic_traversal`). If your view of CLAUDE.md is truncated or the diff deletes that tail: STOP. Do not commit a truncated CLAUDE.md.
6. Record `git config core.autocrlf` (and `core.eol` if set) into freeze_record.json for provenance. Do not change git config.
7. Commit identity: use `-c user.name="Zhouyu" -c user.email="moonlight1939300864@gmail.com"` on the commit command. Do not mutate repo config.

## 5. T0.2 first — author frozen_design.json (before the commit)

Ordering rationale (auditor-resolved ambiguity #1): the card's STATUS line requires the freeze record to cover "this card + constitution + frozen_design.json", so `frozen_design.json` must exist and be sha-pinned BEFORE the freeze commit. Plan numbering T0.1/T0.2 is a list, not a temporal order.

- Path: `artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json` (per card §Expected artifacts).
- Content: every field enumerated in plan §S0 T0.2 and card §Environment design + §Hypothesis + R1 items 2–6. Zero TBD fields. Specifically:
  - Fixed by card (NOT choosable — copy exactly): K=8 topics; ≥2 preregistered interaction pairs (name the pairs); 2 sensitivity flags; θ_probe subset (≥3 dims incl. both sensitivity flags); N_heldout=200; 10 env seeds (list the literal seeds); sessions 20×15; thresholds ideal ≥.80, fair_max ≤.60, headroom mean ≥.15, LCB ≥.10, action-gap ≥.10, saturation sentinel .95, camouflage-off decoder ≥.80 / on ≤.60; four terminal states + gap_certificates vocabulary by reference to constitution §10 (no local copy of the vocabulary table).
  - Choosable NOW within card/constitution constraints (choose, write one-line rationale each in an adjacent `design_choices_rationale.md`, then frozen forever): trust α/β ranges; disclosure d; z_t AR(1) coefficients; probe costs c_i and m (number of probes); MI feature families (single symbols, n-grams to k=3, per-session aggregates) + δ; decoder family spec (≥3 named architectures + tuning budget); fixed-probe schedule grid + UCB scheduler spec; Gap-3 truncation form last-B-tokens with literal B; evaluation regime per gap (Gap-1/3 LOG-PARITY, Gap-2a/2b ON-POLICY — fixed by R1, restate literally); RNG event-log scheme; memory/offline-compute metering fields (R1 item 6); battery membership list (additions later allowed, deletions forbidden — mark the list "append-only").
- Validator: `tests/fsp_pum_env/test_frozen_design.py` — schema check (all required keys present, no null/TBD/placeholder values, thresholds match the card's literals exactly). Run it; it must pass. This validator is itself committed (allowed path per card §Rollback).
- FORBIDDEN: any threshold value differing from the card's H1 literals; any "TODO/TBD/null" placeholder; any second copy of the terminal-vocabulary table.

## 6. Pre-commit file preparation

1. Verify file integrity via full reads (you are host-side; still check tails):
   - CLAUDE.md tail check per §4.5.
   - Card ends with "Notes for implementer (Codex)" section; constitution and plan read completely.
2. ONE textual reconciliation in the card, WITH operator sign-off in-session (auditor-resolved ambiguity #2): the R1 section header reads "(2026-07-01, pre-freeze; card still DRAFT — NOT AUTHORIZED)" which contradicts the STATUS line and ledger L-002 (authorization included R1). Change that parenthetical to "(2026-07-01, pre-freeze; authorized 2026-07-01 together with the card — see STATUS line)". This is a drafting-order leftover, not a substantive change; fix it BEFORE freeze because after freeze the card is read-only and the contradiction becomes permanent. If the operator is not reachable: leave the text unchanged, record the inconsistency in freeze_record.json under `known_textual_inconsistencies`, and proceed — do not block the freeze on wording.
3. Append the freeze block to the card (new final section `## Freeze record (S0, 2026-07-xx)`), containing:
   - blob shas (computed via `git hash-object -- <file>`) of: constitution, execution plan, frozen_design.json;
   - the line: "This card's own blob sha and the freeze commit sha are recorded in artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json and in ledger entry L-004 (self-reference is resolved there, not here)."
4. Compute the card's own blob sha (`git hash-object` AFTER step 3's edit).
5. Author `artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json`: blob shas of card, constitution, plan, frozen_design.json; autocrlf/eol config values; the R1-reconciliation note (applied or deferred); commit sha field left as `"pending"` and filled in step §7.4 (this is the ONLY field allowed to be provisional, and only until §7.4).

## 7. The freeze commit (T0.1)

1. Delete stale `.git/index.lock` (after §4.2 check).
2. Scoped staging — stage EXACTLY these 15 paths, one `git add` with explicit paths, never `git add -A` / `git add .`:
   - `CLAUDE.md`
   - `docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md`
   - `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md`
   - `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S0-FREEZE-OPS-001A.md` (this card)
   - `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md`
   - `docs/research/FSP-LADDER-MEMO-001A.md`
   - `docs/research/FSP-MASTER-PHASE-PLAN-001A.md`
   - `docs/research/FSP-ROADMAP-CONTINGENCY-001A.md`
   - `docs/research/FSP-ROUTE-PROGRAM-001A-functional-subject-proxy-route-design.md`
   - `docs/research/FSP-STAGE-LEDGER.md`
   - `docs/research/SESSION-HANDOFF-FSP-20260701.md`
   - `docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md`
   - `artifacts/FSP-PUM-ENV-IDPROBE-001A/frozen_design.json`
   - `artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json`
   - `tests/fsp_pum_env/test_frozen_design.py` (+ `design_choices_rationale.md` if placed under artifacts/FSP-PUM-ENV-IDPROBE-001A/ — then 16 paths; list it explicitly)
   Then `git status --porcelain --cached` (or `git diff --cached --name-only`) must list exactly this set. Anything extra (especially any TLGP/FULL_RUN artifact or any of the ~700 EOL-churn files) → unstage or STOP.
3. Commit with message:
   `docs(freeze): FSP N0 S0 freeze — governance stack committed, frozen_design.json zero-TBD, canonical shas in freeze_record.json (Track F only; card R1 header reconciled per operator sign-off / deferred; CLAUDE.md +1 additive contracts bullet)`
   using the identity flags from §4.7.
4. Write the commit sha into freeze_record.json's `commit_sha` field, then amend — NO. Do not amend (append-only discipline). Instead: `commit_sha` goes into the LEDGER entry and into a tiny follow-up commit of freeze_record.json alone (`docs(freeze): record S0 commit sha in freeze_record`). Two commits total, both scoped, both Track F. The FIRST commit is "the S0 freeze commit"; the follow-up is bookkeeping.
5. Frozen-vs-committed distinction (record in freeze_record.json): FROZEN (read-only / supersede-only from now on): card, constitution, execution plan, frozen_design.json. COMMITTED-BUT-LIVING: ledger (append-only), phase plan, roadmap, ladder memo, route program, signature standard, CLAUDE.md, handoff, this ops card.

## 8. Post-commit: 3-way identity verification + ledger

1. For each of: card, constitution, plan, frozen_design.json —
   (a) fresh read of the file from disk → `git hash-object -- <file>`;
   (b) sha recorded in card freeze block / freeze_record.json;
   (c) `git ls-tree <freeze-commit-sha> -- <file>` blob sha.
   All three must be identical per file. Any mismatch → STOP, this is an instrument failure (freeze NOT achieved); do not delete the commit; report.
2. Append to `docs/research/FSP-STAGE-LEDGER.md` a `transition_proposal (proposed, appended-by: Codex)` at the NEXT FREE entry number (L-004 if nothing landed since L-003; if Track T's rung1 verdict transition takes L-004 first, use L-005 — numbers are never reused):
   `L-nnn | <date> | P0.2 ACTIVE (proposed) | S0 freeze complete: commit <sha> (+ bookkeeping commit <sha2>); canonical blob shas in artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json; card+constitution+plan+frozen_design now read-only; S1 (sealed simulator) may start per execution plan. | evidence: freeze_record.json`
   ONLY the operator can then append the matching `transition_decision (accepted)` — that is what actually opens S1. Note: L-003 is already occupied by the A2 observation; the handoff's "L-003" pointer is stale.
3. Commit the ledger append (scoped, ledger file only) together with or after the operator's decision entry, per operator preference.
4. Recommended (operator action, not Codex): push the branch from the host (`git push`) for off-machine durability; prior freeze practice published hashes for third-party verifiability.

## 9. Acceptance gate

ALL of:
- Freeze commit exists, staged set was exactly the declared list, zero Track-T files included.
- frozen_design.json passes its validator with zero TBD/placeholder fields; thresholds byte-match the card's H1 literals.
- 3-way identity holds for all four frozen files.
- CLAUDE.md committed complete (tail intact) with exactly one real additive bullet.
- Ledger carries the L-004 proposal (and, for S1 to open, the operator's accepted decision).

## 10. Stop conditions

- Live git process while index.lock exists → stop.
- CLAUDE.md truncated on host, or its real diff ≠ exactly the one additive bullet → stop, report verbatim diff.
- Any TBD/null/placeholder remaining in frozen_design.json → stop (nothing to freeze).
- Staged set ≠ declared list; or any TLGP/FULL_RUN/EOL-churn file staged → stop.
- Any threshold literal in frozen_design.json differing from the card → stop (governance).
- Any edit to constitution or execution plan content (the card's freeze-block APPEND and the single R1-header parenthetical per §6.2 are the only permitted card edits; zero edits to the other two) → governance-self-modification, stop.
- 3-way identity mismatch → stop.
- Anything requiring interpretation of the governing sources beyond §5/§6's two pre-resolved ambiguities → stop and ask.

## 11. Rollback plan

- Abort BEFORE commit: revert the card freeze-block/R1 edits (file-level), delete draft frozen_design.json / freeze_record.json / validator; repo history untouched.
- Failure AFTER commit: do NOT delete or rewrite the commit (append-only history). Append a `blocking_finding` to the ledger; the freeze is simply not achieved; a corrected follow-up commit supersedes. No redesign budget is consumed (instrument/ceremony failures void, they don't count).

## 12. Claim ceiling

This ceremony produces governance state only (frozen rule sources + provenance record). It produces zero experimental evidence and moves zero claims. Everything under the program claim ceiling: bounded offline mechanism evidence only; no consciousness / subjectivity / emotion / autonomy / agency / companion-readiness claims.

## 13. Required final report (from Codex, end of session)

Files changed; commands run; the two commit shas; the four canonical blob shas; validator output; staged-set listing proof; R1 reconciliation applied or deferred; stop conditions triggered (if any); explicit confirmation that no TLGP file was touched.

## 14. Changelog

- 2026-07-01: card authored (auditor: Claude).
- 2026-07-02 run-2 preflight stop + v2 pivot (SUPERSEDES §4.2's lock-deletion step and §7's porcelain staging; `scripts/s0_freeze.ps1` v2 is authoritative for commit mechanics): operator observed git.exe PIDs CHANGING across enumerations — the processes are not hung leftovers but periodic `git add -u` snapshots from the live rung1 agent harness. Consequence: the stale `.git/index.lock` is currently the only thing PREVENTING those snapshots from flooding the shared index with Track-T dirt; deleting it (original plan) would open a mixed-commit race. v2 route: do NOT kill the processes, do NOT delete the lock, never touch the shared index — the whole ceremony runs on a private `GIT_INDEX_FILE` via plumbing (`read-tree` → `add` → `write-tree` → `commit-tree` → `update-ref` with compare-and-swap on the old HEAD, so a concurrent Track-T bank commit causes a clean CAS abort, never an overwrite). Ledger commit uses the same route (`scripts/s0_ledger_commit.ps1`). Shared-index cleanup (delete lock + `git reset`) is deferred until the rung1 session has ended.
- 2026-07-02 run-2 reassignment: operator elected to execute S0 personally (execution plan already defines S0 as "operator + Codex"; fully compliant). The four hung git.exe processes (created 00:13, `add -u` with agent-harness config signature, blocked by the pre-existing stale lock, staged set empty throughout) are killed by the operator before the ceremony. Claude (auditor) drafted the committable inputs at operator request — frozen_design.json (+ rationale + validator, validator PASS), the card freeze-block/R1 edits, and `scripts/s0_freeze.ps1` which performs asserts + sha computation + scoped commits host-side. Auditor-drafting of frozen_design is disclosed inside frozen_design.json and design_choices_rationale.md; S6 audit treats it as auditor-co-authored input. Operator approval = running the script after review.
- 2026-07-02 run-1 STOP (correct stop, preserved as failure evidence): Codex halted pre-edit on §10 — `.git/index.lock` present while live git processes ran, including a broad `git add -- ...` over many dirty paths incl. TLGP artifacts (owner unidentified at stop time). Nothing staged, nothing committed, no files created. Codex confirmed before stopping: HEAD `b812552`, CLAUDE.md real diff = exactly one additive bullet, CLAUDE.md tail intact, `core.autocrlf=true`, target dirs did not pre-exist. Sandbox-side cross-check after the stop: staged set empty, `.git/index` unchanged since Jul 1 19:44, lock = the old zero-byte one. Card revisions in response: §4.1 (HEAD may advance; allowlist shrinks if Track T commits shared paths first), §4.2 (lock/process disambiguation protocol), §8.2 (next-free-L-number instead of hardcoded L-004). autocrlf=true is safe for the 3-way check as specified (HEAD blobs are LF; `git hash-object -- <path>` applies the same filters as `git add`).
