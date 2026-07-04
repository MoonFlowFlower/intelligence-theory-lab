# SESSION-HANDOFF-FSP-20260701 — Program Init + N0 Queue

- Session scope: design + governance only. ZERO experiments executed, ZERO evidence produced, ZERO commits made. Everything below is file-level work awaiting the S0 freeze ceremony.
- Claim ceiling: bounded offline mechanism evidence under specified trace/replay/ablation/baseline contracts. Nothing in this session moves any claim.
- Next session should read this file + `FSP-STAGE-LEDGER.md` first; the memory index entry [FSP route program 001A] is the cross-session pointer.

## 1. What exists now (all created/updated 2026-07-01, all UNCOMMITTED)

| File | Role | Status |
|---|---|---|
| `docs/research/FSP-ROUTE-PROGRAM-001A-functional-subject-proxy-route-design.md` | 5-route program design + frontier scan + Amendment A (GPT-pass reconciliation: adopted 6 / rejected 6) | design memo |
| `docs/research/FSP-ROADMAP-CONTINGENCY-001A.md` | N0–N4 spine; per-node F/B/C/T fallbacks; fallback laws L1–L7; weight reallocation; program-death condition | design memo |
| `docs/research/FSP-ENV-DESIGN-CONSTRAINTS-001A.md` | environment validity constitution (8 laws, Gap matrix 1/2a/2b/3/4, parity contract incl. offline-compute, latent-depth test hierarchy, should-win certificates, terminal vocabulary + gap_certificates, fatal invalidators, redesign invariants) | AUTHORIZED-BINDING; sha to be recorded at S0 commit; then read-only/supersede-only |
| `docs/task_cards/FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A.md` | N0 card incl. Revision R1 (gap_certificates, Gap-2b one-sided test, regimes, truncation-ideal, NULL env, surface-remap, metered costs) | AUTHORIZED-FOR-IMPLEMENTATION (operator, in-session); freeze pending |
| `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md` | Codex handoff: stages S0–S6, WBS, D1 design decision, one-loop-closure definition, standing loop protocol | ACTIVE, waiting for Codex |
| `docs/research/FSP-MASTER-PHASE-PLAN-001A.md` | P0–P3 (+P4 out-of-scope) phase structure + Amendment A1 (exit-mode splits, per-subgate P1 gates, P0.4 hard preconditions, no-lookahead boundary, skeleton horizon = phase+1) | ACTIVE |
| `docs/research/FSP-STAGE-LEDGER.md` | append-only state source, rules v2 (entry types; only operator-accepted transition_decision opens gates); entries L-000..L-002 | ACTIVE — the single source of stage truth |
| `docs/research/FSP-LADDER-MEMO-001A.md` | target decomposition (4 properties × 3 levels) + C1–C6 candidate registry with killer control baselines + phenomenal-tier scaffold (§4, non-evidence) | DESIGN-ONLY, program-level, opens no gate |
| `docs/codex/contracts/MECHANISM-SIGNATURE-VERDICT-STANDARD-001A.md` | candidate-verdict classification standard (phase plan Amendment A2 formalized): signature S1–S5, LOW_SCORE_SIGNATURE_PRESENT / HIGH_SCORE_NO_ATTRIBUTION, guards G1–G4; CLAUDE.md contracts list updated (additive) | ACTIVE standard; applies to P1+ candidate cards, NOT to N0 |

## 2. Current state (= ledger L-002)

- Phase 0. Two tracks: Track T (TLGP) / Track F (FSP).
- P0.1: TLGP rung1 trainability scout RUNNING (Codex, Track T). Latest banked anchor before this session: HEAD `b812552` (capacity sweep 001A = INVALID_optimization_confound; corrective lineage 002A).
- P0.2: N0 (`FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A`) AUTHORIZED-QUEUED behind Codex attention.
- P0.3 retro, P0.4 rung3 rerun (conditional, hard preconditions in phase plan), P0.5 SBMC/RIA design cards: all gated.
- rung3 is NOT abandoned: it waits on P0.1's recipe verdict as a GPU background job (Track-T's own banked identifiability certification is its env gate, not N0).

## 3. Immediate queue (in order)

1. P0.1 scout verdict lands → operator appends ledger transition_decision (L-003).
2. If recipe validated → check P0.4 preconditions (phase plan §P0.4) → rung3 powered rerun as GPU background job.
3. Codex main thread → N0 execution plan S0: freeze ceremony — scoped commit of the FSP docs + card; record canonical shas (3-way identity: live sha == freeze record == file-API readback); author `frozen_design.json` with zero TBD fields.
   - Pre-S0 host hygiene: clear stale `.git/index.lock` (seen again this session); ignore FUSE EOL-churn " M" noise (host is clean; verified CLAUDE.md diff = 276+/276− whole-line churn).
4. S1–S5 implementation + certification run per execution plan (CPU-only; D1: θ on 4-level grids, ≈4^8 atoms, vectorized filter).
5. S6: independent hostile audit by Claude — NEW SESSION, provide artifacts path `artifacts/FSP-PUM-ENV-IDPROBE-001A/`. Auditor ≠ implementer is deliberate and standing.
6. Operator bank ceremony → route strictly per `FSP-ROADMAP-CONTINGENCY-001A` §N0 (PASS → authorize N1 execution-card drafting; FAIL → Plan B 001B structural redesign; INVALID → instrument fix, redesign budget untouched; INCONCLUSIVE → powered rerun).

## 4. Standing invariants (compressed; full text in the governing docs)

- Ledger is the only stage truth; gates open on artifact pointers + matching adjudicator verdicts, never on narrative. No stage opens by confidence.
- Every new card carries `stage: Px.y / ledger: L-nnn` in its header; auditor checks this first.
- No-lookahead: executable/threshold-bearing material only after its gate opens (then frozen immediately); NON-EXECUTABLE skeletons allowed within phase+1.
- Thresholds/battery/claim ceiling never move post-freeze; instrument failures void results and consume no redesign budget; max 2 structural redesigns per node then mandatory terminal bank; every chain ends in a bank.
- Roles: Codex implements; Claude audits (does not implement); operator authorizes, appends ledger, banks. No mixed commits across Track T / Track F.
- Candidate verdicts (P1+) are classified by MECHANISM-SIGNATURE-VERDICT-STANDARD-001A: absolute score is never a gate; control separation is non-negotiable; signature sets freeze at card time; claims never flow product→science.
- C1–C6 (ladder memo) are P2/P3-gated registry entries; interventional ones (C1/C4/C5/C6) each require a candidate-free identifiability probe before any card. C6 has a safety red line: empathic coupling touching any manipulation/engagement/dependency objective = hard stop, not redesign.

## 5. Evidence-status marks for the next session

- Everything FSP in this session = design-level, uncommitted, no artifacts.
- TLGP lineage claims (rung0 pass, rung3 headroom, powered rung3 config-limited negative, sweep INVALID) = banked in repo at/behind `b812552`, previously independently audited.
- G4B / CreatureState / product-attribution = report-level only (not found in this repo); LRGG lineage = repo-verified.
- Frontier scan citations (Dreamer 4, V-JEPA 2, SuRe, LongMemEval/PrefEval, FANToM/EnactToM, Letta, Zep, EFE-as-VI, AdA) = external claims, unverified in-lab; listed in route-program §14.

## 6. Housekeeping

- Auto-memory index (MEMORY.md) is over its size budget → run a consolidate-memory pass in some idle session.
- The FSP memory topic file `fsp-route-program-001a.md` is current through this session, including this handoff pointer.
