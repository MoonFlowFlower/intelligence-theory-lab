# FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A

```text
record_type = bounded independent docs-only hostile-audit task card
task_id = FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A
execution_type = documentation-only independent audit
implementation_authorized = false
gate_m_execution_authorized = false
training_authorized = false
runner_authorized = false
route_state_mutation_authorized = false
remote_publication_authorized = false
Auto-Remote-Anchor = forbidden
```

## 0. Task identity and exact paths

- Task ID: `FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A`.
- Frozen subject under audit:
  `docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md`.
- Frozen source commit:
  `d519a84fb0891bca17edd4e605a0e3cb066ecc7d`.
- Frozen source Git blob:
  `1e5f7e10170d07a02bc4799dc5d28003fcf8ab8f`.
- Frozen source SHA-256:
  `d0d078abce8622fb7c8c492497e849e14bef886012e60a15ae20684530146454`.
- Frozen source size: `77332` bytes.
- Audit report output path, addition only:
  `docs/research/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md`.
- This task card is read-only during audit execution.

The auditor must inspect the Git blob from the frozen commit, not silently audit
different worktree bytes. A source-pin mismatch is a stop condition.

## 1. Problem definition and real objective

The operator-provided handoff reports a bounded independent formal-consistency
review pass for canonical branch semantics, finite enumeration, restore
provenance within the paper contract, and aggregate denominators. The currently
pinned repository input for this task is the exact preregistration blob, not a
separately pinned formal-re-audit artifact. Treat the reported review as
operator-provided current-result provenance, not as a new computation performed
by this audit. Per the operator's scope decision, do not repeat the 512-row
review. None of that establishes that the proposed Gate M instrument is valid.

The real objective is to determine, at paper-contract level only, whether the
proposed M-S intervention is defeated by any of three independent invalidity
families:

1. the public channel exposes a relevance/source label rather than only legal
   causal semantics;
2. the patched state is not covered by a coherent, predeclared state-support
   contract;
3. undeclared persistent state can bypass the declared `(E_t,b_t)` intervention.

The audit must produce a hostile verdict, not repair the source, implement the
instrument, or make the paper pass-shaped.

## 2. Current stage, layer, and effect boundary

- Current stage: operator-directed post-formal-consistency,
  pre-instrument-validity; independent formal-re-audit artifact provenance is
  unavailable within this task's repo-pinned inputs.
- Current layer: engineering-governance plus bounded mechanism-instrument
  hypothesis audit.
- Mainline target: none.
- Mainline integration status: none.
- Enabled-state requirement: no path may be enabled by this task.
- Real-trigger evidence requirement: none is claimed or generated; Gate M is
  not run.
- Mechanism versus resemblance: this audit tests whether a proposed causal
  instrument is paper-defined and non-obviously invalid. It does not test a
  candidate mechanism or behavioral resemblance.
- Solution grade: bounded independent paper audit only.

## 3. Required read-only dependencies

The auditor must read:

1. the frozen source blob identified in Section 0;
2. `docs/EVIDENCE-GATE-INTERPRETABILITY-REFRAME-001A.md` at the frozen source
   commit, especially its auditability, replay, intervention, leakage, and
   black-box allowance requirements;
3. current repo-local `AGENTS.md` and route-governance instructions for scope
   and claim-ceiling constraints.

Complete human semantic interpretation of every possible learned latent is not
required. Evidence-grade state inventory, lineage, intervention, replay,
leakage resistance, and falsifiability remain required. The audit must not use
"black box" as permission to accept inaccessible or undeclared state.

## 4. Bounded audit framing

### 4.1 Hypothesis

If the public channel carries only legal measured-variable/action semantics,
the support rule makes every admitted patched state the deterministic recompute
of a legal ledger, and the admission contract rejects every undeclared
persistent path, then the paper may be conditionally adequate for a later
analytic-instrument calibration card.

This hypothesis does not predict that a learned candidate is supported, that
M-S will pass, or that the instrument is empirically valid.

### 4.2 Strongest baseline / shortcut explanation

A legal-history lookup/table Bayes controller, event cache, count controller,
or history-conditioned model can reproduce the canonical behavior. The
analytic Bayes response therefore has no candidate-specific separator headroom.
Formal consistency and expected analytic response can also coexist with a
leaky or infeasible intervention contract.

### 4.3 Strongest reason the task may be invalid

The paper may use `chi_D` as a privileged relevance label while calling it
public causal semantics; it may conflate record/ledger reachability with
learned joint-state support; or its no-bypass inventory may be only a declared
interface with no way to reject process-level hidden state. Any one of these is
sufficient to block the proposed M-S instrument boundary.

### 4.4 Falsifier for the favorable framing

The favorable framing is falsified or downgraded by any decisive witness that:

- recovers relevance or target direction from a public field not required to
  identify the measured variable or bind the public action/outcome;
- shows that an operated state is outside the paper's own declared legal-ledger
  and deterministic-recompute support, or that the support quantifier is
  insufficiently specified for the claimed admitted model class;
- identifies any persistent policy input not removed, replaced, frozen, or
  rejected by the M-S admission contract.

### 4.5 Evidence that remains insufficient

The following remain insufficient even if internally consistent:

- the prior 512-row enumeration;
- analytic Bayes arithmetic;
- equal vector dimensions or norms alone;
- a prose assertion that public relevance is absent;
- a declared `(E_t,b_t)` tuple without process-level completeness criteria;
- a future score, trace hash, replay hash, or model self-report;
- an auditor's stylistic preference.

## 5. Collision record

| Candidate approach | Evidence produced | Strongest cheap match | Leakage/hard-coding risk | Smallest falsifier | Expected failure mode |
|---|---|---|---|---|---|
| Minimal lexical audit | checks that the paper says channel, support, and bypass words | compliant prose with no enforceable semantics | high | find one declared field with ambiguous role or one unenumerated state class | false assurance from wording |
| Formal-consistency reuse | repeats enumeration and analytic arithmetic | lookup/table Bayes exactly matches | high risk of answering the wrong question | show all old arithmetic passes while one of the three validity axes remains unresolved | Zeno re-audit with no new discrimination |
| Three-axis hostile semantic audit (selected) | explicit per-axis verdicts, witnesses, and implementation-conditional blockers | strongest legal lookup/table controller plus hidden-state shortcut | controlled by exact source citations and fail-closed outcomes | one decisive channel, support, or bypass counterexample | instrument invalid, M-H-only downgrade, or implementation remains blocked |

The selected approach must not repeat the complete 512-row enumeration. The
preregistration bytes are banked, while the handoff's formal-re-audit result is
operator-provided current-result provenance rather than a separately pinned
repo artifact. The operator has nevertheless fixed that review as out of scope;
the current uncertainty is instrument validity on the three axes below.

## 6. Audit Axis A — public channel identity

### 6.1 Question

Does the candidate-visible distinction between `chi_D` and `chi_S` encode only
the public identity of the measured variable/action-outcome channel, or does it
function as a privileged relevance/source label for the private evaluator's
target?

### 6.2 Required hostile checks

The auditor must:

1. enumerate every candidate-visible distinction between diagnostic and sham
   records, including encoding, field domain, slot, position, time, event
   count, missingness, schema, action binding, outcome binding, and neutral
   prompt residue;
2. identify which distinctions are causally necessary to state what public
   variable/action outcome was observed and which merely reveal evaluator
   relevance;
3. test renaming invariance: renaming public measured-variable identities and
   consistently renaming the SCM/interface must not change which channel is
   selected except through its public causal role;
4. test target invariance: changing the private evaluator target while holding
   the public causal interface fixed must not leave a public code whose meaning
   is "the relevant channel";
5. check whether the public diagnostic action and its outcome binding already
   identify the channel, making a separate privileged diagnostic/relevance bit
   redundant;
6. verify that verifier-only lineage, source UID, relevance role, target action,
   `G`, and private reward never enter a candidate/baseline-visible field in the
   paper contract;
7. distinguish equal shape/norm from semantic leakage; matched dimensions alone
   cannot pass this axis.

### 6.3 Axis-A verdicts

Choose exactly one:

- `CHANNEL_IDENTITY_PAPER_ACCEPTABLE_CONDITIONAL` — the public code denotes only
  legal causal identity/action binding and remains invariant to private target
  designation; actual implementation remains unverified.
- `PUBLIC_CHANNEL_ENCODES_RELEVANCE` — a public field carries evaluator-specific
  relevance/source identity or a privileged equivalent.
- `CHANNEL_IDENTITY_PAPER_UNDERDEFINED` — the source does not determine the
  distinction strongly enough for either conclusion.

`PUBLIC_CHANNEL_ENCODES_RELEVANCE` forces overall
`M_INSTRUMENT_INVALID`. It does not authorize an anonymous-bit repair.

## 7. Audit Axis B — state-support contract

### 7.1 Question

Is the paper's support quantifier sufficient for the model class it purports to
admit, and does it avoid treating marginal record occurrence as proof that the
full operated internal state is supported?

### 7.2 Required hostile checks

The auditor must separately adjudicate:

1. record support;
2. complete ledger-grammar support;
3. deterministic state reachability through the declared normal recompute path;
4. marginal model-state support;
5. joint `(H_legal,M')` support and why it is or is not required for the stated
   causal intervention;
6. learned-density or empirical coverage support;
7. representation support;
8. policy-conditioning support;
9. origin and lineage of weights, updates, event writer, recompute, and policy;
10. whether delete, restore, random patch, and coherent state swap satisfy the
    same support definition or require distinct preconditions.

For the canonical analytic controller, the auditor must determine whether the
paper's legal-ledger plus deterministic-recompute rule is exact and closed.

For any learned or hybrid candidate, the auditor must not infer support merely
because individual records or missingness patterns occur. If numerical
coverage, learned-density, representation, or policy-conditioning requirements
are candidate-specific and unfrozen, the report must say so and keep learned
candidate execution unauthorized.

### 7.3 Axis-B verdicts

Choose exactly one primary verdict and any required qualifier:

- `ANALYTIC_CONTROL_STATE_SUPPORT_PAPER_DEFINED_CONDITIONAL` — exact only for
  the declared analytic controller; no learned-candidate support claim.
- `STATE_SUPPORT_CONTRACT_PAPER_ACCEPTABLE_CONDITIONAL` — the contract states a
  coherent fail-closed admission rule for later implementations, without
  claiming that any implementation satisfies it.
- `LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED` — analytic support may be defined,
  but learned/hybrid admission remains unfrozen.
- `M_S_INFEASIBLE_M_H_ONLY` — the required M-S operated state cannot meet the
  contract's own coherent support requirement.
- `STATE_SUPPORT_PAPER_UNDERDEFINED` — the paper does not fix a unique
  adjudicable support meaning.

`M_S_INFEASIBLE_M_H_ONLY` is terminal for M-S under this contract. It does not
falsify history dependence in M-H.

## 8. Audit Axis C — persistent-state completeness and bypass

### 8.1 Question

Does the paper provide a fail-closed admission contract under which every bit
of information that can cross steps and reach the commit policy is either part
of the operated state, frozen public input, or an explicitly rejected path?

### 8.2 Required hostile inventory

The auditor must check at least:

- `E_t` and `b_t`;
- raw observation/action history;
- Transformer KV cache;
- RNN or policy hidden state;
- encoder and feature cache;
- retrieval/RAG/external-memory state;
- episode buffer and replay buffer;
- action-history features;
- wrapper/environment adapter state visible to policy;
- event count, order, padding, missingness, or position-derived features;
- policy sampler state and policy RNG suffix;
- branch/operator identity;
- deleted-record handles and verifier lineage;
- model weights, optimizer/update state, and any online-learning state;
- process globals, singleton caches, files, services, or cross-episode state.

The report must distinguish:

1. paper-level admission completeness — whether any additional persistent path
   is explicitly rejected rather than silently tolerated;
2. implementation-level absence — which cannot be verified because no
   implementation is authorized or inspected here.

A declaration that the policy "only reads `(E_t,b_t)`" is insufficient unless
the contract also says how a later implementation must enumerate, snapshot,
intervene on, or reject every other path.

### 8.3 Axis-C verdicts

Choose exactly one:

- `PERSISTENT_STATE_CONTRACT_PAPER_COMPLETE_CONDITIONAL` — the admission rule is
  fail-closed on undeclared state, but implementation absence is unverified.
- `PERSISTENT_STATE_CONTRACT_PAPER_UNDERDEFINED` — one or more state categories
  can reach policy without a unique admission disposition.
- `M_S_INVALID_RAW_HISTORY_OR_STATE_BYPASS` — the paper explicitly permits or
  structurally requires an unoperated second information path.

No paper-only outcome may be phrased as proof that a real process has no bypass.

## 9. Baseline and ablation requirements

- Strongest baseline: legal-history lookup/table Bayes controller with the same
  public access. Its behavioral equivalence is expected and caps the claim.
- Secondary shortcut challengers: event cache, count table, transition table,
  successor map, finite-state controller, episodic traversal, and
  history-conditioned model.
- No empirical baseline is run.
- No ablation episode is run.
- The paper-level hostile ablations are:
  1. remove or rename the public channel identity;
  2. vary the private evaluator target while freezing the public interface;
  3. delete a record and require full normal recompute;
  4. add one undeclared persistent path and check that admission fails closed.
- These are semantic counterexample tests, not computed Gate evidence.

## 10. Trace/replay and computed-evidence provenance gate

No trace, replay, leakage score, branch score, or empirical verdict may be
generated or claimed in this task.

The auditor may use read-only Git/object/hash commands and exact source
citations. If the report repeats any numeric result from the preregistration, it
must label it as frozen source readback rather than independently recomputed
evidence. The 512-row enumeration must not be rerun.

Any future empirical claim remains blocked until a separate task provides:

```text
producer_function
input_artifacts
run_id
seed/context/episode IDs
aggregation_rule
code_path_hash
independent callable baselines
real intervention reruns
positive-control leakage scan
state-and-observation replay recomputation
```

## 11. Overall verdict function

The report must emit exactly one overall verdict according to this precedence:

1. source/scope/independence failure -> `AUDIT_BLOCKED`;
2. Axis A `PUBLIC_CHANNEL_ENCODES_RELEVANCE` -> `M_INSTRUMENT_INVALID`;
3. Axis B `M_S_INFEASIBLE_M_H_ONLY` -> `M_S_INFEASIBLE_M_H_ONLY`;
4. Axis C `M_S_INVALID_RAW_HISTORY_OR_STATE_BYPASS` ->
   `M_S_INVALID_RAW_HISTORY_OR_STATE_BYPASS`;
5. any axis underdefined -> `PAPER_INSTRUMENT_CONTRACT_REQUIRES_REVISION`;
6. all axes conditionally acceptable ->
   `PAPER_INSTRUMENT_CONTRACT_AUDIT_PASS_FOR_ANALYTIC_CALIBRATION_ONLY`.

The final pass-shaped label is allowed only at the paper-contract level. It does
not authorize implementation. If Axis B also returns
`LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED`, the report must preserve that as an
explicit blocker even if analytic calibration is conditionally acceptable.

## 12. Acceptance gate for the audit report

The report is acceptable only if it contains:

1. auditor identity/independence statement;
2. repo root, branch, audited commit, Git blob, SHA-256, byte count, and source
   pin readback;
3. confirmation that the source and task card were not modified;
4. exact line citations or section citations for every decisive finding;
5. one Axis-A verdict and its strongest counterexample;
6. one Axis-B verdict, with analytic versus learned/hybrid support separated;
7. one Axis-C verdict, with paper completeness versus implementation absence
   separated;
8. the precedence-derived overall verdict;
9. fact / derivation / inference / assumption / unknown labels;
10. blocking and non-blocking findings;
11. minimal repair requirements if and only if the verdict requires revision;
12. claim ceiling and explicit "what this does not prove" section;
13. final exact-path diff/status readback.

The report must also record
`FORMAL_REAUDIT_PROVENANCE_UNAVAILABLE_IN_THIS_TASK` as a provenance limitation;
it must not convert that limitation into permission to repeat the 512-row audit
or to reject the exact-byte source pin.

The auditor must not issue a favorable verdict merely because the source is
well written or because the previous formal-consistency review passed.

## 13. Stop conditions

Stop without repair if:

- the source commit, blob, SHA-256, byte count, or path does not match Section 0;
- the task card or preregistration would need modification;
- the audit cannot be completed without source, runner, test, artifact, route,
  ledger, or schema changes;
- the auditor authored the repaired `001B` and cannot make an independent
  review statement;
- any prior result is silently upgraded from paper readback to computed evidence;
- any attempt is made to run Gate M, train a model, create a runner, or inspect a
  non-existent implementation as though it were real;
- more than the exact report output path would be added or modified;
- any push, tag, or remote anchor is attempted.

## 14. Scope, expected files, and forbidden changes

### 14.1 Card-drafting scope

This drafting task may add only:

```text
docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md
```

### 14.2 Independent-audit execution scope

The independent auditor may add only:

```text
docs/research/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md
```

Read-only dependencies include the task card, frozen preregistration, AGENTS,
route-governance files, and interpretability reframe.

### 14.3 Forbidden changes and actions

```text
docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md
docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md  (during audit)
all other docs/**
src/**
tests/**
scripts/**
artifacts/**
docs/research/FSP-STAGE-LEDGER.md
docs/decision_log.md
artifacts/ROUTE-STATE-MACHINE-001A/**
src/route_state_machine_001a/**
tests/route_state_machine_001a/**
any EGO repository/runtime/mainline path
```

Also forbidden: implementation, Gate M execution, training, runner creation,
threshold selection, route mutation, staging, commit, push, tag, and anchor.

## 15. Rollback plan

- Card drafting rollback: delete only the newly created uncommitted task-card
  file.
- Independent-audit rollback: delete only the newly created uncommitted audit
  report.
- Never reset, revert, overwrite, or clean pre-existing user work.

## 16. Claim ceiling

Maximum favorable claim:

> The frozen preregistration's channel-identity, state-support, and
> persistent-state admission rules survived a bounded independent paper-level
> hostile audit for later analytic instrument calibration, subject to explicit
> implementation-conditional blockers.

Maximum unfavorable claims are limited to the named paper-instrument defect or
downgrade found by the audit.

No outcome proves:

- that any implementation satisfies the contract;
- that the instrument is empirically valid;
- that any candidate state is load-bearing;
- that a learned update exists or is on-support;
- that Gate M, Gate P, or Gate X passed;
- baseline non-equivalence or a unique mechanism;
- agency, autonomy, selfhood, subjectivity, consciousness, or real emotion;
- EGO readiness, mainline effect, runtime readiness, companion readiness, or
  user benefit.

## 17. Next minimal closed-loop action

Run this docs-only audit through an independent reviewer. After its report is
returned, perform a separate exact-scope review/banking decision. Only an
independent paper-audit outcome that conditionally accepts all three axes may
support drafting a later analytic-calibration implementation card; it still
does not authorize that implementation.
