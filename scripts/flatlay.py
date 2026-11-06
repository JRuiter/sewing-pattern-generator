"""Flat-lay model of a top (T-shirt / raglan) for photo mode B (issue #4).

A sewn top laid flat, front up, sleeves spread sideways: the body is front ∪ back (both
mirrored at the centre front), the sleeve is folded along its top line, which starts at the
shoulder point (set-in) or at the raglan point on the neckline and runs outwards at the
angle at which the flattened sleeve is exactly half the sleeve width wide at the underarm.

The same model is used twice: to synthesise test photos (photo_synth) and, inside the
least-squares fit (reverse/fit.py), to compute from a drafted pattern the very features that
photo_measure.measure_top reads from a photo. Scene coordinates: mm, x = 0 at the centre
front, y down, y = 0 at the highest point of the garment.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

TOP_ZONE = 0.4        # the reference "highest point" lies within ±0.4 × hem width of the centre


def _scene(pts):
    p = np.asarray(pts, float)
    return np.stack([p[:, 0], -p[:, 1]], 1)


def _full(ring):
    r = _scene(ring)
    m = r.copy()
    m[:, 0] = -m[:, 0]
    return unary_union([Polygon(r).buffer(0), Polygon(m).buffer(0)])


def _width_at(poly, y):
    ln = LineString([(-1e4, y), (1e4, y)])
    seg = poly.intersection(ln)
    if seg.is_empty:
        return 0.0
    xs = np.asarray([c[0] for g in getattr(seg, "geoms", [seg]) for c in g.coords])
    return float(xs.max() - xs.min())


def neck_corner(xs, ys, x_peak, back_neck, P0):
    """Neck point as the corner of the outline: the shoulder line (y = k·x + c, through the
    shoulder point P0 = (x, y) with slope k) meets the line fitted to the steep part of the back
    neckline (25–75 % of the back neck depth). A photo rounds the corner off, the two lines are
    not affected. xs, ys: top contour (mm, x from the centre, y down from the highest point)."""
    k, c = P0
    sel = []
    for i in np.nonzero(xs <= x_peak)[0][::-1]:
        if ys[i] > 0.75 * back_neck or np.isnan(ys[i]):
            break
        if ys[i] >= 0.25 * back_neck:
            sel.append(i)
    if len(sel) < 3:
        return None
    a, b = np.polyfit(ys[sel], xs[sel], 1)          # back neckline: x = a·y + b (steep)
    y = (k * b + c) / (1 - k * a)
    return float(a * y + b)


def _top_contour(poly, x0, x1, step=0.25):
    xs = np.arange(x0, x1, step)
    ys = np.full(len(xs), np.nan)
    for i, x in enumerate(xs):
        seg = poly.intersection(LineString([(x, -1e4), (x, 1e4)]))
        if not seg.is_empty:
            ys[i] = seg.bounds[1]
    return xs, ys


def _sleeve_angle(P0, U, half_w):
    """Angle α (rad, downwards from horizontal) of the sleeve top line through P0 such that the
    perpendicular distance of the underarm point U to it equals half the sleeve width (on the
    branch closest to horizontal; slightly upwards if the sleeve is very wide)."""
    v = U - P0

    def f(a):
        return math.cos(a) * v[1] - math.sin(a) * v[0] - half_w

    lo, hi = -math.atan2(v[0], v[1]), math.radians(85)
    if f(lo) < 0:
        return lo
    if f(hi) > 0:
        return hi
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def top_flatlay(pat) -> dict:
    o, fin = pat.options, pat.finished
    F, sinfo = o["_F"], o["_sinfo"]
    raglan = o.get("sleeve_style") == "raglan"
    front, back = pat.piece("front"), pat.piece("back")
    body = unary_union([_full(front.seam_ring()), _full(back.seam_ring())])
    U = np.array([F["q"], F["AD"]])
    SW, SL, op = sinfo["SW"], sinfo["SL"], sinfo["op"]
    if raglan:
        closing = _scene(back.edge("raglan").pts)        # U → raglan point on the back neckline
        P0 = closing[-1]
        seam = _scene(front.edge("raglan").pts)
    else:
        P0 = np.array([F["sx"], -F["sy"]])               # shoulder point
        closing = _scene(front.edge("armhole").pts)      # U → S
        seam = closing
    a = _sleeve_angle(P0, U, SW / 2)
    d = np.array([math.cos(a), math.sin(a)])
    n = np.array([-d[1], d[0]])                          # perpendicular, downwards
    T = P0 + SL * d
    B = T + (op / 2) * n
    ring = np.vstack([[P0], [T], [B], closing])
    sleeve = Polygon(ring).buffer(0)
    sleeves = unary_union([sleeve, Polygon(ring * np.array([-1.0, 1.0])).buffer(0)])
    sil = unary_union([body, sleeves]).buffer(0.01).buffer(-0.01)
    hw = _width_at(body, body.bounds[3] - 10.0)
    zone = sil.intersection(Polygon([(-TOP_ZONE * hw, -1e4), (TOP_ZONE * hw, -1e4),
                                     (TOP_ZONE * hw, 1e4), (-TOP_ZONE * hw, 1e4)]))
    y0 = zone.bounds[1]                                  # highest point of the neck/shoulder area
    if raglan:
        # raglan: the top of the sleeves is nearly level, so its highest point is ill-defined;
        # the reference is the centre back neck instead
        y0 = sil.intersection(LineString([(0.0, -1e4), (0.0, 1e4)])).bounds[1]
    shift = np.array([0.0, -y0])
    from shapely.affinity import translate
    sil = translate(sil, 0.0, -y0)
    body_s = translate(body, 0.0, -y0)
    neck = _scene(front.edge("neckline").pts) + shift    # visible front neckline: neck end → centre
    seam = seam + shift
    lines = [neck, neck * np.array([-1.0, 1.0]), seam, seam * np.array([-1.0, 1.0])]
    U_s, P0_s = U + shift, P0 + shift
    Pc = P0_s - (P0_s[0] / d[0]) * d                     # sleeve top line at the centre (x = 0)
    length = float(-front.edge("hem").pts[0, 1]) - y0
    feats = dict(
        neck_half=float(neck[0, 0]),       # replaced below by the outline corner (set-in)
        back_neck=float(F["bnd"]) - y0,
        front_neck=float(F["fnd"]) - y0,
        length=length,
        armhole_depth=float(U_s[1]),
        chest_flat=_width_at(body_s, U_s[1] + 25.0),
        hem_flat=_width_at(body_s, length - 10.0),
        sleeve_reach=float(SL + np.linalg.norm(P0_s - Pc)),
        sleeve_line_y=float(Pc[1]),
        sleeve_angle=math.degrees(a),
        opening_flat=float(op / 2),
        # = SW / 2 whenever the sleeve can lie flat that way; using SW / 2 itself keeps the
        # feature smooth where the angle is clamped (very wide sleeve, see _sleeve_angle)
        bicep_flat=float(SW / 2),
    )
    if not raglan:
        xs, ys = _top_contour(sil, 0.0, float(P0_s[0]))
        kq = (P0_s[1] - neck[0, 1]) / (P0_s[0] - neck[0, 0])
        nc = neck_corner(xs, ys, float(neck[0, 0]), feats["back_neck"], (kq, P0_s[1] - kq * P0_s[0]))
        if nc is not None:
            feats["neck_half"] = nc
        feats["shoulder_x"] = float(P0_s[0])
        feats["shoulder_y"] = float(P0_s[1])
    truth = dict(fin)
    truth.update(feats)
    return dict(silhouette=sil, lines=lines, features=feats, truth=truth, raglan=raglan,
                points=dict(U=U_s, P0=P0_s, T=T + shift, B=B + shift))


FEATURES = ["neck_half", "back_neck", "front_neck", "length", "armhole_depth", "chest_flat", "hem_flat",
            "sleeve_reach", "sleeve_line_y", "opening_flat", "bicep_flat"]
FEATURES_SET_IN = FEATURES + ["shoulder_x", "shoulder_y"]
