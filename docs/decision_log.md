# Decision Log

## ACOLB-A route closure / Route C design-audit boundary

- Commit: `bb65008c365a987b6e5d00c759a153d365bdd476`
- Decision: close ACOLB-A current surface.
- Reason: fair amortized baseline / discounted WLS saturation; candidate and fair baseline are structurally equivalent on this surface.
- Preserved evidence: `artifacts/acolb_001a/**`; verdict `saturated_close`; blocker `blocked_by_saturated_distribution`.
- Next route: draft Route C hostile design blueprint as ACSB-family re-entry.
- Not authorized: Route C implementation, Gate run, mainline wiring, push, tag, remote anchor.
- Claim ceiling: route-governance / bounded local negative surface evidence only.
- Mainline integration: none.
- Enabled status: none.
- Real trigger evidence: none; this is docs-only route-governance preservation, not a live path.

## ACP-BV 001B post-anchor route closure / downgrade

- Anchor: `remote-anchor-acp-bv-001b-negative-harness-repair-evidence-001a-98be7f4`
- Commit: `98be7f4e647d7d5e897ee32b7905e085b67a43e7`
- Decision: close ACP-BV 001B as a mechanism surface; downgrade to negative harness/governance evidence; preserve harness apparatus; defer replacement surface.
- Decisive reason: fair-baseline saturation, not merely hardcoded candidate. The strongest fair legal-channel baseline (`parametric_modular_linear`) reaches `1.0`, the candidate reaches `1.0`, and delta is `0.0`, so discriminative candidate greater than fair-baseline mechanism evidence is structurally unreachable on this distribution.
- Claim ceiling: route-governance / negative-harness evidence only.
- Mainline integration: none.
- Enabled status: none beyond local CLI / pytest / artifact generation.
- Auto-Remote-Anchor: forbidden.
