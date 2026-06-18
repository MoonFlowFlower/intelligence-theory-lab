# Phase 1 Problem Formalization 001A

Task id: `RESEARCH-CAMPAIGN-PHASE1-PROBLEM-FORMALIZATION-001A`

Layer: engineering implementation + mechanism-hypothesis governance.

Claim ceiling: proxy formalization only. This document does not prove
self-awareness, subjective experience, real emotion, autonomy, learning success,
agency success, EGO readiness, companion readiness, or mechanism validity.

Auto-Remote-Anchor: forbidden.

## Objective

Convert broad target language into bounded proxy contracts that can later be
tested by candidate-free baselines before any mechanism search. Each proxy below
defines observables, legal inputs, forbidden leakage, metrics, baselines,
ablations, trace/replay requirements, leakage controls, stop conditions, and a
claim ceiling.

## Proxy Families

### 1. Self-Model Proxy

Question: can a system maintain and use a bounded representation of its own
state, capabilities, uncertainty, commitments, and recent action history when
choosing future actions?

Observable variables:
- serialized internal state snapshot
- prior action and intervention history
- capability/constraint state
- uncertainty over self-state
- predicted consequence of own next action

Legal inputs:
- current observation
- previous serialized state
- own prior actions and outcomes
- declared capability/constraint signals

Illegal leaked inputs:
- hidden labels for the correct action
- future observations
- evaluator verdicts or filenames
- answer keys encoded in action names or prompt text

Metrics:
- self-state prediction error
- own-action counterfactual sensitivity
- uncertainty calibration under self-state perturbation
- policy change after legal self-state update

Baselines:
- last-state lookup
- action-frequency table
- observation-only classifier
- transition-table self-state cache
- nearest-neighbor episode replay

Ablations:
- remove prior own-action history
- corrupt self-state variables
- freeze capability/constraint state
- replace self-state with observation-only state

Trace/replay:
- record serialized state before action
- record observation, legal self-state fields, action, and outcome
- replay recomputes action or score from serialized state plus observation

Leakage controls:
- label permutation
- future-observation deletion
- filename/action-name scanner
- positive-control hidden-label injection

Stop conditions:
- observation-only or lookup baseline saturates metric
- behavior changes only through leaked label fields
- replay cannot recompute from serialized state plus observation

Claim ceiling:
- bounded self-model proxy evidence only after future executable validation
- no self-awareness, subjectivity, autonomy, agency success, or EGO readiness claim

### 2. Affect / Value Regulation Proxy

Question: can a system regulate choices through bounded value, viability, or
preference state that is updated by outcomes rather than by fixed action labels?

Observable variables:
- value or viability state
- outcome valence signal
- uncertainty/confidence over value estimates
- tradeoff weights and constraints
- post-outcome update record

Legal inputs:
- current observation
- previous value state
- own prior action/outcome pairs
- bounded external feedback encoded as outcome evidence

Illegal leaked inputs:
- target action label
- evaluator preference key
- hidden reward oracle outside declared outcome channel
- sentiment text used directly as action choice

Metrics:
- value update sensitivity to outcome perturbation
- action distribution change after source deletion
- calibration of confidence under contradictory feedback
- constraint violation rate under value tradeoff

Baselines:
- fixed-priority policy
- reward lookup table
- recency-only outcome policy
- frequency-only success policy
- prompt/sentiment classifier

Ablations:
- delete supporting outcome sources
- perturb outcome valence
- freeze value state
- remove uncertainty update
- replace value state with fixed priority

Trace/replay:
- record value state before/after update
- record source outcome ids and aggregation rule
- replay recomputes updated value state and action distribution

Leakage controls:
- renamed feedback-channel positive control
- target-action text injection
- source deletion control
- irrelevant outcome deletion control

Stop conditions:
- fixed-priority or reward lookup matches candidate within equivalence band
- value update occurs without source outcome evidence
- contradiction handling flips policy from a single weak signal without admission

Claim ceiling:
- bounded affect/value regulation proxy evidence only after future executable validation
- no real emotion, desire, preference ownership, companion readiness, or user-benefit claim

### 3. Active Exploration Proxy

Question: can a system choose information-gathering actions because they reduce
decision-relevant uncertainty under the same action budget as fair baselines?

Observable variables:
- uncertainty state
- information-gain estimate
- exploration action
- downstream task success after exploration
- action cost/budget

Legal inputs:
- current observation
- previous uncertainty state
- legal transition model or learned transition state
- action budget

Illegal leaked inputs:
- hidden environment target
- oracle state key
- future observation
- evaluator-known optimal exploration route

Metrics:
- diagnostic action rate when ambiguous vs certain
- uncertainty reduction after exploration
- downstream control success after exploration
- budget-normalized information gain

Baselines:
- random exploration
- exhaustive sweep under same budget
- graph lookup / successor map
- uncertainty heuristic without learned state
- oracle-budget legal query

Ablations:
- remove information-gain term
- freeze uncertainty state
- equalize all action information estimates
- remove transition/action conditioning

Trace/replay:
- record uncertainty before action
- record candidate exploration score per legal action
- replay recomputes selected exploration action under same budget

Leakage controls:
- future-observation scanner
- hidden-target positive control
- action-name leakage scan
- heldout context usage check

Stop conditions:
- exhaustive or graph/cache baseline saturates target metric
- exploration action is selected by static route table
- candidate uses hidden target or future observation

Claim ceiling:
- bounded active-exploration proxy evidence only after future executable validation
- no autonomy, curiosity, agency success, or live initiative claim

### 4. Long-Term Update Proxy

Question: can a system update behavior across episodes or sessions from prior
experience while preserving traceable source lineage and resisting recency,
frequency, and nearest-neighbor shortcuts?

Observable variables:
- long-term memory or consolidated state
- source episode ids
- update timestamps
- retained and forgotten evidence
- behavior before and after update

Legal inputs:
- prior serialized memory state
- source episodes with own action/outcome records
- current observation
- bounded update rule

Illegal leaked inputs:
- heldout labels
- evaluator result fields
- future task distribution markers
- manual post-hoc memory edits not represented in trace

Metrics:
- source deletion effect
- counterfactual outcome perturbation effect
- transfer to heldout contexts
- catastrophic forgetting rate
- baseline non-equivalence margin

Baselines:
- nearest-neighbor episodic replay
- recency-only memory
- frequency-only memory
- summary/RAG memory baseline
- transition-table consolidation

Ablations:
- delete source episodes
- corrupt consolidated state
- freeze memory update
- remove old-context replay
- remove heldout transfer contexts

Trace/replay:
- record source episode lineage
- record memory state before/after update
- replay recomputes memory update and downstream action from serialized state

Leakage controls:
- heldout context usage scan
- source deletion positive control
- memory summary label-leak scan
- train/heldout overlap check

Stop conditions:
- recency/frequency/nearest-neighbor baseline reaches equivalence band
- source deletion has no measurable effect on claimed behavior
- replay cannot recompute memory update from sources

Claim ceiling:
- bounded long-term update proxy evidence only after future executable validation
- no robust learning, identity continuity, selfhood, companion readiness, or EGO readiness claim

### 5. Self / Environment Boundary Proxy

Question: can a system distinguish own controlled state changes from environment
changes and use that boundary in prediction, credit assignment, and action
selection?

Observable variables:
- own action channel
- environment transition observations
- boundary attribution state
- intervention record
- predicted controllable vs uncontrollable variables

Legal inputs:
- own action history
- environment observations
- intervention/outcome records
- declared controllability constraints

Illegal leaked inputs:
- hidden controllability labels
- evaluator boundary class
- future transition outcome
- action names that encode controllability

Metrics:
- controllable/uncontrollable attribution accuracy
- action-conditioned prediction improvement
- boundary perturbation action sensitivity
- false controllability rate

Baselines:
- observation-only transition table
- action-agnostic predictor
- graph lookup with hidden state key
- majority controllability baseline
- post-hoc classifier baseline

Ablations:
- remove action conditioning
- swap own-action and environment channels
- freeze boundary attribution state
- delete intervention records

Trace/replay:
- record action, observation, attribution state, and prediction
- replay recomputes boundary attribution and next action from serialized state

Leakage controls:
- controllability-label scanner
- action-name permutation
- future transition deletion
- hidden boundary positive control

Stop conditions:
- action-agnostic predictor saturates metric
- boundary labels are leaked through observation or action names
- intervention deletion does not change claimed attribution behavior

Claim ceiling:
- bounded self/environment boundary proxy evidence only after future executable validation
- no self-awareness, embodiment, subjectivity, agency success, or autonomy claim

## Phase 2 Dependency

Phase 2 may only run candidate-free baseline-first headroom tasks against a
specific proxy environment after this formalization is audited. If the strongest
fair baseline saturates a proxy surface, the correct result is no-headroom
negative evidence and reframing, not candidate mechanism search.
