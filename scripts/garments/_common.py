"""Small helpers shared by the simpler garment modules (accessories, baby items)."""
from __future__ import annotations


def resolve(defaults: dict, options: dict | None) -> dict:
    o = dict(defaults)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    return o


def is_adult(m: dict) -> bool:
    return m["height"] > 1650 and m["chest"] > 780


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# derived hand and foot measurements (mm) from body height, if not given (anthropometric means)
def hand_length(m: dict, o: dict) -> float:
    return float(o.get("hand_length") or m.get("hand_length") or 0.108 * m["height"])


def hand_circ(m: dict, o: dict) -> float:
    """Circumference of the hand across the knuckles (without thumb)."""
    return float(o.get("hand_circ") or m.get("hand_circ") or max(m["wrist"] * 1.38, 0.112 * m["height"]))


def foot_length(m: dict, o: dict) -> float:
    return float(o.get("foot_length") or m.get("foot_length") or 0.152 * m["height"])


def foot_circ(m: dict, o: dict) -> float:
    """Ball-of-foot circumference."""
    return float(o.get("foot_circ") or m.get("foot_circ") or 0.95 * foot_length(m, o))


# --------------------------------------------------------------------------- shapes from polygons
# Accessories (bibs, mittens, hats) are easiest to draft as a union of simple shapes; these helpers
# turn such a shapely polygon into the counter-clockwise named edges a Piece needs.

def ring_of(poly, step: float = 2.0):
    """Counter-clockwise exterior of a shapely polygon, resampled, without the closing point."""
    import numpy as np
    from shapely.geometry.polygon import orient

    import geometry as G
    ring = np.asarray(orient(poly, 1.0).exterior.coords, float)
    out = [ring[:1]]
    for a, b in zip(ring[:-1], ring[1:]):           # densify, keeping every corner of the polygon
        seg = G.line(a, b, step)
        out.append(seg[1:])
    ring = np.vstack(out)
    return ring[:-1] if np.linalg.norm(ring[0] - ring[-1]) < 1e-6 else ring


def edges_from_ring(ring, starts: list[tuple]) -> list:
    """Split a closed ring into edges. ``starts``: ``(point, name, sa, label[, turned])`` in
    counter-clockwise order; each edge runs from its start point to the next one."""
    import numpy as np

    from pattern import Edge
    idx = [int(np.argmin(np.linalg.norm(ring - np.asarray(s[0], float), axis=1))) for s in starts]
    r = np.roll(ring, -idx[0], axis=0)
    n = len(ring)
    idx = [(i - idx[0]) % n for i in idx]
    out = []
    for k, s in enumerate(starts):
        a, b = idx[k], (idx[k + 1] if k + 1 < len(idx) else n)
        pts = np.vstack([r[a:b + 1], r[:1]]) if b == n else r[a:b + 1]
        out.append(Edge(s[1], pts.copy(), s[2], label=s[3], turned=bool(s[4]) if len(s) > 4 else False))
    return out


def smooth(poly, r: float):
    """Round the convex corners of a polygon with radius r (and fill tiny notches)."""
    return poly.buffer(-r, join_style=1).buffer(r, join_style=1) if r > 0 else poly


def rounded_rect(x0: float, y0: float, x1: float, y1: float, r: float):
    from shapely.geometry import box
    return smooth(box(x0, y0, x1, y1), min(r, (x1 - x0) / 2 - 0.5, (y1 - y0) / 2 - 0.5))


def arc(cx: float, cy: float, r: float, a0: float, a1: float, step: float = 2.0):
    """Circular arc (angles in degrees, counter-clockwise from a0 to a1)."""
    import math

    import numpy as np
    n = max(8, int(abs(math.radians(a1 - a0)) * r / step) + 1)
    t = np.radians(np.linspace(a0, a1, n))
    return np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)])


def fillet(pts, corner, r: float = 5.0):
    """Round a sharp corner of a polyline (the point nearest to ``corner``) over ``r`` mm each side."""
    import numpy as np

    import geometry as G
    pts = np.asarray(pts, float)
    i = int(np.argmin(np.linalg.norm(pts - np.asarray(corner, float), axis=1)))
    cl = G.cumlen(pts)
    a = int(np.searchsorted(cl, cl[i] - r))
    b = int(np.searchsorted(cl, cl[i] + r))
    a, b = max(a, 0), min(b, len(pts) - 1)
    if a >= i or b <= i:
        return pts
    return np.vstack([pts[:a], G.quad(pts[a], pts[i], pts[b], 0.5), pts[b + 1:]])
