"""Dungarees: the pants block (trousers, joggers or shorts) with an elastic waistband, a faced bib
on the front waistband with a bib pocket, two straps from the back waistband crossing at the back
and buttoned onto the bib (adjustable), optional side openings. Woven (denim, corduroy) or sweat."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from . import _parts as PT
from . import pants_basic as PB
from ._common import clamp, is_adult

DEFAULTS = dict(style="trousers", fabric="woven", stretch=None, length="long", bib_pocket=True, sa=10.0,
                hem_sa=30.0, cuffs=None, pockets=None)
FINISHED_LABELS = dict(PB.FINISHED_LABELS, bib=("Bib height", "length"), strap=("Strap length", "length"))
FIT_CHECK = "does the bib reach the chest with the straps buttoned in the middle hole, and can the wearer squat?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    popts = {k: v for k, v in o.items() if k not in ("bib_pocket",)}
    popts.update(waistband="casing")
    if popts.get("pockets") is None:
        popts["pockets"] = ["side", "back_patch"]
    pat = PB.draft(m, popts)
    pat.garment = "dungarees"
    adult = is_adult(m)
    # bib: trapezoid on the fold, slightly narrower at the top
    wb = 0.36 * m["waist"] / 2
    wt = 0.32 * m["chest"] / 2
    h = clamp(0.62 * (m["back_length"] - 0.18 * m["chest"]), 90, 260)
    r = 15.0
    pts_top = G.join(G.quad(G.P(wt, h - r), G.P(wt, h), G.P(wt - r, h)), G.line(G.P(wt - r, h), G.P(0, h)))
    edges = [Edge("bottom", G.line(G.P(0, 0), G.P(wb, 0)), sa, label="Waistband seam"),
             Edge("side", G.line(G.P(wb, 0), G.P(wt, h - r)), sa, label="Bib edge"),
             Edge("top", pts_top, sa, label="Bib top edge"),
             Edge("center", G.line(G.P(0, h), G.P(0, 0)), 0.0, True, "Centre front (fold)")]
    bib = Piece("bib", "Bib", edges, cut_count=2, mirror=False, grain=(G.P(wb * 0.5, h * 0.2), G.P(wb * 0.5, h * 0.8)))
    bib.info.append("outer bib and facing")
    bs = PT.button_size(m) + 2
    bib.marks.append(Mark(G.line(G.P(wt - 25, h - 20), G.P(wt - 25, h - 20 - 1.0)), "mark", "Button"))
    pat.pieces.append(bib)
    pat.seams.append(dict(name="Bib round (outer ↔ facing)", a=[("bib", "side", 1), ("bib", "top", 1)],
                          b=[("bib", "side", 1), ("bib", "top", 1)], type="equal"))
    if o["bib_pocket"]:
        pw, ph = 0.55 * wb * 2, 0.5 * h
        pk = rect_piece("bib_pocket", "Bib pocket", pw, ph, sa=sa, cut_count=1,
                        labels=("Pocket edge", "Pocket edge", "Pocket opening (hem)", "Pocket edge"),
                        sas=(sa, sa, 20.0, sa))
        pk.edges[2].turned = True
        pat.pieces.append(pk)
        bib.marks.append(Mark(np.array([[0, h * 0.25], [pw / 2, h * 0.25], [pw / 2, h * 0.25 + ph],
                                        [0, h * 0.25 + ph]]), "placement", "Bib pocket"))
    # straps: from the back waistband over the shoulder to the bib, with 3 buttonholes to adjust
    sw = 35.0 if adult else 25.0
    sl = (m["back_length"] * 0.85 + h) * 1.05 + 80
    strap = rect_piece("strap", "Strap", 2 * sw, sl, sa=sa, cut_count=2,
                       labels=("Strap end (into the back waistband)", "Strap edge", "Strap end (buttonholes)",
                               "Strap edge"))
    strap.marks.append(Mark(G.line(G.P(sw, 0), G.P(sw, sl)), "fold", "Fold line"))
    for k in range(3):
        y = sl - 25 - k * 35
        strap.marks.append(Mark(G.line(G.P(sw / 2, y), G.P(sw / 2, y - bs)), "mark", "Buttonhole"))
    pat.pieces.append(strap)
    pat.seams.append(dict(name="Straps", a=[("strap", "right", 1)], b=[("strap", "left", 1)], type="equal"))
    front_top = pat.piece("front").edge("waistband").length * 2 + (
        pat.piece("side_panel").edge("waist_outer").length * 2 if pat.has("side_panel") else 0)
    pat.checks.append(dict(name="Bib sits on the front waistband", kind="range", value=2 * wb, lo=0.3 * m["waist"],
                           hi=min(0.5 * m["waist"], front_top), note="bib width at the waist"))
    pat.notes.append(f"Buttons: 2 buttons, {bs - 2:.0f} mm (or dungaree buckles)")
    pat.title = "Dungarees" if o["length"] in ("long", "7/8") else "Short dungarees"
    pat.options.update(bib_pocket=o["bib_pocket"], _bib_h=h)
    pat.finished["bib"] = h
    pat.finished["strap"] = sl
    return pat


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = []
    if pat.has("bib_pocket"):
        out += [ST.hem("Hem the bib pocket", [("bib_pocket", "top")], 20.0,
                       "Fold the top edge twice and topstitch it.", section="Bib"),
                ST.place("Stitch the bib pocket on", "bib_pocket", "bib", "Bib pocket",
                         "Press the other edges under and topstitch the pocket onto the outer bib.", section="Bib")]
    out += [ST.seam("Sew the bib", ["Bib round"],
                    f"Lay outer bib and facing right sides together and sew the sides and the top with {sa} seam "
                    "allowance. Clip the corners, turn, press and topstitch.", section="Bib"),
            ST.seam("Sew the straps", ["Straps"],
                    f"Fold each strap lengthwise right sides together and sew the long edge and the buttonhole end "
                    f"with {sa} seam allowance. Turn, press and topstitch.", section="Straps", repeat=2)]
    base = PB.assembly(pat)
    done = base.pop()
    for st in base:
        out.append(st)
        if st.title.startswith("Sew the waistband on"):
            out.append(ST.icon("Sew bib and straps on", "needle",
                               "Lay the bib onto the outside of the front waistband, centre on centre front, its "
                               "lower edge 1 cm over the band seam, and topstitch it on through all layers. "
                               "Cross the straps at the back and sew their ends onto the inside of the back "
                               "waistband, 4 cm from centre back each.", section="Waistband"))
    out += [ST.icon("Buttonholes and buttons", "button",
                    "Sew the buttonholes in the straps and the buttons at the top corners of the bib.",
                    section="Finish"), done]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
