# FSP-PUM-ENV-IDPROBE-001A — S3d Budget Decision 002A (post-battery runtime breach)

Status: **PROPOSAL — UNSIGNED.** Supersedes the line value in `...-S3D-BUDGET-DECISION-001A.md` §8
for S3d execution only; 001A stays a historical blob. Author: Claude (auditor), 2026-07-05. Derived
from the L=30 battery `STOP_runtime_guard_exceeded_signed_line` (31.95 CPU-h) + its trace diagnosis.

## 0. Governance framing (honest — read before signing)

The operator recalled the §8 terms as "second breach = STOP_BUDGET_EXCEEDED, S3d closed, no third
raise." **That clause does not exist.** The signed §8 text, the exec card (line 112), and frozen
spec 001A (line 133) all say only: *"runtime guard (STOP at line; **second breach returns to
operator**)."* So:
- This is the **first** real runtime breach. The runtime guard auto-STOPped; §8's design routes
  the decision to the operator. **Continuing is within the signed terms — not an override of an
  auto-close, because no auto-close was signed.**
- Therefore this note is not "override my stop-loss." It is the §8 first-breach operator decision,
  **plus** a self-imposed hard endgame (§4) that is *stricter* than §8 (which would merely return a
  second breach to the operator again). Net effect on governance: **strengthened**, not weakened.

Do not sign this note as an override. Sign it as a measured line-reset with an added endgame.

## 1. What the STOP established (measured, not projected)

- STOP clean: `s3d_results_void: true`; 8 protected artifacts byte-unchanged; precondition passed;
  STOP payload from committed `_finalize_result_payload`; `wall_cpu_ratio_flag_count: 0` (real CPU,
  not wall inflation). 41/43 units completed; STOP after `ideal::cert::flat_theta`.
- **Root cause = systematic projection underestimate, not run-to-run noise.** Measured vs projected:
  ideal (7 units) **21.61** CPU-h vs projected 12.63 (**1.71×**); nearest_neighbor (2 units) **5.93**
  vs 3.26 (**1.82×**). Cause: the isolated single-eval-user × N extrapolation under-measured true
  per-unit batch cost on the memory-heavy units (see memory `itl-cost-projection-precision-not-accuracy`).
- `discounted_LS_lambda_0.95` (2 units, cert + NULL) never ran (cancelled by STOP).
- **Corrected full-battery cost ≈ 37–42 CPU-h** (31.95 done + discounted_LS ~5.3–9.5).

## 2. Zero-score-exposure confirmation (required before continuing)

The battery is void. To continue past a budget stop honestly, confirm no adjudication score leaked:
`s3d_certificate_report.json` / `s3d_null_env_report.json` / `baseline_comparison.json` /
`replay_report.json` were **NOT regenerated** this run (STOP fired before `_build_reports`); the
per-unit `metric` values in `trace.jsonl` are pre-adjudication and are **not** cert/NULL ρ verdicts.
No pass/fail was computed or seen. (Checklist item; operator confirms `[ ]` below.)

## 3. Decision — line reset by measured formula (NOT a round number)

Continue via **unit-level resume** (card `...-S3D-BATTERY-RESUME-001A`). The runtime guard's
cumulative CPU = (reused units counted at their recorded CPU from the void trace) + (newly executed
units' measured CPU), so the LINE remains a **total-battery** compute budget comparable across runs.

Set L by formula, using the measured trace at authorization:
- **If completed units are reused** (resume validates them): `L = ceil( 1.15 × ( measured_completed_CPUh
  + estimated_missing_2_units + spot_check_budget ) )`. With completed 30.95 + discounted_LS ~5.3–9.5
  + spot-check (≤3 random units) → **L ≈ 38–43**.
- **If a full re-run is chosen** (no reuse): `L = ceil( 1.15 × measured_full )`, measured_full ≈ 37–42
  → **L ≈ 43–48**.

Record the chosen formula and the arithmetic in the sign block. Do not round to a convenient number.

**Key interaction (why a tight line is now safe):** with unit-level resume, a re-breach loses only
the marginal in-flight unit (≤ ~3 CPU-h for an ideal), not the whole run. So prefer the *tightest*
formula-derived L over a fat margin.

## 4. Endgame clause (new hard stop-loss — stricter than §8)

**If the line L set here is breached again → S3d battery CLOSES (Budget Decision 002A is the last
budget note; no 002B, no third raise).** Rationale: the line is now anchored on measurement and the
loss is bounded by resume, so a further breach has no honest justification for another exemption.

## 5. Firewall (unchanged from 001A)

L is a compute-budget convention only, **non-claim-bearing**. This note changes **no** science rule:
ρ thresholds 0.50/0.80/0.90, the 18-member set, cert cells, the 2 cert-only variants, NULL MDE
chance+0.005, strength 3.2, k=5 validity guard, and the frozen spec are untouched. Never cite L
against the S2 tractability line.

## 6. Operator decision (sign to take effect)

```
Zero-score-exposure confirmed (§2: no cert/NULL/baseline/replay regenerated; no ρ verdict seen):  [X] yes
Resume mode (choose one):  [X] reuse-completed (formula A)   [ ] full re-run (formula B)
New line L = 38 CPU-h    Formula + arithmetic used: ___Formula + arithmetic used: 31.95 measured (41 units + PART0, exact) + ~6 margin for the 2 unmeasured discounted_LS units (proj 5.3 / adverse 9.5); resume makes a re-breach cost only the marginal unit_____________________________________
Endgame clause (§4) acknowledged — next breach closes S3d, no further budget note:  [x] yes
Firewall (§5) — no science threshold moved:  [x] yes
Operator: ___________Leo_________   Date: ____ 2026-07-05_____
```
Bank this note (scoped commit, no push) BEFORE handing the resume card to Codex. The resume runner
must read L from this note's §6 and STOP if it is unsigned.
