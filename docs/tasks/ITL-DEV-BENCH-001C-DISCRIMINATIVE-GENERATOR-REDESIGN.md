# ITL-DEV-BENCH-001C - Discriminative Task-Family Generator Redesign

## Task Card

Task id: ITL-DEV-BENCH-001C-DISCRIMINATIVE-GENERATOR-REDESIGN

Problem definition: ITL-DEV-BENCH-001B repaired oracle headroom, but the environment remains too friendly to graph-cache / transition lookup baselines. Redesign the benchmark into a deterministic task-family generator that creates controlled pressure against obs-only, generic FSM, graph-cache, no-memory, no-PE, and planner-not-reading-update routes without tuning the candidate.

Current stage / layer: benchmark validation, environment generator redesign, and baseline discrimination infrastructure.

Mainline target: isolated `itl_devbench` generator/config/eval path only. No EGO, Joi, UI, persona, product, runtime, LLM, AIRI, or deployment path.

Enabled-state requirement: `python -m itl_devbench.eval.run_matrix --config configs/itl_devbench_001c.yaml --smoke` runs the five required generated families and writes the required machine-readable artifacts.

Real-trigger evidence requirement: a new timestamped run under `artifacts/ITL-DEV-BENCH-001A/RUN_<timestamp>/` with trace, manifest, replay/audit reports, generator spec, family/dimension summaries, graph-cache saturation report, oracle headroom report, and candidate hash check.

Hypothesis: A deterministic symbolic task-family generator with aliased observations, delayed effects, context-dependent affordances, rule reversal/return, and active experiment tradeoffs can create baseline-discrimination evidence without changing the minimal-loop candidate.

Strongest baseline: graph-cache / transition lookup can still saturate some symbolic families if exact current observation plus within-episode outcome memory is sufficient. Saturation must be measured by family, not hidden by aggregate.

Ablation requirement: run and log all eight minimal-loop variants unchanged; do not interpret them as mechanism evidence in this task.

Trace/replay requirement: preserve the existing chained event hash and pre-action prediction contract. Delayed effects must include `cause_event_id`, `delayed_effect_event_id`, `delay_ticks`, and `source_object_id` in trace event info.

Computed-evidence provenance gate: verdict, family metrics, saturation, split validity, oracle headroom, graph-cache audit, and candidate hash check must be derived from generated artifacts/source hashes.

Acceptance gate: scoped devbench tests pass; replay succeeds; audit succeeds; oracle valid on required families; graph-cache access audit passes; candidate hash unchanged from 001B; held-out split has no smoke overlap; required family-specific properties are present; final verdict is computed.

Claim ceiling: benchmark-discrimination repair only. No candidate evidence, mechanism evidence, learning validation, agency/autonomy/consciousness/Joi/EGO/product claim.

Stop condition: stop as `candidate_tuning_violation`, `oracle_headroom_regressed`, `replay_failed_evidence_invalid`, `audit_failed_evidence_invalid`, `artifact_preservation_violation`, `heldout_split_invalid`, or `graph_cache_leakage_detected` if any corresponding check fails.

Rollback plan: revert only the 001C task card/config/modules/tests and newly generated 001C run/latest artifacts. Do not delete or rewrite `RUN_20260629T151318Z` or `RUN_20260629T153235Z`.

Expected changed files: this task card, `configs/itl_devbench_001c.yaml`, `src/itl_devbench/envs/task_family_generator.py`, `src/itl_devbench/envs/families.py`, `src/itl_devbench/eval/family_metrics.py`, `src/itl_devbench/eval/saturation.py`, scoped eval/env changes, and five 001C tests.

Forbidden changes: no minimal-loop source changes; no candidate PE/memory/planner/policy tuning; no unrelated TLGP/LRGG/AIDSP/Joi/EGO code; no old artifact overwrite; no push/tag.

Auto-Remote-Anchor: forbidden.

## Bounded Audit Before Implementation

Real objective: make the benchmark harder to cheat and produce replayable by-family discrimination reports, not make a candidate win.

Problem-definition risk: a symbolic generator can accidentally create direct cue-response tasks where graph-cache or obs-only still saturates. The output must preserve saturation evidence if that happens.

Strongest invalidity reason: if held-out combinations overlap smoke, if graph-cache gets hidden/future information, or if candidate source changes, the result is invalid regardless of run success.

Falsifier for this task: replay mismatch, candidate hash mismatch, held-out overlap, missing delayed cause/effect trace, missing perceptual aliasing, oracle invalid by family, or graph-cache saturation above configured threshold.

Insufficient evidence: aggregate reward only; candidate scores without family/split/saturation context; natural-language report without machine-readable support.

Mechanism vs resemblance: this is generator validation only. Candidate behavior is logged for future 001D but not interpreted here.

Minimal validation: RED tests for family split, perceptual aliasing, delayed effect trace, candidate hash stability, family run outputs; smoke run; replay; audit; artifact readback.

## Collision Record

Candidate approach A - tune candidate to beat graph-cache:
- Evidence produced: potentially better candidate score.
- Strongest cheap baseline: graph-cache may still match under access parity.
- Leakage / hard-coding risk: very high and explicitly forbidden.
- Smallest falsifier: minimal-loop source hash changes.
- Expected failure mode: candidate_tuning_violation.

Candidate approach B - add task-family generator with measured saturation:
- Evidence produced: by-family oracle/headroom/saturation metrics, held-out split artifact, generator properties.
- Strongest cheap baseline: graph-cache can still saturate some families, but saturation is counted and bounded by config.
- Leakage / hard-coding risk: medium; controlled through generator spec and graph-cache audit.
- Smallest falsifier: graph-cache saturates too many targeted families or held-out overlaps smoke.
- Expected failure mode: still_baseline_saturated_environment_needs_redesign.

Candidate approach C - make graph-cache artificially weaker:
- Evidence produced: lower baseline score.
- Strongest cheap baseline: unfair baseline restriction invalidates comparison.
- Leakage / hard-coding risk: high.
- Smallest falsifier: graph-cache access contract no longer matches baseline definition.
- Expected failure mode: invalid baseline discrimination.

Selected approach: B. It preserves baseline-first evidence and does not optimize the candidate.
