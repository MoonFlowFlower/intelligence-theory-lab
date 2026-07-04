# FSP-PUM-ENV-IDPROBE-001A — S3D-SHOULD-WIN-NULL-ENV-SPEC-001B (delta-supersede of 001A)

Status: **PROPOSAL — UNSIGNED. supersede-only.** 001A stays a historical frozen blob (do not
rewrite). 001B takes effect only when the operator signs §7 and banks it (operator bank = approval),
becoming the new frozen rule source for S3d. 001B is a **delta** over 001A: everything in 001A holds
UNCHANGED except the three deltas below.

## 0. Trigger (banked evidence)
The banked cell-headroom pre-check (`s3d_cell_headroom_precheck.json`, commit after `8cd95a0`, on the
cert-faithful banked runner scorer) showed the frozen instrument is not executable as-is:
- `constant_none` / `constant_saturated`: `IDEAL_MISSPEC` — the `FactoredExactFilter` silently falls
  through to θ-tables on the constant cert variants, so its ideal ≈ chance though the cells' generative
  mode has ample headroom.
- `camouflage_off` (S2-validated central cell): exact ideal `0.0966` (= banked `0.09948`), headroom
  `0.065 < 0.10` → the 001A cell-validity guard is **not reachable by the optimal predictor** on the
  central cell; `flat_theta` `0.0947 < 0.10` likewise.
- recommend-scope metric gave `0.0586` (old inline scorer) vs `0.1363` (banked cert runner) — 2.3×;
  the canonical scorer was never pinned.

## 1. DELTA 1 — ideal must model every cert cell (implementation gap fix)
001B requires the exact ideal (`FactoredExactFilter`) to correctly model **every** should-win cell,
including `degenerate_should_win_constant_none` and `degenerate_should_win_constant_saturated`
(styled peaked at the constant symbol). This is delivered by a bounded filter repair with the SAME
gates as the prior repair: regression bit-identical on all previously-supported variants
(`camouflage_off` ideal metric `0.09948462995337995` exact), oracle-leakage clean, and per-cell
ideal-sanity (ideal ≥ every member on that cell's canonical metric). No `raise`, no silent
fall-through, for any cert cell.

## 2. DELTA 2 — cell-validity guard recalibration (operator decision; anti-tuning firewall)
The 001A guard `ideal_cell − chance ≥ 0.10` is **superseded** because it is demonstrably unreachable
by the optimal predictor on the validated central cell (`0.065`). This is a correction of a
mis-calibrated pre-registration, NOT motion to make a member pass.

**Firewall (must hold or 001B is invalid):** the recalibrated guard is defined on the **ideal**
(an environment property), computed and fixed **before** any member result is consulted; member ρ
thresholds (0.50 / 0.80 / 0.90) and `strength=3.2` are **UNCHANGED**; the guard is not chosen to make
any specific member pass.

Operator picks one basis in §7:
- **2a (recommended) — statistical distinguishability guard.** Replace 0.10 with
  `ideal_cell − chance ≥ k × SE_cell`, where `SE_cell` is the binomial SE at that cell's eval-point
  count (overall n≈48k → SE≈0.0008; recommend-scope n≈1.3k → SE≈0.005) and `k` is a pre-registered
  constant (recommended `k = 5`, i.e. ~5σ). Rationale: the guard's purpose is that the cell gives the
  ideal statistically real headroom over chance; 0.065 on camouflage_off is ~82σ, so it is genuinely
  a valid cell — 0.10 absolute was arbitrary. Report per-cell `SE_cell`, `k×SE_cell`, and pass/fail.
- **2b — redesign the low-headroom cells' generative signal** so ideal_cell − chance ≥ 0.10 holds
  natively (e.g. strengthen the θ-signal in `camouflage_off`/`flat_theta`). More invasive (touches the
  central cell's generator); a fresh pre-registration; keeps the absolute 0.10 guard.
- **2c — per-cell relative guard**: `ideal_cell` must exceed chance by a fraction of the ideal's own
  scale, pre-registered. (Least standard; listed for completeness.)

## 3. DELTA 3 — canonical metric pinned
The **banked cert runner's** scorer (`s3d_battery_runner_line30.py` metric helpers) is declared the
sole canonical metric for every cell, including recommend-turn-conditional for
`rag_should_win_stable_facts`. The old inline diagnostic scorer (which produced `0.0586`) is
non-canonical and void for adjudication. 001B implementation must include a one-shot verification
that the canonical scorer computes recommend-conditional correctly (agreement on a fixed fixture),
and document why the two scorers differed.

## 4. Invariants held UNCHANGED from 001A
18-member `battery_membership`; the cert-cell assignment table and member ρ thresholds (0.50/0.80/
0.90); the 2 cert-only degenerate simulator variants; BASE-invariance regression; NULL-env with
MDE `chance + 0.005` for every member incl. ideal; `strength = 3.2`; fitting contract; trace/replay
contract; adjudication rules; claim ceiling. **No ρ-threshold motion. No member set change.**

## 5. Anti-tuning audit (Claude will red-team before any bank)
On 001B implementation Claude verifies: guard recalibration is on the ideal only and pre-dates member
results; `strength=3.2` and ρ thresholds byte-unchanged; the constant-cell ideal is exact (regression
+ oracle + ideal≥member), not a hard-coded constant lookup that leaks the cell label; canonical scorer
is the banked runner's, not a reinvention; banked 001A / STOP / probe / repair artifacts byte-unchanged.

## 6. Sequence after signing
Sign §7 → bank 001B (new frozen blob; 001A retained) → bounded ideal repair for the constant cells
(gates as §1) → Claude audit → bank → PART-0 re-gate under L=30 + the recalibrated guard → full battery.
Process lesson banked with this note: S3d was pre-registered twice without an ideal-coverage/headroom
feasibility check; 001B's §1+§2 add that check as a standing pre-registration requirement.

## 7. Operator decision (sign to take effect)
```
Guard basis (choose one):  [x] 2a k = __5__ (recommended k=5)   [ ] 2b (redesign cells)   [ ] 2c ______
Confirm anti-tuning firewall (§2) acknowledged:  [x] yes
Confirm invariants §4 unchanged (no ρ / member / strength motion):  [x] yes

Operator: __________leo____________   Date: ____26/7/4______
```
