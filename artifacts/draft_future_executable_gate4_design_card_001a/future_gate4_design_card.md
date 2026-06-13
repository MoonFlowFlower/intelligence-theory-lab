# FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-EXECUTION-CARD-001A

`DRAFT ONLY — NOT AUTHORIZED FOR IMPLEMENTATION`

This card is a future executable Gate4 design card. It is not an implementation task, not an experiment task, not a Gate4 execution task, not 002E, and not authorization to enter Gate5/admission/bridge/runtime/EGO-mainline.

## Problem Definition

002C dynamic partner-belief POMDP collapsed into bounded baseline-equivalence negative evidence. The candidate reached `1.0`, but faithful non-oracle baselines also reached candidate-equivalent performance, including serialized-state decoding, full-bundle decoding, static belief-table recovery, pair-count/frequency recovery, and n-gram trace lookup. 002D closed the 002C toy POMDP family and rejected same-family patching.

The future Gate4 problem is not to make another toy POMDP harder. The problem is to test whether a candidate can infer and update partner-relevant hidden causal state from partial observations, then use that state under heldout partner-family and task-schema transfer, counterfactual interventions, and distribution shift in a way faithful decoder, table, count, trace, retrieval, and leakage baselines cannot match under fair callable access.

## Current Stage

Future execution-card design only.

Allowed current output: a draft card and machine-readable future contracts.

Forbidden current output: source code, tests, environments, candidate agents, baselines, leakage scanners, replay code, datasets, experiments, 002C reruns, 002D reruns, 002E, Gate5/admission/bridge/runtime/EGO-mainline artifacts, or mechanism success claims.

## Mechanism Hypothesis

If a candidate maintains an internal partner-relevant causal state that is updated from partial observations, then it should:

- improve counterfactual partner prediction or action under heldout partner-family and task-schema transfer;
- degrade under real interventions that remove partner/social latent update, freeze memory update, remove counterfactual branches, or scramble observation order;
- remain replayable from `serialized_state + observation`;
- outperform faithful non-oracle shortcut baselines under fair access.

This is a bounded mechanism-proxy hypothesis only. It is not a claim about social-latent inference success, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, or user benefit.

## Evidence Target

Target ID:

```text
cross_family_social_causal_transfer
```

Evidence target:

```text
Candidate behavior must depend on replayable hidden partner-relevant state updates that support counterfactual prediction or action under unseen partner causal families and unseen task schemas, while faithful non-oracle baselines fail under fair callable access.
```

Primary future metric:

```text
cross_family_counterfactual_transfer_score
```

The future metric must be computed by a callable producer function over heldout partner-family, heldout task-schema, counterfactual intervention, and distribution-shift episodes. It must not be a literal score, static dictionary, unconditional pass report, or test that only asserts pass. The future implementation task must freeze any numeric threshold before candidate execution.

## Task-Family Definition

The future task family must include at least three generated partner causal families and at least two task schema families.

Partner causal families must differ in latent causal structure, not only label names. Examples of allowed family-level differences:

- observation token reliability differs by latent context;
- action consequence depends on delayed partner state;
- partner response changes after a counterfactual intervention;
- useful active probe differs by current posterior uncertainty;
- social-memory carryover affects later prediction only through prior interaction state.

Task schema families must differ in observable task form while preserving equivalent evidence fields and leakage boundaries. A heldout schema cannot reveal the target through different field names, ID formats, file paths, or artifact naming.

## Train, Heldout, And Counterfactual Splits

Future train split:

- `train_partner_family_alpha`
- `train_partner_family_beta`
- `train_task_schema_observation_action`

Future heldout partner-family split:

- `heldout_partner_family_gamma`
- `heldout_partner_family_delta`

Future heldout task-schema split:

- `heldout_task_schema_counterfactual_query`
- `heldout_task_schema_delayed_outcome`

Future counterfactual split:

- `counterfactual_partner_intervention_policy_shift`
- `counterfactual_partner_intervention_observation_reliability_shift`
- `counterfactual_partner_intervention_hidden_preference_reversal`

Future distribution-shift conditions:

- shifted observation reliability;
- shifted delayed outcome mapping;
- shifted partner response to active probe;
- shifted task schema with equivalent fields and no answer-bearing names.

Every declared frozen seed, context ID, episode ID, heldout partner family, heldout task schema, and counterfactual pair must be consumed by candidate scoring, baseline scoring, ablation scoring, leakage scanning, replay, and provenance. If any declared split, seed, context, episode, or counterfactual pair is unused, the future execution must block.

## Candidate Requirements

The future candidate must:

- use only candidate-visible observations and serialized state;
- maintain a replayable partner-relevant hidden-state representation;
- update that state from partial observations;
- expose enough state snapshot structure for replay and audit without directly encoding target labels or answer-sufficient fields;
- produce prediction/action outputs through a callable producer function;
- record producer function, input artifacts, run ID, seed, context IDs, episode IDs, aggregation rule, and code path hash.

The candidate must not:

- use partner IDs as answer keys;
- use context IDs, episode order, filenames, paths, config names, prompt text, or scoring artifacts as target shortcuts;
- depend on a second scoring or replay path unavailable to baselines;
- store final target labels in serialized state.

## Baseline Requirements

Future execution must implement and invoke independent callable baselines before candidate claims are allowed:

- `serialized_state_decoder`
- `full_bundle_decoder`
- `static_belief_table`
- `pair_count_frequency_baseline`
- `ngram_trace_lookup`
- `nearest_neighbor_trace_retrieval`
- `label_config_leakage_scanner`
- `trace_id_episode_order_leakage_scanner`
- `schema_split_leakage_scanner`
- `majority_baseline`
- `random_baseline`
- optional `oracle_upper_bound`

Every faithful non-oracle baseline must declare access rights, producer function, input artifacts, expected failure mode, sanity check or positive control where applicable, and stop condition if it ties or beats the candidate.

The optional oracle upper bound may show task solvability only. It cannot support a candidate mechanism claim.

## Ablation Requirements

Future ablations must rerun episodes under real intervention. Post-hoc score edits are invalid.

Required ablations:

- remove partner/social latent update path;
- freeze memory update;
- remove counterfactual branch;
- shuffle partner identities;
- scramble observation order;
- hold out partner families;
- hold out task schemas;
- disable replay recomputation path;
- remove active belief update while preserving observation access.

Each ablation must record run ID, seed, context ID, episode ID, producer function, aggregation rule, code path hash, intervention target, pre-intervention state hash, post-intervention state hash, and whether the intervention was actually applied.

## Leakage Scanner Requirements

Future leakage scanners must include positive controls for:

- target label leakage;
- partner ID leakage;
- context ID leakage;
- episode order leakage;
- file/path/name leakage;
- config leakage;
- schema split leakage;
- scoring artifact leakage;
- prompt/text leakage if text prompts are used.

If a positive-control leakage injection is not detected, the future execution must block. If non-control leakage is detected in candidate-visible or baseline-visible artifacts, the future execution must report negative evidence or blocked status rather than patching the run.

## Replay Requirements

Future replay must:

- recompute candidate behavior from `serialized_state + observation`;
- recompute baseline behavior from declared baseline inputs;
- reject stored-output replay;
- reject stored-action replay;
- reject trace-only comparison;
- reject hash-only replay;
- include at least one stale-cache failure-path test;
- record producer function, input artifacts, run ID, seed, context IDs, episode IDs, aggregation rule, and code path hash.

Replay success alone is not mechanism evidence. It is an auditability requirement.

## Provenance Requirements

Every future result, candidate metric, baseline metric, ablation metric, leakage result, replay result, contrast, and final verdict must record:

- producer function;
- input artifact paths;
- input artifact hashes;
- output artifact path;
- run ID;
- seed;
- train context IDs consumed;
- heldout context IDs consumed;
- counterfactual context IDs consumed;
- episode IDs consumed;
- aggregation rule;
- code path hash;
- threshold frozen before run;
- access-rights declaration for baselines;
- failure path availability.

No future metric may be specified as a literal score without a callable producer function.

## Acceptance Gate

A future execution may pass only if all of the following hold:

- branch/tag/source boundary is verified by that future task;
- all frozen seeds, context IDs, episode IDs, heldout partner families, heldout task schemas, and counterfactual pairs are consumed;
- candidate primary metric is computed by callable producer function;
- strongest faithful non-oracle baseline is below candidate under the frozen acceptance rule;
- serialized-state decoder fails below candidate;
- full-bundle decoder fails below candidate;
- static belief table fails below candidate;
- pair-count/frequency baseline fails below candidate;
- n-gram trace lookup fails below candidate;
- nearest-neighbor trace retrieval fails below candidate;
- leakage positive controls are detected;
- no non-control leakage explains candidate success;
- all required ablations rerun episodes under real intervention;
- candidate degrades under mechanism-relevant ablations;
- replay recomputes candidate and baseline behavior;
- stale-cache failure-path test fails as expected;
- provenance is complete;
- no source/harness/test path outside the future task's allowed scope is modified;
- claim ceiling remains bounded.

## Negative-Evidence Stop Conditions

Stop and report negative evidence or blocked status if:

- any faithful non-oracle baseline ties or beats candidate on the primary heldout metric;
- `serialized_state_decoder` reaches candidate-equivalent performance;
- `full_bundle_decoder` reaches candidate-equivalent performance;
- `static_belief_table` reaches candidate-equivalent performance;
- n-gram, trace, or retrieval baseline reaches candidate-equivalent performance;
- leakage positive control fails to detect injected leakage;
- replay can pass from stored outputs, stored actions, trace-only comparison, or hashes;
- any declared heldout split, counterfactual pair, frozen seed, context ID, or episode ID is unused;
- candidate score improves only through schema, config, ID, prompt, filename, path, or scoring-artifact leakage;
- ablation drop exists but faithful baselines still solve the task;
- task requires hiding fair candidate-visible information from baselines to create advantage;
- implementation starts before this card is remote-anchored and separately authorized.

## Rollback Plan

If future implementation artifacts fail validation before commit, leave them uncommitted and report exact failing files.

If unauthorized source, harness, test, 002E, Gate5, admission, bridge, runtime, or EGO-mainline changes appear, stop and report exact paths. Do not commit, amend, reset, rebase, or rewrite history without explicit authorization.

If a local tag or source boundary mismatch appears, block rather than repairing by history rewrite.

## Claim Ceiling

Future execution can claim only bounded Gate4 mechanism-proxy evidence under the exact frozen task family, if and only if all acceptance gates pass.

Future execution cannot claim:

- valid Gate4;
- social-latent inference success;
- mechanism validity;
- agency;
- selfhood;
- consciousness;
- emotion;
- autonomy;
- EGO readiness;
- runtime readiness;
- companion readiness;
- user benefit;
- correctness of Bio-CMBC, CVPSM, VCCO, CMBC, or R/G.

## Strict Non-Actions

This draft card does not authorize:

- implementation;
- environment generation;
- candidate-agent code;
- baseline code;
- leakage scanner code;
- replay code;
- pytest;
- experiments;
- 002C reruns;
- 002D reruns;
- 002E creation;
- prior artifact edits;
- Gate5/admission/bridge/runtime/EGO-mainline work;
- mechanism success claims;
- social-latent inference success claims;
- agency/selfhood/consciousness/emotion/autonomy/EGO readiness claims.
