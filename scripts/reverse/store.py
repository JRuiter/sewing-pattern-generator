"""Save/load a project (piece graph + parameters + measurements) and grading.

"Like the one from last time, but 2 sizes bigger": the measured finished measurements
are carried forward with the differences in body measurements between the sizes
(grading rules per size step), not scaled linearly.
"""
from __future__ import annotations

import json
import os
from datetime import date

import measurements as M

KIDS_SIZES = sorted(M.KIDS_TABLE)


def save(path: str, project: dict) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = dict(project)
    data.setdefault("saved", date.today().isoformat())
    data.pop("pattern", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=float)
    return path


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def size_step(size: float, steps: int) -> float:
    """Kids' sizes go up in 6 cm steps."""
    s = min(KIDS_SIZES, key=lambda k: abs(k - size))
    i = KIDS_SIZES.index(s) + steps
    i = max(0, min(len(KIDS_SIZES) - 1, i))
    return float(KIDS_SIZES[i])


# grading rules for pants: finished measurement ← body measurement difference × factor
PANTS_RULES = {
    "hip_circ": ("hip", None),          # factor = ease of the original (Hc / hip)
    "thigh_circ": ("thigh", None),
    "waist_relaxed": ("waist", 0.9),
    "opening": ("ankle", 1.12),
    "front_rise": ("crotch_depth", 1.0),
    "inseam": ("inseam", 1.0),
    "outseam": ("side_length", 1.0),
}


def grade_targets(targets: dict, src_size: float, dst_size: float) -> dict:
    a = M.size_measures(src_size)
    b = M.size_measures(dst_size)
    out = dict(targets)
    for k, (body, fac) in PANTS_RULES.items():
        if k not in targets:
            continue
        f = fac if fac is not None else targets[k] / a[body]
        out[k] = targets[k] + (b[body] - a[body]) * f
    # waistband/cuff height: slightly with body height
    r = b["height"] / a["height"]
    for k in ("waistband_h", "cuff_h"):
        if targets.get(k):
            out[k] = targets[k] * (1 + (r - 1) * 0.5)
    return out
