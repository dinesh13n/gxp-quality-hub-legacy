"""No-AI structural guard - dependency / import deny-list (ADR-002 option B(1), BEH-CO-07, AC-CO-11, OD-08).

Scans Python sources (AST, never imports them) and dependency manifests (pyproject.toml, requirements*.txt).
Fails with E-CO-DENYLIST-IMPORT on:
  R1  any import of a deny-listed AI/ML/LLM package (also importlib.import_module / __import__ string literals);
  R2  any HTTP/RPC client import outside an `adapters/` directory;
  R3  any deny-listed distribution declared in a dependency manifest.
The deny-list is heuristic (ADR-002 consequence; A-12-F10-2) and is maintained here; changing it is a reviewed PR.
AI coding assistants used to BUILD the product are dev tooling, out of scope (BR-AI-7).
"""
import ast
import os
import re

from hub.core.errors import DenylistImport

# R1 - AI / ML / LLM modules (top-level import names). Prefix families match any top-level name starting with the family name.
DENY_MODULES = (
    "openai", "anthropic", "transformers", "torch", "torchvision", "tensorflow", "keras", "jax", "flax",
    "langchain", "langchain_core", "langchain_community", "langgraph", "llama_index", "llama_cpp", "llama",
    "sklearn", "sentence_transformers", "cohere", "mistralai", "google.generativeai", "google.genai",
    "vertexai", "huggingface_hub", "tiktoken", "litellm", "ollama", "groq", "replicate", "together",
    "onnxruntime", "xgboost", "lightgbm", "spacy", "nltk", "gensim", "semantic_kernel", "autogen", "crewai",
    "dspy", "instructor", "guidance", "vllm", "accelerate", "peft", "diffusers", "chromadb", "faiss",
    "pinecone", "weaviate", "qdrant_client",
)
DENY_PREFIX_FAMILIES = ("openai", "anthropic", "langchain", "llama", "torch", "tensorflow", "transformers")
# R2 - network clients allowed only under an adapters/ directory
HTTP_CLIENT_MODULES = (
    "requests", "httpx", "urllib3", "aiohttp", "http.client", "urllib.request", "httplib2", "pycurl",
    "websocket", "websockets", "grpc", "boto3", "botocore", "xmlrpc.client", "ftplib", "smtplib", "telnetlib",
)
# R3 - distribution names (normalised: lower case, '-' and '.' -> '_')
DENY_DISTRIBUTIONS = tuple(sorted(set([m.replace(".", "_") for m in DENY_MODULES] + [
    "scikit_learn", "google_generativeai", "google_genai", "faiss_cpu", "faiss_gpu", "pinecone_client",
    "llama_cpp_python", "openai_agents", "anthropic_bedrock",
])))

SKIP_DIRS = {".git", "__pycache__", "data", "node_modules", ".venv", "venv"}


def _norm_dist(name):
    return re.sub(r"[-.]+", "_", name.strip().lower())


def _matches(module, names):
    for n in names:
        if module == n or module.startswith(n + "."):
            return n
    return None


def _deny_module(module):
    hit = _matches(module, DENY_MODULES)
    if hit:
        return hit
    top = module.split(".")[0]
    for fam in DENY_PREFIX_FAMILIES:
        if top.startswith(fam):  # e.g. torchaudio, langchain_openai, openai_agents (heuristic, ADR-002)
            return fam + "*"
    return None


def _in_adapters(path):
    parts = os.path.normpath(path).split(os.sep)
    return "adapters" in parts


def _imports(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield node.lineno, a.name
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            yield node.lineno, node.module
            for a in node.names:
                yield node.lineno, node.module + "." + a.name
        elif isinstance(node, ast.Call):
            fn = node.func
            fname = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else None)
            if fname in ("import_module", "__import__") and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                yield node.lineno, node.args[0].value


def scan_python(path):
    findings = []
    with open(path, "rb") as f:
        src = f.read()
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        return [{"path": path, "line": e.lineno or 0, "rule": "R0", "item": "unparseable source"}]
    seen = set()
    for line, module in _imports(tree):
        hit = _deny_module(module)
        if hit and (line, hit) not in seen:
            seen.add((line, hit))
            findings.append({"path": path, "line": line, "rule": "R1", "item": module})
            continue
        net = _matches(module, HTTP_CLIENT_MODULES)
        if net and not _in_adapters(path) and (line, net) not in seen:
            seen.add((line, net))
            findings.append({"path": path, "line": line, "rule": "R2", "item": module})
    return findings


_REQ_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def _dist_hit(name):
    n = _norm_dist(name)
    if n in DENY_DISTRIBUTIONS:
        return n
    for fam in DENY_PREFIX_FAMILIES:
        if n.startswith(fam):
            return n
    return None


def scan_manifest(path):
    findings = []
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    base = os.path.basename(path)
    if base == "pyproject.toml":
        # every quoted requirement string inside a *dependencies* array (crude, stdlib-only: no tomllib on 3.10)
        for m in re.finditer(r"(?ms)^\s*[\w.-]*dependencies\s*=\s*\[(.*?)\]", text):
            for q in re.finditer(r"[\"']([^\"']+)[\"']", m.group(1)):
                nm = _REQ_NAME.match(q.group(1))
                if nm and _dist_hit(nm.group(1)):
                    line = text.count("\n", 0, m.start(1) + q.start()) + 1
                    findings.append({"path": path, "line": line, "rule": "R3", "item": q.group(1)})
        for m in re.finditer(r"(?ms)^\[project\.optional-dependencies\](.*?)(^\[|\Z)", text):
            for q in re.finditer(r"[\"']([^\"']+)[\"']", m.group(1)):
                nm = _REQ_NAME.match(q.group(1))
                if nm and _dist_hit(nm.group(1)):
                    line = text.count("\n", 0, m.start(1) + q.start()) + 1
                    findings.append({"path": path, "line": line, "rule": "R3", "item": q.group(1)})
    else:
        for i, line in enumerate(text.splitlines(), 1):
            s = line.split("#", 1)[0].strip()
            if not s or s.startswith("-"):
                continue
            nm = _REQ_NAME.match(s)
            if nm and _dist_hit(nm.group(1)):
                findings.append({"path": path, "line": i, "rule": "R3", "item": s})
    return findings


def _is_manifest(name):
    return name == "pyproject.toml" or (name.startswith("requirements") and name.endswith(".txt"))


def scan(paths):
    findings = []
    for root in paths:
        if os.path.isfile(root):
            files = [root]
        else:
            files = []
            for d, dirs, fns in os.walk(root):
                dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS)
                for fn in sorted(fns):
                    files.append(os.path.join(d, fn))
        for p in files:
            name = os.path.basename(p)
            if name.endswith(".py"):
                findings.extend(scan_python(p))
            elif _is_manifest(name):
                findings.extend(scan_manifest(p))
    findings.sort(key=lambda x: (x["path"], x["line"], x["rule"], x["item"]))
    return findings


def default_targets(repo_root):
    """New product code and its tests, plus the project dependency manifests. The legacy estate is out of
    scope (it is not hub product code; e.g. app/gateway_bridge.py uses urllib.request as the legacy gateway
    client) - recorded in docs/15-modernization/remaining-technical-debt.md."""
    out = [os.path.join(repo_root, "hub"), os.path.join(repo_root, "tests", "hub")]
    for fn in sorted(os.listdir(repo_root)):
        if _is_manifest(fn):
            out.append(os.path.join(repo_root, fn))
    return [p for p in out if os.path.exists(p)]


def check(paths):
    findings = scan(paths)
    if findings:
        raise DenylistImport(findings)
    return findings
