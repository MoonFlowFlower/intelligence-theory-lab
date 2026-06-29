"""R2 meta learners with explicit CUDA/CPU device plumbing."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch
import torch.nn as nn

from src.tlgp_001a.metrics import balanced_accuracy, mean_episode_score
from src.tlgp_001a.world import Episode
from . import preregistration as P

torch.set_num_threads(max(1, torch.get_num_threads()))

DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
CTX_DIM = P.D + 2
QRY_DIM = P.D + 1
SCALE = float(P.M - 1)
FAMILIES = P.all_families()
PRIMARY_FAMILIES = P.primary_families()
DIAGNOSTIC_FAMILIES = P.diagnostic_families()

_DEVICE_RUNS: dict[str, dict[str, Any]] = {}


def reset_device_runs() -> None:
    _DEVICE_RUNS.clear()


def _cuda_name() -> str | None:
    if not torch.cuda.is_available():
        return None
    return torch.cuda.get_device_name(0)


def device_readback() -> dict[str, Any]:
    return {
        "torch_version": torch.__version__,
        "selected_device": str(DEVICE),
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "cuda_device_name": _cuda_name(),
        "meta_learner_ran_on_selected_device": {
            family: bool(_DEVICE_RUNS.get(family, {}).get("any_run_on_selected_device", False))
            for family in FAMILIES
        },
        "meta_learner_ran_on_cuda": {
            family: bool(_DEVICE_RUNS.get(family, {}).get("any_run_on_cuda", False))
            for family in FAMILIES
        },
        "meta_learner_device_runs": _DEVICE_RUNS,
    }


def build_tensors(episodes: list[Episode], context_ablate: bool = False) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    n = len(episodes)
    ctx = np.zeros((n, P.N_ADAPT, CTX_DIM), dtype=np.float32)
    qx = np.zeros((n, P.N_QUERY, QRY_DIM), dtype=np.float32)
    qy = np.zeros((n, P.N_QUERY), dtype=np.int64)
    for i, ep in enumerate(episodes):
        if not context_ablate:
            ctx[i, :, :P.D] = ep.adapt_x
            ctx[i, :, P.D] = ep.adapt_a
            ctx[i, :, P.D + 1] = ep.adapt_e
        qx[i, :, :P.D] = ep.query_x
        qx[i, :, P.D] = ep.query_a
        qy[i] = ep.query_e
    return torch.from_numpy(ctx / SCALE), torch.from_numpy(qx / SCALE), torch.from_numpy(qy)


def move_tensors(tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    return tuple(t.to(DEVICE) for t in tensors)  # type: ignore[return-value]


class QueryHead(nn.Module):
    def __init__(self, summary_dim: int, hidden: int):
        super().__init__()
        self.query = nn.Linear(QRY_DIM, hidden)
        self.net = nn.Sequential(
            nn.Linear(summary_dim + hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, P.K),
        )

    def forward(self, summary: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        query = torch.relu(self.query(qx))
        summary_expanded = summary.unsqueeze(1).expand(-1, query.shape[1], -1)
        return self.net(torch.cat([summary_expanded, query], dim=-1))


class InContextGRU(nn.Module):
    def __init__(self, hidden: int, layers: int):
        super().__init__()
        self.emb = nn.Linear(CTX_DIM, hidden)
        self.gru = nn.GRU(hidden, hidden, layers, batch_first=True)
        self.head = QueryHead(hidden, hidden)

    def forward(self, ctx: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        _, hn = self.gru(torch.relu(self.emb(ctx)))
        return self.head(hn[-1], qx)


class InContextTransformer(nn.Module):
    def __init__(self, d_model: int, layers: int, heads: int, ff_mult: int):
        super().__init__()
        self.emb = nn.Linear(CTX_DIM, d_model)
        enc = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=heads,
            dim_feedforward=d_model * ff_mult,
            batch_first=True,
            dropout=0.0,
        )
        self.enc = nn.TransformerEncoder(enc, num_layers=layers)
        self.head = QueryHead(d_model, d_model)

    def forward(self, ctx: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        h = self.enc(torch.relu(self.emb(ctx))).mean(dim=1)
        return self.head(h, qx)


class AmortizedSummaryMLP(nn.Module):
    def __init__(self, hidden: list[int]):
        super().__init__()
        summary_dim = 2 * CTX_DIM
        widths = [int(v) for v in hidden]
        self.proj = nn.Linear(summary_dim, widths[0])
        layers: list[nn.Module] = []
        for a, b in zip(widths[:-1], widths[1:]):
            layers.extend([nn.Linear(a, b), nn.ReLU()])
        self.trunk = nn.Sequential(*layers) if layers else nn.Identity()
        self.head = QueryHead(widths[-1], widths[-1])

    def forward(self, ctx: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        summary = torch.cat([ctx.mean(dim=1), ctx.std(dim=1)], dim=-1)
        h = torch.relu(self.proj(summary))
        h = self.trunk(h)
        return self.head(h, qx)


def build_model(family: str, params: dict[str, Any], seed: int) -> nn.Module:
    torch.manual_seed(int(seed))
    if family == "in_context_gru":
        return InContextGRU(int(params["hidden"]), int(params["layers"])).to(DEVICE)
    if family == "in_context_transformer":
        return InContextTransformer(
            int(params["d_model"]),
            int(params["layers"]),
            int(params["heads"]),
            int(params["ff_mult"]),
        ).to(DEVICE)
    if family == "amortized_summary_mlp":
        return AmortizedSummaryMLP([int(v) for v in params["hidden"]]).to(DEVICE)
    raise ValueError(f"unknown family {family}")


def witness_params(family: str) -> dict[str, Any]:
    grid = P.capacity_grid()
    if family == "in_context_gru":
        return {"hidden": max(grid["gru"]["hidden"]), "layers": max(grid["gru"]["layers"])}
    if family == "in_context_transformer":
        return {
            "d_model": max(grid["transformer"]["d_model"]),
            "layers": max(grid["transformer"]["layers"]),
            "heads": int(grid["transformer"]["heads"]),
            "ff_mult": int(grid["transformer"]["ff_mult"]),
        }
    if family == "amortized_summary_mlp":
        sizes = grid["mlp_summary"]["hidden"]
        return {"hidden": list(max(sizes, key=lambda values: sum(values)))}
    raise ValueError(family)


def _model_device(model: nn.Module) -> str:
    return str(next(model.parameters()).device)


def _record_device_run(
    family: str,
    model: nn.Module,
    tensor_groups: list[tuple[torch.Tensor, torch.Tensor, torch.Tensor]],
    predictions: list[list[int]],
) -> dict[str, Any]:
    model_device = _model_device(model)
    tensor_devices = sorted({str(t.device) for group in tensor_groups for t in group})
    selected = str(DEVICE)
    ran_selected = model_device == selected and all(d == selected for d in tensor_devices)
    ran_cuda = model_device.startswith("cuda") and all(d.startswith("cuda") for d in tensor_devices)
    plain_ints = all(isinstance(v, int) for row in predictions for v in row)
    rec = _DEVICE_RUNS.setdefault(family, {
        "train_select_calls": 0,
        "any_run_on_cuda": False,
        "any_run_on_selected_device": False,
        "all_runs_on_selected_device": True,
        "last_model_device": None,
        "last_tensor_devices": [],
        "predictions_serialized_on_cpu": True,
    })
    rec["train_select_calls"] += 1
    rec["any_run_on_cuda"] = bool(rec["any_run_on_cuda"] or ran_cuda)
    rec["any_run_on_selected_device"] = bool(rec["any_run_on_selected_device"] or ran_selected)
    rec["all_runs_on_selected_device"] = bool(rec["all_runs_on_selected_device"] and ran_selected)
    rec["last_model_device"] = model_device
    rec["last_tensor_devices"] = tensor_devices
    rec["predictions_serialized_on_cpu"] = bool(rec["predictions_serialized_on_cpu"] and plain_ints)
    return {
        "selected_device": selected,
        "model_device": model_device,
        "tensor_devices": tensor_devices,
        "ran_on_cuda": ran_cuda,
        "ran_on_selected_device": ran_selected,
        "predictions_serialized_on_cpu": plain_ints,
    }


@dataclass
class TrainResult:
    family: str
    params: dict[str, Any]
    lr: float
    best_val_balacc: float
    epochs_run: int
    steps_run: int
    test_balacc: float
    test_preds: list[list[int]]
    device: dict[str, Any]
    train_curve: list[dict[str, float]]
    model: nn.Module = field(repr=False)


def _episode_scores(logits: torch.Tensor, qy: torch.Tensor) -> tuple[float, list[list[int]]]:
    preds = logits.argmax(dim=-1)
    scores: list[float] = []
    records: list[list[int]] = []
    for i in range(preds.shape[0]):
        pred_cpu = preds[i].detach().cpu().numpy()
        truth_cpu = qy[i].detach().cpu().numpy()
        scores.append(balanced_accuracy(truth_cpu, pred_cpu))
        records.append([int(v) for v in pred_cpu])
    return mean_episode_score(scores), records


def eval_model(
    model: nn.Module,
    episodes: list[Episode],
    batch_size: int,
    context_ablate: bool = False,
) -> tuple[float, list[list[int]]]:
    tensors = move_tensors(build_tensors(episodes, context_ablate=context_ablate))
    ctx, qx, qy = tensors
    model.eval()
    weighted: list[tuple[float, int]] = []
    records: list[list[int]] = []
    with torch.no_grad():
        for start in range(0, ctx.shape[0], int(batch_size)):
            logits = model(ctx[start:start + batch_size], qx[start:start + batch_size])
            score, rec = _episode_scores(logits, qy[start:start + batch_size])
            count = int(qx[start:start + batch_size].shape[0])
            weighted.append((score, count))
            records.extend(rec)
    total = sum(count for _, count in weighted)
    mean = float(sum(score * count for score, count in weighted) / total) if total else 0.0
    return mean, records


def _eval_tensors(model: nn.Module, tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor], batch_size: int) -> tuple[float, list[list[int]]]:
    ctx, qx, qy = tensors
    model.eval()
    weighted: list[tuple[float, int]] = []
    records: list[list[int]] = []
    with torch.no_grad():
        for start in range(0, ctx.shape[0], int(batch_size)):
            logits = model(ctx[start:start + batch_size], qx[start:start + batch_size])
            score, rec = _episode_scores(logits, qy[start:start + batch_size])
            count = int(qx[start:start + batch_size].shape[0])
            weighted.append((score, count))
            records.extend(rec)
    total = sum(count for _, count in weighted)
    mean = float(sum(score * count for score, count in weighted) / total) if total else 0.0
    return mean, records


def _train_one(
    family: str,
    params: dict[str, Any],
    lr: float,
    model_seed: int,
    train_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    val_tensors: tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    budget: dict[str, Any],
) -> tuple[nn.Module, float, int, int, list[dict[str, float]]]:
    ctx_tr, qx_tr, qy_tr = train_tensors
    batch = int(budget["batch_size"])
    max_epochs = int(budget["max_epochs"])
    patience = int(budget["early_stop_patience"])
    steps_max = int(budget["steps_max"])
    model = build_model(family, params, model_seed)
    opt = torch.optim.Adam(model.parameters(), lr=float(lr))
    lossf = nn.CrossEntropyLoss()
    gen = torch.Generator(device="cpu").manual_seed(int(model_seed))
    best_val = -1.0
    best_state = None
    since = 0
    steps = 0
    curve: list[dict[str, float]] = []
    epochs_run = 0
    n = int(ctx_tr.shape[0])
    for epoch in range(max_epochs):
        epochs_run = epoch + 1
        model.train()
        perm = torch.randperm(n, generator=gen)
        for start in range(0, n, batch):
            idx = perm[start:start + batch].to(ctx_tr.device)
            logits = model(ctx_tr[idx], qx_tr[idx])
            loss = lossf(logits.reshape(-1, P.K), qy_tr[idx].reshape(-1))
            opt.zero_grad()
            loss.backward()
            opt.step()
            steps += 1
            if steps >= steps_max:
                break
        val_score, _ = _eval_tensors(model, val_tensors, batch)
        curve.append({"epoch": float(epochs_run), "val_balacc": float(val_score), "lr": float(lr)})
        if val_score > best_val + 1e-12:
            best_val = float(val_score)
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            since = 0
        else:
            since += 1
        if since >= patience or steps >= steps_max:
            break
    if best_state is not None:
        model.load_state_dict(best_state)
    return model, best_val, epochs_run, steps, curve


def train_select(
    family: str,
    params: dict[str, Any],
    model_seed: int,
    train_eps: list[Episode],
    val_eps: list[Episode],
    test_eps: list[Episode],
    budget: dict[str, Any],
    context_ablate: bool = False,
) -> TrainResult:
    train_t = move_tensors(build_tensors(train_eps, context_ablate=context_ablate))
    val_t = move_tensors(build_tensors(val_eps, context_ablate=context_ablate))
    test_t = move_tensors(build_tensors(test_eps, context_ablate=context_ablate))
    best: tuple[nn.Module, float, float, int, int, list[dict[str, float]]] | None = None
    for lr in budget["lr_grid"]:
        model, val_score, epochs, steps, curve = _train_one(
            family, params, float(lr), int(model_seed), train_t, val_t, budget
        )
        if best is None or val_score > best[1]:
            best = (model, val_score, float(lr), epochs, steps, curve)
    assert best is not None
    model, val_score, lr, epochs, steps, curve = best
    test_balacc, test_preds = _eval_tensors(model, test_t, int(budget["batch_size"]))
    device = _record_device_run(family, model, [train_t, val_t, test_t], test_preds)
    return TrainResult(
        family=family,
        params=dict(params),
        lr=float(lr),
        best_val_balacc=float(val_score),
        epochs_run=int(epochs),
        steps_run=int(steps),
        test_balacc=float(test_balacc),
        test_preds=test_preds,
        device=device,
        train_curve=curve,
        model=model,
    )

