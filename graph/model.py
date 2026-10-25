"""Graph model: SQLite rows -> labelled nodes and typed edges. Standard library only; opens every database read-only.

Quality graph (data/legacy.sqlite3):
  (Material)-[:SOURCED_AT]->(Site)        (Batch)-[:OF_MATERIAL]->(Material)   (Batch)-[:MADE_AT]->(Site)
  (Batch)-[:HAS_RESULT]->(LabResult)      (Batch)-[:HAS_DEVIATION]->(Deviation) (Deviation)-[:HAS_CAPA]->(CAPA)
  (Case)-[:AT_SITE]->(Site)               (Case)-[:FOR_ACCOUNT]->(Account)      (Case)-[:HAS_EVENT]->(CaseEvent)
Enterprise graph (data/enterprise_legacy.sqlite3):
  (OperationalObject)-[:BELONGS_TO]->(Organization)   (OperationalObject)-[:RELATES_TO {ref_id}]->(OperationalObject)

Free-text columns (case notes, event and evidence payloads) are deliberately not projected: they are untrusted source text.
"""
import contextlib
import os
import sqlite3


def _ro(path):
    """Read-only connection that is closed on exit (sqlite3's own context manager only commits)."""
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    con = sqlite3.connect("file:%s?mode=ro" % path.replace("\\", "/"), uri=True)
    con.row_factory = sqlite3.Row
    return contextlib.closing(con)


class Graph:
    """nodes: {label: {id: props}}, edges: {(type, src_label, dst_label): [(src_id, dst_id, props)]}"""

    def __init__(self):
        self.nodes, self.edges = {}, {}

    def node(self, label, nid, **props):
        if nid is None:
            return
        self.nodes.setdefault(label, {}).setdefault(nid, {}).update({k: v for k, v in props.items() if v is not None})

    def edge(self, etype, src_label, src, dst_label, dst, **props):
        if src is None or dst is None:
            return
        self.edges.setdefault((etype, src_label, dst_label), []).append((src, dst, props))

    def counts(self):
        return ({k: len(v) for k, v in sorted(self.nodes.items())},
                {"%s:%s->%s" % k: len(v) for k, v in sorted(self.edges.items())})


def extract_quality(g, legacy_db):
    with _ro(legacy_db) as c:
        for r in c.execute("SELECT * FROM materials"):
            g.node("Material", r["material_id"], name=r["material_name"], spec_version=r["spec_version"])
            g.node("Site", r["source_site"])
            g.edge("SOURCED_AT", "Material", r["material_id"], "Site", r["source_site"])
        for r in c.execute("SELECT * FROM batch_records"):
            g.node("Batch", r["batch_id"], observed_assay=r["observed_assay"], assay_unit=r["assay_unit"], qa_status=r["qa_status"])
            g.node("Site", r["batch_site"])
            g.edge("OF_MATERIAL", "Batch", r["batch_id"], "Material", r["material_id"])
            g.edge("MADE_AT", "Batch", r["batch_id"], "Site", r["batch_site"])
        for r in c.execute("SELECT * FROM lab_results"):
            g.node("LabResult", r["result_id"], analyte=r["analyte"], result_value=r["result_value"], unit=r["unit"],
                   test_status=r["test_status"], measured_at=r["measured_at"])
            g.edge("HAS_RESULT", "Batch", r["batch_id"], "LabResult", r["result_id"])
        for r in c.execute("SELECT * FROM deviations"):
            g.node("Deviation", r["deviation_id"], opened_at=r["opened_at"], classification=r["classification"],
                   root_cause=r["root_cause"], status=r["status"])
            g.edge("HAS_DEVIATION", "Batch", r["batch_id"], "Deviation", r["deviation_id"])
        for r in c.execute("SELECT * FROM capa_actions"):
            g.node("CAPA", r["capa_id"], owner=r["action_owner"], due_at=r["due_at"], state=r["state"])
            g.edge("HAS_CAPA", "Deviation", r["deviation_id"], "CAPA", r["capa_id"])
        for r in c.execute("SELECT id, account_id, segment, site, region, created_at, status, severity, amount, version FROM cases"):
            g.node("Case", r["id"], segment=r["segment"], region=r["region"], created_at=r["created_at"], status=r["status"],
                   severity=r["severity"], amount=r["amount"], version=r["version"])
            g.node("Site", r["site"])
            g.node("Account", r["account_id"])
            g.edge("AT_SITE", "Case", r["id"], "Site", r["site"])
            g.edge("FOR_ACCOUNT", "Case", r["id"], "Account", r["account_id"])
        for r in c.execute("SELECT id, case_id, recorded_at, event_type FROM events"):
            g.node("CaseEvent", r["id"], recorded_at=r["recorded_at"], event_type=r["event_type"])
            g.edge("HAS_EVENT", "Case", r["case_id"], "CaseEvent", r["id"])


def extract_enterprise(g, enterprise_db):
    with _ro(enterprise_db) as c:
        for r in c.execute("SELECT * FROM organizations"):
            g.node("Organization", r["org_id"], tenant=r["tenant"], region=r["region"], name=r["name"], valid_from=r["valid_from"])
        for r in c.execute("SELECT object_id, tenant, org_id, region, entity_type, status, value, owner_team, event_at, revision"
                           " FROM operational_objects"):
            g.node("OperationalObject", r["object_id"], tenant=r["tenant"], region=r["region"], entity_type=r["entity_type"],
                   status=r["status"], value=r["value"], owner_team=r["owner_team"], event_at=r["event_at"], revision=r["revision"])
            g.edge("BELONGS_TO", "OperationalObject", r["object_id"], "Organization", r["org_id"])
        for r in c.execute("SELECT * FROM cross_references"):
            g.edge("RELATES_TO", "OperationalObject", r["from_object"], "OperationalObject", r["to_object"], ref_id=r["ref_id"])


def build(legacy_db, enterprise_db=None):
    g = Graph()
    extract_quality(g, legacy_db)
    if enterprise_db:
        extract_enterprise(g, enterprise_db)
    return g
