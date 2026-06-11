# SAME_AGENT_BRIDGE_FAILURE_TAXONOMY_001

Task: SAME-AGENT-BRIDGE-GOVERNANCE-001-FIXA
Mode: failure taxonomy only. No implementation.

Future same-agent bridge evidence reports must label failures with this
taxonomy when applicable. Verdict must remain one of `pass`, `fail`, `blocked`,
or `inconclusive`; specific causes belong in `failure_taxonomy_labels`.

## Failure Labels

`rag_equivalent`:
The RAG summary baseline matches or beats the mechanism.

`random_equivalent`:
The random baseline matches or beats the mechanism.

`majority_equivalent`:
The majority baseline matches or beats the mechanism.

`heuristic_equivalent`:
A simple frequency, count, or hand-declared heuristic matches or beats the
mechanism.

`nearest_neighbor_equivalent`:
Nearest-neighbor trace lookup matches or beats the mechanism.

`graph_cache_equivalent`:
A graph/cache family control matches or beats the mechanism.

`transition_table_equivalent`:
The transition-table baseline matches or beats the mechanism.

`successor_map_equivalent`:
The successor-map baseline matches or beats the mechanism.

`fsm_planner_equivalent`:
The finite-state planner baseline matches or beats the mechanism.

`episodic_traversal_equivalent`:
Direct episodic traversal matches or beats the mechanism.

`observation_only_equivalent`:
Observation-only memory matches or beats the mechanism.

`no_action_conditioning_equivalent`:
Removing action-conditioned priors or prediction-error updates does not weaken
the result.

`corrupted_replay_effect_preserved`:
The claimed bridge effect survives corrupted replay order, source binding, or
prediction-error values.

`trace_not_causal`:
The result can be reported from trace, but the trace is not shown to causally
drive the decision, replay event, model delta, or policy delta.

`replay_not_used`:
Replay records exist, but the claimed improvement does not depend on replay.

`seed_overfit`:
The result depends on hand-picked or tuned seeds.

`seen_seed_only_improvement`:
The mechanism improves on seen seeds but not held-out seeds.

`no_held_out_delta`:
There is no improvement on held-out variants against the required comparison.

`schema_fragmentation`:
The task introduces incompatible schemas, missing required fields, test-only
schemas, or undocumented migrations.

`bridge_dependency_missing`:
Gate 1 works without Gate 0 action-conditioned prediction-error traces.

`same_agent_continuity_missing`:
The report relies on a shared `agent_id` string without a state lineage chain
or hash-chain-equivalent record.

`claim_ceiling_violation`:
The report claims beyond bounded same-agent Gate0-to-Gate1 bridge evidence.

`renderer_behavior_only`:
