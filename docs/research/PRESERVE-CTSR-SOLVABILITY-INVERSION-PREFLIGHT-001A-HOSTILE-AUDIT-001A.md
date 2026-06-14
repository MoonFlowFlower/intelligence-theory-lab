# PRESERVE-CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A-HOSTILE-AUDIT-001A

Verdict: `downgrade_inconclusive_admission_unsupported`

Layer: engineering-governance / negative-evidence preservation / preflight-downgrade record only.

Mainline integration status: not integrated.

Enabled status: no new mechanism path, no candidate, no surface redesign, and no new CTSR admission claim.

Claim ceiling: negative-evidence preservation and preflight-downgrade governance only.

## Problem Definition

This preservation record downgrades `CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A` from downstream-usable surface-admission evidence to historical artifact only. The original task reported `admitted_surface_preflight`, but the hostile audit found that the admission claim is unsupported because fair simple baselines can reach oracle-level accuracy.

## Preserved Original Status

- Original reported verdict: `admitted_surface_preflight`
- Downstream usable status: not admissible / blocked pending redesign outside this route
- Original result path: `artifacts/ctsr_solvability_inversion_preflight_001a/result.json`
- Original report path: `docs/research/CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A.md`
- Original remote anchor: `remote-anchor-ctsr-no-candidate-preflight-001a-7552e5d`

## Blocking Issues

- B1 baseline-weakness equivalence: hostile audit reports fair simple baselines = oracle = `1.0`, including task_b-only `context_key + query_offset` arithmetic, legal-join, and legal-observation nearest-neighbor baselines.
- B2 carry leakage into legal `context_key`: the audited surface makes the target recoverable from legal task_b fields without requiring a nontrivial cross-task mechanism.
- B3 oracle/scorer tautology: the oracle prediction and scorer used the same expected-action computation path, so the reported legal-oracle accuracy is not independent surface-admission evidence.
- B4 low-cardinality legal fields can still deterministically encode the target; non-unique fields are not automatically safe.
- B5 leakage positive-control coverage was incomplete and did not cover all answer-bearing channels.
- B6 registry/root-level exhaustiveness did not rule out third-channel or metadata leakage.

## Non-Blocking Caveats

- The harness was reported reproducible.
- Focused pytest passed for the original preflight.
- Ablations appear to be real reruns.
- Original artifacts, source, tests, and report must remain unchanged by this preservation task.

## Downstream Usage Rule

Allowed uses:

- Cite this record as negative evidence that `CTSR-SOLVABILITY-INVERSION-PREFLIGHT-001A` is not downstream-usable surface-admission evidence.
- Cite the original result only as historical artifact with downgraded status.
- Use the hostile-audit blockers to motivate a separate redesign task card if explicitly authorized.

Forbidden uses:

- Do not cite the original `admitted_surface_preflight` verdict as candidate-admission evidence.
- Do not authorize candidate-vs-baseline discrimination from this preflight.
- Do not proceed to Gate4, Gate5, tournament, bridge, runtime, or EGO-mainline work from this preflight.
- Do not rewrite the original CTSR source, artifacts, tests, report, field registry, thresholds, or verdict to make the downgrade look like a pass.

## Readback Summary

- New mechanism score produced: `false`
- Candidate code created: `false`
- Original CTSR preflight source modified: `false`
- Original CTSR preflight artifacts modified: `false`
- Original CTSR report modified: `false`
- Old COMPOSITE negative evidence modified: `false`

## Next Minimal Closed-Loop Action

Treat this preflight as blocked for downstream admission. If CTSR remains in scope, draft a separate redesign task card that includes the hostile audit's fair simple challengers before any candidate or gate work.

## What This Does Not Prove

This does not prove mechanism failure, CTSR impossibility, Gate4/Gate5 invalidity, agency, autonomy, consciousness, emotion, subjectivity, companion readiness, EGO readiness, or stable user benefit. It only blocks this preflight from being used as surface-admission evidence.
