# SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A

Status: DRAFT TASK CARD / ROUTE-DESIGN GOVERNANCE ONLY.

This card drafts the minimal runtime-kernel v0 successor route after
`N2-SBMC-ENV-REDESIGN-001A` was terminally closed as
`ADJUDICATED / BASELINE_EQUIVALENCE`. It does not reopen N2, does not assign a
new route-state frontier, and does not authorize code execution in the current
session. Implementation requires separate explicit operator authorization to
execute this card.

Auto-Remote-Anchor: forbidden

## Task id

`SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A`

## Current stage / route-state readback

- Repo preflight at drafting:
  - branch: `codex/meta-theory-scaffold`
  - HEAD: `a06d736a36d06bc5ed75ebcc0757682f23390a42`
  - worktree/index before this card: clean
  - remote relation: ahead of `origin/codex/meta-theory-scaffold`
- Route-state artifacts read:
  - `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
  - `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`
  - `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
  - `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json`
  - `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/closure.json`
  - `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/state.json`
  - `artifacts/ROUTE-STATE-MACHINE-001A/routes/PUM-ENV-v0/closure.json`
- Current route-state readback:
  - `N2-SBMC-ENV-REDESIGN-001A`: `current_state=ADJUDICATED`,
    `closure_type=BASELINE_EQUIVALENCE`, `mechanism_validity=unknown`,
    `theory_validity=unknown`, `future_scoring=false`,
    `mechanism_experiment=false`.
  - `PUM-ENV-v0`: `current_state=TOMBSTONED`,
    `closure_type=INSTRUMENT_INVALID`, historical packet only, no fresh
    adjudication.
  - `program_state.json` allows drafting a bounded successor task card and
    forbids starting a successor route without one.
- Ledger readback from `docs/research/FSP-STAGE-LEDGER.md`:
  - `L-011`: PUM-ENV is terminal `INVALID_INSTRUMENT`; passive/equal-access
    observational-proxy line closed; future active-axis or N2 mechanism claims
    require their own environment certification.
  - `L-015`: same-agent kernel discriminability spec banked; a closed loop buys
    ablation surfaces only; the hard bar is the integrated-cache + learning
    baseline family.
  - `L-016`: concrete R4 environment argument banked; proceed-to-draft-kernel
    STEP-A is qualified, with decisive contrast against drift-aware
    regime-inferring continual replay.
  - `L-017`: N2 STEP-B result reached ideal headroom by `graph_closure`;
    strongest fair baseline macro-F1 reached ideal; interpretation is
    baseline-equivalence closure-review evidence, not mechanism validity.
  - `L-018`: operator accepted N2 terminal closure as local route-governance
    valid negative evidence only; successor runtime-kernel work requires a
    separate bounded task card and fresh baseline contract.

## Current layer

Engineering implementation planning + mechanism-hypothesis test design, with a
learning/adaptation evaluation boundary. No subjectivity-validation or
philosophical-consciousness claim is entered.

## Problem definition

The lab needs a successor route after the pure-relational N2 surface was closed
because `graph_closure` reached the ideal headroom. The successor must not rescue
or reinterpret N2. It must define a minimal runtime-kernel v0 scaffold whose live
path is:

```text
observe
→ predict
→ act
→ feedback
→ prediction_error
→ update belief / memory
→ replay / consolidate
→ next action changes because of the update
```

The problem is not to show agency, autonomy, subjectivity, consciousness, EGO
readiness, companion readiness, or mainline effect. The problem is to define a
bounded, replayable, baseline-pressured task card that can later test whether a
single persistent kernel can produce causally state-dependent adaptation under a
fresh environment and baseline contract.

## Bounded audit before implementation

- Real objective: produce a task card that narrows successor work to an isolated,
  executable, evidence-bearing runtime-kernel v0 probe after N2 terminal closure.
- Strongest baseline explanation: any visible closed-loop improvement may be
  reproduced by a scripted policy, lookup/cache, batch precompute, vanilla replay,
  or drift-aware regime-inferring continual learner with equal data and access.
- Strongest invalidity risk: the kernel may only demonstrate engineering
  plumbing; action changes may be if-else reactions to feedback rather than a
  causal effect of prediction error, belief update, memory, and consolidation.
- Falsifier for the framing: the same observation under different serialized
  belief/memory states does not change the selected action; or the strongest
  legal baseline ties the kernel; or replay cannot recompute behavior from
  serialized state plus observation.
- Insufficient evidence: a natural-language demo, stored-output replay, UI
  behavior, a single toy trace without baselines, or ablations that do not rerun
  the live path.
- Mechanism-vs-resemblance classification: this can test a bounded mechanism
  only if candidate behavior is recomputed from state, observation, prediction,
  feedback, and update history and survives baseline/ablation pressure. Otherwise
  it is only behavioral resemblance or infrastructure.
- Anti-hardcoding checks to preserve:
  - no hidden rule in action names, fixture names, filenames, or observations;
  - no second logic path used only by tests;
  - no threshold tuning after results;
  - no schema split that hides failure;
  - no renderer-visible behavior as causal evidence;
  - no claim inflation from closed-loop plumbing to agency or subjectivity.

## Mainline target

Future activation of this card targets only an isolated ITL evidence path:

- future local entrypoint, if authorized:
  `python -m src.same_agent_minimal_kernel_bridge_001a.run ...`
- future source scope, if authorized:
  `src/same_agent_minimal_kernel_bridge_001a/`
- future test scope, if authorized:
  `tests/same_agent_minimal_kernel_bridge_001a/`
- future artifact scope, if authorized:
  `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/`

It does not target EGO mainline runtime, UI, companion behavior, AIRI, LLM
integration, deployment, API keys, or external services.

## Mainline integration status

Not integrated. This draft card creates no runtime entrypoint and no enabled
kernel path. Future implementation, if separately authorized, remains isolated
inside ITL and does not become EGO mainline.

## Enabled-state requirement

- Current card: execution disabled; route-design governance only.
- Future implementation: default-off local CLI/test invocation only.
- No automatic scheduling, no background loop, no EGO runtime hook, no UI hook,
  no external service, and no LLM/provider dependency.
- A run counts as enabled only when the local entrypoint is explicitly invoked
  and produces live-path trace/artifacts under the task artifact directory.

## Real-trigger evidence requirement

Future execution must show all of the following from the live path:

1. `observe`, `predict`, `act`, `feedback`, `prediction_error`,
   `belief_or_memory_update`, `replay_or_consolidation`, and `next_action`
   events occur in order with shared `run_id`, `episode_id`, and `step_id`.
2. The prediction is action-conditioned and recorded before feedback.
3. Prediction error is computed from the pre-action prediction and actual
   feedback, not written post hoc as an explanation.
4. Belief/memory update writes a structured event with an ID and before/after
   state hash.
5. Action selection reads the updated belief/memory store; dependency IDs are
   recorded.
6. A counterfactual real-trigger check runs the same observation with different
   serialized belief/memory states and requires different action distributions
   or selected actions when the update is relevant.
7. Removing or corrupting the update/replay path changes downstream behavior in
   the expected direction.

## Hypothesis

H_target, bounded and unlikely: in the concrete `E* / G*` family from
`SAME-AGENT-KERNEL-R4-CONCRETE-ENV-ARGUMENT-001A`, a minimal persistent runtime
kernel with action-conditioned prediction, prediction-error-gated belief/memory
updates, replay/consolidation, and action selection from updated state can
produce held-out adaptation under bounded online resources that is not matched
by integrated cache, no-update, vanilla replay, batch precompute, or drift-aware
regime-inferring continual replay under equal access and budget.

H_null, likely: a known fair baseline, especially drift-aware regime-inferring
continual replay or batch additive-fit/segmentation under the allowed budget,
matches the kernel. Verdict then becomes baseline equivalence / engineering
demo downgrade, not mechanism evidence.

## Strongest baseline

The future baseline panel must inherit and not weaken the `L-015` frozen
integrated baseline family:

- cache subfamily:
  - `episodic_traversal`
  - `count_table`
  - `transition_table`
  - `successor_map`
  - `rag_summary`
  - `no_update`
- learning subfamily:
  - `online_no_replay`
  - `vanilla_experience_replay`
  - `standard_continual_replay`
  - `from_scratch_per_task`
  - `strong_meta_learner`
- decisive challenger for `G*`:
  - drift-aware / regime-inferring continual learner with online change-point
    detection, regime-indexed replay buffer, and per-regime online additive or
    low-rank completion.
- reducibility controls:
  - batch precompute on the same data where admissible;
  - no-memory / no-update;
  - scripted feedback-reactive policy for the minimal closed-loop contract.

Tie with any legal control baseline under the predeclared equivalence band
forces baseline-equivalence closure or downgrade. It must not be patched into a
mechanism pass.

## Ablation requirement

Future execution must rerun episodes under real interventions:

- no-update: prediction error is computed but cannot write belief/memory;
- no-memory-read: action selector is denied belief/memory reads;
- no-replay: replay/consolidation disabled;
- corrupted replay: replay samples are permuted or mismatched by regime;
- prediction-error shuffle: feedback remains but PE is assigned to wrong event;
- consolidation deletion: consolidated store is deleted before held-out action;
- counterfactual memory: same observation with two serialized states must produce
  different action distributions when the learned rule is relevant;
- action-conditioning ablation: prediction ignores action and should lose where
  action-conditioned prediction is necessary;
- positive-control leakage: inject an obvious leaked target/regime field and
  require the scanner to flag it.

Ablations that only mask outputs or compare stored hashes are insufficient.

## Trace / replay requirement

Future traces must be JSONL or CSV with at least:

- `task_id`, `run_id`, `seed`, `episode_id`, `step_id`;
- `producer_function`, `code_path_hash`, config/source hashes;
- `state_hash_before`, serialized state pointer/hash;
- observation payload and observation schema version;
- action candidates, action chosen, and action selection dependency IDs;
- pre-feedback prediction payload;
- feedback/outcome payload;
- prediction error value and aggregation rule;
- belief/memory write ID, delta summary, before/after hashes;
- replay/consolidation event IDs, source memory IDs, and output hashes;
- `state_hash_after`;
- downstream action-change marker when applicable.

Replay must recompute prediction, action selection, update, and downstream
behavior from serialized state plus observation. Stored-output or hash-only
replay does not satisfy this card.

## Computed-evidence provenance gate

All future evidence-bearing outputs must be produced by callable computation
paths, not literals, static verdict dictionaries, or tests that only assert
pass. Required machine-readable artifacts under
`artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/`:

- `result.json`
- `trace.jsonl` or `trace.csv`
- `baseline_comparison.json`
- `ablation_report.json`
- `replay_report.json`
- `leakage_report.json`
- `computed_evidence_provenance.json`
- `failure_manifest.json` if anything fails
- `claim_ceiling.txt` or `claim_ceiling` inside `result.json`

Every score must record:

- `producer_function`
- input artifacts
- `run_id`
- seed/context/episode IDs
- aggregation rule
- `code_path_hash`

Baselines must be independent callable implementations. Leakage scans must use a
real scanner and include at least one positive-control case. Any unused frozen
seed, train context, held-out context, or counterfactual pair blocks the evidence
claim.

## Acceptance gate

Acceptance for this draft-card task:

- this file exists with the required fields;
- it cites N2 terminal closure as negative route-governance evidence;
- it preserves `Auto-Remote-Anchor: forbidden`;
- it does not implement code, mutate route state, reopen N2, or claim mechanism
  validity.

Acceptance for future execution, if separately authorized:

1. Freeze the concrete environment generator/config before scoring.
2. Run the cheapest decisive contrast first: minimal kernel vs drift-aware
   regime-inferring continual replay in `G*`, equal data and stated budget.
3. Verify cache-subfamily members remain at chance plus predeclared MDE on
   cache-void held-out; any cache member above this threshold is leakage,
   mislabeled learner, or environment failure.
4. Produce real-trigger evidence for the full loop and next-action change from
   updated belief/memory.
5. Candidate must beat max over the frozen baseline panel; tie means
   baseline-equivalence closure/downgrade.
6. Required ablations must destroy the claimed effect in the expected direction.
7. Replay recomputation must pass from serialized state plus observation.
8. Computed-evidence provenance must be complete.
9. Claim ceiling must remain bounded offline kernel evidence only.

## Claim ceiling

Current claim ceiling: task-card / route-design governance only.

Future execution, if authorized and successful, can claim at most bounded offline
evidence that a minimal isolated runtime-kernel scaffold survived a specific
baseline/ablation/replay test under stated conditions. It cannot claim mechanism
validity in general, theory correctness, functional-subject success, agency,
autonomy, subjectivity, consciousness, emotion, EGO readiness, companion
readiness, production readiness, stable user benefit, or mainline effect.

## Stop condition

Stop and report without rescue if any of these occur:

- any route-state artifact or ledger source conflicts with this card;
- any route is `CLOSURE_REVIEW_REQUIRED` without explicit exact-path
  authorization;
- N2 is reopened, re-scored, reinterpreted as a pass, or used as mechanism
  evidence;
- PUM-ENV v0 is reused as a certified environment;
- hidden labels, regime IDs, target fields, or action/observation names leak the
  answer;
- a cheap scripted/cache/continual/batch baseline matches the candidate;
- prediction error is not computed from pre-action prediction plus feedback;
- action selector ignores updated belief/memory;
- replay cannot recompute behavior from serialized state plus observation;
- tests use a second logic path not used by the live CLI;
- thresholds or baselines are changed after seeing results;
- implementation expands into UI, persona, LLM integration, EGO runtime,
  deployment, API keys, or companion behavior;
- claim language upgrades beyond the ceiling.

## Rollback plan

For this draft-card task: remove only
`docs/codex/tasks/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A.md` if the operator
rejects it. No code, route state, ledger append, or artifact mutation is
required by this draft.

For future execution, if authorized: revert only scoped source/test files and
preserve any generated failure artifacts as negative evidence unless the
operator explicitly instructs otherwise. Do not rewrite old artifacts or N2
closure records.

## Expected changed files

Current draft task:

- create `docs/codex/tasks/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A.md`

Future implementation, only if separately authorized:

- create `src/same_agent_minimal_kernel_bridge_001a/`
- create `tests/same_agent_minimal_kernel_bridge_001a/`
- create `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/`
- optional route-state or ledger update only under a separate route-state task
  card naming exact paths and transition.

## Forbidden changes

- Any modification to `artifacts/N2-SBMC-ENV-REDESIGN-001A/`.
- Any modification to N2 closure/state packets except under a separate exact
  route-state task card.
- Any attempt to reopen, rescue, or reinterpret N2.
- Any use of PUM-ENV v0 as a certified environment.
- EGO mainline runtime, UI, companion behavior, relationship learning, emotion
  systems, proactive behavior, LLM integration, AIRI integration, deployment,
  API keys, external services, or global schema migrations.
- Weakening `L-015` / `L-016` baseline family, R1-R6, or the decisive
  drift-aware continual replay challenger.
- Rewriting historical artifacts or old failures into passes.

## Collision record

### Candidate 1: Minimal engineering scaffold

- Description: implement the smallest toy closed loop with structured state,
  prediction, feedback, memory update, and next-action change.
- Evidence it would produce: live trace showing the loop fires and state changes.
- Strongest cheap baseline that could match it: scripted feedback-reactive
  policy or lookup table keyed by last failure.
- Leakage / hard-coding risk: high; door/key/room names or action names can
  encode the rule; next-action change can be an if-else.
- Smallest falsifying test: same observation with different serialized memories
  fails to change action; or a scripted policy matches all metrics.
- Expected failure mode: infrastructure-only result; useful for plumbing but not
  mechanism evidence.

### Candidate 2: Strongest baseline / shortcut explanation

- Description: before building the full kernel, instantiate the strongest legal
  baseline panel, especially drift-aware regime-inferring continual replay and
  batch additive-fit/segmentation where admissible.
- Evidence it would produce: negative or narrowing evidence that the proposed
  regime is already solved by known baseline machinery.
- Strongest cheap baseline that could match it: the baseline itself; if it
  matches, the kernel has no discriminative headroom under this task.
- Leakage / hard-coding risk: medium; baseline may accidentally receive latent
  regime ID or target fields and must pass the same leakage scan.
- Smallest falsifying test: remove leaked regime/target fields and require
  cache-void self-test; if the baseline still ties, candidate route downgrades.
- Expected failure mode: expected H_null, baseline equivalence to a known
  continual/replay method.

### Candidate 3: Mechanism-faithful runtime kernel

- Description: implement a persistent hash-chained kernel with action-conditioned
  prediction, PE-gated belief/memory update, replay/consolidation, and action
  selection that reads updated state.
- Evidence it would produce: live-path loop trace, counterfactual
  memory-dependent action changes, replay recomputation, ablation sensitivity,
  and baseline comparison under `E* / G*`.
- Strongest cheap baseline that could match it: drift-aware regime-inferring
  continual replay, batch precompute, or a strengthened cache that crosses into
  the learning subfamily.
- Leakage / hard-coding risk: high unless schema and generator are frozen before
  scoring and the kernel cannot read latent codes/regime IDs.
- Smallest falsifying test: drift-aware continual replay ties within equivalence
  band; no-replay/no-update ablations do not destroy the effect; or replay cannot
  recompute behavior.
- Expected failure mode: route closes as baseline equivalence or downgrades to an
  auditable engineering demo.

### Selection

Select Candidate 3 only as the future mechanism-faithful target, but execute the
Candidate 2 decisive contrast first if this card is later authorized. If the
strongest fair baseline ties on the tiny CPU contrast, stop before broader
kernel plumbing and record baseline equivalence / downgrade. Candidate 1 is
allowed only as internal plumbing if it is explicitly labeled infrastructure and
not used for mechanism claims.

## External chat-note readback

The operator-provided ChatGPT share
`https://chatgpt.com/share/6a4bd0c1-447c-83ea-8b90-05cd66c094a9` was inspected
as non-canonical design context. It supports the same bounded framing:
closed-loop adaptive runtime first; no persona/UI/companion shortcut; toy
environment first; failure must classify into engineering bug, contract-not-wired,
task-too-weak, update-rule-insufficient, baseline-saturated, scope-too-large, or
route-tombstone. The share is not evidence and does not override repo artifacts,
route state, or the ledger.

## What this does not prove

This card proves no mechanism validity, no learning result, no functional
subject, no agency, no autonomy, no subjectivity, no consciousness, no emotion,
no EGO readiness, no companion readiness, no production readiness, and no
mainline effect. It only defines a bounded successor task card that can later be
accepted, revised, or rejected.
