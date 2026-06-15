# ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D

Draft status: revised by `ACSB-001D-CARD-MINOR-REVISION-R1-R5-001A`.

This is a revised task-card draft for delta hostile re-audit. It is not an
implementation authorization.

## Verdict

`draft_revised_for_delta_reaudit_r1_r5_001d`

Codex execution of 001D implementation remains unauthorized until a separate
delta hostile re-audit clears the R1 capacity-disabled-reference repair and the
R5 canonical-anchor reconciliation, followed by an explicit implementation
authorization.

## Status

- Current layer: `engineering-governance / 001D task-card draft only`
- Mainline integration status: `none`
- Enabled status: `none`
- Real trigger evidence: preserved card-level hostile audit
  `CLAUDE-INDEPENDENT-ACSB-001D-CARD-LEVEL-HOSTILE-AUDIT-001A` states that the
  uploaded 001D draft mostly closes the known ACSB collapse modes but fails
  approval criterion #5 because the fair capacity-disabled reference remains
  riggable under prose-only wording.
- Claim ceiling: `revised task-card draft only`
- Auto-Remote-Anchor for this draft-revision task: `conditional`
- Auto-Remote-Anchor for future 001D execution: `forbidden unless a later
  implementation task card explicitly authorizes it`

## Canonical Input Boundary

This draft uses only current repo readback, current artifacts, the current
handoff, and the preserved audit artifacts as canonical state. Memory is not a
canonical source for commit hashes, tags, branch state, gate status, artifact
paths, verdicts, or route status.

Latest preserved boundary:

- Boundary:
  `PRESERVE-AND-REMOTE-ANCHOR-CLAUDE-INDEPENDENT-ACSB-001D-CARD-LEVEL-HOSTILE-AUDIT-001A`
- Verdict:
  `remote_anchor_preserve_claude_independent_acsb_001d_card_level_audit_001a_requires_minor_revision`
- Commit: `1fe086fdc3d86ffd7bb61f167b469715083ff65f`
- Tag:
  `remote-anchor-claude-independent-acsb-001d-card-level-audit-001a-1fe086f`
- Branch: `codex/meta-theory-scaffold`
- Current readback for this revision: local HEAD = remote branch = local tag =
  remote tag = `1fe086fdc3d86ffd7bb61f167b469715083ff65f`
- Ahead/behind: `0 0`
- Start status: clean
- Claim ceiling of parent boundary: `card_level_audit_preservation_only`

The audited card source was an uploaded draft and was not present at
`docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D.md`
before this revision. This repo document is therefore the revised draft record
for re-audit; it does not claim byte-level preservation of the uploaded draft.

## R5 Canonical Anchor Reconciliation

The route-decision anchor named by the uploaded card is:

- Commit: `fb0129aebe760d25bf4051328cdbf9ed14095694`
- Tag: `remote-anchor-acsb-post-001c-route-decision-001a-fb0129a`

Current readback verifies `fb0129a` from `origin_remote_branch_or_tag` via the
remote tag's peeled commit. The local mount also currently contains the commit
object and local annotated tag, but the preserved audit caveat remains part of
the history: in the audit session, the mount `.git/index` was corrupted and the
route-decision commit was only plausibly available through the `/tmp` clone and
origin workflow. This revision preserves that caveat and makes the start-state
gate source-classified rather than mount-only.

Machine-readable field required in future 001D artifacts:

`canonical_anchor_verification_source`

Allowed values:

- `mount_local_repo`
- `origin_remote_branch_or_tag`
- `tmp_clone_from_origin`
- `handoff_only_degraded`
- `unverified_blocked`

Canonical source hierarchy for future 001D:

1. Direct repo readback from the current worktree if `.git` is healthy.
2. Clean temporary clone from `origin`.
3. Current handoff only if origin cannot be reached, with explicit degraded
   claim and no execution unless the user explicitly authorizes degraded
   local-only drafting.

Corrupted-mount handling:

- If mount `.git/index` is corrupted, do not use the dirty mount worktree as
  canonical.
- Build from a clean temporary clone or committed object snapshot.
- Never copy a dirty worktree wholesale into a clean clone.
- Record any divergence excluded from commit.

Acceptance gate #1 is revised to:

> Start-state readback must verify the canonical route-decision boundary from
> the local repo, origin/tmp clone, or current handoff with explicit source
> classification. If only handoff verification is available, execution must
> block unless the user explicitly authorizes degraded local-only drafting.

Stop condition:

- If `fb0129a` or the latest route-decision boundary cannot be verified by any
  allowed source, block with
  `blocked_by_unverified_route_decision_anchor_001d`.

## Bounded Audit Before Any Implementation

- Real objective: define one final corrected ACSB executable challenge contract
  that can fail cleanly against known 001B/001C collapse families.
- Problem definition check: the problem is not missing code. The current
  blocker is that a future implementer could still write a separate
  capacity-disabled formula that is reverse-engineered to fail and label it
  "fair."
- Strongest baseline explanation: a static observation decoder, value-signature
  decoder, lookup/cache family, fitted no-boundary learner, or rigged
  capacity-disabled line can explain apparent ACSB separation without operative
  self-boundary persistence.
- Strongest invalidity reason: the task may again encode the answer in legal
  observations or in a decoy-selecting capacity path, producing a false positive
  margin.
- Falsifies this framing: a callable, source-pinned implementation where the
  same reference core under explicit disable flags is the only capacity-disabled
  path, and where strongest legal baselines/decoders collapse any leaked or
  static solution.
- Insufficient evidence: a clean task card, clean JSON, source existence,
  scanner-clean report, static verdict field, or test that only asserts pass.
- Mechanism versus resemblance: future 001D tests bounded offline
  discriminative surface evidence only. It does not prove mechanism validity.
  It does not prove subjectivity.
- Hard-coding check: block if reference, baseline, ablation, or replay behavior
  branches on evaluator-only targets, row IDs, split labels, hidden answer
  aliases, or fixed failure tokens.
- Local optimum check: block if success depends on threshold tuning after seeing
  results or on removing the strongest challenger.
- Zeno check: this is a terminal ACSB challenge card. Any failed kill-switch or
  matched strong baseline closes/downgrades ACSB; no `001E` ACSB repair loop.
- Evidence leakage check: legal observations, serialized state, action names,
  filenames, fixture names, and context IDs must be scanned for value-level and
  identity-level leakage with positive controls.
- Schema split check: train/heldout non-overlap must be computed without split
  label in the key; heldout row-enumerability is a callable blocking check.
- Second logic path check: tests must fail if implementation uses a separate
  decision rule only for capacity-disabled reference, baselines, ablations, or
  replay.
- Replay weakness check: replay recomputes from serialized state plus
  observation; stored hashes, verdicts, labels, or report fields are not replay.
- Claim inflation check: even a clean future run supports only bounded offline
  ACSB discrimination evidence under this contract.
- Minimal validation: delta hostile re-audit scoped to R1 and R5 before any
  implementation.
- Stop condition: block if R1 same-callable-family constraints or R5 canonical
  source classification cannot be satisfied.
- Rollback plan: revert this draft and artifacts if forbidden files change, if
  implementation paths are introduced, or if the card authorizes execution
  before re-audit.
- Acceptance signal: the revised card is ready for delta hostile re-audit
  scoped to R1 and R5.

## Bounded Task Card

- Task id: `ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D`
- Problem definition: create a future executable ACSB challenge that is
  terminal, fail-able, and structurally resistant to the known 001B/001C
  collapse modes, especially rigged capacity-disabled references.
- Current stage/layer: engineering-governance / task-card draft only.
- Mainline target: none.
- Enabled-state requirement: no Gate4/Gate5, bridge, tournament, runtime,
  companion, product, EGO-mainline, or production path may be enabled.
- Real-trigger evidence requirement: preserved audit
  `CLAUDE-INDEPENDENT-ACSB-001D-CARD-LEVEL-HOSTILE-AUDIT-001A` plus
  source-classified route-decision anchor readback.
- Hypothesis: a final corrected ACSB challenge can produce bounded offline
  discriminative evidence only if apparent success is measured against the
  strongest legal no-boundary, lookup/cache, static-decoder, learned, and
  capacity-disabled challenger families.
- Strongest baseline: maximum score over legal observation-only/value-signature
  decoders, graph/cache/transition/FSM/count-table/episodic traversal baselines,
  fitted no-boundary learners with feature parity, and same-callable-family
  persistence-disabled reference.
- Ablation requirement: future execution must rerun episodes under real
  interventions, including `disable_persistence`, freeze/reset boundary update,
  remove action-conditioned contingency, remove no-action counterfactual,
  shuffle action-effect linkage while preserving marginals, and replace
  boundary state with recency state.
- Trace/replay requirement: future replay must recompute behavior from
  serialized state plus observation and intervention description; it must not
  compare stored hashes or verdict fields.
- Computed-evidence provenance gate: every score must record producer function,
  input artifacts, run ID, seed/context/episode IDs, aggregation rule, code path
  hash, model class where applicable, update counts where applicable, baseline
  path, ablation path, leakage scanner path, and replay path.
- Acceptance gate: future implementation may be authorized only after delta
  hostile re-audit confirms R1 and R5 and a separate instruction explicitly
  authorizes implementation.
- Claim ceiling: bounded offline ACSB task-card / future challenge contract
  only.
- Stop condition: any kill-switch match, leakage positive-control failure,
  same-callable-family violation, capacity ablation path split, unverified
  route-decision anchor, replay/provenance failure, or no-`001E` violation
  blocks or closes ACSB.
- Rollback plan: if future implementation touches unauthorized files, weakens
  baselines, removes kill-switches, tunes thresholds post hoc, or creates a
  second logic path, revert the future implementation and preserve the failure.
- Expected changed files for this revision:
  `docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D.md`
  and
  `artifacts/acsb_001d_card_minor_revision_r1_r5_001a/*`.
- Expected future implementation paths only if separately authorized:
  `src/action_conditioned_self_boundary_corrected_challenge_001d/`,
  `tests/action_conditioned_self_boundary_corrected_challenge_001d/`, and
  `artifacts/action_conditioned_self_boundary_corrected_challenge_001d/`.
- Forbidden changes now: `src/**`, `tests/**`, old ACSB artifacts except
  read-only citation, Gate4/Gate5 files, bridge files, tournament files,
  runtime files, EGO-mainline files, companion/product paths, and
  production/mainline config.
- Auto-Remote-Anchor decision: current draft revision is conditional; future
  001D execution remains forbidden unless a later task card explicitly
  authorizes it.

## Future 001D Measurement Contract

The future challenge measures whether an action-conditioned self-boundary
reference survives the strongest non-oracle challenger family under heldout
interventions after excluding static decoding, value leakage, row enumeration,
inert boundary memory, and rigged capacity reduction.

Headline metric:

`tested_reference_margin = tested_reference_score - max(non_oracle_challenger_scores)`

The margin is evidence-bearing only if all kill-switches, baselines, ablations,
replay, provenance, and source-pin gates pass. If any non-oracle challenger
matches the tested reference within `epsilon_tie`, ACSB closes or downgrades
instead of being repaired into a pass.

Pre-registered thresholds:

- `epsilon_tie = 0.05`
- `minimum_survival_margin = 0.15`
- `reference_minimum_score = 0.80`
- boundary-memory causal paired-probe flip floor = `0.25`, allowed only with a
  short rationale and with probes drawn from or distribution-matched to the
  scored heldout distribution; otherwise block during card audit or raise the
  floor before execution.

The future implementation must not tune thresholds after seeing results.

## R1 Capacity-Disabled Reference Repair

The fair capacity-disabled reference is not a separately designed challenger.
It is the same reference callable family with explicit persistence disable
flags:

```text
fair_capacity_disabled_reference =
  reference_callable(
    same_reference_config,
    persistence_enabled = false,
    boundary_memory_read_enabled = false,
    boundary_memory_write_enabled = false,
    disabled_component_flags = ["disable_persistence"]
  )
```

The exact switch for the fair capacity-disabled reference is
`disable_persistence`. It disables both boundary-memory read and write while
keeping the same legal observations, same preprocessing, same evidence terms,
same selector core, same aggregation rule, and same initial prior construction
as the full reference. Optional write-only or read-only ablations may exist only
as additional ablations; they do not replace the fair capacity-disabled
reference.

Required same-callable-family rule:

- The full reference and `fair_capacity_disabled_reference` must call the same
  reference function or the same shared core function.
- They may differ only by explicitly declared disable flags.
- `fair_capacity_disabled_reference` and the `disable_persistence` ablation must
  be the same callable path or share the same disable flag. If they diverge,
  block with `blocked_by_capacity_ablation_path_split_001d`.

Required shared trace schema:

- input hash;
- boundary memory before;
- boundary memory after;
- evidence terms;
- persistence read/write flags;
- selected output;
- disabled component flags;
- shared core code path hash;
- selector code path hash;
- config hash.

Required callable diff check:

- Assert that reference path and capacity-disabled path use the same shared core
  code path hash except for declared disable flags.
- Assert that capacity-disabled path does not call a separate selector formula.
- Assert that capacity-disabled path does not return stale prior, fixed failure
  token, decoy-by-construction, random fallback, or hardcoded wrong channel.
- Assert that legal evidence not explicitly disabled remains consumed.
- Assert that the selected output is produced by the shared selector core.

Operational definition of rigged:

A capacity-disabled challenger is rigged if any of the following is true:

- it uses a different selector formula than the reference shared core;
- it discards legal evidence not explicitly disabled;
- it returns stale prior by default;
- it returns a fixed failure token;
- it selects decoy or non-target by construction;
- it branches on target/evaluator-only information;
- it has a separate hand-coded decision rule not present in the reference core;
- its code path hash differs beyond declared disable flags;
- it degrades to `0.0` without trace evidence showing a mechanism-specific
  reason.

Required verdicts:

- `blocked_by_rigged_capacity_disabled_reference_001d`
- `blocked_by_capacity_ablation_path_split_001d`
- `blocked_by_capacity_reference_not_same_callable_family_001d`

Required tests for future implementation:

- fail if capacity-disabled reference is replaced by a separate formula;
- fail if capacity-disabled reference returns stale prior;
- fail if capacity-disabled reference returns a constant wrong answer;
- fail if capacity-disabled reference selects decoy by construction;
- fail if capacity-disabled reference discards non-disabled legal evidence;
- fail if `disable_persistence` ablation and capacity-disabled reference
  diverge;
- fail if the code path hash differs beyond declared disable flags;
- fail if the capacity-disabled path consumes target/evaluator-only fields.

R1 acceptance additions:

- fair capacity-disabled reference is same-callable-family with reference core;
- callable diff check passes;
- rigged-capacity tests pass;
- `disable_persistence` and capacity-disabled reference are unified.

## R2 Boundary-Memory Causal Probe Clarification

Boundary-memory causal paired probes must be drawn from, or distribution-matched
to, the scored heldout probe distribution. If the `0.25` causal-effect floor
remains, the future implementation card/run must record a short rationale. If
no rationale is provided, block during card audit or raise the floor before
execution. This clarification does not authorize threshold tuning after seeing
results.

## R3 Heldout Row-Enumerability Clarification

Heldout row-enumerability must be a callable check. The check must compute
train/heldout overlap without including the split label in the key and must
block if heldout rows or targets are row-enumerable from train/evidence
contexts. A lookup or nearest-neighbor enumerator over legal train/evidence
contexts must be unable to recover heldout targets above `majority + epsilon_tie`.

Required verdict:

- `closed_acsb_cosmetic_or_row_enumerable_split_001d`

## R4 Learned-Baseline Feature-Parity Clarification

Learned baselines and decoders must receive feature parity:

- same legal observation features as the reference;
- same legal action/no-action/external evidence where applicable;
- minus only serialized boundary memory or explicitly forbidden boundary-state
  variables;
- no feature impoverishment by omission of legal evidence.

If a learner receives fewer legal features than the reference, block unless the
baseline is explicitly labeled as a weaker auxiliary baseline and excluded from
the strongest-challenger claim.

## R6 Optional Leakage / No-Update Clarification

If the value-leakage threshold remains `majority + 0.20`, future execution must
also report distance from the tested reference and must preserve the
claim-ceiling implication. The "explicit no-update negative result" escape is
allowed only as negative evidence; it cannot be used to support a positive
survival claim.

## Required Challenger Families

Future 001D must run all non-oracle challenger families as independent callable
paths:

- `single_observation_decoder`
- `label_only_decoder`
- `value_signature_decoder`
- `probe_observation_only_learned_model`
- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`
- action-effect-frequency baseline without boundary state
- fitted linear no-boundary learner
- fitted sequence no-boundary learner
- fitted pure-Python or MLP-style no-boundary learner
- embedding/nearest-neighbor no-boundary learner
- `fair_capacity_disabled_reference` using `disable_persistence`
- read-only and write-only boundary ablations if included as additional
  ablations, not as the fair capacity-disabled reference
- oracle leakage positive control, labeled non-comparable and excluded from
  strongest non-oracle margin

If any required non-oracle challenger is omitted, block with
`blocked_by_missing_required_challenger_family_001d`.

## Required Ablations

Future 001D must rerun episodes under real interventions for:

- `disable_persistence` (same callable path as fair capacity-disabled reference);
- `freeze_boundary_update`;
- `reset_state_before_probe`;
- `remove_action_conditioned_contingency`;
- `remove_no_action_counterfactual`;
- `shuffle_action_effect_linkage_preserve_marginals`;
- `replace_boundary_state_with_recency_state`;
- `remove_boundary_memory_from_legal_state`.

Ablations must recompute behavior and must not return a constant token, stale
prior, fixed wrong answer, or report-shaped verdict.

Required verdict:

- `blocked_by_constant_or_nonmechanistic_ablation_001d`

## Required Leakage And Split Controls

Leakage scans must be real scanners with at least one positive-control case for
each forbidden family:

- explicit target/action/output field;
- oracle boundary label;
- benign answer alias;
- hidden ID mapping to answer;
- future outcome leakage;
- constant count/signature value encoding;
- rank/contrast/one-hot/near-one-hot encoding;
- hidden deterministic order;
- filename, fixture name, or context ID leakage.

Scanners must include value-level checks, not only key-name checks. Split checks
must exclude the split label from overlap keys and must include row-enumerability
pressure.

## Required Replay

Replay must recompute reference, challenger, baseline, and ablation behavior
from serialized state plus observation. It must include mutation checks:

- boundary-state mutation changes output where pre-registered;
- observation mutation changes output where pre-registered;
- metadata-only mutation does not change output;
- missing required state blocks replay.

Replay must not use stored hashes, stored verdicts, target labels, report fields,
or source-existence checks as behavior evidence.

## Required Evidence Provenance

Each score must record:

- producer function;
- input artifacts;
- run ID;
- seed/context/episode IDs;
- aggregation rule;
- code path hash;
- model class and fit/update count where applicable;
- callable path for reference, baseline, ablation, leakage scan, and replay;
- source pin for code and configuration;
- whether frozen seeds, train contexts, heldout contexts, and counterfactual
  pairs were consumed.

Any unused frozen seed, train context, heldout context, or counterfactual pair
blocks the evidence claim.

## Required Future Artifacts

If future 001D implementation is separately authorized, it must produce
artifacts under `artifacts/action_conditioned_self_boundary_corrected_challenge_001d/`:

- `result.json`
- `trace.jsonl`
- `baseline_comparison.json`
- `ablation_report.json`
- `replay_report.json`
- `leakage_report.json`
- `provenance_report.json`
- `failure_manifest.json` if anything fails
- `claim_ceiling.txt` or claim ceiling field inside `result.json`

No artifact means no evidence.

## Future Acceptance Gate

Future 001D implementation may be accepted only if all are true:

1. Start-state readback verifies the canonical route-decision boundary from an
   allowed source with `canonical_anchor_verification_source` recorded.
2. R1 same-callable-family capacity-disabled reference constraints pass.
3. Callable diff check passes.
4. Rigged-capacity tests pass, including decoy-by-construction failure.
5. `disable_persistence` and capacity-disabled reference share the same callable
   path or disable flag.
6. R2 heldout-bound paired probes and causal-effect floor rationale pass.
7. R3 row-enumerability callable check passes.
8. R4 feature parity for learned baselines and decoders passes.
9. Required challenger families all run as independent callable paths.
10. Required ablations rerun episodes under real interventions.
11. Leakage scanners include positive controls and value-level scans.
12. Replay recomputes behavior from serialized state plus observation.
13. Computed-evidence provenance is complete and callable-path-backed.
14. No implementation files outside the later authorized isolated paths change.
15. No claim exceeds bounded offline ACSB evidence under this contract.
16. Any kill-switch failure closes or downgrades ACSB with no `001E`.

## Non-Actions In This Draft Revision

- 001D implemented: false
- Runner code created: false
- Test code created: false
- Baselines implemented: false
- Ablations implemented: false
- Replay engine implemented: false
- Gate4/Gate5 entered: false
- Bridge entered: false
- Tournament entered: false
- Runtime path entered: false
- Companion/product path entered: false
- EGO-mainline entered: false
- Old ACSB artifacts modified: false
- Codex execution authorized for 001D implementation: false
- Delta re-audit required: true
- Required delta re-audit scope: `R1_and_R5`

## What This Does Not Prove

This revised draft does not prove ACSB validity.
It does not prove ACSB invalidity.
It does not prove mechanism validity.
It does not prove Gate validity.
It does not prove candidate behavior.
It does not prove agency.
It does not prove autonomy.
It does not prove consciousness.
It does not prove emotion.
It does not prove subjectivity.
It does not prove runtime readiness.
It does not prove EGO readiness.
It does not prove stable user benefit.
It does not prove companion readiness.
It does not prove production readiness.
It does not prove mainline effect.

## Next Minimal Closed-Loop Action

Run a delta hostile re-audit scoped to R1 and R5. Do not implement 001D until
that re-audit is preserved and a separate implementation task explicitly
authorizes the exact allowed paths.
