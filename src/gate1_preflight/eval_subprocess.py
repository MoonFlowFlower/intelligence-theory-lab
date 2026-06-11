"""Isolated slow-only / cache-free candidate evaluation subprocess.

Absence-by-construction: this module opens exactly the three argv paths
(snapshot .npz, queries .json, output .json). It imports only stdlib + numpy.
It contains no code path that can read any store, buffer, cache, index,
teacher, generator, library, or any other artifact. The attestation it emits
lists every file it opened with hashes.

Usage: python eval_subprocess.py <snapshot.npz> <queries.json> <out.json>
"""

import hashlib
import json
import sys

import numpy as np

PROB_FLOOR = 1e-12
N_STATES = 12
N_OBS = 4

OPENED = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def load(path_npz, path_q):
    OPENED.append(path_npz)
    OPENED.append(path_q)
    snap = np.load(path_npz)
    with open(path_q, "r") as f:
        q = json.load(f)
    return snap, q


def softmax(z):
    z = z - z.max()
    p = np.exp(z)
    return p / p.sum()


def eval_A(snap, q):
    e, w, v = snap["e"], snap["w"], snap["v"]
    T = np.array(q["T_true"])
    out = {}
    for slice_name, pairs in q["slices"].items():
        tot = 0.0
        for s, a in pairs:
            p = np.maximum(softmax((e[s] * w[a]) @ v.T), PROB_FLOOR)
            tot += -float(T[s, a] @ np.log(p))
        out[slice_name] = tot / len(pairs)
    return out


OBS_LABEL = (0, 1, 2, 3, 0, 2, 1, 3, 2, 0, 3, 1)  # ENV-PREREG-AMENDMENT-001
# (duplicated deliberately: this module must stay import-isolated from core)


def eval_B(snap, q):
    theta = snap["theta"]
    obs_of = lambda s: OBS_LABEL[s]

    def trans_matrix(a):
        return np.stack([softmax(theta[s, a]) for s in range(N_STATES)])

    TM = [trans_matrix(a) for a in range(3)]
    mask_obs = np.stack([[1.0 if obs_of(s2) == o else 0.0
                          for s2 in range(N_STATES)] for o in range(N_OBS)])

    def predict(belief, a):
        m = belief @ TM[a]
        p = np.array([float(m @ mask_obs[o]) for o in range(N_OBS)])
        return p, m

    def update(belief, a, o_next):
        p, m = predict(belief, a)
        b = m * mask_obs[o_next]
        t = b.sum()
        return b / t if t > 0 else np.full(N_STATES, 1.0 / N_STATES)

    sequences = q["sequences"]      # list of {actions, obs, qtrue (40x4)}
    results = {}

    def beliefs_full(seq):
        b = np.full(N_STATES, 1.0 / N_STATES)
        bs = [b.copy()]
        for t in range(len(seq["actions"]) - 1):
            b = update(b, seq["actions"][t], seq["obs"][t + 1])
            bs.append(b.copy())
        return bs

    def nll_at(b, seq, t):
        p, _ = predict(b, seq["actions"][t])
        p = np.maximum(p, PROB_FLOOR)
        qt = np.array(seq["qtrue"][t])
        return -float(qt @ np.log(p))

    # B1: fresh belief, burn-in 5, score steps 6..39
    tot, n = 0.0, 0
    for seq in sequences:
        bs = beliefs_full(seq)
        for t in range(6, len(seq["actions"])):
            tot += nll_at(bs[t], seq, t); n += 1
    results["B_slice_1"] = tot / n

    # B2: belief reset at step 20, burn-in 5, score 26..39
    tot, n = 0.0, 0
    for seq in sequences:
        b = np.full(N_STATES, 1.0 / N_STATES)
        for t in range(20, len(seq["actions"])):
            if t >= 26:
                tot += nll_at(b, seq, t); n += 1
            if t + 1 < len(seq["obs"]):
                b = update(b, seq["actions"][t], seq["obs"][t + 1])
    results["B_slice_2"] = tot / n

    # B3: sliding window of last 8 steps, score steps >= 9
    tot, n = 0.0, 0
    for seq in sequences:
        for t in range(9, len(seq["actions"])):
            b = np.full(N_STATES, 1.0 / N_STATES)
            for u in range(t - 8, t):
                b = update(b, seq["actions"][u], seq["obs"][u + 1])
            tot += nll_at(b, seq, t); n += 1
    results["B_slice_3"] = tot / n

    # B4: B1 protocol restricted to alias-disambiguation mask
    tot, n = 0.0, 0
    for seq in sequences:
        bs = beliefs_full(seq)
        for t in range(6, len(seq["actions"])):
            if seq["mask_b4"][t]:
                tot += nll_at(bs[t], seq, t); n += 1
    results["B_slice_4"] = tot / n
    return results


def main():
    snap_path, q_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    snap, q = load(snap_path, q_path)
    res = eval_A(snap, q) if q["kind"] == "A" else eval_B(snap, q)
    attestation = {
        "argv_allowlist": [snap_path, q_path, out_path],
        "opened_files": OPENED,
        "opened_file_hashes": {p: sha256(p) for p in OPENED},
        "forbidden_objects_loaded": 0,
        "forbidden_objects_reachable": 0,
        "reachable_object_inventory": OPENED,
        "isolation": "separate python subprocess; module imports stdlib+numpy only; no store/cache/index/buffer code paths exist in this module",
        "numpy_version": np.__version__,
    }
    OPENED.append(out_path)
    with open(out_path, "w") as f:
        json.dump({"results": res, "attestation": attestation}, f, indent=1)


if __name__ == "__main__":
    main()
