"""TLGP-001B: candidate-free cross-episode meta-learner baseline-completeness harness.

Extends TLGP-001A (banked candidate-free gap-testbed). 001A showed ONE procedural world
separates a family-knowing in-family Bayesian observer (ideal, ~1.0) from family-ignorant
per-episode fair baselines (~floor) on a held-out, balanced, leak-audited, extrapolative
metric. 001A's open question (recorded in its audit): does that within-episode headroom
SURVIVE a capacity-saturated cross-episode meta-learner that may amortize the mod-K rule
family across many training episodes?

001B answers that ONE bounded question. It is candidate-free: it tests NO mechanism. It
adds a pre-registered meta-learner panel (in-context GRU, in-context Transformer, amortized
summary MLP) trained across episodes, plus a capacity-control regime that PROVES the
meta-learner family is not underpowered, plus context/shuffle ablations, the 001A dual-target
leakage detector applied to the meta input channels, exact replay, tamper fail-ability,
and a computed verdict with frozen precedence.

Claim ceiling (frozen prereg): bounded offline evidence on whether ONE procedural world's
within-episode inference headroom survives cross-episode amortization. NOT learning-as-
mechanism, agency, self, feeling, subjectivity, intelligence, or EGO-readiness evidence.
A negative in either direction is bounded to THIS world + THIS meta-learner family + this
pre-registered capacity grid.

This package may ONLY create files under src/tlgp_001b/** and artifacts/TLGP-001B/**, and
read-only-imports exactly four 001A modules: world, ideal_observer, metrics, leakage.
It performs NO git operation.
"""
from __future__ import annotations

__all__ = ["preregistration", "splits", "lower_reference", "meta_learners", "harness"]
