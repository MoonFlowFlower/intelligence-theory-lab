# CLAUDE-INDEPENDENT-ACSB-001D-CARD-LEVEL-HOSTILE-AUDIT-001A

Card-level hostile audit (no implementation) of the draft task card
`ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D`.

This audit decides only whether the 001D draft card is fail-able, bounded, and resistant
to the known ACSB collapse modes enough to be handed to Codex for one final bounded
offline corrected challenge. It does not implement 001D, write runner/test code, repair
the card in repo, or enter any Gate/bridge/tournament/runtime/companion/EGO-mainline path.

## Verdict

`claude_independent_acsb_001d_card_audit_requires_minor_card_revision_before_execution`

**Codex execution is NOT authorized as written.** The card's architecture is sound and it
structurally closes the *primary* 001B defect (dummy learner) and the *primary* 001C
defects (inert reference, value-level leakage, cosmetic split, static decodability). It is
**not** approvable as-is because one approval criterion is unmet: the fair capacity-disabled
reference fairness is stated as prose prohibition with no structural/callable enforcement,
so the exact 001C rigging pattern remains constructible. The required fixes (R1–R5 below)
are small and targeted — they do not change the task structure, headline metric, or
pre-registered thresholds — so this is a minor revision, not a major one and not a close.

## Current layer

`engineering-governance / task-card hostile audit only`.

## Mainline integration status

`none`. No module, runner, test, Gate, bridge, tournament, runtime, companion, product, or
EGO-mainline path was created, enabled, or modified.

## Enabled status

`none`. Read-only repository inspection plus authoring of this audit artifact only.

## Real trigger evidence

- The route-decision boundary `ACSB-POST-001C-BLOCKER-AUDIT-ROUTE-DECISION-001A` (verdict
  `authorize_one_final_corrected_acsb_challenge_001a`) authorizes exactly one final
  corrected ACSB challenge, conditional on the 001D card structurally preventing the 001B
  and 001C collapse families, with a strict terminal no-`001E` stop.
- The route-decision doc records its own start-state anchor as
  `d429ad78948e964d2a17efc05a57e8388f7fae26` (tag
  `remote-anchor-claude-independent-acsb-001c-blocker-audit-001a-d429ad7`), with the mount
  `.git/index` corrupted (`unknown index entry format 0x70680000`) and commits performed in
  a `/tmp` clone.
- The draft card under audit was supplied as an upload; it is **not** present in the repo
  (`docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D.md` does not
  exist), consistent with its draft status.

## Claim ceiling

Card-level audit verdict only. This audit does not claim ACSB mechanism validity or
invalidity, Gate validity, candidate behavior, agency, autonomy, consciousness, emotion,
subjectivity, runtime readiness, EGO readiness, stable user benefit, or mainline effect. It
determines only whether the 001D task card is safe to hand to Codex for one final bounded
offline corrected challenge.

## Audited card name

`ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D` (uploaded draft).

## Canonical input boundary actually used

Per the audit contract, only repo readback, current artifacts, and the supplied draft were
used; memory was not relied on. Readback findings:

- Mount branch ref `codex/meta-theory-scaffold` HEAD = `d429ad7…`; remote branch (per
  route-decision `git_readback.json`) = `d429ad7…`.
- The card's claimed anchor `fb0129aebe760d25bf4051328cdbf9ed14095694` and tag
  `remote-anchor-acsb-post-001c-route-decision-001a-fb0129a` are **absent from the mount**:
  `git cat-file -t fb0129a` fails (object not found), `fb0129a` is in no branch log, the tag
  is not in `git tag`, and `fb0129a` appears nowhere in the route-decision artifacts (whose
  `git_readback.json` is `start_state_pre_change` = `d429ad7`).
- This is **explainable, not proven fabricated**: the route-decision commit was made in a
  `/tmp` clone (the documented workaround for the corrupted mount index) and the mount refs
  were never fast-forwarded, so the route-decision files sit in the mount working tree while
  the mount HEAD stays at `d429ad7`. `fb0129a` is therefore *plausibly* the legitimate
  route-decision commit on `origin`, but it is **not independently confirmable from this
  mount**. See R5.

## Strongest support for approving 001D

The card is a disciplined, hostile-aware response to two specifically diagnosed voids. It
converts the route-decision's central insight — make leakage *self-defeating* via a
`reference − max(challenger family)` margin rather than scanner-dependent — into concrete,
pre-registered, mandatory kill-switch probes. The anti-static-decoder battery (four
mandatory decoders), the value-level leakage scanner (count/rank/contrast/one-hot/order/ID
+ linear/stump/NN probes), the operative-boundary-memory battery (mutation-changes-output
plus not-reproducible-from-observation), the mid-episode-serialized-state replay with a
four-way mutation contract, the ~17-field computed-evidence provenance with an explicit
ban on report-shaped scores, and the learner-validity capability positive control
(contaminated input must be learnable) each map directly onto a documented prior failure.
A failure result is terminal and clean by construction, and the claim ceiling is correctly
capped. Most collapse modes are genuinely closed at the card level.

## Strongest objection to approving 001D

**The fair capacity-disabled reference is not structurally fail-able.** The card specifies
its fairness only as prose prohibitions ("disable only the boundary-memory or persistence
operation," "not reverse-engineered to select decoy," "not discard useful information
except the explicitly ablated mechanism") with **no callable check** that the disabled
reference is the reference code path with persistence turned off. 001C's void came from
exactly this gap: a *separately authored* formula (`argmax(self+ext)`) relabeled as the
"fair" capacity reference and reverse-engineered to select the decoy. Under the current
wording that pattern is still constructible. It is worse on a terminal challenge: survival
requirement #6 ("boundary-disabled reference degrades by at least 0.20 without being
rigged") means a capacity reference rigged to fail would *inflate* the survival evidence —
a route to a **false-positive survival** with no `001E` to catch it. The blast radius is
contained (a positive verdict also requires beating the observation-only, label-only, and
learned-no-boundary challengers by ≥0.15, which an inert/static reference cannot do), so
this does not by itself void the whole challenge — but the capacity line of evidence is
untrustworthy as written, and the card's own "capacity-disabled reference is rigged" test
has no operational definition of "rigged," so that test is not actually fail-able. This is
the single blocking-grade defect and the reason the card cannot be approved unrevised. It
is fixable with a small same-callable-flag-off construction (R1).

## Loophole assessment by category

**1. Dummy learner — substantially closed. Risk: LOW.**
`fit_called=true`, nonzero update count, a fit-removal mutation test that must raise, a
constant-predictor guard, a static-score-injection test that must fail, and (decisively) a
capability positive control requiring the learner to actually learn contaminated/leakage
input. A non-fitting heuristic-named-after-ML (the 001B defect) fails the capability
control and the fit-removal test. Residuals (minor): pure-python learners are allowed
(acceptable if genuinely fitted); the "unless an explicit no-update negative result is
preserved" clause is an escape hatch worth bounding; and the card does not explicitly
require learned baselines to receive the *same legal feature set* as the reference
(feature-impoverishment was part of the 001B family) — see R4.

**2. Inert reference — mostly closed. Risk: LOW–MEDIUM, backstopped.**
Five checks, including "mutating boundary memory changes output in ≥25% of paired probes"
and "reference output not reproducible from probe observation alone within epsilon_tie,"
plus the closure verdict `closed_acsb_reference_memory_inert_001d`. 001C's all-zero memory
would fail checks #1, #2, and #4. Residual: the ≥25% paired-flip floor is soft and the
paired-probe set is not required to be drawn from the scored heldout distribution, so it can
be satisfied by a contrived fixture — but check #4 plus the mandatory observation-only
decoder kill-switch is a genuine structural backstop (a secretly observation-driven
reference is matched by the observation-only decoder → close). See R2.

**3. Static decoder — well closed. Risk: LOW.**
Four mandatory kill-switch decoders (`single_observation_decoder`, `label_only_decoder`,
`value_signature_decoder`, `probe_observation_only_learned_model`) with epsilon_tie /
majority+0.20 thresholds, plus a five-phase episode in which "no single observation contains
enough information to decode target." This is the direct fix of the 001C static-decode void.
The concrete generative task is delegated to implementation, so static-undecodability is
enforced by the kill-switches rather than guaranteed by the card's task spec — adequate
given the decoders are mandatory and powered by the learner-validity controls.

**4. Value leakage — well closed. Risk: LOW.**
The value-level scanner enumerates constant-count, rank, contrast, one-hot/near-one-hot,
hidden-deterministic-order, ID-recoverability, and linear/stump/NN decoders — directly
catching the 001C `{self=3,no=0,ext=0}` count signature and the `contrast = self−no−ext`
leak. Residual: the `majority + 0.20` pass threshold is somewhat permissive in isolation;
it is tightened in practice by the primary margin metric and the observation-only
kill-switch. See R6.

**5. Cosmetic split — well closed. Risk: LOW–MEDIUM.**
Bans split-label-in-key, fixed-index targets, and ID/order recoverability; requires a
generative-family split, differing decoy correlations train vs heldout, a controlled
intervention-mapping rule family, target entropy + majority reporting, and a split-overlap
audit computed without the split label; closure verdict
`closed_acsb_cosmetic_or_row_enumerable_split_001d`. Residual: "heldout combinations must
not be row-enumerable" is asserted as a requirement but not operationalized as a callable
check (unlike the split-overlap audit). See R3.

**6. Capacity challenger — NOT structurally closed. Risk: MEDIUM–HIGH (primary fix).**
See "Strongest objection." Prose-only fairness; 001C rigging still constructible; the
`fair_capacity_boundary_disabled_reference` baseline and the `disable_persistence` ablation
are two code paths for one concept (path fragmentation), inviting a separately authored,
riggable formula; "rigged" is undefined so the anti-rigging test is non-fail-able. **R1
required.**

**7. Ablations — well closed. Risk: LOW.**
Eight boundary-process-specific ablations that must recompute behavior, preserve un-ablated
input, record traces, and not return a constant token; closure verdict
`blocked_by_constant_or_nonmechanistic_ablation_001d`.
`shuffle_action_effect_linkage_preserve_marginals` is a strong positive discriminator (it
destroys the contingency while preserving marginals, so a static decoder is unaffected
where a genuine contingency-tracker is not). Residual: the "removes mechanism vs destroys
target information" distinction is not operationalized for freeze/reset, but the
marginals-preserving shuffle carries the discriminative load.

**8. Replay / provenance — well closed. Risk: LOW.**
Replay recomputes from mid-episode serialized state plus observation with a four-way
mutation contract (boundary mutation changes output; observation mutation changes output;
metadata-only mutation does not; missing state fails) and bans stored-hash/verdict/label/
report-field replay. Provenance ties every score to a producer function, input hash, seed,
split/episode IDs, code-path hash, model class, and update count, and explicitly bans
literal/static-dict/report-only/field-presence/validator-cleanliness/manifest-completeness/
source-existence scores, with a required static-score-injection test that must fail. This
directly addresses the 001C weak-determinism replay and the lab's recurring
non-fail-able-provenance pattern.

**9. Thresholds — pre-registered, mostly reasonable. Risk: LOW–MEDIUM.**
`epsilon_tie=0.05` (tight, good), `minimum_survival_margin=0.15` (defensible floor, modest
for a ~4-channel task), `reference≥0.80`, value leakage ≤`majority+0.20`, boundary-disabled
degrade ≥0.20. All pre-registered in the card; "do not tune after seeing results" and the
no-`001E` ban on relaxing thresholds are present. The softest number is the
boundary-causal-effect rate ≥0.25, which interacts with the inert-reference gaming residual
(R2). No threshold is tunable post-hoc as written.

**10. No-001E — operational as far as a card can enforce. Risk: LOW.**
Enumerates allowed downstream actions (preserve, close, switch surface, route-decision
audit) and forbidden ones (`001E`, ACSB repair loop, threshold relaxation, baseline
removal, leakage-probe weakening, failure-reframing); "task suggests 001E" is a stop
condition; acceptance gate #15 enforces closure on any kill-switch. Residual: "switch
surface" / "route-decision audit" could in principle re-authorize ACSB under a new name —
the inherent un-bindability of a future session — partially mitigated by the preserved
one-final-challenge boundary.

**11. Overconstraint / artificiality — not blocking. Risk: LOW–MEDIUM.**
The card is heavy (~19 challengers, 8 ablations, 4 decoders, ~9 leakage probes, 6-part
replay, ~17 provenance fields, 8 learner controls, ~13 required test-failures) but
constructible — comparable POMDP-style tasks already exist in the lab. Critically, the
constraints **fail safe**: an over-tight or accidentally re-leaking construction collapses
the margin and *closes* ACSB (a valid terminal outcome) rather than producing a void. The
concrete generative task is delegated to implementation; its adequacy rests on the
kill-switches firing. A successful result's evidential upside is deliberately bounded (the
claim ceiling concedes this; the route-decision notes the prior on collapse-to-baseline is
high), but a clean result is informative in either direction.

**Canonical-state finding (outside the 11 design categories). Risk: MEDIUM to handoff.**
The card's `fb0129a` anchor is unverifiable from the mount and the card omits the
corrupted-mount-index / `/tmp`-clone workaround. Acceptance gate #1 ("Start-state readback
confirms canonical `fb0129a` route boundary") would spuriously **fail** if executed naively
on the mount (mount HEAD is `d429ad7`, `fb0129a` absent), producing a false block. See R5.

## Required audit questions — answered

1. **Measurement object not solvable by static single-observation decoding?** Yes, by
   enforcement rather than by full task spec: the five-phase structure requires
   ≥2-step contingency integration and the mandatory `single_observation_decoder`
   kill-switch closes ACSB if a single legal observation reaches within `epsilon_tie`. The
   concrete generative instantiation is delegated; the kill-switch is the guarantee.
2. **Operative boundary-memory requirement strong enough?** Mostly yes — five checks
   including mutation-changes-output and not-reproducible-from-observation. Soft on the
   ≥0.25 paired-flip floor; backstopped by check #4 + observation-only kill-switch. Tighten
   per R2.
3. **Can the causal-effect check be gamed without real temporal state?** Partially — a
   contrived paired-probe fixture decoupled from the scored episodes can clear the ≥0.25
   floor. Mitigated, not eliminated; R2 closes it by tying paired probes to the scored
   heldout distribution.
4. **Are observation-only, label-only, value-signature, probe-observation-only decoders
   mandatory and fail-able?** Yes — all four are mandatory kill-switch probes with explicit
   thresholds. This is the strongest section and the direct 001C fix.
5. **Value-level leakage scanner strong enough?** Yes, substantially — enumerated value/
   rank/contrast/one-hot/order/ID/linear/stump/NN probes catch the 001C value leak.
   Threshold permissiveness only (R6).
6. **Split requirements sufficient against cosmetic heldout?** Mostly — bans
   split-label-in-key, fixed-index, ID recoverability; requires generative-family split and
   overlap audit. "Row-enumerable" needs operationalizing (R3).
7. **Prevents fixed-index or hidden deterministic target artifacts?** Yes, explicitly
   (split reqs #3/#4, leakage ID/order probes, `initial_state` ban). Direct fix of the 001C
   `CHANNELS[index%8]` defect.
8. **Is `reference − max(challenger family)` robust?** Yes in principle — the route's core
   structural fix that makes leakage self-defeating. Robust modulo the capacity-fairness gap
   (R1) and a complete challenger family (satisfied).
9. **Are `epsilon_tie=0.05` and `minimum_survival_margin=0.15` reasonable and
   pre-registered?** Pre-registered: yes. Reasonable: `epsilon_tie` tight/good; `0.15`
   defensible though modest; the ≥0.25 causal-rate is the soft one.
10. **Forces all strong challenger families to run?** Yes — 9 cheap (full graph-cache family
    `graph_lookup`/`transition_table`/`successor_map`/`count_table`/`fsm`/`episodic_traversal`,
    mandatory per the lab Preflight Rule), 6 learned, 4 capacity, 3 oracle controls, all as
    independent callable paths, close on any non-oracle match within `epsilon_tie`.
11. **Enough learned no-boundary baselines?** Yes — six, covering linear/sequence/
    mlp-or-pure-python/probe-obs-only/label-only/embedding-knn.
12. **Prevents feature-impoverished learned baselines?** Partially — capability positive
    control + feature-removal control help, but feature parity with the reference is not
    stated explicitly. Add R4.
13. **Requires real fitting and update-count verification?** Yes — `fit_called`, nonzero
    updates, fit-removal test, constant-predictor guard, static-injection test. Direct 001B
    fix. Minor "no-update negative result" escape (R6).
14. **Fair capacity-disabled reference specification strong enough?** **No** — prose-only,
    no same-callable-flag-off construction, path-fragmented with the `disable_persistence`
    ablation. Primary defect. R1.
15. **Can the fair capacity-disabled reference still be rigged under current wording?**
    **Yes** — the 001C separately-authored decoy-selecting formula remains constructible; on
    a terminal challenge it can inflate survival req #6 toward a false positive. R1.
16. **Ablations mechanism-specific rather than target-destroying?** Mostly yes — eight
    boundary-process ablations incl. the marginals-preserving shuffle; must recompute, not
    constant. The mechanism-vs-target distinction is not operationalized for freeze/reset but
    the shuffle carries the load.
17. **Replay strong enough, incl. mid-episode serialized state?** Yes — mid-episode
    serialized-state recomputation + four-way mutation battery + bans on stored-verdict/hash/
    label/report-field replay.
18. **Provenance strong enough against report-shaped scores?** Yes — ~17 fields per score +
    explicit bans + a required static-score-injection test that must fail.
19. **Tests strong enough to fail under each known collapse mode?** Mostly — the
    required-tests list covers inert memory, static decode, scanner/decoder removal,
    split-label-in-key, fixed-index, rigged capacity, constant ablation, fit/update removal,
    stored-verdict replay, provenance gaps, static injection. The "rigged capacity" test is
    not yet fail-able because "rigged" is undefined; R1 makes it real.
20. **Is the no-001E rule operational or rhetorical?** Largely operational (enumerated
    allowed/forbidden actions, stop condition, acceptance gate #15). Residual: future
    "switch surface"/"route audit" could re-authorize ACSB under another name — inherent
    un-bindability, partially mitigated.
21. **Overconstrained to artificiality/impossibility?** No — heavy but constructible, and
    the constraints fail safe to *close* rather than to a void. Concrete task delegated;
    adequacy rests on kill-switches.
22. **Would success add discriminative mechanism evidence or just governance artifact?**
    Bounded but real — a clean positive margin is genuine bounded discriminative *surface*
    evidence (not mechanism validity); a collapse is the clean falsification ACSB has never
    had. Upside deliberately small; both outcomes are evidence the lab currently lacks.
23. **Would a failed 001D cleanly close/downgrade ACSB?** Yes — kill-switches map to
    explicit closure verdicts; terminal no-`001E` stop; failure routes to preserve/close/
    switch. A failure is clean and terminal by construction. A strength.
24. **Approve, revise, or close without 001D?** **Revise (minor).** Architecture sound,
    primary collapse modes closed; a small targeted fix set (R1–R5) is required before
    execution. Not approve (criterion #5 unmet); not close (a bounded revision salvages a
    sound card); not major (no architecture/metric/task-structure rewrite).

## Required card revisions

**R1 (primary, blocking).** Replace the prose-only fair capacity-disabled reference with a
single canonical construction: the *same* reference callable invoked with a
persistence/boundary-write flag disabled — forbid a separately authored formula. Unify the
`fair_capacity_boundary_disabled_reference` baseline and the `disable_persistence` ablation
into one code path (remove the fragmentation). Add a callable diff-check proving the only
behavioral difference vs the full reference is the ablated operation, and give "rigged" an
operational definition so the "capacity-disabled reference is rigged" test is actually
fail-able.

**R2.** Require the boundary-memory causal-effect paired probes to be drawn from the scored
heldout distribution (not a separate fixture); either raise the `0.25` flip floor or
pre-register a justification; keep check #4 (not reproducible from observation) as the
structural backstop.

**R3.** Operationalize "heldout not row-enumerable" as a concrete callable check (e.g., a
lookup / nearest-neighbor enumerator over train contexts must not recover heldout targets
above `majority + epsilon`), with a closure path on failure.

**R4.** State explicit feature parity: learned no-boundary baselines (and the
observation/label decoders) must receive the same legal observation feature set as the
reference minus boundary memory, to foreclose feature-impoverished baselines.

**R5.** Reconcile the canonical start-state: confirm or correct the `fb0129a` anchor (it is
absent from and unverifiable on this mount), and document the corrupted-mount-index +
`/tmp`-clone workaround so acceptance gate #1 is checked against the canonical remote rather
than spuriously failing on the mount.

**R6 (clarifying, optional).** Tie the value-leakage pass threshold to both `majority+0.20`
and an epsilon-of-reference bound; bound or remove the "unless an explicit no-update
negative result is preserved" escape in the learner-validity controls.

## Whether Codex execution is authorized

**Not authorized as written.** Apply R1–R5 (R6 optional). After revision, a delta
re-audit limited to R1 (capacity-disabled-reference construction) and R5 (canonical
start-state) is recommended; a full re-audit is not required because the remaining sections
are already structurally fail-able. If R1 cannot be honored with a genuine
same-callable-flag-off fair challenger, do not execute — close ACSB under the route
decision's Option C fallback rather than ship a terminal challenge with a riggable capacity
line.

## What this cannot prove

This audit cannot prove ACSB validity or invalidity, mechanism validity, Gate validity,
candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, runtime
readiness, EGO readiness, stable user benefit, or mainline effect. It cannot prove that a
revised 001D will avoid a void (the prior two attempts collapsed despite an adequate spec).
It establishes only that the 001D draft card, as supplied, is close to but not yet safe to
hand to Codex: it closes the primary 001B/001C collapse modes but leaves the fair
capacity-disabled reference riggable and a small number of secondary gaps, all of which are
fixable by the bounded revisions R1–R5 without changing the card's task structure, headline
metric, or pre-registered thresholds.
