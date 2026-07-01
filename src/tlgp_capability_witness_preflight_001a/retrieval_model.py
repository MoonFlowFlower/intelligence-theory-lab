"""Retrieval-capable in-context transformer for TLGP positive-control validation."""
from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from src.tlgp_001b_r2 import preregistration as P

FAMILY = "icl_retrieval_transformer"
PARAMS = {"d_model": 256, "layers": 4, "heads": 4, "ff_mult": 4}
SEGMENT_ADAPT = 0
SEGMENT_QUERY = 1
SCALE = float(P.M - 1)


def _to_index(values: torch.Tensor, cardinality: int) -> torch.Tensor:
    return torch.round(values * SCALE).long().clamp_(0, int(cardinality) - 1)


class RetrievalInContextTransformer(nn.Module):
    """Self-attention over adapt and query tokens.

    Inputs match `meta_learners.build_tensors`: `ctx` is normalized
    `[x_0..x_D, a, e]` adapt rows and `qx` is normalized `[x_0..x_D, a]`
    query rows. Query tokens never receive `e`; they can access adapt effects
    only by attending to adapt tokens inside the transformer.
    """

    def __init__(
        self,
        d_model: int = 256,
        layers: int = 4,
        heads: int = 4,
        ff_mult: int = 4,
    ) -> None:
        super().__init__()
        self.d_model = int(d_model)
        self.layers = int(layers)
        self.heads = int(heads)
        self.ff_mult = int(ff_mult)
        self.x_embeddings = nn.ModuleList([nn.Embedding(P.M, self.d_model) for _ in range(P.D)])
        self.action_embedding = nn.Embedding(P.ACTION_CARD, self.d_model)
        self.effect_embedding = nn.Embedding(P.K, self.d_model)
        self.segment_embedding = nn.Embedding(2, self.d_model)
        self.input_norm = nn.LayerNorm(self.d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.d_model,
            nhead=self.heads,
            dim_feedforward=self.d_model * self.ff_mult,
            dropout=0.0,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=self.layers)
        self.query_head = nn.Linear(self.d_model, P.K)

    def _embed_x(self, x_idx: torch.Tensor) -> torch.Tensor:
        token = torch.zeros(*x_idx.shape[:-1], self.d_model, device=x_idx.device, dtype=self.segment_embedding.weight.dtype)
        for dim, emb in enumerate(self.x_embeddings):
            token = token + emb(x_idx[..., dim])
        return token

    def _embed_adapt(self, ctx: torch.Tensor) -> torch.Tensor:
        x_idx = _to_index(ctx[..., :P.D], P.M)
        a_idx = _to_index(ctx[..., P.D], P.ACTION_CARD)
        e_idx = _to_index(ctx[..., P.D + 1], P.K)
        seg = torch.full(a_idx.shape, SEGMENT_ADAPT, device=ctx.device, dtype=torch.long)
        return (
            self._embed_x(x_idx)
            + self.action_embedding(a_idx)
            + self.effect_embedding(e_idx)
            + self.segment_embedding(seg)
        )

    def _embed_query(self, qx: torch.Tensor) -> torch.Tensor:
        x_idx = _to_index(qx[..., :P.D], P.M)
        a_idx = _to_index(qx[..., P.D], P.ACTION_CARD)
        seg = torch.full(a_idx.shape, SEGMENT_QUERY, device=qx.device, dtype=torch.long)
        return self._embed_x(x_idx) + self.action_embedding(a_idx) + self.segment_embedding(seg)

    def forward(self, ctx: torch.Tensor, qx: torch.Tensor) -> torch.Tensor:
        n_adapt = int(ctx.shape[1])
        adapt_tokens = self._embed_adapt(ctx)
        query_tokens = self._embed_query(qx)
        tokens = self.input_norm(torch.cat([adapt_tokens, query_tokens], dim=1))
        encoded = self.encoder(tokens)
        query_encoded = encoded[:, n_adapt:, :]
        return self.query_head(query_encoded)


def build_model(params: dict[str, Any] | None = None) -> RetrievalInContextTransformer:
    params = PARAMS if params is None else params
    return RetrievalInContextTransformer(
        d_model=int(params["d_model"]),
        layers=int(params["layers"]),
        heads=int(params["heads"]),
        ff_mult=int(params["ff_mult"]),
    )


def parameter_count(model: nn.Module) -> int:
    return int(sum(p.numel() for p in model.parameters()))


def model_card(param_count: int | None = None) -> dict[str, Any]:
    if param_count is None:
        param_count = parameter_count(build_model())
    return {
        "family": FAMILY,
        "params": dict(PARAMS),
        "parameter_count": int(param_count),
        "tokenization": {
            "adapt_token": "sum of learned embeddings for each discrete x dimension, action a, observed effect e, plus adapt segment embedding",
            "query_token": "sum of learned embeddings for each discrete x dimension and action a, plus query segment embedding; no effect e input",
            "sequence": "[adapt_1 ... adapt_24, query_1 ... query_30]",
            "attention": "full TransformerEncoder self-attention over adapt and query tokens; no causal mask",
            "readout": "each query token output is passed through a Linear head to K logits",
            "pooling": "none; adapt examples are not mean-pooled or collapsed to a fixed summary before query readout",
            "input_source": "normalized tensors from src.tlgp_001b_r2.meta_learners.build_tensors are rounded back to frozen discrete values for embedding lookup",
        },
        "architecture": {
            "d_model": PARAMS["d_model"],
            "layers": PARAMS["layers"],
            "heads": PARAMS["heads"],
            "ff_mult": PARAMS["ff_mult"],
            "dropout": 0.0,
            "encoder": "torch.nn.TransformerEncoder",
            "segment_embeddings": ["adapt", "query"],
        },
        "claim_ceiling": "retrieval-model architecture description only; not TLGP route, mechanism, agency, self, AGI, or EGO evidence",
    }
