# ITL-DEV-BENCH-001E-DIAGNOSIS-ONLY

> Status: DRAFT task card. Requires operator authorization before any implementation.
> Predecessor evidence: banked at commit `b4ee157a01caef34c598bbeb3ac5ed1bb9b90f24`
> (`docs/banks/ITL-DEV-BENCH-001A-001D-LOCAL-BANK.md`).
> This card authorizes diagnosis only. It does not authorize any candidate,
> generator, baseline, metric, or threshold change.

## Task Card

Task id: ITL-DEV-BENCH-001E-DIAGNOSIS-ONLY

Problem definition: Explain *why* RUN_20260629T162834Z produced
`candidate_factorial_baseline_saturated` with aggregate three-way closure gain
`-0.0666666666666667`, using read-only post-hoc analysis over the frozen 001D
artifacts. Do not modify the candidate, generator, baselines, metrics, or
thresholds. Output is a diagnosis table plus a computed route decision. No score
is allowed to improve as a result of this task.

Current stage/layer: engineering diagnosis / benchmark-evidence interpretation
only. Not mechanism hypothesis testing, not learning/adaptation, not
subjectivity.

Mainline target: `itl_devbench` offline artifact path; new isolated read-only
analysis module + diagnosis artifacts only.

Enabled-state requirement: consume the already-banked 001D final run
(`artifacts/ITL-DEV-BENCH-001A/RUN_20260629T162834Z/`) as the sole evidence
substrate. No new agent/environment rollout is permitted (re-running the agent
would create new traces and break the frozen-evidence condition). All eight
factorial variants (000-111) for all five families are already present in the
existing `trace.jsonl`; counterfactual comparisons must be drawn from that
recorded trace, not regenerated.

Real-trigger evidence requirement: every diagnosis artifact is computed from the
recorded `trace.jsonl` / `metrics.json` / factorial JSONs of
RUN_20260629T162834Z; each output carries `producer_function`, `code_path_hash`,
and the sha256 of every input artifact it consumed.

Pre-registered leading hypothesis (falsifiable, not assumed true): the
PE / memory / planner-read channels do not alter the selected action `A_t`, so
they cannot affect reward. Evidence motivating this hypothesis: in four of five
families the eight variant scores are bit-identical
(`contextual_hazard_v1`=13.0, `delayed_poison_v1`=-4.333…, `info_risk_tradeoff_v1`=-10.0,
`rule_reversal_return_v1`=4.0 for all of 000-111), and only `aliased_food_v1`
moves — downward, from 1.667 to 1.333, exactly when PE and planner-read are both
enabled (variants 101 and 111). The diagnosis must test this hypothesis against
the trace, and must be able to reject it.

Diagnostic questions 001E must answer (carried from handoff; each answered from
artifacts, with "unknown / trace_insufficient" allowed):
1. Which 3 of 5 families are baseline-saturated? (Cross-check against
   `baseline_comparison_by_family.json`: expected
   {aliased_food_v1, delayed_poison_v1, info_risk_tradeoff_v1}.)
2. Which baseline saturates each saturated family (graph_cache, generic_fsm,
   obs_only_policy, random_policy)?
3. Which families/variants caused aggregate 101/111 to drop to 0.8, and is the
   drop attributable to a single family?
4. Is PE update misattributing delayed effects (e.g. `delayed_poison_v1`)?
5. Does memory store decision-relevant evidence, or only log events?
6. Does planner-read actually read updated model/memory state at action time?
7. Does planner-read read a noisy/incorrect model and therefore degrade action
   quality (candidate mechanism for the aliased_food 101/111 drop)?
8. Is the action heuristic too weak/saturating for any mechanism channel to
   change `A_t`? (Decisive sub-test below.)
9. Are family scores dominated by reward-shaping artifacts rather than competence?
10. Does 001C need more generator pressure, or does minimal_loop need a new
    candidate design? (Resolved only by `next_route_decision.json`, never
    pre-stated.)

Decisive sub-test (action invariance): for each (family_id, variant_pair,
seed/rule_seed, episode, tick), compare the recorded `A_t` across variants drawn
from the same matched conditions in `trace.jsonl`. Report, per family, the
fraction of matched decision points where `A_t` differs between 000 and 111 (and
between each single-channel variant and 000). If `A_t` is identical across
variants on >= a pre-declared fraction of matched points, the channels are
behaviorally inert by construction and the score equality is explained without
appeal to power. This test must be able to fail (i.e. find that actions *do*
diverge), in which case the hypothesis is rejected and questions 4-7 carry the
diagnosis instead.

Strongest baseline / comparison: none is being claimed; the relevant comparison
is the already-recorded by-family baseline matrix. 001E must additionally note
that the two *non*-saturated families (`contextual_hazard_v1`,
`rule_reversal_return_v1`) are won by variant 000 as well, i.e. any
above-baseline margin there is produced by the base action heuristic, not by the
channels under test. This must be stated explicitly so non-saturation is not
misread as mechanism-channel value.

Ablation requirement: this task performs no new ablation runs. It re-reads the
existing 000-111 factorial as the ablation grid and attributes each marginal
(`pe_marginal_under_memory_planning`, `memory_marginal_under_pe_planning`,
`planner_read_marginal_under_pe_memory`, three-way closure) to specific families
and, where the trace permits, to specific decision points.

Trace/replay requirement: 001E must first verify it can replay/re-derive the
factorial numbers it diagnoses directly from `trace.jsonl` (independent
recompute of at least the per-family variant scores and the
`three_way_closure_gain_mean = -0.0666666666666667`). If the independent
recompute does not match the banked artifacts, stop and emit
`failure_manifest.json` rather than diagnosing numbers it cannot reproduce.

Trace-sufficiency gate (handoff rule 6): before diagnosing, emit
`trace_field_sufficiency.json` confirming the fields each report needs are
present (`S_before, O_t, pre_action_prediction, A_t, env_result, reward,
prediction_error, U_t, M_diff, S_after, variant, family_id, seed, rule_seed,
episode, tick`). If a required field is missing for a given report, that report
must emit `trace_insufficient_for_diagnosis` for that question rather than guess.

Computed-evidence provenance gate: `next_route_decision.json`'s `verdict` /
`route` field MUST be produced by a named decision function over the computed
diagnostic numbers, not written as a literal. The decision function and its
inputs must be inspectable, and the report header verdict must equal the
function output (this lineage has repeatedly failed on report-header verdict
literals; that failure mode is explicitly in scope to prevent).

Acceptance gate:
- scoped pytest for the new read-only analyzer passes;
- independent recompute of per-family variant scores and aggregate closure gain
  from `trace.jsonl` matches RUN_20260629T162834Z to within float tolerance;
- all eight required diagnosis artifacts are emitted and internally consistent;
- candidate / generator / baseline / metric / eval source hashes listed in
  `source_hash_check_001d.json` are unchanged;
- commit `b4ee157a01caef34c598bbeb3ac5ed1bb9b90f24` and the
  RUN_20260629T162834Z artifact bytes are unmodified;
- `next_route_decision.json` verdict is computed, not literal.

Required diagnosis artifacts (under a NEW dir `artifacts/ITL-DEV-BENCH-001E/<RUN_...>/`,
never inside the 001D run dir):
- `diagnosis_001d_factorial_failure.md`
- `family_saturation_attribution.json`
- `variant_underperformance_by_family.json`
- `action_invariance_by_variant.json`  (the decisive sub-test output)
- `pe_error_attribution_report.json`
- `memory_usefulness_report.json`
- `planner_read_effect_report.json`
- `action_heuristic_limitations_report.json`
- `trace_field_sufficiency.json`
- `next_route_decision.json`
- `failure_manifest.json` if any gate fails
- `claim_ceiling.txt` (or claim_ceiling field in each result)

Claim ceiling: bounded offline diagnosis of one frozen candidate's factorial
behavior under the 001C trace/replay contract. 001E may conclude only that the
*current minimal_loop implementation's* PE/memory/planner-read wiring did or did
not influence action and reward in this run. It may NOT conclude that the PE,
memory, or planner ideas are invalid in general; that the 001C generator is or
is not strong enough beyond smoke; nor anything about mechanism validity,
learning, adaptation, agency, autonomy, consciousness, emotion, Joi readiness,
EGO readiness, or product readiness.

Stop condition: stop and emit `failure_manifest.json` on any of:
independent recompute mismatch; required trace field missing; attempt to modify
candidate/generator/baseline/metric/eval sources or thresholds; attempt to
re-run the agent/environment; route verdict not derivable from a decision
function; or detection that a diagnosis number was tuned after inspection.

Rollback plan: 001E adds only new read-only analysis files and a new
`artifacts/ITL-DEV-BENCH-001E/` directory. If anything fails, delete the new
analyzer module and the new artifact dir; the 001D bank and commit remain the
authoritative record. No existing file is edited, so rollback is removal-only.

Expected changed files: this task card; one new isolated read-only analyzer
(e.g. `src/itl_devbench/eval/diagnosis_001e.py`, additive — must not edit any
file pinned in `source_hash_check_001d.json`); a scoped test file under
`tests/itl_devbench_001e/`; and new artifacts under `artifacts/ITL-DEV-BENCH-001E/`.

Forbidden changes: no edits to `minimal_loop.py`, `task_family_generator.py`,
`families.py`, `developmental_grid.py`, any frozen baseline agent, any
`src/itl_devbench/eval/*.py` file pinned in `source_hash_check_001d.json`,
`metrics.py`, or any 001A-001D artifact bytes. No threshold tuning. No re-run of
the agent/environment. No new candidate or generator.

Auto-Remote-Anchor: forbidden.

FUSE / line-ending caveat (provenance hygiene): the working tree currently shows
artifact/doc files as modified, but `git diff --ignore-all-space` is empty — this
is CRLF<->LF churn from a `.gitattributes` change, not content drift, and
`src/itl_devbench` is byte-clean vs HEAD. 001E must (a) verify any source/artifact
identity via `git show HEAD:<path> | sha256sum` against committed blobs, not via
mount readback, to avoid the known FUSE truncation false-mismatch; and (b) must
not "normalize" or commit the existing EOL churn as part of this task.

## Bounded Audit

Real objective: produce a computed, replayable explanation of a negative result,
not to rescue or improve the candidate.

Strongest shortcut explanation: the diagnosis could simply restate the banked
verdict ("baseline saturated") without attributing it to a mechanism in the
trace. The action-invariance sub-test and the independent recompute requirement
exist to force attribution, not restatement.

Strongest invalidity risk: the route verdict is hand-written after inspecting the
numbers; or a "diagnosis" silently reads regenerated traces rather than the
frozen 001D trace; or the analyzer imports candidate internals and re-executes
them (turning diagnosis into a hidden re-run).

Falsifying result for the current framing: action-invariance fails (i.e. `A_t`
*does* diverge across variants on a non-trivial fraction of matched decision
points). If so, the inert-channel hypothesis is rejected and the diagnosis must
pivot to PE/memory/planner correctness (questions 4-7).

Insufficient evidence: any report that asserts a cause without a trace-derived
number behind it; aggregate-only claims without per-family/per-decision-point
attribution; or a route decision not tied to the decision function's inputs.

Mechanism status: this task validates nothing about any mechanism. It explains
one frozen implementation's factorial behavior under a benchmark contract.

Leakage / hardcoding checks: preserve and re-run the existing source-hash,
graph-cache access, replay, and forbidden-claim audits; additionally verify the
new analyzer reads only recorded artifacts (no env/agent import-and-execute) and
that `next_route_decision.json` verdict is a function output.

Acceptance signal: `diagnosis_001d_factorial_failure.md`,
`action_invariance_by_variant.json`, `family_saturation_attribution.json`, and
`next_route_decision.json` agree, are each backed by trace-derived numbers, and
reproduce the banked 001D figures on independent recompute.

## Route Decision Contract

`next_route_decision.json` must select exactly one route via the decision
function (not by hand). Permitted outcomes (from handoff):
- `diagnosis_supports_tombstone_minimal_loop_family`
- `diagnosis_supports_new_model_based_planner_candidate`
- `diagnosis_supports_delayed_credit_assignment_candidate`
- `diagnosis_supports_memory_retrieval_candidate`
- `diagnosis_supports_generator_specific_redesign`
- `diagnosis_inconclusive_needs_artifact_inspection`

Suggested (non-binding) decision rule the function should implement, keyed to the
action-invariance result so the route is mechanically determined:
- if `A_t` invariant across variants on >= the pre-declared fraction in >= 4/5
  families -> channels are behaviorally inert -> route in
  {tombstone_minimal_loop_family, new_model_based_planner_candidate} selected by
  whether planner-read is even wired into action selection;
- elif planner-read changes `A_t` but only degrades reward (aliased_food 101/111
  pattern generalizes) -> `diagnosis_supports_new_model_based_planner_candidate`
  (current planner reads bad state);
- elif PE marginal is negative only on delayed-effect families ->
  `diagnosis_supports_delayed_credit_assignment_candidate`;
- elif memory is written but never read at decision time ->
  `diagnosis_supports_memory_retrieval_candidate`;
- elif all families saturate every baseline including obs_only with no headroom
  used -> `diagnosis_supports_generator_specific_redesign`;
- else -> `diagnosis_inconclusive_needs_artifact_inspection`.
The pre-declared invariance fraction must be fixed in the analyzer BEFORE reading
the trace and recorded in the artifact; it may not be tuned afterward.

## Collision Record

Approach A — narrative diagnosis from the banked report.md only: cheap, but fails
001E because it restates the verdict without trace-level attribution and cannot
answer questions 4-8.

Approach B — new read-only analyzer over the frozen RUN_20260629T162834Z
`trace.jsonl` + factorial JSONs, emitting the eight attribution artifacts and a
computed route decision: produces the required evidence without touching
candidate/generator/baselines or re-running anything. Failure mode is that the
trace may lack a needed field (handled by the sufficiency gate) or the route is
inconclusive (a permitted outcome).

Approach C — instrument the agent and re-run the factorial to capture richer
internal state: forbidden here, because re-running breaks the frozen-evidence
condition and would diagnose a different run than the one banked. If Approach B
reports `trace_insufficient_for_diagnosis`, a *separate* future task card may
authorize a re-instrumented re-run under a new run id — it is out of 001E scope.

Selected approach: Approach B.
