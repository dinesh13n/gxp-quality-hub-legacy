"""Stage 23 autonomy / HITL catalogue tests (DW-18). zone_h.holders here are SYNTHETIC TEST DATA (holder-1, holder-2); the shipped list stays EMPTY. Synthetic, unvalidated.

  S40  docs/23-human-control/autonomy-catalogue.json is consistent with the code: ZH-01..ZH-10 (10 of 10) equal the choke point's action table and each id is
       found in hub/; every path, needle and test name the catalogue cites exists; HAR-01..HAR-16 are all classified
  S41  refusal matrix: for each of ZH-01..ZH-10 a missing authority_ref, a wrong re-authentication proof and a non-holder dispositioner are refused and write nothing
  S42  success matrix: ZH-01, 02, 03, 07, 08, 09 (not exercised through the choke point before Stage 23) each write exactly one Zone H event by a human holder with a
       holder_check_ref that points at an accepted ZONE_H_ATTEMPT audit record of that holder; the audit chain verifies
  S43  the shipped configuration ships the gate closed: holders [] and disposition mode none, and the authority switch defaults to shadow
"""
import json
import os
import re
import unittest

import _support as S
import _inc08 as W
from hub import config
from hub.gate.service import ZONE_H_ACTIONS
from hub.security import audit

CATALOGUE = os.path.join(S.CODE_ROOT, "docs", "23-human-control", "autonomy-catalogue.json")
ZH_ALL = ["ZH-%02d" % i for i in range(1, 11)]
HAR_ALL = ["HAR-%02d" % i for i in range(1, 17)]
EVENT_CFG = {"disposition": {"mode": "event", "values": ["accept", "reject", "hold"]}}
HOLDERS = {"zone_h": {"holders": ["holder-1", "holder-2"]}}  # SYNTHETIC TEST DATA


def setUpModule():
    W.skip_in_inner_egress_run()


def _read(rel):
    with open(os.path.join(S.CODE_ROOT, rel), encoding="utf-8") as f:
        return f.read()


def _tree_text(rel):
    p = os.path.join(S.CODE_ROOT, rel)
    if os.path.isfile(p):
        return _read(rel)
    out = []
    for d, _, fns in os.walk(p):
        for fn in sorted(fns):
            if fn.endswith((".py", ".sql", ".json")):
                with open(os.path.join(d, fn), encoding="utf-8") as f:
                    out.append(f.read())
    return "\n".join(out)


def _has_test(fn, name):
    with open(os.path.join(S.CODE_ROOT, "tests", "hub", fn), encoding="utf-8") as f:
        return any(re.match(r"\s+def test\w*" + re.escape(name), line) or (name in line and re.match(r"\s+def test", line)) for line in f)


class TST_HUB_STG23_Catalogue(unittest.TestCase):
    def setUp(self):
        with open(CATALOGUE, encoding="utf-8") as f:
            self.cat = json.load(f)

    def test_TST_HUB_STG23_S40_catalogue_matches_the_code(self):
        """S40 (DW-18): ZH-01..ZH-10 and HAR-01..HAR-16 are all catalogued; ZH ids equal the choke point's table; every cited path / needle / test exists."""
        cat = self.cat
        self.assertEqual([z["id"] for z in cat["zone_h"]], ZH_ALL)
        self.assertEqual(sorted(ZONE_H_ACTIONS), ZH_ALL)
        self.assertEqual(dict((z["id"], z["action"]) for z in cat["zone_h"]), ZONE_H_ACTIONS)
        self.assertEqual([h["id"] for h in cat["har"]], HAR_ALL)
        hub_text = "\n".join(_tree_text("hub/" + d) for d in ("gate", "policy", "runs", "decision", "web"))
        found = [z for z in ZH_ALL if z in hub_text]
        self.assertEqual(found, ZH_ALL)  # 10 of 10 ZH ids appear in hub/
        missing = []
        for z in cat["zone_h"]:
            self.assertTrue(z["code"] and z["tests"], z["id"])
        refs = [r for z in cat["zone_h"] for r in z["code"]] + [cat["zone_h_common"][k] for k in ("choke_point", "holder_check", "db_trigger")]
        refs += [r for h in cat["har"] for r in h["code"]]
        for path, needle in refs:
            if needle not in _tree_text(path):
                missing.append((path, needle))
        tests = [t for z in cat["zone_h"] for t in z["tests"]] + cat["zone_h_common"]["tests"] + [t for h in cat["har"] for t in h["tests"]]
        for fn, name in tests:
            if not os.path.exists(os.path.join(S.CODE_ROOT, "tests", "hub", fn)) or not _has_test(fn, name):
                missing.append((fn, name))
        self.assertEqual(missing, [])
        classes = dict((h["id"], h["class"]) for h in cat["har"])
        self.assertTrue(set(classes.values()) <= {"code-enforced", "partial", "process-only"})
        for h in cat["har"]:
            if h["class"] == "process-only":
                self.assertEqual((h["code"], h["tests"]), ([], []), h["id"])
            else:
                self.assertTrue(h["code"] and h["tests"], h["id"])
        from collections import Counter
        T = importlib_t()
        T.write_evidence("autonomy-catalogue-check.json", {"label": T.LABEL, "zh_ids_in_code": len(found), "zh_actions": len(ZONE_H_ACTIONS),
                                                          "har_classes": dict(Counter(classes.values())), "cited_references": len(refs), "cited_tests": len(tests)})

    def test_TST_HUB_STG23_S43_shipped_config_ships_the_gate_closed(self):
        """S43 (DW-18, DW-17): the shipped defaults keep zone_h.holders empty, disposition.mode none and every capability authority shadow."""
        from hub.control import flags
        from hub.security import settings
        cfg = config.load(None, {})
        s = settings.resolve(cfg)
        self.assertEqual(s["zone_h"]["holders"], [])
        self.assertEqual(flags.get(cfg, "disposition.mode", "none"), "none")
        self.assertEqual(cfg.get("capability_authority", {}), {})
        self.assertEqual(flags.nondefault(cfg), [])
        self.assertIs(flags.get(cfg, "schedule.enabled", False), False)


def importlib_t():
    import _stg23
    return _stg23


class _Base(unittest.TestCase):
    def setUp(self):
        self.stores = []

    def tearDown(self):
        for st in self.stores:
            st.close()

    def event_store(self):
        cfg = dict(EVENT_CFG)
        cfg.update(HOLDERS)
        st = W.WStore(extra=cfg)
        self.stores.append(st)
        st.case = st.new_case()
        return st


class TST_HUB_STG23_ZoneHMatrix(_Base):
    def test_TST_HUB_STG23_S41_refusal_matrix(self):
        """S41 (DW-18, HAR-12): for each of ZH-01..ZH-10, with synthetic holders configured: no authority_ref, a wrong re-authentication proof and a non-holder
        dispositioner are each refused and no Zone H event, policy event or flag action is written."""
        st = self.event_store()
        before = st.zh_counts()
        seen = {}
        for zh in ZH_ALL:
            ph = st.pack("holder-1", st.case).json()["pack_hash"]
            a = st.zh("holder-1", zh, {}, st.case, ph, authority_ref=None)
            b = st.zh("holder-1", zh, {}, st.case, ph, reauth_token="0" * 64)
            c = st.zh("nonholder", zh, {}, st.case, ph)
            seen[zh] = [(r.status, r.code) for r in (a, b, c)]
            self.assertEqual(c.code, "E-GATE-NOT-AUTHORISED", (zh, c.text))
            self.assertEqual(b.code, "E-GATE-REAUTH-REQUIRED", (zh, b.text))
            self.assertEqual(a.code, "E-POL-AUTHORITY-REQUIRED", (zh, a.text))
            for r in (a, b, c):
                self.assertGreaterEqual(r.status, 400, (zh, r.text))
        self.assertEqual(st.zh_counts(), before)
        import _stg23 as T
        T.write_evidence("zone-h-refusal-matrix.json", {"label": T.LABEL, "holders": "synthetic test data (holder-1, holder-2)", "results": seen})

    def test_TST_HUB_STG23_S42_success_matrix(self):
        """S42 (DW-18, HAR-12): ZH-01, 02, 03, 07, 08, 09 each write exactly one event by a human holder with a holder_check_ref -> the accepted attempt."""
        st = self.event_store()
        st.load_rules()
        ev = st.evidence(st.case)
        out = {}

        def ph():
            return st.pack("holder-1", st.case).json()["pack_hash"]
        cases = [("ZH-01", {"decision": "accept", "basis": "synthetic basis", "evidence_refs": [ev]}, True),
                 ("ZH-02", {"decision": "hold", "basis": "synthetic basis"}, True),
                 ("ZH-03", {"basis": "synthetic basis", "statement": "synthetic statement, not a signature"}, True),
                 ("ZH-07", {"ruleset_ref": "as-found-python@1", "reason": "synthetic reason"}, False),
                 ("ZH-08", {"mode": "event", "values": ["accept", "reject", "hold"]}, False),
                 ("ZH-09", {"enabled": True}, False)]
        for zh, payload, needs_case in cases:
            before = st.zh_counts()
            n_att = st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'success'")
            r = st.zh("holder-1", zh, payload, st.case if needs_case else None, ph() if needs_case else None)
            self.assertEqual(r.status, 201, (zh, r.text))
            body = r.json()
            self.assertEqual(body["action"], zh)
            after = st.zh_counts()
            self.assertEqual(sum(after) - sum(before), 1, (zh, before, after))
            self.assertGreaterEqual(st.count("audit_log", "action = 'ZONE_H_ATTEMPT' AND outcome = 'success'") - n_att, 1, (zh, "accepted attempts"))
            seq = int(body["holder_check_ref"].split(":")[1])
            row = st.con.execute("SELECT action, actor, actor_kind, outcome FROM audit_log WHERE audit_seq = ?", (seq,)).fetchone()
            self.assertEqual(tuple(row), ("ZONE_H_ATTEMPT", "holder-1", "human", "success"))
            out[zh] = {"event_ref": body["event_ref"], "holder_check_ref": body["holder_check_ref"]}
        self.assertEqual(audit.verify(st.con, st.anchor_path)["status"], "ok")
        import _stg23 as T
        T.write_evidence("zone-h-success-matrix.json", {"label": T.LABEL, "holders": "synthetic test data (holder-1, holder-2)", "results": out})


if __name__ == "__main__":
    unittest.main()
