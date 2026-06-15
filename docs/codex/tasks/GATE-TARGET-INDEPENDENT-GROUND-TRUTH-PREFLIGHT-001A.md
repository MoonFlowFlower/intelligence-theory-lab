# GATE-TARGET-INDEPENDENT-GROUND-TRUTH-PREFLIGHT-001A

## Bounded Task Card

Task id: `GATE-TARGET-INDEPENDENT-GROUND-TRUTH-PREFLIGHT-001A`

Problem definition: recent negative evidence shows two circular-evidence failures:
EAV 001B admitted candidate-controlled producer/expected digest circularity, and
`cb95bbd` removed candidate declaration and producer control but still scored
against candidate-authored `serialized_state.policy_map`. Before any future Gate
rerun or harness repair, the lab must determine whether the next intended Gate
target has harness-owned, environment-owned, or otherwise candidate-inaccessible
truth.

Current stage/layer: engineering-governance / Gate target independent-ground-truth
preflight only.

Mainline target: none. No Gate3, Gate4, integrated admission, bridge, runtime,
companion, or EGO-mainline wiring is authorized.

Enabled-state requirement: no new enabled path. This task is readback and
classification only.

Real-trigger evidence requirement: start from repo readback after commit
`72cb216a8134d21f1ff9e1d57232464a2df4c8cf` and tag
`remote-anchor-one-gate-harness-negative-audit-ledger-sync-001a-72cb216`; cite the
canonical ledger / failed-claims successor constraint requiring
candidate-inaccessible ground truth.

Hypothesis: a Gate evidence route is only worth rerunning if at least one
score-bearing path can be evaluated against harness-owned, environment-owned, or
otherwise candidate-inaccessible truth.

Strongest baseline: candidate-authored self-consistency, where the candidate
supplies both raw behavior and the truth key, as in the `policy_map` failure.

Ablation / contrast requirement: create or describe a policy-map-style positive
control for the selected Gate only if the repo defines a selected Gate target with
score-bearing truth fields. Hold observations/actions/states fixed, alter only a
candidate-authored truth field, and block if score/admission changes.

Trace/replay requirement: record target-selection source paths, truth inventory,
ownership rationale, temp probe commands, inspected-file hashes, and whether
replay can be recomputed from candidate-inaccessible observation/environment
state rather than candidate-authored truth.

Computed-evidence provenance gate: report/verdict/result prose cannot prove
ground-truth independence. Use repo source/readback inspection and callable probes
only where the selected target exists and a non-mutating probe is available.

Acceptance gate:

- `independent_ground_truth_available`: a target Gate is identified from repo
  readback, at least one score-bearing path uses candidate-inaccessible truth, and
  a policy-map-style positive control cannot flip admission by editing
  candidate-authored truth alone.
- `target_ground_truth_blocked`: a target Gate is identified, but all
  score-bearing truth is candidate-authored, candidate-derived, report-derived, or
  unknown.
- `target_selection_blocked`: no clear next executable Gate target can be
  identified from repo state. No Gate rerun is authorized.

Claim ceiling: independent-ground-truth preflight only. No Gate validity,
mechanism validity, admission readiness, mainline effect, bridge readiness,
runtime readiness, agency, consciousness, emotion, autonomy, stable user benefit,
or EGO readiness claim.

Stop condition: stop if target selection depends on memory rather than repo
readback; verifier/harness source repair begins; old bundles are mutated; a Gate
is rerun before truth ownership classification; candidate-authored truth is
treated as independent; or self-consistency is reframed as mechanism evidence.

Rollback plan: if blocked, preserve a bounded blocker artifact and leave source
unchanged. Do not repair verifier or harness source in this task.

Expected changed files:

- `docs/codex/tasks/GATE-TARGET-INDEPENDENT-GROUND-TRUTH-PREFLIGHT-001A.md`
- `artifacts/gate_target_independent_ground_truth_preflight_001a/**`

Forbidden changes:

- `src/one_gate_future_only_non_circular_harness_001a/**`
- `src/evidence_admission_verifier_001a/**`
- Gate3/Gate4 source or artifacts except read-only inspection
- integrated admission / bridge / runtime / mainline files
- unrelated tests or artifacts

Auto-Remote-Anchor decision: conditional. Remote-anchor is allowed only if A, B,
or C is clearly reached; final worktree is clean; changed files are within the
allowlist; and local HEAD, remote branch HEAD, local tag, and remote tag exactly
match after publication.

## Bounded Audit Before Classification

Layer: engineering-governance / evidence-hygiene preflight.

Real objective: prevent another Gate rerun or harness repair from reusing a
self-consistency oracle as ground truth.

Problem definition wrong if: this task treats a route recommendation as an
executable Gate target, or treats future task-card requirements as already
instantiated truth.

Strongest baseline explanation: a candidate can appear perfect when its own
serialized state supplies the scoring key.

Strongest invalidating reason: the repo may name only a future route direction,
not a concrete Gate target with score-bearing labels, rewards, latent states,
baselines, ablations, replay targets, leakage oracles, or pass conditions.

Would falsify current framing: a repo-defined current task card, source module,
or artifact target for the selected Gate that names concrete candidate-inaccessible
truth fields and a non-mutating positive control path.

Evidence still insufficient: route-governance prose that says a future target
can be specified; a report verdict; a task name; a selected route without an
executable target; or old score artifacts from unrelated historical Gates.

Tests mechanism or resemblance: this task tests neither. It classifies whether a
future evidence route has independent target truth available.

Risk checks:

- hard-coding: no new mechanism or verifier code is authorized.
- local optimum: do not repair the failed future-only harness.
- Zeno trap: block target selection instead of another harness repair if no target
  exists.
- evidence leakage: do not accept candidate-authored or report-derived truth.
- weak baseline: preserve the policy-map self-consistency baseline as the main
  challenger.
- schema split / second logic path: no new schema or runner path is introduced.
- replay weakness: no replay claim unless a selected target can recompute from
  candidate-inaccessible state.
- claim inflation: route/governance classification only.

Minimal validation: git anchor readback, canonical ledger/failed-claims readback,
selected-route source readback, search for an ACP-BV task-card/source target,
hash inspected files, JSON parse produced artifacts, and verify changed-file
allowlist.

Stop condition result: target selection is blocked if repo readback names only a
route selected for future task-card drafting, with implementation unauthorized
and no executable target artifact.

Acceptance signal: one of A/B/C in the task card is explicitly returned with
machine-readable artifact readback.

## Result Summary

Verdict: `target_selection_blocked`.

Repo readback identified `ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY` as a
selected route for future task-card drafting only, not as an executable Gate
target. The same source states implementation remains unauthorized and the next
minimal action is to draft a future ACP-BV task card. A tracked-file search found
no ACP-BV task card or source target to inventory.

Because no concrete selected Gate target exists, this task cannot classify
score-bearing truth ownership for labels, rewards, partner/latent state,
baseline targets, ablation targets, replay targets, leakage oracles, or admission
conditions. No Gate rerun is authorized.

Next minimal closed-loop action: draft the ACP-BV task card only, if separately
authorized, and require it to define candidate-inaccessible truth ownership before
any harness or Gate rerun.
