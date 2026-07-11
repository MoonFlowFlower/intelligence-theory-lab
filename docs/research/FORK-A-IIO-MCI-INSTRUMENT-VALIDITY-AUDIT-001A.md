# FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A — Independent Instrument-Validity Paper Audit Report

```text
record_type = independent docs-only hostile instrument-validity paper audit report
task_id = FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A
executed_by = Claude (independent auditor role per repo Same-Agent Bridge Audit Role 001)
execution_type = documentation-only audit; no implementation, no run, no enumeration rerun
audit_date_utc = 2026-07-10

axis_A_verdict = CHANNEL_IDENTITY_PAPER_ACCEPTABLE_CONDITIONAL
axis_B_primary_verdict = ANALYTIC_CONTROL_STATE_SUPPORT_PAPER_DEFINED_CONDITIONAL
axis_B_qualifier = LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED (preserved explicit blocker)
axis_C_verdict = PERSISTENT_STATE_CONTRACT_PAPER_COMPLETE_CONDITIONAL
overall_verdict = PAPER_INSTRUMENT_CONTRACT_AUDIT_PASS_FOR_ANALYTIC_CALIBRATION_ONLY

formal_reaudit_provenance = FORMAL_REAUDIT_PROVENANCE_UNAVAILABLE_IN_THIS_TASK
implementation_authorized = false
gate_m_execution_authorized = false
banking_status = report only; independent banking decision pending
Auto-Remote-Anchor = forbidden
```

Citation convention: `PRE §x (Ln–m)` cites `docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md`
by section and line numbers of the frozen blob; `CARD §y` cites
`docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md`.

## 1. Auditor identity and independence

This audit was executed by Claude acting in the durable independent-auditor /
red-team role defined by the repo operating contract (Same-Agent Bridge Audit
Role 001; Solo Development Protocol 2026-07-05C). The auditor did not author
`FORK-A-IIO-MCI-PREREG-001B.md` or its repair, has no authorship stake in the
IIO/MCI design, and had no contact with the prereg content before this audit
session. PRE §0 (L22–24) records that the design author does not hold the
independent-audit role; that separation is satisfied here. No stop condition
under CARD §13 item "auditor authored the repaired 001B" applies.

## 2. Source pin readback

| Pin | Required (CARD §0 / operator) | Observed | Match |
|---|---|---|---|
| Repo root (host) | `D:\Project\AIProject\MyProject\intelligence-theory-lab` | same; mounted read/write for docs only | yes |
| Branch | — (not pinned) | `codex/meta-theory-scaffold` | n/a |
| HEAD at audit time | — | `d519a84fb0891bca17edd4e605a0e3cb066ecc7d` (= frozen source commit) | yes |
| Frozen source commit | `d519a84fb0891bca17edd4e605a0e3cb066ecc7d` | `git rev-parse HEAD` = `d519a84fb0891bca17edd4e605a0e3cb066ecc7d` | yes |
| Frozen source blob | `1e5f7e10170d07a02bc4799dc5d28003fcf8ab8f` | `git rev-parse d519a84...:docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md` = `1e5f7e10170d07a02bc4799dc5d28003fcf8ab8f` | yes |
| Frozen source SHA-256 | `d0d078abce8622fb7c8c492497e849e14bef886012e60a15ae20684530146454` | `sha256sum` of worktree file and of `git cat-file blob 1e5f7e10...` both = `d0d078ab...146454` | yes |
| Frozen source size | `77332` bytes | `wc -c` = 77332; `git cat-file -s 1e5f7e10...` = 77332 | yes |
| Worktree == frozen blob | required (CARD §0: inspect blob, not different worktree bytes) | `git hash-object` of worktree prereg = `1e5f7e10170d07a02bc4799dc5d28003fcf8ab8f` | yes |
| Audit card SHA-256 | `fc8555c6cd19c34338fe365a3695718b3de862bfd001e6c94f7c7f1f54f86d6f` (operator pin) | `sha256sum` = same | yes |
| Interpretability reframe | read at frozen commit (CARD §3.2) | blob at `d519a84...` = `0ef77cf4a81c39c0a7c3a238285cbecbd02c5a30`, equal to worktree hash-object and to PRE §6 pin (L295) | yes |
| Report output path | must not pre-exist | `docs/research/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md` absent before this write | yes |

Worktree state observations (facts):

1. The audit card itself is untracked (`?? docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md`);
   it is not in the frozen commit. Its identity is pinned by the operator
   SHA-256 above, which matched. This is consistent with CARD §14.1
   (card-drafting adds only the card) and is not a stop condition: CARD §0
   pins the audited source by commit/blob/SHA-256, and those pins hold.
2. Broad `git status` shows many ` M` entries on unrelated paths (artifacts,
   AGENTS.md, etc.). Known FUSE mount line-ending/staleness churn; the host
   git view is authoritative per repo protocol. Decisive checks above used
   content hashes, which are immune to this. The pinned prereg path itself is
   clean (not in the dirty list).
3. Read-only git commands on the no-delete mount emitted
   `warning: unable to unlink .git/index.lock`; a stray `.git/index.lock` may
   remain for operator cleanup. No repo content was modified by this audit.

## 3. Non-modification confirmation

The frozen prereg and the audit card were not modified: both files re-hash to
their pinned SHA-256 values in the final readback (Section 14), taken after
this report was written. The only path added by this audit is this report
file, matching CARD §14.2 exactly. No stage, commit, push, tag, anchor, route,
ledger, src, tests, scripts, or artifacts action was performed.

## 4. Method, scope discipline, and provenance limitation

- Scope: exactly the three axes of CARD §§6–8, at paper-contract level only.
- The 512-row enumeration was NOT rerun (CARD §10). Where this report states
  numeric values from PRE §§13–14, they are frozen source readback. A small
  number of single-point analytic values (Section 6.3, Section 8) were
  re-derived by hand by the auditor solely to check axis arguments; these are
  labeled derivations, are not a rerun of the enumeration, and are not
  computed Gate evidence.
- `FORMAL_REAUDIT_PROVENANCE_UNAVAILABLE_IN_THIS_TASK`: the operator handoff
  reports a formal-consistency re-audit pass (canonical branch semantics,
  finite enumeration, restore provenance, aggregate denominators). No such
  re-audit artifact is pinned among this task's repo inputs. It is treated
  here as operator-provided current-result provenance only. This limitation
  is recorded and was not used to expand scope, repeat the 512-row review, or
  question the exact-byte source pin (CARD §12).
- Read-only dependencies read in full: frozen prereg (1687 lines),
  `docs/EVIDENCE-GATE-INTERPRETABILITY-REFRAME-001A.md` at the frozen commit,
  current `AGENTS.md`, and the repo/route governance instructions. Per CARD
  §3, "black box" was not accepted anywhere as permission for undeclared
  state (cross-checked against reframe §9 allowance and §16 stop conditions).

## 5. Axis A — public channel identity

### 5.1 Exhaustive candidate-visible distinction inventory (CARD §6.2 item 1)

From PRE §7.4 (L482–534), §10 (L695–714), §15 (L1337–1370):

| Distinction channel | Diagnostic vs sham difference | Adjudication |
|---|---|---|
| channel code `chi` | `chi_D` vs `chi_S`, fixed-width one-hot, equal norm (L489–491, L494–499) | the sole semantic separator; adjudicated in 5.2–5.4 |
| bit payload `v` | `Y^d` vs `Z`; both marginal Bernoulli(1/2) | no distributional separator; see 5.5 |
| slot index `i` | assigned by `Pi`, randomized (L512, L521–523) | none |
| write step `t_out`, schema `sigma` | identical encodings (L496–497) | none |
| missingness | `R_D,R_S` i.i.d. Bernoulli(1/2) (L348–352); public missing symbol reveals presence only (L529–531) | presence/absence of the `chi_D`-channel record is variable-level information, same legality class as `chi` itself; used by the analytic posterior (L666–672) |
| event count / order / padding / prompt residue | neutral prompt byte-constant, carries no masks, count, order, timestamps, metadata (L531–534; §14.7#3 L1285–1295) | none |
| action binding | diagnostic action is forced and constant in Stage-0 (L431, L437–439) | none |

Verifier-only fields (lineage, source UID, relevance role, target action,
`G`, private reward `J`): the four-stream access matrix marks all of them
candidate-invisible and baseline-invisible (PRE §15 L1354–1358, L1364–1367),
and PRE §7.2 (L415–417) states the model receives no field named `Q_D`, `G`,
`relevant`, or `target`. No contradictory double classification was found
(L1369–1370). CARD §6.2 item 6: satisfied at paper level.

### 5.2 Is `chi` causally necessary or merely relevance-revealing? (items 2, 5)

Without `chi`, the two outcome records are exchangeable to candidate and
baseline: payloads are marginally identical, slots are `Pi`-randomized, and
within one episode `(v, y_0)` statistics do not separate `Y^d` from `Z`
(auditor derivation; agrees with PRE §4.2's anonymous-bits analysis, L170–176,
where exact Bayes accuracy degrades to 3/4). Therefore the public diagnostic
action and outcome binding do NOT already identify the channel; `chi` is
load-bearing public schema, not a redundant privileged bit. The instrument as
specified requires channel identity, and the source openly declares it as an
explicit analytic assumption (PRE §4.4 L217–219) rather than hiding it.

### 5.3 Renaming invariance (item 3)

`chi_D` is defined as "the `Y` outcome measurement" and `chi_S` as the sham
(= `Z`) measurement (PRE §7.4 L489–491); `Z` is a declared public exogenous
variable (PRE §7.1 L319). The SCM graph equations are public spec (PRE §15
L1365). Renaming `Y→V2`, `Z→N`, `chi_D→chi_V2post`, `chi_S→chi_N`
consistently across SCM and interface leaves the analytic controller's
selection rule derivable from the renamed public spec alone: it selects the
record measuring the (renamed) post-diagnostic `Y`-variable because the public
structural equations make that variable's agreement with the passive value
identify `G`. Selection changes only through public causal role. Renaming
invariance holds at paper level.

### 5.4 Target invariance (item 4) — decisive test

Hold the public interface fixed and change the private evaluator target
(e.g., reward matching `Z` instead of `c_G`). `chi_D` still denotes "the `Y`
measurement"; the evaluator-relevant record becomes the `chi_S` record; no
public code changes meaning or assignment. Therefore no public code means
"the relevant channel": the codes denote fixed variable identities, invariant
to private target designation. The binding of `chi_D` to the `Y`-measurement
is static in the frozen SCM — it is not assigned per-episode by
informativeness. Target invariance holds at paper level.

### 5.5 Strongest counterexample (required by CARD §12 item 5)

Single-informative-channel extensional collapse: in this SCM exactly one
public channel is informative about `G`, so extensionally
"is the `chi_D` record" ⟺ "is the evaluator-relevant record". A hostile
reading says `chi_D` therefore functions as a relevance label. Adjudication:
the code's content is variable identity; relevance is obtained only by
combining that identity with the public SCM spec through causal inference —
the code shortcuts nothing that is not already public. It is target-invariant
and renaming-invariant (5.3–5.4), whereas a true relevance label would track
the target. The extensional coincidence is a property of this deliberately
minimal environment, and the claim ceiling already caps the result at
instrument calibration (no relevance-discovery or uniqueness claim; PRE §4.1
L157–167, §24). The source also explicitly accepts that an auditor could
reject even this code, and forbids the anonymous-bit repair (PRE §4.2
L184–188); this audit does not reject it, for the stated reasons.
Implementation-conditional blocker: `chi` assignment must remain statically
bound to variable identity; any generator that assigns `chi_D` per-episode to
whichever record is informative, or that surfaces the strings
"diagnostic"/"sham"/"relevant" in a candidate-visible encoding, flips this
axis to `PUBLIC_CHANNEL_ENCODES_RELEVANCE`.

Equal shape/norm was not accepted as a pass reason (CARD §6.2 item 7); the
adjudication above rests on semantic invariance, not on matched dimensions
(PRE §10 matching is treated only as necessary mechanical hygiene).

### 5.6 Axis-A verdict

`CHANNEL_IDENTITY_PAPER_ACCEPTABLE_CONDITIONAL` — the public code denotes
legal causal identity/action binding and remains invariant to private target
designation; actual implementation remains unverified. This also discharges,
at paper level only, PRE §22 blocker 2 (L1615–1618): the required independent
adjudication of `chi_D/chi_S` is hereby rendered, subject to the independent
banking decision.

## 6. Axis B — state-support contract

### 6.1 The ten required adjudications (CARD §7.2)

Support checker: PRE §12 (L813–861), three conjuncts — record support,
ledger-grammar support (`E' ∈ E_cal`), state reachability
(`state = Recompute_theta(E')`); quantifier explicitly marginal (L845–851).

1. Record support: defined and decidable — every field combination
   enumerable under the frozen calibration distribution (L816–819). Exact.
2. Complete ledger-grammar support: `E_cal` is closed-form and finite
   (L820–838); deletion from the both-present ledger lands in an
   asymmetric-missingness cell that has positive natural support
   (L836–838; §14.3 L1015–1023). Exact.
3. Deterministic state reachability: conjunct 3 (L839–843) requires exact
   equality with the declared normal recompute output and explicitly bans
   density estimates, probe accuracy, NN scores, and retrospective latent
   interpretation as substitutes. Exact for the canonical controller.
4. Marginal model-state support: the chosen quantifier (L845–851), with the
   missingness-quantifier subtlety resolved rather than fudged: PRE §7.1
   (L350–361) states the distributional-plus-scored-pair reading and the
   honest consequence that the stricter episodewise reading would force an
   `M_S` downgrade. No conflation of marginal record occurrence with
   operated-state support was found: the operated object is always the whole
   ledger-plus-recompute, not a record marginal.
5. Joint `(H_legal, M')` support: explicitly not required, with the correct
   reason — under the deterministic declared writer, conditioning on fixed
   intact `H_legal` collapses the joint-support set to the intact state, so
   joint support would define M-S out of existence (L852–855). The swap
   operator is explicitly declared cross-world-inconsistent and is labeled
   the causal intervention, not a natural joint sample (PRE §11.6 L806–811).
   Auditor assessment: sound; this is the honest treatment, not a loophole.
6. Learned-density / empirical coverage: explicitly required to be frozen
   before any learned/hybrid candidate runs, and explicitly NOT frozen here
   (L857–861; §22 blocker 4 L1621–1623). Candidate-specific and unfrozen.
7. Representation support: analytic controller — the ledger itself plus
   `b ∈ {0, 1/2, 1}`; exact. Learned — unfrozen (no criterion stated).
8. Policy-conditioning support: analytic — `delta_tau(b)` total on all
   reachable `b`, tie rule fixed and target-independent (PRE §7.1 L330–338,
   §9 L679–686). Learned — unfrozen.
9. Origin/lineage: origin enum required without synonym expansion (PRE §8.4
   L627–635); canonical control all-ANALYTIC (PRE §9 L646–651); event
   writer, recompute, and policy declared; `theta`/`tau` frozen at the branch
   point (PRE §7.5 L541–554) and hash-recorded in the future trace contract
   (PRE §19.2). Paper-adequate.
10. Operator preconditions: delete/sham require own-record presence
    (independent of the partner; PRE §14.5 table L1055–1062, invariants
    I14–I16 readback L1227); restore additionally requires the frozen
    verifier-private handle (`RESTORE_SOURCE_UNDEFINED` otherwise); patch and
    swap are walled outside the 512-row function (PRE §11.5–11.6 L773–811,
    §7.1 L369–371) but their outputs are still governed by the same §12
    support checker. Distinct preconditions are declared, not blurred.

### 6.2 Exact-and-closed determination for the canonical analytic controller

Auditor derivation (operator-closure check, not an enumeration rerun): from
any base ledger in `E_cal` — rel_delete lands in the `(R_D=0)` cell;
sham_delete in the `(R_S=0)` cell; both single-deletion results are members
of `E_cal` with natural support; restore returns the exact base ledger; the
random patch with payload `W` yields a record vector identical to
`e_D(G'',U,Pi)` for the `G''` with `Y^d(G'',U)=W`, hence a member of `E_cal`
(both `W` values realizable for either `U`); the swap installs a donor bundle
that is itself `(Recompute_theta(E'), E')` for a donor `E' ∈ E_cal`. The
passive record `e_Y0` is present in every member and is never operated
(PRE §7.4 L478–480). Conclusion: the legal-ledger-plus-deterministic-recompute
rule is exact and closed for the declared analytic controller.

### 6.3 Analytic versus learned/hybrid support — separated

- Analytic: support is exactly defined, decidable, and closed (6.1–6.2). The
  spot-checked canonical values used by the axis argument
  (`b_intact=G`, `b_rel_delete=1/2`, `b_sham_delete=G`, `b_rel_restore=G`;
  `D_rel=1/2`, `D_sham=0`, `LSE_J=1/2`, `E[J_rel_delete]=3/8`) were
  re-derived by hand from PRE §§7.2, 9, 13 and agree with the frozen readback
  (PRE §13 L910–951). Labeled: auditor derivation confirming frozen source
  readback; not computed Gate evidence; not the formal re-audit.
- Learned/hybrid: the admitted model class is nominally covered by the same
  three-conjunct definition, but the evidence standard that would make the
  definition adjudicable for a learned `Recompute_theta` (coverage, sample
  size, representation and policy-conditioning evidence) is candidate-specific
  and deliberately unfrozen (L857–861). Per CARD §7.2, this is reported as
  such and learned-candidate execution remains unauthorized.

### 6.4 Axis-B verdict

Primary: `ANALYTIC_CONTROL_STATE_SUPPORT_PAPER_DEFINED_CONDITIONAL` — exact
only for the declared analytic controller; no learned-candidate support claim.
Qualifier: `LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED` — preserved as an
explicit blocker per CARD §11, even though analytic calibration is
conditionally acceptable. `M_S_INFEASIBLE_M_H_ONLY` is not triggered: the
paper's own support requirement is met by the declared analytic operated
states (6.2), and the contract's fail-closed downgrade path for
non-conforming candidates is itself well-formed (PRE §12 L853–855).

## 7. Axis C — persistent-state completeness and bypass

### 7.1 Required inventory adjudication (CARD §8.2)

Against PRE §8.1–8.2 (L558–599), §7.5 (L541–554), §15, §18, §22:

| CARD §8.2 item | Prereg disposition | Class |
|---|---|---|
| `E_t`, `b_t` | declared operated state; `b_t` has no independent update path (L580–596) | operated |
| raw observation/action history | "raw public history buffer outside `E_t` — absent" (L590); Stage-0 action is forced/constant, so no action-history information exists to carry | explicitly rejected |
| Transformer KV cache | itemized absent (L591) | explicitly rejected |
| RNN / policy hidden state | "auxiliary recurrent state — absent" (L592); §18 stop condition adds "undeclared recurrent state ... or any other bypass" (L1443–1445) | explicitly rejected |
| encoder / feature cache | not itemized by name; caught by the universal clause L597–599 | rejected via catch-all |
| retrieval / RAG / external memory | itemized absent (L593) | explicitly rejected |
| episode / replay buffer | training-side covered by "optimizer state or online-training state — absent during evaluation" (L594); inference-side is a raw history buffer (L590) | explicitly rejected |
| action-history features | derived persistent features are additional state → catch-all | rejected via catch-all |
| wrapper/adapter state visible to policy | excluded by the single semantic call interface `Policy_theta(NU_COMMIT_V1, M_t)` (L572–575); any extra input violates the declared interface | rejected via interface contract |
| event count/order/padding/missingness/position features | inside `E_t` they are the ledger (legal); at the neutral prompt they are absent (L531–534; §14.7#3 `I(G;O_neutral)=0`, L1285–1292) | operated or absent |
| policy sampler state / RNG suffix | model-private RNG absent; sampling external, suffix `omega_pi` frozen byte-identical across branches (L595, L551–553, L363–367) | frozen |
| branch/operator identity | verifier-only (§15 L1356); candidate cannot read `K` | rejected (not candidate-visible) |
| deleted-record handles / verifier lineage | verifier-only (§15 L1354–1355) | rejected (not candidate-visible) |
| weights, optimizer/update, online-learning state | `theta` frozen at branch point (L549); optimizer/online state absent during evaluation (L594) | frozen / rejected |
| process globals, singleton caches, files, services, cross-episode state | not itemized by name; caught by the universal clause; additionally, any cross-episode ledger accumulation makes `E' ∉ E_cal` and fails the §12 support checker; §18 stop condition "a future learned candidate leaves any persistent state unenumerated" (L1456); §22 blocker 3 requires future process-state enumeration and proof (L1619–1621) | rejected via catch-all + support checker |

The universal clause is L597–599: "An implementation with any additional
inference-time persistent state is not an M-S subject under this card. It
must not be rescued by calling the state ephemeral." This is an explicit,
fail-closed rejection of every unenumerated category, not silent tolerance.

The CARD §8.3 sufficiency test — a bare "policy only reads `(E_t,b_t)`"
declaration is insufficient unless the contract says how a later
implementation must enumerate/snapshot/intervene/reject other paths — is met
at paper level: enumerate (L578–579 "must account for exactly these
categories"; §22.3), snapshot/serialize (§19.2 trace contract:
`E_before/E_after`, `b_before/b_after`, `theta`/code-path hash, RNG suffix
identifiers, L1478–1497), replay-recompute rather than hash comparison
(L1499–1502), absence manifest (§15 L1363), and reject (L597–599, §18).

### 7.2 Paper completeness versus implementation absence — separated

- Paper-level admission completeness: acceptable-conditional. Every category
  in the CARD §8.2 list has a unique disposition (operated / frozen /
  explicitly rejected / verifier-only), several via the universal
  disqualification clause rather than by-name itemization (non-blocking
  finding N-3). No state category was found that can reach the commit policy
  with a tolerated-but-undeclared disposition.
- Implementation-level absence: unverified and unverifiable here — no
  implementation exists or was inspected. The prereg itself is explicit that
  the neutral-prompt leakage result is "a proof about the specified
  interface, not evidence that a future implementation obeys it" and that a
  future process-level state inventory and positive leak controls remain
  mandatory (L1293–1295). This report makes no claim that any real process
  has no bypass.

### 7.3 Bypass hunt (hostile)

Searched for any path the paper explicitly permits or structurally requires
that crosses the branch point unoperated: `theta`/`tau` frozen; `omega_E`,
`omega_pi` frozen byte-identical; public history frozen; neutral observation
byte-constant; environment-private `(G,U,Z,Pi,R_D,R_S)` reaches only the
environment/evaluator, never the policy (§15 L1364–1367); post-commit public
channel adds no `G` information (§14.7#4 L1297–1321, with the honest
refutation of the over-broad literal claim); verifier lineage/handles persist
but are policy-unreachable; a stale cached `b_t` alongside `E_t` would be a
second copy of state → disqualified by L597–599; donor/pairing state for the
swap is verifier-side. No permitted or structurally required unoperated
second information path was found in the paper contract.

### 7.4 Axis-C verdict

`PERSISTENT_STATE_CONTRACT_PAPER_COMPLETE_CONDITIONAL` — the admission rule
is fail-closed on undeclared state; implementation absence is unverified.
Not `M_S_INVALID_RAW_HISTORY_OR_STATE_BYPASS`: no unoperated second path is
permitted or required by the paper.

## 8. Paper-level hostile ablations (CARD §9)

Semantic counterexample tests only; nothing was run.

1. Remove the public channel identity: exact Bayes collapses to the
   anonymous-bits mixture with accuracy 3/4 (PRE §4.2 L170–176, frozen source
   readback; single-point logic re-derived). The design degrades to a
   different, non-calibratable instrument — confirming `chi` is load-bearing
   declared schema, not decoration. Consistent rename changes nothing (5.3).
2. Vary the private target with the public interface frozen: no public code
   tracks the target (5.4). Passes.
3. Delete a record and require full normal recompute: `rel_delete` output
   `{e_Y0, e_S}` (or `{e_Y0}`) is a natural-support member of `E_cal`;
   recompute gives `b=1/2` through the normal path (PRE §9, §12, §14.3).
   Passes.
4. Add one undeclared persistent path: the implementation ceases to be an
   M-S subject (L597–599); §18 stop conditions fire; admission fails closed
   at paper level. Passes as a contract; absence in a real process remains
   unverified (7.2).

## 9. Precedence application and overall verdict (CARD §11)

1. Source/scope/independence failure — none (Sections 1–3). Not triggered.
2. Axis A `PUBLIC_CHANNEL_ENCODES_RELEVANCE` — not returned.
3. Axis B `M_S_INFEASIBLE_M_H_ONLY` — not returned.
4. Axis C `M_S_INVALID_RAW_HISTORY_OR_STATE_BYPASS` — not returned.
5. Any axis underdefined — no primary axis verdict is an underdefined
   verdict. The Axis-B qualifier `LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED`
   does not trigger this row: CARD §11 explicitly provides that this
   qualifier coexists with a conditionally acceptable analytic calibration
   and "must [be] preserve[d] ... as an explicit blocker even if analytic
   calibration is conditionally acceptable". Preserved in Section 11.
6. All axes conditionally acceptable — YES.

Overall verdict:

```text
PAPER_INSTRUMENT_CONTRACT_AUDIT_PASS_FOR_ANALYTIC_CALIBRATION_ONLY
```

This label is paper-contract level only. It does not authorize
implementation, Gate M execution, learned-candidate work, or route mutation.

## 10. Fact / derivation / inference / assumption / unknown ledger

Fact:
- All source pins verified byte-exact (Section 2 table; Section 14 readback).
- The prereg's own external status is `PAPER_UNDERDEFINED /
  REPAIR_PENDING_REAUDIT` pending independent formal-consistency re-audit
  (PRE §17 L1420–1422); no formal-re-audit artifact is pinned in this task.
- The access matrix classifies lineage, source UID, relevance role, target,
  and `J` as candidate- and baseline-invisible (PRE §15).
- The support quantifier is declared marginal with an explicit anti-joint
  argument (PRE §12); learned coverage standards are declared unfrozen.
- The state inventory carries a universal fail-closed disqualification
  clause (PRE §8.2 L597–599).

Derivation (auditor's own, paper-level):
- Absent `chi`, the two outcome records are candidate-exchangeable within an
  episode (Section 5.2).
- Operator closure of `E_cal` under delete/sham/restore/patch/swap
  (Section 6.2).
- Under the deterministic declared writer, joint `(H_legal, M')` support
  collapses to the intact state (Section 6.1 item 5).
- Spot re-derivation of the canonical branch outputs and
  `D_rel=1/2, D_sham=0, LSE_J=1/2` (Section 6.3; confirms frozen readback).

Inference:
- `chi_D/chi_S` is intensionally a variable-identity code (renaming- and
  target-invariant), and therefore legal public causal semantics under the
  paper's own §4.2 distinction; the extensional relevance coincidence is an
  environment-size artifact capped by the claim ceiling (Section 5.5).
- Admission-by-exclusion plus freeze-before-run constitutes a fail-closed
  paper contract for Axis C (Section 7).

Assumption:
- The host git view is authoritative over FUSE-mount churn artifacts (repo
  protocol); content hashes used for all decisive checks make this
  assumption non-load-bearing for the pins.
- The operator-supplied audit-card SHA-256 is the intended card pin.
- The frozen SCM specification is public to candidate and baseline exactly
  as the access matrix declares (PRE §15 L1365); if a future implementation
  hides the SCM spec from baselines, the Axis-A adjudication must be redone.

Unknown / unverified:
- Whether any implementation obeys the declared interface and inventory
  (implementation-level bypass absence).
- Whether learned/hybrid coverage standards, once frozen, will be adequate.
- The provenance of the reported formal-consistency re-audit
  (`FORMAL_REAUDIT_PROVENANCE_UNAVAILABLE_IN_THIS_TASK`).
- All empirical outcomes of Gates M, P, X; every candidate-specific
  direction, SESOI, sample size, threshold.
- Whether the independent banking decision will accept this report.

## 11. Blocking and non-blocking findings

Blocking (for any successor step, per the stated condition; none blocks this
report's verdict):
- B-1 `LEARNED_CANDIDATE_SUPPORT_UNDERDEFINED` (Axis-B qualifier, preserved):
  no learned or hybrid candidate execution until candidate-specific coverage,
  representation, and policy-conditioning evidence standards are frozen in a
  separate card (PRE §12 L857–861, §22.4).
- B-2 Implementation-level bypass absence is unverified: any future
  implementation card must provide a process-level persistent-state
  inventory, absence manifest, and positive-control leak scan before any M-S
  claim (PRE §14.7#3 L1293–1295, §22.3; CARD §8.3).
- B-3 Formal-consistency re-audit provenance is not pinned in-repo: before
  any successor card cites the 512-row review as independently cleared, its
  artifact must be pinned (commit/blob/SHA-256). This audit neither performed
  nor cleared that review; PRE §17's external status is not upgraded by this
  report.

Non-blocking:
- N-1 Vocabulary: "sham"/"diagnostic" are evaluator-perspective names inside
  the paper; harmless at paper level (renaming-invariant), but the
  implementation card should state that candidate-visible encodings are
  opaque code points and that these strings never appear in any
  candidate-visible field, filename, or fixture name (repo anti-hardcoding
  rule on label leakage through names).
- N-2 Patch/swap operators are outside the canonical `BranchSemantics`
  function by design; their admissibility/reason-code bookkeeping must be
  frozen in any future execution card (PRE §11.5–11.6, §16).
- N-3 The §8.2 inventory covers encoder/feature caches, episode/replay
  buffers, wrapper/adapter state, process globals, and cross-episode state
  only via the universal clause; the future implementation card should
  itemize the CARD §8.2 list by name.
- N-4 Environment: FUSE-mount ` M` churn on unrelated paths and a possible
  stray `.git/index.lock` (Section 2); operator-side cleanup note only; no
  content effect on pinned files (hash-verified).

## 12. Minimal repair requirements

Not applicable. Per CARD §12 item 11, repair requirements are stated if and
only if the verdict requires revision; the overall verdict does not.
Findings N-1..N-3 are forward requirements on future cards, not repairs of
the frozen source, and do not authorize any edit to `001B`.

## 13. Claim ceiling and what this does not prove

Claim ceiling (maximum favorable claim, per CARD §16):

> The frozen preregistration's channel-identity, state-support, and
> persistent-state admission rules survived a bounded independent
> paper-level hostile audit for later analytic instrument calibration,
> subject to explicit implementation-conditional blockers (B-1, B-2, B-3).

This audit does not prove:
- that any implementation satisfies the contract, or that any real process
  lacks a bypass;
- that the instrument is empirically valid;
- that any candidate state is load-bearing;
- that a learned update exists or is on-support;
- that Gate M, Gate P, or Gate X passed, or any empirical branch contrast;
- baseline non-equivalence or a unique mechanism (a legal-history
  lookup/table Bayes controller is expected to match canonical behavior and
  caps all claims; PRE §4.1, §19.1);
- formal consistency of the 512-row enumeration (not re-audited here;
  provenance unavailable in this task);
- any upgrade of the prereg's external status in PRE §17 (a separate
  operator banking/clearance decision);
- agency, autonomy, selfhood, subjectivity, consciousness, real emotion,
  functional-subject status, EGO readiness, mainline effect, runtime
  readiness, companion readiness, or user benefit.

## 14. Final exact-path scope readback

Read-only pin/scope commands rerun during report finalization (verbatim outputs):

```text
$ sha256sum docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md \
            docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md
d0d078abce8622fb7c8c492497e849e14bef886012e60a15ae20684530146454  docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md
fc8555c6cd19c34338fe365a3695718b3de862bfd001e6c94f7c7f1f54f86d6f  docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md

$ git hash-object docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md
1e5f7e10170d07a02bc4799dc5d28003fcf8ab8f

$ git rev-parse HEAD
d519a84fb0891bca17edd4e605a0e3cb066ecc7d

$ git --no-optional-locks status --porcelain -- \
      docs/codex/tasks/FORK-A-IIO-MCI-PREREG-001B.md \
      docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md \
      docs/research/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md
?? docs/codex/tasks/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md
?? docs/research/FORK-A-IIO-MCI-INSTRUMENT-VALIDITY-AUDIT-001A.md

```

Readback interpretation:
- The frozen prereg re-hashes to its pinned SHA-256 and blob id after the
  audit: source not modified.
- The audit card re-hashes to its operator-pinned SHA-256: card not modified.
- HEAD unchanged and equal to the frozen source commit.
- The only paths reported for this lineage are the pre-existing untracked
  audit card (`??`, present before this audit began) and this report (`??`,
  the single authorized addition). No tracked file was modified by this
  audit; no stage/commit/push/tag/anchor was performed.
- Pre-existing repo-wide ` M` churn entries on unrelated paths (including
  other `docs/research/` files) were visible in the sandbox mount both
  before and after this audit; they are FUSE line-ending/staleness
  artifacts, none of these files were opened for writing by this audit, and
  the host git view remains authoritative.
- A stray zero-byte `.git/index.lock` (created by a read-only `git status`
  on the no-delete mount, timestamped during this audit) remains for
  operator-side cleanup; the auditor cannot and did not delete it.
- Stop conditions triggered: none.
