"""Reconstruct: fit the garment module's parameters to the measurements by least squares.

The drafting rules stay valid (smooth curves, right angles); the measurement only
drives the parameters. Several fit variants are tried; the one with the smallest
residual wins (model selection).
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import least_squares

import measurements as M
from garments import get

WIDTH_KEYS = {"hip_circ", "thigh_circ", "knee_circ", "opening", "waist_relaxed", "chest_circ", "hem_circ"}
TOL = {"length": 10.0, "width_rel": 0.02}


def tolerance(key, target):
    return target * TOL["width_rel"] if key in WIDTH_KEYS else TOL["length"]


def estimate_size(targets: dict) -> float:
    """Roughly estimate the kids' size / body height from the outseam (for small pieces, grading)."""
    sizes = sorted(M.KIDS_TABLE)
    side = [M.KIDS_TABLE[s][M.KIDS_COLS.index("side_length")] * 10 for s in sizes]
    out = targets.get("outseam", 700) - targets.get("front_rise", 200) * 0.1
    return float(np.interp(out, side, sizes, left=sizes[0], right=sizes[-1]))


PANTS_PARAMS = ["hip_total", "fork_factor", "front_rise_total", "inseam_total", "opening_total"]
PANTS_RES = ["hip_circ", "thigh_circ", "knee_circ", "opening", "front_rise", "inseam", "outseam"]


def fit_pants(targets: dict, base_options: dict, fits=("harem", "normal", "wide", "slim"), size=None):
    mod = get("pants_basic")
    size = size or round(estimate_size(targets))
    body = M.size_measures(size)
    fixed = dict(base_options)
    fixed.update(waistband_height=targets["waistband_h"] or None,
                 cuff_height=targets["cuff_h"] or None,
                 cuffs=targets["cuff_h"] > 10,
                 elastic_total=targets["waist_relaxed"], blouse=0.0, crotch_drop=0.0)
    if not targets["waistband_h"]:
        fixed["waistband"] = "tunnel"
    best = None
    for fit in fits:
        names = PANTS_PARAMS + (["knee_total"] if fit == "slim" else [])
        x0 = np.array([targets["hip_circ"], 1.0, targets["front_rise"], targets["inseam"], targets["opening"]]
                      + ([targets.get("knee_circ", targets["thigh_circ"] * 0.7)] if fit == "slim" else []))
        lo = x0 * np.array([0.6, 0.4, 0.6, 0.6, 0.5] + ([0.6] if fit == "slim" else []))
        hi = x0 * np.array([1.5, 2.2, 1.5, 1.5, 2.0] + ([1.5] if fit == "slim" else []))
        opts = dict(fixed, fit=fit)
        if fit == "slim":
            opts["fabric"] = opts.get("fabric") if opts.get("fabric") in ("jersey_elastane", "jersey") else "jersey_elastane"
            opts["pockets"] = []

        def residuals(x):
            o = dict(opts, **dict(zip(names, x)))  # noqa: B023 - used within the same iteration
            try:
                pat = mod.draft(body, o)
            except Exception:
                return np.full(len(PANTS_RES), 1e3)
            f = pat.finished
            return np.array([(f[k] - targets[k]) / tolerance(k, targets[k]) for k in PANTS_RES])

        r = least_squares(residuals, x0, bounds=(lo, hi), x_scale=np.maximum(np.abs(x0), 1),
                          diff_step=1e-3, max_nfev=200)
        # model selection: the extra parameter (knee width for "slim") is penalised
        cost = float(np.sum(r.fun ** 2)) + 2.0 * (len(names) - len(PANTS_PARAMS))
        if best is None or cost < best["cost"]:
            params = dict(zip(names, map(float, r.x)))
            best = dict(cost=cost, fit=fit, params=params, options=dict(opts, **params), size=size)
    best["pattern"] = mod.draft(body, best["options"])
    return best


def fit(garment: str, targets: dict, base_options: dict | None = None, **kw):
    if garment in ("pants", "pants_basic"):
        return fit_pants(targets, base_options or {}, **kw)
    from garments import tshirt_basic
    return tshirt_basic.fit_to_targets(targets, base_options or {}, **kw)
