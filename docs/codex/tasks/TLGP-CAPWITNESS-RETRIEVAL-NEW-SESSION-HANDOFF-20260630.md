# TLGP Capability-Witness / Retrieval-Runner — New Session Handoff (2026-06-30)

## 0. TL;DR (the pivotal turn)
The TLGP capability-witness line looked **dead** ("family/learnability-limited") across four
probes. A **positive control** then caught the real problem: the frozen "in-context"
learners in `src/tlgp_001b_r2/meta_learners.py` **mean-pool the adapt set** (GRU `hn[-1]`,
Transformer `.mean(dim=1)`, MLP `cat[mean,std]`) — the query never attends to per-example
adapt tokens, so they **cannot do in-context retrieval/inference**. A new **retrieval
architecture** (query attends to per-example adapt tokens, no pooling) then **passed** the
real rung0 seen-rule capability witness: 0b heldout ≈ 0.95 on 3 seeds (bar 0.90, fair 0.23,
query/adapt overlap ~4% = genuine inference, no leakage). **⇒ Every prior capability-witness
negative + the TLGP-R2 floor failure were CONFOUNDED by a pooling-architecture artifact, not
a learnability limit. The route reopens.** Claim ceiling: this is rung0 = SEEN rules (the
prerequisite), a 3-seed TREND — NOT transfer. rung3 (unseen rules + the identifiability
ceiling) is untested and is the real question.

> IMPORTANT: The assistant that wrote this verified the load-bearing claims against git
> objects. Still, treat any commit/sha/number below as readback — a new session should
> re-verify from the live repo before acting (that discipline is exactly what saved this line).

## 1. Current repo state
- Repo: `D:\Project\AIProject\MyProject\intelligence-theory-lab` (if a session opens in
  `...\Ego`, switch to ITL first).
- Branch: `codex/meta-theory-scaffold`. HEAD: `9e3e3d2705426f10093b8ae76949f55d3028fbf4`.
  Ahead of origin by local commits; **no push has been done in this whole line** (remote is
  BLOCKED until `scripts/push.*` hardcoded-PAT is rotated).
- Banked lineage (oldest→newest):
  - `b4ee157` devbench 001A-001D
  - `63d5177` TLGP-001B-R2 INVALID (learnability-floor) — **now known to be a pooling artifact**
  - `3d5e88e` capability-witness preflight: minimal + grokking-001A (trend evidence)
  - `d4f1430` grokking_probe behavior-preserving parameterization
  - `2de7fef` grokking-001B closeout (ambiguous/negative-leaning)
  - `2c3f00f` grokking-001B curve/config audit
  - `9e3e3d2` **positive control — runner_copy_fail (HEAD)**
- **Uncommitted and needing a bank** (staged `A`/`AM` but not committed):
  - `src/tlgp_capability_witness_preflight_001a/retrieval_model.py` (the fix; sha `0cba9239`)
  - `src/tlgp_capability_witness_preflight_001a/icl_retrieval_runner.py`
  - `src/tlgp_capability_witness_preflight_001a/rung0_retrieval_rerun.py`
  - `artifacts/.../ICL_RETRIEVAL_RUNNER_001A/` (runner_ok) and `.../RUNG0_RETRIEVAL_RERUN_001A/`
    (witness_trend_pass)
  - `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A.md` + `.frozen_design.json`
  - `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A.frozen_design.json` (frozen `69e86cb1`)
- Cosmetic-only: several banked artifact files show ` M` — that is EOL/LFS churn from the
  mount (`git diff --ignore-all-space` empty); do NOT "fix" or commit it. Judge banks by exact
  staged allowlist, not overall untracked/churn noise.

## 2. Key anchors (verify before use)
- Frozen prereg: `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`
- `route_decision.py` (self-tested, all 6 terminals fire): `0dcf3659…`
- Validated retrieval model `retrieval_model.py`: `0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb`
- Frozen designs: positive control `90f2a503…`; rung0-retrieval-rerun `e917ad29…`;
  rung0-POWERED `69e86cb1df0f29c60f0d9d3046ea65e13a246a1d809a1afb8139bc6019ae5cb8`
- Protected/untouched: `meta_learners.py` `358d2bb2…` (the pooling source — do NOT edit; it is
  banked TLGP-R2 + prereg-frozen).

## 3. What is verified vs the claim ceiling
Verified (independently, from git objects + artifacts):
- The pooling root cause (`meta_learners.py` forward lines: `hn[-1]` / `mean(dim=1)` / `cat[mean,std]`).
- Positive control: PC_COPY train→1.0 / heldout 0.65 (memorizes episodes, can't retrieve);
  PC_SINGLE_RULE=1.0. Construction valid (query⊆adapt for copy).
- Retrieval fix: PC_COPY=PC_SINGLE_RULE=1.0 at step 2000; architecture confirmed no adapt pool,
  query reads per-example tokens; banked source untouched.
- rung0 rerun: 0b 0.962/0.948/0.949 (3 seeds), overlap ~4% (real inference), no rule_id/query_e
  leakage, same model sha, fair 0.23; verdict `witness_trend_pass`.

Claim ceiling (do NOT exceed):
- 3-seed **trend** (`route_decision=inconclusive_underpowered`), not a formal terminal.
- rung0 = **SEEN** rules (prerequisite / capability witness), **NOT transfer**. The model likely
  passes by recognizing which of 8 seen rules from adapt + applying it.
- **rung3 (unseen rules/values) — the real transfer question and where the identifiability
  ceiling lives — is completely untested.**
- Nothing here is mechanism/agency/self/subjectivity/AGI/EGO evidence.
- The banked `63d5177` TLGP-R2 INVALID still stands as a bounded fact ("those frozen pooling
  architectures failed rung0"); its broad interpretation ("neural meta-learning can't") is now
  known wrong (architectural, not learnability).

## 4. Immediate queue (in order)
1. **Bank the fix + rerun** (currently uncommitted). Scoped commit; see §6.A.
2. **Powered rung0** (10 seeds → formal terminal via unmodified `route_decision.py`). Frozen
   design `69e86cb1`; ready prompt in §6.B. Turns the trend into a bankable pass.
3. **rung1** (seen-rule eligibility, disjoint episodes) — draft after powered rung0 passes.
4. **rung3** (unseen rules + unseen values = the actual transfer test). This is the real
   experiment; design it carefully — the identifiability ceiling (learner-independent) is the
   open wall here. A retrieval model that passed rung0 by "recognize 1-of-8 seen rules" may fail
   rung3, where it must infer NOVEL rule parameters.

## 5. Two standing policy decisions (from this session)
- **Positive control before interpreting negatives (make it a rule).** We ran four negative
  probes and nearly closed the route before a positive control revealed a broken instrument.
  Any instrument that produces interpreted (esp. negative) evidence must first pass a positive
  control ("can it detect a signal that exists?"). Do NOT do a big upfront calibrate-everything
  sweep; calibrate-on-use, and prioritize now only instruments whose old negatives still drive a
  live decision. (`route_decision.py` and the leakage detector already self-test.)
- **Re-test mis-judged theories selectively, not wholesale.** Re-test iff (a) the conclusion was
  "a learner can't learn/represent/beat-baseline" AND (b) it used the pooling metas (or another
  unvalidated instrument) AND (c) it still matters. Do NOT re-test structural findings — the
  **identifiability ceiling** (equal-access saturation) and the self-boundary killers
  (K1 obs-decodability / K2 interventional saturation) are learner-independent and are NOT
  confounded by this. Fixing the instrument reopened only the *learnability* sub-question; the
  identifiability wall still stands at rung3.

## 6. Ready-to-use

### 6.A — Bank fix + rerun (Codex, local, no push)
Guardrails: explicit-path staging only, no `git add -A`; no edit to `src/tlgp_001b_r2/*` /
`src/tlgp_001a/*`; `route_decision.py`=`0dcf3659`, `meta_learners.py`=`358d2bb2` unchanged;
`.jsonl` stage as LFS pointers (the `**/*.jsonl` rule already exists); no non-LFS blob >10 MB;
no push.
```
git add -- src/tlgp_capability_witness_preflight_001a/retrieval_model.py \
           src/tlgp_capability_witness_preflight_001a/icl_retrieval_runner.py \
           src/tlgp_capability_witness_preflight_001a/rung0_retrieval_rerun.py \
           artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/ICL_RETRIEVAL_RUNNER_001A/ \
           artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG0_RETRIEVAL_RERUN_001A/ \
           "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A.md" \
           "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A.frozen_design.json" \
           "docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A.frozen_design.json"
```
message: `docs(bank): TLGP retrieval runner_ok + rung0 witness_trend_pass (prior negatives were a pooling artifact)` — body: retrieval arch passes positive control (PC_COPY=PC_SINGLE_RULE=1.0) and clears real rung0 (0b 0.96/0.95/0.95, bar 0.90, fair 0.23, overlap 4% genuine inference, no leakage); prior capability-witness negatives + TLGP-R2 floor were CONFOUNDED by the meta_learners mean-pool bottleneck, NOT a learnability limit; bounded TREND (3 seeds, route_decision inconclusive_underpowered), rung0=SEEN prerequisite NOT transfer; not mechanism/agency/self/AGI/EGO; shas retrieval_model 0cba9239 / rerun design e917ad29 / prereg 6e61a831.

### 6.B — Powered rung0 (Codex, GPU) — formalize the trend
Frozen design: `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG0-POWERED-001A.frozen_design.json`
(canonical sha `69e86cb1`). NEW file `rung0_retrieval_powered.py` reusing rung0 construction +
`_eval_checkpoint` + retrieval model READ-ONLY; 10 prereg seeds [20260710..20260719]; compute
ideal + fair baselines incl **graph_cache** + leakage + MDE/power; build `route_decision_input.json`
= {rung:"rung0", ideal_balacc, fair_baseline_balacc{…incl graph_cache}, learner_per_seed_balacc:
{"retrieval_model":[10×best 0b]}, n_seeds:10, leakage_clean, headroom_power:{"retrieval_model":
{passes_power}}}; run the UNMODIFIED `route_decision.py` → the formal terminal (expect
`route_open_capability_witness_feasible` if 0b≥0.9 on ≥9/10 with power-backed headroom over
fair+graph_cache and leakage clean). Emit under `.../RUNG0_POWERED_001A/`; STOP at the verdict;
no commit, no audit layers, no push. (Full prompt was provided in chat; regenerate from the
frozen design.)

## 7. Standing constraints / lessons (read before acting)
- **Verify, don't trust readback.** Every milestone here was independently re-checked against git
  objects/artifacts; that caught the copy-vs-inference and behavior-preservation questions.
- **Freeze design + record canonical sha BEFORE reading results** (anti-tuning). All probes did this.
- **STOP means STOP.** Codex has twice over-built (auto-committed 001B, added closeout/curve-config/
  operator-review layers with self-rewriting scripts). Prompts must say: emit artifacts, do NOT
  commit, do NOT add audit/review layers, do NOT push. Do not bank self-rewriting review scripts.
- **Never edit banked/frozen source** (`meta_learners.py`, `route_decision.py`, prereg, any
  `src/tlgp_001b_r2/*`, banked probe runners). New work = new files/families. If reuse needs a
  banked-file edit, STOP and do a separate behavior-preserving parameterization commit (verified),
  never in the same commit that banks executed evidence (the TLGP-B2 trap).
- **Hairline thresholds**: three probes landed "ambiguous" on ~0.001 threshold edges; prefer
  fit-conditioned / substantive reads and don't over-index on the label.
- Git/LFS: banked large traces use LFS (`**/*.jsonl` rule); commit pointers, never inline;
  scoped `git add` only; local commits only (remote blocked).
- Detailed running log lives in the assistant's memory index (very long entry under the
  ITL-DEV-BENCH/TLGP CURRENT FRONT pointer).

## 8. The real open question
Even after the instrument fix and a formal rung0 pass, the line's outcome is undecided. The
genuine test is **rung3 (unseen rules/values)**: can a working in-context learner infer NOVEL
rule structure and generalize — beating a fair meta-baseline — or does the **identifiability
ceiling** (equal access ⇒ baseline gets the same identifiability) reassert itself? That, not
rung0, decides whether this route yields mechanism-relevant evidence.
