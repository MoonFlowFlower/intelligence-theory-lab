# NEXT-MECHANISM-SURFACE-ROUTE-DECISION-001A

## 1. Status Report

Verdict: `next_mechanism_surface_route_decision_001a_pass`

Current layer: `route-governance / post-ACSB-downgrade mechanism-surface admissibility review`.

Mainline integration status: none.

Enabled status: none.

Real trigger evidence:

- Canonical ACSB downgrade boundary:
  `PRESERVE-ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A`.
- Boundary verdict:
  `preserve_acsb_current_route_downgrade_closure_001a_pass`.
- Boundary commit:
  `a70b4262b04feaccf51e997fa8d0583d20b1af6e`.
- Boundary tag:
  `remote-anchor-acsb-current-route-downgrade-closure-001a-a70b426`.
- Preserved invalid-harness blocker:
  `claude_independent_acsb_001d_execution_001a_audit_blocks_feature_impoverished_or_unfair_baseline`.

This record performs route selection only. It does not implement a harness,
create a candidate, create ACSB `001E`, start an ACSB replacement preflight, or
authorize runtime, bridge, Gate, admission, companion, product, LLM/RAG, or
EGO-mainline work.

## 2. Canonical Start-State Readback

Producer commands:

- `git branch --show-current`
- `git rev-parse HEAD`
- `git status --porcelain=v1`
- `git rev-list --left-right --count "HEAD...@{u}"`
- `git rev-parse refs/tags/remote-anchor-acsb-current-route-downgrade-closure-001a-a70b426`
- `git ls-remote origin refs/heads/codex/meta-theory-scaffold`
- `git ls-remote origin refs/tags/remote-anchor-acsb-current-route-downgrade-closure-001a-a70b426`
- `git tag -l remote-anchor-acsb-current-route-downgrade-closure-001a-a70b426 --format='%(objecttype)'`

Readback:

| Field | Required | Observed | Status |
| --- | --- | --- | --- |
| current branch | `codex/meta-theory-scaffold` | `codex/meta-theory-scaffold` | match |
| local HEAD | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | match |
| remote branch | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | match |
| local tag | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | match |
| remote tag | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | `a70b4262b04feaccf51e997fa8d0583d20b1af6e` | match |
| ahead/behind | `0 0` | `0 0` | match |
| worktree/index | clean | clean | match |
| tag type | `commit` | `commit` | match |

Start-state gate result: passed.

## 3. Preserved ACSB Downgrade Constraints

The route decision preserves these constraints:

1. Current ACSB route is downgraded and sealed as an active route.
2. This is not a claim that ACSB is false.
3. ACSB was not validly tested by `001D`.
4. ACSB remains unknown, not proven false.
5. `fe5aa85` is not accepted as ACSB negative evidence.
6. `fe5aa85` may be cited only as invalid-harness blocker evidence.
7. `001B`, `001C`, and `001D` are invalid-harness / evidence-hygiene lessons,
   not mechanism-negative evidence.
8. No ACSB `001E` is created or authorized.
9. No non-`001E` ACSB replacement preflight is authorized.
10. No Claude implementation of an ACSB replacement is authorized.

## 4. Problem Definition

The ACSB current route was downgraded because repeated executions collapsed into
invalid-harness and evidence-surface failure modes: oracle or legal-observation
shortcut, lookup/static decoder behavior, fake learner or no real train
consumption, inert boundary memory, capacity-disabled inertness, provenance
that proved callable execution without proving non-oracle semantics, and tests
that asserted artifact conclusions rather than discriminative failure paths.

The real objective is to select, block, or freeze the next mechanism-surface
direction without repairing ACSB, creating a replacement harness, or converting
invalid-harness lessons into stronger evidence.

## 5. Route Candidates

### Route A: ACP-BV

Name: `ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY`.

Layer: mechanism-surface hypothesis / future executable surface candidate.

Hypothesis: a bounded agent with usable self-boundary / viability state should
show future prediction and behavior differences that depend causally on
history-derived internal boundary/viability state, not only same-step legal
observation.

Route role in this decision: selected for future task-card drafting only.
Implementation remains unauthorized.

### Route B: World-Model-Only Causal Intervention Surface

Layer: engineering / learning-adaptation substrate surface.

Hypothesis: before any boundary proxy claim, action-conditioned predictive
world-model learning should survive causal intervention, transfer, and replay
recomputation.

Route role in this decision: mandatory substrate baseline and fallback. If
Route A cannot specify or later satisfy boundary-memory causal-dependence gates,
the route should downgrade to Route B.

### Route C: Social / ACSB Re-Entry Family

Layer: frozen contrast only.

Status: not authorized for implementation by this boundary.

Route role in this decision: contrast class explaining why immediate social /
ACSB re-entry is lower-yield after repeated oracle, lookup, and inert-boundary
collapse.

## 6. Route Comparison Matrix

| Criterion | Route A: ACP-BV | Route B: World-model-only | Route C: Social / ACSB re-entry |
| --- | --- | --- | --- |
| Current authorization | future task-card drafting only | fallback / baseline only | frozen contrast only |
| Mainline target | none | none | none |
| Implementation authorized | no | no | no |
| ACSB re-entry authorized | no | no | no |
| Target non-oracle specifiable | yes: future outcome depends on history, action, intervention, and latent boundary/viability state | yes: future transition target can be intervention-conditioned without boundary variables | no under this boundary; immediate re-entry is blocked |
| Target-generator isolation specifiable | yes: target generator must be unreachable from candidate/reference/baseline/replay/evaluator model paths | yes: target generator isolation is simpler because no boundary channel is exposed | no implementation surface is admitted |
| Train-consumption gate specifiable | yes: no-boundary learner, empty-train, and label-shuffle controls are required | yes: model learners must degrade or block under empty-train / label-shuffle controls | no |
| Boundary-state causal gate specifiable | yes: serialized boundary / viability memory mutation and persistence-disabled controls must change pre-registered behavior or block | not a boundary route; cannot support a boundary-proxy claim | blocked |
| Fair strongest baseline | no-boundary recurrent learner, world-model-only learner, no-memory sequence learner, fitted no-boundary MLP/RNN/transformer-like baseline, simple causal transition learner | model-free policy learner, recurrent predictor, non-causal sequence learner, lookup / transition table control, frozen representation baseline | ACSB historical failure family only |
| Replay recomputation | must recompute from serialized memory plus history/observation, and fail under mismatched or mutated state when behavior should differ | must recompute from serialized world model state plus history/observation | no new replay authorized |
| Collapse risk | viability may reduce to reward shaping, or memory may become a hidden lookup table | can become ordinary model-based control with no boundary claim | repeats the ACSB evidence-surface collapse |
| Decision | select for future task-card drafting only, with hard downgrade to Route B on failed admissibility | not selected as primary, but required as substrate baseline/fallback | blocked |

## 7. Strongest Objection Per Route

Route A strongest objection: ACP-BV may collapse into ordinary model-based
control or reward shaping. If viability is just reward, or boundary memory is
just a hidden lookup table, the surface cannot support a self-boundary /
viability proxy claim. The future task card must therefore include an explicit
objection test: compare against a world-model-only causal intervention learner,
mutate or disable boundary memory, disable persistence/capacity, and downgrade
the route if behavior is unchanged or if the strongest no-boundary baseline
matches the candidate/reference.

Route B strongest objection: world-model-only causal intervention is a lower
level substrate. It can test prediction/adaptation and causal intervention, but
it cannot by itself support self-boundary, viability, agency, subjectivity, or
EGO readiness claims. Selecting only Route B would be a theory downgrade, not a
boundary-proxy advance.

Route C strongest objection: immediate ACSB or social re-entry would ignore the
sealed downgrade lesson. The preserved record shows the chain repeatedly
collapsed into oracle, lookup, fake-learner, and inert-boundary failure modes.
Re-entry would require a separate route-decision card and materially different
surface, not another current-route repair.

## 8. Oracle / Lookup / Fake-Learner / Inert-Boundary Collapse Analysis

The preserved ACSB blocker shows the failure family to avoid:

- Same-step legal observation contained enough answer-bearing structure for
  `_target_from_observation = phase_bit XOR action_bit`.
- The reported no-boundary learner was wired to a rule path and did not prove
  train consumption.
- The reference path and capacity-disabled path shared the target-generation
  identity rather than discriminating boundary-memory use.
- Boundary memory and disable flags did not causally control scored behavior.
- Replay and tests risked confirming stored conclusions instead of recomputing
  behavior from serialized state and observation/history.

Route A is selected only because it can name admissibility gates that directly
attack this collapse family. The selection is conditional at the route level:
future drafting must make the target future/intervention/history dependent,
isolate target generation, require train-consuming independent baselines,
require boundary-memory causal dependence, and require replay recomputation
positive controls. If any of those cannot be specified, the route decision
downgrades to Route B or blocks.

## 9. Future Admissibility Gates For Selected Route

Future ACP-BV task-card drafting must enforce these gates before any harness is
implemented:

1. Target non-oracle: the target cannot be computed from same-step legal
   observation alone, or from same-step action bits plus legal observation
   alone. The target must require history, intervention, future transition, or
   latent state not exposed as answer-bearing fields.
2. Target-generator isolation: target generation must be unreachable from
   candidate, reference, baseline, decoder, replay, and evaluator-facing model
   paths. Call-graph or AST scanner positive controls must prove oracle wiring
   is caught.
3. Train consumption: at least one no-boundary learner must consume train data.
   Empty-train and label-shuffle controls must reduce learned baseline
   performance or block. Static dictionary, precomputed rule decoder, and
   literal target lookup must block.
4. Boundary-state causal dependence: reference/candidate behavior must causally
   depend on serialized boundary / viability memory. Boundary-memory mutation,
   persistence-disabled intervention, or capacity-disabled intervention must
   change pre-registered behavior on some cases or block.
5. Fair strongest baseline: the no-boundary baseline may be strong and
   train-consuming. If the strongest fair no-boundary baseline matches the
   candidate/reference, the route must downgrade rather than repair toward a
   pass-shaped artifact.
6. Replay recomputation: replay must recompute behavior from serialized state
   plus observation/history, not compare stored output hashes. Mismatched or
   mutated state must fail when behavior should differ.
7. Leakage/scanner positive controls: future validation must catch oracle
   wiring, target-generator access, same-step legal-observation shortcut,
   answer-bearing alias, fake train consumption, empty-train pass,
   label-shuffle pass, boundary-memory inertness, capacity-disabled inertness,
   path splitting, and stored-trace replay tautology.
8. Objection test: if viability reduces to reward shaping or boundary memory
   reduces to a hidden lookup table, ACP-BV must be downgraded to
   world-model-only or blocked.

## 10. Stop Conditions

This route decision would block if:

- start-state readback failed;
- worktree or index was dirty before changes;
- required tag or remote branch could not be verified;
- the route decision authorized ACSB re-entry;
- the route decision created or authorized ACSB `001E`;
- the route decision authorized implementation;
- any source, runtime, bridge, Gate, admission, companion, product, LLM/RAG, or
  EGO-mainline file was modified;
- selected route could not specify target non-oracle constraints;
- selected route could not specify fair strongest baseline;
- selected route could not specify boundary-memory causal-dependence test;
- selected route could not specify replay recomputation;
- selected route relied on same-step legal-observation target;
- produced artifacts contained unbounded mechanism or EGO-readiness claims.

Triggered stop conditions: none.

## 11. Selected Route Or Blocked Outcome

Selected route: `ACTION-CONDITIONED-PREDICTIVE-BOUNDARY-VIABILITY`.

Authorization level: future task-card drafting only.

Implementation authorized: false.

ACSB re-entry authorized: false.

ACSB `001E` authorized: false.

Replacement ACSB preflight authorized: false.

Claude implementation authorized: false.

Route B is retained as the mandatory strongest substrate baseline and fallback.
Route C is blocked as immediate re-entry.

## 12. Claim Ceiling

Maximum claim:

`bounded route recommendation / route block / surface-admissibility decision only`

This is a route-governance boundary. It does not report mechanism scores,
performance pass/fail numbers, or computed mechanism evidence.

## 13. What This Does Not Prove

This does not prove ACSB true or false in general. It does not prove a
successful mechanism, sound Gate evidence, agency, autonomy, consciousness,
emotion, subjectivity, EGO readiness, runtime readiness, companion/product
readiness, user-benefit stability, or mainline effect.

It also does not authorize ACSB repair, ACSB `001E`, a replacement ACSB
preflight, a harness, a candidate, or any runtime/mainline path.

## 14. Next Minimal Closed-Loop Action

Draft a future ACP-BV task card only. That task card must remain
implementation-forbidden unless it independently specifies the non-oracle
target, target-generator isolation, train-consumption controls, strongest fair
baselines, boundary-memory causal-dependence tests, replay recomputation tests,
leakage positive controls, stop conditions, and downgrade rule to
world-model-only.
