"""Baby bib, 0–3 years: `classic` (round bib whose tabs close behind the neck with a snap) or
`bandana` (triangle). Two layers sewn right sides together and turned: cotton on top, terry or
fleece underneath, optionally an absorbent layer in between."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point, Polygon

import geometry as G
from pattern import Mark, Pattern, Piece

from ._common import arc, edges_from_ring, resolve, ring_of, smooth

DEFAULTS = dict(style="classic", fabric="woven", stretch=None, absorbent=True, sa=7.5, length_cm=None)
FINISHED_LABELS = {"length": ("Length", "length"), "width": ("Width", "width")}
FIT_CHECK = "does the neck opening close with a little room (one finger) and cover the chest?"
OVERLAP = 30.0       # mm, tabs overlap at the back for the snap
TAB = 32.0           # mm, width of the band round the neck


def _outline(m: dict, o: dict) -> tuple[Polygon, float, float, float]:
    """Bib shape with the neck centre at (0, 0); returns (polygon, inner radius, gap angle, length)."""
    # the neck curve is neck + overlap long and leaves a gap of 2 × gap° at the back
    gap = 14.0
    li = m["neck"] * 1.05 + OVERLAP
    ri = li / (2 * math.pi * (360 - 2 * gap) / 360)
    ro = ri + TAB
    L = o["length_cm"] * 10 if o["length_cm"] else float(np.clip(0.30 * m["chest"], 130, 210))
    W = float(np.clip(0.42 * m["chest"], 170, 260))
    ring_pts = np.vstack([arc(0, 0, ro, 90 + gap, 450 - gap, 1.0), arc(0, 0, ri, 450 - gap, 90 + gap, 1.0)])
    band = Polygon(ring_pts).buffer(0)
    top_y, bot_y = ri * 0.35, -(ri + L)
    if o["style"] == "classic":
        from shapely import affinity
        W = max(W, 2 * ro + 30)
        body = affinity.scale(Point(0, (top_y + bot_y) / 2).buffer(1.0, 128), W / 2, (top_y - bot_y) / 2)
    else:
        W = max(W, 2 * ro + 50)
        body = smooth(Polygon([(-W / 2, top_y), (W / 2, top_y), (0, bot_y)]), 22.0)
    shape = band.union(body).difference(Point(0, 0).buffer(ri, 256))
    shape = shape.buffer(10, join_style=1).buffer(-10, join_style=1)     # fill the notch tab ↔ body
    shape = shape.difference(Point(0, 0).buffer(ri, 256)).difference(
        Polygon([(0, 0), (ro * 2 * math.sin(math.radians(gap)), ro * 2 * math.cos(math.radians(gap))),
                 (-ro * 2 * math.sin(math.radians(gap)), ro * 2 * math.cos(math.radians(gap)))]))
    if shape.geom_type != "Polygon":
        shape = max(shape.geoms, key=lambda g: g.area)
    # soften the two tab ends
    shape = shape.buffer(-4, join_style=1).buffer(4, join_style=1)
    return shape, ri, gap, L


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    if o["style"] not in ("classic", "bandana"):
        raise ValueError("bib style must be classic or bandana")
    shape, ri, gap, L = _outline(m, o)
    ring = ring_of(shape, 1.5)
    # neck edge: the ring points on the inner circle, from the left tab end round to the right one
    r = np.linalg.norm(ring, axis=1)
    on_neck = np.abs(r - ri) < 3.0
    idx = np.where(on_neck)[0]
    ang = np.degrees(np.arctan2(ring[:, 1], ring[:, 0])) % 360
    neck_pts = idx[(np.abs(ang[idx] - 90) > gap + 6)]
    left = ring[neck_pts[np.argmin((ang[neck_pts] - 90) % 360)]]      # neck curve next to the left tab end
    right = ring[neck_pts[np.argmax((ang[neck_pts] - 90) % 360)]]     # … and next to the right one
    sa = o["sa"]
    edges = edges_from_ring(ring, [(left, "outer", sa, "Outer edge"), (right, "neck", sa, "Neck edge")])
    xs, ys = ring[:, 0], ring[:, 1]
    y_lo, y_hi = ys.min() + 15, -ri - 12
    grain = (G.P(0, y_lo + 0.15 * (y_hi - y_lo)), G.P(0, y_hi - 0.1 * (y_hi - y_lo)))
    top = Piece("bib_top", "Bib top", edges, cut_count=1, mirror=False, fabric="Main fabric", grain=grain)
    under = Piece("bib_under", "Bib underside", [type(e)(e.name, e.pts.copy(), e.sa, e.fold, e.label) for e in edges],
                  cut_count=1, mirror=False, fabric="Terry or fleece", grain=grain)
    snap_l = G.P(-(ri + TAB / 2) * math.sin(math.radians(gap + 10)), (ri + TAB / 2) * math.cos(math.radians(gap + 10)))
    for pc in (top, under):
        pc.marks.append(Mark(np.vstack([snap_l, snap_l]), "placement", "Snap"))
    pieces = [top, under]
    seams = [dict(name="Bib round", a=[("bib_top", "outer", 1), ("bib_top", "neck", 1)],
                  b=[("bib_under", "outer", 1), ("bib_under", "neck", 1)], type="equal")]
    if o["absorbent"]:
        inner = shape.buffer(-sa * 0.4 - 4)
        if inner.geom_type != "Polygon":
            inner = max(inner.geoms, key=lambda g: g.area)
        ring2 = ring_of(inner, 1.5)
        r2 = np.linalg.norm(ring2, axis=1)
        ang2 = np.degrees(np.arctan2(ring2[:, 1], ring2[:, 0])) % 360
        nk = np.where(np.abs(r2 - (ri + 4 + sa * 0.4)) < 4)[0]
        nk = nk[np.abs(ang2[nk] - 90) > gap + 8]
        e2 = edges_from_ring(ring2, [(ring2[nk[np.argmin((ang2[nk] - 90) % 360)]], "outer", 0.0, "Outer edge"),
                                     (ring2[nk[np.argmax((ang2[nk] - 90) % 360)]], "neck", 0.0, "Neck edge")])
        for e in e2:
            e.raw = True
        pieces.append(Piece("bib_core", "Absorbent layer", e2, cut_count=1, mirror=False,
                            fabric="Absorbent layer (terry, bamboo fleece)", grain=grain))
        pieces[-1].info.append("No seam allowance: lies loose inside, caught by the topstitching")
    W = float(xs.max() - xs.min())
    checks = [dict(name="Neck opening incl. overlap", kind="range",
                   value=G.length(top.edge("neck").pts) - OVERLAP, lo=m["neck"] * 0.98, hi=m["neck"] * 1.2,
                   note="neck + a finger of room")]
    title = "Bib" if o["style"] == "classic" else "Bandana bib"
    pat = Pattern("bib", title, "", pieces, dict(m), o, seams=seams, corners=[], checks=checks)
    pat.finished = dict(length=float(-ys.min()), width=W)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("bib_top").edge("outer").sa)
    out = []
    if pat.has("bib_core"):
        out.append(ST.icon("Lay the absorbent layer in", "hand",
                           "Lay the absorbent layer centred on the wrong side of the underside and pin it; it is "
                           "caught later by the topstitching.", section="Bib"))
    out += [
        ST.seam("Sew round the bib", ["Bib round"],
                "Lay top and underside right sides together, edges level, and pin. "
                f"Sew all round with {sa} seam allowance; leave 6 cm open on the lower edge.", section="Bib",
                hint="Clip the allowances in the neck curve every 1 cm, close to the seam."),
        ST.icon("Turn right side out", "turn",
                "Turn through the opening, shape the tabs and press. Fold the allowances of the opening in.",
                section="Bib"),
        ST.topstitch("Topstitch all round", [("bib_top", "outer"), ("bib_top", "neck")], 4.0,
                     "Topstitch 4 mm from the edge all round; this also closes the opening.", section="Bib"),
        ST.icon("Attach the snap", "snap",
                "Attach a plastic snap to the marked tab ends: the cap on the top tab, the socket on the other.",
                section="Bib"),
        ST.done(""),
    ]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
