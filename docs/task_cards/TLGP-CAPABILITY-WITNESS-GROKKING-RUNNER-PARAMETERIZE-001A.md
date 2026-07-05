# TLGP-CAPABILITY-WITNESS-GROKKING-RUNNER-PARAMETERIZE-001A

> Status: DRAFT repair card. Authorizes a MINIMAL, BEHAVIOR-PRESERVING
> parameterization of `grokking_probe.py` so 001B can run wd {0.3,0.5} without
> editing banked-as-executed code semantics. Blocked-by: 001A grokking probe banked
> as-executed FIRST (so 001A provenance = the hard-coded version that produced its
> artifacts). This is a SEPARATE commit after that bank.

Task id: TLGP-CAPABILITY-WITNESS-GROKKING-RUNNER-PARAMETERIZE-001A

Problem definition: `grokking_probe.py` hard-codes the weight-decay grid {0.1,1.0},
the output subdir, and 001A verdict semantics, exposing only `--run`/`--validate-only`.
001B needs the SAME training core run with wd {0.3,0.5} into GROKKING_PROBE_001B/.
Add optional CLI args + extract the training loop into an importable function, with
NO change to training behavior, so both 001A (via defaults) and 001B reuse one core.

Why this ordering (provenance): refactoring before banking 001A would make
banked-source ≠ the source that produced the 001A artifacts (the TLGP-B2 trap). So
001A is banked as-executed first; this behavior-preserving change is a later,
separately-verified commit.

Allowed change (ISOLATED, behavior-preserving):
- Extract the existing training/eval loop into a module-level function (e.g.
  `run_probe(weight_decay_grid, out_subdir, seeds, max_steps, lr, ...)`); the CLI
  calls it.
- Add OPTIONAL CLI args with defaults equal to the 001A constants:
  `--weight-decay-grid` (default "0.1,1.0"), `--out-subdir` (default
  "GROKKING_PROBE_001A"); other knobs default to the frozen 001A values.
- NO change to: model, metric, optimizer construction, seed/RNG handling, data
  construction, checkpoint logic, leakage detector, or verdict/trend logic.

Acceptance gate (behavior preservation — MUST pass before 001B uses it):
- Config/dry-run readback with no args == the 001A frozen params (wd {0.1,1.0},
  out GROKKING_PROBE_001A, seeds [20260710,20260711,20260712], 50k steps, lr 3e-4,
  capacity 256/4) — assert in a unit test.
- Deterministic re-run check: re-run ONE 001A cell (seed=20260710, wd=0.1) under the
  parameterized runner with defaults and confirm the per-checkpoint heldout curve
  reproduces the banked 001A `val_curves.jsonl` for that cell within fp tolerance
  (e.g. max |Δ| < 1e-6). If it does not reproduce, the change is NOT
  behavior-preserving → STOP, revert.
- `route_decision.py`, `src/tlgp_001b_r2/*`, `src/tlgp_001a/*`, and the banked 001A
  artifacts are unchanged.

Claim ceiling: engineering refactor correctness only. Produces NO new evidence;
changes no result, verdict, or claim. 001A banked evidence is untouched.

Stop conditions → failure_manifest.json: any training-behavior change (re-run check
fails); editing route_decision.py or banked TLGP-R2/001A source; changing verdict/
trend semantics; `git add -A`; push.

Rollback: single-file change to `grokking_probe.py` + one test; revert = restore the
banked-as-executed version.

Forbidden: behavior change to the training core; editing banked TLGP source;
`AGENTS.md`/`CLAUDE.md`/global config; `scripts/push.*`; remote/push.

## For Codex (execution)
After 001A is banked: extract the training loop into `run_probe(...)`, add the two
optional CLI args (defaults = 001A), add a unit test asserting (a) default config ==
001A frozen params and (b) the seed-710/wd-0.1 re-run reproduces banked 001A
val_curves within 1e-6. Run the test (GPU for the re-run check). If green, commit
(local, scoped: `grokking_probe.py` + the test) with a message stating
"behavior-preserving parameterization; 001A defaults reproduce banked curves; no new
evidence." Then 001B (`…GROKKING-PROBE-001B.md`) runs:
`grokking_probe.py --run --weight-decay-grid 0.3,0.5 --out-subdir GROKKING_PROBE_001B`.
Report: re-run max|Δ| vs banked 001A, test result, commit hash, confirm no banked
source / route_decision edit, no push.

## Collision Record
Approach A — edit grokking_probe.py in place before banking 001A: rejected (banked ≠
executed for 001A; the TLGP-B2 trap).
Approach B — bank 001A as-executed, then a separate behavior-preserving
parameterization verified to reproduce 001A: selected.
Approach C — duplicate the training core in a new 001B runner: rejected (risks a
divergent core → 001A vs 001B not a clean wd-only comparison).
Selected approach: Approach B.
