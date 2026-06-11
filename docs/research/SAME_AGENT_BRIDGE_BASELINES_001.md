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

Every first-class baseline must have a comp