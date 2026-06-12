# EGO-MAINLINE-ADMISSION-TASK-CARD-001A

## 1. Task Identity

```text
task_id = EGO-MAINLINE-ADMISSION-TASK-CARD-001A
verdict = ego_mainline_admission_task_card_001a_contract_drafted
layer = bounded EGO-mainline admission contract drafting only
execution_authorized = false
ego_mainline_runtime_authorized = false
bridge_runtime_authorized = false
companion_behavior_authorized = false
llm_rag_authorized = false
user_model_authorized = false
relationship_authorized = false
emotion_authorized = false
personalization_product_demo_authorized = false
romance_attachment_authorized = false
persistent_profile_authorized = false
long_term_human_user_memory_authorized = false
ego_repository_modification_authorized = false
real_user_data_authorized = false
```

This task drafts the future bounded EGO-mainline admission contract. It does not
execute an admission test.

## 2. Layer

Bounded EGO-mainline admission contract drafting only.

This is not EGO mainline implementation, bridge runtime work, companion
behavior, LLM/RAG integration, user-model work, relationship learning, emotion
systems, personalization, product-demo work, romance, attachment, persistent
profile work, or long-term human-user memory work.

## 3. Scope And Non-Authorization Flags

Allowed output is limited to this task card and the machine-readable artifacts
under `artifacts/ego_mainline_admission_task_card_001a/`.

This task does not authorize:

```text
EGO runtime implementation
EGO repository modification
bridge runtime
LLM/RAG integration
real user data use
persistent human-user memory
user model
relationship learning
emotion system
personalization
companion behavior
product demo
romance or attachment behavior
```

## 4. Parent Evidence Inventory

Primary authorization:

```text
EGO-MAINLINE-READINESS-AUDIT-001B
commit = f648dac4bfbcdc7a98c1edea5a97dbef4101d83a
remote_tag = remote-anchor-001o-f648dac
verdict = ego_mainline_readiness_audit_001b_authorize_admission_task_card
claim_ceiling = bounded EGO-mainline readiness revalidation audit evidence for admission-contract authorization only
authorized_next_step = EGO-MAINLINE-ADMISSION-TASK-CARD-001A drafting only
```

Mandatory inherited standard:

```text
COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A
path = docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md
commit = 09cff85ac377aaa99f913c30e3d31f85264d1344
remote_tag = remote-anchor-001i-09cff85
verdict = computed_evidence_provenance_contract_001a_created
```

Current post-bridge positive candidate:

```text
POST-BRIDGE-ADMISSION-EXECUTABLE-001D
commit = c2f6c5184a119202dd0a7efc23d3bfe3317af890
remote_tag = remote-anchor-001n-c2f6c51
verdict = post_bridge_admission_executable_001d_pass
claim_ceiling = bounded post-bridge admission evidence under computed-evidence provenance contract after leakage-gate repair only
status = current bounded post-bridge positive candidate with caveats
```

Historical context only:

```text
EGO-MAINLINE-READINESS-AUDIT-001A
commit = ed9355b464162065dfbba77a6a6ebfad22cb1767
remote_tag = remote-anchor-001l-ed9355b
prior_verdict = ego_mainline_readiness_audit_001a_authorize_admission_task_card
current_status = historical context only, revalidated by 001B, not direct actionable authorization
```

## 5. Negative Evidence Handling

The future executable EGO-mainline admission test must preserve these statuses:

```text
POST-BRIDGE-ADMISSION-EXECUTABLE-001B = invalidated as downstream positive evidence
POST-BRIDGE-ADMISSION-EXECUTABLE-001C = historical/suspended as downstream positive evidence
EGO-MAINLINE-READINESS-AUDIT-001A = historical context only, not direct actionable authorization
```

`POST-BRIDGE-ADMISSION-EXECUTABLE-001B` may be cited as negative evidence,
evidence-custody context, or false-positive artifact-generation evidence. It
must not be cited as positive post-bridge evidence.

`POST-BRIDGE-ADMISSION-EXECUTABLE-001C` may be cited as historical nominal
evidence subject to the admitted leakage fail-ability blocker. It must not be
cited as current positive evidence that the leakage boundary is clean.

Any future executable task that uses 001B or 001C as positive evidence must
block with:

```text
failed_001b_positive_evidence_leak
failed_001c_positive_evidence_leak
```

## 6. Current Evidence Status

Current bounded evidence status:

```text
001B_executable_status = invalidated_as_downstream_positive_evidence
001C_executable_status = historical_suspended_as_downstream_positive_evidence
001D_executable_status = current_bounded_post_bridge_positive_candidate_with_caveats
001A_readiness_audit_status = historical_context_only_revalidated_by_001B
001B_readiness_audit_status = authorizes_this_task_card_drafting_only
```

The strongest currently allowed statement is that 001B-readiness-audit
authorizes drafting this contract. It does not authorize execution, EGO runtime,
bridge runtime, companion behavior, or product work.

## 7. Problem Definition

Draft the future bounded EGO-mainline admission contract. The contract defines
what evidence would be required before any later bounded EGO-mainline executable
admission test can be considered.

The future executable test may only evaluate whether a bounded EGO-mainline
admission contract can be satisfied under synthetic or controlled evidence
conditions. It must not build or modify EGO runtime.

## 8. Wrong Problem Definition

Wrong problem definitions:

```text
Is EGO ready?
Can EGO runtime begin?
Can bridge runtime begin?
Can companion behavior begin?
Can LLM/RAG integration begin?
Can user-model, relationship, emotion, personalization, product-demo, romance, attachment, persistent profile, or long-term human-user memory work begin?
Does 001D prove mechanism validity?
Does this contract prove agency, selfhood, consciousness, real emotion, subjective experience, real relationship learning, companion readiness, or stable user benefit?
```

## 9. Hypothesis

Engineering hypothesis for the future executable admission test:

```text
If a bounded EGO-mainline admission executable is later run under this contract,
then every verdict-bearing result can be derived from callable computation paths,
old negative evidence can remain preserved, 001D can be used only within its
bounded claim ceiling and caveats, and no runtime/product authorization will be
created.
```

Strongest baseline explanation:

```text
A hidden lookup over serialized state hashes, identity tokens, memory keys,
state tables, transcripts, summaries, graph/cache structures, snapshots, or
stitched outputs could mimic continuity without testing carried-state causality.
```

Strongest reason this task may be invalid:

```text
A contract card can create false confidence if downstream work treats it as EGO
readiness or drops the 001D caveat during executable admission.
```

Result that would falsify this framing:

```text
The future executable admission task uses 001B or 001C as positive evidence,
omits 001D caveats, weakens computed-evidence provenance, lacks callable
baselines, lacks real ablation reruns, lacks same-surface leakage controls,
lacks behavior-causal replay where applicable, or authorizes runtime/product work.
```

Evidence that would still be insufficient:

```text
A schema-complete contract, clean JSON artifacts, remote anchors, and a future
bounded executable pass remain insufficient for EGO readiness, bridge readiness,
mechanism validity, agency, selfhood, consciousness, real emotion, real
relationship learning, companion readiness, or stable user benefit.
```

This task tests contract completeness and authorization boundaries only. It does
not test mechanism validity and does not produce behavioral resemblance.

## 10. Baseline Requirements

The future executable EGO-mainline admission test must use independent callable
baselines. Each baseline must consume legal comparable inputs, emit per-case
outputs before aggregation, record `producer_function`, record `code_path_hash`,
and prove invocation through tests or metric provenance.

Minimum baseline families:

```text
random policy
majority or no-action baseline where applicable
snapshot reload
stitched-output baseline
state-table lookup
identity-token lookup
memory-key lookup
summary retrieval
transcript retrieval
observation-only baseline
nearest-neighbor or lookup baseline
graph_lookup
transition_table
successor_map
count_table
fsm_planner
episodic_traversal
bounded-order window model order-1
bounded-order window model order-2
shuffled-history same-loss control
behavior imitation
frozen-state carryover
fresh-agent no-carryover
oracle control as upper-bound/leakage diagnostic only
trace-only replay as integrity hygiene only
```

Any fair baseline equivalence or baseline invocation gap blocks admission.

## 11. Ablation Requirements

The future executable test must use real ablation reruns. Every required
ablation must define an intervention function, apply the intervention to the
frozen episode set or a justified subset, rerun candidate behavior, recompute
scores from outputs, and record producer functions and code path hashes.

Minimum ablations:

```text
reset all memory
corrupt serialized state
replace serialized state
remove replay carryover
remove self-boundary carryover
remove viability carryover
remove social-latent carryover
remove identity_continuity_state
remove memory_carryover_state
time-shift state
cross-agent state swap
duplicate identity-token contrast
freeze post-bridge learning
remove post-bridge observation update
disable action
invert bridge mapping
```

Insensitive required ablations block admission.

## 12. Leakage Requirements

The future executable task must use real leakage scanners with same-surface
positive controls, clean controls, and surface-specific metric provenance.

Required scanned surfaces include:

```text
candidate inputs
trace rows
observation objects or rows
serialized state snapshots
serialized_state_provenance rows
metric_provenance rows
artifact path inventories
fixture names
labels
verifier-only fields
future observations
future partner responses
later-action labels
post-hoc metrics
test-only schema paths
renderer-visible behavior where applicable
```

The future task must preserve the 001D external red-team caveat:

```text
leakage metadata whitelist is global in 001D
values under reserved metadata keys such as metric_name or surface_label may be skipped on surfaces where those keys should not be privileged
future EGO-mainline admission work must require surface-scoped metadata whitelist behavior
future tests must include independent manual leakage injection tests, not only production injector tests
future stop conditions must distinguish leakage detected from scanner not fail-able
```

## 13. Replay / Behavior-Causal Replay Requirements

Where the future executable admission test makes behavior claims, replay must
recompute behavior from serialized state and observation. Hash-chain or trace
integrity replay is hygiene only.

Behavior-causal replay must:

```text
load serialized_state from artifacts
deserialize through the candidate public path
load or reconstruct observation from artifact or frozen seed
recompute candidate_action_id from serialized_state + observation
compare recomputed action with recorded action
emit mismatches
record replay_function and code_path_hash
```

Replay that only rehashes stored snapshots blocks admission for any behavioral
claim.

## 14. Frozen Input Consumption Requirements

Every frozen seed family, train context, heldout context, counterfactual pair,
cross-agent swap pair, duplicate identity-token contrast, and ablation
definition must be consumed by callable computation paths or explicitly absent
from the freeze before execution.

Unused frozen inputs block with:

```text
failed_unused_frozen_input
```

## 15. Source / Artifact Integrity Requirements

The future executable task must verify source and artifact integrity before and
after evaluation.

Minimum required integrity artifacts:

```text
stage0_freeze_manifest.json
execution_manifest.json
execution_manifest.sha256
protected_artifact_inventory_before.json
protected_artifact_hashes_before.json
protected_artifact_hashes_after.json
tracked_old_artifact_mutation_report.json
mutation_check_report.json
source_code_path_hashes.json or equivalent metric-level code_path_hashes
```

Old artifacts must not be rewritten. Any old-artifact mutation blocks
admission.

## 16. Metric Provenance Requirements

The future executable task must cite and comply with
`docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md`.

Every verdict-bearing metric must record at minimum:

```text
metric_id
metric_name
producer_function
producer_module
code_path_hash
run_id
episode_ids
seed_ids
train_context_ids_consumed
heldout_context_ids_consumed
counterfactual_pair_ids_consumed
input_artifact_paths
input_artifact_hashes
input_row_count
output_artifact_path
output_row_ids
aggregation_rule
threshold_used
threshold_frozen_before_run
computed_not_literal
failure_path_available
```

Literal metrics, static metric dictionaries, unconditional clean reports, and
tests that merely assert pass block admission.

## 17. EGO-Mainline Admission Boundary

The future executable EGO-mainline admission test may only evaluate whether a
bounded admission contract can be satisfied under synthetic or controlled
evidence conditions.

It may not:

```text
modify the Ego repository
modify EGO runtime
create EGO runtime files
connect to EGO mainline
use real user data
write persistent human-user memory
integrate LLM/RAG
create user-model, relationship, emotion, personalization, or companion behavior
```

Any boundary leak blocks admission.

## 18. Forbidden Runtime / Product Work

Forbidden in this contract and any directly authorized future executable
admission task:

```text
EGO runtime implementation
bridge runtime implementation
companion behavior
LLM/RAG integration
user model
relationship learning
emotion system
personalization
product demo
romance behavior
attachment behavior
persistent profile
long-term human-user memory
deployment
API keys or external services
real user data processing
```

## 19. Required Stop Conditions

The future executable admission task must stop and report blocked or failed if
any of the following occur:

```text
missing_parent_authorization
missing_remote_anchor
missing_computed_evidence_contract
001b_positive_evidence_leak
001c_positive_evidence_leak
001d_caveat_missing
claim_inflation
scope_leak
ego_repository_modification
runtime_or_product_work_created
baseline_equivalence
baseline_invocation_missing
ablation_not_rerun
ablation_insensitive
leakage_detected
leakage_scanner_not_fail_able
positive_control_missing
same_surface_positive_control_missing
manual_injection_test_missing
metadata_whitelist_not_surface_scoped
replay_not_behavior_causal
hash_only_replay_for_behavior_claim
unused_frozen_input
source_hash_mismatch
old_artifact_mutation
metric_provenance_missing
literal_metric_detected
static_metric_dictionary_detected
unconditional_clean_report_detected
threshold_tuning_after_results
negative_evidence_rewrite
```

## 20. Rollback Plan

If the future executable admission task blocks or fails:

```text
preserve_failure_artifacts = true
do_not_rewrite_old_artifacts = true
do_not_patch_thresholds_after_results = true
do_not_weaken_baselines = true
do_not_delete_negative_evidence = true
do_not_use_001B_or_001C_as_positive_evidence = true
do_not_enter_ego_mainline = true
do_not_create_runtime_or_product_work = true
minimum_patch = repair exact blocker in a new bounded task card or executable rerun with a new freeze
```

## 21. Acceptance Gates

This contract-drafting task may pass only if:

```text
parent_001b_readiness_audit_anchor_verified = true
computed_evidence_contract_cited = true
001b_invalidation_preserved = true
001c_suspension_preserved = true
001d_caveat_preserved = true
surface_scoped_metadata_whitelist_required = true
independent_manual_leakage_injection_tests_required = true
callable_baselines_required = true
real_ablation_reruns_required = true
behavior_causal_replay_required_where_applicable = true
frozen_input_consumption_required = true
source_artifact_integrity_required = true
metric_provenance_required = true
runtime_product_work_unauthorized = true
ego_repository_modification_unauthorized = true
claim_ceiling_preserved = true
```

The future executable admission task may pass only if all requirements in this
contract are implemented and the executable evidence remains inside the claim
ceiling.

## 22. Claim Ceiling

```text
bounded EGO-mainline admission contract drafting evidence only
```

The strongest claim from this task is that the repository contains a bounded
future admission-contract task card with explicit evidence requirements and
non-authorization boundaries.

## 23. What This Contract Cannot Prove

This contract cannot prove:

```text
EGO readiness
bridge readiness
companion readiness
mechanism validity
theory validity
agency
selfhood
consciousness
real relationship learning
real emotion
subjective experience
stable user benefit
correctness of any future EGO runtime
```

It also cannot prove that any future executable task will comply. Compliance
requires a later bounded executable task, callable computations, machine-readable
artifacts, failure-path tests, and review under this claim ceiling.
