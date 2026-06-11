# Expressivity Proof

The frozen environment is `ParityAliasGrid-v0`. Each allowed token is an action/observation pair. The target is the XOR of `action_bit XOR observation_bit` over the full six-token sequence.

For K=1,2,3,4 the verifier enumerates all finite histories and finds at least one equivalence class where two histories share the same K-window but require different targets. Therefore no bounded-order K-window predictor can represent the target for K<=4.

The positive witness is non-oracle: it maintains one internal parity bit updated online from the same allowed tokens. It uses no hidden labels, heldout ids, future outcomes, seed labels, or environment internals.

This is not a horizon-only gap: the dependency is the compositional parity update. Increasing K beyond 4 was not attempted and is not needed for this bounded preflight.
