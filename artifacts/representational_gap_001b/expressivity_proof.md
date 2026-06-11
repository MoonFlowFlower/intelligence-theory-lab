# Expressivity Proof

The frozen family preserves the 001A K<=4 bounded-window collision residue: suffix windows of
length 1 through 4 have equivalence classes containing both target labels.

Under the fair 001B control contract, this residue does not survive. The full-history paired-token
count statistic computes `(count(a0_o1) + count(a1_o0)) mod 2`, which equals the target for every
enumerated history. A 2-state finite automaton with token-conditioned parity transitions also solves
the target. History graph cache, exact episodic retrieval, successor-map parity composition, and
minimal sufficient summary search solve as well.

Verdict: `representational_gap_001b_failed_count_or_statistic_control_solved`.

This is negative evidence for the attempted 001B gap, not evidence for model-class reset.
