"""Reconstruct: fit the garment module's parameters to the measurements by least squares.

The drafting rules stay valid (smooth curves, right angles); the measurement only
drives the parameters. Several fit variants are tried; the one with the smallest
residual wins (model selection).
"""
from __future__ import annotations

import math

import numpy as np
from scipy.optimize import least_squares

import measurements as M
from garments import get

WIDTH_KEYS = {"hip_circ", "thigh_circ", "knee_circ", "opening", "waist_relaxed", "chest_circ", "hem_circ",
              "chest_flat", "hem_flat"}
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


TOP_OPTS = ["chest_total", "hem_total", "body_length", "bicep_total", "sleeve_len_total", "sleeve_opening"]
TOP_CONS = ["neck_width_half", "back_neck_depth", "front_neck_depth", "armhole_depth"]
TOP_CONS_SET_IN = ["shoulder_length", "shoulder_slope"]


def estimate_top_size(feats: dict) -> float:
    """Kids' size from the chest (body chest ≈ flat chest × 2 / 1.1)."""
    sizes = sorted(M.KIDS_TABLE)
    chest = [M.KIDS_TABLE[s][M.KIDS_COLS.index("chest")] * 10 for s in sizes]
    return float(np.interp(feats["chest_flat"] * 2 / 1.1, chest, sizes, left=sizes[0], right=sizes[-1]))


def _top_params(names, x):
    opts, cons = {}, {}
    for k, v in zip(names, x):
        (cons if k in TOP_CONS + TOP_CONS_SET_IN else opts)[k] = float(v)
    return opts, cons


def fit_top(feats: dict, base_options: dict, size=None, **kw):
    """Tops (T-shirt / raglan): least squares on the flat-lay features (flatlay.py).

    Parameters: chest, hem, length, upper arm, sleeve length and opening (options) plus neck
    width/depths, armhole depth and, for set-in sleeves, shoulder length and slope
    (construction values). Residuals: every feature photo_measure.measure_top reads.
    """
    import flatlay as FLY
    mod = get("tshirt_basic")
    style = base_options.get("sleeve_style", feats.get("_sleeve_style", "set_in"))
    raglan = style == "raglan"
    size = size or round(estimate_top_size(feats) / 6) * 6
    size = min(max(size, min(M.KIDS_TABLE)), max(M.KIDS_TABLE))
    body = M.size_measures(size)
    keys = [k for k in (FLY.FEATURES if raglan else FLY.FEATURES_SET_IN) if k in feats]
    names = TOP_OPTS + TOP_CONS + ([] if raglan else TOP_CONS_SET_IN)
    off = feats.get("back_neck", 0.0)               # raglan: the top is the centre back
    sx = feats.get("shoulder_x", feats["neck_half"] + 60)
    sy = feats.get("shoulder_y", 20.0)
    nw0 = feats["neck_half"] if not raglan else feats["neck_half"] * 1.25
    sh0 = math.hypot(sx - nw0, sy)
    x0 = dict(chest_total=2 * feats["chest_flat"], hem_total=2 * feats["hem_flat"],
              body_length=feats["length"] + (15.0 if raglan else 0.0),
              bicep_total=2 * feats["bicep_flat"],
              sleeve_len_total=max(40.0, feats["sleeve_reach"] - (sx if not raglan else feats["neck_half"])),
              sleeve_opening=2 * feats["opening_flat"],
              neck_width_half=nw0, back_neck_depth=max(5.0, off if not raglan else 15.0),
              front_neck_depth=feats.get("front_neck", nw0 + 20) + (15.0 if raglan else 0.0),
              armhole_depth=feats["armhole_depth"] + (15.0 if raglan else 0.0),
              shoulder_length=sh0, shoulder_slope=math.degrees(math.atan2(sy, max(sx - nw0, 1.0))))
    x0v = np.array([x0[k] for k in names])
    lo = x0v * 0.6
    hi = x0v * 1.6
    if not raglan:
        i = names.index("shoulder_slope")
        lo[i], hi[i] = 0.0, 40.0
    arm = body["arm"]
    sleeve_cat = "short" if x0["sleeve_len_total"] < 0.45 * arm else ("3/4" if x0["sleeve_len_total"] < 0.85 * arm
                                                                          else "long")
    fixed = dict(base_options, sleeve_style=style, sleeve_length=sleeve_cat, sleeve_cuffs=False, hem_band=False)

    def build(x):
        opts, cons = _top_params(names, x)
        return dict(fixed, **opts, construction={**(fixed.get("construction") or {}), **cons})

    scale = {k: 2.0 for k in keys}
    # weak prior towards the size's standard construction values: keeps parameters that the
    # flat lay hardly shows (e.g. the back neck depth of a raglan) at a sensible value
    try:
        std = {c["name"]: c["value"] for c in mod.draft(body, dict(fixed)).construction}
    except Exception:  # pragma: no cover
        std = {}
    prior = [(i, std[k], 5.0 if k == "shoulder_slope" else 20.0)
             for i, k in enumerate(names) if k in std and isinstance(std[k], (int, float))]

    def residuals(x):
        try:
            f = FLY.top_flatlay(mod.draft(body, build(x)))["features"]
        except Exception:
            return np.full(len(keys) + len(prior), 1e3)
        return np.array([(f[k] - feats[k]) / scale[k] for k in keys]
                        + [(x[i] - v) / sc for i, v, sc in prior])

    r = least_squares(residuals, np.clip(x0v, lo + 1e-6, hi - 1e-6), bounds=(lo, hi),
                      x_scale=np.maximum(np.abs(x0v), 1), diff_step=1e-3, max_nfev=200)
    opts = build(r.x)
    pat = mod.draft(body, opts)
    model = FLY.top_flatlay(pat)["features"]
    params = dict(zip(names, map(float, r.x)))
    return dict(cost=float(np.sum(r.fun[:len(keys)] ** 2)), fit=opts.get("fit", "normal"), params=params, options=opts,
                size=size, pattern=pat, features=model, sleeve_style=style)


def regrade_top(options: dict, src_size: float, dst_size: float):
    """A copied top in another size: every fitted value moves by the difference that the
    standard draft shows between the two sizes (the copied ease and proportions stay)."""
    mod = get("tshirt_basic")
    a, b = M.size_measures(src_size), M.size_measures(dst_size)
    base = {k: v for k, v in options.items() if k not in TOP_OPTS and k != "construction"}

    def std(body):
        pat = mod.draft(body, dict(base))
        return {c["name"]: c["value"] for c in pat.construction}, pat
    ca, pa = std(a)
    cb, pb = std(b)
    sa, sb = pa.options["_sinfo"], pb.options["_sinfo"]
    shift = dict(chest_total=cb["chest_width"] - ca["chest_width"], hem_total=cb["chest_width"] - ca["chest_width"],
                 body_length=cb["body_length"] - ca["body_length"], bicep_total=sb["SW"] - sa["SW"],
                 sleeve_len_total=sb["SL"] - sa["SL"], sleeve_opening=sb["op"] - sa["op"])
    opts = dict(base)
    for k in TOP_OPTS:
        if options.get(k) is not None:
            opts[k] = options[k] + shift[k]
    cons = {}
    for k, v in (options.get("construction") or {}).items():
        if isinstance(v, (int, float)) and isinstance(ca.get(k), (int, float)) and isinstance(cb.get(k), (int, float)):
            cons[k] = v + (cb[k] - ca[k])
        else:
            cons[k] = v
    opts["construction"] = cons
    return dict(pattern=mod.draft(b, opts), options=opts, size=dst_size, fit=options.get("fit", "normal"))


def fit(garment: str, targets: dict, base_options: dict | None = None, **kw):
    if garment in ("pants", "pants_basic"):
        return fit_pants(targets, base_options or {}, **kw)
    return fit_top(targets, base_options or {}, **kw)
