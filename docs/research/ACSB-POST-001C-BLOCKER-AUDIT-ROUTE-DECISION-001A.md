# ACSB-POST-001C-BLOCKER-AUDIT-ROUTE-DECISION-001A

Route-decision audit (no-implementation) for the `action_conditioned_self_boundary`
(ACSB) surface, executed after both the 001B positive-evidence attempt and the 001C
negative/blocker attempt were independently blocked.

This document decides process direction only. It does not implement, rerun, or repair a
runner, candidate, baseline, ablation, leakage scanner, replay engine, test, Gate4/Gate5
path, bridge, tournament, runtime path, companion behaviour, or EGO-mainline path.

## Verdict

`authorize_one_final_corrected_acsb_challenge_001a`

Route option selected: **Option A — one final corrected ACSB challenge**, conditional on
the successor task (`ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D`) adopting
the structural metric and kill-switch probes specified below, and on a strict terminal
stop that closes or downgrades ACSB on any probe failure with no `001E` redesign.

This is a close call against Option C (close/switch). Option A is chosen **only because**
(a) the corrected challenge can be made terminal and (b) the headline metric can be
redefined so that the two defects that voided 001B and 001C become self-defeating rather
than dependent on a scanner catching them. Without both of those, Option C would be the
correct decision. See "Route decision rationale".

## Status

- Current layer: `engineering-governance / post-blocker route-decision audit only`
- Mainline integration status: `none`
- Enabled status: `none` (no runner, candidate, Gate4/Gate5, bridge, tournament, runtime,
  companion, product, or EGO-mainline path is created or enabled by this task)
- Real trigger evidence: the preserved boundary
  `PRESERVE-AND-REMOTE-ANCHOR-CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A`
  (`d429ad7…`) records that the 001C blocker does not validly support ACSB closure or
  downgrade: the 001C reference was not an operative ACSB mechanism, the target was
  value-encoded into legal observations, the leakage scanner was name-based and missed
  value-level leakage, and the capacity-disabled reference was not fair. ACSB therefore
  remains unresolved — not validated and not validly falsified.
- Claim ceiling: `route-decision recommendation only`
- Auto-Remote-Anchor: `conditional`

## Start-State Readback (no reliance on memory)

All readback below was taken fresh from repository refs and from a clean clone of
`origin/codex/meta-theory-scaffold`, not from prior memory.

- Branch: `codex/meta-theory-scaffold`
- Local HEAD (mount `.git/refs/heads/...`): `d429ad78948e964d2a17efc05a57e8388f7fae26`
- Remote branch `origin/codex/meta-theory-scaffold`: `d429ad78948e964d2a17efc05a57e8388f7fae26`
- Local/remote tag `remote-anchor-claude-independent-acsb-001c-blocker-audit-001a-d429ad7`
  → `d429ad78948e964d2a17efc05a57e8388f7fae26`
- Local HEAD = remote branch = canonical tag = `d429ad7…` (exact 3-way match)
- Ahead/behind vs `origin/codex/meta-theory-scaffold`: `0 0`

### Environment / worktree-hygiene findings (non-blocking, pre-existing, not authored here)

- The mount `.git/config` was corrupted with ~24 trailing NUL bytes (FUSE artifact),
  producing `bad config line 19`; the NUL padding was stripped so git could read refs.
  No semantic config change was made (remote, branch, user unchanged).
- The mount `.git/index` is independently corrupted (`unknown index entry format`);
  `git status` cannot run against the mount. All git operations for this task were
  therefore performed in a clean `/tmp` clone of the canonical remote, which is the
  documented workaround for this mount.
- The mount **working tree is not clean** relative to canonical `d429ad7`. Besides
  pervasive whole-file CRLF rewrites (cosmetic), there are 10 genuine semantic
  divergences, including `AGENTS.md` (a governance rule source) with a deleted block,
  and several `gate4_replacement_discriminative_social_latent_implementation_task_card_001a`
  artifacts. These are **uncommitted, pre-existing, and not authored by this task** (the
  same CRLF + `AGENTS.md`-governance-block condition was independently flagged in the
  001B hostile audit). They are excluded from this task's commit by construction: the
  commit is built from the clean canonical tree plus this task's five new files only.
- Consequence (audit note): the blanket `rsync -a --delete` push recipe in
  `scripts/push.sh` would have swept all of the above (including the `AGENTS.md`
  governance-block deletion) into this route-decision commit — a governance-self-
  modification and evidence contamination. A controlled add-only clone workflow was used
  instead.
- `scripts/push.sh` and `scripts/push.py` carry a plaintext GitHub token and are
  git-ignored; they are excluded from the commit and the token is never reproduced in any
  artifact. Flagged as a repo-hygiene concern, out of scope for this route decision.

## Source Artifact Readback (canonical SHA-256, from clean clone at `d429ad7`)

| Path | SHA-256 |
| --- | --- |
| `docs/research/CLAUDE-INDEPENDENT-ACSB-001B-HOSTILE-AUDIT-001A.md` | `dfa3c3c0de34e3aacf3934d90693165b4a611c510b4cb2db0261d36e476e0c5a` |
| `docs/research/CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A.md` | `56010927d6b4a6e932bd5b6ad004aa2b1fe23d5d7e762e3a81ea04e0dd6e0cf2` |
| `docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-MEASUREMENT-OBJECT-SPEC-001A.md` | `084b64076f03d603351a8131eb3c9291485fc5666cd2a39dd0a31f9eeda5c8c9` |
| `artifacts/claude_independent_acsb_001b_hostile_audit_001a/audit_verdict.json` | `93de18a8afbbf196dbd68a69079cb3fc96e6ae395d894047a1d81c409dad792a` |
| `artifacts/claude_independent_acsb_001b_hostile_audit_001a/readback.json` | `58af207570227c76d9abfd6a6842528849c08cd2595948bc4278ca4343be17d0` |
| `artifacts/claude_independent_acsb_001c_blocker_audit_001a/audit_verdict.json` | `06bc3c388a01f6a05db2947029c21770f99292a0d7fd18c6b4748a6547fc2ccc` |
| `artifacts/claude_independent_acsb_001c_blocker_audit_001a/readback.json` | `73f5e63ee554d1e73c55342a7b7568853f6f672d7414a33647abd0dc0f63e4a4` |
| `artifacts/action_conditioned_self_boundary_executable_preflight_001b/result.json` | `298dd55f9b1aab545233e59913c4b55114e8dacfa64e2eb025acde2df70b856f` |
| `artifacts/action_conditioned_self_boundary_executable_preflight_001c/result.json` | `7a9202686c3177532375d89874a1f0ff895fe7a0085a1e002244ddf2aa57554f` |

Note: the mount copy of `CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A.md` hashes to
`54d335db…` because it carries CRLF terminators; it is byte-identical to the canonical
LF copy after stripping CR (verified). The canonical LF hash above is authoritative.

## Inherited Negative Evidence (constraints, not positive mechanism evidence)

1. **001B — positive attempt, blocked.** `result.json` verdict
   `action_conditioned_self_boundary_executable_preflight_001b_survives_learned_baseline_scaling_challenge`
   was blocked by `CLAUDE-INDEPENDENT-ACSB-001B-HOSTILE-AUDIT-001A`
   (`claude_independent_acsb_001b_audit_blocks_on_learned_baseline_invalidity`). The three
   "learned" baselines were deterministic heuristics named after ML methods (no
   `numpy`/`torch`/`sklearn`, no `.fit`, no train/test split); the capacity-matched
   reference discarded its computation and returned `stale_prior_channel`. The
   `reference 1.0 vs challenger 0.0` gap was a **designed** separation; the headline gate
   was non-fail-able on exactly the three axes it claimed to test.

2. **001C — negative attempt, blocked.** `result.json` verdict
   `blocked_by_fitted_no_boundary_learned_baseline_001c` (`reference_score = 1.0`) was
   blocked by `CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A`
   (`…audit_blocks_on_reference_or_capacity_mismatch`). 001C **did** fix the 001B
   fake-learner defect (genuine perceptron/sequence fitting with guards), but: the
   "reference" boundary memory was provably all-zero across all 32 held-out episodes with
   `update_rate = 1.0`, so it reduced to a static `argmax(self − no − ext)` decoder (not
   operative ACSB); the target was written into the legal observation as a constant
   `{self=3, no=0, ext=0}` signature (statically decodable on 100% of held-out episodes);
   the fair-capacity reference `argmax(self + ext)` was reverse-engineered to select the
   decoy (`0.0`); the leakage scanner matched key names only and was structurally blind to
   the value-level leak; the split non-overlap was guaranteed by including the split label
   in the key. 001C is **void, not negative**.

3. **Measurement-object spec already exists.**
   `ACTION-CONDITIONED-SELF-BOUNDARY-MEASUREMENT-OBJECT-SPEC-001A`
   (`action_conditioned_self_boundary_measurement_object_spec_001a_complete`) already
   names the object `ACSB-CONTINGENCY-BOUNDARY-UPDATE-OBJECT-001A` and already required
   exclusion of value-encoded answers, fail-able cheap-baseline pressure, operative state,
   non-cosmetic split, and the graph-cache challenger family. **Both 001B and 001C
   collapsed into failure modes the spec had already named.** This is the single most
   important fact for the route decision: the binding constraint is not specification (it
   exists) but a metric whose validity does not depend on a scanner catching a subtle leak.

4. **Prior route precedent.** A prior route decision
   (`CLAUDE-INDEPENDENT-POST-FAILABILITY-BLOCKER-ROUTE-DECISION-AUDIT-001A`) preserved
   `switch_to_different_surface` when an earlier route went governance-proxy-shaped. ACSB's
   situation is materially different: 001C removed the fake-learner degree of freedom, and
   a concrete corrected metric is available, so the precedent does not compel an immediate
   switch here.

## Route Options Compared

**Option A — one final corrected ACSB challenge.** Strongest case: ACSB has never received
a valid test; both prior results are void (rigged challengers / inert reference / value
leakage), not genuine falsifications. 001C fixed the 001B defect, so the diagnosis is
converging. A terminal challenge under a margin-over-strongest-cheap-baseline metric
yields valid evidence in either direction (positive margin = bounded survival evidence;
≈0 margin = valid collapse/negative evidence).

**Option B — downgrade ACSB to harness lessons.** Strongest case: preserve ACSB only as a
testbed-hygiene lesson (value-level leakage control, operative-reference requirement,
anti-static-decoder tests, real-split checks, fair capacity baseline) and stop treating it
as the primary route. Weakness: it resolves nothing and risks indefinite ambiguity — it
neither obtains the one valid test ACSB has never had nor commits to a cleaner surface.

**Option C — close ACSB and switch surface.** Strongest case: two implementations
collapsed despite a detailed spec that named those exact failure modes; a surface that
keeps re-encoding the answer into legal observations may have a poor signal-to-governance
ratio, and the cycles are an opportunity cost. Weakness: the alternatives (intervention-
response persistence, delayed counterfactual update, action-conditioned intervention
transfer) face the **same** anti-leakage / fair-baseline / cheap-baseline-family
requirements — switching does not escape the governance cost; it discards the accumulated
ACSB diagnosis and resets the construction clock on a new surface.

## Required Audit Questions — Answered

1. **What must ACSB measure to avoid static single-observation decoding?** A target defined
   only over a multi-step action→outcome contingency (e.g., which channels become
   self-controlled only after the agent's own calibration interventions), such that no
   single legal observation frame contains the answer and the decision requires integrating
   contingency across ≥2 steps. Enforced operationally by defining the metric as the margin
   over a fitted single-observation decoder.

2. **Can an operative boundary-memory/persistence reference be specified without privileged
   target access?** Yes — the reference reads only legal fields (serialized boundary state +
   legal observation + intervention) and writes its boundary state from past action-outcome
   evidence carried across steps. Operativeness must be *measured* by an inert-reference
   probe: mutating/zeroing the boundary state must change the reference output on a
   pre-registered fraction of held-out episodes; if output is invariant to state mutation,
   the reference is inert → close. (001C failed exactly here.)

3. **Can the task be constructed so the legal observation is not enough for a label-only
   decoder?** It cannot be assumed — it must be tested. Fit a label-only decoder on the
   legal observation; if it reaches ≈reference on held-out, the observation leaks the target
   → close. The target must never be written into observation values (001C wrote a `{3,0,0}`
   signature).

4. **Can value-level leakage be tested cheaply and fail-ably?** Yes — a fitted label-only /
   count-signature decoder over legal observation *values* is cheap and structurally
   fail-able. It must be a **blocking gate**, replacing the 001C name-based scanner.

5. **Can train/heldout split be made genuinely non-cosmetic?** Yes — split on a generative
   parameter family (e.g., contingency-schedule family) with the split label excluded from
   the key, and verify held-out requires generalization (a decoder fit on train must not
   transfer trivially). 001C's split label was the key's first element → guaranteed-disjoint
   but cosmetic.

6. **Can a fair capacity-disabled reference be specified without rigging it to fail?** Yes —
   same input access and same parametric capacity, with only the persistence/state-write
   disabled (memory frozen at prior). It must not be a different hand-written formula that
   selects a decoy (001C's `argmax(self+ext)`, 001B's `stale_prior`). If this fair
   challenger matches the reference, persistence adds nothing → close.

7. **Would one more corrected challenge create discriminative mechanism evidence, or mostly
   another governance-heavy artifact?** Conditional. Under a margin-over-strongest-cheap-
   baseline metric with pre-registered kill-switch probes, it creates discriminative
   evidence in both directions. Without that structural metric, it risks another void.
   Authorization is contingent on the structural metric.

8. **Is ACSB still the best surface, or has the route shown surface-class brittleness?**
   Brittleness is real but concentrated in two now-diagnosed, fixable construction defects,
   not an intrinsic impossibility. The Option-C alternatives face the same requirements, so
   switching resets the diagnostic clock rather than removing the cost. The accumulated
   diagnosis is an asset that survives only if ACSB gets one more attempt.

9. **What is the strongest baseline for a corrected ACSB challenge?** The strongest cheap-
   baseline *family*, pre-registered and mandatory: a fitted label-only decoder over legal
   observations, plus `graph_lookup`, `transition_table`, `successor_map`, `count_table`,
   `fsm_planner`, `episodic_traversal`, and an action-effect-frequency model. Per the lab's
   Preflight Audit Rule, the graph-cache family is mandatory when representational or
   environment claims are made. The headline metric must be `candidate − max(family)`.

10. **Strongest reason to stop ACSB now?** Two implementations collapsed despite a spec that
    already named the failure modes; a surface that keeps re-encoding the answer into legal
    observations may be easier to game than to test, and the cycle cost is an opportunity
    cost against cleaner surfaces.

11. **Strongest reason to allow one final corrected challenge?** ACSB has never received a
    valid test — both prior results are void, not genuine. 001C fixed the 001B defect, so
    the diagnosis is converging. A terminal challenge yields valid evidence either way, and
    closing now would close on void tests rather than on one fair test.

12. **Stop condition after the next action?** Hard terminal stop, no `001E`. ACSB closes (or
    downgrades) if any of: the fitted label-only decoder reaches ≈reference (value/static
    leakage); the inert-reference probe shows the boundary state is non-operative; the fair
    capacity-disabled challenger matches the reference; any cheap-baseline-family member
    matches the candidate within the pre-registered margin ε; or the split is shown
    cosmetic. A positive margin yields only "bounded offline action-conditioned
    self-boundary discrimination evidence under the 001D contract" — nothing higher.

## Strongest Reason to Continue ACSB vs Strongest Reason to Stop

- **Continue:** ACSB has not yet been validly tested. 001B was void by rigged challengers;
  001C was void by inert reference + value-encoded target. 001C nonetheless fixed the
  fake-learner defect, so the failure family is shrinking, and a margin-over-cheap-baseline
  metric makes the remaining defects self-defeating rather than scanner-dependent.
- **Stop:** A detailed measurement-object spec already existed and named these exact failure
  modes, yet two implementations still collapsed. That is evidence of surface-class
  brittleness and a poor signal-to-governance ratio, and the accumulated cycles are an
  opportunity cost.

## Route Decision Rationale (why A over C, and why this is not a Zeno step)

The decision turns on one distinction: the void in 001B/001C was not a failure of
*specification* (the object spec already required the right controls) but a failure of
*metric construction* — each implementation's self-check (leakage scanner, capacity
reference, split key) was built in a non-fail-able way, and the headline metric used the
raw reference score rather than a margin over the strongest cheap baseline. The fix is
therefore structural, not "try harder": redefine the headline metric as
`candidate − max(cheap-baseline family)`, where the family mandatorily includes a fitted
label-only decoder over legal observations and the graph-cache family. Under that metric,
value-leakage and static decodability automatically collapse the margin to ≈0 — they
become self-defeating rather than something a separate scanner must catch. That removes the
specific degrees of freedom that voided both prior attempts.

This is what separates Option A from a Zeno loop. The loop is "keep redesigning 001C
forever." Option A here is a **single terminal experiment** with pre-registered kill-switch
probes and an automatic close-on-failure: either it produces a valid discriminative result
(positive margin = bounded survival evidence; ≈0 margin = valid collapse/negative evidence,
which is the clean falsification ACSB has never had), or it trips a probe and ACSB closes.
The downside is bounded — the audit layer has now twice caught invalid ACSB evidence, so a
bad 001D will also be caught — and both terminal outcomes are evidence the lab currently
lacks. Option C remains the correct decision the moment 001D's structural metric or terminal
stop cannot be honoured; it is the automatic fallback, not a discarded option.

## Acceptance Criteria for Authorizing Option A — Satisfaction

1. Concrete corrected measurement object defined — yes (refines
   `ACSB-CONTINGENCY-BOUNDARY-UPDATE-OBJECT-001A`; metric = margin over strongest cheap
   baseline; probes below).
2. Requires temporal/action-contingency structure, not static decoding — yes (Q1; metric
   = margin over fitted single-observation decoder).
3. Value-level leakage probe — yes (Q4; fitted label-only/count-signature decoder as a
   blocking gate).
4. Observation-only decoder probe — yes (Q3; same fitted decoder).
5. Operative boundary-memory/persistence check — yes (Q2; inert-reference probe).
6. Fair capacity-disabled challenger — yes (Q6; persistence-only disabled, equal access &
   capacity, not reverse-engineered).
7. Non-cosmetic split criteria — yes (Q5; split label excluded from key; target not
   fixed-index/deterministic artifact).
8. Strict no-`001E` stop condition — yes (Q12).
9. Failure of the final challenge closes/downgrades ACSB — yes (Q12; automatic fallback to
   Option C/B).
10. Does not enter implementation directly — yes (this is a route decision only; no `src/`,
    `tests/`, runner, candidate, baseline, ablation, Gate, bridge, tournament, or runtime
    file is created).

## Successor Constraints (binding on `ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D`)

The corrected challenge must be a **new task**, not an in-place repair of 001C, and must
require a separate bounded task card and a separate authorization instruction before any
implementation. Mandatory constraints:

- Reference boundary memory must be causally used; mutating boundary-memory state must
  change reference behaviour on a pre-registered fraction of held-out episodes (inert
  reference → close).
- The legal observation alone must not allow near-perfect decoding; a fitted label-only /
  observation-only decoder reaching ≈reference score blocks the task (close).
- A value-level leakage scanner must test count/signature value encodings, not key names
  (close on detected value leakage).
- The train/heldout split key must not include the split label; the target rule must not be
  a fixed index or hidden deterministic artifact.
- The fair capacity-disabled reference must be independently callable, equal in access and
  capacity, with only persistence disabled, and must not be rigged to select a decoy; if it
  matches the reference, close.
- The headline discriminative metric is `candidate − max(cheap-baseline family)` where the
  family mandatorily includes the fitted label-only decoder, `graph_lookup`,
  `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`,
  and action-effect-frequency. If any non-boundary learned/cheap baseline matches the
  reference/candidate within the pre-registered margin ε, close ACSB.
- Ablations must be non-constant and mechanism-specific (perturb the boundary-update process,
  not only observation values).
- No further ACSB redesign after this challenge (no `001E`). Failure closes or downgrades
  ACSB.
- Claim ceiling for a successful 001D may be no stronger than "bounded offline
  action-conditioned self-boundary discrimination evidence under the 001D trace/replay
  contract." It must not be upgraded toward mechanism truth, Gate validity, agency,
  autonomy, consciousness, emotion, subjectivity, runtime/EGO readiness, companion
  readiness, or stable user benefit.

## Anti-Hardcoding / Governance Discipline

This route decision creates no behaviour and tunes no threshold. The margin ε and the
kill-switch probe thresholds are deferred to the 001D task card and must be pre-registered
there before any run, not tuned after seeing results. The decision does not modify the
governance documents that would judge 001D; it inherits the 001B/001C audit verdicts and
the measurement-object spec read-only. No second logic path, schema change, or label
leakage is introduced.

## Stop Condition

This route-decision task stops after writing the five allowed files, running the required
checks, and (conditionally) anchoring. It must not enter 001D implementation. 001D, if
later authorized, carries the strict terminal stop in "Successor Constraints": any tripped
kill-switch probe closes or downgrades ACSB with no `001E`.

## What This Cannot Prove

This document is a process-direction recommendation. It proves nothing about ACSB
mechanism validity or invalidity (001C is void, not negative; 001B is void, not positive).
It asserts no mechanism validity, Gate validity, candidate behaviour, agency, autonomy,
consciousness, subjective experience, real emotion, self-awareness, AGI, runtime/EGO
readiness, companion readiness, stable user benefit, or mainline effect. A future 001D, at
best, could yield only bounded offline discrimination evidence under its own contract.

## Remaining Unknowns

- Whether a 001D implementation can in fact honour the margin-over-cheap-baseline metric
  without re-introducing a void (the prior two attempts collapsed despite an adequate spec;
  the structural metric reduces but does not eliminate this risk).
- The numeric margin ε and probe thresholds (deferred to the 001D task card; must be
  pre-registered).
- Whether, conditional on a clean 001D construction, the ACSB reference shows any positive
  margin at all over the cheap-baseline family (the prior on collapse-to-baseline is high).

## Next Minimal Closed-Loop Action

Draft the bounded task card
`ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D` (task-card only, no
implementation), encoding the Successor Constraints above and pre-registering ε and the
kill-switch probe thresholds, then stop for a separate authorization instruction before any
run. If that task card cannot be written so that every kill-switch probe is fail-able and
the terminal stop is honoured, do not author it — close ACSB under Option C instead.
