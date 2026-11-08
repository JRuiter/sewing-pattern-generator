"""Baseball cap: six crown panels (the two back panels with the arch for the adjustable strap), a
stiffened peak (top, under and a plastic insert), bias binding inside, covered button on top and
a strap with velcro or snaps at the back."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point, Polygon
from shapely import affinity

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import clamp, edges_from_ring, resolve, ring_of

DEFAULTS = dict(fabric="woven", stretch=None, sa=7.5, peak_cm=None, ease_cm=1.0)
FINISHED_LABELS = {"circ": ("Head opening (strap closed in the middle)", "width"), "peak": ("Peak depth", "length"),
                   "height": ("Crown height", "length")}
FIT_CHECK = "does it sit on the head with the strap in the middle position, the peak straight to the front?"


def _side(bw: float, h: float) -> np.ndarray:
    """Left side of a panel from the lower corner (0, 0) to the apex (bw / 2, h)."""
    return G.cubic(G.P(0, 0), G.P(-bw * 0.10, h * 0.42), G.P(bw * 0.18, h * 0.93), G.P(bw / 2, h))


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    sa = o["sa"]
    head = m["head"] + o["ease_cm"] * 10
    bw = head / 6
    h = clamp(0.30 * m["head"], 120, 175)                 # panel height along the seam
    left = _side(bw, h)
    apex = G.P(bw / 2, h)
    # front and side panels; the right side is the mirrored left side (lower right corner → apex)
    edges = [Edge("bottom", G.line(G.P(0, 0), G.P(bw, 0)), sa, label="Lower edge"),
             Edge("right", G.mirror_x(left, bw / 2), sa, label="Crown seam"),
             Edge("left", left[::-1].copy(), sa, label="Crown seam")]
    panel = Piece("panel", "Crown panel", edges, cut_count=4, mirror=False, fabric="Main fabric",
                  grain=(G.P(bw / 2, h * 0.15), G.P(bw / 2, h * 0.65)))
    panel.info.append("2 front panels (with interfacing) and 2 side panels")
    panel.marks.append(Mark(np.vstack([apex - G.P(0, 6), apex - G.P(0, 6)]), "mark", "Eyelet (optional)"))
    # back panels: the arch for the strap is cut out at the centre-back corner
    aw, ah = clamp(0.13 * m["head"], 55, 80), clamp(0.10 * m["head"], 40, 60)
    poly = Polygon(np.vstack([edges[0].pts, edges[1].pts[1:], edges[2].pts[1:-1]]))
    arch = affinity.scale(Point(bw, 0).buffer(1.0, 64), aw / 2, ah)
    back = poly.difference(arch)
    ring = ring_of(back, 1.0)
    # start points: lower left corner, start of the arch, end of the arch on the centre-back side, apex
    on_bottom = ring[np.abs(ring[:, 1]) < 0.5]
    p_arch0 = on_bottom[np.argmax(on_bottom[:, 0])]
    side_pts = ring[(ring[:, 0] > bw * 0.6) & (ring[:, 1] > 1)]
    d_arch = np.abs(((side_pts[:, 0] - bw) / (aw / 2)) ** 2 + (side_pts[:, 1] / ah) ** 2 - 1)
    p_arch1 = side_pts[np.argmin(d_arch + (side_pts[:, 1] < ah * 0.5) * 10)]
    b_edges = edges_from_ring(ring, [(G.P(0, 0), "bottom", sa, "Lower edge"), (p_arch0, "arch", sa, "Strap opening"),
                                     (p_arch1, "cb", sa, "Centre back seam"), (apex, "front", sa, "Crown seam")])
    back_pc = Piece("panel_back", "Back panel", b_edges, cut_count=2, mirror=True, fabric="Main fabric",
                    grain=(G.P(bw * 0.4, h * 0.15), G.P(bw * 0.4, h * 0.65)))
    # peak: inner edge (attached to the two front panels) concave, outer edge D-shaped
    L_in = 2 * bw
    c = L_in * 0.93
    lo, hi = c / 2 + 1, 50 * c
    for _ in range(60):                                # radius whose arc over chord c is L_in long
        r = (lo + hi) / 2
        if 2 * r * math.asin(min(1.0, c / (2 * r))) > L_in:
            lo = r
        else:
            hi = r
    s = r - math.sqrt(r * r - c * c / 4)
    depth = o["peak_cm"] * 10 if o["peak_cm"] else clamp(0.125 * m["head"], 50, 75)
    a0 = math.degrees(math.asin(c / (2 * r)))
    inner = np.array([[r * math.sin(math.radians(t)), r - r * math.cos(math.radians(t)) - s]
                      for t in np.linspace(a0, -a0, 120)])          # right end → left end, bowing down
    xr, xl = inner[0], inner[-1]
    bottom_y = -s - depth
    outer = G.join(G.cubic(xl, xl + G.P(-c * 0.12, -depth * 0.55), G.P(-c * 0.25, bottom_y), G.P(0, bottom_y)),
                   G.cubic(G.P(0, bottom_y), G.P(c * 0.25, bottom_y), xr + G.P(c * 0.12, -depth * 0.55), xr))
    peak_edges = [Edge("inner", inner, sa, label="Peak seam"), Edge("outer", outer, sa, label="Peak edge")]
    peak = Piece("peak", "Peak", peak_edges, cut_count=2, mirror=False, fabric="Main fabric",
                 grain=(G.P(0, bottom_y * 0.75), G.P(0, bottom_y * 0.35)))
    peak.info.append("Top and under peak")
    ins = Piece("peak_insert", "Peak insert", [Edge(e.name, e.pts.copy(), 0.0, label=e.label) for e in peak_edges],
                cut_count=1, mirror=False, fabric="Peak insert (plastic, 0.5–0.8 mm)", grain=peak.grain)
    for e in ins.edges:
        e.raw = True
    ins.info.append("No seam allowance; trim 3 mm all round")
    lower = 4 * bw + 2 * G.length(back_pc.edge("bottom").pts) + 2 * G.length(back_pc.edge("arch").pts)
    strap = rect_piece("strap", "Strap", 30.0 * 2, clamp(0.25 * m["head"], 100, 150), sa=sa, cut_count=2,
                       labels=("Strap end", "Strap edge", "Strap end", "Strap edge"))
    strap.marks.append(Mark(G.line(G.P(30, 0), G.P(30, strap.edges[1].length)), "fold", "Fold line"))
    pieces = [panel, back_pc, peak, ins, strap]
    seams = [dict(name="Crown seams (front and sides)", a=[("panel", "right", 1)], b=[("panel", "left", 1)],
                  type="equal"),
             dict(name="Crown seams (back)", a=[("panel", "right", 1)], b=[("panel_back", "front", 1)], type="equal"),
             dict(name="Centre back seam", a=[("panel_back", "cb", 1)], b=[("panel_back", "cb", 1)], type="equal"),
             dict(name="Peak edge", a=[("peak", "outer", 1)], b=[("peak", "outer", 1)], type="equal"),
             dict(name="Peak ↔ front panels", a=[("peak", "inner", 1)], b=[("panel", "bottom", 2)], type="ease",
                  lo=-2, hi=3, note="peak eased in")]
    circ = 4 * bw + 2 * G.length(back_pc.edge("bottom").pts) + G.length(back_pc.edge("arch").pts) * 0.0 + aw * 0.3
    pat = Pattern("cap", "Baseball cap", "", pieces, dict(m), o, seams=seams, corners=[], checks=[
        dict(name="Head opening incl. strap", kind="range", value=4 * bw + 2 * (bw - aw / 2) + aw * 0.95,
             lo=m["head"], hi=m["head"] + 25, note="strap closed in the middle position")],
        notes=["Button: 1 cover button 18–22 mm for the top", "Velcro: 3 cm × 8 cm for the strap",
               "Interfacing: firm iron-on for the two front panels",
               f"Binding: {(lower + 60) / 10:.0f} cm bias binding, 20 mm wide (folded), for the inside lower edge"])
    pat.finished = dict(circ=circ, peak=depth, height=h)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("panel").edge("right").sa)
    return [
        ST.icon("Interface the front panels", "interfacing",
                "Iron firm interfacing onto the wrong side of two of the four crown panels: they become the front.",
                section="Prepare"),
        ST.seam("Sew the front and the sides", ["Crown seams (front and sides)"],
                "Sew the two front panels together along one long edge, then a side panel to each, all with "
                f"{sa} seam allowance.", section="Crown"),
        ST.seam("Sew the back", ["Centre back seam"],
                f"Sew the two back panels together along the centre-back edge above the arch, {sa} seam allowance.",
                section="Crown"),
        ST.seam("Close the crown", ["Crown seams (back)"],
                f"Pin the back to the front part and sew the two remaining seams with {sa} seam allowance, "
                "over the top.", section="Crown", hint="Press every seam open over a ham or a rolled towel."),
        ST.topstitch("Topstitch the crown seams", [("panel", "right")], 3.0,
                     "Topstitch 3 mm on both sides of every crown seam.", section="Crown"),
        ST.seam("Sew the peak", ["Peak edge"],
                f"Lay the two peak pieces right sides together and sew the outer curve with {sa} seam allowance. "
                "Trim to 3 mm and turn.", section="Peak"),
        ST.topstitch("Slide the insert in", [("peak", "inner")], 8.0,
                     "Push the plastic insert into the peak up to the outer edge. Sew close along the insert's inner "
                     "edge with a zipper foot so it cannot move.", section="Peak"),
        ST.topstitch("Topstitch the peak", [("peak", "outer")], 5.0,
                     "Topstitch rows 6 mm apart, parallel to the outer edge, with a long stitch.", section="Peak"),
        ST.seam("Sew the peak on", ["Peak ↔ front panels"],
                "Pin the peak right sides together to the lower edge of the front panels, centres matching, "
                f"and sew with {sa} seam allowance.", section="Peak"),
        ST.topstitch("Bind the lower edge", [("panel", "bottom"), ("panel_back", "bottom"), ("panel_back", "arch")],
                     5.0, "Unfold one edge of the bias binding and sew it right sides together round the whole lower "
                     "edge and the arch in the crease. Fold it inside over the allowances and topstitch it down.",
                     section="Finish"),
        ST.icon("Sew on the strap", "velcro",
                "Sew the straps with velcro (or snaps) to the inside of the arch, one on each side.", section="Finish"),
        ST.icon("Cover the button", "button", "Cover the button with a scrap of fabric and sew it on the top where "
                "the six seams meet.", stitch="hand", section="Finish", data={"single": True}),
        ST.done("Press the crown over a ball or a rolled towel."),
    ]


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
