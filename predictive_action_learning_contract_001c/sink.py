"""Anchored RFC 3161 commit sink (001 section 7.5 mode 2).

Every PRE_STEP commit is appended (flushed) to an explicit hash chain in
commits.log.jsonl. The chain head is anchored with an external RFC 3161 token
at seq 0, every ANCHOR_EVERY commits (synchronously, before that step's
outcome reveal), and at close(). Tokens live in anchors.log.jsonl sidecars,
never in trace.jsonl. Network access happens ONLY here, user-side. Anchoring
failure raises: tokens are never faked or backfilled."""

import hashlib
import json
import time
import os
import urllib.request
from datetime import datetime, timezone

from .der import build_timestamp_request

DEFAULT_TSA_URLS = ["https://freetsa.org/tsr", "http://timestamp.digicert.com"]
ANCHOR_EVERY = 200


class AnchoringError(RuntimeError):
    pass


def http_transport(url, tsq_der, timeout=30):
    req = urllib.request.Request(
        url, data=tsq_der, method="POST",
        headers={"Content-Type": "application/timestamp-query"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# Tests monkeypatch this module attribute with a local fake TSA. There is no
# test-only branch inside the sink itself.
TRANSPORT = http_transport


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _utc():
    return datetime.now(timezone.utc).isoformat()


class AnchoredRFC3161Sink:
    mode = "rfc3161_anchored"
    sink_id = "rfc3161_anchored_sink_v1"
    receipt_type = "chained_log_rfc3161_anchor"
    receipt_verifier_key_id = "rfc3161_tsa_token"
    externally_verifiable = True

    def __init__(self, run_dir, spec=None, tsa_urls=None, anchor_every=ANCHOR_EVERY):
        os.makedirs(run_dir, exist_ok=True)
        self.f = open(os.path.join(run_dir, "commits.log.jsonl"), "w", encoding="utf-8")
        self.af = open(os.path.join(run_dir, "anchors.log.jsonl"), "w", encoding="utf-8")
        self.tsa_urls = (tsa_urls or (spec or {}).get("tsa_urls")
                         or DEFAULT_TSA_URLS)
        self.anchor_every = anchor_every
        self.chain = ""
        self.seq = 0
        self.n_anchors = 0

    def commit(self, t, payload_sha256):
        entry = {
            "seq": self.seq,
            "t": t,
            "payload_sha256": payload_sha256,
            "commit_ts_utc": _utc(),
            "commit_monotonic_ns": time.monotonic_ns(),
            "sink_id": self.sink_id,
        }
        self.chain = hashlib.sha256((self.chain + _canonical(entry)).encode()).hexdigest()
        entry["commit_chain_hash"] = self.chain
        self.f.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")
        self.f.flush()
        receipt = dict(entry)
        receipt["receipt_type"] = self.receipt_type
        receipt["receipt_verifier_key_id"] = self.receipt_verifier_key_id
        if self.seq % self.anchor_every == 0:
            # synchronous: the token exists before this step's outcome reveal
            receipt["anchor"] = self._anchor(f"interval_seq_{self.seq}", self.seq)
        self.seq += 1
        return receipt

    def _anchor(self, reason, covers_seq):
        digest = bytes.fromhex(self.chain)
        nonce = int.from_bytes(hashlib.sha256(
            f"{self.chain}|{self.n_anchors}".encode()).digest()[:8], "big")
        tsq = build_timestamp_request(digest, nonce)
        token, used, errors = None, None, []
        for url in self.tsa_urls:
            try:
                token = TRANSPORT(url, tsq)
                used = url
                break
            except Exception as e:  # try fallback TSA, never fabricate
                errors.append(f"{url}: {e!r}")
        if token is None:
            raise AnchoringError(f"all TSAs unreachable; refusing to fake tokens: {errors}")
        rec = {
            "anchor_index": self.n_anchors,
            "reason": reason,
            "covers_through_seq": covers_seq,
            "chain_head": self.chain,
            "nonce": nonce,
            "tsa_url": used,
            "token_b64": __import__("base64").b64encode(token).decode(),
            "anchor_ts_utc": _utc(),
            "anchor_monotonic_ns": time.monotonic_ns(),
        }
        self.af.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
        self.af.flush()
        self.n_anchors += 1
        return {k: rec[k] for k in ("anchor_index", "chain_head", "tsa_url", "anchor_ts_utc")}

    def close(self):
        if self.seq > 0:
            self._anchor("final", self.seq - 1)
        self.f.close()
        self.af.close()
