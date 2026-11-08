"""Five-finger gloves from the hand measurements (hand length and circumference; finger lengths
and widths follow from them by average proportions, or can be given).

* ``outline`` (default, fleece and knit): two layers per hand, thumb drawn in profile, sewn
  round in one go. The quickest glove to sew.
* ``fourchette``: back and palm of the same shape with narrow gussets (fourchettes) between the
  fingers and a separate thumb set into an opening in the palm. Fits closer, for knits and
  thin fleece.
"""
from __future__ import annotations

import math

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import arc, clamp, fillet, hand_circ, hand_length, resolve

DEFAULTS = dict(style="outline", fabric="fleece", stretch=None, cuff_cm=None, sa=None, hem_sa=15.0,
                hand_circ=None, hand_length=None, finger_lengths_cm=None)
FINISHED_LABELS = {"width": ("Width (flat)", "width"), "length": ("Length", "length")}
FIT_CHECK = "do all fingers reach the tips with a few millimetres to spare, and does the hand slip in easily?"
# finger lengths (crotch to tip) as a fraction of the hand length: index, middle, ring, little
FINGER_LEN = (0.37, 0.42, 0.39, 0.31)
# finger circumference as a fraction of the hand circumference (knuckles)
FINGER_CIRC = (0.31, 0.32, 0.30, 0.26)
CROTCH_Y = (0.555, 0.57, 0.555, 0.50)    # height of each finger base (crotch) above the wrist, × hand length


def _fingers(m: dict, o: dict, gap: float, ease: float):
    L, C = hand_length(m, o), hand_circ(m, o)
    lens = [float(v) * 10 for v in o["finger_lengths_cm"]] if o["finger_lengths_cm"] else [f * L for f in FINGER_LEN]
    fourchette = o["style"] == "fourchette"
    ws = []
    for k in FINGER_CIRC:
        fc = k * C
        # outline: half the finger + ease; fourchette: the gusset adds the finger's thickness
        # (a finger is roughly round: flat width ≈ its diameter, the gusset ≈ 0.18 × its circumference)
        ws.append(fc / 2 * (1 + ease) + 2 if not fourchette else fc * 0.32 * (1 + ease))
    return L, C, lens, ws


def _outline(m: dict, o: dict):
    """The hand outline as named, counter-clockwise edges (see module doc)."""
    fourchette = o["style"] == "fourchette"
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    ease = 0.04 if stretch >= 20 else 0.12
    # space between the fingers on the pattern: room for both seam allowances
    gap = 2 * o["sa"] + 1
    L, C, lens, ws = _fingers(m, o, gap, ease)
    span = sum(ws) + 3 * gap
    W = C / 2 * (1 + ease) + (0 if not fourchette else 8)       # palm width at the knuckles
    cuff_h = o["cuff_cm"] * 10 if o["cuff_cm"] else clamp(0.06 * m["height"], 50, 90)
    wrist_w = max(m["wrist"] / 2 * (1.10 if knit else 1.25), W * 0.85,
                  C * 1.04 / 2 / (1 + (stretch if knit else 0) / 200) + 1)
    # finger 0 (index) on the left at x0; the little finger on the right
    x0 = (W - span) / 2
    xs = []
    x = x0
    for w in ws:
        xs.append((x, x + w))
        x += w + gap
    ys = [c * L for c in CROTCH_Y]
    sa = o["sa"]
    hem = o["hem_sa"]
    yw = -cuff_h
    r_gap = gap / 2
    pts_wrist = G.line(G.P((W - wrist_w) / 2, yw), G.P((W + wrist_w) / 2, yw))
    # right side: wrist → base of the little finger (outer side)
    xr, yr = xs[3][1], ys[3]
    side_r = G.join(G.line(G.P((W + wrist_w) / 2, yw), G.P((W + wrist_w) / 2, 0)),
                    G.cubic(G.P((W + wrist_w) / 2, 0), G.P((W + wrist_w) / 2, yr * 0.45),
                            G.P(xr, yr * 0.55), G.P(xr, yr - 2)))
    edges: list[Edge] = []
    edges.append(Edge("wrist", pts_wrist, hem, label="Hem", turned=True))
    side_r = G.join(side_r, G.line(G.P(xr, yr - 2), G.P(xr, yr + lens[3] - ws[3] / 2)))
    edges.append(Edge("outer_r", side_r, sa, label="Outer seam"))
    # fingers from the little finger (3) to the index finger (0)
    for i in (3, 2, 1, 0):
        xl_, xr_ = xs[i]
        w = ws[i]
        top = ys[i] + lens[i]
        tip = arc((xl_ + xr_) / 2, top - w / 2, w / 2, 0, 180, 1.0)
        edges.append(Edge(f"tip_{i}", tip, sa, label="Fingertip"))
        if i > 0:
            # inner side of finger i (down), crotch, inner side of finger i-1 (up)
            xl_prev = xs[i - 1][1]
            yb = max(ys[i], ys[i - 1])
            down = G.line(G.P(xl_, top - w / 2), G.P(xl_, yb + r_gap))
            crotch = arc((xl_ + xl_prev) / 2, yb + r_gap, r_gap, 0, -180, 0.5)
            top_prev = ys[i - 1] + lens[i - 1]
            up = G.line(G.P(xl_prev, yb + r_gap), G.P(xl_prev, top_prev - ws[i - 1] / 2))
            edges.append(Edge(f"gap_{i - 1}", G.join(down, crotch, up), sa, label="Between the fingers"))
    # left side: index finger outer side down → thumb (outline style) → wrist
    xl0 = xs[0][0]
    top0 = ys[0] + lens[0]
    left = [G.line(G.P(xl0, top0 - ws[0] / 2), G.P(xl0, ys[0]))]
    if not fourchette:
        tl, tw = 0.47 * L, 0.36 * C / 2 * (1 + ease) + 3
        # thumb in profile: leaves the hand at 0.48 L, angled outwards by 44°
        a = math.radians(44)
        base_top = G.P(min(xl0, (W - wrist_w) / 2) - 2, 0.33 * L)
        d = np.array([-math.sin(a), math.cos(a)])           # thumb axis (up and to the left)
        n = np.array([-math.cos(a), -math.sin(a)])          # thumb width direction (outwards/down)
        p_top = base_top
        t_tip_c = p_top + d * (tl - tw / 2) + n * tw / 2
        side1 = G.line(p_top, p_top + d * (tl - tw / 2))
        ang0 = math.degrees(math.atan2(-n[1], -n[0]))
        tip = arc(t_tip_c[0], t_tip_c[1], tw / 2, ang0, ang0 + 180, 1.0)
        p_low = p_top + n * tw
        side2 = G.line(tip[-1], p_low + d * 6)
        crotch_low = G.P((W - wrist_w) / 2, 0.10 * L)
        down_in = G.cubic(p_low + d * 6, p_low - d * 8, crotch_low + G.P(-2, 12), crotch_low)
        left.append(G.cubic(G.P(xl0, ys[0]), G.P(xl0, ys[0] - 0.1 * L), p_top + G.P(4, 10), p_top))
        left += [side1, tip, side2, down_in, G.line(crotch_low, G.P((W - wrist_w) / 2, yw))]
        edges.append(Edge("outer_l", fillet(G.join(*left), p_top, 16.0), sa, label="Outer seam"))
    else:
        left.append(G.cubic(G.P(xl0, ys[0]), G.P(xl0, ys[0] * 0.5), G.P((W - wrist_w) / 2, ys[0] * 0.4),
                            G.P((W - wrist_w) / 2, 0)))
        left.append(G.line(G.P((W - wrist_w) / 2, 0), G.P((W - wrist_w) / 2, yw)))
        edges.append(Edge("outer_l", G.join(*left), sa, label="Outer seam"))
    # the outline is drawn clockwise above (wrist left→right, then the fingers right→left): fine,
    # the wrist runs left to right and the rest comes back over the top, i.e. counter-clockwise
    return edges, dict(L=L, C=C, W=W, ws=ws, lens=lens, xs=xs, ys=ys, cuff_h=cuff_h, wrist_w=wrist_w, ease=ease)


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    if o["style"] not in ("outline", "fourchette"):
        raise ValueError("gloves style must be outline or fourchette")
    o["sa"] = o["sa"] if o["sa"] is not None else 4.0
    m = measures
    edges, info = _outline(m, o)
    L, C = info["L"], info["C"]
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    sa = o["sa"]
    hand = Piece("hand", "Glove", edges, cut_count=4, mirror=True, fabric="Main fabric",
                 grain=(G.P(info["W"] / 2, -info["cuff_h"] * 0.6), G.P(info["W"] / 2, 0.35 * L)))
    hand.info.append("2 mirrored pairs (back and palm of each hand)")
    if knit:
        hand.stretch_dir = "Stretch direction: across the hand"
    pieces = [hand]
    seams = [dict(name="Fingertips", a=[("hand", f"tip_{i}", 1) for i in range(4)],
                  b=[("hand", f"tip_{i}", 1) for i in range(4)], type="equal"),
             dict(name="Outer seams", a=[("hand", "outer_r", 1), ("hand", "outer_l", 1)],
                  b=[("hand", "outer_r", 1), ("hand", "outer_l", 1)], type="equal")]
    if o["style"] == "outline":
        seams.append(dict(name="Between the fingers", a=[("hand", f"gap_{i}", 1) for i in range(3)],
                          b=[("hand", f"gap_{i}", 1) for i in range(3)], type="equal"))
    else:
        fw = 0.18 * np.mean(FINGER_CIRC[:3]) * C * (1 + info["ease"])     # gusset: the finger's side
        for i in range(3):
            gl = G.length(hand.edge(f"gap_{i}").pts)
            f = rect_piece(f"fourchette_{i}", f"Fourchette {i + 1}", fw, gl, sa=sa, cut_count=2,
                           names=("end_a", "right", "end_b", "left"),
                           labels=("Gusset tip", "Gusset side", "Gusset tip", "Gusset side"))
            f.info.append("1 per hand")
            pieces.append(f)
            seams.append(dict(name=f"Fourchette {i + 1} ↔ back", a=[("hand", f"gap_{i}", 1)],
                              b=[(f"fourchette_{i}", "right", 1)], type="equal"))
            seams.append(dict(name=f"Fourchette {i + 1} ↔ palm", a=[("hand", f"gap_{i}", 1)],
                              b=[(f"fourchette_{i}", "left", 1)], type="equal"))
        # thumb: a folded profile piece; its base is set into an oval opening in the palm
        tw = 0.36 * C * (1 + info["ease"]) / 2 + 3
        tl = 0.47 * L
        x0 = 0.0
        thumb_edges = [Edge("base", G.line(G.P(x0, 0), G.P(x0 + tw, 0)), sa, label="Thumb base"),
                       Edge("outline", G.line(G.P(tw, 0), G.P(tw, tl - tw / 2)), sa, label="Thumb seam"),
                       Edge("outline_tip", arc(tw / 2, tl - tw / 2, tw / 2, 0, 180, 1.0), sa, label="Thumb seam"),
                       Edge("outline_l", G.line(G.P(0, tl - tw / 2), G.P(0, 0)), sa, label="Thumb seam")]
        th = Piece("thumb", "Thumb", thumb_edges, cut_count=4, mirror=True, fabric="Main fabric",
                   grain=(G.P(tw / 2, tl * 0.15), G.P(tw / 2, tl * 0.6)))
        th.info.append("2 per hand")
        pieces.append(th)
        th_all = [("thumb", "outline", 1), ("thumb", "outline_tip", 1), ("thumb", "outline_l", 1)]
        seams.append(dict(name="Thumb seam", a=th_all, b=th_all, type="equal"))
        # oval opening on the palm (template, palm pieces only): circumference = 2 × thumb base
        oc = 2 * tw
        a_ = oc / (2 * math.pi) * 1.25
        b_ = oc / (2 * math.pi) * 0.75
        cx, cy = (info["W"] - info["wrist_w"]) / 2 + a_ + 10, 0.30 * L
        t = np.linspace(0, 2 * math.pi, 120)
        oval = np.column_stack([cx + a_ * np.cos(t), cy + b_ * np.sin(t)])
        hand.marks.append(Mark(oval, "mark", "Thumb opening (palm only): cut out on the line", template=True))
        oval_len = G.length(oval)
        seams.append(dict(name="Thumb ↔ opening in the palm", a=[("thumb", "base", 2)], b=[], type="equal",
                          _len=oval_len))
        seams.pop()          # the opening is a marked line, not an edge: checked below
        checks_extra = [dict(name="Thumb base fits the opening", kind="range", value=2 * tw, lo=oval_len - 3,
                             hi=oval_len + 3, note="opening is cut after tracing")]
    open_w = info["wrist_w"] * 2
    checks = [dict(name="Hand slips through the wrist", kind="min",
                   value=open_w * (1 + (stretch if knit else 0) / 200), target=C * 1.02,
                   note="opening incl. half the stretch ≥ hand"),
              dict(name="Middle finger length incl. room", kind="range",
                   value=info["lens"][1] + 0, lo=info["lens"][1] * 0.98, hi=info["lens"][1] * 1.1,
                   note="finger length + 3–5 mm room")]
    if o["style"] == "fourchette":
        checks += checks_extra
    ys_all = np.vstack([e.pts for e in edges])[:, 1]
    xs_all = np.vstack([e.pts for e in edges])[:, 0]
    pat = Pattern("gloves", "Gloves", "", pieces, dict(m), o, seams=seams, corners=[], checks=checks)
    pat.finished = dict(width=float(np.ptp(xs_all)), length=float(np.ptp(ys_all)))
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("hand").edge("outer_r").sa)
    hs = pat.piece("hand").edge("wrist").sa
    out = []
    if pat.options["style"] == "outline":
        out += [ST.seam("Sew round the gloves", ["Fingertips", "Outer seams", "Between the fingers"],
                        "Lay each mirrored pair right sides together, edges level, and pin between the fingers. "
                        f"Sew round with {sa} seam allowance and a short stitch (2 mm), from wrist to wrist.",
                        section="Gloves", repeat=2,
                        hint="Pivot at each finger crotch with the needle down, then clip into the crotch close to "
                             "the seam."),
                ST.icon("Turn right side out", "turn",
                        "Turn the gloves; push every finger out with a blunt pencil or a chopstick.", section="Gloves")]
    else:
        out += [ST.icon("Cut the thumb openings", "cut",
                        "Trace the oval thumb opening onto the two palm pieces (not the back pieces) and cut it out "
                        "on the line.", section="Prepare"),
                ST.seam("Sew the thumbs", ["Thumb seam"],
                        f"Lay each thumb pair right sides together and sew the curved edge with {sa} seam "
                        "allowance.", section="Thumb", repeat=2),
                ST.place("Set in the thumbs", "thumb", "hand", "Thumb opening (palm only): cut out on the line",
                         "Thumb wrong side out, palm right side up: push the thumb through the opening from the right "
                         f"side and sew its base to the opening with {sa} seam allowance, the thumb seam towards the "
                         "index finger.", stitch="seam", section="Thumb", repeat=2),
                ST.seam("Sew the fourchettes to the back", [f"Fourchette {i + 1} ↔ back" for i in range(3)],
                        "Pin one long edge of each fourchette right sides together to the sides between two fingers of "
                        f"the back piece, the tip in the crotch. Sew with {sa} seam allowance.", section="Fingers",
                        repeat=2, hint="Sew each side from the crotch towards the fingertip."),
                ST.seam("Sew the palm on", [f"Fourchette {i + 1} ↔ palm" for i in range(3)] + ["Fingertips",
                                                                                               "Outer seams"],
                        "Lay the palm right sides together onto the back. Sew the other edges of the fourchettes to "
                        f"the palm, then round the fingertips and the outer seams, all with {sa} seam allowance.",
                        section="Fingers", repeat=2),
                ST.icon("Turn right side out", "turn",
                        "Turn the gloves; push every finger out with a blunt pencil or a chopstick.", section="Gloves")]
    out += [ST.hem("Hem the wrist", [("hand", "wrist")], hs,
                   f"Fold the wrist edge {ST.cm(hs)} to the wrong side and sew it down, stretching slightly.",
                   section="Finish", repeat=2),
            ST.done("")]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
