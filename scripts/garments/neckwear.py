"""Neck gaiter (knit tube, double layer) and triangle neckerchief (woven, two layers sewn and
turned, closed with a snap)."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import clamp, is_adult, resolve

DEFAULTS = dict(style="gaiter", fabric=None, stretch=None, height_cm=None, sa=None, circ_total=None)
FINISHED_LABELS = {"circ": ("Circumference", "width"), "height": ("Height", "length")}
FIT_CHECK = "does it go over the head easily and lie flat round the neck?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    if o["style"] not in ("gaiter", "neckerchief"):
        raise ValueError("neckwear style must be gaiter or neckerchief")
    if o["style"] == "gaiter":
        o["fabric"] = o["fabric"] or "jersey"
        o["sa"] = o["sa"] or 7.5
        _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
        # it has to go over the head: circumference incl. half the stretch ≥ head
        circ = o["circ_total"] or max(m["head"] / (1 + stretch / 200), m["neck"] * 1.25)
        h = o["height_cm"] * 10 if o["height_cm"] else clamp(0.17 * m["height"], 150, 300)
        p = rect_piece("gaiter", "Neck gaiter", circ, 2 * h, sa=o["sa"], cut_count=1,
                       names=("bottom", "right", "top", "left"),
                       labels=("Long edge", "Cross seam", "Long edge", "Cross seam"), grain_vertical=False)
        p.marks.append(Mark(G.line(G.P(0, h), G.P(circ, h)), "fold", "Fold line"))
        p.stretch_dir = "Stretch direction: round the neck"
        seams = [dict(name="Cross seam", a=[("gaiter", "right", 1)], b=[("gaiter", "left", 1)], type="equal"),
                 dict(name="Long edges together", a=[("gaiter", "bottom", 1)], b=[("gaiter", "top", 1)],
                      type="equal")]
        checks = [dict(name="Gaiter goes over the head", kind="min", value=circ * (1 + stretch / 200),
                       target=m["head"] * 0.98, note="circumference incl. half the stretch")]
        pat = Pattern("neckwear", "Neck gaiter", "", [p], dict(m), o, seams=seams,
                      corners=[dict(name="Corner", piece="gaiter", a="bottom", b="right", target=90)], checks=checks)
        pat.finished = dict(circ=circ, height=h)
        return pat
    o["fabric"] = o["fabric"] or "woven"
    o["sa"] = o["sa"] or 7.5
    # right-angled triangle: the long edge goes round the neck and overlaps 8–10 cm at the back
    long_edge = o["circ_total"] or m["neck"] * 1.25 + (100 if is_adult(m) else 80)
    half = long_edge / 2
    depth = half * 0.75
    a, b, c = G.P(-half, 0), G.P(half, 0), G.P(0, -depth)
    edges = [Edge("top", G.line(b, a), o["sa"], label="Long edge"),
             Edge("left", G.line(a, c), o["sa"], label="Side edge"),
             Edge("right", G.line(c, b), o["sa"], label="Side edge")]
    p = Piece("scarf", "Neckerchief", edges, cut_count=2, mirror=False, fabric="Main fabric",
              grain=(G.P(0, -depth * 0.2), G.P(0, -depth * 0.75)))
    p.marks.append(Mark(G.line(G.P(-half + 40, -8), G.P(-half + 40, -8)), "placement", "Snap"))
    seams = [dict(name="Outer edges", a=[("scarf", "left", 1), ("scarf", "right", 1)],
                  b=[("scarf", "left", 1), ("scarf", "right", 1)], type="equal"),
             dict(name="Long edge", a=[("scarf", "top", 1)], b=[("scarf", "top", 1)], type="equal")]
    checks = [dict(name="Neckerchief overlaps round the neck", kind="min", value=long_edge,
                   target=m["neck"] * 1.2, note="neck + overlap for the snap")]
    pat = Pattern("neckwear", "Neckerchief", "", [p], dict(m), o, seams=seams, corners=[], checks=checks)
    pat.finished = dict(circ=long_edge, height=depth)
    return pat


def assembly(pat):
    import steps as ST
    if pat.has("gaiter"):
        sa = ST.cm(pat.piece("gaiter").edge("right").sa)
        return [
            ST.seam("Sew the cross seam", ["Cross seam"],
                    "Fold the piece crosswise right sides together, short edges level, and pin. "
                    f"Sew with {sa} seam allowance: you get a wide ring.", section="Gaiter"),
            ST.fold_band("Fold the ring in half", "gaiter",
                         "Fold the ring lengthwise wrong sides together, raw edges level. The seam allowance is "
                         "now inside.", section="Gaiter", data={"hands": "fold"}),
            ST.seam("Sew the raw edges together", ["Long edges together"],
                    f"Pin the raw edges together all round and sew them with {sa} seam allowance, stretching "
                    "slightly. Leave 5 cm open if you sew right sides together and turn; with the overlocker "
                    "sew round in one go.", section="Gaiter"),
            ST.done(""),
        ]
    sa = ST.cm(pat.piece("scarf").edge("top").sa)
    return [
        ST.seam("Sew the side edges", ["Outer edges"],
                "Lay both triangles right sides together, edges level, and pin. "
                f"Sew the two short edges with {sa} seam allowance, pivoting at the point.", section="Neckerchief"),
        ST.seam("Sew the long edge", ["Long edge"],
                f"Sew the long edge with {sa} seam allowance, leaving 6 cm open in the middle.",
                section="Neckerchief", hint="Clip the point diagonally so it turns out sharp."),
        ST.icon("Turn right side out", "turn",
                "Turn through the opening, push the points out with a blunt tool and press.", section="Neckerchief"),
        ST.topstitch("Topstitch all round", [("scarf", "top"), ("scarf", "left"), ("scarf", "right")], 3.0,
                     "Topstitch 3 mm from the edge all round; this also closes the opening.", section="Neckerchief"),
        ST.icon("Attach the snap", "snap",
                "Try it on, mark the overlap and attach a snap (or sew on two ties).", section="Neckerchief"),
        ST.done(""),
    ]


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
