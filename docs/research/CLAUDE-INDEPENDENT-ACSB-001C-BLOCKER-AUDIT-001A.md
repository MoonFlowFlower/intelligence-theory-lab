I'll start by verifying the canonical repo state and locating the 001C artifacts, while loading the task tracker. This is a read-only audit — I won't modify, rerun, or repair anything.Git failed (known FUSE `.git/config` ENOENT issue in this mount). Let me work around it and set up the audit task list.Canonical file-level state confirmed (branch ref = `5896d01`). Now reading the high-signal small artifacts.Top-level artifacts look internally consistent. But the verdict is a *blocker* — its validity hinges on whether the fitted learner wins by legitimate legal features or by leakage, and whether the reference=1.0 is a real mechanism or just the label-generation rule. That can only be resolved in the source. Let me read it.The core is `runner.py` (1647 lines). Reading it in full — this is where the blocker's validity lives.Read needs the Windows path. Let me use it.The mechanism is now visible and it's decisive. The target is constructed first, then encoded into `channel_evidence` as a static per-channel count signature; the "reference" path's boundary memory is initialized to all-zeros and never carried across episodes, so it reduces to a static argmax over those same counts. Let me read the remaining helpers to confirm `_evidence_scores`, the learner feature extractors, target generation, and the split audit.Full mechanism confirmed in source. Now the verification step: I'll confirm my source reading matches the actual committed artifacts (real run, not just code), and empirically verify the target-encoding claim against `episodes.json`.All code-derived claims are now empirically confirmed against the committed artifacts. The audit is conclusive on read-only evidence — no probe needed.## 中文执行摘要

**结论:001C blocker 无效,判定 `blocks_on_reference_or_capacity_mismatch`,路线建议=否决该 blocker(不要据此关闭或降级 ACSB)。**

核心一句话:被当作"ACSB 参考"的 `boundary_update_reference_path`,其 boundary memory 在全部 32 个 heldout episode 上**实测恒为全零、update_rate 恒为 1.0**,所以它在数学上退化为 `argmax(self−no−ext)` 这个静态观测解码器——它根本不是动作条件自边界机制,只是戴着 "uses_persistence: True" 标签的目标解码规则。于是"无边界学习器追平参考"这件事,是两个静态解码器在一个**目标被写进观测**(target 行恒为 `{self=3,no=0,ext=0}`,100% 可解码)的退化任务上打平,完全不能支撑"ACSB 不可判别"这一主张。001C 确实修好了 001B 的"假学习器"缺陷(这次学习器真在拟合),但把一个无效换成了另一个无效。

下面是可入库引用的正式审计报告(英文,遵循仓库文档约定)。

---

# CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A — Final Report

**Verdict:** `claude_independent_acsb_001c_audit_blocks_on_reference_or_capacity_mismatch`

**Current layer:** engineering-governance / independent hostile audit of the 001C blocker only.

**Mainline integration status:** none.

**Enabled status:** none beyond the local offline module/tests/artifacts already reported by 001C. This audit performed read-only inspection plus a read-only deterministic recomputation over existing artifacts; it did not rerun, repair, or modify the experiment.

**Real trigger evidence (audited):** canonical commit `5896d01…` confirmed (branch ref `codex/meta-theory-scaffold` = `5896d01f355d147075dcf15901d5111471d3010e`). 001C `result.json` reports reference `1.0`, `fitted_linear=1.0` (1 update), `fitted_sequence=1.0` (32 updates), `fair_capacity_disabled=0.0`, `fsm=0.25`, leakage 6/6 blocked, replay/provenance passed, verdict `blocked_by_fitted_no_boundary_learned_baseline_001c`. All reproduced from artifacts.

**Claim ceiling:** independent blocker-audit verdict only. This audit does not claim mechanism validity, mechanism invalidity beyond this bounded surface, Gate validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, runtime/EGO readiness, stable user benefit, or mainline effect.

## Audited files / artifacts
- `src/action_conditioned_self_boundary_executable_preflight_001c/runner.py` (1648 lines, read in full)
- `tests/test_…_001c.py` (header/contract reviewed)
- artifacts: `result.json`, `scores.json`, `baseline_comparison.json`, `ablation_report.json`, `episodes.json`, `learner_validity_controls.json`, `leakage_scan.json`, `replay_report.json`, `provenance.json`, `failure_manifest.json`, `source_boundary_readback.json`, `summary.md`, `claim_ceiling.txt`
- Read-only recomputation over `episodes.json` (decode check, memory-state check, split-disjointness check).

## Strongest support for the 001C blocker
The learners are now genuinely fitted (real perceptron over 8 epochs; real sequence-weight accumulation), guarded by `fit_called`, `zero_update`, `constant_predictor`, and a `fit_removed` mutation control that raises if inference precedes fit. They consume only non-forbidden-named observation fields; the name-based leakage scanner blocks 6/6 named positive controls; replay recomputes from state+observation without reading stored verdicts/scores; provenance ties every score to a callable path with input hashes and update counts. On its literal contract — "a truly fitted no-boundary learner reaches the reference score on held-out legal inputs" — the run did execute and the learner did reach `1.0`. This is a **real fix of the specific 001B defect** (001B's "learned" baselines were deterministic, `ml_library_used=False`, no fit).

## Strongest objection to the 001C blocker (decisive)
The "reference" the learner allegedly replaced is **not an operative ACSB mechanism**, and the held-out task **encodes the target inside the legal observation**. Both were verified empirically, not just read:

1. **Reference is inert / mis-specified (load-bearing).** `boundary_update_reference_path` computes `updated[c] = update_rate·evidence[c] + memory[c]`. Across all 32 held-out episodes, `boundary_update_memory` is `{all: 0.0}` and `update_rate` is `1.0` (recomputed). So the persistence/memory term contributes nothing and the reference reduces exactly to `argmax(self_action − no_action − external_effect)` — a static, single-observation decoder. Its `uses_explicit_boundary_update: True` / `uses_persistence: True` diagnostics are renderer-only labels with zero causal effect. You cannot demonstrate "ACSB is not discriminative" with a reference in which the action-conditioned self-boundary state is provably never used.

2. **Target is a deterministic observation artifact (leakage by value).** `_build_observation` writes the target channel's evidence row as a constant signature `{self=3, no=0, ext=0}`. Recomputation: the target-row signature set across all held-out episodes is exactly `{(3,0,0)}`, and `argmax(self−no−ext) == target` on **100%** of held-out episodes. `_linear_channel_features` even exposes a `"contrast" = self−no−ext` coordinate — i.e. the reference's entire decision statistic is handed to the learner as one feature, which is why the linear model converges in a single update. The match is **constructed equivalence**, not discovered equivalence.

3. **Fair-capacity-disabled reference is rigged, not fair.** `fair_capacity_boundary_disabled_reference = argmax(self_action + external_effect)`. By the constructed signatures the decoy row is `{5,3,2}` (highest `self_action`), so this formula selects the decoy on every episode → `0.0`. It is reverse-engineered to fail, the same crippling family as 001B's `stale_prior`, merely relabeled (`returned_stale_prior_channel: False` is technically true but evasive).

4. **Leakage scanner is structurally unable to fail on the real leak.** `scan_legal_input_for_leakage_001c` matches **key names / string fragments** only. The actual leak is in observation **values** (the count signature). 6/6 "blocked" controls are all name-injections; none probes value-recoverability. The scanner cannot detect the leakage that voids the blocker.

5. **Split non-overlap is cosmetic.** `combo_key[0]` is the split label (`"train"`/`"heldout"`), so `train_combos ∩ heldout_combos = ∅` is structurally guaranteed (recomputed: empty). The decode rule is identical across splits, so held-out requires no generalization beyond the fixed decode. `target_is_fixed_index_rule` is hard-coded `False`, yet `_target_for("heldout", …)` is literally `CHANNELS[[0,2,1,3,2,0,3,1][index%8]]` — a fixed index rule.

## Per-question answers
1. **Fitted?** Yes — real perceptron/sequence fitting with guards. (Genuine 001B fix.)
2. **Update counts real?** Yes, tied to weight changes. Linear shows `1` because the `contrast` feature makes the problem linearly trivial, not because fitting is fake.
3. **Legal inputs only, or target leakage?** Name-level clean; **value-level leaked** — channel_evidence deterministically encodes the target.
4. **Unfair extra info vs reference?** No — learner and reference see the same observation. The leakage is **shared**, not asymmetric (this is why the verdict is reference-mismatch, not "unfair access").
5. **Split real or cosmetic?** Cosmetic where it matters; disjointness guaranteed by the split label; identical decode rule both sides.
6. **Target recoverable from fixed rule/artifact?** Yes — fixed index sequence + constant `{3,0,0}` observation encoding; decodable on 100% of held-out.
7. **Solves by legal evidence or leakage?** By reading the label-encoding count values; `_run_feature_removal_control` actually *confirms* dependence on those encoding features (drops to 0 when no/ext removed).
8. **Reference meaningful ACSB or target-gen rule?** **Target-decode rule.** Boundary state provably inert ⇒ not operatively ACSB.
9. **Capacity-disabled reference fair?** No — `self+ext` formula deterministically selects the decoy ⇒ rigged 0.0.
10. **Ablations non-constant reruns?** Mechanically yes (4 unique preds, deg 0.656–1.0), but they perturb observation values, testing a static decoder's knobs, not a boundary process.
11. **Leakage controls detect the leak?** Only name-based leaks (6/6); structurally blind to the value-encoded target — the real leak.
12. **Replay from serialized state?** Yes, and it avoids stored verdicts — but it is a determinism/idempotence check (`f(x)==f(deepcopy(x))`), a weak replay (non-blocking).
13. **Provenance real?** Yes for what it covers (callable scores, hashes, IDs, update counts); out of scope for reference-mismatch / value-leakage.
14. **Tests fail under dummy learner / constant predictor / fixed-token ablation?** Yes for those specific substitutions (real guards). **No** test guards the inert-reference or encoded-target defects.
15. **Justify closing/downgrading ACSB?** **Neither.** The blocker is an artifact; it requires a corrected challenge, not a verdict on ACSB.

## Assessments (summary)
- **Learner validity:** valid fitting; genuine 001B fix. Not the problem.
- **Train/heldout split:** cosmetic non-overlap; mislabeled `target_is_fixed_index_rule=False`. Blocking.
- **Leakage:** value-encoded target present; scanner name-only and non-fail-able on the real leak. Blocking.
- **Reference/capacity:** reference inert (not ACSB); capacity-disabled reference rigged to 0.0. **Primary blocking.**
- **Ablation:** real reruns but test a static decoder, not boundary state. Non-blocking weakness.
- **Replay/provenance:** mechanically real but a weak determinism check; cannot detect the voiding defects. Non-blocking.
- **Test strength:** guards the 001B failure family only; blind to the 001C voiding defects. Blocking.

## Recommended route — **block the blocker as invalid**
Do **not** cite 001C as "ACSB surface not discriminative under true-learned/fair-capacity challenge," and do **not** close or downgrade ACSB on this basis. (Symmetric caution: this also does **not** validate ACSB — it voids the test.) The 001C negative evidence is an artifact of (a) a reference whose boundary state is never exercised and (b) a target encoded into the observation.

Minimal requirements for any successor before a blocker may stand: a reference that **operatively** depends on boundary memory/persistence on a task where the decision is **not** statically decodable from a single observation (temporal/action-contingency structure that carries the answer only across steps); a **value-level** leakage probe (e.g. fit a label-only decoder on the legal observation — if it reaches ≈1.0, the observation leaks the target); a split-overlap check that does **not** include the split label in the key; and a fair capacity-reduction that lowers the reference's expressiveness without being reverse-engineered to select the decoy.

**Implementation may proceed?** No implementation is authorized by this audit (audit-only task). A new bounded task card is required for any corrected challenge.

## What this cannot prove
That ACSB is discriminative or valid; that ACSB is invalid (001C is void, not negative); anything about mechanism validity, Gate validity, candidate behavior, agency, autonomy, consciousness, emotion, subjectivity, runtime/EGO readiness, stable user benefit, or mainline effect. Bounded strictly to: **the 001C blocker, as constructed at `5896d01`, does not validly support its stated claim, for the reference/capacity/leakage/split reasons above, verified by read-only artifact recomputation.**

---

I can persist this as `docs/research/CLAUDE-INDEPENDENT-ACSB-001C-BLOCKER-AUDIT-001A.md` and anchor it via your push flow if you want it in the evidence lineage — say the word and I'll do exactly that and nothing more.