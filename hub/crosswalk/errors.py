"""Crosswalk errors live in hub/decision/errors.py (E-ID-*, exit code 26); this module re-exports them for readers of hub.crosswalk."""
from hub.decision.errors import (AmbiguousType, IdNotFound, IdReasonRequired, LinkExists, LinkNotFound, PairNotRegistered,  # noqa: F401
                                 SelfLink)
