"""Route table for the loopback HTTP surface (deny by default, BEH-SEC-01/04; INC-08).

Two registries feed one matcher: hub/security/route_registry.json (the 48 OpenAPI operations, generated from x-roles, frozen by TST-SEC-01) and
hub/web/ui_routes.json (server-rendered pages). A request whose method + path matches no template is refused 403 E-AUTH-FORBIDDEN (audited). Path
templates use {name} segments, matched on whole segments only (no wildcard, no prefix match).
"""
import json
import os
import re
import urllib.parse as _up

from hub.security import authz

UI_REGISTRY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui_routes.json")
_SEG = re.compile(r"^[A-Za-z0-9._:@#=-]{1,200}$")


def load_ui_registry(path=UI_REGISTRY_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["routes"]


def _compile(template):
    parts = []
    for seg in template.strip("/").split("/"):
        parts.append("([^/]+)" if seg.startswith("{") and seg.endswith("}") else re.escape(seg))
    return re.compile("^/" + "/".join(parts) + ("/" if template.endswith("/") and template != "/" else "") + "$"), \
        [seg[1:-1] for seg in template.strip("/").split("/") if seg.startswith("{")]


class Table(object):
    def __init__(self, api=None, ui=None):
        self.api = list(api if api is not None else authz.load_registry())
        self.ui = list(ui if ui is not None else load_ui_registry())
        self.compiled = []
        for kind, rows in (("api", self.api), ("ui", self.ui)):
            for r in rows:
                rx, names = _compile(r["path"])
                self.compiled.append((r["method"].upper(), rx, names, r, kind))

    def match(self, method, path):
        """-> (route entry, kind, params) or (None, None, None). A path that exists under another method is still 'not registered' for this one."""
        for m, rx, names, r, kind in self.compiled:
            if m != method.upper():
                continue
            hit = rx.match(path)
            if hit:
                params = {}
                for n, v in zip(names, hit.groups()):
                    v = _up.unquote(v)
                    if not _SEG.match(v):
                        return None, None, None
                    params[n] = v
                return r, kind, params
        return None, None, None

    def path_known(self, path):
        return any(rx.match(path) for _, rx, _, _, _ in self.compiled)
