"""Runtime FTS5 / trigram detection (BEH-REV-06, OD-S12-12 floor Python 3.10 / SQLite 3.37). Detected at run time on the store connection with
TEMP objects only (no new sqlite3.connect: TST-CO-04 d), never assumed from the version string.

`probe(con)` -> {"fts5": bool, "trigram": bool, "sqlite": version}. A probe override (a callable with the same result) is the test hook for an
FTS-less runtime (AC-REV-16); it is never set by configuration.
"""
import sqlite3

FTS_TABLE, TRI_TABLE = "search_fts", "search_tri"


def _try(con, ddl, name):
    try:
        con.execute(ddl)
        con.execute("DROP TABLE temp.%s" % name)
        return True
    except sqlite3.Error:
        return False


def probe(con):
    fts5 = _try(con, "CREATE VIRTUAL TABLE temp.hub_fts_probe USING fts5(x)", "hub_fts_probe")
    tri = fts5 and _try(con, "CREATE VIRTUAL TABLE temp.hub_tri_probe USING fts5(x, tokenize='trigram')", "hub_tri_probe")
    return {"fts5": fts5, "trigram": tri, "sqlite": sqlite3.sqlite_version}


def index_present(con):
    names = set(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE name IN (?, ?)", (FTS_TABLE, TRI_TABLE)))
    return names == {FTS_TABLE, TRI_TABLE}


def create_index(con):
    """Inside the caller's transaction: (re)create both external-content FTS tables over search_doc.folded and fill them."""
    drop_index(con)
    con.execute("CREATE VIRTUAL TABLE search_fts USING fts5(folded, content='search_doc', content_rowid='rowid',"
                " tokenize='unicode61 remove_diacritics 0')")
    con.execute("CREATE VIRTUAL TABLE search_tri USING fts5(folded, content='search_doc', content_rowid='rowid', tokenize='trigram')")
    con.execute("INSERT INTO search_fts(search_fts) VALUES('rebuild')")
    con.execute("INSERT INTO search_tri(search_tri) VALUES('rebuild')")


def drop_index(con):
    con.execute("DROP TABLE IF EXISTS search_fts")
    con.execute("DROP TABLE IF EXISTS search_tri")


def select(con, settings, probe_fn=None):
    """-> (engine, reason, probe result). fts5 only when search.fts = auto AND FTS5 + trigram are available AND the derived index exists."""
    pr = (probe_fn or probe)(con)
    if settings["fts"] != "auto":
        return "fallback", "flag_off", pr
    if not (pr["fts5"] and pr["trigram"]):
        return "fallback", "fts5_unavailable", pr
    if not index_present(con):
        return "fallback", "fts_index_not_built", pr
    return "fts5", "auto", pr
