"""Offline RFC 3161 anchor verification (no network).

Verifies, per anchor: response status, token signature (signer certificate
embedded in the token), messageImprint == independently recomputed chain head,
nonce binding, genTime monotonicity; and per run: chain recomputation from the
raw commit log, full anchor coverage of every commit, and trace<->log
consistency (delegated to the 001 validator). Reports the signer certificate
fingerprint and refuses to mark test-CA-signed tokens as external evidence."""

import base64
import hashlib
import json
import os

from asn1crypto import cms, tsp
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding

from .fake_tsa import TEST_CA_CN


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def verify_token(token_der, expected_head_hex, expected_nonce=None):
    out = {"ok": False, "errors": [], "gen_time": None,
           "signer_cn": None, "signer_sha256_fingerprint": None, "is_test_ca": None}
    try:
        resp = tsp.TimeStampResp.load(token_der)
        if resp["status"]["status"].native not in ("granted", "granted_with_mods"):
            out["errors"].append(f"status={resp['status']['status'].native}")
            return out
        token = resp["time_stamp_token"]
        sd = token["content"]
        tst_der = bytes(sd["encap_content_info"]["content"])  # raw encapsulated octets
        tst = tsp.TSTInfo.load(tst_der)
        if tst["message_imprint"]["hashed_message"].native != bytes.fromhex(expected_head_hex):
            out["errors"].append("messageImprint != recomputed chain head")
        if expected_nonce is not None and tst["nonce"].native != expected_nonce:
            out["errors"].append("nonce mismatch")
        out["gen_time"] = tst["gen_time"].native.isoformat()

        signer = sd["signer_infos"][0]
        certs = [c.chosen for c in sd["certificates"]]
        cert = _match_signer_cert(signer, certs)
        if cert is None:
            out["errors"].append("signer certificate not present in token")
            return out
        cert_der = cert.dump()
        out["signer_sha256_fingerprint"] = hashlib.sha256(cert_der).hexdigest()
        cobj = x509.load_der_x509_certificate(cert_der)
        cns = cobj.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        out["signer_cn"] = cns[0].value if cns else None
        out["is_test_ca"] = out["signer_cn"] == TEST_CA_CN

        digest_alg = signer["digest_algorithm"]["algorithm"].native
        hashfn = {"sha256": hashlib.sha256, "sha384": hashlib.sha384,
                  "sha512": hashlib.sha512}.get(digest_alg)
        if hashfn is None:
            out["errors"].append(f"unsupported signer digest algorithm {digest_alg}")
            return out
        sattrs = signer["signed_attrs"]
        md = next(a for a in sattrs if a["type"].native == "message_digest")
        if md["values"][0].native != hashfn(tst_der).digest():
            out["errors"].append(f"signed messageDigest != {digest_alg}(TSTInfo)")
        sig_input = b"\x31" + sattrs.dump()[1:]
        try:
            _verify_signature(cobj, signer, sig_input, digest_alg)
        except Exception as e:
            out["errors"].append(f"signature invalid: {e!r}")
        out["ok"] = not out["errors"]
        return out
    except Exception as e:
        out["errors"].append(f"token parse failure: {e!r}")
        return out


def _match_signer_cert(signer, certs):
    sid = signer["sid"]
    if sid.name != "issuer_and_serial_number":
        return certs[0] if certs else None
    serial = sid.chosen["serial_number"].native
    for c in certs:
        if c["tbs_certificate"]["serial_number"].native == serial:
            return c
    return None


def _verify_signature(cert_obj, signer, sig_input, digest_alg="sha256"):
    pub = cert_obj.public_key()
    sig = signer["signature"].native
    alg = signer["signature_algorithm"]["algorithm"].native
    h = {"sha256": hashes.SHA256(), "sha384": hashes.SHA384(),
         "sha512": hashes.SHA512()}[digest_alg]
    if isinstance(pub, ec.EllipticCurvePublicKey):
        pub.verify(sig, sig_input, ec.ECDSA(h))
    elif alg in ("rsassa_pkcs1v15", "rsa") or alg.endswith("_rsa"):
        pub.verify(sig, sig_input, padding.PKCS1v15(), h)
    else:
        raise ValueError(f"unsupported signature algorithm {alg}")


def recompute_chain(commit_log_path):
    """Independently recompute the chain heads from the raw commit log."""
    heads, chain = [], ""
    with open(commit_log_path, encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            stored = entry.pop("commit_chain_hash")
            chain = hashlib.sha256((chain + _canonical(entry)).encode()).hexdigest()
            heads.append({"seq": entry["seq"], "head": chain, "stored": stored,
                          "match": chain == stored})
    return heads


def verify_run_dir(run_dir):
    report = {"run_dir": run_dir, "ok": False, "errors": [], "anchors": [],
              "n_commits": 0, "external_valid": False}
    anchors_path = os.path.join(run_dir, "anchors.log.jsonl")
    commits_path = os.path.join(run_dir, "commits.log.jsonl")
    if not os.path.exists(anchors_path):
        report["errors"].append("anchors.log.jsonl missing")
        return report
    heads = recompute_chain(commits_path)
    report["n_commits"] = len(heads)
    bad = [h for h in heads if not h["match"]]
    if bad:
        report["errors"].append(
            f"chain recomputation mismatch at seq {bad[0]['seq']} "
            "(commit log tampered or entries missing)")
    by_seq = {h["seq"]: h["head"] for h in heads}
    anchors = [json.loads(x) for x in open(anchors_path, encoding="utf-8")]
    last_time = None
    covered = -1
    any_test_ca = False
    for a in anchors:
        seq = a["covers_through_seq"]
        expected = by_seq.get(seq)
        v = verify_token(base64.b64decode(a["token_b64"]),
                         a["chain_head"], expected_nonce=a.get("nonce"))
        if expected is None:
            v["errors"].append(f"anchor covers unknown seq {seq}")
            v["ok"] = False
        elif expected != a["chain_head"]:
            v["errors"].append("stored chain_head != recomputed head at covered seq")
            v["ok"] = False
        if v["gen_time"] is not None and last_time is not None and v["gen_time"] < last_time:
            v["errors"].append("genTime not monotonic")
            v["ok"] = False
        last_time = v["gen_time"] or last_time
        any_test_ca |= bool(v["is_test_ca"])
        covered = max(covered, seq)
        report["anchors"].append({"anchor_index": a["anchor_index"],
                                  "reason": a["reason"], "covers_through_seq": seq,
                                  "tsa_url": a.get("tsa_url"), **v})
    if heads and covered < heads[-1]["seq"]:
        report["errors"].append(
            f"coverage gap: last commit seq {heads[-1]['seq']} not covered by any anchor")
    if not anchors and heads:
        report["errors"].append("no anchors present")
    for a in report["anchors"]:
        if not a["ok"]:
            report["errors"].append(
                f"anchor {a['anchor_index']} ({a['reason']}): {a['errors']}")
    all_ok = all(a["ok"] for a in report["anchors"]) and not report["errors"]
    report["ok"] = all_ok
    report["external_valid"] = all_ok and not any_test_ca and report["n_commits"] > 0
    if any_test_ca:
        report["errors"].append(
            "tokens signed by the TEST LOCAL CA: valid for implementation tests only, "
            "never external evidence")
    return report
