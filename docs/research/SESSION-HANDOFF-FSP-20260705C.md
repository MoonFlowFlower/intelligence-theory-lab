# SESSION HANDOFF — FSP — 2026-07-05C

Branch: `codex/meta-theory-scaffold` · Banked HEAD: `70cdf7e` (remote == local, verified this session).
Prior handoff: `SESSION-HANDOFF-FSP-20260705B` (S3d v0 tombstone closure, pre-audit).
Full lineage: `MEMORY.md` current-front (FSP route program 001A).

## One-line status
S3d v0 is tombstoned + banked (`70cdf7e`). P0 / PUM-ENV DECIDED closed as `INVALID_INSTRUMENT`; N1 gated behind an admission probe. Two decision cards are DECIDED but **NOT YET BANKED** (untracked in the working tree); a Codex bank instruction is pending.

## What this session did
- **Audited the S3d v0 tombstone closure → ACCEPT** (independent re-derivation from committed blobs at `397df12`): NULL ideal `0.07211` > limit `0.03625` (18/18 non-ideal members pass); the 3 cert cells match `s3d_v0_closure_record.json` byte-for-byte; `nearest_neighbor 0.162` > assigned `seq_window 0.075` = **2.16×** denominator-free; only N2-degenerate (constant) + N3-fragile `rag` rows pass. No-delete held (0 file deletions; run-1 STOP recoverable at `d983b59`; resume STOP preserved under `_v1`); commit scoping clean; claim ceiling clean across card / closure_record / decision_log. Git `improper chunk offset` = FUSE/pack artifact (native `fsck` clean).
- **Workflow change (operator, solo policy):** operator signatures WAIVED; Codex may now bank (commit + push); Claude → post-bank check. `70cdf7e` is the signature-waiver commit — banked+pushed by Codex, post-bank checked by Claude (remote == local, scoped to 2 files, evidence commits `afda452b`/`397df12` unchanged). Memory `itl-bank-workflow-operator-run` rewritten to reflect this (07-03 rule superseded).
- **Route + admission decided (operator delegated to auditor, authorized 2026-07-05 "你勾就行,我同意授权"):**
  - `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-P0-ROUTE-DECISION-POST-S3D-001A.md` → **A+C**: close P0 / PUM-ENV as `INVALID_INSTRUMENT`; reallocate cheapest-unblocked → clear Track-T L-005 bank.
  - `docs/codex/tasks/N1-ADMIT-IDENTIFIABILITY-001.md` → **NEEDS_ONE_MINIMAL_PROBE**, target `TLGP-LEARNABILITY-FLOOR-DIAG-001`. Deliberately NOT `ADMIT` — the controllable-variable advantage over a fair meta-baseline is not yet stateable on paper.

## Standing research finding (carry forward)
The PUM-ENV S3d tombstone is another confirmation of the **identifiability ceiling** (PUM-ENV joins LRGG Tier0-2). Under equal access, identifiability is a property of the access regime and is handed to the fair baseline. The only unclosed live line = a **cross-episode reusable prior that beats a fair META-baseline** — NOT a weak per-episode extrapolator (TLGP-001A's 0.80 headroom was measured vs the weak one and does not transfer). Sharpened this session: the candidate's advantage must live in a **named agent-controlled variable** —
- advantage in `M/U` (passive cross-episode prior) → a fair amortized meta-learner gets the same prior → presumed ceiling-blocked;
- advantage in `A` (active query / intervention policy) → possibly non-tautological, but only vs a fair UCB / max-info-gain policy with a pre-declared double-dissociation (this is route P1.5, EFE-vs-UCB).

So the honest N1 target may be an **active-policy** target, not passive prior decoding. See memory `itl-why-no-qualified-mechanism-testbed-identifiability-ceiling` (2026-07-05 addendum).

## Repo state / uncommitted
- **Banked HEAD `70cdf7e`** (pushed; remote == local).
- **UNTRACKED + decided (NOT banked):**
  - `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-P0-ROUTE-DECISION-POST-S3D-001A.md` (selection A+C filled in)
  - `docs/codex/tasks/N1-ADMIT-IDENTIFIABILITY-001.md` (selection NEEDS_PROBE filled in)
  - `docs/research/SESSION-HANDOFF-FSP-20260705C.md` (this file)
- Pre-existing unrelated dirty/untracked worktree residue — leave untouched (not this task's scope).
- Standing debts: `273137f` 162-file preserve commit (on remote, unaudited-scope); Track-T L-005 pending bank; ~13M EOL-churn debt (isolated from S3d).

## Next actions (ordered)
1. **Run the pending Codex bank instruction** (from the 2026-07-05C chat). Commit 1 = the 2 decided cards + ledger transition (`FSP-STAGE-LEDGER`: P0.2 → INVALID_INSTRUMENT; N1-admission → NEEDS_PROBE) + `decision_log` + **this handoff file**; Commit 2 = Track-T L-005 (Fork C, report-first / stop-if-ambiguous). Then push. Claude post-bank checks.
2. **Resolve compute posture for the diagnostic:** is `TLGP-LEARNABILITY-FLOOR-DIAG-001` CPU-feasible at diagnostic scale, or does it need explicit Track-T GPU authorization? (TLGP-001B was GPU; FSP side is CPU-only per spec §6.) This gates the diagnostic execution card. Claude offered to investigate CPU-feasibility.
3. **Draft `TLGP-LEARNABILITY-FLOOR-DIAG-001` execution card** once posture is set: decide whether TLGP-001B's failure was a real learnability floor or a positive-control defect (`control ≡ real`). Mandatory: fair cross-episode meta-baseline (not weak extrapolator), positive-control fix, full baseline family (random/majority, episode-only lookup, NN/graph-cache, amortized learner, oracle upper bound, ablated-memory, shuffled-family leakage control), budget + stop + claim ceiling. Design-only until authorized.

## Claim ceiling
Bounded offline route/admission evidence only. Established: S3d / PUM-ENV v0 is not a qualified S4/N1 downstream instrument. NOT proven: mechanism absence; any theory (Bio-CMBC / CVPSM / VCCO / CMBC / R-G) true or false; that the cross-episode line has real headroom (unknown until the diagnostic runs); N1 readiness; EGO / agency / autonomy / consciousness.

## Role for the next session
Claude = independent auditor + card-drafter (per CLAUDE.md). Operator = flat delegation, solo policy: no signatures; Codex banks (commit+push) under scoped/git-reset discipline; Claude post-bank checks; positive-claim banks still get a pre-bank Claude look. Do NOT run the TLGP diagnostic without an authorized execution card (compute posture + budget + stop).

> CORRECTION 2026-07-05C: the 'P0/N1 not yet banked' statement above is stale. P0 route decision + N1 admission are banked at cbd8a2e (ledger L-005). Host worktree confirmed dirty; preserved via this session's STEP 0 commit.
