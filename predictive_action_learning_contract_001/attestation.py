"""Runtime attestation: measured (not merely self-reported) evidence that the
learner performs no file/network access, plus manifest and policy hashes.

A sys.addaudithook monitor counts os-level events (open/socket/connect) raised
while the learner's predict/observe calls are executing. Mechanism-level
retrieval is counted separately via explicit retrieval event logs. Combined
with cold-start duplicate runs and full trace replay, this gives structural
evidence beyond a self-declared flag (stop condition 6)."""

import hashlib
import os
import sys

from .trace import canonical_json, sha256_hex

_MONITORED = ("open", "socket.connect", "socket.getaddrinfo", "socket.__new__",
              "urllib.Request", "shutil.copyfile")


class AuditMonitor:
    """Process-global; audit hooks cannot be removed, so a singleton with an
    active flag gates counting to learner execution windows only."""
    _instance = None

    def __init__(self):
        self.active = False
        self.window_count = 0
        self.total_count = 0
        self.samples = []

        def hook(event, args):
            if self.active and event in _MONITORED:
                self.window_count += 1
                self.total_count += 1
                if len(self.samples) < 20:
                    self.samples.append({"event": event, "repr": repr(args)[:200]})

        sys.addaudithook(hook)

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = AuditMonitor()
        return cls._instance

    def window(self):
        return _Window(self)


class _Window:
    def __init__(self, mon):
        self.mon = mon

    def __enter__(self):
        self.mon.window_count = 0
        self.mon.active = True
        return self.mon

    def __exit__(self, *exc):
        self.mon.active = False
        return False


def runtime_manifest_hash(package_dir):
    """sha256 over sorted (relpath, sha256(bytes)) of package source files."""
    entries = []
    for root, _dirs, files in os.walk(package_dir):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if fn.endswith(".py"):
                p = os.path.join(root, fn)
                rel = os.path.relpath(p, package_dir).replace(os.sep, "/")
                with open(p, "rb") as f:
                    entries.append((rel, hashlib.sha256(f.read()).hexdigest()))
    entries.sort()
    return sha256_hex(canonical_json(entries))


STORAGE_POLICY = {
    "learner_storage": "in_memory_only",
    "trace_storage": "append_only_jsonl_written_by_harness",
    "commit_storage": "append_only_jsonl_local_mock",
    "persistence_between_runs": "none",
    "durability_note": "local mock sink uses flush() ordering, not fsync; "
                       "acceptable only because evidence is local-mock anyway",
}
NETWORK_POLICY = {
    "learner_network_access": "forbidden",
    "harness_network_access": "none",
    "enforcement": "sys.addaudithook counting of socket/open events during "
                   "learner predict/observe windows; required to be zero",
}
STORAGE_POLICY_HASH = sha256_hex(canonical_json(STORAGE_POLICY))
NETWORK_POLICY_HASH = sha256_hex(canonical_json(NETWORK_POLICY))
