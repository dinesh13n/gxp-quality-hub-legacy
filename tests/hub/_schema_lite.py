"""A small stdlib JSON Schema (draft-07 SUBSET) validator for the Stage 12 contract schemas (Stage 23 DW-16). Synthetic, unvalidated.

The product is stdlib-only (OD-08, no new third-party dependency), so the contract test cannot use `jsonschema`. Supported keywords are exactly the ones the
16 schemas (and the Stage 12 v0.2 addendum schemas) use: type, enum, const, pattern, minLength, maxLength, minimum, maximum, exclusiveMinimum, properties,
required, additionalProperties, items, minItems, uniqueItems, allOf, anyOf, not, if / then / else, plus annotation keywords. `unsupported(schema)` lists any other
keyword so a schema change that needs more cannot pass silently. Cross-checked against `jsonschema` 3.2.0 (evaluation tooling only) in
docs/23-human-control/evidence/s23_schema_crosscheck.py.
"""
import json
import re

ANNOTATIONS = {"$schema", "$id", "title", "description", "documentation", "examples", "default", "$comment"}
KEYWORDS = {"type", "enum", "const", "pattern", "minLength", "maxLength", "minimum", "maximum", "exclusiveMinimum", "properties", "required",
            "additionalProperties", "items", "minItems", "uniqueItems", "allOf", "anyOf", "not", "if", "then", "else"}


def unsupported(schema, path=""):
    out = []
    if isinstance(schema, dict):
        for k, v in schema.items():
            if k in ("properties",):
                for pk, pv in v.items():
                    out += unsupported(pv, path + "/properties/" + pk)
            elif k in ANNOTATIONS:
                continue
            elif k in KEYWORDS:
                if k in ("items", "additionalProperties", "not", "if", "then", "else") and isinstance(v, dict):
                    out += unsupported(v, path + "/" + k)
                elif k in ("allOf", "anyOf"):
                    for i, sub in enumerate(v):
                        out += unsupported(sub, "%s/%s/%d" % (path, k, i))
            else:
                out.append("%s/%s" % (path, k))
    return out


def _canon(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def _type_ok(t, v):
    if t == "string":
        return isinstance(v, str)
    if t == "integer":
        return isinstance(v, int) and not isinstance(v, bool)
    if t == "number":
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    if t == "boolean":
        return isinstance(v, bool)
    if t == "null":
        return v is None
    if t == "object":
        return isinstance(v, dict)
    if t == "array":
        return isinstance(v, list)
    raise ValueError("unknown type " + str(t))


def errors(schema, inst, path="$"):
    """List of 'path: message' strings (empty = valid)."""
    if schema is True or schema == {}:
        return []
    if schema is False:
        return ["%s: nothing is allowed here" % path]
    out = []
    if "type" in schema:
        ts = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(t, inst) for t in ts):
            return ["%s: type %s expected, got %s" % (path, "|".join(ts), type(inst).__name__)]
    if "enum" in schema and _canon(inst) not in [_canon(x) for x in schema["enum"]]:
        out.append("%s: %s is not one of %s" % (path, _canon(inst)[:60], _canon(schema["enum"])[:80]))
    if "const" in schema and _canon(inst) != _canon(schema["const"]):
        out.append("%s: %s is not the constant %s" % (path, _canon(inst)[:60], _canon(schema["const"])))
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            out.append("%s: does not match pattern %s" % (path, schema["pattern"][:60]))
        if "minLength" in schema and len(inst) < schema["minLength"]:
            out.append("%s: shorter than %d" % (path, schema["minLength"]))
        if "maxLength" in schema and len(inst) > schema["maxLength"]:
            out.append("%s: longer than %d" % (path, schema["maxLength"]))
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            out.append("%s: %s < minimum %s" % (path, inst, schema["minimum"]))
        if "maximum" in schema and inst > schema["maximum"]:
            out.append("%s: %s > maximum %s" % (path, inst, schema["maximum"]))
        if "exclusiveMinimum" in schema and inst <= schema["exclusiveMinimum"]:
            out.append("%s: %s <= exclusiveMinimum %s" % (path, inst, schema["exclusiveMinimum"]))
    if isinstance(inst, dict):
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in inst:
                out.append("%s: missing required property %s" % (path, k))
        for k, v in inst.items():
            if k in props:
                out += errors(props[k], v, "%s.%s" % (path, k))
            elif "additionalProperties" in schema:
                ap = schema["additionalProperties"]
                if ap is False:
                    out.append("%s: additional property %s is not allowed" % (path, k))
                elif isinstance(ap, dict):
                    out += errors(ap, v, "%s.%s" % (path, k))
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            out.append("%s: fewer than %d items" % (path, schema["minItems"]))
        if schema.get("uniqueItems") and len(set(_canon(x) for x in inst)) != len(inst):
            out.append("%s: items are not unique" % path)
        if "items" in schema:
            for i, x in enumerate(inst):
                out += errors(schema["items"], x, "%s[%d]" % (path, i))
    for sub in schema.get("allOf", []):
        out += errors(sub, inst, path)
    if "anyOf" in schema and not any(not errors(sub, inst, path) for sub in schema["anyOf"]):
        out.append("%s: matches none of the anyOf alternatives" % path)
    if "not" in schema and not errors(schema["not"], inst, path):
        out.append("%s: matches a schema it must not match" % path)
    if "if" in schema:
        if not errors(schema["if"], inst, path):
            if "then" in schema:
                out += errors(schema["then"], inst, path)
        elif "else" in schema:
            out += errors(schema["else"], inst, path)
    return out
