# Admission Gate Redteam Contract

Purpose: test whether the option admission gate is meaningful rather than always-pass, always-reject, or weak-evidence high-confidence.

Required future checks:

- weak evidence proposals must stay low-confidence or pending
- single contradictory feedback must become `pending_counterevidence`
- repeated/high-confidence context-matched feedback may become `admitted_context_counterevidence`
- admitted updates may change selector-visible effect vectors only after admission
- report admission pass/reject/pending rates
- report `weak_evidence_high_confidence_rate`

Stop if weak evidence creates high-confidence options, single contradiction changes selector-visible effect vectors before admission, or the gate always admits or always rejects proposals.

