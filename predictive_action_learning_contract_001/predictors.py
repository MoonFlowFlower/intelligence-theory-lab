"""Predictor interface, the frozen-skeleton predictor, and all required baselines
(task card section 9) plus ablation variants (section 10).

Every predictor exposes the same interface so that all runs produce comparable
trace records and metrics. Predictors never see the true hidden state and never
see o_{t+1} before observe() — except OracleLeakPredictor, which is a deliberate
sanity leak that the harness must catch via the NLL floor.
"""

from .environment import counter_rng
from .skeleton import FrozenSkeleton


class BasePredictor:
    predictor_id = "base"
    replayable_skeleton = False
    declares_retrieval = False

    def reset(self, o0):
        raise NotImplementedError

    def predict_all(self, t):
        """Return (pobs_by_a, bhat_by_a_or_None) for all actions, same history."""
        raise NotImplementedError

    def observe(self, t, a_t, o_next):
        """Consume revealed o_{t+1}. Returns update internals dict."""
        raise NotImplementedError

    def chosen_action_label(self, t, a_t):
        """Action label whose prediction this predictor commits to for step t."""
        return a_t

    def belief(self):
        return None

    def theta_T(self):
        return None

    def theta_O(self):
        return None

    def pop_retrieval_events(self):
        return []

    def state_snapshot(self):
        return None


class SkeletonPredictor(BasePredictor):
    """The frozen contract learner. action_input_mode:
       'true'     - core skeleton
       'shuffled' - baseline 2 / ablation 2: per-step random action label fed in
       'none'     - ablation 1: action input removed (pooled table)
    """
    replayable_skeleton = True

    def __init__(self, cfg, action_input_mode="true", shuffle_seed=None,
                 theta_update_enabled=True, theta_freeze_at_t=None,
                 belief_update_enabled=True, predictor_id="frozen_skeleton",
                 init_seed=None):
        self.cfg = cfg
        self.mode = action_input_mode
        self.shuffle_seed = shuffle_seed
        self.init_seed = init_seed
        self.predictor_id = predictor_id
        n_a = 1 if action_input_mode == "none" else cfg.N_A
        self.core = FrozenSkeleton(
            cfg.N_S, n_a, cfg.N_O, cfg.ALPHA_PSEUDOCOUNT, cfg.ETA_LEARNING_RATE,
            cfg.LOG_EPS, theta_update_enabled=theta_update_enabled,
            theta_freeze_at_t=theta_freeze_at_t,
            belief_update_enabled=belief_update_enabled)
        if init_seed is not None and cfg.INIT_JITTER > 0.0:
            # Declared symmetry-breaking initialization (see config.py). Drawn in
            # fixed nested order so traces replay exactly from (params, seed).
            j = cfg.INIT_JITTER
            rt = counter_rng(init_seed, -1, "init_T")
            for s in range(cfg.N_S):
                for a in range(n_a):
                    for sp in range(cfg.N_S):
                        self.core.C_T[s][a][sp] = (
                            cfg.ALPHA_PSEUDOCOUNT * (1.0 + rt.uniform(-j, j)))
            # Anchored emission prior (see config.INIT_OBS_ANCHOR_KAPPA):
            # informative pseudo-counts in the skeleton's own vocabulary; fixes
            # the latent labeling gauge, encodes no transition rule.
            K = cfg.INIT_OBS_ANCHOR_KAPPA
            for sp in range(cfg.N_S):
                for o in range(cfg.N_O):
                    self.core.C_O[sp][o] = (
                        cfg.ALPHA_PSEUDOCOUNT * (1.0 + (K if o == sp else 0.0)))

    def reset(self, o0):
        # Initial Bayes conditioning on o_0 (uniform prior x O_theta(o0|s)).
        O = self.core.theta_O()
        b = [self.core.b[s] * O[s][o0] for s in range(self.cfg.N_S)]
        z = sum(b)
        self.core.b = [x / z for x in b]

    def _fed_action(self, t, a_t):
        if self.mode == "true":
            return a_t
        if self.mode == "none":
            return 0
        return counter_rng(self.shuffle_seed, t, "shuffle").randrange(self.cfg.N_A)

    def chosen_action_label(self, t, a_t):
        return self._fed_action(t, a_t)

    def predict_all(self, t):
        bhat_by_a, pobs_by_a = self.core.predict_all_actions()
        if self.mode == "none":
            # honest action-blind map: identical prediction for every external action
            pobs_by_a = {a: list(pobs_by_a[0]) for a in range(self.cfg.N_A)}
            bhat_by_a = {a: list(bhat_by_a[0]) for a in range(self.cfg.N_A)}
        return pobs_by_a, bhat_by_a

    def observe(self, t, a_t, o_next):
        return self.core.update(self._fed_action(t, a_t), o_next, t)

    def belief(self):
        return list(self.core.b)

    def theta_T(self):
        return self.core.theta_T()

    def theta_O(self):
        return self.core.theta_O()

    def state_snapshot(self):
        return {
            "b": list(self.core.b),
            "C_T": [[list(r) for r in a] for a in self.core.C_T],
            "C_O": [list(r) for r in self.core.C_O],
        }


class PassiveObsMarkovPredictor(BasePredictor):
    """Baseline 1: passive next-observation predictor, no action input.
    First-order observation Markov counts P(o_{t+1}|o_t)."""
    predictor_id = "baseline_passive_obs_markov"

    def __init__(self, cfg):
        self.cfg = cfg
        self.M = [[cfg.ALPHA_PSEUDOCOUNT] * cfg.N_O for _ in range(cfg.N_O)]
        self.last_obs = None

    def reset(self, o0):
        self.last_obs = o0

    def predict_all(self, t):
        row = self.M[self.last_obs]
        tot = sum(row)
        p = [c / tot for c in row]
        return {a: list(p) for a in range(self.cfg.N_A)}, None

    def observe(self, t, a_t, o_next):
        self.M[self.last_obs][o_next] += 1.0
        self.last_obs = o_next
        return {}


class ActionTokenOnlyPredictor(BasePredictor):
    """Baseline 3: action-token-only predictor P(o_{t+1}|a_t); no state, no
    transition semantics. Under confounding it inherits spurious correlation."""
    predictor_id = "baseline_action_token_only"

    def __init__(self, cfg):
        self.cfg = cfg
        self.K = [[cfg.ALPHA_PSEUDOCOUNT] * cfg.N_O for _ in range(cfg.N_A)]

    def reset(self, o0):
        pass

    def predict_all(self, t):
        out = {}
        for a in range(self.cfg.N_A):
            tot = sum(self.K[a])
            out[a] = [c / tot for c in self.K[a]]
        return out, None

    def observe(self, t, a_t, o_next):
        self.K[a_t][o_next] += 1.0
        return {}


RETRIEVAL_K_MAX = 3        # pre-declared, not tuned post-hoc
RETRIEVAL_MIN_MATCH = 3.0  # minimum raw match mass before backoff stops


class NearestHistoryRetrievalPredictor(BasePredictor):
    """Baseline 4: nearest-history / RAG-like suffix lookup with backoff.
    Context of length k = ((o,a) pairs for the last k steps, candidate action in
    the final slot). Longest suffix with enough matches wins; add-1 smoothing."""
    predictor_id = "baseline_nearest_history_retrieval"
    declares_retrieval = True

    def __init__(self, cfg):
        self.cfg = cfg
        self.counts = {k: {} for k in range(1, RETRIEVAL_K_MAX + 1)}
        self.marginal = [cfg.ALPHA_PSEUDOCOUNT] * cfg.N_O
        self.hist = []  # list of (o_t, a_t)
        self.cur_obs = None
        self._events = []

    def reset(self, o0):
        self.cur_obs = o0

    def _context(self, k, candidate_a):
        if len(self.hist) < k - 1:
            return None
        tail = self.hist[len(self.hist) - (k - 1):] if k > 1 else []
        return tuple(tail) + ((self.cur_obs, candidate_a),)

    def _predict_one(self, t, a):
        for k in range(RETRIEVAL_K_MAX, 0, -1):
            key = self._context(k, a)
            if key is None:
                continue
            row = self.counts[k].get(key)
            if row and sum(row) >= RETRIEVAL_MIN_MATCH:
                self._events.append({"t": t, "kind": "suffix_match", "k": k,
                                     "matches": sum(row)})
                tot = sum(row) + self.cfg.N_O
                return [(c + 1.0) / tot for c in row]
        self._events.append({"t": t, "kind": "marginal_fallback", "k": 0,
                             "matches": sum(self.marginal)})
        tot = sum(self.marginal)
        return [c / tot for c in self.marginal]

    def predict_all(self, t):
        return {a: self._predict_one(t, a) for a in range(self.cfg.N_A)}, None

    def observe(self, t, a_t, o_next):
        for k in range(1, RETRIEVAL_K_MAX + 1):
            key = self._context(k, a_t)
            if key is None:
                continue
            row = self.counts[k].setdefault(key, [0.0] * self.cfg.N_O)
            row[o_next] += 1.0
        self.marginal[o_next] += 1.0
        self.hist.append((self.cur_obs, a_t))
        self.cur_obs = o_next
        return {}

    def pop_retrieval_events(self):
        ev, self._events = self._events, []
        return ev


class HardcodedRuleFilterPredictor(BasePredictor):
    """Baseline 5: hard-coded rule baseline. A Bayes filter whose T and O are the
    TRUE initial environment parameters, frozen forever (never adapts to any
    shift). This is the strongest hard-coded variant; it must fail under rule
    shift if adaptation matters."""
    predictor_id = "baseline_hardcoded_true_rule"

    def __init__(self, cfg, target_fn, eps_T, eps_O):
        self.cfg = cfg
        n_s, n_o = cfg.N_S, cfg.N_O
        self.T = [[[0.0] * n_s for _ in range(cfg.N_A)] for _ in range(n_s)]
        for s in range(n_s):
            for a in range(cfg.N_A):
                tgt = target_fn(s, a)
                for sp in range(n_s):
                    self.T[s][a][sp] = (1.0 - eps_T) if sp == tgt else eps_T / (n_s - 1)
        self.O = [[eps_O / (n_o - 1)] * n_o for _ in range(n_s)]
        for s in range(n_s):
            self.O[s][s] = 1.0 - eps_O
        self.b = [1.0 / n_s] * n_s

    def reset(self, o0):
        b = [self.b[s] * self.O[s][o0] for s in range(self.cfg.N_S)]
        z = sum(b)
        self.b = [x / z for x in b]

    def predict_all(self, t):
        pobs, bhat = {}, {}
        for a in range(self.cfg.N_A):
            bh = [0.0] * self.cfg.N_S
            for s in range(self.cfg.N_S):
                for sp in range(self.cfg.N_S):
                    bh[sp] += self.b[s] * self.T[s][a][sp]
            po = [0.0] * self.cfg.N_O
            for sp in range(self.cfg.N_S):
                for o in range(self.cfg.N_O):
                    po[o] += bh[sp] * self.O[sp][o]
            bhat[a], pobs[a] = bh, po
        return pobs, bhat

    def observe(self, t, a_t, o_next):
        nb = [0.0] * self.cfg.N_S
        for s in range(self.cfg.N_S):
            for sp in range(self.cfg.N_S):
                nb[sp] += self.b[s] * self.T[s][a_t][sp] * self.O[sp][o_next]
        z = sum(nb)
        self.b = [x / z for x in nb]
        return {}

    def belief(self):
        return list(self.b)


class OracleLeakPredictor(BasePredictor):
    """Baseline 8: oracle-leak sanity baseline. Deliberately peeks at the
    environment's deterministic counter-based draw for o_{t+1}. Its performance
    is impossible for any legitimate predictor; the harness MUST flag it via the
    pre-declared NLL floor. Never use outside the sanity check."""
    predictor_id = "baseline_oracle_leak_sanity"

    def __init__(self, cfg, env, leak_prob=0.95):
        self.cfg, self.env, self.leak_prob = cfg, env, leak_prob

    def reset(self, o0):
        pass

    def predict_all(self, t):
        out = {}
        for a in range(self.cfg.N_A):
            o_peek = self.env.peek_transition(t, a)
            p = [(1.0 - self.leak_prob) / (self.cfg.N_O - 1)] * self.cfg.N_O
            p[o_peek] = self.leak_prob
            out[a] = p
        return out, None

    def observe(self, t, a_t, o_next):
        return {}


class RetrievalReplacedUpdatePredictor(NearestHistoryRetrievalPredictor):
    """Ablation 6: internal belief/theta update replaced with retrieval while the
    run spec (incorrectly) declares retrieval_enabled=false. The validator must
    catch the contradiction from logged retrieval events."""
    predictor_id = "ablation_retrieval_replaced_update"
    declares_retrieval = False  # the lie under test
