# TLGP-LEARNABILITY-FLOOR-DIAG-001

Full diagnostic = **NON-EXECUTABLE** until (a) Claude Red-audits the baseline-family + acceptance gate and (b) compute posture + budget line are authorized. Feasibility timing probe is the only pre-authorized next micro-step.

## task id

`TLGP-LEARNABILITY-FLOOR-DIAG-001`

## status

Executable-card draft + static compute-posture assessment only. This card does **not** authorize a full diagnostic run, a new mechanism, a new control implementation, GPU use, threshold changes, or any experiment execution beyond the separately stated timing-only feasibility probe.

## current stage / route context

- FSP ledger: `L-005` closed P0 / PUM-ENV as `INVALID_INSTRUMENT`; N1 admission = `NEEDS_ONE_MINIMAL_PROBE`.
- FSP ledger: `L-006` reconciled Fork-C / Track-T rung1 L-005 as already tracked; no new Track-T bank required.
- This card is the named minimal probe target for the remaining cross-episode learnability question.

## layer

Learning/adaptation diagnostic + route-admission evidence governance. It is not mechanism validation, subjectivity validation, EGO runtime work, or product work.

## claim ceiling

At most: bounded offline evidence about whether the prior TLGP-001B / TLGP-001B-R2 failure is better explained as a real learnability floor or as a positive-control / harness-design defect. It does **not** prove that any mechanism holds, that N1 is ready, that any theory is true or false, or that there is agency, autonomy, consciousness, emotion, stable user benefit, companion readiness, or EGO readiness.

## problem definition

TLGP-001B produced an invalid outcome because the capacity-positive control failed, while the H1-shaped real-task pattern was also present. The independent audit identified a likely design flaw: the CONTROL test task was byte-identical to the REAL unseen-rule task, so the "positive control" still required the same hard held-out-rule generalization it was supposed to deconfound. TLGP-001B-R2 then produced a bounded `invalid_learnability_floor` result under a CUDA-only official harness, but this does not yet answer the route-admission question against a deliberately fair cross-episode meta-baseline and a corrected fail-able positive control.

The diagnostic must answer only:

- **H0 floor:** the candidate family does not establish learnability / controllable-variable headroom once compared to strongest fair meta-baselines and corrected controls.
- **H1 defect:** the prior invalid result was primarily a positive-control / harness-design defect, and a corrected diagnostic shows candidate advantage over the strongest fair meta-baseline under held-out novelty with required ablation collapse and replay.

## formal object

Use `T=(S,O,A,M,U,J)`.

- `S`: latent task/rule/world state.
- `O`: observations / adaptation examples visible to candidate and baselines.
- `A`: permitted action / query / intervention policy.
- `M`: memory / cross-episode update state.
- `U`: update rule / learner state transition.
- `J`: scored judgment / prediction.

Nuisance variables: surface label, episode id, memorized-instance identity, fixture/file naming, and any value that makes the target directly decodable without the admitted update/intervention channel.

## source readback for 001B / 001B-R2

- TLGP-001B entry point: `PYTHONPATH=. python -m src.tlgp_001b.harness --full`; `src/tlgp_001b/harness.py:458-473`.
- TLGP-001B device posture: `src/tlgp_001b/meta_learners.py` selects `cuda:0` if available, otherwise CPU; `src/tlgp_001b/harness.py:330-336` warns the frozen full run is heavy on CPU. The banked 001B result reports `selected_device="cuda:0"`.
- TLGP-001B frozen scale: `batch_size=256`, `max_epochs=200`, `early_stop_patience=20`, `lr_grid=[0.001,0.0003]`, `n_train=5000`, `n_val=1000`, `n_test=200`, `N_SEEDS=10`, capacity witnesses `{GRU hidden=256 layers=2, Transformer d_model=256 layers=4, MLP [256,256]}`.
- TLGP-001B executed scale: 40 `train_select` calls per family across real/control/context-ablation/shuffle and 10 seeds; with two LR candidates per call this is 80 optimizer trainings per family, 240 optimizer trainings total.
- TLGP-001B-R2 entry point: `PYTHONPATH=. python -m src.tlgp_001b_r2.harness --full`; `src/tlgp_001b_r2/harness.py:442-506`.
- TLGP-001B-R2 official full hard-requires CUDA: `src/tlgp_001b_r2/official_full.py:226-229` blocks if CUDA is unavailable or selected device is not `cuda:0`.
- TLGP-001B-R2 frozen scale: same capacity grid and 10 seeds; primary families are `in_context_gru` and `in_context_transformer`, with MLP diagnostic-only. The official run recorded 420 training records = 14 configs × 10 seeds × 3 training rungs (`rung0`, `rung1`, `rung3`).
- TLGP-001B-R2 banked runtime readback: `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/result.json` reports `elapsed_sec=57714.883` (~16.0h) on `NVIDIA GeForce RTX 5070 Ti Laptop GPU`.

## located 001B positive-control defect

Spec/code lines showing CONTROL and REAL share the same test task:

- `artifacts/TLGP-001B/prereg.json:160`: `test set identical across REAL and CONTROL`.
- `src/tlgp_001b/splits.py:76-77`: `if split == "test": return P.HELDOUT_VALUES`.
- `src/tlgp_001b/splits.py:105-107`: `make_real_control_test()` returns `make_split("test", REAL, ...)`.
- `src/tlgp_001b/harness.py:350`: `test = S.make_real_control_test()`.
- Independent audit readback: `artifacts/TLGP-001B-INVALID-AUDIT-001/AUDIT_REPORT.md:60-68` states the CONTROL test is episode-for-episode identical to REAL and still requires unseen-rule generalization.

Corrected control requirement for this diagnostic: construct a capability-positive control that should fail if the harness is sound and should close for a working learner independently of the experimental question. Minimum acceptable options include a family-shuffled / label-permuted input that destroys cross-episode structure, plus a seen-rule or same-rule-pool control that isolates "can the learner fit/use cross-episode structure" from unseen-rule generalization.

## strongest baseline / shortcut explanation

The strongest baseline explanation is that any apparent cross-episode advantage is captured by a fair amortized meta-learner or by lookup / graph-cache / nearest-neighbor / episode-only memory under the same access. Passive prior advantage in `M/U` is presumed ceiling-blocked unless a fair meta-baseline with the same information cannot form it under the predeclared budget. Active-policy advantage in `A` is admissible only against a fair active policy such as UCB or max-info-gain with a predeclared double-dissociation.

## collision record

### Candidate A — minimal static diagnostic card only

- Evidence produced: card, source readback, compute posture, baseline/ablation/replay contract.
- Strongest cheap baseline that could match: none at runtime because no score is produced.
- Leakage / hard-coding risk: low for the card; risk deferred to future implementation.
- Smallest falsifying test: a later Red audit finds the baseline family or acceptance gate weaker than existing standards.
- Expected failure mode: card is too abstract and does not lead to a bounded timing probe.

### Candidate B — run existing TLGP-001B-R2 official full harness

- Evidence produced: known CUDA-only full-run style artifact.
- Strongest cheap baseline that could match: fair meta-baseline / amortized learner already central; could still fail to answer corrected-control question.
- Leakage / hard-coding risk: high if reused without correcting positive-control semantics.
- Smallest falsifying test: CPU unavailable or CUDA unauthorized; corrected-control defect remains unaddressed.
- Expected failure mode: expensive rerun reproduces the same floor/invalid pattern without resolving route admission.

### Candidate C — implement corrected control now

- Evidence produced: new control source and tests.
- Strongest cheap baseline that could match: label-permutation / family-shuffle scanner only if implemented as a static assertion rather than recomputation.
- Leakage / hard-coding risk: medium/high because changing the control is governance-affecting Red work.
- Smallest falsifying test: control construction is not pre-registered as an ancestor commit or is tuned after seeing scores.
- Expected failure mode: unauthorized implementation changes the test after observing prior failures.

Selected approach for this task: **Candidate A**. This step lands only the executable card and static compute posture, setting up a Red-audited gate before any scoring run.

## mandatory baselines

The full diagnostic must include at minimum:

- random / majority;
- episode-only lookup;
- nearest-neighbor / graph-cache family;
- amortized learner;
- **fair cross-episode meta-learner** with the same legal information and budget;
- oracle rule-family upper bound;
- ablated-memory candidate;
- shuffled-family / label-permuted leakage control.

Graph-cache family must include, when representational or environment claims are made: `graph_lookup`, `transition_table`, `successor_map`, `count_table`, `fsm_planner`, `episodic_traversal`.

## ablation requirement

Memory-ablation and family-shuffle / label-permutation must destroy any claimed candidate advantage. If the advantage survives no-memory, shuffled-family, label-permuted, no-update, or observation-only controls, it is not evidence of cross-episode learnability. Any ablation must rerun the same episode construction under the intervention; it may not be a stored-hash comparison or a static verdict dictionary.

## trace / replay requirement

Future artifacts must be written under `artifacts/TLGP-LEARNABILITY-FLOOR-DIAG-001/` and must include, unless a Red-audited execution card narrows this:

- `result.json`;
- `trace.jsonl`;
- `baseline_comparison.json`;
- `ablation_report.json`;
- `replay_report.json`;
- `leakage_report.json`;
- `failure_manifest.json` if anything fails;
- `claim_ceiling.txt` or claim-ceiling field in `result.json`.

Replay must recompute candidate and baseline behavior from serialized state + observation + allowed memory/update state. It must not merely compare stored hashes. Every score must record `producer_function`, input artifacts, `run_id`, seed/context/episode IDs, aggregation rule, and code path hash.

## computed-evidence provenance gate

Reported result, baseline, ablation, contrast, leakage, and replay metrics must come from callable computation paths. Static verdict literals, unconditional clean reports, and tests that only assert pass are forbidden. Leakage scan must include a real scanner and at least one positive-control case. Baselines must be independent callable implementations.

## acceptance gate [RED — pre-registered, ancestor of any run]

Full diagnostic acceptance is Red and must be pre-registered in a commit that is an ancestor of any scoring run.

Accept **H1 defect** only if all are true:

1. Candidate exceeds the strongest fair meta-baseline by a pre-registered margin on held-out families and held-out episodes.
2. The result survives independent callable baseline comparison including lookup / NN / graph-cache and a fair cross-episode meta-learner.
3. Memory-ablation and family-shuffle / label-permutation destroy the candidate advantage.
4. Trace replay recomputes the result exactly within the predeclared tolerance.
5. Corrected positive controls are fail-able and pass their positive-control semantics.
6. No leakage scanner positive-control failure, schema split, second logic path, post-hoc threshold tuning, or stale artifact reuse is found.

Accept **H0 floor / close-or-redesign** if the fair meta-baseline erases the gap, if the candidate only beats random/majority, if oracle-only headroom is the only positive signal, if controls are defective, or if replay/leakage/provenance gates fail.

Beating random/majority alone is not evidence. Oracle-only headroom is not evidence. A defective positive control voids the result.

## compute posture

Static assessment only; no timing or scoring was run for this card.

- Existing TLGP-001B can technically fall back to CPU but the frozen full path was documented as heavy on CPU and the banked result used CUDA.
- Existing TLGP-001B-R2 official full path is **GPU-required** by code (`CUDA is unavailable; official full R2 is not authorized on CPU`).
- Prior measured R2 full run cost was ~16h on an RTX 5070 Ti Laptop GPU for 420 training records.
- A full diagnostic at comparable scale is therefore Track-T GPU-scale unless explicitly redesigned as a smaller diagnostic.
- Static estimates systematically under-project cost in this repo's prior projection lessons. The recommended next micro-step is a bounded live CPU timing probe: `device=cpu`, all RNG seeded, no score claim, no artifact verdict, timing only, ≤5 minutes wall-clock. This timing probe may estimate whether a reduced CPU diagnostic is feasible; it is not a mechanism result and was not run by this card.

Budget line for any full diagnostic: **DEFERRED** pending Red audit + compute posture authorization.

## stop condition

Stop without full diagnostic execution if any of the following holds:

- Claude Red audit rejects the baseline family or acceptance gate;
- compute posture / budget is not authorized;
- GPU is required but Track-T GPU is not separately authorized;
- CPU timing probe exceeds the bounded wall-clock line or cannot isolate timing without scores;
- corrected positive-control construction is not pre-registered as an ancestor of the run;
- any fair baseline is loosened after seeing scores;
- any threshold, schema, or frozen design is changed to rescue a result;
- replay/leakage/provenance paths cannot be made callable.

## rollback plan

Documentation-only rollback: revert the commit adding this card. Do not delete prior TLGP artifacts or rewrite 001B / 001B-R2 evidence. Any future runner/control implementation must be isolated to a new authorized path and reversible by scoped revert.

## forbidden

- Run the full diagnostic without CPU-feasible + budget authorization.
- Use GPU without separate Track-T GPU authorization.
- Implement a new mechanism or corrected control from this card alone.
- Loosen or omit any fair baseline.
- Treat random/majority win or oracle-only headroom as evidence.
- Treat seen-rule capability, rung0/rung1 fit, or control closure as mechanism evidence.
- Patch thresholds, schema, frozen design, or positive controls after seeing scores.
- Touch EGO mainline, runtime, UI, LLM/AIRI integration, relationship learning, emotion systems, deployment, or API keys.
- Claim N1 readiness, Gate pass, mechanism validity, theory truth/falsity, agency, autonomy, consciousness, emotion, or EGO readiness.

## auto-remote-anchor

Auto-Remote-Anchor: forbidden.

