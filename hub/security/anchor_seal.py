"""Opt-in HMAC seal for the audit anchor file (Stage 24, DW-19 'anchor location / strength'; RTD-29, R-SEC-1). Synthetic, unvalidated.

The anchor (hub.security.audit) is an unsigned JSON-lines file on the same host: someone who can rewrite BOTH the database and the anchor file can
present a consistent but false history. The seal adds a keyed layer that needs a secret the database and the anchor do not contain:

  mac_0 = 64 x "0";   mac_i = HMAC-SHA256(key, mac_{i-1} || canonical({audit_seq, hash, occurred_at}))   for anchor line i
  seal file (default <anchor_path>.seal, may be kept elsewhere): one canonical-JSON line {n, audit_seq, mac} per sealed anchor line.

`seal` verifies the already-sealed prefix and appends the missing entries (append-only). `check` reports: ok; seal_mismatch (an anchor line was edited,
moved or removed inside the sealed range); anchor_truncated (the seal knows more lines than the anchor holds); and the number of unsealed tail anchors
(anchors written since the last `seal`, not an error). The key comes from the environment variable HUB_ANCHOR_SEAL_KEY (at least 32 bytes) and is never
read from config, written to audit, log, anchor or seal, or echoed.
LIMITS (residual risk RS-03, said plainly): it is NOT a signature scheme with an external verifier; whoever holds the key and the host can re-seal a
forged anchor; deleting the anchor AND the seal together is not detected by this module; records appended after the last seal are unprotected until the
next `seal`. A stronger design (an append-only store or witness on another host, signed checkpoints) is option C of docs/24-security-privacy/
data-protection-controls.md and needs Dinesh's decision (DQ-S24-02). The seal is OFF unless an operator runs it.
"""
import hashlib
import hmac
import json
import os

from hub.core.errors import ConfigInvalid
from hub.security import audit
from hub.security.canonical import GENESIS, canonical
from hub.security.errors import AuditTamperDetected

KEY_ENV = "HUB_ANCHOR_SEAL_KEY"
MIN_KEY_BYTES = 32


def load_key(environ=None, name=KEY_ENV):
    value = (environ if environ is not None else os.environ).get(name)
    if not value or len(value.encode("utf-8")) < MIN_KEY_BYTES:
        raise ConfigInvalid({"env": name, "reason": "the seal key must be set in the environment, at least %d bytes (never in config)" % MIN_KEY_BYTES})
    return value.encode("utf-8")


def seal_path_for(anchor_path, seal_path=None):
    return seal_path or (anchor_path + ".seal")


def _mac(key, prev, anchor):
    body = canonical({"audit_seq": anchor["audit_seq"], "hash": anchor["hash"], "occurred_at": anchor.get("occurred_at")})
    return hmac.new(key, (prev + body).encode("ascii"), hashlib.sha256).hexdigest()


def _read_seal(path):
    out = []
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def _expected(key, anchors):
    prev, macs = GENESIS, []
    for a in anchors:
        prev = _mac(key, prev, a)
        macs.append(prev)
    return macs


def check(anchor_path, key, seal_path=None):
    """Report dict; status 'ok' or 'broken' (kind seal_mismatch / anchor_truncated, with the 1-based line)."""
    sp = seal_path_for(anchor_path, seal_path)
    anchors = audit.read_anchors(anchor_path)
    sealed = _read_seal(sp)
    exp = _expected(key, anchors)
    if len(sealed) > len(anchors):
        return {"status": "broken", "kind": "anchor_truncated", "anchor_lines": len(anchors), "sealed_lines": len(sealed), "first_broken_line": len(anchors) + 1}
    for i, entry in enumerate(sealed):
        if entry.get("mac") != exp[i] or entry.get("audit_seq") != anchors[i]["audit_seq"] or entry.get("n") != i + 1:
            return {"status": "broken", "kind": "seal_mismatch", "anchor_lines": len(anchors), "sealed_lines": len(sealed), "first_broken_line": i + 1}
    return {"status": "ok", "anchor_lines": len(anchors), "sealed_lines": len(sealed), "unsealed_tail": len(anchors) - len(sealed),
            "limitation": "a holder of the key and the host can re-seal; anchor + seal deleted together is not detected (RS-03)"}


def seal(anchor_path, key, seal_path=None):
    """Append the missing seal entries (after verifying the sealed prefix). Raises E-SEC-AUDIT-TAMPER-DETECTED if the prefix does not verify."""
    rep = check(anchor_path, key, seal_path)
    if rep["status"] != "ok":
        raise AuditTamperDetected(rep)
    sp = seal_path_for(anchor_path, seal_path)
    anchors = audit.read_anchors(anchor_path)
    exp = _expected(key, anchors)
    start = rep["sealed_lines"]
    if start < len(anchors):
        d = os.path.dirname(sp)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(sp, "a", encoding="utf-8") as f:
            for i in range(start, len(anchors)):
                f.write(canonical({"n": i + 1, "audit_seq": anchors[i]["audit_seq"], "mac": exp[i]}) + "\n")
            f.flush()
            os.fsync(f.fileno())
    return {"status": "ok", "anchor_lines": len(anchors), "sealed_lines": len(anchors), "newly_sealed": len(anchors) - start}
