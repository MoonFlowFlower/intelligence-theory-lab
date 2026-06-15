# ONE-GATE-FUTURE-ONLY-NON-CIRCULAR-EVIDENCE-HARNESS-001A

## Problem Definition

Verifier 001B was independently downgraded because its callable-provenance check
is circular: the candidate can control both `producer_function` and
`expected_output_digest`.

Do not repair the standalone verifier in this task.

Build a minimal future-only, non-circular evidence harness for one current Gate
target, so future Gate evidence is generated from raw outputs by harness-owned
metrics rather than admitted retroactively from candidate-controlled bundles.

## Current Stage / Layer

Engineering implementation / future-only Gate evidence harness preflight.

## Mainline Target

None.

Do not wire into EGO mainline, bridge, runtime, integrated admission, or
companion paths.

## Selected Gate Target

Selected target: future-only Gate4 evidence harness target.

Repo readback basis:

- `artifacts/evidence_admission_verifier_001b_bypass_audit_001a/route_decision.json`
  records `safe_to_wire_gate4: false`, `safe_to_wire_gate3: false`, and
  `verifier_001b_usable_for_gate_admission: false`.
- `artifacts/ego_mainline_evidence_dependency_closure_001a/route_permission_matrix.json`
  keeps `Gate4_preflight_task_card_drafting_allowed_future_only` blocked/current
  or future-only.
- `artifacts/ego_mainline_known_failure_triage_001a/downstream_route_impact_matrix.json`
  keeps `Gate4_execution` blocked and `Gate4_task_card_drafting`
  `blocked_current`.

This task does not execute Gate4 and does not reopen old Gate4 bundles. It only
creates a raw-output-only harness shape for a future Gate4 evidence path.

## Enabled-State Requirement

Local CLI/test runner only. No default mainline activation.

## Real-Trigger Evidence Requirement

The harness must include positive controls derived from verifier 001B failure:

1. constant producer / fabricated digest attempt;
2. echo producer / row-injection attempt;
3. candidate-declared score attempt;
4. candidate-declared baseline pass attempt;
5. candidate-declared ablation pass attempt;
6. candidate-declared replay pass attempt.

## Hard Contract

- Candidate may output only raw traces, raw predictions, raw actions,
  serialized states, and environment observations.
- Candidate may not output `expected_score`, `expected_digest`, `verdict`,
  `admission_decision`, `producer_function`, `baseline_result`,
  `ablation_result`, `leakage_result`, or `replay_result`.
- Metric producers must come from a harness-owned registry or allowlist.
- The harness computes scores, digests, baselines, ablations, leakage checks,
  and replay checks from raw outputs.
- No `row` injection into metric producers.
- No metric producer located inside candidate bundle/artifacts.
- Any candidate-controlled expected value must block.

## Hypothesis

A future-only harness can prevent the specific circular evidence failure by
removing candidate control over metrics, expected values, and producer
selection.

## Strongest Baseline

The downgraded verifier 001B / row-shape callable-provenance approach, which
admitted constant-producer fabricated digest evidence.

## Ablation Requirement

Remove or corrupt one raw trace/action/state input and rerun harness metrics.
The score or replay check must change or block. Do not accept unchanged pass
reports.

## Trace / Replay Requirement

Record raw input hashes, harness-owned metric function path, metric code hash,
run_id, seed/context/episode IDs, computed score, baseline score, ablation
score, leakage positive-control result, replay recomputation result, and block
reasons.

Replay must recompute behavior from `serialized_state + observation`, not stored
hash comparison.

## Computed-Evidence Provenance Gate

All score-bearing results must come from harness-owned callable computation over
raw outputs. No literal verdict dictionaries. No candidate-declared expected
outputs.

## Acceptance Gate

- All circular-evidence positive controls block.
- Candidate raw-output-only fixture can be scored by harness.
- Baseline is independently invoked by harness.
- Ablation reruns under actual intervention.
- Leakage scanner has at least one positive control.
- Replay recomputes from serialized state plus observation, not stored hash
  comparison.
- Existing verifier 001B is not repaired or used as citation admission.
- No Gate/mainline integration claim.

## Claim Ceiling

Future-only non-circular evidence-harness preflight only.

No Gate validity, mechanism validity, mainline effect, agency, consciousness,
emotion, autonomy, stable user benefit, or EGO readiness claim.

## Stop Condition

Stop if the chosen Gate cannot produce raw outputs without candidate-declared
expected values, if metrics require candidate-selected `producer_function`, if
baseline/ablation/replay cannot be rerun by harness, or if the task starts
retroactively admitting old bundles.

## Rollback Plan

If blocked, preserve negative evidence and downgrade the target Gate evidence
route. Do not patch reports to pass.

## Expected Changed Files

Allowed:

- `docs/codex/tasks/ONE-GATE-FUTURE-ONLY-NON-CIRCULAR-EVIDENCE-HARNESS-001A.md`
- `src/one_gate_future_only_non_circular_harness_001a/**`
- `tests/test_one_gate_future_only_non_circular_harness_001a.py`
- `artifacts/one_gate_future_only_non_circular_harness_001a/**`

Forbidden:

- `src/evidence_admission_verifier_001a/**`
- Gate3/Gate4/mainline/bridge/runtime files unless read-only input inspection is
  required
- old bundle mutation
- integrated admission wiring

## Auto-Remote-Anchor

conditional.

Anchor only if all acceptance gates pass, final worktree is clean, and local
HEAD / remote branch / local tag / remote tag exactly match.

## Bounded Audit

- Layer: engineering implementation / future-only Gate evidence harness
  preflight.
- Real objective: replace candidate-controlled admission of metric bundles with
  harness-owned computation over raw future Gate4 outputs.
- Problem-definition risk: a "verifier repair" would target the wrong layer by
  preserving retroactive bundle admission; this task must not repair verifier
  001B.
- Strongest baseline explanation: verifier 001B can appear callable because it
  imports and executes a producer, but it still lets the candidate select the
  producer and expected digest.
- Strongest invalidating reason: if the selected Gate target cannot be expressed
  as raw traces/predictions/actions/states/observations, the harness would
  become another report-shape linter.
- Falsifier for the framing: any positive control with candidate-declared score,
  digest, producer, baseline, ablation, leakage, replay, or verdict is accepted.
- Still-insufficient evidence: passing this preflight does not validate Gate4,
  any mechanism, or any old Gate evidence bundle.
- Mechanism-vs-resemblance classification: tests evidence hygiene only, not a
  mechanism hypothesis.
- Hard-coding check: block by forbidden candidate-controlled fields and compute
  metric outcomes from raw rows; do not special-case task ids.
- Local optimum / Zeno check: do not continue repairing verifier 001B; create a
  future-only harness path.
- Evidence leakage check: include a leakage positive control with label-like
  content and require scanner detection.
- Weak-baseline check: invoke an independent majority-action baseline from the
  harness registry.
- Second logic path check: raw fixture and positive controls must go through the
  same harness evaluator.
- Replay weakness check: recompute actions from serialized state and observation,
  not hashes or stored replay verdicts.
- Claim inflation check: result must keep all authorization flags false.
- Minimal validation: focused tests plus one artifact-generation run.
- Stop condition: any candidate expected value is accepted or any old bundle is
  retroactively admitted.
- Acceptance signal: all six circular controls block, raw-only fixture scores,
  baseline/ablation/leakage/replay are invoked and recorded.
