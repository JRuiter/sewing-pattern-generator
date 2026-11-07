"""Skirt with elastic waistband: gathered (rectangles), A-line, circle skirt (quarter circle on the fold)."""
from __future__ import annotations

import math

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

DEFAULTS = dict(style="gathered", length="knee", fabric="woven", stretch=None, sa=10.0, hem_sa=25.0,
                waistband_height=None, gather=1.6, flare_deg=None, top_total=None, skirt_length=None)

FINISHED_LABELS = {"top_circ": ("Skirt width at top (ungathered)", "width"), "hem_circ": ("Hem width", "width"),
                   "length": ("Skirt length incl. waistband", "length"), "waist_relaxed": ("Waistband relaxed", "width")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    adult = m["height"] > 1650
    sa, hem_sa = o["sa"], o["hem_sa"]
    wb_h = o["waistband_height"] or (35.0 if adult else 30.0)
    knee_h = 0.285 * m["height"]
    L = o["skirt_length"] or {"mini": 0.75 * (m["side_length"] - knee_h), "knee": m["side_length"] - knee_h,
                              "midi": m["side_length"] - 0.2 * m["height"],
                              "maxi": m["side_length"] - 0.05 * m["height"]}[o["length"]]
    Lp = L - wb_h
    style = o["style"]
    pieces, seams, corners, checks = [], [], [], []
    if style == "gathered":
        top = o["top_total"] or max(m["hip"] * o["gather"], m["hip"] * 1.25)
        w = top / 4
        for key, name in (("front", "Front skirt"), ("back", "Back skirt")):
            p = rect_piece(key, name, w, Lp, sa=sa, fold_left=True, cut_count=1,
                           names=("hem", "side", "waistband", "center"),
                           labels=("Hem", "Side seam", "Waist (gather)", "Centre (fold)"),
                           sas=(hem_sa, sa, sa, 0.0))
            pieces.append(p)
        hem = top
    elif style == "a_line":
        top = o["top_total"] or m["hip"] * 1.10
        flare = math.radians(o["flare_deg"] or 12.0)
        w0 = top / 4
        for key, name in (("front", "Front skirt"), ("back", "Back skirt")):
            S0 = G.P(w0, 0)
            S1 = G.P(w0 + Lp * math.tan(flare), -Lp)
            sd = G.unit(S1 - S0)                      # side seam direction (downwards)
            perp_in = np.array([sd[1], -sd[0]])       # ⟂ side, towards the centre
            drop = Lp * (1 / math.cos(flare) - 1)     # hem lower at the centre
            rise = w0 * math.tan(flare) * 0.5         # waist lower at the centre
            H0, T0 = G.P(0, -Lp - drop), G.P(0, -rise)
            hem_c = G.tangent_curve(H0, (1, 0), S1, -perp_in, 0.4, 0.4)
            top_c = G.tangent_curve(S0, perp_in, T0, (-1, 0), 0.4, 0.4)
            edges = [
                Edge("center", G.line(T0, H0), 0.0, True, "Centre (fold)"),
                Edge("hem", hem_c, hem_sa, label="Hem", turned=True),
                Edge("side", G.line(S1, S0), sa, label="Side seam"),
                Edge("waistband", top_c, sa, label="Waist"),
            ]
            pieces.append(Piece(key, name, edges, cut_count=1, mirror=False,
                                grain=(G.P(w0 * 0.4, -Lp * 0.2), G.P(w0 * 0.4, -Lp * 0.8))))
        hem = 4 * pieces[0].edge("hem").length
    elif style == "circle":
        top = o["top_total"] or m["hip"] * 1.05
        r = top / (2 * math.pi)
        R = r + Lp
        for key, name in (("front", "Circle skirt front"), ("back", "Circle skirt back")):
            # quarter circle to the lower right of the centre: fold on the left (x = 0), side seam at the top (y = 0)
            t = np.linspace(-math.pi / 2, 0, 200)
            outer = np.stack([R * np.cos(t), R * np.sin(t)], 1)       # (0,-R) → (R,0)
            inner = np.stack([r * np.cos(t), r * np.sin(t)], 1)[::-1]  # (r,0) → (0,-r)
            edges = [
                Edge("center", G.line(G.P(0, -r), G.P(0, -R)), 0.0, True, "Centre (fold)"),
                Edge("hem", outer, 15.0, label="Hem (narrow)", turned=True),
                Edge("side", G.line(G.P(R, 0), G.P(r, 0)), sa, label="Side seam"),
                Edge("waistband", inner, sa, label="Waist"),
            ]
            pieces.append(Piece(key, name, edges, cut_count=1, mirror=False,
                                grain=(G.P(R * 0.08, -(r + (R - r) * 0.3)), G.P(R * 0.08, -(r + (R - r) * 0.7)))))
        hem = 2 * math.pi * R
    else:
        raise ValueError(f"Unknown skirt style {style}")
    top_len = 2 * sum(p.edge("waistband").length for p in pieces)
    band_len = top_len if style != "gathered" else max(m["hip"] * 1.05, m["waist"] * 1.0)
    band = rect_piece("waistband", "Waistband (elastic)", band_len / 2, 2 * wb_h, sa=sa, cut_count=1, fold_left=True,
                      labels=("Seam edge", "Cross seam", "Seam edge", "Centre"))
    band.marks.append(Mark(G.line(G.P(0, wb_h), G.P(band_len / 2, wb_h)), "fold", "Fold line"))
    pieces.append(band)
    if style == "gathered":
        seams.append(dict(name="Waistband ↔ skirt top edge (gathered)", a=[("front", "waistband", 2), ("back", "waistband", 2)],
                          b=[("waistband", "bottom", 2)], type="ratio", lo=1 / (o["gather"] + 0.4), hi=0.85,
                          note="the skirt is gathered (intended extra length)"))
    else:
        seams.append(dict(name="Waistband ↔ skirt top edge", a=[("front", "waistband", 2), ("back", "waistband", 2)],
                          b=[("waistband", "bottom", 2)], type="equal"))
    seams.insert(0, dict(name="Side seam front ↔ back", a=[("front", "side", 1)],
                         b=[("back", "side", 1)], type="equal"))
    corners += [dict(name="Hem ↔ side seam", piece="front", a="hem", b="side", target=90),
                dict(name="Side seam ↔ waist", piece="front", a="side", b="waistband", target=90),
                dict(name="Waist ↔ centre", piece="front", a="waistband", b="center", target=90)]
    elastic = m["waist"] * 0.9
    checks.append(dict(name="Waistband fits over the hip", kind="min", value=band_len, target=m["hip"] * 1.02,
                       note="waistband unstretched ≥ hip (the elastic gathers it)"))
    titles = {"gathered": "Gathered skirt", "a_line": "A-line skirt", "circle": "Circle skirt"}
    pat = Pattern("skirt", titles[style], "", pieces, dict(m), o, seams=seams, corners=corners, checks=checks,
                  notes=[f"Elastic {25 if not adult else 30} mm wide, length {elastic / 10:.0f} cm (+2 cm)"])
    pat.finished = dict(top_circ=top_len, hem_circ=hem, length=L, waist_relaxed=elastic)
    pat.options["_gap"] = 30.0                      # opening for threading the elastic
    return pat


def _cm_text(mm: float) -> str:
    return f"{mm / 10:g} cm" if mm >= 15 else f"{mm:.0f} mm"


def assembly(pat):
    """The construction as one-action steps (see steps.py)."""
    import steps as ST
    o = pat.options
    st = o["style"]
    knit = E.fabric_info(o["fabric"])[2]
    gap = o.get("_gap", 30.0)
    out = [ST.seam("Sew the side seams", ["Side seam"], "Front and back skirt right sides together.", repeat=2,
                   section="Skirt")]
    if ST.needs_finish(o, knit):
        out.append(ST.finish("Finish the side seams", [("front", "side"), ("back", "side")], repeat=2,
                             section="Skirt"))
    if st == "gathered":
        out.append(ST.gather("Gather the top edge", [("front", "waistband")],
                             "Two rows of the longest stitch; pull them up to the waistband length, spread the "
                             "gathers evenly.", section="Skirt"))
    sec = "Waistband"
    out += [
        ST.ring("Close the waistband into a ring", "waistband",
                f"Right sides together across the short ends (centre back); leave {_cm_text(gap)} open.",
                section=sec),
        ST.fold_band("Fold the waistband in half", "waistband", "Lengthwise, wrong sides together.", section=sec),
        ST.quarter("Mark quarters", "waistband", "skirt top edge", "Centre front, centre back, sides.",
                   section=sec, data={"quarters": "waist"}),
        ST.attach_band("Sew the waistband on", "waistband", ["Waistband"], "skirt top edge",
                       "Right sides together, raw edges meet, opening on the inside.", stretch=False, section=sec),
        ST.icon("Thread the elastic", "elastic", "With a safety pin; join the ends with an overlap.",
                stitch="elastic", section=sec),
        ST.icon("Close the opening", "hand", "Stitch the opening closed.", stitch="topstitch", section=sec),
    ]
    hs = pat.piece("front").edge("hem").sa
    if st == "circle":
        out += [ST.icon("Let the skirt hang for 24 h", "level", "Then level the hem: the bias stretches.",
                        section="Hem"),
                ST.hem("Sew a narrow hem", [("front", "hem"), ("back", "hem")], hs / 2,
                       f"Press under twice by {round(hs / 20, 2):g} cm.", section="Hem")]
    else:
        out.append(ST.hem("Sew the hem", [("front", "hem"), ("back", "hem")], hs,
                          "Press the allowance under twice and stitch.", section="Hem"))
    out.append(ST.done())
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
