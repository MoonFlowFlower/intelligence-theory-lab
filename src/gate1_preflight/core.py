"""GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001 — core mechanisms.

Everything here follows artifacts/gate1_replay_consolidation_exec_taskcard_001/
environment_preregistration.json exactly. No hyperparameter, rule, or fallback
in this file may deviate from that frozen record.

RNG discipline (all preregistered, derived from run seed):
  trajectory phase-1: default_rng(seed)
  trajectory phase-2: default_rng(seed*31+1)
  A model init:       default_rng(seed*1000+7)
  B model init:       default_rng(seed*1000+13)
  eval sequences:     default_rng(seed*7919+101)
  salience sampling:  default_rng(seed*1000+77)
  shuffle orders:     default_rng(seed*1000+88)
  random replay:      default_rng(seed*1000+99)
  synthetic library:  default_rng(seed*1000+55)
  post-hoc generator: default_rng(seed*1000+66)
"""

import numpy as np

N_STATES = 12
N_ACTIONS = 3
D_PHASE1 = (1, 4, 9)
D_PHASE2 = (2, 7, 5)
EPS_SLIP = 0.15
N_OBS = 4  # B-variant aliasing: o = s mod 4
EMB_DIM = 8
LR = 0.05
PROB_FLOOR = 1e-12

HELDOUT = frozenset((s, a) for s in range(N_STATES) for a in range(N_ACTIONS)
                    if (2 * s + 5 * a) % 9 == 0)


def true_kernel(displacements):
    """T[s,a,s'] for the ring environment."""
    T = np.full((N_STATES, N_ACTIONS, N_STATES), EPS_SLIP / N_STATES)
    for s in range(N_STATES):
        for a in range(N_ACTIONS):
            T[s, a, (s + displacements[a]) % N_STATES] += 1.0 - EPS_SLIP
    return T


def allowed_actions(s):
    return [a for a in range(N_ACTIONS) if (s, a) not in HELDOUT]


def generate_stream(seed_rng, displacements, n_steps):
    """Uniform-random behavior over allowed (non-heldout) actions."""
    T = true_kernel(displacements)
    s = int(seed_rng.integers(N_STATES))
    out = []
    for _ in range(n_steps):
        acts = allowed_actions(s)
        a = int(acts[seed_rng.integers(len(acts))])
        s2 = int(seed_rng.choice(N_STATES, p=T[s, a]))
        out.append((s, a, s2))
        s = s2
    return out


# Observation map per ENV-PREREG-AMENDMENT-001 (human-owner approved):
# fixed irregular labeling; classes {0,4,9},{1,6,11},{2,5,8},{3,7,10} are not
# arithmetic progressions, so the observation process is not lumpable under
# the additive ring dynamics and alias disambiguation requires memory.
OBS_LABEL = (0, 1, 2, 3, 0, 2, 1, 3, 2, 0, 3, 1)


def obs_of(s):
    return OBS_LABEL[s]


# ---------------------------------------------------------------- A model

class CompositionalSlowModel:
    """logits(s'|s,a) = (e_s * w_a) . v_s'  — generic, no ring topology encoded."""

    def __init__(self, seed):
        rng = np.random.default_rng(seed * 1000 + 7)
        self.e = rng.normal(0, 0.1, (N_STATES, EMB_DIM))
        self.w = rng.normal(0, 0.1, (N_ACTIONS, EMB_DIM))
        self.v = rng.normal(0, 0.1, (N_STATES, EMB_DIM))
        self.update_steps = 0

    def logits(self, s, a):
        return (self.e[s] * self.w[a]) @ self.v.T

    def probs(self, s, a):
        z = self.logits(s, a)
        z = z - z.max()
        p = np.exp(z)
        return p / p.sum()

    def sgd_step(self, s, a, s_next):
        p = self.probs(s, a)
        d = p.copy()
        d[s_next] -= 1.0                    # dL/dlogits
        ew = self.e[s] * self.w[a]
        grad_v = np.outer(d, ew)            # (12, K)
        grad_ew = d @ self.v                # (K,)
        grad_e = grad_ew * self.w[a]
        grad_w = grad_ew * self.e[s]
        self.v -= LR * grad_v
        self.e[s] -= LR * grad_e
        self.w[a] -= LR * grad_w
        self.update_steps += 1

    def item_nll(self, s, a, s_next):
        return -float(np.log(max(self.probs(s, a)[s_next], PROB_FLOOR)))

    def snapshot(self):
        return {"e": self.e.copy(), "w": self.w.copy(), "v": self.v.copy(),
                "update_steps": self.update_steps}

    def restore(self, snap):
        self.e = snap["e"].copy(); self.w = snap["w"].copy()
        self.v = snap["v"].copy(); self.update_steps = snap["update_steps"]


def exact_nll_A(prob_fn, T_true, queries):
    """Exact expected NLL of a predictive fn against the true kernel."""
    tot = 0.0
    for (s, a) in queries:
        p = np.maximum(prob_fn(s, a), PROB_FLOOR)
        tot += -float(T_true[s, a] @ np.log(p))
    return tot / len(queries)


# ------------------------------------------------- A lookup/cache controls

class CountStore:
    """Shared accumulator for all A-side lookup controls."""

    def __init__(self):
        self.counts = np.zeros((N_STATES, N_ACTIONS, N_STATES))
        self.episodes = []          # chronological (s,a,s') list

    def add(self, s, a, s2):
        self.counts[s, a, s2] += 1
        self.episodes.append((s, a, s2))

    # 1. runtime graph lookup / 8. direct episodic graph traversal /
    # direct episodic retrieval (documented functional equivalence)
    def graph_lookup(self, s, a):
        c = self.counts[s, a]
        n = c.sum()
        return c / n if n > 0 else np.full(N_STATES, 1.0 / N_STATES)

    # 2. transition-table lookup (same keying; equivalence documented)
    def transition_table(self, s, a):
        return self.graph_lookup(s, a)

    # 3. successor-map cache
    def successor_map(self, s, a):
        succ = self.counts[s, a] > 0
        if succ.sum() == 0:
            return np.full(N_STATES, 1.0 / N_STATES)
        p = succ.astype(float)
        return p / p.sum()

    # 4. predecessor-map cache
    def predecessor_map(self, s, a):
        return self.successor_map(s, a)  # uniform over states whose
        # predecessor set contains (s,a) == observed successor set; documented.

    # 5. finite-state transition planner (mode successor, Laplace 0.01)
    def fsm_planner(self, s, a):
        c = self.counts[s, a]
        p = np.full(N_STATES, 0.01 / N_STATES)
        if c.sum() > 0:
            p[int(c.argmax())] += 0.99
        else:
            p = np.full(N_STATES, 1.0 / N_STATES)
        return p / p.sum()

    # 6. count-table predictor (Laplace alpha=1)
    def count_table(self, s, a):
        c = self.counts[s, a]
        return (c + 1.0) / (c.sum() + N_STATES)

    # 7. compressed predictive-map memory (rank-4 SVD)
    def compressed_map(self):
        M = self.counts.reshape(N_STATES * N_ACTIONS, N_STATES)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        Mk = (U[:, :4] * S[:4]) @ Vt[:4]
        Mk = np.clip(Mk, 0, None) + 1e-6
        Mk = Mk / Mk.sum(axis=1, keepdims=True)

        def fn(s, a):
            return Mk[s * N_ACTIONS + a]
        return fn


# ------------------------------------------------------------- B model

class BeliefPredictor:
    """Learned transition logits + public observation map o = s mod 4."""

    def __init__(self, seed):
        rng = np.random.default_rng(seed * 1000 + 13)
        self.theta = rng.normal(0, 0.1, (N_STATES, N_ACTIONS, N_STATES))
        self.update_steps = 0

    def trans(self, s, a):
        z = self.theta[s, a] - self.theta[s, a].max()
        p = np.exp(z)
        return p / p.sum()

    def trans_matrix(self, a):
        return np.stack([self.trans(s, a) for s in range(N_STATES)])

    def predict_obs(self, belief, a):
        m = belief @ self.trans_matrix(a)            # next-state marginal
        p = np.zeros(N_OBS)
        for s2 in range(N_STATES):
            p[obs_of(s2)] += m[s2]
        return p, m

    def belief_update(self, belief, a, o_next):
        _, m = self.predict_obs(belief, a)
        mask = np.array([1.0 if obs_of(s2) == o_next else 0.0
                         for s2 in range(N_STATES)])
        b = m * mask
        tot = b.sum()
        return b / tot if tot > 0 else np.full(N_STATES, 1.0 / N_STATES)

    def sgd_step_obs(self, belief, a, o_next):
        """Truncated one-step gradient on next-observation NLL."""
        p_obs, m = self.predict_obs(belief, a)
        po = max(p_obs[o_next], PROB_FLOOR)
        dL_dm = np.array([-(1.0 if obs_of(s2) == o_next else 0.0) / po
                          for s2 in range(N_STATES)])
        for s in range(N_STATES):
            if belief[s] <= 1e-15:
                continue
            P = self.trans(s, a)
            dL_dP = belief[s] * dL_dm
            g = P * (dL_dP - float(dL_dP @ P))    # softmax row jacobian
            self.theta[s, a] -= LR * g
        self.update_steps += 1
        return -float(np.log(po))

    def multistep_loss_and_update(self, belief, actions, obs_targets):
        """Candidate B consistency loss: horizons j=1..len, action-conditioned
        rollout, no intermediate observation conditioning. One SGD step on the
        summed loss (gradient accumulated per horizon, truncated as in the
        one-step rule applied to each horizon's marginal)."""
        grads = np.zeros_like(self.theta)
        b = belief.copy()
        total = 0.0
        for j, (a, o_t) in enumerate(zip(actions, obs_targets)):
            p_obs, m = self.predict_obs(b, a)
            po = max(p_obs[o_t], PROB_FLOOR)
            total += -float(np.log(po))
            dL_dm = np.array([-(1.0 if obs_of(s2) == o_t else 0.0) / po
                              for s2 in range(N_STATES)])
            for s in range(N_STATES):
                if b[s] <= 1e-15:
                    continue
                P = self.trans(s, a)
                dL_dP = b[s] * dL_dm
                grads[s, a] += P * (dL_dP - float(dL_dP @ P))
            b = m  # action-conditioned rollout, no observation conditioning
        self.theta -= LR * grads
        self.update_steps += 1
        return total

    def snapshot(self):
        return {"theta": self.theta.copy(), "update_steps": self.update_steps}

    def restore(self, snap):
        self.theta = snap["theta"].copy()
        self.update_steps = snap["update_steps"]


# ----------------------------------------------- B lookup/cache controls

class SequenceStore:
    """Phase-1 (o,a) window stores for all B-side cache/retrieval controls."""

    def __init__(self, stream):
        self.oa = [(obs_of(s), a) for (s, a, _s2) in stream]
        self.next_obs = [obs_of(s2) for (_s, _a, s2) in stream]
        self.windows = {}            # exact window (len 8/4/2) -> obs counts
        for L in (8, 4, 2):
            for t in range(L - 1, len(self.oa)):
                key = (L, tuple(self.oa[t - L + 1:t + 1]))
                self.windows.setdefault(key, np.zeros(N_OBS))
                self.windows[key][self.next_obs[t]] += 1
        self.marginal = np.zeros(N_OBS)
        for o in self.next_obs:
            self.marginal[o] += 1
        self.marginal /= self.marginal.sum()
        self.w8 = [(tuple(self.oa[t - 7:t + 1]), self.next_obs[t])
                   for t in range(7, len(self.oa))]
        # vectorized window codes for kNN (pair (o,a) -> o*N_ACTIONS+a);
        # identical distances and stable tie-break as the tuple version
        self._w8_codes = np.array([[o * 3 + a for (o, a) in w]
                                   for (w, _n) in self.w8], dtype=np.int16)
        self._w8_next = np.array([n for (_w, n) in self.w8], dtype=np.int16)

    @staticmethod
    def _key_of(history, L):
        if len(history) < L:
            return None
        return (L, tuple(history[-L:]))

    def hidden_state_cache(self, history):
        """Longest-suffix match (8 then 4 then 2); uniform on total miss.
        Functional note: keyed cache of phase-1 predictive state."""
        for L in (8, 4, 2):
            k = self._key_of(history, L)
            if k is not None and k in self.windows:
                c = self.windows[k]
                return c / c.sum()
        return np.full(N_OBS, 1.0 / N_OBS)

    def prefix_cache(self, history):
        """Exact window-of-8 keying only; uniform on miss (near-equivalence
        to hidden_state_cache documented)."""
        k = self._key_of(history, 8)
        if k is not None and k in self.windows:
            c = self.windows[k]
            return c / c.sum()
        return np.full(N_OBS, 1.0 / N_OBS)

    def knn_retrieval(self, history, k=5):
        if len(history) < 8:
            return self.marginal.copy()
        q = np.array([o * 3 + a for (o, a) in history[-8:]], dtype=np.int16)
        dist = (self._w8_codes != q).sum(axis=1)
        idx = np.argsort(dist, kind="stable")[:k]   # stable = chronological
        c = np.zeros(N_OBS)                          # tie-break, as before
        for i in idx:
            c[self._w8_next[i]] += 1
        return c / c.sum()

    def sequence_lookup(self, history):
        """Exact match with predeclared backoff 8 -> 4 -> 2 -> marginal."""
        for L in (8, 4, 2):
            k = self._key_of(history, L)
            if k is not None and k in self.windows:
                c = self.windows[k]
                return c / c.sum()
        return self.marginal.copy()

    def nn1_retrieval(self, history):
        return self.knn_retrieval(history, k=1)


# ----------------------------------------------------- exact B evaluation

def stationary_distribution(T_true):
    """Stationary dist of phase-1 chain under uniform-allowed behavior."""
    P = np.zeros((N_STATES, N_STATES))
    for s in range(N_STATES):
        acts = allowed_actions(s)
        for a in acts:
            P[s] += T_true[s, a] / len(acts)
    pi = np.full(N_STATES, 1.0 / N_STATES)
    for _ in range(500):
        pi = pi @ P
    return pi / pi.sum()


def true_obs_dist(T_true, s, a):
    q = np.zeros(N_OBS)
    for s2 in range(N_STATES)