"""Decimal parsing for rule inputs (BEH-POL-11, AC-POL-23). Pure: imports only decimal and re.

Accepted: int, float (via repr, so 50000.01 is the decimal 50000.01), Decimal, and a strict numeric string
(optional sign, digits, optional fraction, optional exponent). Rejected -> E-POL-INPUT-INVALID: None, bool,
NaN, +/-Infinity, '', 'abc', '1_000', ' 5 ', '0x10', any other type, and absurd exponents.
"""
import decimal
import re

from hub.policy.errors import InputInvalid

_NUM = re.compile(r"^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)([eE][+-]?[0-9]{1,3})?$")


def to_decimal(value, field="amount"):
    try:
        if isinstance(value, bool) or value is None:
            raise InputInvalid({"field": field, "reason": "null or boolean"})
        if isinstance(value, decimal.Decimal):
            d = value
        elif isinstance(value, int):
            d = decimal.Decimal(value)
        elif isinstance(value, float):
            d = decimal.Decimal(repr(value))
        elif isinstance(value, str):
            if not _NUM.match(value):
                raise InputInvalid({"field": field, "reason": "not a plain decimal string"})
            d = decimal.Decimal(value)
        else:
            raise InputInvalid({"field": field, "reason": "unsupported type"})
    except decimal.InvalidOperation:
        raise InputInvalid({"field": field, "reason": "not a decimal"})
    if not d.is_finite():
        raise InputInvalid({"field": field, "reason": "NaN or infinite"})
    return d


def text(d):
    """Canonical text of a Decimal for traces (no exponent, no trailing-zero padding)."""
    s = format(d.normalize(), "f")
    return "0" if s in ("-0", "") else s
