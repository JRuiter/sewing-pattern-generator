"""Mittens (fleece or knit) from hand circumference and hand length: two layers per hand, the
thumb drawn in profile on the side (sewn round in one go), optional rib cuff. Babies get
thumbless mittens (`thumb: false`)."""
from __future__ import annotations

import numpy as np
from shapely import affinity
from shapely.geometry import Point
from shapely.ops import unary_union

import ease as E
import geometry as G
from pattern import Mark, Pattern, Piece, rect_piece

from ._common import clamp, edges_from_ring, hand_circ, hand_length, resolve, ring_of, rounded_rect, smooth

DEFAULTS = dict(fabric="fleece", stretch=None, thumb=None, cuff=True, cuff_cm=None, sa=6.0, hem_sa=15.0,
                hand_circ=None, hand_length=None, string=False)
FINISHED_LABELS = {"width": ("Width (flat)", "width"), "length": ("Length", "length")}
FIT_CHECK = "do the hands slip in easily, with 1–1.5 cm room at the fingertips and the thumb?"


def _hand(m: dict, o: dict) -> tuple[float, float, float]:
    L = hand_length(m, o)
    C = hand_circ(m, o)
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    # flat width: half the hand circumference + ease (fleece 18 %, knit 10 %) + room for the seam
    W = C / 2 * (1.10 if stretch >= 20 else 1.18) + 4
    return L, C, W


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    L, C, W = _hand(m, o)
    thumb = o["thumb"] if o["thumb"] is not None else m["height"] >= 800
    o["thumb"] = thumb
    sa = o["sa"]
    top = L * 1.06 + 8                    # room at the fingertips
    cuff_h = o["cuff_cm"] * 10 if o["cuff_cm"] else clamp(0.055 * m["height"], 45, 90)
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    # the hand must slip through the wrist: opening incl. half the stretch ≥ hand + 3 %
    wrist_w = max(m["wrist"] / 2 * 1.12, W * 0.82, C * 1.04 / 2 / (1 + (stretch if knit else 0) / 200) + 1)
    # palm and fingers: rounded top; the wrist narrows a little (fleece) and opens again to the hem
    body = rounded_rect(0, 0, W, top, W / 2 - 1)
    wrist_y = 0.0
    shapes = [body]
    y_hem = -0.5 * cuff_h if o["cuff"] else -cuff_h
    from shapely.geometry import box
    cuff_part = box((W - wrist_w) / 2, y_hem, (W + wrist_w) / 2, 20)
    shapes.append(cuff_part)
    if thumb:
        tl = 0.50 * L                     # thumb length from the crotch
        tw = 0.30 * C / 2 * 1.25 + 6      # flat thumb width
        th = Point(0, 0).buffer(1.0, 64)
        th = affinity.scale(th, tw / 2, tl / 2)
        th = affinity.rotate(th, 28, origin=(0, 0))
        th = affinity.translate(th, -tw * 0.1, 0.42 * L)
        shapes.append(th)
        shapes.append(rounded_rect(-tw * 0.15, 0.18 * L, W * 0.4, 0.5 * L, 6))
    shape = smooth(unary_union(shapes), 3.0)
    shape = shape.buffer(4, join_style=1).buffer(-4, join_style=1)       # soften the thumb crotch
    shape = unary_union([shape, box((W - wrist_w) / 2, y_hem, (W + wrist_w) / 2, y_hem + 25)])   # square hem corners
    ring = ring_of(shape, 1.5)
    ys = ring[:, 1]
    yb = ys.min()
    bottom = ring[np.abs(ys - yb) < 0.6]
    bl, br = bottom[np.argmin(bottom[:, 0])], bottom[np.argmax(bottom[:, 0])]
    hem_sa = sa if o["cuff"] else o["hem_sa"]
    tip = ring[np.argmax(ys)]
    edges = edges_from_ring(ring, [(bl, "wrist", hem_sa, "Cuff seam" if o["cuff"] else "Hem", not o["cuff"]),
                                   (br, "outline", sa, "Outline seam"), (tip, "outline_b", sa, "Outline seam")])
    pc = Piece("mitten", "Mitten", edges, cut_count=4, mirror=True, fabric="Main fabric",
               grain=(G.P(W * 0.6, top * 0.25), G.P(W * 0.6, top * 0.7)))
    pc.info.append("2 mirrored pairs (palm and back of each hand)")
    if knit:
        pc.stretch_dir = "Stretch direction: across the hand"
    pieces = [pc]
    seams = [dict(name="Outline seam", a=[("mitten", "outline", 1), ("mitten", "outline_b", 1)],
                  b=[("mitten", "outline", 1), ("mitten", "outline_b", 1)], type="equal")]
    w_open = G.length(pc.edge("wrist").pts) * 2
    if o["cuff"]:
        cl = max(m["wrist"] * 1.0, w_open * 0.78)
        cf = rect_piece("cuff", "Cuff", cl, 2 * cuff_h, sa=sa, cut_count=2, fabric="Rib knit",
                        labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"), grain_vertical=True)
        cf.marks.append(Mark(G.line(G.P(0, cuff_h), G.P(cl, cuff_h)), "fold", "Fold line"))
        cf.stretch_dir = "Stretch direction: round the wrist"
        pieces.append(cf)
        seams.append(dict(name="Cuff ↔ mitten (stretched)", a=[("mitten", "wrist", 2)], b=[("cuff", "bottom", 1)],
                          type="ratio", lo=0.72, hi=0.95))
    hand_through = w_open * (1 + (stretch if knit else 0) / 200)
    checks = [dict(name="Hand slips through the wrist opening", kind="min", value=hand_through, target=C * 1.02,
                   note="opening incl. half the stretch ≥ hand"),
              dict(name="Room at the fingertips", kind="range", value=top - L, lo=5, hi=40, note="1–3 cm")]
    if o["cuff"]:
        _, rib_stretch, _ = E.fabric_info("rib", None)
        checks.append(dict(name="Cuff goes over the hand", kind="min",
                           value=pieces[1].edge("bottom").length * (1 + rib_stretch / 100), target=C * 1.0,
                           note="cuff incl. stretch ≥ hand"))
    notes = []
    if o["string"]:
        notes.append(f"Cord: 1 piece of {(m['arm'] * 2 + 0.4 * m['chest']) / 10:.0f} cm (mitten string)")
    title = "Mittens" if thumb else "Baby mittens"
    pat = Pattern("mittens", title, "", pieces, dict(m), o, seams=seams, corners=[], checks=checks, notes=notes)
    pat.finished = dict(width=W, length=top - yb)
    del wrist_y
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("mitten").edge("outline").sa)
    thumb = pat.options.get("thumb")
    out = [ST.seam("Sew round the mittens", ["Outline seam"],
                   "Lay each mirrored pair right sides together, edges level, and pin. "
                   f"Sew round with {sa} seam allowance from wrist to wrist"
                   + (", slowly round the thumb." if thumb else "."), section="Mittens", repeat=2,
                   hint="Clip into the thumb crotch close to the seam." if thumb else
                   "Shorten the stitch a little round the fingertips."),
           ST.icon("Turn right side out", "turn",
                   "Turn both mittens; push the thumb out with a blunt pencil." if thumb else "Turn both mittens.",
                   section="Mittens")]
    if pat.has("cuff"):
        out += [ST.ring("Close the cuffs into rings", "cuff",
                        f"Fold each cuff crosswise right sides together and sew the short edges with {sa} seam "
                        "allowance.", section="Cuffs"),
                ST.fold_band("Fold the cuffs in half", "cuff",
                             "Fold each ring lengthwise wrong sides together, raw edges level.", section="Cuffs",
                             data={"hands": "fold"}),
                ST.attach_band("Sew the cuffs on", "cuff", ["Cuff"], "wrist opening",
                               "Slide the cuff over the mitten, raw edges level, cuff seam on the side seam. Pin at the "
                               f"quarters and sew with {sa} seam allowance, stretching only the cuff.", section="Cuffs",
                               repeat=2, data={"hands": "stretch"})]
    else:
        hs = pat.piece("mitten").edge("wrist").sa
        out.append(ST.hem("Hem the wrist", [("mitten", "wrist")], hs,
                          f"Fold the wrist edge {ST.cm(hs)} to the wrong side and sew it down; thread a narrow elastic "
                          "through if the mitten should hold better.", section="Mittens", repeat=2))
    if pat.notes:
        out.append(ST.icon("Sew on the mitten string", "hand",
                           "Sew the ends of the cord firmly to the inside of the cuffs. The cord runs through both "
                           "sleeves of the jacket.", stitch="hand", section="Finish"))
    out.append(ST.done(""))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
