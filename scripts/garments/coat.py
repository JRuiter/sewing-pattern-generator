"""Coat: the lined jacket (see `jacket`) in knee length with more ease and flap pockets."""
from __future__ import annotations

from . import jacket as J

DEFAULTS = dict(J.DEFAULTS, style="coat", length="knee")
FINISHED_LABELS = J.FINISHED_LABELS
FIT_CHECK = "does it close over a jacket or a thick sweater, and can you sit down without it pulling?"


def draft(measures: dict, options: dict | None = None):
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    pat = J.draft(measures, o)
    pat.garment = "coat"
    return pat


finished_measures = J.finished_measures
assembly = J.assembly
sewing_steps = J.sewing_steps
