"""Exact Bayesian ideal observer (P2 ceiling) for TLGP-001A.

Knows the rule FAMILY (the K^(D+1) linear-mod hypotheses) but NOT which rule. Filters to
the rules consistent with the episode's adaptation interactions (exact likelihood: a rule
is consistent iff it reproduces every observed effect), then predicts each held-out query
by posterior-predictive MAP (uniform posterior over the consistent set).

It NEVER sees a held-out effect. It is a probe instrument and is excluded from the fair
baseline panel. This is an EXACT enumeration (625 rules), not an approximation, so it is
deterministic and fully replayable.

The same `predict_core` powers the K1 single-step decoder (adaptation truncated to ONE
observation) and its value-level positive control (`forced_rule_idx` = the rule is revealed
in the single observation -> consistent set collapses to the true rule -> exact prediction).
"""
from __future__ import annotations

import numpy as np

from . import preregistration as P
from .world import Episode, enumerate_rules

_W = None   # (R, D)
_C = None   # (R,)


def _rule_arrays():
    global _W, _C
    if _W is None:
        rules = enumerate_rules()
        _W = np.array([r.w for r in rules], dtype=int)
        _C = np.array([r.c for r in rules], dtype=int)
    return _W, _C


def predict_core(adapt_x, adapt_a, adapt_e, query_x, query_a,
                 forced_rule_idx=None):
    """Posterior-predictive MAP over held-out queries.

    forced_rule_idx: if given, the consistent set is forced to that single rule (used by the
    K1 value-level positive control to simulate the latent being revealed in the observation).
    """
    W, C = _rule_arrays()
    adapt_x = np.asarray(adapt_x, dtype=int).reshape(-1, P.D)
    adapt_a = np.asarray(adapt_a, dtype=int).reshape(-1)
    adapt_e = np.asarray(adapt_e, dtype=int).reshape(-1)
    query_x = np.asarray(query_x, dtype=int).reshape(-1, P.D)
    query_a = np.asarray(query_a, dtype=int).reshape(-1)

    if forced_rule_idx is not None:
        consistent_idx = np.array([forced_rule_idx])
    else:
        pred_adapt = (W @ adapt_x.T + np.outer(C, adapt_a)) % P.K   # (R, n_adapt)
        consistent = np.all(pred_adapt == adapt_e[None, :], axis=1)
        consistent_idx = np.flatnonzero(consistent)

    n_consistent = int(consistent_idx.size)
    if n_consistent == 0:
        vals, counts = np.unique(adapt_e, return_counts=True)
        return np.full(query_x.shape[0], int(vals[np.argmax(counts)]), dtype=int), 0

    Wc, Cc = W[consistent_idx], C[consistent_idx]
    pred_query = (Wc @ query_x.T + np.outer(Cc, query_a)) % P.K        # (Rc, n_query)
    preds = np.empty(query_x.shape[0], dtype=int)
    for q in range(pred_query.shape[1]):
        preds[q] = int(np.argmax(np.bincount(pred_query[:, q], minlength=P.K)))
    return preds, n_consistent


def predict_episode(ep: Episode):
    return predict_core(ep.adapt_x, ep.adapt_a, ep.adapt_e, ep.query_x, ep.query_a)
