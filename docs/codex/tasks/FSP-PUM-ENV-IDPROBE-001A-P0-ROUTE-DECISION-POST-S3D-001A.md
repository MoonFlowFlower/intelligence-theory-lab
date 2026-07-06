# FSP-PUM-ENV-IDPROBE-001A — P0-ROUTE-DECISION-POST-S3D-001A

Status: **DECISION CARD (route-level). Operator selects a fork (flat — solo policy 2026-07-05, no signature ceremony).**
Auditor-drafted (Claude), 2026-07-05. Records what the S3d v0 tombstone means for the P0 route and bounds the choice. Changes no science code, no spec, no banked artifact. Does **not** select the route; it enumerates the forks and states the auditor recommendation.

## task id
`FSP-PUM-ENV-IDPROBE-001A-P0-ROUTE-DECISION-POST-S3D-001A`

## current stage / ledger
- P0.2 (N0 experiment = PUM-ENV identifiability probe) — ACTIVE per `FSP-STAGE-LEDGER` L-004.
- Culminating step S3d (should-win + NULL-env certificate battery) v0 → **TOMBSTONED**, banked+pushed `70cdf7e` (evidence `397df12`, closure `afda452b`; card `FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A`).
- This is a P0-level route decision, not an experiment. It becomes an operator ledger transition once a fork is picked.

## problem definition
P0's job (probe-first): certify that PUM-ENV is a **qualified instrument** — an environment + certificate battery where a latent-mechanism decoder is *fairly* separable from cheap baselines (lookup / NN / graph-cache): ideal ≥0.80, fair_max ≤0.60, headroom LCB ≥0.10, action-conditioning gap, camouflage-off decoder, graph-cache challengers (draft probe card `FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A` gates). S3d v0 was the should-win certificate that would qualify the instrument. It did **not** qualify, on two independent grounds:
- **Ground 1 (identifiability):** NULL false-headroom — ideal `0.0721` > limit `0.0363`; the ρ denominator conflates per-user renderer-permutation (`style_map`) recovery with latent decoding (diag `30caa7f` / `5cb90397`).
- **Ground 2 (baseline dominance, denominator-free — robust to Ground 1):** lookup `nearest_neighbor` raw `0.162` beats the assigned mechanism `seq_window` raw `0.075` (**2.16×**) in `low_diversity`; no assigned mechanism member passes any discriminative cell.

This is the **2nd instance of the same style_map-privilege identifiability-ceiling family** (1st = LRGG Tier0-2 oracle-coupling / equal-access saturation), already formalized in the "no qualified mechanism testbed = identifiability ceiling" finding and FSP constitution L-A: *access regime decides identifiability; under equal access the win goes to the baseline.*

## the decision (pick one; A and C are compatible)

### Fork A — Close P0 as `INVALID_INSTRUMENT` (identifiability-ceiling, 2nd instance) — auditor default
- **Commit:** P0 / PUM-ENV route closes with a bounded negative "no qualified mechanism testbed at this access regime" verdict; reallocate program weight per `FSP-ROADMAP-CONTINGENCY` weight-map.
- **For:** two independent grounds; Ground 2 is denominator-free and shows the mechanism *loses* to a lookup baseline (not merely a scoring artifact); 2nd family instance; the tombstone's own reopen bar is unmet by current evidence.
- **Cost:** ~0 new compute; a closure/decision record + ledger transition.
- **Does NOT prove:** mechanism absence; falsity of any theory (Bio-CMBC / CVPSM / VCCO / CMBC / R-G); that no other instrument could separate signal. Bounded instrument-negative only.
- **Red line:** do not upgrade "instrument failed" → "mechanism / theory false."

### Fork B — Bounded S3d-R2 successor (equal-access redesign), ONE attempt
- **Gate to even open (pre-registered in the tombstone):** R2 must state **ex ante WHY** equal-access / style-invariant scoring would separate the mechanism from the lookup family. **Current evidence does not supply that reason** — Ground 2 already shows `seq_window` < `nearest_neighbor` with the ρ denominator removed, so stripping the `style_map` privilege makes the failure *cleaner*, not the mechanism a winner. Open B only if the operator can articulate the ex-ante mechanism>lookup argument; otherwise B is dominated by A.
- **Commit (if opened):** fresh spec with equal-access (ideal infers `style_map` from the eval-prefix, no handed `style_map`; used consistently in BOTH the NULL guard AND the ρ denominator — no second ideal / no schema fragmentation) + mandatory falsifier (assigned mechanism must **beat, not tie**, the lookup / NN / graph-cache / count-table / successor-map family by a pre-registered margin, full control family reported) + NULL clean for the equal-access ideal.
- **Cost:** high — new env/spec + new full battery (measured ≈ **40 CPU-h**, no checkpoint); counts against the pre-registered redesign budget (verify remaining count vs `FSP-ROADMAP-CONTINGENCY` "max 2 redesigns").
- **Red line:** no threshold / strength-3.2 / ρ-threshold tuning to pass; equal-access used identically across guard and denominator.

### Fork C — Reallocate to an unblocked line (cheapest: clear Track-T L-005 bank)
- **Rationale:** P1 (single-mechanism) is gated behind a PASSED P0 instrument; with no qualified instrument (Fork A) P1 cannot legitimately open on PUM-ENV, and the P1-gated design objects (MPVL / EBPP control baseline, borrowed-stack registry) stay design-only. The cheapest unblocked forward motion is the OTHER track: bank the audited Track-T rung1 (H_cap segment-bounded) + 6 outstanding json, clearing L-005. TLGP capability-witness feeds P0.1 / P0.4 and does not depend on FSP P0.
- **Compatible with A** (close P0, then advance Track-T). Not a substitute for the P0 verdict.
- **Cost:** housekeeping bank; no new experiment.

## auditor recommendation
**A + C.** Close P0 / PUM-ENV as `INVALID_INSTRUMENT` (2nd identifiability-ceiling instance — the honest verdict the evidence supports), and take the cheapest unblocked step (Track-T L-005 bank). Open **B only** if you can state, before any new number, the ex-ante reason equal-access scoring would let the mechanism beat the lookup family — current evidence points the other way. This is a recommendation; you decide.

## claim ceiling
Bounded route-decision record only. No mechanism, theory, learning, agency, EGO-readiness, or consciousness claim. Fork A's closure ceiling = "bounded evidence that PUM-ENV v0 is not a qualified mechanism instrument at this access regime"; it does NOT claim the mechanism or any theory is false.

## stop condition
Decision record; triggers no compute. Superseded when the operator picks a fork and the ledger transition (L-005+) is appended.

## rollback
Documentation only; revert the commit. No science code, spec, or banked artifact touched.

## forbidden
Selecting a fork on the operator's behalf; upgrading instrument-negative into mechanism / theory falsification; opening B without the ex-ante justification; any threshold / spec motion.

## §operator selection (flat — solo policy, no signature required)
Pick: [ ] A   [ ] B   [ ] C   [x] A+C   —   Operator: Zhouyu (delegated to auditor; authorized 2026-07-05)   Date: 2026-07-05
Ex-ante reason (required only if B): n/a — B not selected. Denominator-free the mechanism loses to `nearest_neighbor`; no ex-ante mechanism>lookup reason exists.
Recorded decision: close P0 / PUM-ENV as `INVALID_INSTRUMENT` (2nd identifiability-ceiling instance); reallocate cheapest-unblocked = clear Track-T L-005 bank.
