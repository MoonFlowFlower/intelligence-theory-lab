"""Finite hidden-state environment, regimes, perturbations, and action policies.

Randomness is counter-based: every draw is a pure function of
(seed, t, tag) via sha256, so any run can be reconstructed mid-stream from a
trace without hidden RNG state, independent of process or PYTHONHASHSEED.
"""

import hashlib
import random


def counter_rng(seed, t, tag):
    h = hashlib.sha256(f"{seed}|{t}|{tag}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def _target_as_cycle(s, a):       # AS-CYCLE-001
    return [(s - 1) % 3, (s + 1) % 3, s][a]          # left, right, stay


def _target_as_cycle_rev(s, a):   # left/right swapped (transition reversal)
    return [(s + 1) % 3, (s - 1) % 3, s][a]


def _target_as_swap(s, a):        # AS-SWAP-001
    return [(s + 1) % 3, s, (s - 1) % 3][a]


def _target_hidden_rule(s, a):    # HIDDEN-RULE-001 post-shift table
    return [s, (s - 1) % 3, (s + 1) % 3][a]


def _target_null(s, a):           # NULL-001 / TRAP-001: action causally inert
    return (s + 1) % 3


class FiniteEnv:
    """Finite latent-state environment with declared rule id and perturbation schedule.

    The true state s_true is environment-private. It is never given to any
    predictor. The trap policy receives it because the confounder is part of
    the environment, not of the learner.
    """

    def __init__(self, env_rule_id, seed, eps_T, eps_O,
                 shift_t=None, ambig_t=None, n_s=3, n_o=3):
        self.env_rule_id = env_rule_id
        self.seed = seed
        self.eps_T = eps_T
        self.eps_O = eps_O
        self.shift_t = shift_t
        self.ambig_t = ambig_t
        self.n_s, self.n_o = n_s, n_o
        self.s_true = counter_rng(seed, -1, "init_state").randrange(n_s)

    def _target_fn(self, t):
        r = self.env_rule_id
        if r == "AS-CYCLE-001":
            return _target_as_cycle
        if r == "AS-SWAP-001":
            return _target_as_swap
        if r in ("NULL-001", "TRAP-001"):
            return _target_null
        if r == "SHIFT-REVERSAL-001":
            return _target_as_cycle if (self.shift_t is None or t < self.shift_t) else _target_as_cycle_rev
        if r == "HIDDEN-RULE-001":
            return _target_as_cycle if (self.shift_t is None or t < self.shift_t) else _target_hidden_rule
        if r == "AMBIG-001":
            return _target_as_cycle
        raise ValueError(f"unknown env_rule_id {r}")

    def _obs_row(self, sp, t):
        """Emission distribution for state sp at time t."""
        if self.env_rule_id == "AMBIG-001" and self.ambig_t is not None and t >= self.ambig_t and sp in (1, 2):
            return [0.05, 0.475, 0.475]
        row = [self.eps_O / 2.0] * self.n_o
        row[sp] = 1.0 - self.eps_O
        return row

    def sample_initial_obs(self):
        row = self._obs_row(self.s_true, 0)
        return _sample(counter_rng(self.seed, -1, "init_obs"), row)

    def transition(self, t, a):
        """Advance hidden state with action a at step t; emit o_{t+1}.

        Must only be called AFTER the PRE_STEP commitment for step t."""
        target = self._target_fn(t)(self.s_true, a)
        rng_s = counter_rng(self.seed, t, "trans")
        if rng_s.random() < 1.0 - self.eps_T:
            s_next = target
        else:
            others = [s for s in range(self.n_s) if s != target]
            s_next = others[rng_s.randrange(len(others))]
        row = self._obs_row(s_next, t + 1)
        o_next = _sample(counter_rng(self.seed, t, "obs"), row)
        self.s_true = s_next
        return o_next, s_next

    def peek_transition(self, t, a):
        """Deliberate leak used ONLY by the oracle-leak sanity baseline.

        Computes the same deterministic counter-based draw the env will make,
        without advancing state. The harness must detect the resulting
        impossible performance via the NLL floor."""
        target = self._target_fn(t)(self.s_true, a)
        rng_s = counter_rng(self.seed, t, "trans")
        if rng_s.random() < 1.0 - self.eps_T:
            s_next = target
        else:
            others = [s for s in range(self.n_s) if s != target]
            s_next = others[rng_s.randrange(len(others))]
        row = self._obs_row(s_next, t + 1)
        return _sample(counter_rng(self.seed, t, "obs"), row)


def _sample(rng, dist):
    u = rng.random()
    acc = 0.0
    for i, p in enumerate(dist):
        acc += p
        if u < acc:
            return i
    return len(dist) - 1


# ---- action policies (external to the learner; prediction task, not control) ----

class UniformPolicy:
    policy_id = "uniform_random_policy_v1"

    def __init__(self, seed, n_a=3):
        self.seed, self.n_a = seed, n_a

    def act(self, t, s_true):
        return counter_rng(self.seed, t, "policy").randrange(self.n_a)


class TrapPolicy:
    """Confounded policy for TRAP-001: prefers action index == true state index
    with probability pref. Actions correlate with states (hence with next
    observations) while remaining causally inert for transitions."""
    policy_id = "trap_confounded_policy_v1"

    def __init__(self, seed, pref, n_a=3):
        self.seed, self.pref, self.n_a = seed, pref, n_a

    def act(self, t, s_true):
        rng = counter_rng(self.seed, t, "policy")
        if rng.random() < self.pref:
            return s_true % self.n_a
        others = [a for a in range(self.n_a) if a != s_true % self.n_a]
        return others[rng.randrange(len(others))]
