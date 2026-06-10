"""Minimal DER construction for RFC 3161 TimeStampReq (user-side, stdlib only)."""

SHA256_OID = "2.16.840.1.101.3.4.2.1"


def _len(n):
    if n < 0x80:
        return bytes([n])
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def tlv(tag, content):
    return bytes([tag]) + _len(len(content)) + content


def der_int(i):
    if i == 0:
        return tlv(0x02, b"\x00")
    body = i.to_bytes((i.bit_length() + 8) // 8, "big")  # extra byte keeps it positive
    while len(body) > 1 and body[0] == 0 and body[1] < 0x80:
        body = body[1:]
    return tlv(0x02, body)


def der_oid(dotted):
    parts = [int(x) for x in dotted.split(".")]
    body = bytes([40 * parts[0] + parts[1]])
    for p in parts[2:]:
        chunk = [p & 0x7F]
        p >>= 7
        while p:
            chunk.append(0x80 | (p & 0x7F))
            p >>= 7
        body += bytes(reversed(chunk))
    return tlv(0x06, body)


def der_bool(v):
    return tlv(0x01, b"\xff" if v else b"\x00")


def build_timestamp_request(digest32, nonce):
    """TimeStampReq: version=1, messageImprint{sha256, digest}, nonce, certReq=TRUE."""
    assert len(digest32) == 32
    alg = tlv(0x30, der_oid(SHA256_OID) + tlv(0x05, b""))      # AlgorithmIdentifier + NULL
    imprint = tlv(0x30, alg + tlv(0x04, digest32))             # MessageImprint
    return tlv(0x30, der_int(1) + imprint + der_int(nonce) + der_bool(True))
