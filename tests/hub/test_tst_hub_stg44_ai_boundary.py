"""Stage 44 boundary tests (OD-40): the ONLY permitted model / network path is hub/adapters/azure_openai.py, and only when ai.enabled. Synthetic, unvalidated.

  B01  the endpoint rules (Azure host suffixes, https, loopback http only for the local fake, no user info / path / port) and the key handling of ProviderSettings
  B02  the egress guard: a non-loopback host is refused except the validated endpoint host inside the adapter's permit scope (addresses it resolved to only)
  B03  the client without the AI gate trips the No-AI tripwire and opens no socket; a gated call counts as an advisory call, not a tripwire
  B04  static: network client imports, record_model_call sites, AZURE_OPENAI_* reads, file writes and SQL writes are confined to the reviewed places
  B05  the deny-list (no-ai-check) is clean with the new adapter; the error codes are registered; hub.ai imports no HTTP layer
  B06  redirects are not followed and no proxy from the environment is used
"""
import ast
import json
import os
import socket
import unittest

import _stg44 as T
import _support as S
from hub.adapters import azure_openai
from hub.core import ai_errors as E
from hub.core.errors import EgressAttempt
from hub.guards import egress, no_ai
from hub.obs import metrics

HUB = os.path.join(S.CODE_ROOT, "hub")


def setUpModule():
    T.skip_in_inner_egress_run()


def _py(sub=""):
    for d, dirs, fns in os.walk(os.path.join(HUB, sub)):
        dirs[:] = [x for x in dirs if x != "__pycache__"]
        for fn in sorted(fns):
            if fn.endswith(".py"):
                p = os.path.join(d, fn)
                yield os.path.relpath(p, S.CODE_ROOT).replace(os.sep, "/"), p


def _tree(p):
    with open(p, encoding="utf-8") as f:
        return ast.parse(f.read(), p)


def _env(**kw):
    e = {"AZURE_OPENAI_ENDPOINT": "https://res-synthetic.openai.azure.com", "AZURE_OPENAI_DEPLOYMENT": "dep-1", "AZURE_OPENAI_API_VERSION": "2024-06-01",
         "AZURE_OPENAI_API_KEY": T.fake_key()}
    e.update(kw)
    return e


class TST_HUB_STG44_Boundary(unittest.TestCase):

    def test_TST_HUB_STG44_B01_endpoint_rules_and_key_handling(self):
        """B01: Azure host suffixes over https are accepted; loopback http is accepted (the local fake); everything else is E-AI-NOT-CONFIGURED naming the variable only. The key has no
        config fallback, is hidden in repr/str, and a key with whitespace or control characters is refused."""
        for ok in ("https://r1.openai.azure.com", "https://r1.openai.azure.com/", "https://R1.COGNITIVESERVICES.azure.com", "https://r1.services.ai.azure.com",
                   "http://127.0.0.1:8080", "http://localhost:9", "https://127.0.0.1:8443"):
            with self.subTest(ok=ok):
                ps = azure_openai.resolve(None, _env(AZURE_OPENAI_ENDPOINT=ok))
                self.assertTrue(ps.url().startswith(ps.endpoint + "/openai/deployments/dep-1/chat/completions?api-version=2024-06-01"))
        for bad in ("http://r1.openai.azure.com", "https://openai.azure.com", "https://r1.openai.azure.com.evil.io", "https://evil.io/r1.openai.azure.com",
                    "https://r1.openai.azure.com?x=1", "https://r1.openai.azure.com#f", "https://r1.openai.azure.com/x", "https://a@r1.openai.azure.com", "gopher://127.0.0.1",
                    "https://r1.openai.azure.com:444", "http://169.254.169.254", "https://[::ffff:8.8.8.8]", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(E.AiNotConfigured):
                    azure_openai.resolve(None, _env(AZURE_OPENAI_ENDPOINT=bad))
        for name, val in (("AZURE_OPENAI_DEPLOYMENT", "a b"), ("AZURE_OPENAI_DEPLOYMENT", "../x"), ("AZURE_OPENAI_API_VERSION", "latest"), ("AZURE_OPENAI_API_VERSION", "2024-06-01&x=1"),
                          ("AZURE_OPENAI_API_KEY", "has space"), ("AZURE_OPENAI_API_KEY", "line\nbreak"), ("AZURE_OPENAI_API_KEY", "x" * 600)):
            with self.subTest(name=name, val=val[:8]):
                with self.assertRaises(E.AiNotConfigured) as cm:
                    azure_openai.resolve(None, _env(**{name: val}))
                self.assertEqual(cm.exception.details, {"invalid": [name]})
        key = T.fake_key()
        ps = azure_openai.resolve(None, _env(AZURE_OPENAI_API_KEY=key))
        self.assertNotIn(key, repr(ps) + str(ps))
        self.assertEqual(ps.redact("a %s b" % key), "a [REDACTED] b")
        # the config placeholders may carry the three non-secret values, never the key
        fb = {"endpoint": "https://r2.openai.azure.com", "deployment": "dep-2", "api_version": "2024-02-01"}
        ps2 = azure_openai.resolve(fb, {"AZURE_OPENAI_API_KEY": key})
        self.assertEqual((ps2.host, ps2.deployment, ps2.api_version), ("r2.openai.azure.com", "dep-2", "2024-02-01"))
        with self.assertRaises(E.AiNotConfigured) as cm:
            azure_openai.resolve(dict(fb, api_key=key), {})
        self.assertEqual(cm.exception.details, {"missing": ["AZURE_OPENAI_API_KEY"]})

    def test_TST_HUB_STG44_B02_egress_guard_allows_only_the_permitted_host_inside_the_scope(self):
        """B02: with the egress guard installed, a name lookup / connect to a non-loopback host is refused (E-CO-EGRESS-ATTEMPT) outside the adapter's scope; inside `permit(host)` that
        ONE host may be resolved and the addresses it resolved to may be connected to; another host and another address stay refused; after the scope everything is refused again.
        (The resolver and connect are stubbed - no packet and no DNS query leaves the machine.)"""
        was = egress.installed()
        egress.install()
        saved = (egress._orig["getaddrinfo"], egress._orig["connect"])
        calls = []
        egress._orig["getaddrinfo"] = lambda host, *a, **k: calls.append(("resolve", host)) or [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("203.0.113.9", 443))]
        egress._orig["connect"] = lambda self_, addr: calls.append(("connect", addr))

        def restore():
            egress._orig["getaddrinfo"], egress._orig["connect"] = saved
            if not was:
                egress.uninstall()
        self.addCleanup(restore)
        before = metrics.value("egress_attempts_total")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addCleanup(s.close)
        with self.assertRaises(EgressAttempt):
            socket.getaddrinfo("res-synthetic.openai.azure.com", 443)
        with self.assertRaises(EgressAttempt):
            s.connect(("203.0.113.9", 443))
        with egress.permit("res-synthetic.openai.azure.com"):
            res = socket.getaddrinfo("res-synthetic.openai.azure.com", 443)
            self.assertEqual(res[0][4], ("203.0.113.9", 443))
            s.connect(("203.0.113.9", 443))
            with self.assertRaises(EgressAttempt):
                socket.getaddrinfo("other.openai.azure.com", 443)
            with self.assertRaises(EgressAttempt):
                s.connect(("198.51.100.7", 443))
        with self.assertRaises(EgressAttempt):
            socket.getaddrinfo("res-synthetic.openai.azure.com", 443)
        with self.assertRaises(EgressAttempt):
            s.connect(("203.0.113.9", 443))
        self.assertEqual(calls, [("resolve", "res-synthetic.openai.azure.com"), ("connect", ("203.0.113.9", 443))])
        self.assertEqual(metrics.value("egress_attempts_total") - before, 6)  # the six refusals above were deliberate ...
        metrics.inc("egress_attempts_total", before - metrics.value("egress_attempts_total"))  # ... put the tripwire back
        egress.reset()
        self.assertEqual(metrics.value("egress_attempts_total"), before)
        with self.assertRaises(ValueError):
            with egress.permit("https://x/y"):
                pass

    def test_TST_HUB_STG44_B03_client_without_the_gate_trips_the_tripwire_and_opens_no_socket(self):
        """B03: AzureOpenAIClient(enabled=False) -> E-AI-DISABLED, model_calls_total = 1 (the Stage 32 tripwire / gate G5) and ZERO requests at the fake; an enabled call increments
        ai_advisory_calls_total, NOT the tripwire."""
        with T.FakeAoai("ok") as f:
            ps = azure_openai.resolve(None, _env(AZURE_OPENAI_ENDPOINT=f.url))
            msgs = [{"role": "system", "content": "x"}, {"role": "user", "content": "y"}]
            base = metrics.value("model_calls_total")
            for flag in (False, None, 1, "yes"):
                with self.assertRaises(E.AiDisabled):
                    azure_openai.AzureOpenAIClient(ps, enabled=flag).complete(msgs, 50)
            self.assertEqual(f.requests, [])
            self.assertEqual(metrics.value("model_calls_total"), base + 4)
            metrics.inc("model_calls_total", -4)  # put the tripwire back
            adv = metrics.value("ai_advisory_calls_total")
            out = azure_openai.AzureOpenAIClient(ps, enabled=True).complete(msgs, 50)
            self.assertEqual((len(f.requests), out["usage"]["total"]), (1, 440))
            self.assertEqual((metrics.value("model_calls_total"), metrics.value("ai_advisory_calls_total")), (base, adv + 1))
            self.assertEqual(metrics.tripwires()["model_calls_total"], base)

    def test_TST_HUB_STG44_B04_static_confinement(self):
        """B04: (a) urllib.request / http.client are imported only by hub/adapters/gateway_client.py and hub/adapters/azure_openai.py; (b) record_model_call is called only in
        azure_openai.py; (c) AZURE_OPENAI_* names are read from the environment only there; (d) the adapter opens no file and imports no time / random / datetime / socket / ssl;
        (e) hub/ai opens no file for writing and runs no INSERT / UPDATE / DELETE / DDL except through hub.security.audit; (f) the adapter has no `.connect(` call (STG21 S06)."""
        clients, calls, envnames, nonconst_env = {}, [], {}, []
        for rel, p in _py():
            tree = _tree(p)
            for n in ast.walk(tree):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] + [n.module + "." + a.name for a in n.names] if isinstance(n, ast.ImportFrom) and n.module else [])
                for m in mods:
                    if m in ("urllib.request", "http.client", "requests", "httpx", "urllib3", "aiohttp"):
                        clients.setdefault(rel, set()).add(m)
                if isinstance(n, ast.Call):
                    f = n.func
                    nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
                    if nm == "record_model_call":
                        calls.append(rel)
                    if isinstance(f, ast.Attribute) and f.attr in ("get", "getenv", "pop") and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                        if n.args[0].value.startswith("AZURE_OPENAI_"):
                            envnames.setdefault(rel, set()).add(n.args[0].value)
                if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("AZURE_OPENAI_") and rel != "hub/adapters/azure_openai.py":
                    nonconst_env.append((rel, n.value))
        self.assertEqual(sorted(clients), ["hub/adapters/azure_openai.py", "hub/adapters/gateway_client.py"])
        self.assertEqual(clients["hub/adapters/azure_openai.py"], {"urllib.request"})
        self.assertEqual(sorted(set(calls)), ["hub/adapters/azure_openai.py"])
        self.assertEqual(envnames, {"hub/adapters/azure_openai.py": set(azure_openai.ENV_NAMES)})
        self.assertEqual(nonconst_env, [], "the variable names are written only in the adapter (others call azure_openai.env_report / resolve)")
        src = open(os.path.join(HUB, "adapters", "azure_openai.py"), encoding="utf-8").read()
        tree = _tree(os.path.join(HUB, "adapters", "azure_openai.py"))
        imported = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                imported |= set(a.name.split(".")[0] for a in n.names)
            elif isinstance(n, ast.ImportFrom) and n.module:
                imported.add(n.module.split(".")[0])
        self.assertFalse(imported & {"time", "random", "secrets", "datetime", "socket", "ssl", "subprocess", "logging", "pickle"}, imported)
        self.assertEqual([n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open"], [])
        self.assertEqual([n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "connect"], [])
        self.assertNotIn("print(", src)
        writes = []
        for rel, p in _py("ai"):
            for n in ast.walk(_tree(p)):
                if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "open":
                    mode = n.args[1] if len(n.args) > 1 else next((k.value for k in n.keywords if k.arg == "mode"), None)
                    if mode is not None and set(getattr(mode, "value", "w")) & set("wax+"):
                        writes.append((rel, "open for write"))
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executemany", "executescript") and n.args:
                    a0 = n.args[0]
                    if not (isinstance(a0, ast.Constant) and isinstance(a0.value, str) and a0.value.lstrip().upper().startswith("SELECT")):
                        writes.append((rel, "non-SELECT or non-literal SQL"))
        self.assertEqual(writes, [])

    def test_TST_HUB_STG44_B05_denylist_registry_and_layering(self):
        """B05: `no-ai-check` is clean (R1/R2/R3) with the new adapter; the 14 E-AI-* codes are in the committed error registry on exits 40 / 41 only; no module outside hub/web and
        hub/r2 imports hub.web (S22 rule) and hub.ai imports neither hub.web nor hub.r2; nothing outside hub/ai, the adapter, the CLI-free config and the flag register imports hub.ai."""
        self.assertEqual(no_ai.check(no_ai.default_targets(S.CODE_ROOT)), [])
        p = S.run_hub(["no-ai-check"])
        self.assertEqual(p.returncode, 0, p.stderr)
        reg = json.load(open(os.path.join(S.CODE_ROOT, "docs", "27-hardening", "error-registry", "error-code-registry.json"), encoding="utf-8"))
        ai = dict((r["code"], r["exit_code"]) for r in reg["codes"] if r["code"].startswith("E-AI-"))
        self.assertEqual(len(ai), 14)
        self.assertEqual(sorted(set(ai.values())), [40, 41])
        self.assertEqual(sorted(c for c, x in ai.items() if x == 41), ["E-AI-PROVIDER-BAD-RESPONSE", "E-AI-PROVIDER-RATE-LIMITED", "E-AI-PROVIDER-REJECTED",
                                                                        "E-AI-PROVIDER-TIMEOUT", "E-AI-PROVIDER-UNAVAILABLE"])
        users = []
        for rel, path in _py():
            for n in ast.walk(_tree(path)):
                mods = [a.name for a in n.names] if isinstance(n, ast.Import) else ([n.module] + [n.module + "." + a.name for a in n.names] if isinstance(n, ast.ImportFrom) and n.module else [])
                if rel.startswith("hub/ai/") and any(m == "hub.web" or m.startswith(("hub.web.", "hub.r2")) for m in mods):
                    users.append((rel, "web/r2"))
                if not rel.startswith("hub/ai/") and any(m == "hub.ai" or m.startswith("hub.ai.") for m in mods):
                    users.append(rel)
        self.assertEqual(users, [])

    def test_TST_HUB_STG44_B06_no_redirect_and_no_environment_proxy(self):
        """B06: HTTP(S)_PROXY from the environment is ignored (the opener holds no proxy handler; a dead proxy address in the environment does not matter) and the redirect handler
        refuses; a 302 from the endpoint is E-AI-PROVIDER-REJECTED and the Location target is never contacted."""
        op = azure_openai._opener()
        names = [type(h).__name__ for h in op.handlers]
        self.assertNotIn("ProxyHandler", names)
        self.assertIn("_NoRedirect", names)
        self.assertNotIn("HTTPRedirectHandler", names)
        with T.FakeAoai("ok") as f:
            ps = azure_openai.resolve(None, _env(AZURE_OPENAI_ENDPOINT=f.url))
            old = dict((k, os.environ.get(k)) for k in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"))
            for k in old:
                os.environ[k] = "http://127.0.0.1:9"  # nothing listens there
            try:
                out = azure_openai.AzureOpenAIClient(ps, enabled=True).complete([{"role": "user", "content": "x"}], 20)
            finally:
                for k, v in old.items():
                    if v is None:
                        os.environ.pop(k, None)
                    else:
                        os.environ[k] = v
            self.assertEqual((len(f.requests), out["usage"]["total"]), (1, 440))
        with T.FakeAoai("s302") as f, T.FakeAoai("ok") as target:
            ps = azure_openai.resolve(None, _env(AZURE_OPENAI_ENDPOINT=f.url))
            with self.assertRaises(E.AiProviderRejected):
                azure_openai.AzureOpenAIClient(ps, enabled=True).complete([{"role": "user", "content": "x"}], 20)
            self.assertEqual((len(f.requests), len(target.requests)), (1, 0))


if __name__ == "__main__":
    unittest.main()
