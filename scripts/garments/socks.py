"""Socks from foot length (and foot/ankle circumference), stretch-aware.

* ``profile`` (default, knit with elastane): two mirrored side pieces with a shaped heel curve
  (the sewn counterpart of a short-row heel), sewn along the front and along the back and sole.
* ``sole``: house socks (fleece, sweat, knit): two mirrored uppers and a separate sole, e.g.
  from anti-slip fabric.

Lengths: ankle, crew (default), knee. Top finish: turned hem or rib cuff.
"""
from __future__ import annotations

import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import edges_from_ring, foot_circ, foot_length, resolve, ring_of, smooth

DEFAULTS = dict(style="profile", fabric="jersey", stretch=None, length="crew", cuff=False, sa=6.0, hem_sa=20.0,
                foot_length=None, foot_circ=None)
FINISHED_LABELS = {"foot": ("Foot length", "length"), "leg": ("Leg height", "length")}
FIT_CHECK = "does the heel sit on the heel, and is there no fold over the instep?"
LEG = {"ankle": 0.05, "crew": 0.09, "knee": 0.24}         # leg height above the ankle, × body height


def _dims(m: dict, o: dict) -> dict:
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    FL = foot_length(m, o)
    FC = foot_circ(m, o)
    s = stretch if knit else 0
    # knits with good stretch: 8–10 % negative ease round the foot; non-stretch (fleece): + 6 %
    k = 0.90 if s >= 40 else 0.95 if s >= 20 else 1.06
    foot_w = FC * k / 2                      # flat width of the foot tube
    heel_diag = 1.38 * FC                    # heel → instep circumference the foot must pass
    ankle = m.get("ankle", 0.24 * m["hip"])
    leg_w = max(ankle * k / 2, heel_diag / (2 * (1 + 0.8 * s / 100)) * 1.0, foot_w * 1.02)
    if o["length"] not in LEG:
        raise ValueError("socks length must be ankle, crew or knee")
    LH = LEG[o["length"]] * m["height"]
    calf = ankle * 1.55
    top_w = max(leg_w, (ankle * 1.2 if o["length"] == "crew" else calf if o["length"] == "knee" else ankle) * k / 2)
    return dict(FL=FL * (0.97 if s >= 40 else 1.0), FC=FC, foot_w=foot_w, leg_w=leg_w, top_w=top_w, LH=LH,
                heel_diag=heel_diag, stretch=s, knit=knit, ankle_y=0.055 * m["height"])


def _profile(d: dict):
    """Side view: sole on y = 0, heel at x = 0, toe to the right; leg up from the heel."""
    FL, fw, lw, tw = d["FL"], d["foot_w"], d["leg_w"], d["top_w"]
    y_top = d["ankle_y"] + d["LH"]
    toe_r = fw * 0.42
    heel_out = 0.10 * lw                        # the heel bulges back
    top = G.line(G.P(tw - (tw - lw) * 0.0, y_top), G.P(0 - (tw - lw) * 0.0, y_top))
    # back seam: down the back of the leg, round the heel, along the sole to the toe
    x_back_top = -(tw - lw) * 0.5
    back = G.join(G.cubic(G.P(x_back_top, y_top), G.P(x_back_top * 0.4, y_top * 0.55), G.P(0, d["ankle_y"] * 1.6),
                          G.P(0, d["ankle_y"])),
                  G.cubic(G.P(0, d["ankle_y"]), G.P(-heel_out, d["ankle_y"] * 0.45), G.P(lw * 0.05, 0),
                          G.P(lw * 0.45, 0)),
                  G.line(G.P(lw * 0.45, 0), G.P(FL - toe_r, 0)))
    # front seam: from the toe tip over the instep up to the front of the leg
    toe_tip = G.P(FL, toe_r * 0.9)
    back = G.join(back, G.cubic(G.P(FL - toe_r, 0), G.P(FL - toe_r * 0.35, 0), G.P(FL, toe_r * 0.35), toe_tip))
    x_front_top = lw + (tw - lw) * 0.5
    y_j = min(max(d["ankle_y"] + fw * 0.55, fw * 1.25), y_top - 30)      # instep curve meets the leg
    front = G.join(G.cubic(toe_tip, G.P(FL, fw * 0.75), G.P(FL - toe_r, fw), G.P(FL - toe_r * 2.2, fw)),
                   G.cubic(G.P(FL - toe_r * 2.2, fw), G.P(lw + (FL - toe_r * 2.2 - lw) * 0.45, fw * 1.02),
                           G.P(lw, min(fw * 0.95, y_j - 5)), G.P(lw, y_j)),
                   G.cubic(G.P(lw, y_j), G.P(lw, min(max(y_top * 0.6, y_j + 15), y_top - 8)),
                           G.P(x_front_top, y_top * 0.8), G.P(x_front_top, y_top)))
    top = G.line(G.P(x_front_top, y_top), G.P(x_back_top, y_top))
    return top, back, front


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    if o["style"] not in ("profile", "sole"):
        raise ValueError("socks style must be profile or sole")
    m = measures
    d = _dims(m, o)
    sa = o["sa"]
    top_sa = sa if o["cuff"] else o["hem_sa"]
    pieces: list[Piece] = []
    seams: list[dict] = []
    if o["style"] == "profile":
        top, back, front = _profile(d)
        edges = [Edge("top", top, top_sa, label="Cuff seam" if o["cuff"] else "Hem", turned=not o["cuff"]),
                 Edge("back", back, sa, label="Back and sole seam"),
                 Edge("front", front, sa, label="Front seam")]
        pc = Piece("sock", "Sock", edges, cut_count=4, mirror=True, fabric="Main fabric",
                   grain=(G.P(d["leg_w"] * 0.5, d["ankle_y"] + d["LH"] * 0.25),
                          G.P(d["leg_w"] * 0.5, d["ankle_y"] + d["LH"] * 0.75)))
        pc.info.append("2 mirrored pairs")
        pieces.append(pc)
        seams += [dict(name="Front seam", a=[("sock", "front", 1)], b=[("sock", "front", 1)], type="equal"),
                  dict(name="Back and sole seam", a=[("sock", "back", 1)], b=[("sock", "back", 1)], type="equal")]
        key = "sock"
    else:
        # sole: heel and ball circles, smoothed hull
        FL = d["FL"]
        sole_shape = unary_union([Point(0.16 * FL, 0).buffer(0.135 * FL, 64), Point(0.68 * FL, 0).buffer(0.19 * FL, 64),
                                  Point(0.86 * FL, 0.01 * FL).buffer(0.14 * FL, 64)]).convex_hull
        sole_shape = smooth(sole_shape, 8.0)
        minx = sole_shape.bounds[0]
        from shapely import affinity
        sole_shape = affinity.translate(sole_shape, -minx, 0)
        sole_shape = affinity.scale(sole_shape, FL / (sole_shape.bounds[2] - sole_shape.bounds[0]), 1.0,
                                    origin=(0, 0))
        ring = ring_of(sole_shape, 1.0)
        per = G.length(np.vstack([ring, ring[:1]]))
        heel_pt = ring[np.argmin(ring[:, 0])]
        toe_pt = ring[np.argmax(ring[:, 0])]
        sole_edges = edges_from_ring(ring, [(heel_pt, "outline", sa, "Sole seam"), (toe_pt, "outline_b", sa,
                                                                                    "Sole seam")])
        sole = Piece("sole", "Sole", sole_edges, cut_count=2, mirror=False, fabric="Sole fabric (anti-slip)",
                     grain=(G.P(0.25 * FL, 0), G.P(0.75 * FL, 0)))
        half = per / 2
        lw, tw, fw = d["leg_w"], d["top_w"], d["foot_w"] * 0.85
        y_top = d["ankle_y"] + d["LH"]
        x_b = -(tw - lw) * 0.5
        x_f = lw + (tw - lw) * 0.5
        y_j = min(max(d["ankle_y"] + fw * 0.6, fw * 1.25), y_top - 30)
        lower = G.line(G.P(0, 0), G.P(half, 0))
        front = G.join(G.cubic(G.P(half, 0), G.P(half + fw * 0.3, fw * 0.5), G.P(half - fw * 0.2, fw),
                               G.P(half - fw * 0.9, fw)),
                       G.cubic(G.P(half - fw * 0.9, fw), G.P(lw + (half - fw * 0.9 - lw) * 0.45, fw * 1.02),
                               G.P(lw, min(fw * 0.95, y_j - 5)), G.P(lw, y_j)),
                       G.cubic(G.P(lw, y_j), G.P(lw, min(max(y_top * 0.6, y_j + 15), y_top - 8)),
                               G.P(x_f, y_top * 0.8),
                               G.P(x_f, y_top)))
        top = G.line(G.P(x_f, y_top), G.P(x_b, y_top))
        back = G.cubic(G.P(x_b, y_top), G.P(x_b * 0.4, y_top * 0.5), G.P(-0.06 * lw, d["ankle_y"]), G.P(0, 0))
        edges = [Edge("lower", lower, sa, label="Sole seam"), Edge("front", front, sa, label="Front seam"),
                 Edge("top", top, top_sa, label="Cuff seam" if o["cuff"] else "Hem", turned=not o["cuff"]),
                 Edge("back", back, sa, label="Back seam")]
        up = Piece("upper", "Upper", edges, cut_count=4, mirror=True, fabric="Main fabric",
                   grain=(G.P(lw * 0.5, y_top * 0.3), G.P(lw * 0.5, y_top * 0.8)))
        up.info.append("2 mirrored pairs")
        pieces += [up, sole]
        seams += [dict(name="Front seam", a=[("upper", "front", 1)], b=[("upper", "front", 1)], type="equal"),
                  dict(name="Back seam", a=[("upper", "back", 1)], b=[("upper", "back", 1)], type="equal"),
                  dict(name="Sole seam", a=[("upper", "lower", 2)],
                       b=[("sole", "outline", 1), ("sole", "outline_b", 1)], type="equal")]
        key = "upper"
    if d["knit"]:
        pieces[0].stretch_dir = "Stretch direction: round the foot (across)"
    if o["cuff"]:
        open_w = 2 * G.length(pieces[0].edge("top").pts)
        ch = 0.035 * m["height"]
        cl = open_w * 0.85
        cf = rect_piece("cuff", "Cuff", cl, 2 * ch, sa=sa, cut_count=2, fabric="Rib knit",
                        labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"))
        cf.marks.append(Mark(G.line(G.P(0, ch), G.P(cl, ch)), "fold", "Fold line"))
        pieces.append(cf)
        seams.append(dict(name="Cuff ↔ sock (stretched)", a=[(key, "top", 2)], b=[("cuff", "bottom", 1)],
                          type="ratio", lo=0.78, hi=0.92))
    s = d["stretch"]
    checks = [dict(name="Foot passes the heel", kind="min", value=2 * d["leg_w"] * (1 + 0.8 * s / 100),
                   target=d["heel_diag"] * 0.99, note="leg width incl. stretch ≥ heel–instep circumference"),
              dict(name="Sock length vs. foot", kind="range", value=d["FL"], lo=foot_length(m, o) * 0.94,
                   hi=foot_length(m, o) * 1.04, note="knits slightly shorter than the foot")]
    pat = Pattern("socks", "Socks" if o["style"] == "profile" else "House socks", "", pieces, dict(m), o,
                  seams=seams, corners=[], checks=checks)
    pat.finished = dict(foot=d["FL"], leg=d["LH"] + d["ankle_y"])
    return pat


def assembly(pat):
    import steps as ST
    key = "sock" if pat.has("sock") else "upper"
    sa = ST.cm(pat.piece(key).edge("front").sa)
    out = []
    if key == "sock":
        out += [ST.seam("Sew the front seam", ["Front seam"],
                        "Lay each mirrored pair right sides together. Sew the front seam from the top edge over the "
                        f"instep to the toe with {sa} seam allowance, stretching slightly.", section="Socks", repeat=2),
                ST.seam("Sew the back and sole seam", ["Back and sole seam"],
                        "Sew from the top edge down the back, round the heel and along the sole to the toe, "
                        f"with {sa} seam allowance.", section="Socks", repeat=2,
                        hint="Sew the heel curve slowly; stretch the fabric a little.")]
    else:
        out += [ST.seam("Sew front and back seams", ["Front seam", "Back seam"],
                        f"Lay each mirrored pair of uppers right sides together and sew the front seam and the back "
                        f"seam with {sa} seam allowance.", section="Socks", repeat=2),
                ST.seam("Sew the sole in", ["Sole seam"],
                        "Upper wrong side out: pin the sole right sides together into the lower edge, the back seam "
                        f"at the heel and the front seam at the toe. Sew round with {sa} seam allowance.",
                        section="Socks", repeat=2, hint="Clip the allowance of the upper at the toe and heel curves.")]
    out.append(ST.icon("Turn right side out", "turn", section="Socks"))
    if pat.has("cuff"):
        out += [ST.ring("Close the cuffs into rings", "cuff",
                        f"Fold each cuff crosswise right sides together and sew the short edges with {sa} seam "
                        "allowance.", section="Cuffs"),
                ST.fold_band("Fold the cuffs in half", "cuff",
                             "Fold each ring lengthwise wrong sides together, raw edges level.", section="Cuffs",
                             data={"hands": "fold"}),
                ST.attach_band("Sew the cuffs on", "cuff", ["Cuff"], "top edge",
                               "Slide the cuff over the sock, raw edges level, cuff seam on the back seam. Pin at the "
                               f"quarters and sew with {sa} seam allowance, stretching only the cuff.", section="Cuffs",
                               repeat=2, data={"hands": "stretch"})]
    else:
        hs = pat.piece(key).edge("top").sa
        out.append(ST.hem("Hem the top edge", [(key, "top")], hs,
                          f"Fold the top edge {ST.cm(hs)} to the wrong side and sew it down, stretching slightly.",
                          section="Socks", repeat=2))
    out.append(ST.done(""))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
