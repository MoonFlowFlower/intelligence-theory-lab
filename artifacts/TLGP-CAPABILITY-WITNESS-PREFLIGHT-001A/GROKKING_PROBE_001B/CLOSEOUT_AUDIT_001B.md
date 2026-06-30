# GROKKING_PROBE_001B Closeout Audit

Task: `TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B-CLOSEOUT-AUDIT-001A`
Formal status: `ambiguous`
Substantive assessment: `negative_leaning_no_grokking_signature`

## Readback

- Records: 6
- Curve rows: 150
- Route decision: `inconclusive_underpowered`
- Leakage detector valid: `True`
- Failure manifest present: `False`

## Per Cell

| seed | wd | final train | final heldout | best heldout | fit step | tail delta | late rise |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 20260710 | 0.3 | 0.999978 | 0.548624 | 0.571358 | 6000 | 0.004031 | false |
| 20260710 | 0.5 | 0.987321 | 0.587743 | 0.601140 | 10000 | 0.004785 | false |
| 20260711 | 0.3 | 0.999924 | 0.529257 | 0.545886 | 6000 | -0.016629 | false |
| 20260711 | 0.5 | 0.987938 | 0.474135 | 0.514671 | 8000 | -0.024244 | false |
| 20260712 | 0.3 | 0.955029 | 0.568503 | 0.582508 | 8000 | 0.002517 | false |
| 20260712 | 0.5 | 0.991188 | 0.553420 | 0.598042 | 10000 | -0.035024 | false |

## Threshold Blip

The formal negative-close cutoff is blocked by one best-heldout checkpoint above 0.60; the crossing is not a 3-checkpoint sustained plateau and is not a positive grokking signal.

## Claim Ceiling

formal ambiguous; negative-leaning/no grokking signature for this local cheap fit+regularization probe only. No route terminal, no TLGP-R2 verdict, no mechanism validity claim, no EGO claim.
