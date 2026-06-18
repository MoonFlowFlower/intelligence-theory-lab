"""
Clean-room reproduction for hostile audit of
CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A.

Independently regenerates the toy episodes from the salts/seeds hard-coded in
src/candidate_free_route_c_baseline_separation_probe_001a/runner.py WITHOUT
importing that module, then shows that a trivial, non-privileged, fully-legal
"predict-all" baseline reaches recall 1.0 == oracle, i.e. the reported
separation (oracle 1.0 vs strongest_fair mean 0.5833) is a weakened-baseline /
metric-design artifact, not a real privilege gap.

Run: python3 cleanroom_reproduction.py
"""
import hashlib

def sha(t): return hashlib.sha256(t.encode()).hexdigest()

SOURCE_SALT = "candidate-free-route-c-oracle-only-hidden-set-v1"   # oracle-only ranking salt
VISIBLE_SALT = "candidate-free-route-c-visible-features-v1"        # visible-feature salt (DIFFERENT stream)
EPISODE_SEEDS = (91701, 91702, 91703, 91704, 91705, 91706)
N = 12   # legal_action_space_size
K = 4    # hidden_set_size

def hidden(seed):
    return set(sorted(range(N), key=lambda i: sha(f"{SOURCE_SALT}:{seed}:{i}"))[:K])

def vis(seed, i):
    d = sha(f"{VISIBLE_SALT}:{seed}:{i}")
    return {"item_id": i, "visible_score": int(d[12:16], 16) % 101}

def recall(truth, pred):
    return len(truth & pred) / len(truth) if truth else (1.0 if not pred else 0.0)

def mean_pred(seed):
    rows = [vis(seed, i) for i in range(N)]
    m = sum(r["visible_score"] for r in rows) / N
    return {r["item_id"] for r in rows if r["visible_score"] >= m}      # probe's `mean` baseline

def predict_all(seed):
    return set(range(N))                                                # trivial fair baseline (OMITTED from panel)

def threshold_min(seed):
    rows = [vis(seed, i) for i in range(N)]
    mn = min(r["visible_score"] for r in rows)
    return {r["item_id"] for r in rows if r["visible_score"] >= mn}     # same `mean` family, threshold=min

if __name__ == "__main__":
    for name, fn in [("oracle(reads hidden_set)", hidden),
                     ("mean (probe strongest_fair)", mean_pred),
                     ("predict_all (fair, omitted)", predict_all),
                     ("threshold_min (mean-family)", threshold_min)]:
        ss = [recall(hidden(s), (hidden(s) if name.startswith("oracle") else fn(s))) for s in EPISODE_SEEDS]
        print(f"{name:32s} per_ep={['%.3f'%x for x in ss]} mean={sum(ss)/len(ss):.4f}")

    # feature/label independence
    xs, ys = [], []
    for s in EPISODE_SEEDS:
        h = hidden(s)
        for i in range(N):
            xs.append(vis(s, i)["visible_score"]); ys.append(1 if i in h else 0)
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    cov = sum((a-mx)*(b-my) for a, b in zip(xs, ys)) / len(xs)
    import statistics
    corr = cov / (statistics.pstdev(xs) * statistics.pstdev(ys))
    print(f"\ncorr(visible_score, hidden_membership) = {corr:.4f}  (~0 => visible features carry no signal)")
    print("=> strongest admissible fair baseline (predict_all) recall == oracle recall == 1.0; delta == 0.0")
