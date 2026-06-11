"""TEST-ONLY local fake TSA. Generates an ephemeral RSA CA and signs
syntactically valid RFC 3161 TimeStampResp tokens. Issuer CN marks the tokens
as NON-EXTERNAL; the verifier must refuse to count them as external evidence.
Used to test sink/verifier logic offline. Never used in official runs."""

import hashlib
from datetime import datetime, timezone, timedelta

from asn1crypto import algos, cms, core, tsp, x509 as a_x509
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

TEST_CA_CN = "PALC001C TEST LOCAL CA - NOT EXTERNAL EVIDENCE"
_POLICY_OID = "1.3.6.1.4.1.99999.1"


class FakeTSA:
    def __init__(self):
        self.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, TEST_CA_CN)])
        now = datetime.now(timezone.utc)
        self.cert = (x509.CertificateBuilder()
                     .subject_name(name).issuer_name(name)
                     .public_key(self.key.public_key())
                     .serial_number(x509.random_serial_number())
                     .not_valid_before(now - timedelta(days=1))
                     .not_valid_after(now + timedelta(days=365))
                     .add_extension(x509.ExtendedKeyUsage(
                         [x509.oid.ExtendedKeyUsageOID.TIME_STAMPING]), critical=True)
                     .sign(self.key, hashes.SHA256()))
        self.cert_der = self.cert.public_bytes(serialization.Encoding.DER)
        self.serial = 0

    def transport(self, url, tsq_der):
        """Drop-in replacement for sink.TRANSPORT."""
        req = tsp.TimeStampReq.load(tsq_der)
        self.serial += 1
        tst = tsp.TSTInfo({
            "version": "v1",
            "policy": _POLICY_OID,
            "message_imprint": req["message_imprint"],
            "serial_number": self.serial,
            "gen_time": core.GeneralizedTime(datetime.now(timezone.utc)),
            "nonce": req["nonce"].native,
        })
        tst_der = tst.dump()
        signed_attrs = cms.CMSAttributes([
            cms.CMSAttribute({"type": "content_type", "values": ["tst_info"]}),
            cms.CMSAttribute({"type": "message_digest",
                              "values": [hashlib.sha256(tst_der).digest()]}),
        ])
        # signature is over the EXPLICIT SET OF (0x31) re-tagged signed attrs
        sig_input = b"\x31" + signed_attrs.dump()[1:]
        signature = self.key.sign(sig_input, padding.PKCS1v15(), hashes.SHA256())
        signer = cms.SignerInfo({
            "version": "v1",
            "sid": cms.SignerIdentifier({"issuer_and_serial_number":
                cms.IssuerAndSerialNumber({
                    "issuer": a_x509.Certificate.load(self.cert_der).subject,
                    "serial_number": self.cert.serial_number})}),
            "digest_algorithm": algos.DigestAlgorithm({"algorithm": "sha256"}),
            "signed_attrs": signed_attrs,
            "signature_algorithm": algos.SignedDigestAlgorithm(
                {"algorithm": "rsassa_pkcs1v15", "parameters": core.Null()}),
            "signature": signature,
        })
        sd = cms.SignedData({
            "version": "v3",
            "digest_algorithms": [algos.DigestAlgorithm({"algorithm": "sha256"})],
            "encap_content_info": cms.EncapsulatedContentInfo({
                "content_type": "tst_info",
                "content": core.ParsableOctetString(tst_der)}),
            "certificates": [cms.CertificateChoices(
                name="certificate", value=a_x509.Certificate.load(self.cert_der))],
            "signer_infos": [signer],
        })
        resp = tsp.TimeStampResp({
            "status": tsp.PKIStatusInfo({"status": "granted"}),
            "time_stamp_token": cms.ContentInfo({"content_type": "signed_data",
                                                 "content": sd}),
        })
        return resp.dump()
