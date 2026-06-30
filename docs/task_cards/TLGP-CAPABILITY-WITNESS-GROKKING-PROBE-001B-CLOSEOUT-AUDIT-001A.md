# TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CLOSEOUT-AUDIT-001A

> Status: LOCAL closeout/audit card. Authorizes only a readback audit of the
> already-produced `GROKKING_PROBE_001B` artifacts. This is not a rerun, not a
> continuation, not a powered sweep, and not a bank/publish operation.

Task id: TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CLOSEOUT-AUDIT-001A

Problem definition: `GROKKING_PROBE_001B` completed with a formal artifact verdict
of `ambiguous`: all six cells fitted, no positive heldout threshold or sustained
late-rise signal appeared, but one fitted cell had a single best-heldout checkpoint
of `0.6011401515`, narrowly above the strict `<=0.60` negative-close cutoff. The
result must be closed out without upgrading it into a route terminal or dismissing
the threshold blip.

Current stage/layer: candidate-free feasibility preflight closeout; learning/adaptation
proxy evidence review only.

Mainline target: local ITL artifact interpretation only. No EGO mainline integration,
no TLGP-R2 adjudication, no H0/H1 verdict.

Enabled-state requirement: consume the existing completed local 001B artifact set
under `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/`.
Do not start training or modify runner behavior.

Real-trigger evidence requirement: read `training_records.json`, `val_curves.jsonl`,
`probe_trend_report.json`, `route_decision.json`, `route_decision_input.json`,
`leakage_report.json`, and `manifest.json` from the completed 001B run.

Hypothesis: the formal result is `ambiguous`, but the observable curve morphology is
negative-leaning for grokking: fitted train curves, heldout below the positive bar,
no sustained late rise, and the lone `>0.60` value is not sustained.

Strongest baseline / false explanation: the apparent closeout could be an artifact
of threshold wording, a single checkpoint noise blip, insufficient run length, a split
or metric readback issue, or missing optimizer/config provenance.

Ablation requirement: no new ablation is authorized. The audit may only classify the
existing 001B outputs and identify missing provenance needed before future claims.

Trace/replay requirement: verify the dense curve row count and per-cell checkpoint
coverage from `val_curves.jsonl`; do not synthesize missing checkpoints.

Computed-evidence provenance gate: the closeout classification must be produced by a
callable artifact-local audit script and record:
- producer script path and SHA256;
- input artifact paths and SHA256;
- route/prereg/frozen/probe hashes;
- split sizes and split hashes from the frozen rung0 generator;
- label/rule distributions;
- per-cell final train/heldout, best heldout, fit step, late-rise flag;
- tail-window heldout slope/delta;
- whether the `0.6011401515` threshold crossing is sustained or isolated;
- fields unavailable from the completed artifacts, especially runtime optimizer
  param-group readback.

Acceptance gate:
- no source files edited;
- no training rerun or continuation;
- no powered/full sweep;
- all required 001B artifacts present;
- dense curve coverage is 6 cells x 25 checkpoints = 150 rows;
- manifest hashes match `515a415b...`, `0dcf3659...`, and `6e61a831...`;
- protected source status for `src/tlgp_001b_r2` and `src/tlgp_001a` is empty;
- route decision remains `inconclusive_underpowered`;
- formal closeout remains `ambiguous`;
- substantive readback may say only `negative-leaning/no grokking signature`, not
  route closed, theory falsified, or mechanism invalid.

Claim ceiling: bounded closeout interpretation of one local cheap fit+regularization
probe. This can support `formal ambiguous; negative-leaning; no grokking signature in
001B`, but it proves nothing about transfer, rung3/H1, TLGP-R2 validity, mechanism
validity, the GRU witness, agency, self, subjectivity, AGI, EGO, or stable user benefit.

Stop condition: stop and write a closeout failure artifact if any hash mismatch,
missing required artifact, protected-source dirty status, evidence inconsistency,
unexpected successful positive signal, or unauthorized source edit is observed.

Rollback plan: remove the new closeout-audit card and artifact-local closeout audit
files. Do not delete the original 001B run artifacts as part of this card.

Expected changed files:
- `docs/task_cards/TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CLOSEOUT-AUDIT-001A.md`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/closeout_audit_001b.py`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/closeout_audit_001b.json`
- `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/CLOSEOUT_AUDIT_001B.md`

Forbidden changes:
- no edits to `grokking_probe.py`, `minimal_probe.py`, `route_decision.py`,
  `src/tlgp_001b_r2/*`, or `src/tlgp_001a/*`;
- no threshold tuning;
- no continuation beyond 50k;
- no new training, known-good sanity run, or powered sweep;
- no `git add -A`;
- no push, tag, PR, or remote anchor;
- no `AGENTS.md`, `CLAUDE.md`, or global config edits.

Auto-Remote-Anchor: forbidden.

## Collision Record

Approach A - immediately bank as `grok_negative_close`: rejected. It would erase the
formal `ambiguous` artifact status and ignore the single `0.6011401515` threshold
crossing.

Approach B - run a powered/full sweep now: rejected. The completed cheap probe does
not show late-rise morphology strong enough to justify automatic spend escalation.

Approach C - local closeout audit with formal/substantive split: selected. It
preserves the frozen verdict (`ambiguous`) while separately recording the
negative-leaning curve morphology and the precise threshold-blip reason.

Selected approach: Approach C.
