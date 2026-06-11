"""001C driver.

`run-suite-external` (USER-SIDE, stdlib only, network required): reruns the
frozen 001 suite with the anchored RFC 3161 sink. No verification deps needed.

`verify-artifacts` (OFFLINE): anchor verification, masked behavioral equality
against the 001 reference suite, 001 gate re-evaluation, 001C verdict assembly.
"""

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)

from predictive_action_learning_contract_001 import config as cfg  # noqa: E402
from predictive_action_learning_contract_001 import suite as S  # noqa: E402
from predictive_action_learning_contract_001.runner import run_episode  # noqa: E402
from . import sink as sinkmod  # noqa: E402
from .der import build_timestamp_request  # noqa: E402

DEFAULT_REFERENCE = os.path.join(
    "artifacts", "predictive_action_learning_contract_001", "suite_2026-06-10_r1")
RESIDUAL_ASSUMPTIONS = (
    "Residual trust assumptions (001C card section 10): the environment is a seeded "
    "deterministic simulation - anchors prove that committed PRE_STEP content existed "
    "no later than the anchor genTime (and, at anchor steps, before that step's own "
    "outcome reveal); they do not prove outcome unpredictability. obs_reveal_ts between "
    "anchors remains self-reported. Signer authenticity rests on the certificate "
    "embedded in each token; fingerprints are reported for out-of-band confirmation."
)


def _suite_anchor(suite_dir, label, digest32, tsa_urls):
    nonce = int.from_bytes(hashlib.sha256(
        (label + digest32.hex()).encode()).digest()[:8], "big")
    tsq = build_timestamp_request(digest32, nonce)
    token, used, errors = None, None, []
    for url in tsa_urls:
        try:
            token = sinkmod.TRANSPORT(url, tsq)
            used = url
            break
        except Exception as e:
            errors.append(f"{url}: {e!r}")
    if token is None:
        raise sinkmod.AnchoringError(f"suite anchor '{label}' failed: {errors}")
    rec = {"label": label, "digest": digest32.hex(), "nonce": nonce, "tsa_url": used,
           "token_b64": base64.b64encode(token).decode(),
           "anchor_ts_utc": datetime.now(timezone.utc).isoformat()}
    with open(os.path.join(suite_dir, "suite_anchors.log.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")
    return rec


def _final_chain_heads(suite_dir):
    heads = {}
    runs = os.path.join(suite_dir, "runs")
    for run_id in sorted(os.listdir(runs)):
        p = os.path.join(runs, run_id, "commits.log.jsonl")
        if not os.path.exists(p):
            continue
        last = None
        with open(p, encoding="utf-8") as f:
            for line in f:
                last = line
        if last:
            heads[run_id] = json.loads(last)["commit_chain_hash"]
    return heads


def run_suite_external(suite_dir, tsa_urls=None):
    tsa_urls = tsa_urls or sinkmod.DEFAULT_TSA_URLS
    conf = S.write_config_artifact(suite_dir)
    from predictive_action_learning_contract_001.reporting import write_readme
    write_readme(suite_dir)
    cfg_bytes = open(os.path.join(suite_dir, "CONFIG.json"), "rb").read()
    _suite_anchor(suite_dir, "suite_start_config",
                  hashlib.sha256(cfg_bytes).digest(), tsa_urls)
    groups = S.build_specs()
    for group in ("core", "baselines", "ablations", "protocol", "perturbations"):
        for spec in groups[group]:
            spec = dict(spec)
            if spec.get("commit") != "disabled":
                spec["commit"] = "rfc3161_anchored"
                spec["tsa_urls"] = tsa_urls
            spec["config_manifest_hash"] = conf["config_manifest_hash"]
            run_episode(spec, os.path.join(suite_dir, "runs", spec["run_id"]))
            print(f"ran {spec['run_id']}", flush=True)
    base = dict(groups["core"][0])
    for tag in ("dup_a", "dup_b"):   # cold-start duplicates in fresh processes
        spec = dict(base)
        spec.update({"run_id": f"b9_coldstart_{tag}", "group": "baselines",
                     "baseline_id": "b9_coldstart_duplicate",
                     "commit": "rfc3161_anchored", "tsa_urls": tsa_urls})
        r = subprocess.run(
            [sys.executable, "-m", "predictive_action_learning_contract_001",
             "run-single", "--suite-dir", suite_dir, "--spec-json", json.dumps(spec)],
            cwd=_REPO, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"duplicate {tag} failed: {r.stderr[-1500:]}")
        print(f"ran b9_coldstart_{tag}", flush=True)
    heads = _final_chain_heads(suite_dir)
    digest = hashlib.sha256(json.dumps(
        heads, sort_keys=True, separators=(",", ":")).encode()).digest()
    _suite_anchor(suite_dir, "suite_end_all_run_chain_heads", digest, tsa_urls)
    print("suite complete; hand the suite directory back for offline verification")


def verify_artifacts(suite_dir, reference, tests_exit_code, tests_summary):
    from .compare import compare_suite
    from .verify import verify_run_dir, verify_token
    from predictive_action_learning_contract_001.reporting import finalize
    from predictive_action_learning_contract_001.trace import load_trace
    from predictive_action_learning_contract_001.validator import split_records

    anchor_reports, errors = {}, []
    runs_dir = os.path.join(suite_dir, "runs")
    any_test_ca, all_external = False, True
    for run_id in sorted(os.listdir(runs_dir)):
        rd = os.path.join(runs_dir, run_id)
        meta = split_records(load_trace(os.path.join(rd, "trace.jsonl")))[0]
        if meta.get("commit_mode") == "disabled":
            anchor_reports[run_id] = {"skipped": "commit disabled by ablation 5",
                                      "anchors_present": os.path.exists(
                                          os.path.join(rd, "anchors.log.jsonl"))}
            continue
        rep = verify_run_dir(rd)
        anchor_reports[run_id] = rep
        any_test_ca |= any(a.get("is_test_ca") for a in rep["anchors"])
        all_external &= rep["external_valid"]
        if not rep["ok"]:
            errors.append(f"{run_id}: {rep['errors']}")

    suite_anchor_results = []
    sa_path = os.path.join(suite_dir, "suite_anchors.log.jsonl")
    if os.path.exists(sa_path):
        cfg_digest = hashlib.sha256(
            open(os.path.join(suite_dir, "CONFIG.json"), "rb").read()).hexdigest()
        heads_digest = hashlib.sha256(json.dumps(
            _final_chain_heads(suite_dir), sort_keys=True,
            separators=(",", ":")).encode()).hexdigest()
        expected = {"suite_start_config": cfg_digest,
                    "suite_end_all_run_chain_heads": heads_digest}
        for line in open(sa_path, encoding="utf-8"):
            a = json.loads(line)
            exp = expected.get(a["label"])
            v = verify_token(base64.b64decode(a["token_b64"]), a["digest"],
                             expected_nonce=a.get("nonce"))
            if exp is not None and a["digest"] != exp:
                v["ok"] = False
                v["errors"].append("suite anchor digest != recomputed value")
            suite_anchor_results.append({"label": a["label"], **v})
            any_test_ca |= bool(v["is_test_ca"])
            all_external &= bool(v["ok"]) and not v["is_test_ca"]
            if not v["ok"]:
                errors.append(f"suite anchor {a['label']}: {v['errors']}")
    else:
        errors.append("suite_anchors.log.jsonl missing")
        all_external = False

    equality = compare_suite(suite_dir, reference)
    res001 = finalize(suite_dir, {"exit_code": tests_exit_code, "summary": tests_summary})
    mech_ok = res001["verdicts"]["evidence_verdict"] == \
        "protocol_blocked_by_T1_external_commit_missing"  # frozen 001 logic: mech gates passed
    impl = res001["verdicts"]["implementation_verdict"]

    if mech_ok and equality["all_identical"] and all_external and not errors:
        evidence = "bounded_contract_pass"
        ceiling = ("The frozen predictive-action learning contract passed the bounded "
                   "isolated experiment, including externally verifiable RFC 3161 "
                   "pre-outcome commitment anchoring, under the stated residual trust "
                   "assumptions.")
    elif mech_ok and equality["all_identical"] and any_test_ca and not errors:
        evidence = "protocol_blocked_by_T1_external_commit_missing"
        ceiling = ("Implementation-test tokens only (local test CA); external evidence "
                   "remains blocked.")
    else:
        evidence = "bounded_contract_fail" if not mech_ok or not equality["all_identical"] \
            else "protocol_blocked"
        ceiling = cfg.CLAIM_CEILING_FAIL if evidence == "bounded_contract_fail" else \
            "Evidence blocked: anchor verification incomplete."

    result = {
        "task_id": "predictive_action_learning_contract_001c",
        "task_card": "PREDICTIVE-ACTION-LEARNING-CONTRACT-001C-T1-EXTERNAL-COMMIT",
        "predecessor": "PREDICTIVE-ACTION-LEARNING-CONTRACT-001 / 001B closeout",
        "implementation_verdict": impl,
        "evidence_verdict": evidence,
        "claim_mode": cfg.CLAIM_MODE,
        "claim_ceiling": ceiling,
        "residual_trust_assumptions": RESIDUAL_ASSUMPTIONS,
        "anchor_verification_ok_all_runs": not errors,
        "anchors_signed_by_test_ca": any_test_ca,
        "anchors_externally_valid": all_external,
        "masked_equality_vs_001": {"all_identical": equality["all_identical"]},
        "frozen_001_gate_outcome": res001["verdicts"],
        "errors": errors[:20],
    }
    with open(os.path.join(suite_dir, "anchor_verification.json"), "w", encoding="utf-8") as f:
        json.dump({"runs": anchor_reports, "suite_anchors": suite_anchor_results},
                  f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(suite_dir, "masked_equality.json"), "w", encoding="utf-8") as f:
        json.dump(equality, f, indent=1, sort_keys=True)
    with open(os.path.join(suite_dir, "result_001c.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    with open(os.path.join(suite_dir, "FINAL_REPORT_001C.md"), "w", encoding="utf-8") as f:
        f.write(_final_report_md(result, equality, anchor_reports))
    return result


def _final_report_md(result, equality, anchor_reports):
    n_anchored = sum(1 for r in anchor_reports.values() if "anchors" in r)
    return f"""# FINAL REPORT - PREDICTIVE-ACTION-LEARNING-CONTRACT-001C

- implementation_verdict: `{result['implementation_verdict']}`
- evidence_verdict: `{result['evidence_verdict']}`
- anchored runs verified: {n_anchored}
- anchors signed by test CA (non-external): {result['anchors_signed_by_test_ca']}
- masked behavioral equality vs 001 reference: {equality['all_identical']}
- frozen 001 gate outcome: `{result['frozen_001_gate_outcome']['evidence_verdict']}`
  (in-suite result.json keeps 001's frozen local-mock precedence by design;
  this report supersedes it for the commitment question only)

## Claim ceiling

{result['claim_ceiling']}

{result['residual_trust_assumptions']}

This report does not support: consciousness, subjective experience, real
emotion, self-awareness, agency, functional-subject evidence, electronic life,
companion readiness, AGI, biological equivalence, predictive superiority over
retrieval, or any total-theory claim.
"""
