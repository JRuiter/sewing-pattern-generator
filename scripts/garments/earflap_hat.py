"""Hat with ear flaps (trapper hat): beanie-like crown in two halves, two ear flaps over the side
seams, fully lined, optional ties. Outer fabric fleece or sweat, lining jersey or fleece."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import arc, clamp, resolve

DEFAULTS = dict(fabric="fleece", stretch=None, ties=True, sa=7.5, flap_cm=None, circ_total=None)
FINISHED_LABELS = {"circ": ("Head opening", "width"), "height": ("Hat height", "length"),
                   "flap": ("Ear flap length", "length")}
FIT_CHECK = "does it sit firmly without pressing, and do the flaps cover the ears completely?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    head = m["head"]
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    # lined, so less negative ease than a single-layer beanie
    circ = o["circ_total"] or head * (0.93 if stretch >= 30 else 1.0)
    W = circ / 2
    H = head * 0.34
    Hs = H - W * 0.42
    sa = o["sa"]
    right = G.line(G.P(W, 0), G.P(W, Hs))
    dome = G.join(G.tangent_curve(G.P(W, Hs), (0, 1), G.P(W / 2, H), (-1, 0), 0.55, 0.55),
                  G.tangent_curve(G.P(W / 2, H), (-1, 0), G.P(0, Hs), (0, -1), 0.55, 0.55))
    left = G.line(G.P(0, Hs), G.P(0, 0))

    def crown(key, name, fab):
        edges = [Edge("bottom", G.line(G.P(0, 0), G.P(W, 0)), sa, label="Lower edge"),
                 Edge("right", right.copy(), sa, label="Side seam"), Edge("crown", dome.copy(), sa, label="Crown seam"),
                 Edge("left", left.copy(), sa, label="Side seam")]
        pc = Piece(key, name, edges, cut_count=2, mirror=False, fabric=fab,
                   grain=(G.P(W / 2, H * 0.15), G.P(W / 2, H * 0.7)))
        return pc
    hat = crown("hat", "Hat", "Main fabric")
    lin = crown("hat_lining", "Hat lining", "Lining")
    # ear flap: top edge across the side seam, U-shaped bottom
    fw = clamp(0.21 * head, 90, 130)
    fh = o["flap_cm"] * 10 if o["flap_cm"] else clamp(0.15 * head, 60, 95)
    r = fw / 2
    flap_edges = [Edge("top", G.line(G.P(fw, 0), G.P(0, 0)), sa, label="Flap top"),
                  Edge("outline", G.join(G.line(G.P(0, 0), G.P(0, -(fh - r))), arc(r, -(fh - r), r, 180, 360, 1.0),
                                         G.line(G.P(fw, -(fh - r)), G.P(fw, 0))), sa, label="Flap edge")]
    # the top edge has to be its own run of points from right to left: counter-clockwise is top (right→left),
    # then down the left, round the bottom and up the right
    flap = Piece("flap", "Ear flap", flap_edges, cut_count=2, mirror=False, fabric="Main fabric",
                 grain=(G.P(r, -fh * 0.7), G.P(r, -fh * 0.2)))
    flap_l = Piece("flap_lining", "Ear flap lining", [Edge(e.name, e.pts.copy(), e.sa, label=e.label)
                                                      for e in flap_edges], cut_count=2, mirror=False,
                   fabric="Lining", grain=flap.grain)
    for pc in (hat, lin):
        pc.marks.append(Mark(G.line(G.P(W - fw / 2, 2), G.P(W, 2)), "placement", "Ear flap"))
    pieces = [hat, lin, flap, flap_l]
    seams = [dict(name="Side and crown seams", a=[("hat", "right", 1), ("hat", "crown", 1)],
                  b=[("hat", "left", 1), ("hat", "crown", 1)], type="equal"),
             dict(name="Lining side and crown seams", a=[("hat_lining", "right", 1), ("hat_lining", "crown", 1)],
                  b=[("hat_lining", "left", 1), ("hat_lining", "crown", 1)], type="equal"),
             dict(name="Ear flaps round", a=[("flap", "outline", 1)], b=[("flap_lining", "outline", 1)],
                  type="equal"),
             dict(name="Lower edge (hat ↔ lining)", a=[("hat", "bottom", 2)], b=[("hat_lining", "bottom", 2)],
                  type="equal")]
    if o["ties"]:
        tl = clamp(0.30 * head, 150, 300)
        tie = rect_piece("tie", "Tie", 40.0, tl, sa=sa, cut_count=2,
                         labels=("Tie end", "Tie edge", "Tie end", "Tie edge"))
        pieces.append(tie)
        seams.append(dict(name="Ties", a=[("tie", "right", 1)], b=[("tie", "left", 1)], type="equal"))
    checks = [dict(name="Hat goes over the head", kind="min", value=circ * (1 + stretch / 200), target=head * 0.99,
                   note="opening incl. half the stretch"),
              dict(name="Flap covers the ear", kind="min", value=fh, target=0.10 * head, note="≥ 10 % of the head")]
    pat = Pattern("earflap_hat", "Ear flap hat", "", pieces, dict(m), o, seams=seams, corners=[
        dict(name="Side ↔ crown (smooth)", piece="hat", a="right", b="crown", target=180)], checks=checks)
    pat.finished = dict(circ=circ, height=H, flap=fh)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("hat").edge("right").sa)
    out = []
    if pat.has("tie"):
        out += [ST.seam("Sew the ties", ["Ties"],
                        f"Fold each tie lengthwise right sides together and sew the long edge and one end with {sa} "
                        "seam allowance. Turn with a safety pin.", section="Ties")]
    out += [
        ST.seam("Sew the ear flaps", ["Ear flaps round"],
                "Lay each flap right sides together onto its lining" + (", the tie between them at the bottom, "
                                                                       "pointing inwards" if pat.has("tie") else "")
                + f". Sew round the curved edge with {sa} seam allowance; the top stays open.", section="Ear flaps",
                repeat=2),
        ST.icon("Turn the flaps", "turn", "Clip the curve, turn the flaps and press them flat.", section="Ear flaps"),
        ST.seam("Sew the hat", ["Side and crown seams"],
                f"Lay both hat halves right sides together and sew from one lower edge over the crown to the other "
                f"with {sa} seam allowance.", section="Hat"),
        ST.seam("Sew the lining", ["Lining side and crown seams"],
                "Sew the lining the same way, but leave 8 cm open in one side seam for turning.", section="Lining"),
        ST.place("Baste the flaps on", "flap", "hat", "Ear flap",
                 "Hat right side out: pin each flap onto the right side of the hat, centred over a side seam, raw "
                 "edges level, the flap pointing up. Baste close to the edge.", stitch="baste", section="Hat"),
        ST.seam("Sew hat and lining together", ["Lower edge"],
                "Put the hat into the lining, right sides together; the flaps lie between the layers. Match the side "
                f"seams and sew round the lower edge with {sa} seam allowance.", section="Finish"),
        ST.icon("Turn and close the opening", "turn",
                "Turn the hat through the opening in the lining. Close the opening with a ladder stitch and push "
                "the lining into the hat.", section="Finish"),
        ST.topstitch("Topstitch the lower edge", [("hat", "bottom")], 5.0,
                     "Optional: topstitch 5 mm from the lower edge and round the flaps.", section="Finish"),
        ST.done(""),
    ]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
