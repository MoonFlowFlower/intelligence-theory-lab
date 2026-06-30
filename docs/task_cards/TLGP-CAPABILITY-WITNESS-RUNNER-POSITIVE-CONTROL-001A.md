# TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A

> Status: DRAFT implementation card. Authorizes a BOUNDED positive-control run on GPU
> (instrument validation). NOT a TLGP route terminal; does NOT change any banked TLGP
> verdict. Frozen design: `…RUNNER-POSITIVE-CONTROL-001A.frozen_design.json`, canonical
> sha256 `90f2a5034747e0153f29ccc86a672a2cfcd8fe75910de54c02966149eeeef56b`.
> Runner reused READ-ONLY: `grokking_probe.py` (banked sha `9126dc92…`); world frozen
> (prereg `6e61a831…`).

Task id: TLGP-CAPABILITY-WITNESS-RUNNER-POSITIVE-CONTROL-001A

Problem definition: the capability-witness negatives (budget + full wd spectrum, all
no-grokking, heldout plateau ~0.55) are only interpretable if the runner/arch actually
works. Run the SAME instrument (transformer 256/4, AdamW, the banked runner's
model+train+eval, frozen D=3/K=5 world) on two tasks it SHOULD solve, changing ONLY the
dataset, and apply the pre-frozen go/no-go. This is the gate before closing the
learnability route.

Why: it separates "TLGP rung0 is a genuine task/family limit" (runner works, negative is
real → clean close) from "a pipeline bug confounds every negative" (must fix + re-run).

Layer: candidate-free instrument validation. Not a route terminal; does not alter banked
TLGP verdicts.

The two controls (same world, same runner, dataset-only change):
- PC_COPY (floor): episodes where every query (x,a) is drawn FROM the adapt (x,a) set, so
  the correct effect is literally in the adapt context. Tests whether the model READS and
  USES the context (in-context retrieval). Ideal ≈ 1.0. If this fails, the pipeline is
  broken and all negatives are confounded.
- PC_SINGLE_RULE: ONE fixed rule_id across ALL train+test episodes, full value coverage.
  Tests whether the arch can REPRESENT the mod-5 D=3 mapping at all (weight-space). Ideal ≈ 1.0.

Build instructions: add a NEW `src/tlgp_capability_witness_preflight_001a/positive_control.py`
that IMPORTS the model + training step + `_eval_checkpoint` + the world helpers
(`make_episode_for_rule`, etc.) READ-ONLY and constructs PC_COPY / PC_SINGLE_RULE episodes,
training with the SAME model/optimizer/metric. Do NOT edit `grokking_probe.py`,
`route_decision.py`, the world, or any `src/tlgp_001b_r2/*` / `src/tlgp_001a/*` byte. If the
model/train/eval core cannot be reused for a custom dataset WITHOUT editing banked code,
STOP and report (do NOT auto-extract/refactor — that needs a separate authorized card).

Frozen parameters (see frozen_design.json — do NOT change after results): transformer 256/4
(frozen); AdamW; lr 3e-4; weight_decay 0.1; batch 256; max_steps 20000; early-stop allowed;
seeds [20260710, 20260711]; checkpoint every 2000 steps.

Pre-frozen go/no-go:
- runner_ok → AUTHORIZE clean close/downgrade of the learnability route as
  task/family-complexity-limited: PC_COPY heldout ≥ 0.95 (all seeds) AND PC_SINGLE_RULE
  heldout ≥ 0.85 (all seeds).
- runner_copy_fail → STOP, prior negatives CONFOUNDED, open a runner-investigation card:
  PC_COPY heldout < 0.70 (any seed).
- representational_limit → close learnability route as REPRESENTATION-limited: PC_COPY ≥ 0.95
  but PC_SINGLE_RULE < 0.70.
- ambiguous → report numbers + curves, operator decides.

Required outputs under `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNNER_POSITIVE_CONTROL_001A/`:
`training_records.json`, `val_curves.jsonl` (dense per-checkpoint train+heldout per control/seed),
`positive_control_report.json` (per-control heldout + ideal + the go/no-go verdict with numbers),
`manifest.json` (frozen_design_sha256 = 90f2a503…, grokking_probe_sha256 = 9126dc92…,
prereg_sha256 = 6e61a831…, git HEAD/branch, GPU env, capacity_unchanged, banked_source_diff_empty),
`failure_manifest.json` if a stop fires.

Acceptance gate: 4 runs (2 controls × 2 seeds) complete or recorded; dense curves logged;
ideal_balacc recorded per control; go/no-go applied as frozen; `grokking_probe.py` / world /
banked source unmodified (shas match); capacity unchanged; manifest shas match.

Claim ceiling: instrument-validation evidence only. Confirms/refutes that the runner/arch can
solve easy in-context tasks. Does NOT change banked TLGP verdicts; proves nothing about
transfer/rung3/H1, mechanism, capability-witness feasibility, the GRU witness, agency, self,
subjectivity, AGI, or EGO.

Process discipline (tightened): STOP means STOP — emit the artifacts above, then STOP. Do NOT
commit the control artifacts (leave on disk for operator/auditor verification). Do NOT add
closeout/curve-config/operator-review or any extra audit layers. Do NOT push.

Stop conditions → failure_manifest.json: editing banked grokking_probe.py/world/TLGP source;
reuse requires editing banked code; capacity changed; go/no-go tuned after results; adding
extra audit layers; committing/pushing.

Rollback: new file `positive_control.py` + new artifact dir only; revert = delete them.

Forbidden: editing banked source/world/grokking_probe.py/route_decision.py; capacity change;
new candidate; `AGENTS.md`/`CLAUDE.md`/global config; `scripts/push.*`; remote/push; extra
audit layers.

Auto-Remote-Anchor: forbidden.

Expected cost: ~4 short transformer-256/4 runs on easy tasks (≤20k steps) — well under a day;
these should solve fast if the pipeline works.

## For Codex (execution)
Run on a GPU machine. Read this card + frozen_design.json first. Build the read-only
`positive_control.py` (import model/train/_eval_checkpoint/world helpers; STOP if that needs
editing banked code), run the 4 cells (PC_COPY + PC_SINGLE_RULE × 2 seeds, transformer 256/4,
AdamW lr3e-4 wd0.1, ≤20k steps, checkpoint 2k), emit the artifacts above (dense curves + ideal
per control), apply the FROZEN go/no-go, and STOP at the verdict. Do NOT commit, do NOT add
audit layers, do NOT push. Final report: per-control/per-seed best heldout + ideal +
go/no-go verdict; manifest sha matches (90f2a503 / 9126dc92 / 6e61a831); confirm no
banked-source edit, capacity unchanged, nothing committed/pushed. Paste back for closing
verification.

## Collision Record
Approach A — close the learnability route on the probe negatives alone: rejected — the runner
has no positive control; "no grokking ~0.55 plateau" could be a pipeline bug.
Approach B — positive control reusing the exact instrument on two solvable tasks (this card):
selected — cheaply validates or refutes the runner before any close.
Approach C — test the runner on a canonical single-table grokking task: rejected as primary —
different (non-in-context) setup; tests optimizer plumbing but not the in-context wiring that
matters here.
Selected approach: Approach B.
