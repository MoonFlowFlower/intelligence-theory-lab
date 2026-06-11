"""Frozen mathematical skeleton (task card section 4). Equations must not be altered.

Pure arithmetic only: no I/O, no randomness, no retrieval, no replay, no hidden state
beyond belief b, pseudo-counts C_T, C_O, and static dimensions/hyperparameters.
"""

import math


class FrozenSkeleton:
    """Finite-state predictive-action learner.

    b_t(s)                belief over latent state
    C_T[s][a][s']         transition pseudo-counts -> T_theta(s'|s,a)
    C_O[s'][o]            observation pseudo-counts -> O_theta(o|s')

    Flags (for baselines/ablations only; defaults are the core skeleton):
      theta_update_enabled  - if False, C_T/C_O never change (frozen theta)
      theta_freeze_at_t     - if set, theta updates stop at t >= value
      belief_update_enabled - if False, b stays at its current value (ablation 4)
    """

    def __init__(self, n_s, n_a, n_o, alpha, eta, log_eps,
                 theta_update_enabled=True, theta_freeze_at_t=None,
                 belief_update_enabled=True):
        self.n_s, self.n_a, self.n_o = n_s, n_a, n_o
        self.alpha, self.eta, self.log_eps = alpha, eta, log_eps
        self.theta_update_enabled = theta_update_enabled
        self.theta_freeze_at_t = theta_freeze_at_t
        self.belief_update_enabled = belief_update_enabled
        self.C_T = [[[alpha for _ in range(n_s)] for _ in range(n_a)] for _ in range(n_s)]
        self.C_O = [[alpha for _ in range(n_o)] for _ in range(n_s)]
        self.b = [1.0 / n_s for _ in range(n_s)]

    # ---- normalized model tables ------------------------------------------------
    def theta_T(self):
        out = []
        for s in range(self.n_s):
            rows = []
            for a in range(self.n_a):
                tot = sum(self.C_T[s][a])
                rows.append([c / tot for c in self.C_T[s][a]])
            out.append(rows)
        return out

    def theta_O(self):
        out = []
        for sp in range(self.n_s):
            tot = sum(self.C_O[sp])
            out.append([c / tot for c in self.C_O[sp]])
        return out

    # ---- section 4.5: prediction -------------------------------------------------
    def predict_all_actions(self):
        """Return ({a: predicted next-state belief}, {a: predicted obs distribution})
        for ALL actions from the same current belief/history (section 4.11)."""
        T = self.theta_T()
        O = self.theta_O()
        bhat_by_a = {}
        pobs_by_a = {}
        for a in range(self.n_a):
            bhat = [0.0] * self.n_s
            for s in range(self.n_s):
                bs = self.b[s]
                if bs == 0.0:
                    continue
                row = T[s][a]
                for sp in range(self.n_s):
                    bhat[sp] += bs * row[sp]
            pobs = [0.0] * self.n_o
            for sp in range(self.n_s):
                w = bhat[sp]
                if w == 0.0:
                    continue
                orow = O[sp]
                for o in range(self.n_o):
                    pobs[o] += w * orow[o]
            bhat_by_a[a] = bhat
            pobs_by_a[a] = pobs
        return bhat_by_a, pobs_by_a

    # ---- sections 4.7, 4.9, 4.10: error, belief update, model learning ----------
    def update(self, a_t, o_next, t):
        """Observe o_{t+1} after taking a_t. Returns a dict of update internals.

        xi_t(s,s') ∝ b_t(s) T(s'|s,a_t) O(o_{t+1}|s'),  normalized over (s,s')
        b_{t+1}(s') = sum_s xi_t(s,s')
        C_T(s,a_t,s') += eta * xi_t(s,s')
        C_O(s',o_{t+1}) += eta * b_{t+1}(s')
        """
        T = self.theta_T()
        O = self.theta_O()
        b_pre = list(self.b)
        xi = [[0.0] * self.n_s for _ in range(self.n_s)]
        z = 0.0
        for s in range(self.n_s):
            bs = b_pre[s]
            if bs == 0.0:
                continue
            for sp in range(self.n_s):
                v = bs * T[s][a_t][sp] * O[sp][o_next]
                xi[s][sp] = v
                z += v
        if z <= 0.0:
            # impossible with alpha>0 pseudo-counts; guard kept explicit
            raise RuntimeError("xi normalization failure (zero mass)")
        for s in range(self.n_s):
            for sp in range(self.n_s):
                xi[s][sp] /= z
        b_post = [0.0] * self.n_s
        for sp in range(self.n_s):
            acc = 0.0
            for s in range(self.n_s):
                acc += xi[s][sp]
            b_post[sp] = acc

        theta_updated = False
        if self.theta_update_enabled and (
                self.theta_freeze_at_t is None or t < self.theta_freeze_at_t):
            for s in range(self.n_s):
                for sp in range(self.n_s):
                    self.C_T[s][a_t][sp] += self.eta * xi[s][sp]
            for sp in range(self.n_s):
                self.C_O[sp][o_next] += self.eta * b_post[sp]
            theta_updated = True

        if self.belief_update_enabled:
            self.b = list(b_post)

        return {
            "xi": xi,
            "belief_pre": b_pre,
            "belief_post": list(b_post),
            "belief_applied": list(self.b),
            "theta_updated": theta_updated,
        }

    def nll(self, p):
        return -math.log(max(p, self.log_eps))
