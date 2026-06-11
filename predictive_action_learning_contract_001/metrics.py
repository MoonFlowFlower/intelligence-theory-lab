"""Metrics (task card sections 4.7, 4.8, 4.11): NLL, Brier, entropy, pairwise
JS divergence, rolling windows, ECE with pre-declared suitability policy, and
delta helpers. All entropies/divergences in nats."""

import math


def entropy(p, eps=1e-12):
    return -sum(x * math.log(max(x, eps)) for x in p if x > 0.0)


def kl(p, q, eps=1e-12):
    return sum(x * (math.log(max(x, eps)) - math.log(max(q[i], eps)))
               for i, x in enumerate(p) if x > 0.0)


def jsd(p, q):
    m = [(a + b) / 2.0 for a, b in zip(p, q)]
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def jsd_mean_pairwise(dists):
    n = len(dists)
    if n < 2:
        return 0.0
    tot, cnt = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            tot += jsd(dists[i], dists[j])
            cnt += 1
    return tot / cnt


def jsd_mean_confident(dists, entropy_max, eps=1e-12):
    """Mean pairwise JSD among distributions confident enough to count
    (entropy <= entropy_max). Fewer than two confident distributions means no
    confident separation evidence: returns 0.0."""
    keep = [d for d in dists if entropy(d, eps) <= entropy_max]
    if len(keep) < 2:
        return 0.0
    return jsd_mean_pairwise(keep)


def brier_component(p, actual):
    return sum((p[o] - (1.0 if o == actual else 0.0)) ** 2 for o in range(len(p)))


def l1(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def l1_nested(a, b):
    tot = 0.0
    for x, y in zip(a, b):
        if isinstance(x, list):
            tot += l1_nested(x, y)
        else:
            tot += abs(x - y)
    return tot


def rolling_mean(xs, window):
    out, acc = [], 0.0
    from collections import deque
    q = deque()
    for x in xs:
        q.append(x)
        acc += x
        if len(q) > window:
            acc -= q.popleft()
        out.append(acc / len(q))
    return out


def window_mean(xs, last_n):
    if not xs:
        return None
    seg = xs[-last_n:]
    return sum(seg) / len(seg)


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def ece(pred_dists, actuals, num_bins, min_total, min_nonempty_bins, min_bin_samples):
    """Expected calibration error over argmax confidence; secondary metric only.
    Returns (value_or_None, report)."""
    confs, hits = [], []
    for p, y in zip(pred_dists, actuals):
        am = max(range(len(p)), key=lambda i: p[i])
        confs.append(p[am])
        hits.append(1.0 if am == y else 0.0)
    n = len(confs)
    bins = [[] for _ in range(num_bins)]
    for c, h in zip(confs, hits):
        idx = min(int(c * num_bins), num_bins - 1)
        bins[idx].append((c, h))
    nonempty = [b for b in bins if b]
    suitable = (n >= min_total and len(nonempty) >= min_nonempty_bins
                and all(len(b) >= min_bin_samples for b in nonempty))
    val = 0.0
    for b in nonempty:
        bc = sum(c for c, _ in b) / len(b)
        ba = sum(h for _, h in b) / len(b)
        val += (len(b) / n) * abs(bc - ba)
    report = {
        "ece_value": val,
        "suitable": suitable,
        "primary": False,
        "n_samples": n,
        "n_nonempty_bins": len(nonempty),
        "bin_sizes": [len(b) for b in bins],
        "policy": "secondary metric; decisive use forbidden when unsuitable "
                  "(task card 4.8, 12.2.15, stop condition 16)",
    }
    return (val if suitable else None), report
