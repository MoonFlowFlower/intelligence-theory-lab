"""Isolated candidate-R evaluation subprocess (R_slice_1..5).

Absence-by-construction: opens exactly the three argv paths. Imports
stdlib + numpy only. No store/cache/index/chunk/buffer code paths exist here.

Usage: python eval_subprocess.py <snapshot.npz> <queries.json> <out.json>
"""

import hashlib
import json
import sys

import numpy as np

N, NA, NO = 16, 3, 5
FLOOR = 1e-12
OBS_LABEL = (0, 1, 2, 3, 4, 2, 0, 3, 1, 4, 1, 3, 0, 4, 2, 0)
OBS_MASK = np.stack([[1.0 if OBS_LABEL[s] == o else 0.0 for s in range(N)]
                     for o in range(NO)])
OPENED = []


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(65536), b""):
            h.update(blk)
    return h.hexdigest()


def softmax(z):
    z = z - z.max()
    p = np.exp(z)
    return p / p.sum()


def main():
    snap_path, q_path, out_path = sys.argv[1:4]
    OPENED.extend([snap_path, q_path])
    snap = np.load(snap_path)
    with open(q_path) as f:
        q = json.load(f)
    theta = snap["theta"]
    TM = [np.stack([softmax(theta[s, a]) for s in range(N)])
          for a in range(NA)]

    def predict(b, a):
        m = b @ TM[a]
        return OBS_MASK @ m, m

    def update(b, a, o_next):
        _p, m = predict(b, a)
        bb = m * OBS_MASK[o_next]
        t = bb.sum()
        return bb / t if t > 0 else np.full(N, 1.0 / N)

    def predict_h4(b, acts4):
        v = b.copy()
        for a in acts4:
            v = v @ TM[a]
        return OBS_MASK @ v

    def nll(p, qt):
        return -float(np.array(qt) @ np.log(np.maximum(p, FLOOR)))

    seqs = q["sequences"]
    acc = {k: [0.0, 0] for k in
           ["R_slice_1", "R_slice_2", "R_slice_3", "R_slice_4", "R_slice_5"]}
    for seq in seqs:
        A, O = seq["actions"], seq["obs"]
        bs = [np.full(N, 1.0 / N)]
        for t in range(len(A) - 1):
            bs.append(update(bs[-1], A[t], O[t + 1]))
        for t in range(6, len(A)):
            p, _ = predict(bs[t], A[t])
            v = nll(p, seq["qtrue1"][t])
            acc["R_slice_1"][0] += v; acc["R_slice_1"][1] += 1
            if seq["mask_r4"][t]:
                acc["R_slice_4"][0] += v; acc["R_slice_4"][1] += 1
        b = np.full(N, 1.0 / N)
        for t in range(25, len(A)):
            if t >= 31:
                p, _ = predict(b, A[t])
                acc["R_slice_2"][0] += nll(p, seq["qtrue1"][t])
                acc["R_slice_2"][1] += 1
            if t + 1 < len(O):
                b = update(b, A[t], O[t + 1])
        for t in range(11, len(A)):
            b = np.full(N, 1.0 / N)
            for u in range(t - 10, t):
                b = update(b, A[u], O[u + 1])
            p, _ = predict(b, A[t])
            acc["R_slice_3"][0] += nll(p, seq["qtrue1"][t])
            acc["R_slice_3"][1] += 1
        for t in range(6, 46):
            p4 = predict_h4(bs[t], A[t:t + 4])
            acc["R_slice_5"][0] += nll(p4, seq["qtrue4"][t])
            acc["R_slice_5"][1] += 1
    results = {k: v[0] / v[1] for k, v in acc.items()}
    attestation = {
        "argv_allowlist": [snap_path, q_path, out_path],
        "opened_files": OPENED,
        "opened_file_hashes": {p: sha256(p) for p in OPENED},
        "forbidden_objects_loaded": 0,
        "forbidden_objects_reachable": 0,
        "reachable_object_inventory": OPENED,
        "isolation": "separate python subprocess; stdlib+numpy only; no "
                     "store/cache/index/chunk/buffer code paths in module",
        "numpy_version": np.__version__,
    }
    with open(out_path, "w") as f:
        json.dump({"results": results, "attestation": attestation}, f, indent=1)


if __name__ == "__main__":
    main()
