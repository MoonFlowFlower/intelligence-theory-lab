# Risk Register

| Risk | Status | Mitigation / stop line |
| --- | --- | --- |
| 20 fixed handles replace 7 fixed handles | open | 005 must require variable-N CandidateOption input, not a larger tuple. |
| Effect representation only works for act ids | open | If confirmed in 005, stop and run ACTION-REPRESENTATION-RCA. |
| Renderer leaks public action names | controlled in 004 | Renderer must remain post-selection and adapter-only. |
| Replay contract hides fixed ids | partial | Replay can be parametric if traces contain full option distribution. |
| Baselines are weaker in expanded space | open | Expanded baselines must consume same anonymous options. |
| 003 evidence invalidated by interface rewrite | open | Use shadow adapter and preserve 003 as small-action-set evidence. |
| Threshold retune or selector patch to win | forbidden | Any occurrence invalidates the run. |
| EGO/product leap from RCA | forbidden | RCA supports only a 005 contract review, not implementation. |
