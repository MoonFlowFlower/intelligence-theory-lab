# Option Composition Contract

Generated options may be composed from admitted option evidence only. Composition is a proposal operation, not selection.

- A composed option must reference all source option IDs.
- A composed option must pass the same `OptionAdmissionGate` as non-composed proposals.
- Composition cannot import natural-language descriptions into selector-visible fields.
- Composition cannot infer an oracle effect.
- If the composed effect is weakly supported, the option must carry high uncertainty until repeated outcomes support it.
