"""
Clean-room reproduction for hostile audit rejection of
CANDIDATE-FREE-ROUTE-C-BASELINE-SEPARATION-PROBE-001A.

This regenerates the toy episodes from the public salts/seeds used by the
original probe without importing that probe module. It shows that a legal,
non-privileged predict_all baseline reaches the same recall as the privileged
oracle under the old recall-only metric.

Run: python cleanroom_reproduction.py
"""

import hashlib
import statistics


SOURCE_SALT = "candidate-free-route-c-oracle-only-hidden-set-v1"
VISIBLE_SALT = "candidate-free-route-c-visible-features-v1"
EPISODE_SEEDS = (91701, 91702, 91703, 91704, 91705, 91706)
N = 12
K = 4


def sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def hidden(seed: int) -> set[int]:
    return set(sorted(range(N), key=lambda item_id: sha(f"{SOURCE_SALT}:{seed}:{item_id}"))[:K])


def visible_row(seed: int, item_id: int) -> dict[str, int]:
    digest = sha(f"{VISIBLE_SALT}:{seed}:{item_id}")
    return {"item_id": item_id, "visible_score": int(digest[12:16], 16) % 101}


def recall(truth: set[int], prediction: set[int]) -> float:
    if truth:
        return len(truth & prediction) / len(truth)
    return 1.0 if not prediction else 0.0


def mean_prediction(seed: int) -> set[int]:
    rows = [visible_row(seed, item_id) for item_id in range(N)]
    mean_score = sum(row["visible_score"] for row in rows) / N
    return {row["item_id"] for row in rows if row["visible_score"] >= mean_score}


def predict_all(seed: int) -> set[int]:
    del seed
    return set(range(N))


def threshold_min(seed: int) -> set[int]:
    rows = [visible_row(seed, item_id) for item_id in range(N)]
    minimum = min(row["visible_score"] for row in rows)
    return {row["item_id"] for row in rows if row["visible_score"] >= minimum}


def scores_for(name: str, fn) -> list[float]:
    scores = []
    for seed in EPISODE_SEEDS:
        truth = hidden(seed)
        prediction = truth if name.startswith("oracle") else fn(seed)
        scores.append(recall(truth, prediction))
    return scores


def visible_hidden_correlation() -> float:
    xs = []
    ys = []
    for seed in EPISODE_SEEDS:
        truth = hidden(seed)
        for item_id in range(N):
            xs.append(visible_row(seed, item_id)["visible_score"])
            ys.append(1 if item_id in truth else 0)
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    covariance = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / len(xs)
    return covariance / (statistics.pstdev(xs) * statistics.pstdev(ys))


if __name__ == "__main__":
    producers = [
        ("oracle(reads hidden_set)", hidden),
        ("mean (probe strongest_fair)", mean_prediction),
        ("predict_all (fair, omitted)", predict_all),
        ("threshold_min (mean-family)", threshold_min),
    ]
    for name, producer in producers:
        values = scores_for(name, producer)
        formatted = ["%.3f" % value for value in values]
        print(f"{name:32s} per_ep={formatted} mean={sum(values) / len(values):.4f}")

    corr = visible_hidden_correlation()
    print(f"\ncorr(visible_score, hidden_membership) = {corr:.4f}  (~0 => visible features carry no signal)")
    print("=> strongest admissible fair baseline (predict_all) recall == oracle recall == 1.0; delta == 0.0")
