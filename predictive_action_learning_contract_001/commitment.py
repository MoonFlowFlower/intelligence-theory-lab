"""Pre-outcome commitment sinks (task card section 7.5).

Only the LOCAL MOCK sink is implemented. External RFC3161 / transparency-log
sinks are external services, which the lab boundary forbids; therefore the
evidence verdict for any run committed through the local mock is capped at
protocol_blocked_by_T1_external_commit_missing. Do not fake external receipts.
"""

import json
import time
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).isoformat()


class LocalMockCommitSink:
    sink_id = "local_mock_sink_v1"
    receipt_type = "local_mock"
    receipt_verifier_key_id = "local_mock_unverifiable"
    externally_verifiable = False

    def __init__(self, path):
        self.path = path
        self.f = open(path, "w", encoding="utf-8")
        self.seq = 0

    def commit(self, t, payload_sha256):
        """Append the commitment BEFORE the outcome is revealed; flush so the
        OS-visible log precedes the reveal. Local mock only: forgeable by the
        process that owns the file, hence not external evidence."""
        rec = {
            "seq": self.seq,
            "t": t,
            "payload_sha256": payload_sha256,
            "commit_ts_utc": utc_now(),
            "commit_monotonic_ns": time.monotonic_ns(),
            "sink_id": self.sink_id,
        }
        self.f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
        self.f.flush()
        self.seq += 1
        receipt = dict(rec)
        receipt["receipt_type"] = self.receipt_type
        receipt["receipt_verifier_key_id"] = self.receipt_verifier_key_id
        return receipt

    def close(self):
        self.f.close()


class DisabledCommitSink:
    """Ablation 5: pre-commit disabled. The gate evaluation must block the
    evidence verdict for any run using this sink."""
    sink_id = "commit_disabled"
    receipt_type = "none"
    receipt_verifier_key_id = "none"
    externally_verifiable = False

    def __init__(self, path=None):
        pass

    def commit(self, t, payload_sha256):
        return None

    def close(self):
        pass


def load_commit_log(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
