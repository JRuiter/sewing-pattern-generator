"""Hoodie / sweatshirt: T-shirt block (sweat, wide, long sleeves with cuffs, hem band)
+ hood (two mirrored pieces) and an optional kangaroo pocket.
Without the hood you get a sweatshirt with a neckband."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece

from . import tshirt_basic as T

DEFAULTS = dict(fit="wide", fabric="sweat", hood=True, kangaroo=True, sleeve_style="set_in",
                sleeve_length="long", sleeve_cuffs=True, hem_band=True, hood_lining=False)

FINISHED_LABELS = dict(T.FINISHED_LABELS, hood_height=("Hood height", "length"))


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    hood = bool(o.pop("hood"))
    kang = bool(o.pop("kangaroo"))
    lining = bool(o.pop("hood_lining"))
    if hood:
        o.setdefault("neck_extra", 8.0)
        o["neckline"] = "round"
    pat = T.draft(measures, o, _garment="hoodie")
    m = measures
    pat.title = "Hoodie" if hood else "Sweatshirt"
    pat.options.update(hood=hood, kangaroo=kang, hood_lining=lining)
    sa = pat.options["sa"]
    front = pat.piece("front")
    if hood:
        # remove the neckband, add the hood
        pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
        pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
        pat.checks = [c for c in pat.checks if c["name"] != "Neckline fits over the head"]
        refs = [("front", "neckline", 1), ("back", "neckline", 1)]
        if pat.piece("sleeve").edges[-1].name == "neck":
            refs.append(("sleeve", "neck", 1))
        half_neck = sum(pat.piece(k).edge(e).length * n for k, e, n in refs)
        Hh = 0.58 * m["head"] + 25
        Wh = 0.44 * m["head"] + 15
        # neck edge: curved slightly down, length = half the neckline
        def neck_curve(bx):
            return G.cubic(G.P(0, 0), G.P(bx * 0.35, 0), G.P(bx * 0.7, -8), G.P(bx, 18))
        lo, hi = half_neck * 0.6, half_neck * 1.05
        for _ in range(50):
            bx = (lo + hi) / 2
            if G.length(neck_curve(bx)) < half_neck:
                lo = bx
            else:
                hi = bx
        neck = neck_curve((lo + hi) / 2)
        B0 = neck[-1]
        Tp = G.P(0, Hh)
        back = G.cubic(B0, B0 + np.array([max(Wh - B0[0], 10) * 0.9 + 15, Hh * 0.3]),
                       G.P(Wh * 0.95, Hh * 1.02), Tp)
        back = G.join(back)
        edges = [
            Edge("neck", neck, sa, label="Neck seam"),
            Edge("center", back, sa, label="Hood centre seam"),
            Edge("front_edge", G.line(Tp, G.P(0, 0)), 25.0, label="Front edge (casing/facing)", turned=True),
        ]
        hp = Piece("hood", "Hood", edges, cut_count=4 if lining else 2, mirror=True, fabric="Main fabric",
                   grain=(G.P(Wh * 0.4, Hh * 0.2), G.P(Wh * 0.4, Hh * 0.75)))
        hp.marks.append(Mark(G.line(G.P(12, Hh * 0.92), G.P(12, 8)), "fold", "Front edge fold line"))
        if lining:
            hp.info.append("2× main fabric + 2× lining (jersey)")
        pat.pieces.append(hp)
        pat.seams.append(dict(name="Hood ↔ neckline (each side)", a=refs, b=[("hood", "neck", 1)],
                              type="equal"))
        pat.seams.append(dict(name="Hood centre seam (left ↔ right)", a=[("hood", "center", 1)],
                              b=[("hood", "center", 1)], type="equal"))
        pat.corners.append(dict(name="Hood: front edge ↔ neck seam", piece="hood", a="front_edge", b="neck",
                                target=90))
        pat.checks.append(dict(name="Hood tall enough", kind="min", value=Hh + 0.0, target=0.55 * m["head"],
                               note="hood height ≥ 0.55 × head circumference"))
        pat.finished["hood_height"] = Hh
    if kang:
        F = pat.options["_F"]
        q = F["q"]
        hem_y = float(front.edge("hem").pts[0, 1])
        Wk, Hk = q * 0.62, min(0.36 * F["L"], 0.45 * (-hem_y - F["AD"]))
        op = Hk * 0.55
        pts = [G.P(0, 0), G.P(Wk, 0), G.P(Wk, Hk - op), G.P(Wk - op * 0.45, Hk), G.P(0, Hk)]
        edges = [
            Edge("bottom", G.line(pts[0], pts[1]), sa, label="Hem seam"),
            Edge("side", G.line(pts[1], pts[2]), sa, label="Side"),
            Edge("opening", G.line(pts[2], pts[3]), 15.0, label="Opening (hem it)"),
            Edge("top", G.line(pts[3], pts[4]), sa, label="Top edge (press under)"),
            Edge("center", G.line(pts[4], pts[0]), 0.0, True, "Centre (fold)"),
        ]
        kp = Piece("kangaroo_pocket", "Kangaroo pocket", edges, cut_count=1, mirror=False, fabric="Main fabric",
                   grain=(G.P(Wk * 0.35, Hk * 0.2), G.P(Wk * 0.35, Hk * 0.8)))
        pat.pieces.append(kp)
        y0 = hem_y
        front.marks.append(Mark(np.array([[0, y0 + Hk], [Wk - op * 0.45, y0 + Hk], [Wk, y0 + Hk - op],
                                          [Wk, y0]]), "placement", "Kangaroo pocket"))
    return pat


def finished_measures(pat):
    return T.finished_measures(pat)


def sewing_steps(pat):
    o = pat.options
    steps = []
    if o.get("kangaroo"):
        steps.append("**Kangaroo pocket:** press the openings under by 1.5 cm and topstitch, press the top edge "
                     "under by 1 cm. Place the pocket on the front at the marking and stitch the top edge and sides; "
                     "the bottom edge is caught later with the hem band.")
    base = T.sewing_steps(pat)
    if o.get("hood"):
        base = [s for s in base if not s.startswith("**Neckband")]
        hood = ["**Hood:** place the hood pieces right sides together and sew the centre seam. Press the front "
                "edge to the inside along the fold line and topstitch (it can take a drawstring)" +
                ("; for a lined hood, sew the lining the same way and join it to the hood right sides together "
                 "along the front edge, then turn" if o.get("hood_lining") else "") + ".",
                "**Attach the hood:** pin the hood right sides together to the neckline (centre seam at centre "
                "back, front edges meet at centre front, overlap by 1 cm if needed) and sew. Finish the seam "
                "allowance with jersey binding."]
        base = base[:1] + hood + base[1:]
    return steps + base
