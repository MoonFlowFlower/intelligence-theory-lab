# TLGP-001B-R2-HARNESS-SMOKE-001 Collision Record

## Scope

- Task type: isolated R2 harness implementation plus non-evidential smoke/calibration only.
- Current layer: engineering implementation + mechanism-hypothesis preflight.
- Real objective: produce a replayable, CUDA-plumbed R2 harness skeleton that preserves the frozen preregistration and can prove smoke plumbing without launching the official full R2 run.
- Claim ceiling: implementation/plumbing evidence only. No H0, H1, INVALID official verdict, mechanism evidence, learning evidence, subjectivity evidence, EGO readiness, or mainline effect.
- Mainline integration: none.
- Enabled status: R2 prereg is frozen; implementation path is local-only and isolated.
- Auto-Remote-Anchor: forbidden.

## Prior Negative Evidence Readback

- TLGP-001B-R1 official run is preserved as INVALID.
- The invalid audit assigns the primary cause to a capacity-control design flaw: CONTROL and REAL shared the unseen-rule test difficulty, so R1 did not establish a valid capability witness.
- R2 must not patch R1 into a pass or reinterpret R1 as H1. It must add a graded capability-witness ladder while preserving R1/001A evidence.

## Bounded Audit

- Problem definition risk: implementing a "smoke" could accidentally become a partial official run. Mitigation: smoke artifacts must set `evidential: false` and `official_verdict: NOT_EMITTED`; no `result.json` is created.
- Strongest baseline explanation: a cheap seen-rule lookup or count-table path may match rung-1, so rung-1 scanner and context-ablation remain load-bearing.
- Strongest invalidity reason: if CUDA is available but models or tensors remain on CPU, smoke proves the wrong runtime path and must stop as a device-plumbing blocker.
- Falsifier for current framing: prereg canonical SHA mismatch, smoke official verdict emission, replay mismatch from recorded smoke predictions, leakage fixture failure, tamper fixture coverage failure, or CUDA telemetry showing CPU execution when CUDA is available.
- Insufficient evidence even if smoke passes: no full-budget training, no scientific verdict, no H0/H1/INVALID official outcome, no mechanism conclusion, no mainline effect.
- Mechanism-vs-resemblance classification: this task tests harness plumbing and failability only; it does not test a mechanism.

## Candidate Approaches

### Candidate A: Minimal CLI Stub

- Evidence produced: prereg hash readback, artifact writing, and CLI smoke command.
- Strongest cheap baseline that could match it: a report-only stub can appear complete without exercising model/tensor devices or replay.
- Leakage/hard-coding risk: high if verdict/tamper/leakage outputs are static strings.
- Smallest falsifying test: require trace replay and synthetic tamper branches to be recomputed from recorded fields.
- Expected failure mode: passes superficial smoke while leaving device plumbing and replay untested.

### Candidate B: Strongest Shortcut/Baseline Harness

- Evidence produced: callable lower references, scanner calculations, and replay over synthetic episodes, but no real training path.
- Strongest cheap baseline that could match it: lookup/count-table/predict_all can saturate easy seen-rule fixtures.
- Leakage/hard-coding risk: medium if synthetic traces encode labels or branch outcomes directly.
- Smallest falsifying test: structural leakage scan with planted and clean controls plus no `rule_id`/`query_e` in meta inputs.
- Expected failure mode: demonstrates scanner math but not primary meta CUDA training.

### Candidate C: Mechanism-Faithful Smoke Harness

- Evidence produced: frozen-prereg loader, deterministic split/world generation, lower references, primary/diagnostic model instantiation, tiny CUDA training calibration for primary families, CPU-serialized predictions, replay recomputation, leakage smoke, rung1 scanner smoke, and 7-terminal synthetic verdict tamper coverage.
- Strongest cheap baseline that could match it: synthetic tiny tasks can be too easy; therefore smoke is explicitly non-evidential and cannot emit official verdicts.
- Leakage/hard-coding risk: lower if all smoke claims are derived from callable functions and recorded fixtures, but still non-evidential.
- Smallest falsifying test: when CUDA is available, assert selected device is `cuda:0`, model parameters and tensors are on `cuda:0`, and serialized predictions are CPU/list values.
- Expected failure mode: implementation complexity may expose a device-plumbing blocker; in that case stop without changing prereg or running CPU full budget.

## Selected Approach

Select Candidate C for implementation. It is the only approach that can satisfy the user's CUDA requirement and the task card's smoke/replay/leakage/tamper requirements without upgrading smoke into evidence.

## Acceptance Signals

- `artifacts/TLGP-001B-R2/prereg.json` canonical SHA equals `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`.
- `PYTHONPATH=. python -m src.tlgp_001b_r2.harness --smoke` writes only non-evidential smoke artifacts.
- If CUDA is available, selected device is `cuda:0` and both primary families record model and tensor devices on `cuda:0`.
- Predictions are serialized as CPU/plain Python values.
- Smoke replay recomputes from trace without retraining.
- Leakage planted controls are caught and clean controls are not falsely flagged.
- Synthetic tamper fixtures uniquely cover all 7 terminal verdict branches.
- No forbidden paths are modified, no git operation is run, and no official full run starts.

## Stop Conditions

- Prereg SHA mismatch.
- CUDA available but primary model/tensor telemetry is not `cuda:0`.
- Smoke emits official H0/H1/INVALID or creates official `result.json`.
- Replay/leakage/tamper smoke fails.
- Implementation requires changing frozen constants, prereg, prior evidence, forbidden files, or training semantics.

## Rollback

Delete only:

- `src/tlgp_001b_r2/**`
- R2 implementation/smoke outputs under `artifacts/TLGP-001B-R2/**` created by this task

Preserve prereg/freeze files unless the operator explicitly requests cleanup.
