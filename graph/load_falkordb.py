"""Load the legacy estate into FalkorDB for browsing in FalkorDB Browser (http://localhost:3000).

  python -m graph.load_falkordb [--host localhost] [--port 6379] [--graph gxp_quality] [--no-enterprise] [--dry-run]

The graph is dropped and rebuilt on every run (idempotent). Source databases are opened read-only.
"""
import argparse
import os

from graph import model

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH = 1000


def _chunks(rows):
    for i in range(0, len(rows), BATCH):
        yield rows[i:i + BATCH]


def load(g, host, port, name):
    from falkordb import FalkorDB  # third-party; only needed for an actual load
    db = FalkorDB(host=host, port=port)
    if name in db.list_graphs():
        db.select_graph(name).delete()
    fg = db.select_graph(name)
    for label in g.nodes:
        fg.query("CREATE INDEX FOR (n:%s) ON (n.id)" % label)
    for label, items in g.nodes.items():
        rows = [dict(props, id=nid) for nid, props in items.items()]
        for chunk in _chunks(rows):
            fg.query("UNWIND $rows AS r CREATE (n:%s) SET n = r" % label, {"rows": chunk})
    for (etype, src_label, dst_label), items in g.edges.items():
        rows = [{"s": s, "d": d, "p": p} for s, d, p in items]
        for chunk in _chunks(rows):
            fg.query("UNWIND $rows AS r MATCH (a:%s {id: r.s}), (b:%s {id: r.d}) CREATE (a)-[e:%s]->(b) SET e = r.p"
                     % (src_label, dst_label, etype), {"rows": chunk})
    return fg.query("MATCH (n) RETURN count(n)").result_set[0][0], fg.query("MATCH ()-[e]->() RETURN count(e)").result_set[0][0]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="python -m graph.load_falkordb", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--legacy-db", default=os.environ.get("LEGACY_DB", os.path.join(ROOT, "data", "legacy.sqlite3")))
    ap.add_argument("--enterprise-db", default=os.path.join(ROOT, "data", "enterprise_legacy.sqlite3"))
    ap.add_argument("--no-enterprise", action="store_true", help="skip the 12,500-object enterprise graph")
    ap.add_argument("--host", default=os.environ.get("FALKORDB_HOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("FALKORDB_PORT", "6379")))
    ap.add_argument("--graph", default="gxp_quality")
    ap.add_argument("--dry-run", action="store_true", help="extract and print counts; do not connect")
    a = ap.parse_args(argv)
    g = model.build(a.legacy_db, None if a.no_enterprise else a.enterprise_db)
    nodes, edges = g.counts()
    for k, v in list(nodes.items()) + list(edges.items()):
        print("%-50s %7d" % (k, v))
    if a.dry_run:
        return 0
    n, e = load(g, a.host, a.port, a.graph)
    print("loaded graph %r: %d nodes, %d edges -> open http://localhost:3000 and select it" % (a.graph, n, e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
