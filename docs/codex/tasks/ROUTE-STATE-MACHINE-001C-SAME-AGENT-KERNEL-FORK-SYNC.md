# ROUTE-STATE-MACHINE-001C-SAME-AGENT-KERNEL-FORK-SYNC

Status: DRAFT TASK CARD / ROUTE-STATE SYNC ONLY / NON-MECHANISM.

Auto-Remote-Anchor: forbidden

## Task id

`ROUTE-STATE-MACHINE-001C-SAME-AGENT-KERNEL-FORK-SYNC`

## Problem definition

The route-state machine is stale after the banked same-agent runtime-kernel
tiny-contrast result and fork decision. It still reports
`current_frontier_route_id=N2-SBMC-ENV-REDESIGN-001A`, while current repo
governance has moved to:

1. `N2-SBMC-ENV-REDESIGN-001A` remains terminal
   `ADJUDICATED / BASELINE_EQUIVALENCE`.
2. `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A` was executed and banked as
   `BASELINE_EQUIVALENCE / downgrade`.
3. Closed object is only the tiny passive/offline contrast mechanism-headroom
   claim:

   ```text
   baseline_equivalence_closure /
   no_mechanism_headroom_under_drift_aware_continual_replay
   ```

4. Runtime-kernel-v0 engineering scaffold is preserved as engineering
   infrastructure, not validated as a mechanism and not closed as an
   engineering runtime/kernel direction.
5. Fork decision selected Option A by default: close this contrast and keep the
   kernel as engineering runtime.
6. Option C may only be opened as a design-only preflight if an ex-ante
   active/interventional separation can be stated before implementation. C is
   not implementation authorization.

This task updates local route-state artifacts to record that boundary. It must
not run experiments, rerun the kernel contrast, rescue the baseline-equivalence
result, or implement any C-preflight.

## Current layer

Engineering implementation layer, limited to route-governance bookkeeping and
local validator hygiene. No mechanism-validation, subjectivity-validation, or
philosophical-consciousness layer is entered.

## Current stage

Post-bank route-state synchronization after:

- `48269bd61d809b95cd3a4b1d3e9f7f064fd2626f`
  (`bank: preserve runtime-kernel tiny contrast baseline equivalence`)
- `9b168cb790634b0765bc29729aab3fee311c9828`
  (`docs: record runtime kernel fork decision`)

Preflight at task-card drafting:

- repo root: `D:/Project/AIProject/MyProject/intelligence-theory-lab`
- branch: `codex/meta-theory-scaffold`
- HEAD: `9b168cb790634b0765bc29729aab3fee311c9828`
- upstream relation: ahead `9`, behind `0`
- worktree/index before this card: clean
- `.git/index.lock`: absent

## Mainline target

No EGO mainline target. The target is only the local
`ROUTE-STATE-MACHINE-001A` artifact bundle and local `routectl` validation
readback.

## Mainline integration status

None. This task must not touch EGO runtime, EGO mainline, UI, companion
behavior, LLM/AIRI integration, deployment, API keys, external services, or
background execution.

## Enabled-state requirement

The sync is enabled only through explicit local CLI validation:

```powershell
$env:PYTHONPATH="src"
python -m route_state_machine_001a.routectl validate --root .
python -m route_state_machine_001a.routectl status --root .
python -m route_state_machine_001a.routectl dashboard --root .
```

No runtime loop, scheduler, CI, remote publication, or production path is
enabled.

## Real-trigger evidence requirement

Real trigger evidence for this task is limited to local `routectl` commands
reading serialized route-state artifacts and producing a fresh
`validation_report.json` through callable code.

The already banked runtime-kernel trigger may be cited only as source readback:

```text
python -m src.same_agent_minimal_kernel_bridge_001a --output-dir artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A
```

Do not rerun it.

## Source readback requirements

Before editing, read and cite:

- `docs/codex/tasks/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A.md`
- `docs/codex/tasks/SAME-AGENT-KERNEL-DRIFT-AWARE-TOMBSTONE-FORK-001A.md`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/result.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/baseline_comparison.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/ablation_report.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/replay_report.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/leakage_report.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/failure_manifest.json`
- `artifacts/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/computed_evidence_provenance.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/N2-SBMC-ENV-REDESIGN-001A/closure.json`
- `docs/research/FSP-STAGE-LEDGER.md` entries `L-011`, `L-015`, `L-016`,
  `L-017`, and `L-018`.

Required readback facts:

- N2 remains `ADJUDICATED / BASELINE_EQUIVALENCE` and is untouched.
- Runtime-kernel tiny contrast is `BASELINE_EQUIVALENCE`.
- Candidate score = `1.0`.
- Strongest fair baseline =
  `drift_aware_regime_inferring_continual_replay`.
- Strongest fair baseline score = `1.0`.
- `batch_precompute=1.0` and `strong_meta_learner=1.0` are recorded as further
  saturation evidence in the same baseline comparison.
- Ablation, replay, leakage, and provenance controls are present, but do not
  rescue the mechanism-headroom claim because the fair baseline tied.
- Fork decision selects A by default and permits C only as design-only preflight
  under an ex-ante active/interventional separation.

## Hypothesis

Updating the route-state artifacts to include the banked same-agent kernel
closure and fork decision will reduce stale-frontier confusion without creating
new mechanism evidence or authorizing new implementation.

## Strongest baseline / shortcut explanation

A prose status note could say the same thing, but would not be machine-readable
or locally validated. This task must therefore produce route-state JSON packets
and a callable `routectl validate/status/dashboard` readback. It still remains
governance bookkeeping, not evidence of mechanism validity.

## Required route-state content

Create a new route packet:

```text
artifacts/ROUTE-STATE-MACHINE-001A/routes/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/
```

with:

- `state.json`
- `closure.json`
- `events.jsonl`

Minimum `state.json` semantics:

- `route_id`: `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A`
- `route_family`: `SAME-AGENT-KERNEL`
- `current_state`: `ADJUDICATED`
- `frontier_scope`: `terminal_tiny_passive_offline_contrast_baseline_equivalence`
- `closure_type`: `BASELINE_EQUIVALENCE` either directly or under
  `adjudication`
- `closed_object`:
  `tiny_passive_offline_contrast_mechanism_headroom_only`
- `runtime_kernel_scaffold`: preserved as engineering infrastructure; not
  mechanism-validated; not closed as engineering direction
- `default_fork_selection`: `A`
- `conditional_next_preflight`: C design-only preflight allowed only if an
  ex-ante active/interventional separation is stated
- all mechanism/theory/agency/mainline authorizations false
- source readback pointing to:
  - commit `48269bd61d809b95cd3a4b1d3e9f7f064fd2626f`
  - commit `9b168cb790634b0765bc29729aab3fee311c9828`
  - the banked result/baseline/ablation/replay/leakage/provenance artifacts
  - the fork decision card

Minimum `closure.json` semantics:

- `route_id`: `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A`
- `closure_type`: `BASELINE_EQUIVALENCE`
- `mechanism_evidence_authorized`: `false`
- `theory_pressure_authorized`: `false`
- `claim_ceiling.max`: bounded offline tiny-contrast negative evidence and
  route-state readback only
- `allowed_next_actions` includes:
  - preserve the tiny-contrast baseline-equivalence closure;
  - keep runtime-kernel-v0 as engineering scaffold;
  - draft C design-only preflight only if ex-ante active/interventional
    separation is stated;
  - run route-state validation.
- `forbidden_next_actions` includes:
  - claim mechanism validity;
  - claim runtime-kernel pass;
  - reopen/rescue/retune/rerun the tiny contrast;
  - start C implementation from this task;
  - start B/passive successor without a separate differentiator card;
  - modify EGO mainline/runtime/UI/LLM/AIRI/deployment/API paths;
  - push/tag/remote-anchor.
- `evidence_status` records baseline, ablation, replay, leakage positive
  control, and provenance as present, with mechanism validity and theory
  validity unknown.

Minimum `events.jsonl` semantics:

- event for tiny contrast banked as baseline equivalence;
- event for fork decision selecting A by default;
- event for route-state sync execution.

## Program-state update requirement

Update `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json` so the current
governed boundary no longer reads as N2-only. The existing schema names this
field `current_frontier_route_id`; until the schema is broadened, set it to:

```json
"current_frontier_route_id": "SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A"
```

Add explicit clarifying fields if useful:

- `current_route_posture`: `kernel_tiny_contrast_closed_default_A`
- `active_mechanism_frontier`: `none`
- `selected_default_fork`: `A`
- `c_preflight_status`: `design_only_allowed_if_ex_ante_active_interventional_separation_stated`

Update `allowed_next_actions` to include:

- `preserve_same_agent_kernel_tiny_contrast_baseline_equivalence`
- `keep_runtime_kernel_v0_as_engineering_scaffold_only`
- `draft_C_design_only_preflight_if_ex_ante_active_interventional_separation_stated`
- `run_route_state_machine_validation`

Update `forbidden_next_actions` to include:

- `claim_mechanism_validity`
- `claim_runtime_kernel_pass`
- `claim_agency_autonomy_subjectivity_consciousness_or_ego_readiness`
- `rerun_retune_or_rescue_same_agent_tiny_contrast`
- `start_C_implementation_without_design_only_preflight_and_separate_authorization`
- `start_B_passive_successor_without_ex_ante_differentiator`
- `push_tag_or_remote_anchor_without_explicit_authorization`

## C-preflight baseline floor to record

If a C design-only preflight is later drafted, it must face fair active
baselines including at least:

- UCB;
- max-information-gain / myopic information gain;
- Bayesian active learner;
- POMDP belief planner;
- drift-aware active replay baseline;
- oracle upper bound / structural Bayes-EVI where tractable;
- no-update / no-memory / random-action / cost-blind controls.

If the candidate cannot state why it should outperform or lag-separate from
these before implementation, no C implementation card is allowed.

## Ablation requirement

No mechanism ablation is authorized in this task. Route-governance validation
must at minimum prove that:

- the new route packet is present and parseable;
- closure packet is `BASELINE_EQUIVALENCE`;
- mechanism evidence and theory pressure are not authorized;
- `program_state.current_frontier_route_id` resolves to an existing route
  directory;
- local `routectl validate` returns `pass`.

If validator code is changed, add focused tests for:

- valid same-agent kernel boundary route passes;
- missing same-agent source readback fails if source-readback validation is
  generalized;
- current boundary route missing fails;
- tombstoned current boundary still fails.

## Trace / replay requirement

No mechanism replay is authorized. Route-governance replay is deterministic
revalidation from serialized JSON route-state artifacts plus `routectl`.

Do not rerun the kernel replay. Only read the already banked `replay_report.json`
as source evidence.

## Computed-evidence provenance gate

The fresh route-state result must be produced by callable code:

- `producer_function`: `build_validation_report`
- input artifacts include the new route packet and `program_state.json`
- `run_id` generated by `routectl validate`
- aggregation rule from `validation_report.json`
- `code_path_hash`
- `validation_errors=[]`
- `verdict=pass`

Do not hand-write a pass verdict without running validation.

## Acceptance gate

Accept only if all hold:

1. N2 state and closure remain unchanged.
2. A new route-state packet exists for
   `SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A`.
3. `program_state.json` records the same-agent kernel tiny-contrast closure /
   default-A posture and no longer presents N2 as the current governed boundary.
4. `STATUS.md` explains:
   - N2 remains terminal;
   - same-agent tiny contrast is closed as baseline equivalence;
   - runtime kernel is preserved only as engineering scaffold;
   - default fork is A;
   - C is design-only preflight if ex-ante active/interventional separation is
     stated.
5. `validation_report.json` is regenerated by callable `routectl validate` and
   reports `verdict=pass`.
6. `routectl status` and `routectl dashboard` read back the updated route
   posture.
7. If route-state code/tests are changed, `pytest tests/route_state_machine_001a
   -q` passes.
8. Staged/committed files are limited to this task's allowed paths.
9. No push, tag, or remote-anchor is performed.

## Claim ceiling

Local route-state synchronization and negative-evidence bookkeeping only. No
mechanism validity, learning headroom, runtime-kernel pass, agency, autonomy,
subjectivity, consciousness, EGO readiness, companion readiness, production
readiness, user benefit, or mainline effect.

## Stop condition

Stop and report without patching around if:

- `.git/index.lock` is present;
- worktree has unrelated dirty paths overlapping planned paths;
- N2 state/closure would need modification;
- the same-agent banked artifacts are missing or contradict the recorded
  baseline-equivalence verdict;
- `routectl validate` cannot pass without weakening safety checks;
- implementation would require rerunning the kernel contrast or any mechanism
  experiment;
- a C-preflight implementation, active environment, or successor mechanism is
  started;
- claim language upgrades beyond the ceiling.

## Rollback plan

Before commit, rollback by reverting only this task's changed files. Do not
delete or rewrite banked same-agent evidence, N2 evidence, PUM-ENV evidence, or
historical artifacts.

## Expected changed files

Required:

- `docs/codex/tasks/ROUTE-STATE-MACHINE-001C-SAME-AGENT-KERNEL-FORK-SYNC.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/program_state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/state.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/closure.json`
- `artifacts/ROUTE-STATE-MACHINE-001A/routes/SAME-AGENT-MINIMAL-KERNEL-BRIDGE-001A/events.jsonl`
- `artifacts/ROUTE-STATE-MACHINE-001A/STATUS.md`
- `artifacts/ROUTE-STATE-MACHINE-001A/validation_report.json`

Allowed only if needed for validator/readback hygiene:

- `src/route_state_machine_001a/state_machine.py`
- `src/route_state_machine_001a/validator.py`
- `tests/route_state_machine_001a/test_validator.py`
- schema files under `artifacts/ROUTE-STATE-MACHINE-001A/schemas/`

Forbidden unless separately authorized:

- `docs/research/FSP-STAGE-LEDGER.md`
- N2 route files
- PUM-ENV route files
- same-agent kernel source/tests/artifacts

## Forbidden changes

- No mechanism experiment.
- No kernel rerun, retune, rescue, or scoring.
- No C-preflight implementation.
- No EGO mainline/runtime/UI/companion behavior.
- No LLM/AIRI/API/deployment/external-service integration.
- No N2 modification.
- No baseline weakening.
- No push, tag, or remote-anchor.

## Local commit authorization

Local commit is authorized only if:

- validation passes;
- no stop condition is triggered;
- staged files are limited to the expected/allowed paths above;
- final `git status` after commit is clean.

Suggested commit message:

```text
chore: sync route state after same-agent kernel fork
```

Remote publication remains forbidden.

## Collision record

### Candidate 1: Data-only route-state sync

- Evidence produced: new route packet, program-state update, status text, and
  validation report.
- Strongest cheap baseline that could match it: a prose-only status note.
- Leakage / hard-coding risk: low to medium; may leave validator source-readback
  requirements stale.
- Smallest falsifying test: `routectl validate` fails or still reports N2 as
  current boundary.
- Expected failure mode: schema/validator hardcoding around N2 requires minimal
  validator repair.

### Candidate 2: Minimal validator-hygiene sync

- Evidence produced: data route packet plus minimal validator/test update to
  recognize the same-agent boundary and source readback.
- Strongest cheap baseline that could match it: data-only sync if validation
  already passes.
- Leakage / hard-coding risk: validator may special-case a pass instead of
  checking serialized fields.
- Smallest falsifying test: remove required same-agent source readback and
  observe validation still passing.
- Expected failure mode: overbuilding transition automation.

### Candidate 3: Full transition-system rewrite

- Evidence produced: generalized route transition writer and richer route graph.
- Strongest cheap baseline that could match it: minimal sync plus validation.
- Leakage / hard-coding risk: high; broad rewrite can create second logic path
  or route-policy claims.
- Smallest falsifying test: new writer changes N2 or old packets unexpectedly.
- Expected failure mode: scope creep into mechanism roadmap / governance engine.

Selected approach: Candidate 1 first. Use Candidate 2 only if validation or
readback requires minimal code/test hygiene. Candidate 3 is forbidden.

## What this does not prove

This task does not prove mechanism validity, runtime-kernel pass, learning
headroom, active/interventional separation, agency, autonomy, subjectivity,
consciousness, EGO readiness, companion readiness, production readiness, user
benefit, or mainline effect. It only synchronizes route-state bookkeeping with
already banked negative evidence and the selected default fork.
