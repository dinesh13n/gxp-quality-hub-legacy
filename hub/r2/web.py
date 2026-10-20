"""R2WebApp: the INC-08 WebApp (frozen) plus the INC-09 / R2 handlers (additive subclass; the 48-operation route registry and its roles are
unchanged, TST-SEC-01). Differences from WebApp:
  * `self.api` is hub.r2.api (R2 handlers; everything else delegates to hub.web.api);
  * `self.search` is hub.search.engine.R2SearchService (FTS5 behind `search.fts`, fallback otherwise; `search.enabled` still gates OP-REV-03);
  * injected read-only providers: `case_inputs` (divergence inputs, e.g. the legacy snapshot cases) and `facts(type, id)` (joined view fields);
  * start() additionally requires M007 and logs the selected search engine (fts_engine_selected, object_ref `search-engine:<engine>:<reason>`).
"""
from hub.r2 import api as r2api
from hub.search import schema as search_schema
from hub.search.engine import R2SearchService
from hub.web.app import WebApp


class R2WebApp(WebApp):
    def __init__(self, data_dir, cfg, clock, case_inputs=None, facts=None, probe_fn=None, **kw):
        WebApp.__init__(self, data_dir, cfg, clock, **kw)
        self.case_inputs, self.facts = case_inputs, facts
        self.search = R2SearchService(cfg, probe_fn, clock, self.anchor)
        self.api = r2api

    def engine(self):
        con = self._connect()
        try:
            search_schema.require(con)
            eng, why, pr = self.search.engine_for(con)
        finally:
            con.close()
        return {"engine": eng, "reason": why, "fts5": pr["fts5"], "trigram": pr["trigram"], "sqlite": pr["sqlite"]}

    def start(self, correlation_id="web-start"):
        rep = WebApp.start(self, correlation_id)
        e = self.engine()
        self.log.emit("fts_engine_selected", "INFO", correlation_id, op_id="OP-REV-03", outcome="success",
                      object_ref="search-engine:%s:%s" % (e["engine"], e["reason"]))
        rep = dict(rep)
        rep["search_engine"] = e
        return rep
