# SAME_AGENT_BRIDGE_BASELINES_001

Task: SAME-AGENT-BRIDGE-GOVERNANCE-001-FIXA
Mode: baseline and ablation contract only. No implementation.

Future Gate0-to-Gate1 bridge tasks must compare the mechanism against the
baselines and ablations below using the same environment seeds, held-out split,
observation/action access rules, competence checks, and reporting schema unless
a later governance fix narrows scope before implementation.

## First-Class Graph/Cache Challenger Family

Prior Gate 1 execution failed with `graph_cache_collapse`. `CausalMemoryGrid-v0`
is especially vulnerable to transition-table and successor-map collapse.
Therefore the following are mandatory first-class challenger baselines, not
optional diagnostics:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Each must receive the legal trace/environment access defined by the frozen
access contract. If any matches or beats the mechanism under the predeclared
margin, bridge verdict must be `fail` or `blocked`, and no bridge evidence claim
is allowed.

## Other Required Baselines

`random_baseline`:
Samples legal actions/predictions from the allowed output space.

`majority_baseline`:
Uses the majority action/outcome/prediction target from training traces under
the same allowed access contract.

`RAG_summary_baseline`:
Receives a text or structured summary of prior traces within the same access
budget as the mechanism. It must not be weakened by denying information that
the mechanism effectively receives.

`nearest_neighbor_trace_baseline`:
Selects decisions or predictions by nearest trace similarity using declared
features only. It detects lookup equivalence.

`frequency_heuristic_baseline`:
Uses action/outcome frequencies and simple count rules. It detects whether the
environment is solvable without the claimed mechanism.

`observation_only_memory_baseline`:
Uses observation history without action-conditioned prediction-error traces.
It detects whether action-conditioning is unnecessary.

`no_action_conditioning_baseline`:
Uses the same observations and memory writes but removes action-conditioned
priors or action-specific prediction-error updates.

`same_agent_no_replay_baseline`:
Runs the same agent lineage without Gate 1 replay/consolidation.

`corrupted_replay_ablation`:
Preserves replay volume but corrupts replay order, source bindings, or
prediction-error values according to frozen rules.

`oracle_leak_scan`:
Searches for hidden labels, future observations, seed identity leakage,
filename leakage, renderer leakage, fixture leakage, action-name leakage, and
test-only paths.

## Required Cross-Gate Ablations

Every bridge execution must include:

- remove Gate 0 trace
- remove prediction-error trace
- corrupt replay order
- replace trace with observation-only memory
- replace trace with RAG summary
- compare against same-agent no-replay version

## Baseline Parity, Competence, and Strawman Protection

Baselines must receive comparable legal inputs. The mechanism may not use
private labels, future observations, hidden environment IDs, post-hoc selected
replay items, or runtime objects that baselines cannot access under their
declared role.

Every first-class baseline must have a competence check. A failed or sandbagged
baseline invalidates the comparison; it does not become candidate evidence.

Strawman protection:

- no intentionally weak baseline implementation
- no weaker tuning budget for controls
- no weaker compute budget for controls unless frozen and justified
- no disabling graph/cache controls by environment construction
- no redefining a matching baseline as a diagnostic after results

If a baseline matches or beats the mechanism under the predeclared comparison
rule, the verdict must report baseline equivalence instead of patching the
mechanism.

## Stop Conditions

Stop and report `fail` or `blocked` if:

- any graph/cache family baseline matches or beats the mechanism
- RAG summary baseline matches or beats the mechanism
- random or majority baseline matches or beats the mechanism
- frequency heuristic baseline matches or beats the mechanism
- nearest-neighbor trace baseline matches or beats the mechanism
- observation-only memory matches the mechanism
- no-action-conditioning matches the mechanism
- no-replay version matches the mechanism
- corrupted replay preserves the claimed effect
- oracle/leak scan is suspicious or positive
- threshold selection depends on observed results
- baseline competence checks are missing or failed

## What This Baseline Contract Does Not Prove

Passing these baselines would support only bounded same-agent bridge evidence
under the specified trace/replay contract. It would not prove consciousness,
subjective experience, real emotion, agency, stable autonomy, functional
subject success, companion readiness, or EGO mainline readiness.
