"""Geometry primitives for pattern drafting.

All coordinates in millimetres, mathematical coordinate system (x to the right,
y up). Curves are kept as densely sampled polylines (numpy arrays of shape (n, 2));
Bézier curves are sampled when they are created. This keeps all further operations
(length, offset, intersections, transformations) simple and robust.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring

STEP = 1.0  # default sampling step in mm


def P(x: float, y: float) -> np.ndarray:
    return np.array([float(x), float(y)])


def as_pts(pts) -> np.ndarray:
    a = np.asarray(pts, dtype=float)
    if a.ndim == 1:
        a = a.reshape(1, 2)
    return a


# ---------------------------------------------------------------------------
# Creating lines and curves
# ---------------------------------------------------------------------------

def line(p0, p1, step: float = STEP) -> np.ndarray:
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    n = max(2, int(math.ceil(np.linalg.norm(p1 - p0) / step)) + 1)
    t = np.linspace(0.0, 1.0, n)[:, None]
    return p0 + (p1 - p0) * t


def cubic(p0, p1, p2, p3, step: float = STEP) -> np.ndarray:
    """Cubic Bézier curve, sampled with about `step` mm between points."""
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    approx = (np.linalg.norm(p1 - p0) + np.linalg.norm(p2 - p1) + np.linalg.norm(p3 - p2))
    n = max(8, int(math.ceil(approx / step)) + 1)
    t = np.linspace(0.0, 1.0, n)[:, None]
    mt = 1 - t
    return mt ** 3 * p0 + 3 * mt ** 2 * t * p1 + 3 * mt * t ** 2 * p2 + t ** 3 * p3


def quad(p0, p1, p2, step: float = STEP) -> np.ndarray:
    p0, p1, p2 = (np.asarray(p, float) for p in (p0, p1, p2))
    return cubic(p0, p0 + 2 / 3 * (p1 - p0), p2 + 2 / 3 * (p1 - p2), p2, step)


def unit(v) -> np.ndarray:
    v = np.asarray(v, float)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v


def tangent_curve(p0, dir0, p3, dir3, k0: float = 0.4, k3: float = 0.4,
                  step: float = STEP) -> np.ndarray:
    """Bézier curve from p0 to p3 with given tangent directions.

    dir0: direction in which the curve leaves p0. dir3: direction in which it
    arrives at p3. k0/k3: control-arm length as a fraction of the chord length.
    """
    p0, p3 = np.asarray(p0, float), np.asarray(p3, float)
    c = np.linalg.norm(p3 - p0)
    return cubic(p0, p0 + unit(dir0) * c * k0, p3 - unit(dir3) * c * k3, p3, step)


def join(*parts: np.ndarray) -> np.ndarray:
    """Concatenate polylines, dropping duplicate joint points."""
    out = [as_pts(parts[0])]
    for p in parts[1:]:
        p = as_pts(p)
        if np.linalg.norm(out[-1][-1] - p[0]) < 1e-6:
            p = p[1:]
        out.append(p)
    return np.vstack(out)


# ---------------------------------------------------------------------------
# Measuring
# ---------------------------------------------------------------------------

def length(pts) -> float:
    pts = as_pts(pts)
    if len(pts) < 2:
        return 0.0
    return float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))


def cumlen(pts) -> np.ndarray:
    pts = as_pts(pts)
    return np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])


def point_at(pts, s: float) -> np.ndarray:
    """Point at distance s (mm) from the start along the polyline (negative: from the end)."""
    pts = as_pts(pts)
    cl = cumlen(pts)
    if s < 0:
        s = cl[-1] + s
    s = min(max(s, 0.0), cl[-1])
    i = int(np.searchsorted(cl, s, side="right") - 1)
    i = min(i, len(pts) - 2)
    seg = cl[i + 1] - cl[i]
    t = 0.0 if seg < 1e-12 else (s - cl[i]) / seg
    return pts[i] + (pts[i + 1] - pts[i]) * t


def tangent_at(pts, s: float) -> np.ndarray:
    pts = as_pts(pts)
    total = length(pts)
    a = point_at(pts, max(0.0, min(total, s - 0.5)))
    b = point_at(pts, max(0.0, min(total, s + 0.5)))
    return unit(b - a)


def start_dir(pts, probe: float = 3.0) -> np.ndarray:
    pts = as_pts(pts)
    return unit(point_at(pts, min(probe, length(pts))) - pts[0])


def end_dir(pts, probe: float = 3.0) -> np.ndarray:
    pts = as_pts(pts)
    return unit(pts[-1] - point_at(pts, max(0.0, length(pts) - probe)))


def angle_deg(v1, v2) -> float:
    """Undirected angle between two vectors in degrees (0..180)."""
    v1, v2 = unit(v1), unit(v2)
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(v1, v2))))))


def corner_angle(edge_in, edge_out) -> float:
    """Interior angle at the corner between the end of edge_in and the start of edge_out."""
    a = -end_dir(edge_in, 1.5)
    b = start_dir(edge_out, 1.5)
    return angle_deg(a, b)


def sub(pts, s0: float, s1: float) -> np.ndarray:
    """Part of the polyline between arc lengths s0 and s1."""
    ls = LineString(as_pts(pts))
    g = substring(ls, s0, s1)
    return np.asarray(g.coords, float)


def resample(pts, step: float = STEP) -> np.ndarray:
    pts = as_pts(pts)
    total = length(pts)
    n = max(2, int(math.ceil(total / step)) + 1)
    return np.array([point_at(pts, s) for s in np.linspace(0, total, n)])


def signed_area(poly) -> float:
    p = as_pts(poly)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def bbox(pts):
    p = as_pts(pts)
    return float(p[:, 0].min()), float(p[:, 1].min()), float(p[:, 0].max()), float(p[:, 1].max())


def width_at_y(poly, y: float) -> float:
    """Width of a polygon at height y (sum of all intersection segments)."""
    p = Polygon(as_pts(poly))
    x0, _, x1, _ = p.bounds
    inter = p.intersection(LineString([(x0 - 10, y), (x1 + 10, y)]))
    return float(inter.length)


# ---------------------------------------------------------------------------
# Transformations
# ---------------------------------------------------------------------------

def rot_matrix(angle_deg_: float) -> np.ndarray:
    a = math.radians(angle_deg_)
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def rotate(pts, angle: float, origin=(0.0, 0.0)) -> np.ndarray:
    o = np.asarray(origin, float)
    return (as_pts(pts) - o) @ rot_matrix(angle).T + o


def translate(pts, dx: float, dy: float) -> np.ndarray:
    return as_pts(pts) + np.array([dx, dy])


def mirror_x(pts, x0: float = 0.0) -> np.ndarray:
    """Mirror about the vertical line x = x0."""
    p = as_pts(pts).copy()
    p[:, 0] = 2 * x0 - p[:, 0]
    return p


def mirror_line(pts, a, b) -> np.ndarray:
    """Mirror about the line through a and b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = unit(b - a)
    p = as_pts(pts) - a
    proj = np.outer(p @ d, d)
    return a + 2 * proj - p


def rigid_place(pts, src_a, src_b, dst_a, dst_b_dir=None, dst_b=None) -> np.ndarray:
    """Move a polyline rigidly so that src_a lies on dst_a and the chord
    src_a→src_b points towards dst_b (or dst_b_dir). Length is preserved."""
    src_a, src_b, dst_a = (np.asarray(v, float) for v in (src_a, src_b, dst_a))
    v_src = src_b - src_a
    v_dst = (np.asarray(dst_b, float) - dst_a) if dst_b is not None else np.asarray(dst_b_dir, float)
    ang = math.degrees(math.atan2(v_dst[1], v_dst[0]) - math.atan2(v_src[1], v_src[0]))
    return rotate(as_pts(pts) - src_a, ang) + dst_a


# ---------------------------------------------------------------------------
# Offset (seam allowance) and intersections
# ---------------------------------------------------------------------------

def normals_right(pts) -> np.ndarray:
    """Normal per point, to the right of the direction of travel (outside for a CCW polygon)."""
    p = as_pts(pts)
    d = np.zeros_like(p)
    d[1:-1] = p[2:] - p[:-2]
    d[0] = p[1] - p[0]
    d[-1] = p[-1] - p[-2]
    n = np.stack([d[:, 1], -d[:, 0]], axis=1)
    norm = np.linalg.norm(n, axis=1, keepdims=True)
    norm[norm < 1e-12] = 1.0
    return n / norm


def offset_polyline(pts, d: float) -> np.ndarray:
    """Offset a polyline by d mm to the right (outside); loops are removed."""
    p = as_pts(pts)
    if abs(d) < 1e-9:
        return p.copy()
    ls = LineString(p)
    off = ls.offset_curve(-d, join_style="mitre", mitre_limit=3.0)  # shapely: + = left
    if off.geom_type == "MultiLineString":
        off = max(off.geoms, key=lambda g: g.length)
    out = np.asarray(off.coords, float)
    # keep the direction of travel
    if np.linalg.norm(out[0] - (p[0] + normals_right(p)[0] * d)) > \
            np.linalg.norm(out[-1] - (p[0] + normals_right(p)[0] * d)):
        out = out[::-1]
    return out


def ray_intersection(p, d, q, e):
    """Intersection of the lines p + t d and q + u e. Returns (point, t, u) or None."""
    p, d, q, e = (np.asarray(v, float) for v in (p, d, q, e))
    m = np.array([[d[0], -e[0]], [d[1], -e[1]]])
    det = np.linalg.det(m)
    if abs(det) < 1e-9:
        return None
    t, u = np.linalg.solve(m, q - p)
    return p + t * d, t, u


def _trim_end(a: np.ndarray, pt) -> np.ndarray:
    ls = LineString(a)
    s = ls.project(Point(pt))
    return sub(a, 0, s)


def _trim_start(a: np.ndarray, pt) -> np.ndarray:
    ls = LineString(a)
    s = ls.project(Point(pt))
    return sub(a, s, ls.length)


def join_offsets(a: np.ndarray, b: np.ndarray, limit: float):
    """Join two offset edges at a corner (end of a, start of b)."""
    la, lb = LineString(a), LineString(b)
    inter = la.intersection(lb)
    if not inter.is_empty:
        pts = []
        for g in getattr(inter, "geoms", [inter]):
            if g.geom_type == "Point":
                pts.append(np.array(g.coords[0]))
            else:
                pts.extend(np.array(c) for c in g.coords)
        x = min(pts, key=lambda q: np.linalg.norm(q - a[-1]) + np.linalg.norm(q - b[0]))
        return _trim_end(a, x), _trim_start(b, x)
    da = end_dir(a, 2.0)
    db = start_dir(b, 2.0)
    if angle_deg(da, db) < 3.0:
        return a, b
    r = ray_intersection(a[-1], da, b[0], db)
    if r is not None:
        x, t, u = r
        if t >= -1e-6 and u <= 1e-6 and np.linalg.norm(x - a[-1]) < limit and np.linalg.norm(x - b[0]) < limit:
            return np.vstack([a, x]), np.vstack([x, b])
    return a, b  # bevel


def offset_outline(edges: Sequence[np.ndarray], allowances: Sequence[float]) -> np.ndarray:
    """Cutting outline from a closed CCW edge sequence with a seam allowance per edge."""
    offs = [offset_polyline(e, sa) for e, sa in zip(edges, allowances)]
    n = len(offs)
    limit = 4 * max(max(allowances), 5.0)
    for i in range(n):
        j = (i + 1) % n
        offs[i], offs[j] = join_offsets(offs[i], offs[j], limit)
    ring = join(*offs)
    poly = Polygon(ring)
    if not poly.is_valid:
        poly = poly.buffer(0)
        if poly.geom_type == "MultiPolygon":
            poly = max(poly.geoms, key=lambda g: g.area)
        ring = np.asarray(poly.exterior.coords, float)
        if signed_area(ring) < 0:
            ring = ring[::-1]
    return ring


# ---------------------------------------------------------------------------
# Smoothing free-form contours (reverse engineering)
# ---------------------------------------------------------------------------

def smooth_contour(pts, smoothing: float = 2.0, closed: bool = False, step: float = STEP) -> np.ndarray:
    """Smoothed cubic spline approximation of a noisy contour."""
    from scipy.interpolate import splev, splprep

    p = as_pts(pts)
    keep = np.concatenate([[True], np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-6])
    p = p[keep]
    s = smoothing * len(p)
    tck, _ = splprep([p[:, 0], p[:, 1]], s=s, per=1 if closed else 0, k=3)
    n = max(10, int(length(p) / step))
    x, y = splev(np.linspace(0, 1, n), tck)
    return np.stack([x, y], axis=1)


def polyline_self_intersects(pts) -> bool:
    return not LineString(as_pts(pts)).is_simple


def ring_is_valid(pts) -> bool:
    poly = Polygon(as_pts(pts))
    return bool(poly.is_valid and poly.area > 0)


def fmt_mm(v: float) -> str:
    return f"{v:.0f} mm"


def fmt_cm(v_mm: float, nd: int = 1) -> str:
    return f"{v_mm / 10:.{nd}f} cm"
