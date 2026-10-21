"""Deviation register (BEH-CO-02). DV-01..DV-11 ship `proposed` (F10-2; Stage 20 DW-05 / FAC-06 adds DV-10, DV-11, the DV-07a
text and the DV-09 label). Only `approved` with a non-empty `approval_ref` counts as approved. Approval is Dinesh Naik's decision
(HAR-06), recorded OUTSIDE the product and only referenced here - the product has no command that approves a deviation.
Justification text is treated as Untrusted when rendered.

Stage 20 refresh rule: a row of an existing store is rewritten to the current seed text ONLY while it is still byte-identical to
the INC-02 seed row (same golden_ref, legacy_value, new_value, justification), status 'proposed' and approval_ref NULL - i.e. a
registration-text correction that cannot touch any human decision. Any other row is left exactly as it is.
"""
import json
import os

from hub.core.untrusted import Untrusted

SEED_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_s20.json")
SEED_INC02_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_inc02.json")


def load_seed(path=SEED_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def seed(con):
    s = load_seed()
    old = dict((r["dev_id"], r) for r in load_seed(SEED_INC02_PATH)["deviations"])
    with con:
        for r in s["deviations"]:
            con.execute("INSERT OR IGNORE INTO deviation_register(dev_id, golden_ref, legacy_value, new_value, "
                        "justification, approval_ref, status) VALUES (?,?,?,?,?,NULL,'proposed')",
                        (r["dev_id"], r["golden_ref"], r["legacy_value"], r["new_value"], r["justification"]))
            o = old.get(r["dev_id"])
            if o is not None and (o["golden_ref"], o["legacy_value"], o["new_value"], o["justification"]) != \
                    (r["golden_ref"], r["legacy_value"], r["new_value"], r["justification"]):
                con.execute("UPDATE deviation_register SET golden_ref = ?, legacy_value = ?, new_value = ?, justification = ? "
                            "WHERE dev_id = ? AND status = 'proposed' AND approval_ref IS NULL AND golden_ref = ? AND legacy_value = ? "
                            "AND new_value = ? AND justification = ?",
                            (r["golden_ref"], r["legacy_value"], r["new_value"], r["justification"], r["dev_id"],
                             o["golden_ref"], o["legacy_value"], o["new_value"], o["justification"]))
        for r in s["coexistence_inventory"]:
            con.execute("INSERT OR IGNORE INTO coexistence_inventory(item_id, description, owner, status) VALUES (?,?,?,?)",
                        (r["item_id"], r["description"], r["owner"], r["status"]))


def rows(con):
    cur = con.execute("SELECT dev_id, golden_ref, legacy_value, new_value, justification, approval_ref, status "
                      "FROM deviation_register ORDER BY dev_id")
    out = []
    for dev_id, golden_ref, legacy_value, new_value, justification, approval_ref, status in cur:
        out.append({"dev_id": dev_id, "golden_ref": golden_ref, "legacy_value": legacy_value,
                    "new_value": new_value, "justification": Untrusted(justification, "deviation_register"),
                    "approval_ref": approval_ref, "status": status})
    return out


def is_approved(row):
    ref = row.get("approval_ref")
    return row.get("status") == "approved" and isinstance(ref, str) and ref.strip() != ""


def inventory(con):
    return [dict(zip(("item_id", "description", "owner", "status"), r)) for r in
            con.execute("SELECT item_id, description, owner, status FROM coexistence_inventory ORDER BY item_id")]
