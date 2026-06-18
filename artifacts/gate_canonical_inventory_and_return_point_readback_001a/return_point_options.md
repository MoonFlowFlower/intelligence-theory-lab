# Return Point Options

Required choice set:

1. `return_to_gate_provenance_hardening`
2. `return_to_gate4_replacement_route_selection`
3. `return_to_gate5_blocked_pending_lower_gate_readback`
4. `switch_to_alternative_mechanism_route_selection`
5. `blocked_pending_canonical_conflict`

## Selected Recommendation

`return_to_gate_provenance_hardening`

## Basis

Fact:

- Branch is `codex/meta-theory-scaffold`, HEAD is `b45598b1c56080f2f850ae088f42cf585950483e`, and the working tree is dirty.
- Route C separation-probe rejection preservation files exist.
- `docs/decision_log.md` contains the Route C rejection pointer and the baseline-immunity admission-standard pointer.
- `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A.md` and `.registry.json` exist and the registry parses as JSON.
- The registry declares no executor, but `executor_exact_none` is false because the field contains explanatory text after `none`.
- Gate1 positive inheritance is closed by the graph-cache reconciliation route.
- Gate3/integrated-route evidence is downgraded for current integrated use.
- Current Gate4/Route C replacement surfaces are closed, blocked, or negative evidence due baseline saturation, false-pass risk, graph-cache/lookup collapse, leakage, or oracle issues.
- Gate5 has no current lower-gate-safe execution basis in this readback.

Inference:

- `return_to_gate4_replacement_route_selection` is unsafe because the lower-gate chain and current Gate4/Route C surfaces are not clean positive parents.
- `return_to_gate5_blocked_pending_lower_gate_readback` is true as a ceiling, but it is not the safest next route because Gate5 is not the active problem to repair; it is a downstream block.
- `switch_to_alternative_mechanism_route_selection` is not selected because the repo readback still exposes lower-gate provenance/readback hardening as the first closed-loop prerequisite.
- `blocked_pending_canonical_conflict` is not selected because no HEAD/branch mismatch, unreadable relevant artifact, decision-log contradiction, unclassifiable memory-index modification, or implementation-dependent status conflict was found.

## Next Minimal Closed-Loop Action

Draft or run a separate bounded provenance/readback-hardening task that reconciles the current dirty Route C/baseline-immunity working-tree additions against the remote-anchored lower-Gate boundaries, without Gate execution, source/test changes, or mechanism-claim upgrade unless a new task card explicitly authorizes them.
