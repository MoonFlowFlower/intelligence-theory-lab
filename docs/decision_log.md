# Decision Log

## ACP-BV 001B post-anchor route closure / downgrade

- Anchor: `remote-anchor-acp-bv-001b-negative-harness-repair-evidence-001a-98be7f4`
- Commit: `98be7f4e647d7d5e897ee32b7905e085b67a43e7`
- Decision: close ACP-BV 001B as a mechanism surface; downgrade to negative harness/governance evidence; preserve harness apparatus; defer replacement surface.
- Decisive reason: fair-baseline saturation, not merely hardcoded candidate. The strongest fair legal-channel baseline (`parametric_modular_linear`) reaches `1.0`, the candidate reaches `1.0`, and delta is `0.0`, so discriminative candidate greater than fair-baseline mechanism evidence is structurally unreachable on this distribution.
- Claim ceiling: route-governance / negative-harness evidence only.
- Mainline integration: none.
- Enabled status: none beyond local CLI / pytest / artifact generation.
- Auto-Remote-Anchor: forbidden.
