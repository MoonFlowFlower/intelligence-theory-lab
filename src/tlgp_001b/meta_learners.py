"""Pre-registered cross-episode meta-learner panel for TLGP-001B (torch).

Three fair-meta families (prereg `panel.new_fair_meta`), each parameterized by the frozen
capacity grid:
  * in_context_gru          : GRU over the adaptation context -> summary; query head.
  * in_context_transformer  : TransformerEncoder over the context -> mean-pool summary; query head.
  * amortized_summary_mlp   : permutation-invariant context summary (mean/std) -> MLP; query head.

Fairness / anti-rigging:
  * Inputs are NUMERIC (raw integer values scaled by a FIXED 1/(M-1); NO one-hot of the value
    axis -> no one-hot starvation that would trivially block extrapolation to {3,4}). This is
    the K4-fair choice consistent with 001A's fair baselines; it gives the meta a genuine chance
    to amortize the mod-K family across episodes.
  * The meta receives ONLY (adapt_x, adapt_a, adapt_e, query_x, query_a). It NEVER receives
    rule_id or query_e (the held-out answer). Enforced structurally by build_tensors().
  * Training budget (optimizer, lr grid, batch, max_epochs, patience, steps_max) is IDENTICAL
    across REAL / CAPACITY_CONTROL / context-ablation / shuffle conditions. The ONLY permitted
    condition difference lives in the data (train/val query value-regime), never here.

Deterministic per MODEL_SEED (torch.manual_seed + seeded shuff/init). Eval records per-episode
predictions so replay can recompute balanced accuracy WITHOUT retraining.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn

from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from . import preregistration as P

torch.set_num_threads(max(1, torch.get_num_threads()))
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
_DEVICE_RUNS: Dict[str, Dict] = {}

CTX_DIM = P.D + 1 + 1   # x_0..x_{D-1}, a, e
QRY_DIM = P.D + 1       # x_0..x_{D-1}, a
_SCALE = float(P.M - 1)  # fixed input scaling constant (= 4.0); NOT data-derived

FAMILIES = ["in_context_gru", "in_context_transformer", "amortized_summary_mlp"]


def _cuda_name() -> str | None:
    if DEVICE.type != "cuda":
        return None
    return torch.cuda.get_device_name(DEVICE)


def device_readback() -> Dict:
    """Runtime-only device telemetry for runner verification; not experimental evidence."""
    runs = {
        f: {
            **v,
            "last_tensor_devices": list(v.get("last_tensor_devices", [])),
        }
        for f, v in _DEVICE_RUNS.items()
    }
    return {
        "torch_version": torch.__version__,
        "selected_device": str(DEVICE),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "cuda_device_name": _cuda_name(),
        "meta_learner_ran_on_cuda": {
            f: bool(runs.get(f, {}).get("any_run_on_cuda", False)) for f in FAMILIES
        },
        "meta_learner_device_runs": runs,
    }


def _move_tensors(tensors: Tuple[torch.Tensor, torch.Tensor, torch.Tensor]
                  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    return tuple(t.to(DEVICE) for t in tensors)


def _model_device(model: nn.Module) -> torch.device:
    return next(model.parameters()).device


def _record_device_run(family: str, model: nn.Module, tensors) -> Dict:
    model_dev = str(_model_device(model))
    tensor_devs = sorted({str(t.device) for group in tensors for t in group})
    ran_on_cuda = bool(model_dev.startswith("cuda") and all(d.startswith("cuda") for d in tensor_devs))
    ran_on_selected = bool(model_dev == str(DEVICE) and all(d == str(DEVICE) for d in tensor_devs))
    rec = _DEVICE_RUNS.setdefault(family, {
        "train_select_calls": 0,
        "any_run_on_cuda": False,
        "all_runs_on_selected_device": True,
        "last_model_device": None,
        "last_tensor_devices": [],
    })
    rec["train_select_calls"] += 1
    rec["any_run_on_cuda"] = bool(rec["any_run_on_cuda"] or ran_on_cuda)
    rec["all_runs_on_selected_device"] = bool(rec["all_runs_on_selected_device"] and ran_on_selected)
    rec["last_model_device"] = model_dev
    rec["last_tensor_devices"] = tensor_devs
    return {
        "selected_device": str(DEVICE),
        "model_device": model_dev,
        "tensor_devices": tensor_devs,
        "ran_on_cuda": ran_on_cuda,
        "ran_on_selected_device": ran_on_selected,
    }


# --- tensors (the structural leakage boundary: only legal fields enter) --------
def build_tensors(episodes: List[Episode], context_ablate: bool = False
                  ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    n = len(episodes)
    ctx = np.zeros((n, P.N_ADAPT, CTX_DIM), dtype=np.float32)
    qx = np.zeros((n, P.N_QUERY, QRY_DIM), dtype=np.float32)
    qy = np.zeros((n, P.N_QUERY), dtype=np.int64)
    for i, ep in enumerate(episodes):
        if not context_ablate:                                   # ablation zeros the context
            ctx[i, :, :P.D] = ep.adapt_x
            ctx[i, :, P.D] = ep.adapt_a
            ctx[i, :, P.D + 1] = ep.adapt_e
        qx[i, :, :P.D] = ep.query_x
        qx[i, :, P.D] = ep.query_a
        qy[i] = ep.query_e                                       # TARGET only (never an input)
    return (torch.from_numpy(ctx / _SCALE), torch.from_numpy(qx / _SCALE), torch.from_numpy(qy))


# --- models --------------------------------------------------------------------
class _QueryHead(nn.Module):
    def __init__(self, summ_dim: int, hidden: int):
        super().__init__()
        self.qe = nn.Linear(QRY_DIM, hidden)
        self.net = nn.Sequential(nn.Linear(summ_dim + hidden, hidden), nn.ReLU(),
                                 nn.Linear(hidden, P.K))

    def forward(self, summary: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        q = torch.relu(self.qe(qx))                              # (B, NQ, hidden)
        s = summary.unsqueeze(1).expand(-1, q.shape[1], -1)      # (B, NQ, summ_dim)
        return self.net(torch.cat([s, q], dim=-1))               # (B, NQ, K)


class InContextGRU(nn.Module):
    def __init__(self, hidden: int, layers: int):
        super().__init__()
        self.emb = nn.Linear(CTX_DIM, hidden)
        self.gru = nn.GRU(hidden, hidden, layers, batch_first=True)
        self.head = _QueryHead(hidden, hidden)

    def forward(self, ctx, qx):
        _, hn = self.gru(torch.relu(self.emb(ctx)))
        return self.head(hn[-1], qx)


class InContextTransformer(nn.Module):
    def __init__(self, d_model: int, layers: int, heads: int, ff_mult: int):
        super().__init__()
        self.emb = nn.Linear(CTX_DIM, d_model)
        enc = nn.TransformerEncoderLayer(d_model, heads, d_model * ff_mult,
                                         batch_first=True, dropout=0.0)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.head = _QueryHead(d_model, d_model)

    def forward(self, ctx, qx):
        h = self.enc(torch.relu(self.emb(ctx))).mean(dim=1)      # mean-pool context
        return self.head(h, qx)


class AmortizedSummaryMLP(nn.Module):
    def __init__(self, hidden: List[int]):
        super().__init__()
        summ_dim = 2 * CTX_DIM                                   # mean + std over context tokens
        h0 = hidden[0]
        self.proj = nn.Linear(summ_dim, h0)
        layers: List[nn.Module] = []
        widths = hidden
        for a, b in zip(widths[:-1], widths[1:]):
            layers += [nn.Linear(a, b), nn.ReLU()]
        self.trunk = nn.Sequential(*layers) if layers else nn.Identity()
        self.head = _QueryHead(widths[-1], widths[-1])

    def forward(self, ctx, qx):
        summ = torch.cat([ctx.mean(dim=1), ctx.std(dim=1)], dim=-1)
        s = torch.relu(self.proj(summ))
        s = self.trunk(s)
        return self.head(s, qx)


def build_model(family: str, params: Dict, seed: int) -> nn.Module:
    torch.manual_seed(seed)
    if family == "in_context_gru":
        return InContextGRU(int(params["hidden"]), int(params["layers"])).to(DEVICE)
    if family == "in_context_transformer":
        return InContextTransformer(int(params["d_model"]), int(params["layers"]),
                                    int(params["heads"]), int(params["ff_mult"])).to(DEVICE)
    if family == "amortized_summary_mlp":
        return AmortizedSummaryMLP(list(params["hidden"])).to(DEVICE)
    raise ValueError(f"unknown family {family}")


def witness_params(family: str) -> Dict:
    """Largest-capacity ('saturation witness') params per family, from the frozen grid."""
    g = P.capacity_grid()
    if family == "in_context_gru":
        return {"hidden": max(g["gru"]["hidden"]), "layers": max(g["gru"]["layers"])}
    if family == "in_context_transformer":
        return {"d_model": max(g["transformer"]["d_model"]), "layers": max(g["transformer"]["layers"]),
                "heads": int(g["transformer"]["heads"]), "ff_mult": int(g["transformer"]["ff_mult"])}
    if family == "amortized_summary_mlp":
        sizes = g["mlp_summary"]["hidden"]
        return {"hidden": max(sizes, key=lambda h: sum(h))}
    raise ValueError(family)


def capacity_configs() -> List[Tuple[str, Dict]]:
    """Full frozen capacity grid expanded to (family, params) configs (REAL run uses all;
    the verdict keys only on the per-family witness, but the sweep is corroborating)."""
    g = P.capacity_grid()
    out: List[Tuple[str, Dict]] = []
    for h in g["gru"]["hidden"]:
        for l in g["gru"]["layers"]:
            out.append(("in_context_gru", {"hidden": h, "layers": l}))
    for d in g["transformer"]["d_model"]:
        for l in g["transformer"]["layers"]:
            out.append(("in_context_transformer", {"d_model": d, "layers": l,
                        "heads": int(g["transformer"]["heads"]), "ff_mult": int(g["transformer"]["ff_mult"])}))
    for h in g["mlp_summary"]["hidden"]:
        out.append(("amortized_summary_mlp", {"hidden": list(h)}))
    return out


# --- training / eval -----------------------------------------------------------
@dataclass
class TrainResult:
    family: str
    params: Dict
    lr: float
    best_val_balacc: float
    epochs_run: int
    steps_run: int
    test_balacc: float
    test_preds: List[List[int]]    # per test episode argmax predictions (recorded for replay)
    device: Dict


def _episode_balacc(logits: torch.Tensor, qy: torch.Tensor) -> Tuple[float, List[List[int]]]:
    preds = logits.argmax(dim=-1)                                # (B, NQ)
    scores, recorded = [], []
    for i in range(preds.shape[0]):
        p = preds[i].detach().cpu().numpy()
        scores.append(balanced_accuracy(qy[i].detach().cpu().numpy(), p))
        recorded.append([int(v) for v in p])
    return mean_episode_score(scores), recorded


def _eval_balacc(model: nn.Module, ctx, qx, qy, batch: int) -> Tuple[float, List[List[int]]]:
    model.eval()
    scores, recorded = [], []
    with torch.no_grad():
        for s in range(0, ctx.shape[0], batch):
            logits = model(ctx[s:s + batch], qx[s:s + batch])
            bs, rec = _episode_balacc(logits, qy[s:s + batch])
            # weight by episode count for an exact mean over all episodes
            scores.append((bs, qx[s:s + batch].shape[0]))
            recorded.extend(rec)
    total = sum(n for _, n in scores)
    mean = float(sum(bs * n for bs, n in scores) / total) if total else 0.0
    return mean, recorded


def _train_one(family: str, params: Dict, lr: float, model_seed: int,
               train_t, val_t, budget: Dict) -> Tuple[nn.Module, float, int, int]:
    ctx_tr, qx_tr, qy_tr = train_t
    ctx_va, qx_va, qy_va = val_t
    model = build_model(family, params, model_seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()
    batch = int(budget["batch_size"])
    max_epochs = int(budget["max_epochs"])
    patience = int(budget["early_stop_patience"])
    steps_max = int(budget["steps_max"])
    g = torch.Generator().manual_seed(model_seed)
    n = ctx_tr.shape[0]
    best_val, best_state, since, steps, epochs_run = -1.0, None, 0, 0, 0
    for epoch in range(max_epochs):
        epochs_run = epoch + 1
        model.train()
        perm = torch.randperm(n, generator=g)
        for s in range(0, n, batch):
            idx = perm[s:s + batch].to(ctx_tr.device)
            logits = model(ctx_tr[idx], qx_tr[idx])
            loss = lossf(logits.reshape(-1, P.K), qy_tr[idx].reshape(-1))
            opt.zero_grad(); loss.backward(); opt.step()
            steps += 1
            if steps >= steps_max:
                break
        val_score, _ = _eval_balacc(model, ctx_va, qx_va, qy_va, batch)
        if val_score > best_val + 1e-9:
            best_val, best_state, since = val_score, {k: v.detach().clone() for k, v in model.state_dict().items()}, 0
        else:
            since += 1
        if since >= patience or steps >= steps_max:
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    return model, best_val, epochs_run, steps


def train_select(family: str, params: Dict, model_seed: int,
                 train_eps: List[Episode], val_eps: List[Episode], test_eps: List[Episode],
                 budget: Dict, context_ablate: bool = False) -> TrainResult:
    """Train at each lr in the frozen grid, select best on val balanced accuracy (preregistered),
    then evaluate on the (regime-invariant) test set and record per-episode predictions."""
    train_t = _move_tensors(build_tensors(train_eps, context_ablate))
    val_t = _move_tensors(build_tensors(val_eps, context_ablate))
    test_t = _move_tensors(build_tensors(test_eps, context_ablate))
    best: Tuple = None
    for lr in budget["lr_grid"]:
        model, val_score, epochs_run, steps = _train_one(
            family, params, float(lr), model_seed, train_t, val_t, budget)
        if best is None or val_score > best[1]:
            best = (model, val_score, float(lr), epochs_run, steps)
    model, val_score, lr, epochs_run, steps = best
    test_balacc, test_preds = _eval_balacc(model, *test_t, int(budget["batch_size"]))
    dev = _record_device_run(family, model, (train_t, val_t, test_t))
    return TrainResult(family, params, lr, val_score, epochs_run, steps, test_balacc, test_preds, dev)
