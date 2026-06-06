# M1-005 Strong Baseline Gap Audit

Conclusion: current baseline coverage is strong for bounded contract shortcuts, but still not enough for LCC theory support.

The gaps below do not invalidate Cycle 000-010 bounded passes. They do block any theory-support upgrade and motivate independent reimplementation followed by a cross-theory tournament.

## Covered Or Partially Covered

| Baseline Family | Current Coverage | Remaining Gap |
| --- | --- | --- |
| Action-label heuristic | Directly attacked from Cycle 000 onward. | Low gap for the original shortcut class. |
| Static safety table | Repeatedly attacked through label/effect swaps and heldouts. | Low-medium gap; independent implementation still needed. |
| Nearest-neighbor / trace lookup | Attacked in multiple cycles. | Medium gap under richer continuous traces. |
| Explicit effect table | Treated as diagnostic upper bound, not valid mechanism. | Low gap as an invalid candidate path. |
| Generic model-based MPC proxy | Included in Cycle 010. | Medium-high gap versus a full learned-dynamics planner. |
| Active inference proxy | Included as a generic challenger in Cycle 010. | High gap versus a strong EFE implementation. |
| Empowerment proxy | Included as a generic challenger in Cycle 010. | High gap versus a learned controllability/empowerment planner. |

## Major Remaining Challengers

- Strong learned-dynamics model-based RL planner.
- Causal graph learner plus planner.
- Active inference / expected free energy controller.
- Learned empowerment or information-gain planner.
- Meta-RL / recurrent policy baseline.
- Program synthesis or search baseline for small contracts.

## Review Finding

No current result authorizes the statement that LCC is distinct from model-based causal control. The correct claim is narrower: the current LCC line has survived strong anti-shortcut bounded contracts, including a blind holdout and generic baseline proxies.

## Impact On M1 Decision

The baseline gap blocks theory support but does not block an independent reimplementation contract. It also makes cross-theory tournament the necessary next major review after independent replication.
