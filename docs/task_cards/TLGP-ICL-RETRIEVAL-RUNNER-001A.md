# TLGP-ICL-RETRIEVAL-RUNNER-001A

> Status: DRAFT implementation card. Builds a NEW retrieval-capable in-context model
> (NEW architecture / NEW family / NEW file) and validates it against the FROZEN
> positive control (design sha `90f2a503…`). It must achieve `runner_ok`. This does
> NOT edit banked `meta_learners.py` / TLGP-R2 / `positive_control.py`, and is NOT a
> TLGP-R2 frozen family — it does NOT change any banked TLGP-R2 verdict.

## Verified root cause (code-level)
All three TLGP "meta-learners" collapse the adapt context into a fixed summary
vector before the query is applied; the query never attends to individual adapt
examples (`src/tlgp_001b_r2/meta_learners.py`):
- `InContextGRU.forward`: `self.head(hn[-1], qx)` — GRU last hidden = summary.
- `InContextTransformer.forward`: `self.enc(...).mean(dim=1)` — mean-pool = summary.
- `AmortizedSummaryMLP.forward`: `cat([ctx.mean, ctx.std])` — explicit summary.
- `QueryHead.forward(summary, qx)`: the same summary is broadcast to every query;
  the query has NO path to attend to per-example adapt tokens.

Consequence: these families CANNOT do per-example retrieval or per-example in-context
inference. PC_COPY fails (retrieval impossible), PC_SINGLE_RULE passes (weight-space
memorization of a fixed rule), and the capability-witness negatives + the TLGP-R2
floor failure are CONFOUNDED by this architectural bottleneck, not a learnability limit.

Task id: TLGP-ICL-RETRIEVAL-RUNNER-001A

Problem definition: build a true in-context / retrieval architecture in which the
query attends to per-example adapt tokens, and validate (on the FROZEN positive
control) that it can both retrieve (PC_COPY) and represent (PC_SINGLE_RULE). This
repairs the instrument so that any subsequent capability-witness result is
interpretable. No probe re-run in this card.

Layer: engineering implementation (instrument repair) + candidate-free validation.
NOT a TLGP route terminal; does NOT alter banked TLGP-R2/probe verdicts.

Bounded architecture (the fix): a sequence-token in-context transformer — embed each
adapt example as a token carrying (x, a, e), and the query as a token carrying (x, a);
run a transformer with self-attention over the sequence [adapt_1 … adapt_n, query],
and read the query token's output to predict e (K classes). The query token can thus
attend to (retrieve from) individual adapt tokens. Keep size comparable to the frozen
witness (d_model ~256, layers ~4, heads ~4) so a later fair comparison is possible.
Standard causal/full self-attention is fine; document the exact tokenization.

Build instructions: add NEW files only —
`src/tlgp_capability_witness_preflight_001a/retrieval_model.py` (the model) and a NEW
validation runner that REUSES the frozen positive control's data construction
(`_make_copy_episode`, `_make_single_rule_episode`, `_make_control_episodes`) and
`_eval_checkpoint` from `positive_control.py` READ-ONLY (import; do NOT edit it),
swapping in the new model. Do NOT edit `meta_learners.py`, `grokking_probe.py`,
`route_decision.py`, the world, or any `src/tlgp_001b_r2/*` / `src/tlgp_001a/*` byte.
If reuse requires editing a banked file, STOP and report (do not auto-edit).

Acceptance gate (pre-declared; reuse the FROZEN positive-control go/no-go, design
sha `90f2a503…`, run on the SAME PC_COPY + PC_SINGLE_RULE, seeds [20260710,20260711],
≤20k steps): the new model must reach
`runner_ok` = PC_COPY heldout ≥ 0.95 (all seeds) AND PC_SINGLE_RULE heldout ≥ 0.85
(all seeds).
- runner_ok → instrument repaired → authorize a SEPARATE follow-up card to re-run the
  capability-witness probes (rung0/rung1) with the new retrieval model.
- PC_COPY still < 0.95 → the new architecture also fails retrieval → iterate the
  architecture/tokenization (bounded) or report; do NOT proceed to probe re-runs.
- between → report curves, operator decides.

Required outputs under
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/ICL_RETRIEVAL_RUNNER_001A/`:
`training_records.json`, `val_curves.jsonl` (dense per-checkpoint train+heldout per
control/seed), `validation_report.json` (per-control/seed best heldout + ideal +
runner_ok/representational/copy_fail verdict, vs the frozen positive-control thresholds),
`model_card.json` (exact tokenization + arch + param count), `manifest.json`
(positive_control_frozen_design_sha256 = 90f2a503…, prereg_sha256 = 6e61a831…, git
HEAD/branch, GPU env, banked_source_diff_empty), `failure_manifest.json` if a stop fires.

Acceptance: 4 validation runs (PC_COPY + PC_SINGLE_RULE × 2 seeds) complete; dense
curves logged; gate applied vs the frozen positive-control thresholds; NO banked
source byte edited (shas match); new files only.

Claim ceiling: builds + validates a NEW in-context architecture's retrieval/representation
capability. Does NOT change banked TLGP-R2 verdict (those frozen pooling families
failed for the now-identified architectural reason). A `runner_ok` ONLY unlocks
re-running the capability-witness probes; it is NOT itself capability-witness,
transfer, mechanism, agency, self, subjectivity, AGI, or EGO evidence.

Process discipline: emit the artifacts, then STOP at the validation verdict. Do NOT
commit the artifacts (leave for operator/auditor verification). Do NOT add
closeout/curve-config/operator-review or any audit layers. Do NOT push. Do NOT
re-run the capability-witness probes from this card.

Stop conditions → failure_manifest.json: editing any banked file (meta_learners.py,
positive_control.py, grokking_probe.py, route_decision.py, src/tlgp_001b_r2/*,
src/tlgp_001a/*); tuning the acceptance thresholds; adding audit layers;
committing/pushing; re-running probes from this card.

Rollback: new files only (`retrieval_model.py` + the validation runner + the artifact
dir); revert = delete them. No banked file touched.

Forbidden: editing banked source/world/meta_learners/positive_control/grokking_probe/
route_decision; `AGENTS.md`/`CLAUDE.md`/global config; `scripts/push.*`; remote/push;
extra audit layers.

Auto-Remote-Anchor: forbidden.

Expected cost: building the model + 4 short validation runs (≤20k steps each) — about
a day of GPU. The positive control is the acceptance test.

## For Codex (execution)
Read this card + the positive-control card/frozen_design first. Build
`retrieval_model.py` (sequence-token in-context transformer; query attends to
per-example adapt tokens; document tokenization in model_card.json) and a NEW
validation runner that imports the positive control's data construction + eval
READ-ONLY and runs the new model through PC_COPY + PC_SINGLE_RULE (seeds
[20260710,20260711], ≤20k steps, checkpoint 2k). Emit the artifacts above, apply the
FROZEN positive-control go/no-go, and STOP at the verdict. Do NOT commit, no audit
layers, no push, no probe re-runs. Final report: per-control/seed best heldout +
ideal; runner_ok/copy_fail/representational verdict; param count + tokenization
summary; confirm no banked-source edit, nothing committed/pushed. Paste back for
closing verification.

## Collision Record
Approach A — edit the frozen meta_learners to add retrieval: rejected — banked TLGP-R2
source + prereg-frozen families; would corrupt the banked record.
Approach B — new retrieval model (new file/family) validated on the frozen positive
control before any probe re-run: selected.
Approach C — re-run the probes immediately with a new model, skipping the positive
control: rejected — that is the exact mistake we just caught (interpret before
validating the instrument).
Selected approach: Approach B.
