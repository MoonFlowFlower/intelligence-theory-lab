"""LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A — core mechanisms.

Everything follows artifacts/latent_multistep_consistency_residue_001a/
environment_preregistration.json (sha256 e9ba27c2...) exactly.

RNG discipline (preregistered):
  phase-1 stream:        default_rng(seed)
  eval sequences:        default_rng(seed*7919+202)
  belief init:           default_rng(seed*1000+13)
  learned-obs init:      default_rng(seed*1000+17)
  window-model inits:    default_rng(seed*1000+19/23/29) per order
  shuffled order:        default_rng(seed*1000+88)
  random fixed order:    default_rng(seed*1000+89)
  generic chunk order:   default_rng(seed*1000+90)
  uniform replay items:  default_rng(seed*1000+98)
  random replay items:   default_rng(seed*1000+99)
"""

import numpy as np

N = 16
NA = 3
NO = 5
D_MOTIF = (1, 5, 11)
EPS = 0.10
OBS_LABEL = (0, 1, 2, 3, 4, 2, 0, 3, 1, 4, 1, 3, 0, 4, 2, 0)
LR = 0.05
FLOOR = 1e-12
BURN_IN = 5
KDEPTH = 4
CHUNK_LEN = 40
HELDOUT = frozenset((s, a) for s in range(N) for a in range(NA)
                    if (3 * s + 7 * a) % 11 == 0)


def true_kernel():
    T = np.full((N, NA, N), EPS / N)
    for s in range(N):
        for a in range(NA):
            T[s, a, (s + D_MOTIF[a]) % N] += 1.0 - EPS
    return T


def obs_of(s):
    return OBS_LABEL[s]


def allowed_actions(s):
    return [a for a in range(NA) if (s, a) not in HELDOUT]


def generate_stream(rng, n_steps, exclude_heldout=True, T=None):
    T = true_kernel() if T is None else T
    s = int(rng.integers(N))
    out = []
    for _ in range(n_steps):
        acts = allowed_actions(s) if exclude_heldout else list(range(NA))
        a = int(acts[rng.integers(len(acts))])
        s2 = int(rng.choice(N, p=T[s, a]))
        out.append((s, a, s2))
        s = s2
    return out


def q1_true(T, s, a):
    q = np.zeros(NO)
    for s2 in range(N):
        q[obs_of(s2)] += T[s, a, s2]
    return q


def q4_true(T, s, acts4):
    v = np.zeros(N)
    v[s] = 1.0
    for a in acts4:
        v = v @ T[:, a, :]
    q = np.zeros(NO)
    for s2 in range(N):
        q[obs_of(s2)] += v[s2]
    return q


def softmax(z):
    z = z - z.max()
    p = np.exp(z)
    return p / p.sum()


OBS_MASK = np.stack([[1.0 if obs_of(s2) == o else 0.0 for s2 in range(N)]
                     for o in range(NO)])


# ------------------------------------------------------------ belief model

class BeliefModel:
    """Candidate-R architecture: learned transition logits, public obs map."""

    PARAMS = N * NA * N  # 768

    def __init__(self, seed, init_const=13):
        rng = np.random.default_rng(seed * 1000 + init_const)
        self.theta = rng.normal(0, 0.1, (N, NA, N))
        self.update_steps = 0

    def trans_matrix(self, a):
        return np.stack([softmax(self.theta[s, a]) for s in range(N)])

    def predict_obs(self, b, a):
        m = b @ self.trans_matrix(a)
        return OBS_MASK @ m, m

    def belief_update(self, b, a, o_next):
        _p, m = self.predict_obs(b, a)
        bb = m * OBS_MASK[o_next]
        t = bb.sum()
        return bb / t if t > 0 else np.full(N, 1.0 / N)

    def sgd_step_obs(self, b, a, o_next):
        p_obs, m = self.predict_obs(b, a)
        po = max(p_obs[o_next], FLOOR)
        dL_dm = -OBS_MASK[o_next] / po
        for s in range(N):
            if b[s] <= 1e-15:
                continue
            P = softmax(self.theta[s, a])
            dL_dP = b[s] * dL_dm
            self.theta[s, a] -= LR * (P * (dL_dP - float(dL_dP @ P)))
        self.update_steps += 1
        return -float(np.log(po))

    def multistep_loss_and_update(self, b0, actions, obs_targets):
        grads = np.zeros_like(self.theta)
        b = b0.copy()
        total = 0.0
        for a, o_t in zip(actions, obs_targets):
            p_obs, m = self.predict_obs(b, a)
            po = max(p_obs[o_t], FLOOR)
            total += -float(np.log(po))
            dL_dm = -OBS_MASK[o_t] / po
            for s in range(N):
                if b[s] <= 1e-15:
                    continue
                P = softmax(self.theta[s, a])
                dL_dP = b[s] * dL_dm
                grads[s, a] += P * (dL_dP - float(dL_dP @ P))
            b = m
        self.theta -= LR * grads
        self.update_steps += 1
        return total

    def predict_h4(self, b, acts4):
        v = b.copy()
        for a in acts4:
            v = v @ self.trans_matrix(a)
        return OBS_MASK @ v

    def snapshot(self):
        return {"theta": self.theta.copy(), "update_steps": self.update_steps}

    def restore(self, snap):
        self.theta = snap["theta"].copy()
        self.update_steps = snap["update_steps"]


class BeliefModelLearnedObs:
    """Larger-capacity baseline: learns the observation logits too (848 params).
    The public observation map is NOT given to this model."""

    PARAMS = N * NA * N + N * NO  # 848

    def __init__(self, seed):
        rng = np.random.default_rng(seed * 1000 + 17)
        self.theta = rng.normal(0, 0.1, (N, NA, N))
        self.theta_o = rng.normal(0, 0.1, (N, NO))
        self.update_steps = 0

    def obs_matrix(self):
        return np.stack([softmax(self.theta_o[s]) for s in range(N)])

    def trans_matrix(self, a):
        return np.stack([softmax(self.theta[s, a]) for s in range(N)])

    def predict_obs(self, b, a):
        m = b @ self.trans_matrix(a)
        O = self.obs_matrix()
        return m @ O, m

    def belief_update(self, b, a, o_next):
        _p, m = self.predict_obs(b, a)
        O = self.obs_matrix()
        bb = m * O[:, o_next]
        t = bb.sum()
        return bb / t if t > 0 else np.full(N, 1.0 / N)

    def sgd_step_obs(self, b, a, o_next):
        O = self.obs_matrix()
        m = b @ self.trans_matrix(a)
        p_obs = m @ O
        po = max(p_obs[o_next], FLOOR)
        dL_dm = -O[:, o_next] / po          # dNLL/dm(s')
        for s in range(N):
            if b[s] <= 1e-15:
                continue
            P = softmax(self.theta[s, a])
            dL_dP = b[s] * dL_dm
            self.theta[s, a] -= LR * (P * (dL_dP - float(dL_dP @ P)))
        # obs logits gradient: dNLL/dO[s',o] = -1[o=o_next]*m(s')/po
        for s2 in range(N):
            if m[s2] <= 1e-15:
                continue
            g = np.zeros(NO)
            g[o_next] = -m[s2] / po
            Po = O[s2]
            self.theta_o[s2] -= LR * (Po * (g - float(g @ Po)))
        self.update_steps += 1
        return -float(np.log(po))

    def predict_h4(self, b, acts4):
        v = b.copy()
        for a in acts4:
            v = v @ self.trans_matrix(a)
        return v @ self.obs_matrix()

    def snapshot(self):
        return {"theta": self.theta.copy(), "theta_o": self.theta_o.copy(),
                "update_steps": self.update_steps}


# ----------------------------------------------------------- window models

def code_of(o, a):
    return o * NA + a


NCODE = NO * NA  # 15


class Order2WindowModel:
    """Equal-parameter-budget baseline: logits[(code_{t-1}, code_t)] -> o'.
    1125 params. h=4 via exact joint propagation over (o_prev, o_cur)."""

    PARAMS = NCODE * NCODE * NO  # 1125

    def __init__(self, seed):
        rng = np.random.default_rng(seed * 1000 + 19)
        self.table = rng.normal(0, 0.1, (NCODE, NCODE, NO))
        self.update_steps = 0

    def predict(self, hist):
        (o1, a1), (o2, a2) = hist[-2], hist[-1]
        return softmax(self.table[code_of(o1, a1), code_of(o2, a2)])

    def sgd(self, hist, o_next):
        (o1, a1), (o2, a2) = hist[-2], hist[-1]
        c1, c2 = code_of(o1, a1), code_of(o2, a2)
        p = softmax(self.table[c1, c2])
        d = p.copy(); d[o_next] -= 1.0
        self.table[c1, c2] -= LR * d
        self.update_steps += 1
        return -float(np.log(max(p[o_next], FLOOR)))

    def predict_h4(self, hist, acts4):
        # joint over (o_{t-1}, o_t); first prediction uses real history,
        # later steps propagate predicted observation uncertainty exactly
        (o1, a1) = hist[-2]
        (o2, _a2_real) = hist[-1]
        joint = np.zeros((NO, NO)); joint[o1, o2] = 1.0
        prev_a, cur_a = a1, acts4[0]
        for j in range(4):
            nxt = np.zeros((NO, NO))
            pred = np.zeros(NO)
            for oa in range(NO):
                for ob in range(NO):
                    w = joint[oa, ob]
                    if w <= 0:
                        continue
                    p = softmax(self.table[code_of(oa, prev_a),
                                           code_of(ob, cur_a)])
                    pred += w * p
                    nxt[ob] += w * p
            if j == 3:
                return pred
            joint = nxt
            prev_a = cur_a
            cur_a = acts4[j + 1]

    def snapshot(self):
        return {"table": self.table.copy(), "update_steps": self.update_steps}


class InterpWindowModel:
    """Stronger sequence model without multi-step consistency: interpolated
    order-1/2/3 conditional tables with learned mixture weights."""

    def __init__(self, seed):
        rng = np.random.default_rng(seed * 1000 + 23)
        self.t1 = rng.normal(0, 0.1, (NCODE, NO))
        self.t2 = rng.normal(0, 0.1, (NCODE, NCODE, NO))
        self.t3 = rng.normal(0, 0.1, (NCODE, NCODE, NCODE, NO))
        self.w = np.zeros(3)
        self.update_steps = 0

    def _components(self, hist):
        c = [code_of(o, a) for (o, a) in hist[-3:]]
        p1 = softmax(self.t1[c[-1]])
        p2 = softmax(self.t2[c[-2], c[-1]]) if len(c) >= 2 else p1
        p3 = softmax(self.t3[c[-3], c[-2], c[-1]]) if len(c) >= 3 else p2
        return c, [p1, p2, p3]

    def predict(self, hist):
        _c, ps = self._components(hist)
        lam = softmax(self.w)
        return lam[0] * ps[0] + lam[1] * ps[1] + lam[2] * ps[2]

    def sgd(self, hist, o_next):
        c, ps = self._components(hist)
        lam = softmax(self.w)
        mix = lam[0] * ps[0] + lam[1] * ps[1] + lam[2] * ps[2]
        po = max(mix[o_next], FLOOR)
        for k, p in enumerate(ps):
            dmix = np.zeros(NO); dmix[o_next] = -lam[k] / po
            g = p * (dmix - float(dmix @ p))
            if k == 0:
                self.t1[c[-1]] -= LR * g
            elif k == 1 and len(c) >= 2:
                self.t2[c[-2], c[-1]] -= LR * g
            elif k == 2 and len(c) >= 3:
                self.t3[c[-3], c[-2], c[-1]] -= LR * g
        dw = np.array([-(p[o_next]) / po for p in ps]) * lam
        dw -= lam * float(dw.sum())
        self.w -= LR * dw
        self.update_steps += 1
        return -float(np.log(po))

    def predict_h4(self, hist, acts4):
        # exact propagation over the last-3 observation joint
        os3 = [o for (o, _a) in hist[-3:]]
        as3 = [a for (_o, a) in hist[-3:]]
        joint = np.zeros((NO, NO, NO))
        joint[os3[0], os3[1], os3[2]] = 1.0
        acts_hist = list(as3)
        for j in range(4):
            a_next = acts4[j]
            nxt = np.zeros((NO, NO, NO))
            pred = np.zeros(NO)
            for oa in range(NO):
                for ob in range(NO):
                    for oc in range(NO):
                        w = joint[oa, ob, oc]
                        if w <= 0:
                            continue
                        h_full = [(oa, acts_hist[-3]), (ob, acts_hist[-2]),
                                  (oc, a_next)]
                        p = self.predict(h_full)
                        pred += w * p
                        nxt[ob, oc] += w * p
            if j == 3:
                return pred
            joint = nxt
            acts_hist.append(a_next)

    def snapshot(self):
        return {"w": self.w.copy(), "update_steps": self.update_steps}


# -------------------------------------------------------- sequence stores

class SeqStores:
    """All cache/retrieval/table controls built from the phase-1 stream."""

    def __init__(self, stream):
        self.oa = [(obs_of(s), a) for (s, a, _x) in stream]
        self.next_obs = [obs_of(s2) for (_s, _a, s2) in stream]
        self.windows = {}
        for Lw in (12, 8, 4, 2):
            for t in range(Lw - 1, len(self.oa)):
                key = (Lw, tuple(self.oa[t - Lw + 1:t + 1]))
                self.windows.setdefault(key, np.zeros(NO))
                self.windows[key][self.next_obs[t]] += 1
        self.marginal = np.zeros(NO)
        for o in self.next_obs:
            self.marginal[o] += 1
        self.marginal /= self.marginal.sum()
        self._w8_codes = np.array(
            [[code_of(o, a) for (o, a) in self.oa[t - 7:t + 1]]
             for t in range(7, len(self.oa))], dtype=np.int16)
        self._w8_next = np.array(self.next_obs[7:], dtype=np.int16)
        # (o,a) -> o' conditional (for table controls and h4 chaining)
        self.oa_counts = np.zeros((NO, NA, NO))
        for (o, a), o2 in zip(self.oa, self.next_obs):
            self.oa_counts[o, a, o2] += 1

    def _match(self, hist, lengths, miss):
        for Lw in lengths:
            if len(hist) >= Lw:
                k = (Lw, tuple(hist[-Lw:]))
                if k in self.windows:
                    c = self.windows[k]
                    return c / c.sum()
        return miss

    def hidden_state_cache(self, hist):
        return self._match(hist, (8, 4, 2), np.full(NO, 1.0 / NO))

    def prefix_cache(self, hist):
        return self._match(hist, (8,), np.full(NO, 1.0 / NO))

    def sequence_lookup(self, hist):
        return self._match(hist, (8, 4, 2), self.marginal.copy())

    def episodic_retrieval(self, hist):
        return self._match(hist, (12, 8, 4, 2), self.marginal.copy())

    def knn(self, hist, k):
        if len(hist) < 8:
            return self.marginal.copy()
        q = np.array([code_of(o, a) for (o, a) in hist[-8:]], dtype=np.int16)
        dist = (self._w8_codes != q).sum(axis=1)
        idx = np.argsort(dist, kind="stable")[:k]
        c = np.zeros(NO)
        for i in idx:
            c[self._w8_next[i]] += 1
        return c / c.sum()

    # table controls -------------------------------------------------
    def count_table(self, hist):
        o, a = hist[-1]
        c = self.oa_counts[o, a]
        return (c + 1.0) / (c.sum() + NO)

    def graph_lookup(self, hist):
        o, a = hist[-1]
        c = self.oa_counts[o, a]
        return c / c.sum() if c.sum() > 0 else np.full(NO, 1.0 / NO)

    def compressed_map(self):
        M = self.oa_counts.reshape(NCODE, NO)
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        Mk = (U[:, :3] * S[:3]) @ Vt[:3]
        Mk = np.clip(Mk, 0, None) + 1e-6
        Mk = Mk / Mk.sum(axis=1, keepdims=True)

        def fn(hist):
            o, a = hist[-1]
            return Mk[code_of(o, a)]
        return fn

    def chain_conditional(self, laplace):
        """(o,a)->o' conditional used for h>1 rollout chaining."""
        cond = np.zeros((NO, NA, NO))
        for o in range(NO):
            for a in range(NA):
                c = self.oa_counts[o, a]
                if laplace:
                    cond[o, a] = (c + 1.0) / (c.sum() + NO)
                elif c.sum() > 0:
                    cond[o, a] = c / c.sum()
                else:
                    cond[o, a] = np.full(NO, 1.0 / NO)
        return cond


def store_h4(first_step_fn, cond, hist, acts4):
    """Retrieval/table h=4 rollout: step 1 native, steps 2..4 chained via
    the store's own (o,a)->o' conditional (interpretation lock)."""
    q = first_step_fn(hist)
    for j in range(1, 4):
        q = np.array([sum(q[o] * cond[o, acts4[j], o2] for o in range(NO))
                      for o2 in range(NO)])
    return q
