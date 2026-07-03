# SESSION-HANDOFF-FSP-20260702 — S0 freeze executed; S1–S2 complete; S3 open

- Session scope: operator-executed S0 freeze ceremony + five implement/audit loops (S1, S2-slice, S2b, S2c/S2d, S2e). Roles held: Codex implemented (separate host-side sessions), Claude audited every report against artifacts/code (did not implement mechanism code; drafted frozen_design.json pre-freeze at operator request — disclosed in-file), operator executed ceremony/banks/pushes.
- Claim ceiling: instrument code + PC/tractability evidence only. Zero environment-validity, mechanism, learning, agency, subjectivity, or EGO claims. S5 certification has NOT run.
- Next session: read this file + `FSP-STAGE-LEDGER.md` (L-004 = current stage truth) + memory topic `fsp-route-program-001a`.

## 1. State (end of 2026-07-02)

- Ledger: L-004 accepted = P0.2 ACTIVE. N0 = FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A executing per `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-EXECUTION-PLAN-001A.md`.
- Stage position: S0 ✓ → S1 ✓ → S2 ✓ (T2.1 + T2.2 both closed) → **S3 open, S3a prompt delivered** (4-way split: S3a data+degenerates/LS → S3b graph-cache+RAG/NN → S3c decoders+sequence models → S3d should-win certs+NULL env) → S4 harness/adjudicator → S5 certification → S6 verdict/audit/bank/route.
- Commit chain (all pushed to origin/codex/meta-theory-scaffold): `b812552` (pre-existing TLGP anchor) → `f1cf1aa` S0 freeze (16 files) → `6bb6107` bookkeeping → `ac4fa20` ledger L-004 → `9aa6680` S1 → `2c9a4ec` S2 slice (+ intervening) → `03845e5` S2c → `326bd51` S2d → (S2e bank pending or done — check `git log --oneline -3`).
- Frozen read-only sources + canonical blob shas (full values in `artifacts/FSP-PUM-ENV-IDPROBE-001A/freeze_record.json`): card `0a5e38a5dbe9…` / constitution `882a68de2973…` / execution plan `c07eec2ac384…` / frozen_design `32d2cbd538f3…`. Every implementation session verifies these BEFORE work; every checkpoint commit re-verifies (built into the script). Drift = STOP.
- Track T: rung1 full run still RUNNING (Codex separate session). Its verdict → operator ledger transition at the NEXT FREE number (L-005). No mixed commits, ever.

## 2. Operational contract (hard-won; violating any of these cost us a stop this session)

1. **Git**: the stale `.git/index.lock` (Jul 1) is a DELIBERATE shield — the rung1 harness fires `git add -u` snapshots every turn (signature `core.hooksPath=NUL`); the lock blocks them from flooding the shared index. Do NOT delete it while the rung1 session lives. ALL Track-F commits go through private-index plumbing: `scripts/trackf_checkpoint_commit.ps1 -Message "..."` (operator, host-side, repo root) — it CAS-guards the ref, enforces the Track-F path allowlist, blocks frozen-file drift, and refuses TLGP paths. Then `git push`. Ceremony scripts kept: `s0_freeze.ps1`, `s0_ledger_commit.ps1` (historical).
2. **Codex sessions**: implementer only, NO git commands (card forbids executor commits). One bounded stage-slice per session with an explicit DoD file list. ANTI-IDLE rule (learned after one session returned a re-description of existing artifacts as its "output"): every prompt must state "re-describing existing artifacts = task failure", name the NEW files required, and demand freshness proof (new sha256 + new wall-clocks + pytest count). Wall-clock values repeated to full precision = re-read of an old artifact, not a new run.
3. **FUSE illusions (Claude sandbox), 5 lessons**: edited-existing-files show stale content beyond old EOF (hit CLAUDE.md, the card, simulator.py), stale mtimes (hit ideal_observer.py), and sandbox pytest on edited files has ZERO evidential force (3-failed false alarm). New files sync fine. Provenance/freshness = file-API reads + artifact sha256 chains + host execution only.
4. **Audit loop convention**: Codex report pasted back → Claude audits (numbers cross-checked against artifacts; code read via file API; verdict + blockers + next prompt) → operator banks via checkpoint script → next session. Failure artifacts are preserved and labeled, never deleted (v1 INVALID_BENCHMARK, v2/v3 honest negatives all still on disk, listed in v4's `invalid_prior_artifact_preserved`).

## 3. Audit trail of this session (verdicts + standing items)

- **S1** (sealed simulator): ACCEPT w/ pre-S2 fixes → both fixed and verified (session rollover lazy-trigger via `_ensure_session_started`; NULL_ENV θ-invariance test is strong: α/β/d extremes + trust=0.2 + all actions, 1e-12).
- **S2 slice**: ACCEPT as scaffold; found blocker B1 (filter shared master_seed → atom z trajectories == true z realization → p(o|θ,z*) oracle inflation, L-A violation, false-PASS direction) and B2 (tractability unmeasured).
- **S2b**: B1 CLOSED (independent `filter_seed` w/ explicit check; `style_map` required explicit; information interface documented = kernels + style map, NOT θ/z realizations or seeds; z marginalized via stationary-GH). Disclosures on record: z scheme is stationary-marginal per turn (NOT filtered-z exact) — direction conservative (underestimates ideal → false-FAIL not false-PASS risk); concern later CLOSED by z0 margin 0.006 nats (z impact tiny). B2 found INVALID_BENCHMARK: v1 "benchmark" measured dummy-array counting, not the filter (test-only-logic-path class failure) — artifact kept, labeled.
- **S2c**: FactoredExactFilter (full 7,077,888-atom joint posterior, per-atom equivalence cert 7.2e-16); REAL benchmark 61.2s/user → 33.98 CPU-h > 24 line → honest `stop_N0_F3_required` (instrument fallback; redesign budget untouched).
- **S2d**: z quadrature g=3 via convergence cert (7.3e-9 << 1e-3); v3 30.04 CPU-h still > 24 → honest STOP. Diagnosis: 7M-vector kernel = ~90% of cost (~25 passes/step).
- **S2e**: log-domain kernel (ONE indexed-add pass/step; query-time logsumexp normalization w/ written overflow bound; bincount class-aggregated queries; exp-shift caching). v4 = 15.3s/user single-thread (explicit accounting: threads=1, numba=false) → **8.51 CPU-h < 24 = TRACTABLE. S2 complete.** Equivalence re-cert 6.1e-16 (verified fresh via per-row delta comparison).
- **24 CPU-h line note**: pre-registered in S2b; held firm through two honest failures rather than tuned. Precedent to keep.

## 4. Standing debts and queued objects

- **S4 obligations** (accumulated from audits, must enter the S4 card): real planted-VALUE leak mutant (current scanner is key/type-based only); `stable_fact` RNG stream reconciled into declared vocabulary; structural sealing enforcement at harness level (battery cannot reach `controlled_theta` / `response_distribution` — S3a adds the import-graph test, S4 adds runtime enforcement); per-gap N interpretation note (frozen 200 heldout binds Gap-1/H1; per-gap evaluation plans documented, not thresholds); **policy-class compute budget: naive 20× = 170 CPU-h** (myopic-IG 0.46s/step selection) — needs an evaluation-plan design, not silent shrinking.
- **S3 remaining**: S3a (in flight or next: trajectory sets w/ leak-scan + sealing test + 6 members w/ declared degenerate conventions) → S3b (graph-cache ×5 real fitted tables w/ alias_report; RAG-k5; NN-user) → S3c (obs-decoder logreg/GBT/GRU ×24 configs, family_max; sequence models ± action conditioning) → S3d (should-win certificates for EVERY member per constitution §7 + NULL-env control; any cert failure = FAIL_BASELINE_UNDERPOWERED, instrument-invalid).
- **Design-only queue (P1 gate, do NOT execute now)**: MPVL/EBPP explicit-belief probe-policy control baseline (naming: avoid "viability"); FSP-BORROWED-STACK-REGISTRY-001A (external components: infra vs baseline vs inspiration vs prohibited; local-run-only; offline-compute parity; LLM orchestration needs operator unlock at P1).
- Housekeeping: memory index consolidated ✓ (this session verified); Current-front line refreshed.

## 5. Evidence-status marks

- S0 freeze + S1–S2e artifacts = repo-committed + pushed + audited. All PC/tractability/convergence/equivalence certificates live under `artifacts/FSP-PUM-ENV-IDPROBE-001A/`.
- Nothing in this session moves any claim: no environment-validity, no Gap certificates, no mechanism evidence. The first claim-bearing event will be the S5 certification run adjudicated in S6.
- v1 tractability artifact = INVALID_BENCHMARK (labeled, preserved); v2/v3 = valid honest negatives superseded by v4.
