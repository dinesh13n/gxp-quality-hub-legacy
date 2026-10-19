"""Metric registry (BEH-MET-01, AC-MET-01, AC-MET-15, AC-MET-16; INC-07): every metric is declared in `metric_definition` (insert-only, versioned).

A metric whose category is time / age, or whose name, window, denominator or documentation mentions closed / resolved / approved / cost / handling,
cannot be registered without a definition tag (E-MET-TAG-REQUIRED). A source of `operating_costs` is never accepted as 'cases created'
(E-MET-SOURCE-REFUSED, OD-07) and forces basis = modelled. `documentation_pages` generates one page per KPI and fails when a window, denominator,
exclusions text or (where required) tag is missing (AC-MET-15).
"""
import re

from hub.metrics.errors import MetDefinitionRequired, MetSourceRefused, MetTagRequired, MetUnknownMetric

CATEGORIES = ("time", "count", "money", "rate", "age")
BASES = ("event_derived", "modelled")
_CONCEPTS = re.compile(r"(?i)\b(closed|closure|close|resolved|resolution|approved|approval|cost|handling)\b")
_REQ = ("metric_id", "name", "category", "window", "denominator", "exclusions", "basis", "documentation")
_COLS = ("metric_id", "version", "name", "category", "definition_tag", "involves_definition", "window", "denominator", "exclusions",
         "cutoff_ref", "basis", "documentation")

BUILTIN = (
    {"metric_id": "MET-TTC-C-OPS", "name": "Time to ops-closed (clock C-OPS)", "category": "time", "definition_tag": "C-OPS",
     "window": "all completed cycles recorded", "denominator": "completed cycles (a start and a stop event of the clock exist in the cycle)",
     "exclusions": "incomplete cycles (counted as open_count); never pooled with another clock", "basis": "event_derived",
     "documentation": "Median and p90 of the elapsed hours between the clock's start and stop events per completed cycle (decision_events); "
                      "method: median = mean of the two middle values, p90 = nearest rank. n = 0 gives null, never 0."},
    {"metric_id": "MET-TTC-C-EVID", "name": "Time to evidence-complete (clock C-EVID)", "category": "time", "definition_tag": "C-EVID",
     "window": "all completed cycles recorded", "denominator": "completed cycles (a start and a stop event of the clock exist in the cycle)",
     "exclusions": "incomplete cycles (counted as open_count); never pooled with another clock", "basis": "event_derived",
     "documentation": "Same method as MET-TTC-C-OPS under the evidence-complete clock; a different definition, never combined with it."},
    {"metric_id": "MET-MONTH-END-TOTAL", "name": "Month-end total of case amounts", "category": "money", "definition_tag": None,
     "window": "cases created up to the explicit cut-off", "denominator": "all rows of cases.amount at the cut-off (one row per case)",
     "exclusions": "none; unparsable amounts raise unless allow_partial", "cutoff_ref": "CUTOFF policy (explicit parameter, no default)",
     "basis": "event_derived",
     "documentation": "Exact decimal sum of cases.amount read with one query on one table (no join, no fan-out); quantised to 2 decimals "
                      "ROUND_HALF_EVEN at presentation. Reference on the shipped baseline: 622826.44 for 125 cases."},
    {"metric_id": "MET-BACKLOG-D-OPS", "name": "Backlog and ageing per site (D-OPS)", "category": "count", "definition_tag": "D-OPS",
     "window": "state at the as_of instant", "denominator": "cases existing at as_of",
     "exclusions": "cases whose state is in the closing-state set; cases created after as_of",
     "basis": "event_derived",
     "documentation": "Cases not in the closing-state set at as_of, per site, with ageing buckets <=90, 91-365, 366-730, >730 days from creation; "
                      "one declared definition per table."},
    {"metric_id": "MET-UNRESOLVED-EXC-RATE-D-OPS", "name": "Unresolved-exception rate per site (D-OPS)", "category": "rate", "definition_tag": "D-OPS",
     "window": "exception-queue history up to the computation instant", "denominator": "all items that ever sat in an exception queue",
     "exclusions": "items that never entered an exception queue; unmatched items are reported under site 'unknown'", "basis": "event_derived",
     "documentation": "Open exception-queue items / all exception-queue items, per site of the matched case (A-12-F07-2: formula is a spec choice)."},
)
# KPIs that cannot have a value without explicit parameters (reported by kpi-coverage with this reason)
NEEDS_PARAMS = {"MET-MONTH-END-TOTAL": "cutoff_ts and denominator_ref are required parameters and no cut-off is adopted (E-MET-CUTOFF-REQUIRED, OD-S12-08)"}


def _row(r):
    d = dict(zip(_COLS, r))
    d["involves_definition"] = bool(d["involves_definition"])
    return d


class Registry(object):
    def __init__(self, con, clock=None):
        self.con, self.clock = con, clock

    def involves_definition(self, d):
        text = " ".join(str(d.get(k) or "") for k in ("name", "window", "denominator", "documentation"))
        return bool(d.get("involves_definition")) or d.get("category") in ("time", "age") or bool(_CONCEPTS.search(text))

    def register(self, d):
        """Insert a new version of a metric definition; returns its version. Own transaction."""
        miss = [k for k in _REQ if not (isinstance(d.get(k), str) and d[k].strip())]
        if miss:
            raise MetDefinitionRequired({"missing": miss})
        if d["category"] not in CATEGORIES or d["basis"] not in BASES:
            raise MetDefinitionRequired({"category": d["category"], "basis": d["basis"]})
        src = d.get("source")
        if isinstance(src, str) and src.startswith("operating_costs"):
            if d.get("source_meaning") in ("cases_created", "cases"):
                raise MetSourceRefused({"source": src, "reason": "operating_costs.total_cases is random, not 'cases created' (OD-07)"})
            if d["basis"] != "modelled":
                raise MetSourceRefused({"source": src, "reason": "any metric using operating_costs has basis = modelled"})
        involves = self.involves_definition(d)
        tag = d.get("definition_tag")
        if involves and not (isinstance(tag, str) and tag.strip()):
            raise MetTagRequired({"metric_id": d["metric_id"], "category": d["category"]})
        self.con.execute("BEGIN IMMEDIATE")
        try:
            v = self.con.execute("SELECT COALESCE(MAX(version), 0) + 1 FROM metric_definition WHERE metric_id = ?", (d["metric_id"],)).fetchone()[0]
            self.con.execute("INSERT INTO metric_definition(metric_id, version, name, category, definition_tag, involves_definition, \"window\","
                             " denominator, exclusions, cutoff_ref, basis, documentation) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                             (d["metric_id"], v, d["name"], d["category"], tag if involves else (tag or None), 1 if involves else 0, d["window"],
                              d["denominator"], d["exclusions"], d.get("cutoff_ref"), d["basis"], d["documentation"]))
            self.con.commit()
        except BaseException:
            self.con.rollback()
            raise
        return v

    def seed_builtin(self):
        """Idempotent: registers the R1 KPIs that are not registered yet. Returns the metric ids registered now."""
        done = []
        for d in BUILTIN:
            if self.con.execute("SELECT 1 FROM metric_definition WHERE metric_id = ?", (d["metric_id"],)).fetchone() is None:
                self.register(d)
                done.append(d["metric_id"])
        return done

    def list(self, latest_only=True):
        q = ("SELECT " + ", ".join('"window"' if c == "window" else c for c in _COLS) + " FROM metric_definition" +
             (" WHERE version = (SELECT MAX(version) FROM metric_definition x WHERE x.metric_id = metric_definition.metric_id)" if latest_only else "") +
             " ORDER BY metric_id, version")
        return [_row(r) for r in self.con.execute(q)]

    def get(self, metric_id, version=None):
        q = "SELECT " + ", ".join('"window"' if c == "window" else c for c in _COLS) + " FROM metric_definition WHERE metric_id = ?"
        row = (self.con.execute(q + " AND version = ?", (metric_id, version)) if version else
               self.con.execute(q + " ORDER BY version DESC LIMIT 1", (metric_id,))).fetchone()
        if row is None:
            raise MetUnknownMetric({"metric_id": str(metric_id)[:60]})
        return _row(row)

    def documentation_pages(self):
        """One page per KPI (AC-MET-15). A KPI without window, denominator, exclusions or (when it involves a definition) tag fails the build."""
        pages, bad = [], []
        for d in self.list():
            gaps = [k for k in ("window", "denominator", "exclusions") if not (d.get(k) or "").strip()]
            if d["involves_definition"] and not (d.get("definition_tag") or "").strip():
                gaps.append("definition_tag")
            if gaps:
                bad.append({"metric_id": d["metric_id"], "missing": gaps})
                continue
            pages.append({"metric_id": d["metric_id"], "version": d["version"], "title": d["name"], "definition_tag": d["definition_tag"],
                          "window": d["window"], "denominator": d["denominator"], "exclusions": d["exclusions"], "basis": d["basis"],
                          "cutoff_ref": d["cutoff_ref"], "code_reference": "hub/metrics/service.py", "text": d["documentation"]})
        if bad:
            raise MetDefinitionRequired({"incomplete": bad})
        return pages
