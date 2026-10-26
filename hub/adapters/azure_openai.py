"""The ONE network client of the optional advisory document Q&A (Stage 44, OD-40): Azure OpenAI chat-completions REST over the standard library.

Everything about the model connection lives here and nowhere else:

  environment   AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_DEPLOYMENT / AZURE_OPENAI_API_VERSION / AZURE_OPENAI_API_KEY. The API KEY is read ONLY from
                the environment (never from a config or repository file, never logged, never put in an audit record, never in an error detail).
                The three non-secret values may also come from the shipped config placeholders (`ai.azure_openai.*`, empty by default); the
                environment wins.
  endpoint      https://<resource>.openai.azure.com (or .cognitiveservices.azure.com / .services.ai.azure.com). http:// is accepted ONLY for a
                loopback host (the local fake used by the tests). No user info, no query, no fragment, no path; no redirects are followed;
                no proxy from the environment is used.
  call          POST {endpoint}/openai/deployments/{deployment}/chat/completions?api-version={api_version}, header `api-key`, JSON body, ONE
                attempt (no retry, no sleep: the caller decides), a hard timeout and a response size cap.
  guards        the client works only when it was constructed with enabled=True by hub.ai.gate (ai.enabled). A call without it records the
                No-AI tripwire (metrics.record_model_call -> model_calls_total, release gate G5) and raises E-AI-DISABLED BEFORE any socket is
                opened. A permitted call increments `ai_advisory_calls_total` (not a tripwire). The egress guard (hub.guards.egress) refuses every
                non-loopback host except the validated endpoint host, and only inside this module's `permit` scope.

This is the only module under hub/ that may call `record_model_call` (TST-CO-12 d) and the only one that reads AZURE_OPENAI_* (STG28 A02).
No `time`, `random` or `datetime` import (adapters are core, TST-CO-13 b). Synthetic data only; no real endpoint, key or call is made by the shipped tests.
"""
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from hub.core.ai_errors import (AiDisabled, AiNotConfigured, AiProviderBadResponse, AiProviderRateLimited, AiProviderRejected,
                                AiProviderTimeout, AiProviderUnavailable)
from hub.guards import egress

ENV_NAMES = ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_API_KEY")
HOST_SUFFIXES = (".openai.azure.com", ".cognitiveservices.azure.com", ".services.ai.azure.com")
LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_REQUEST_BYTES = 256 * 1024
_DEPLOYMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_VERSION = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}(-preview)?$")
_TOKEN_PARAMS = ("max_tokens", "max_completion_tokens")


class ProviderSettings(object):
    """endpoint / deployment / api_version are plain values; the key is held privately and never appears in repr(), str(), vars() output or errors."""
    __slots__ = ("endpoint", "deployment", "api_version", "_key", "host", "loopback")

    def __init__(self, endpoint, deployment, api_version, key, host, loopback):
        self.endpoint, self.deployment, self.api_version, self._key, self.host, self.loopback = endpoint, deployment, api_version, key, host, loopback

    def __repr__(self):
        return "ProviderSettings(host=%r, deployment=%r, api_version=%r, key=<set, hidden>)" % (self.host, self.deployment, self.api_version)

    __str__ = __repr__

    def url(self):
        return "%s/openai/deployments/%s/chat/completions?api-version=%s" % (self.endpoint, self.deployment, self.api_version)

    def redact(self, text):
        """Replace the API key (and its URL-quoted form) in `text` by a marker - applied to everything that came from the provider."""
        text = text if isinstance(text, str) else str(text)
        if self._key:
            for k in (self._key, urllib.parse.quote(self._key, safe="")):
                if k:
                    text = text.replace(k, "[REDACTED]")
        return text

    def _headers(self):
        return {"api-key": self._key, "Content-Type": "application/json", "Accept": "application/json", "User-Agent": "gxp-quality-hub-advisory-qa/0.1"}


def env_report(environ=None):
    """{name: bool} - which of the four variables are set and non-empty. Values are never returned."""
    env = os.environ if environ is None else environ
    return dict((n, bool((env.get(n) or "").strip())) for n in ENV_NAMES)


def _clean_endpoint(raw):
    """-> (endpoint without trailing slash, host, is_loopback) or raises AiNotConfigured naming WHAT is wrong (never the value)."""
    try:
        u = urllib.parse.urlsplit(raw.strip())
        host = (u.hostname or "").lower()
        port = u.port
    except ValueError:
        raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "not a valid URL"})
    loop = host in LOOPBACK_HOSTS
    if u.username or u.password or u.query or u.fragment or u.path not in ("", "/"):
        raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "must be a bare origin: no user info, path, query or fragment"})
    if loop:
        if u.scheme not in ("http", "https"):
            raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "scheme must be http or https"})
    else:
        if u.scheme != "https":
            raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "https is required for a non-loopback host"})
        if port not in (None, 443):
            raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "port must be the default 443"})
        if not any(host.endswith(s) and len(host) > len(s) for s in HOST_SUFFIXES):
            raise AiNotConfigured({"AZURE_OPENAI_ENDPOINT": "host must end with one of %s" % list(HOST_SUFFIXES)})
    netloc = host if port is None else "%s:%d" % (host, port)
    if ":" in host:
        netloc = "[%s]%s" % (host, "" if port is None else ":%d" % port)
    return "%s://%s" % (u.scheme, netloc), host, loop


def resolve(fallback=None, environ=None):
    """Build the validated ProviderSettings. Environment first; the three non-secret values may fall back to `fallback` (the config placeholders).
    The key has NO fallback. Raises AiNotConfigured listing only the NAMES of what is missing or invalid."""
    env = os.environ if environ is None else environ
    fb = fallback or {}
    endpoint = (env.get("AZURE_OPENAI_ENDPOINT") or fb.get("endpoint") or "").strip()
    deployment = (env.get("AZURE_OPENAI_DEPLOYMENT") or fb.get("deployment") or "").strip()
    version = (env.get("AZURE_OPENAI_API_VERSION") or fb.get("api_version") or "").strip()
    key = env.get("AZURE_OPENAI_API_KEY") or ""
    missing = [n for n, v in (("AZURE_OPENAI_ENDPOINT", endpoint), ("AZURE_OPENAI_DEPLOYMENT", deployment),
                              ("AZURE_OPENAI_API_VERSION", version), ("AZURE_OPENAI_API_KEY", key.strip())) if not v]
    if missing:
        raise AiNotConfigured({"missing": missing})
    bad = []
    if not _DEPLOYMENT.match(deployment):
        bad.append("AZURE_OPENAI_DEPLOYMENT")
    if not _VERSION.match(version):
        bad.append("AZURE_OPENAI_API_VERSION")
    if len(key) > 512 or not key.isprintable() or any(c.isspace() for c in key):
        bad.append("AZURE_OPENAI_API_KEY")
    if bad:
        raise AiNotConfigured({"invalid": bad})
    clean, host, loop = _clean_endpoint(endpoint)
    return ProviderSettings(clean, deployment, version, key, host, loop)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())


def _retry_after(headers):
    try:
        v = int(str(headers.get("Retry-After", "")).strip())
        return v if 0 <= v <= 3600 else None
    except (ValueError, AttributeError):
        return None


class AzureOpenAIClient(object):
    """One chat-completions call. `enabled` must be the True produced by hub.ai.gate; anything else trips the No-AI tripwire and refuses."""

    def __init__(self, settings, enabled=False, timeout=20, token_param="max_tokens"):
        if token_param not in _TOKEN_PARAMS:
            raise AiNotConfigured({"token_param": "one of %s" % list(_TOKEN_PARAMS)})
        self.settings, self.enabled, self.timeout, self.token_param = settings, enabled, timeout, token_param

    def complete(self, messages, max_output_tokens):
        """-> {text, finish_reason, model, request_id, usage: {prompt, completion, total}}. Raises HubError subclasses (E-AI-*) only."""
        if self.enabled is not True:
            from hub.obs import metrics   # function-level: avoids the adapters -> obs -> resilience -> adapters 3-cycle (S27 ratchet, same precedent as gateway_client)
            metrics.record_model_call("azure_openai")  # the Stage 32 tripwire: a model path was reached without the AI gate
            raise AiDisabled({"where": "azure_openai.complete"})
        st = self.settings
        body = json.dumps({"messages": messages, self.token_param: int(max_output_tokens), "temperature": 0, "n": 1, "stream": False},
                          ensure_ascii=False).encode("utf-8")
        if len(body) > MAX_REQUEST_BYTES:
            raise AiProviderRejected({"reason": "request over %d bytes" % MAX_REQUEST_BYTES})
        req = urllib.request.Request(st.url(), data=body, headers=st._headers(), method="POST")
        from hub.obs import metrics   # function-level, see above
        metrics.inc("ai_advisory_calls_total")
        try:
            with egress.permit(st.host):
                with _opener().open(req, timeout=self.timeout) as resp:
                    raw = resp.read(MAX_RESPONSE_BYTES + 1)
                    status, rid = resp.status, resp.headers.get("apim-request-id") or resp.headers.get("x-request-id")
        except urllib.error.HTTPError as e:
            raise self._http_error(e)
        except TimeoutError:  # socket.timeout is an alias of TimeoutError since Python 3.10 (the runtime floor)
            raise AiProviderTimeout({"timeout_seconds": self.timeout})
        except urllib.error.URLError as e:
            if isinstance(getattr(e, "reason", None), TimeoutError):
                raise AiProviderTimeout({"timeout_seconds": self.timeout})
            raise AiProviderUnavailable({"reason": st.redact(type(getattr(e, "reason", e)).__name__)})
        except (OSError, ValueError) as e:
            raise AiProviderUnavailable({"reason": st.redact(type(e).__name__)})
        return self._parse(raw, status, rid)

    def _http_error(self, e):
        st, code = self.settings, e.code
        detail = {"http_status": code}
        try:
            doc = json.loads(e.read(4096).decode("utf-8", "replace"))
            err = doc.get("error") if isinstance(doc, dict) else None
            if isinstance(err, dict):
                if isinstance(err.get("code"), str):
                    detail["provider_code"] = st.redact(err["code"])[:60]
                if isinstance(err.get("message"), str):
                    detail["provider_message"] = st.redact(err["message"])[:200]
        except (ValueError, OSError, AttributeError):
            pass
        if code == 429:
            ra = _retry_after(e.headers)
            if ra is not None:
                detail["retry_after_seconds"] = ra
            return AiProviderRateLimited(detail)
        if code >= 500:
            return AiProviderUnavailable(detail)
        return AiProviderRejected(detail)

    def _parse(self, raw, status, request_id):
        st = self.settings
        if len(raw) > MAX_RESPONSE_BYTES:
            raise AiProviderBadResponse({"reason": "response over %d bytes" % MAX_RESPONSE_BYTES})
        try:
            doc = json.loads(raw.decode("utf-8"))
            choice = doc["choices"][0]
            text = choice["message"]["content"]
            if status != 200 or not isinstance(text, str):
                raise ValueError("shape")
            use = doc.get("usage") or {}
            usage = {"prompt": int(use.get("prompt_tokens", 0)), "completion": int(use.get("completion_tokens", 0)),
                     "total": int(use.get("total_tokens", int(use.get("prompt_tokens", 0)) + int(use.get("completion_tokens", 0))))}
            return {"text": st.redact(text), "finish_reason": str(choice.get("finish_reason"))[:30], "model": st.redact(str(doc.get("model", "")))[:80],
                    "request_id": st.redact(str(request_id or ""))[:80], "usage": usage}
        except (ValueError, KeyError, IndexError, TypeError, AttributeError, UnicodeDecodeError):
            raise AiProviderBadResponse({"reason": "unexpected response shape"})
