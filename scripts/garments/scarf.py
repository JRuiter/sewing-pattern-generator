"""Scarf: a long rectangle, either sewn into a tube (double layer, knit or fleece) or as a single
layer (fleece: raw edges, woven: narrow double hem, optional fringe)."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Mark, Pattern, rect_piece

from ._common import clamp, resolve

DEFAULTS = dict(style="tube", fabric="jersey", stretch=None, length_cm=None, width_cm=None, fringe=False,
                sa=10.0, hem_sa=10.0)
FINISHED_LABELS = {"length": ("Length", "length"), "width": ("Width", "width")}
TITLES = {"tube": "Scarf", "flat": "Scarf"}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    if o["style"] not in ("tube", "flat"):
        raise ValueError("scarf style must be tube or flat")
    # common practice: about 0.95 × body height long (kids 120–140 cm, adults 160–180 cm),
    # 12 % of the height wide (kids 15 cm, adults 20–22 cm)
    L = o["length_cm"] * 10 if o["length_cm"] else clamp(0.95 * m["height"], 700, 1800)
    W = o["width_cm"] * 10 if o["width_cm"] else clamp(0.12 * m["height"], 100, 300)
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    sa = o["sa"]
    seams = []
    checks = [dict(name="Scarf length plausible", kind="range", value=L, lo=0.6 * m["height"], hi=1.3 * m["height"],
                   note="about the body height")]
    if o["style"] == "tube":
        p = rect_piece("scarf", "Scarf", W * 2, L, sa=sa, cut_count=1,
                       names=("end_a", "right", "end_b", "left"),
                       labels=("Scarf end", "Long edge", "Scarf end", "Long edge"))
        p.marks.append(Mark(G.line(G.P(W, 0), G.P(W, L)), "fold", "Fold line"))
        seams.append(dict(name="Long seam", a=[("scarf", "right", 1)], b=[("scarf", "left", 1)], type="equal"))
        seams.append(dict(name="Scarf ends", a=[("scarf", "end_a", 1)], b=[("scarf", "end_b", 1)], type="equal"))
    else:
        raw = o["fabric"] == "fleece"
        hs = 0.0 if raw else o["hem_sa"]
        p = rect_piece("scarf", "Scarf", W, L, sa=hs, cut_count=1,
                       names=("end_a", "right", "end_b", "left"),
                       labels=("Scarf end", "Long edge", "Scarf end", "Long edge"))
        for e in p.edges:
            e.turned = not raw
            e.raw = raw
        if o["fringe"]:
            p.info.append("Fringe: fray 6 cm at both ends")
    if knit:
        p.stretch_dir = "Stretch direction: across the scarf"
    pat = Pattern("scarf", TITLES[o["style"]], "", [p], dict(m), o, seams=seams,
                  corners=[dict(name="Corner", piece="scarf", a="end_a", b="right", target=90)], checks=checks)
    pat.finished = dict(length=L, width=W)
    return pat


def assembly(pat):
    import steps as ST
    o = pat.options
    pc = pat.piece("scarf")
    if o["style"] == "tube":
        sa = ST.cm(pc.edge("right").sa)
        return [
            ST.seam("Sew the long seam", ["Long seam"],
                    "Fold the scarf lengthwise right sides together, long edges level, and pin. "
                    f"Sew with {sa} seam allowance along the whole length: you get a tube.", section="Scarf"),
            ST.seam("Close one end", ["Scarf ends"],
                    f"Sew one end closed with {sa} seam allowance, the long seam in the middle or at the side.",
                    section="Scarf"),
            ST.icon("Turn right side out", "turn",
                    "Push the closed end through the tube with a long ruler or a wooden spoon.", section="Scarf"),
            ST.icon("Close the other end by hand", "hand",
                    "Fold the allowances of the open end inwards and close it with a ladder stitch.",
                    stitch="hand", section="Scarf"),
            ST.done(""),
        ]
    if o["fabric"] == "fleece":
        return [ST.icon("Round the corners", "notch",
                        "Fleece does not fray: round the four corners slightly with scissors. Nothing to sew.",
                        section="Scarf"), ST.done("")]
    hs = pc.edge("right").sa
    out = [ST.hem("Hem the long edges", [("scarf", "right"), ("scarf", "left")], hs / 2,
                  f"Fold each long edge {ST.cm(hs / 2)} to the wrong side and press, then again by the same amount. "
                  "Sew it down close to the inner fold.", section="Scarf")]
    if o["fringe"]:
        out.append(ST.icon("Fray the fringe", "notch",
                           "At both ends pull out the crosswise threads one by one, 6 cm deep. Secure the fringe with "
                           "a straight stitch 6 cm from the end.", section="Scarf"))
    else:
        out.append(ST.hem("Hem the ends", [("scarf", "end_a"), ("scarf", "end_b")], hs / 2,
                          f"Fold each end {ST.cm(hs / 2)} to the wrong side and press, then again by the same amount. "
                          "Sew it down close to the inner fold.", section="Scarf"))
    out.append(ST.done(""))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)


FIT_CHECK = "is the length right when it is wrapped once round the neck?"
