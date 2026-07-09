# ITL-K0-H0-H1-INSTRUMENT-001A

Status: H0 BLOCKED UNTIL CANONICAL ROUTE READS READY_TO_IMPLEMENT FOR H0 /
H1 BLOCKED UNTIL H0 BANKED / NO FORMAL K0 RUN

Auto-Remote-Anchor: forbidden

## Task identity and pins

- Task id: `ITL-K0-H0-H1-INSTRUMENT-001A`
- Parent: `K0-DUAL-TRACK-SUPERSESSION-001A`
- Parent commit: `4e4700ca6e00b1a0e2dc3adf6a6e473b2f6ef6be`
- Parent card: `docs/codex/tasks/K0-DUAL-TRACK-SUPERSESSION-001A.md`
- Drafting base: branch `codex/meta-theory-scaffold`, parent commit above,
  clean before child drafting.
- H0 and H1 are phases of one instrument card, not one mutable phase. H0 is an
  immutable semantic contract. H1 implements that contract. Any semantic H1
  change requires a new H0 version/addendum banked before the changed code.

## Problem definition

K0 needs a candidate-independent test instrument with usable headroom, access
parity, independent sensitivity controls, sealed heldout inputs, and
component-scoped verdict mapping. The old pattern either tuned a harness around
the candidate or let one saturated comparator erase every component result.

H0 freezes what the instrument means. H1 later makes every generator, control,
baseline, scanner, replay path, dependency resolver, metric, and report callable.
K0-R may be built after H0 is banked, but it cannot affect H0 and cannot receive
formal interpretation before H1 acceptance plus immutable freeze.

## Layer

Engineering implementation + mechanism-hypothesis instrument design. H0 is
preregistration/evidence governance; H1 is isolated instrument implementation.
Neither is EGO runtime or subject/agency validation.

## Mainline, enabled state, and real trigger

- Mainline integration: none; ITL remains offline.
- Enabled: card banking only. H0 stays disabled until a separate canonical ITL
  `READY_TO_IMPLEMENT` transition pins the child-card commits and names H0.
  H1 stays disabled until a committed H0 acceptance readback passes. Formal
  scoring remains disabled.
- Real H0 trigger: exact-path artifact generation plus hash/readback from a
  callable contract-freeze utility or independently recomputed hashes.
- Real H1 trigger: explicit local CLI over dev/calibration inputs only.
- No network, API keys, LLM, UI, scheduler, deployment, or Ego working-tree
  import is permitted.

## Hypothesis

A three-family, non-query instrument with a frozen finite panel and independent
positive/negative controls can distinguish at least some of model, online,
replay, memory-use, transfer, and panel-relative specialness without conflating
their verdicts.

Falsifier: independent controls fail, legal observation/lookup paths saturate all
positive families, access differs across arms, heldout inputs are exposed before
freeze, or component failure propagation cannot be recomputed from the frozen
matrix.

Evidence still insufficient: an oracle gap, a K0-R learning curve, a replay hash,
or a candidate win on one seed is not instrument validity or component evidence.

## Frozen K0 task families (H0)

All families are program-generated distributions, not three hand-authored
episodes. `family_id`, split, sequence position, latent rule, and answer labels
are evaluator-only and forbidden adapter/kernel inputs.

### A — delayed consequence and source reliability

Current observation is ambiguous. Earlier legal transitions identify which of
several sources predicts delayed action outcomes. Actions affect typed outcomes;
useful prediction requires historical source/outcome evidence. The generator
varies source reliability, delay, action/outcome map, distractors, and regime
change within H0-frozen ranges.

### B — heldout factor composition

Training exposes factors and partial combinations; heldout episodes contain
unseen legal combinations. A transition/outcome model may compose factor effects.
Exact episode/tuple lookup must fail on novel combinations, while a legal ideal
model retains solvability. Generator factors, train/heldout exclusion rules, and
novelty checks are frozen in H0.

### C — two-step controllable consequence

Typed task actions change an intermediate state and a horizon-2 downstream
outcome. Current observations do not expose the transition table, but legal
action/outcome experience does. This family varies shared dynamics factors,
costs, distractors, and delayed payoff under frozen ranges. Actions are ordinary
task actions, not information-query actions; no belief-space planner is needed.
Retention/transfer metrics are forbidden inside C and come only from the
separate persistent-sequence protocol.

Active query, query-result branching, epistemic value, and belief-space planning
are explicitly deferred beyond K0. Their absence is not a K0 failure.

## H0 immutable contract

H0 must bank and hash at least:

```text
artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h0/
  h0_contract.json
  task_family_manifest.json
  generator_distribution.json
  adapter_capability_manifest.json
  access_budget_manifest.json
  metric_mde_contract.json
  baseline_panel.json
  component_control_mapping.json
  component_dependency_matrix.json
  protocol_manifest.json
  positive_control_manifest.json
  heldout_preimage_schema.json
  heldout_seal_manifest.json
  own_rule_constructor_contract.json
  public_dev_fixture_manifest.json
  smoke_contract.json
  h0_acceptance.json
  claim_ceiling.txt
```

The contract freezes:

- family distributions and parameter ranges, not candidate-chosen instances;
- train/dev/calibration/heldout split rules and disjointness checks;
- storage, history, compute, parameter, replay, and query budgets (query budget
  is zero in K0);
- adapter readable/writable fields and forbidden capabilities;
- metrics, aggregation, uncertainty method, MDE/power rule, equivalence band,
  missing-data rule, and component mapping;
- finite baseline categories and finite rival panel; adding a post-result rival
  changes the panel version, not the completed run;
- parent two-axis verdict schema and integrity dependency matrix;
- fresh-init and persistent-sequence protocols;
- independent control fixtures and expected detector directions;
- a commit-reveal heldout scheme with canonical UTF-8 JSON preimage
  `{schema_version, generator_distribution_hash, seed_records, nonce_hex}`;
  keys are lexicographically sorted with compact separators and no trailing
  whitespace; `nonce_hex` is 32 OS-random bytes; commitment is SHA-256 over the
  exact UTF-8 bytes. Custodian is the operator. The sole pre-reveal copy is
  `C:/Users/LEO/AppData/Local/EGO_K0_SEALED/ITL-K0-H0-H1-INSTRUMENT-001A/heldout_preimage.json`,
  outside both repos. H0 stores only schema, commitment, byte length, custodian,
  custody path, and generator hash. After immutable freeze, Formal copies the
  exact preimage to `heldout_reveal.json` and a callable verifier emits
  `heldout_commitment_verification.json`. K0-R/H1 development cannot read it.
- a deterministic candidate-own-rule amortized-control constructor contract:
  frozen callable interface, legal inputs, access/budget limits, training split,
  output schema, aggregation mapping, and constructor code hash. K0 freeze may
  fill only the instantiated artifact hash; candidate behavior cannot change the
  constructor semantics or panel membership.

No frozen seed/context/counterfactual pair may be decorative. Formal execution
must fail if any declared input is unused.

## Adapter parity contract

Candidate, control, and rival arms receive the same typed observation, legal
action set, feedback timing, history/storage allowance, and compute budget unless
H0 explicitly records a matched ablation. The adapter never exposes family id,
split, sequence order, hidden rule, label, oracle state, or future outcome.

The adapter may invoke only the frozen kernel ABI. It cannot call Ego source,
change kernel state, execute candidate actions outside the environment, or
provide a hidden actuator unavailable to comparators.

## Frozen panels

### Control panel (causal or shortcut explanations)

- random, majority, and observation-only;
- recency/summary/RAG-equivalent legal-history lookup;
- nearest-neighbor and exact lookup;
- mandatory graph/cache family: `graph_lookup`, `transition_table`,
  `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`;
- no-update, shuffled-outcome, predictor checkpoint swap, planner bypass;
- replay-off and corrupted replay;
- memory-read-off/zero, source deletion, history replacement;
- from-scratch, checkpoint-only, replay-reset, and memory-reset carriers;
- candidate-own-rule batched/amortized control instantiated after K0 freeze only
  by the H0-frozen deterministic constructor; only its artifact hash is filled.

Controls map only to their preregistered component propositions. A replay-off
tie cannot erase online learning; a batched-own-rule tie cannot erase learned
model existence.

### Rival panel (comparative qualifier only)

H0 must instantiate a finite, budget-matched panel from declared categories,
including a tabular/transition learner, an online compositional learner, and a
drift-aware replay learner where applicable. Rival results populate only
`comparison_state`, except `V_special`, whose proposition is explicitly
relative to that frozen panel.

## Independent instrument controls

K0-R is the object under test and cannot be the sole positive control. H1 must
implement independently:

1. an artificial updater, not sharing K0 model/update code, that recovers a
   synthetic transition available only through legal online feedback;
2. a matched no-update arm that fails that fixture;
3. an injected label/answer side channel that the real scanner detects;
4. an observation-decodable negative-control family where O-only saturates;
5. a no-signal family where candidate-independent arms remain at chance;
6. replay corruption that the recomputing validator rejects;
7. an ablation-identity positive control that fails if intervention and full arm
   are identical when they should differ.

Each control maps to explicit components. A failed control invalidates only its
mapped dependency unless it is a global provenance/access/leakage control.

## Protocols

Fresh-init resets checkpoint, optimizer, memory, replay buffer, kernel/RNG state,
and history for every family. It tests architecture reuse, not transfer.

Persistent-sequence retains full state through H0-frozen orders and limited
permutations. Minimum carriers: full carryover, full fresh-init,
checkpoint-only, replay-reset, and memory-reset. Report forward transfer,
retention/backward transfer, interference/forgetting, order sensitivity, and
memory/buffer/compute growth.

## H1 implementation target

After H0 is banked and its hash is read back, H1 may create only:

```text
src/itl_k0_h0_h1_instrument_001a/__init__.py
src/itl_k0_h0_h1_instrument_001a/contracts.py
src/itl_k0_h0_h1_instrument_001a/generators.py
src/itl_k0_h0_h1_instrument_001a/adapters.py
src/itl_k0_h0_h1_instrument_001a/controls.py
src/itl_k0_h0_h1_instrument_001a/baselines.py
src/itl_k0_h0_h1_instrument_001a/rivals.py
src/itl_k0_h0_h1_instrument_001a/leakage.py
src/itl_k0_h0_h1_instrument_001a/replay.py
src/itl_k0_h0_h1_instrument_001a/metrics.py
src/itl_k0_h0_h1_instrument_001a/resolver.py
src/itl_k0_h0_h1_instrument_001a/artifacts.py
src/itl_k0_h0_h1_instrument_001a/cli.py
tests/itl_k0_h0_h1_instrument_001a/test_contracts.py
tests/itl_k0_h0_h1_instrument_001a/test_controls.py
tests/itl_k0_h0_h1_instrument_001a/test_access_leakage.py
tests/itl_k0_h0_h1_instrument_001a/test_replay.py
tests/itl_k0_h0_h1_instrument_001a/test_resolver.py
tests/itl_k0_h0_h1_instrument_001a/test_cli.py
```

H1 must provide independent callable generators, adapters, controls, baselines,
rivals, scanners, replay recomputation, metric aggregation, power/headroom
calculation, component dependency resolution, and artifact production. Static
verdict dictionaries, literal pass reports, and test-only logic paths are
forbidden.

H1 acceptance artifacts include:

```text
instrument_validation.json
positive_control_report.json
negative_control_report.json
access_parity_report.json
leakage_report.json
replay_report.json
computed_evidence_provenance.json
failure_manifest.json  # whenever any gate fails
h1_acceptance.json
```

## Strongest baseline and invalidity risk

The strongest explanation is a legal history learner or graph/transition table
under equal access. The strongest invalidity risk is candidate-driven harness
tuning or a hidden adapter field/actuator. H0 ancestry, heldout sealing,
capability manifests, real leakage positive controls, and a frozen finite panel
are load-bearing.

## Collision record

### 1. Candidate-shaped harness
- Evidence: likely K0-R sensitivity.
- Cheap match: tune fixtures to K0 inductive bias.
- Leak risk: high.
- Falsifier: independent updater/no-update pair does not produce expected split.
- Failure: self-validating instrument.

### 2. Lookup-friendly delayed task
- Evidence: high scores and replay.
- Cheap match: transition table/episodic traversal.
- Leak risk: observation/history decodability.
- Falsifier: graph/cache family saturates heldout.
- Failure: valid saturation, component claim blocked, route not globally erased.

### 3. Frozen three-family instrument (selected)
- Evidence: headroom/sensitivity by family plus component-scoped failures.
- Cheap match: full frozen control panel and finite rivals.
- Leak risk: cross-family ids, heldout exposure, access asymmetry.
- Falsifier: any independent integrity control fails.
- Failure: `INVALID_INSTRUMENT` only for dependent components.

## Ablation and trace/replay requirement

Ablations rerun episodes with real interventions. Replay reconstructs candidate,
control, and rival actions from serialized state plus observation and may not
compare stored hashes alone. Trace includes inputs, legal actions, predictions,
candidate ranking, selected action, outcome, prediction error, update delta,
memory/replay refs, ablation id, adapter capability hash, seed context, and
state/checkpoint hashes.

## Computed-evidence provenance gate

Every H1 metric/report records producer function, input artifact hashes, run id,
seed/context/episode ids, aggregation rule, code-path hash, and H0 contract hash.
Tests must prove producer/baseline/ablation/scanner/replay/dependency-resolver
invocation and their failure paths.

## Acceptance gates

### H0 bank

Accept H0 only if every listed contract exists, parses, hashes, is internally
consistent, contains the complete two-axis/dependency semantics, seals heldout
inputs, and predates K0-R access to task semantics beyond the public contract.
H0 is produced/verified by the exact callable paths
`src/itl_k0_h0_h1_instrument_001a/h0_freeze.py` and
`tests/itl_k0_h0_h1_instrument_001a/test_h0_freeze.py` after the canonical READY
transition. `h0_acceptance.json` must contain task/card-bank commit, status
`h0_contract_banked_valid`, every contract/artifact hash, heldout commitment,
public-dev fixture/smoke hashes, producer function, input hashes, run id,
aggregation rule, and code-path hash. A hand-written acceptance is invalid.
H0 banking authorizes H1 implementation and K0-R reference implementation only
when their own prerequisite cards also pass; it authorizes no formal claim.

### H1

Accept H1 only if all independent controls fire in their declared directions,
access parity and leakage scans pass, replay corruption is rejected, every
frozen dev/calibration input is consumed, and outputs come from callable paths.
H1 may report valid saturation or invalid components; it must not tune around
them. H1 acceptance still authorizes no formal run until immutable freeze.
`h1_acceptance.json` must be callable and record exact H0 acceptance/card-bank
commits, H1 source/test hashes, every validation artifact hash, status
`h1_instrument_accepted`, producer/input/run/aggregation/code hashes, and the
bundle input manifest later consumed by Freeze.

## Claim ceiling

- H0: immutable instrument/preregistration contract only.
- H1: bounded instrument sensitivity, access-parity, leakage, replay, and
  headroom diagnostics on dev/calibration controls only.
- Neither proves any K0 component, mechanism validity, transfer, initiative,
  agency, autonomy, subjectivity, consciousness, functional subject, electronic
  life, EGO readiness, product benefit, or mainline effect.

## Stop conditions

Stop and preserve a failure manifest if H0 semantics change after candidate
inspection; heldout is unsealed early; generator provenance is unknown; access
parity fails; a positive control fails; a label/family id leaks; any frozen input
is unused; a literal verdict or second logic path appears; or scope requires EGO
runtime, LLM, UI, network, or external services.

## Rollback plan

Before H0 bank, remove only new H0 paths. After H0 bank, never rewrite it; create
an additive version/addendum and invalidate dependent builds. H1 bug fixes that
preserve semantics may use a new code hash; semantic fixes require new H0. Keep
all negative/invalid artifacts append-only.

## Expected changed files

Card landing only:

- `docs/codex/tasks/ITL-K0-H0-H1-INSTRUMENT-001A.md`

H0 execution only:

- `src/itl_k0_h0_h1_instrument_001a/__init__.py`
- `src/itl_k0_h0_h1_instrument_001a/h0_freeze.py`
- `tests/itl_k0_h0_h1_instrument_001a/test_h0_freeze.py`
- the exact H0 files enumerated in `H0 immutable contract`; no other
  H0 artifact filename is allowed

H1 only after H0:

- the exact source and test files enumerated in `H1 implementation target`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/instrument_validation.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/positive_control_report.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/negative_control_report.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/access_parity_report.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/leakage_report.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/replay_report.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/computed_evidence_provenance.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/h1_acceptance.json`
- `artifacts/ITL-K0-H0-H1-INSTRUMENT-001A/h1/failure_manifest.json` when needed

Forbidden: EGO repos/working trees, prior artifacts/cards, global schema
rewrites, route claims outside a separately authorized transition, formal K0
execution, threshold rescue, push, tag, or remote anchor.

## Local commit authorization

Exact-path local commits are authorized separately for (1) card bank, (2) H0
bank, and (3) H1 implementation/evidence after their gates. This user-authorized
landing turn may bank the card only. Remote publication remains forbidden.

## Next minimal action

After this card and the Ego Foundation card are banked and route readback permits
the first pair, execute the H0 contract bank in parallel with Foundation. Do not
start H1, K0-R, freeze, or formal evidence early.

## What this does not prove

This card is a specification. It does not establish instrument headroom,
learning, replay benefit, memory causality, transfer, specialness, or life-like
function.
