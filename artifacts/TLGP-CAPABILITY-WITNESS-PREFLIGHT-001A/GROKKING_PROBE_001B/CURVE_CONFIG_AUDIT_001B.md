# GROKKING_PROBE_001B Curve/Config Audit

Task: `TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CURVE-CONFIG-AUDIT-001A`
Formal status: `ambiguous`
Substantive assessment: `negative_leaning_no_grokking_signature`
Route: `inconclusive_underpowered`
Closeout comparison: `no_evidence_metric_drift`

## Coverage

- Records: 6
- Curve rows: 150
- Cells: 6
- Checkpoint coverage ok: `true`
- Protected source status empty: `true`

## Curve Diagnostics

| seed | wd | fit step | best heldout | best step | final heldout | full delta | post-fit delta | tail delta | post-fit best-to-final drop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 20260710 | 0.3 | 6000 | 0.571358 | 38000 | 0.548624 | 0.080783 | 0.009407 | 0.004031 | 0.022734 |
| 20260710 | 0.5 | 10000 | 0.601140 | 38000 | 0.587743 | 0.130561 | 0.013664 | 0.004785 | 0.013397 |
| 20260711 | 0.3 | 6000 | 0.545886 | 42000 | 0.529257 | 0.094953 | 0.024660 | -0.016629 | 0.016629 |
| 20260711 | 0.5 | 8000 | 0.514671 | 36000 | 0.474135 | 0.060710 | -0.015985 | -0.024244 | 0.040536 |
| 20260712 | 0.3 | 8000 | 0.582508 | 14000 | 0.568503 | 0.110776 | -0.001088 | 0.002517 | 0.014005 |
| 20260712 | 0.5 | 10000 | 0.598042 | 40000 | 0.553420 | 0.111778 | -0.030355 | -0.035024 | 0.044622 |

## Threshold Windows

No cell has a three-checkpoint sustained window at `0.60`, `0.65`, or `0.75`.
The formal negative-close cutoff remains blocked by one best-heldout checkpoint above 0.60; the crossing is not sustained over three checkpoints and does not meet 0.65 or 0.75 windows.

## Config Readback

- Static AdamW plumbing passes `weight_decay=float(weight_decay)`: `true`
- Direct optimizer param-group readback: `unavailable`
- Direct readback reason: completed 001B artifacts record requested weight_decay per run but do not serialize optimizer.param_groups; this audit can prove manifest inputs plus static AdamW plumbing, not direct completed-runtime param-group values

## Drift

- Evidence metric drift vs closeout: `false`
- Repo context differences vs closeout: `1`

## Claim Ceiling

curve/config audit only; no route terminal, no TLGP-R2 verdict, no mechanism validity claim, no witness validity claim, no agency/self/subjectivity/AGI/EGO/stable-benefit claim
