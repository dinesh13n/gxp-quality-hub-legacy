"""Read-only inputs of the crosswalk rule matcher from the legacy snapshot (AD-01; LT-05 reads the document JSONL).

Snapshot first, pinned sha256, `mode=ro&immutable=1` (hub.adapters.legacy_sqlite): the working-tree `data/` is never opened.
Only identifier columns are read - no free text. The document file is read as bytes (its sha256 is reported) from the sandbox
copy; a missing file leaves LT-05 not run (reported), never an error.
"""
import hashlib
import json
import os

from hub.crosswalk.service import identity_targets
from hub.guards import sandbox

DOC_REL = os.path.join("data", "documents", "source_documents.jsonl")


def legacy_inputs(handle):
    """{code: (items, targets)} for LT-01..LT-04 from an open read-only legacy handle."""
    batches = [r[0] for r in handle.execute("SELECT batch_id FROM batch_records ORDER BY batch_id")]
    devs = [r[0] for r in handle.execute("SELECT deviation_id FROM deviations ORDER BY deviation_id")]
    cases = [r[0] for r in handle.execute("SELECT id FROM cases ORDER BY id")]
    return {
        "LT-01": ([(r[0], r[1]) for r in handle.execute("SELECT deviation_id, batch_id FROM deviations ORDER BY deviation_id")],
                  identity_targets(batches)),
        "LT-02": ([(r[0], r[1]) for r in handle.execute("SELECT capa_id, deviation_id FROM capa_actions ORDER BY capa_id")],
                  identity_targets(devs)),
        "LT-03": ([(r[0], r[1]) for r in handle.execute("SELECT result_id, batch_id FROM lab_results ORDER BY result_id")],
                  identity_targets(batches)),
        "LT-04": ([(r[0], r[1]) for r in handle.execute("SELECT feed_id, ref_id FROM partner_feeds ORDER BY feed_id")],
                  identity_targets(cases)),
    }, cases


def document_items(legacy_root):
    """LT-05 items [(doc_id, reference)] and the file's sha256, or (None, None) when the file is absent."""
    sandbox.assert_safe_path(legacy_root, "legacy source root")
    path = os.path.join(legacy_root, DOC_REL)
    if not os.path.isfile(path):
        return None, None
    with open(path, "rb") as f:
        raw = f.read()
    items = []
    for line in raw.decode("utf-8").splitlines():
        if line.strip():
            d = json.loads(line)
            items.append((d["doc_id"], d.get("reference")))
    return items, hashlib.sha256(raw).hexdigest()
