"""Joined read-only view of a connected set (OP-ID-04, BEH-ID-06, FR-ID-04, AC-ID-13/14/17; INC-09).

Breadth-first over ACTIVE crosswalk links (retracted links are not followed), depth cap 4, size cap 500 (config `crosswalk_view.depth_cap` /
`size_cap`). Entering with any member id returns the same set (the connected component within the depth cap). Order: (type, id). Fields are
filtered first (hub.r2.protection, F09): a document the caller may not read appears as {type: document, access: denied}, carries no id, and is not
counted in `total`; links touching it are not shown. When the permitted set holds C3 (restricted) documents a non-empty reason is required and the
read is audited (BEH-SEC-10). When the permitted set is larger than the size cap: `truncated = true`, `total` = the full permitted count, the first
`size_cap` entities in (type, id) order are returned - never a silent cut. Read-only: the only write is the C3_READ audit record.
"""
from hub.core.errors import ConfigInvalid
from hub.crosswalk.service import CrosswalkService
from hub.r2 import protection

DEFAULTS = {"depth_cap": 4, "size_cap": 500}


def settings(cfg):
    s = dict(DEFAULTS)
    s.update((cfg or {}).get("crosswalk_view") or {})
    for k in DEFAULTS:
        if isinstance(s[k], bool) or not isinstance(s[k], int) or s[k] < 1:
            raise ConfigInvalid({"crosswalk_view." + k: "positive integer"})
    return s


def _active_links(con, t, i):
    q = ("SELECT l.link_id, l.from_type, l.from_id, l.to_type, l.to_id, l.key_used, l.creator_kind FROM crosswalk_link l"
         " WHERE ((l.from_type = ? AND l.from_id = ?) OR (l.to_type = ? AND l.to_id = ?)) AND NOT EXISTS"
         " (SELECT 1 FROM crosswalk_link_event e WHERE e.link_id = l.link_id AND e.event_type = 'LINK_RETRACTED') ORDER BY l.link_id")
    return con.execute(q, (t, i, t, i)).fetchall()


def component(con, start, depth_cap):
    """-> (entities set {(type, id)}, links {link_id: row}, depth_capped bool)."""
    seen, frontier, links, capped = {start}, [start], {}, False
    for depth in range(depth_cap + 1):
        nxt = []
        for t, i in frontier:
            for row in _active_links(con, t, i):
                other = (row[3], row[4]) if (row[1], row[2]) == (t, i) else (row[1], row[2])
                if depth == depth_cap:
                    if other not in seen:
                        capped = True
                    continue
                links[row[0]] = row
                if other not in seen:
                    seen.add(other)
                    nxt.append(other)
        frontier = sorted(nxt)
        if not frontier:
            break
    return seen, links, capped


def _doc_level(con, doc_id):
    try:
        r = con.execute("SELECT access_level FROM search_doc WHERE doc_id = ? ORDER BY version DESC LIMIT 1", (doc_id,)).fetchone()
    except Exception:  # noqa: BLE001 - M007 absent: the level is unknown -> restricted (MA-1)
        r = None
    return r[0] if r else None


def view(con, s, clock, anchor, sess, id_value, id_type=None, cfg=None, reason=None, facts=None, correlation_id="joined-view"):
    st = settings(cfg)
    cw = CrosswalkService(con, s, clock, anchor)
    head = cw.lookup(sess, id_value, id_type, correlation_id)  # role check (audited), id pattern and ambiguity rules of OP-ID-01
    roles = sess.principal.roles
    members, links, capped = component(con, (head["id_type"], head["id"]), st["depth_cap"])
    visible, denied, c3 = [], 0, 0
    hidden = set()
    for t, i in sorted(members):
        if t == "document":
            level = _doc_level(con, i)
            pr = protection.project("document", {"doc_id": i, "access_level": level}, roles)
            if pr.get("access") == "denied":
                denied += 1
                hidden.add((t, i))
                continue
            if pr["access_level"] == "restricted":
                c3 += 1
            visible.append({"type": t, "id": i, "access": "granted", "access_level": pr["access_level"], "field_class": pr["field_class"]})
        else:
            e = {"type": t, "id": i, "access": "granted"}
            if facts is not None:
                rec = facts(t, i)
                if rec:
                    e["fields"] = protection.project(t, rec, roles)
            visible.append(e)
    if c3:
        why = protection.require_reason(reason, "OP-ID-04", c3)
        protection.audit_c3_read(con, clock, anchor, sess.principal, why, "OP-ID-04", {"c3_rows": c3, "entry": "%s:%s" % (head["id_type"], head["id"])},
                                 correlation_id)
    total = len(visible)
    shown = visible[:st["size_cap"]]
    ents = shown + [{"type": "document", "access": "denied"}] * denied
    link_rows = [{"link_id": r[0], "from_type": r[1], "from_id": r[2], "to_type": r[3], "to_id": r[4], "key_used": r[5], "creator_kind": r[6]}
                 for _, r in sorted(links.items()) if (r[1], r[2]) not in hidden and (r[3], r[4]) not in hidden]
    return {"entry": {"type": head["id_type"], "id": head["id"]}, "entities": ents, "links": link_rows, "truncated": total > len(shown),
            "total": total, "depth_cap": st["depth_cap"], "depth_capped": capped, "size_cap": st["size_cap"], "read_only": True,
            "label": "synthetic, unvalidated"}
