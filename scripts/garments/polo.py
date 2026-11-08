"""Polo shirt (pique or jersey): T-shirt block with a half placket at centre front (two placket
strips, buttons), a knit collar (rib or self fabric, folded), short sleeves with rib cuffs or a
hem, optional side vents."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Mark, Pattern, rect_piece

from . import _parts as PT
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(fit="normal", fabric="jersey", stretch=25, sleeve_length="short", sleeve_cuffs=True,
                collar_fabric="rib", side_vents=False, buttons=None, sa=10.0, hem_sa=20.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, placket=("Placket length", "length"))
FIT_CHECK = "does the head slip through the open placket, and does the collar lie flat round the neck?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    top = {k: o[k] for k in ("fit", "fabric", "stretch", "sleeve_length", "sleeve_cuffs", "sa", "hem_sa",
                             "chest_total", "body_length", "construction", "machines", "notch_style") if k in o}
    top.update(neckline="round", hem_band=False, _auto_neck=99, band_fabric="rib")
    pat = T.draft(m, top, _garment="polo")
    pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
    pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    f, b = pat.piece("front"), pat.piece("back")
    for pc in (f, b):
        pc.edge("neckline").sa = sa * 0.7
    adult = is_adult(m)
    pw = 30.0 if adult else 22.0                       # finished placket width
    F = pat.options["_F"]
    pl = clamp(0.085 * m["height"], 90, 170)           # placket length below the neckline
    y0 = -F["fnd"]
    f.marks.append(Mark(np.vstack([G.P(0, y0), G.P(pw / 2, y0), G.P(pw / 2, y0 - pl), G.P(0, y0 - pl)]),
                        "placement", "Placket opening"))
    strip = rect_piece("placket", "Placket strip", 2 * pw, pl + 15, sa=sa, cut_count=2,
                       labels=("Bottom end", "Raw edge (folded in)", "Neckline end", "Placket seam"))
    strip.marks.append(Mark(G.line(G.P(pw, 0), G.P(pw, pl + 15)), "fold", "Fold line"))
    strip.info.append("interface one half; buttonholes in the right strip")
    PT.buttonholes(strip, pl - 10, 30, o["buttons"] or (2 if pl < 120 else 3), PT.button_size(m) * 0.8 + 3,
                   x=pw * 0.5, vertical=True)
    pat.pieces.append(strip)
    pat.seams.append(dict(name="Placket strips ↔ placket opening", a=[("placket", "left", 2)],
                          b=[("placket", "left", 2)], type="equal", note="sewn onto both edges of the slit"))
    neck_half = f.edge("neckline").length + b.edge("neckline").length
    pieces, info = PT.collar_pieces("polo", neck_half - pw / 2, m, sa * 0.7,
                                    fabric="Rib knit" if o["collar_fabric"] == "rib" else "Main fabric")
    pat.pieces += pieces
    pat.seams.append(dict(name="Collar ↔ neckline (slightly stretched)", a=[("front", "neckline", 2),
                                                                         ("back", "neckline", 2)],
                          b=[("collar", "bottom", 2)], type="ratio", lo=0.85, hi=1.0,
                          note="from placket centre to placket centre"))
    stretch = F["stretch"]
    neck_len = 2 * neck_half
    pat.checks.append(dict(name="Head fits through the open placket", kind="min",
                           value=neck_len * (1 + stretch / 100) + 2 * pl, target=m["head"] * 1.05,
                           note="neckline + both placket edges ≥ head + 5 %"))
    if o["side_vents"]:
        for pc in (f, b):
            y = float(pc.edge("hem").pts[0, 1])
            x = float(pc.edge("hem").pts[-1, 0])
            pc.marks.append(Mark(G.line(G.P(x - 2, y), G.P(x - 2, y + 60)), "mark", "Side vent"))
    pat.notes.append(f"Buttons: {len([mk for mk in strip.marks if mk.label == 'Buttonhole'])} buttons, "
                     f"{PT.button_size(m) * 0.8:.0f} mm; light interfacing for the placket strips")
    pat.title = "Polo shirt"
    pat.options.update(collar_fabric=o["collar_fabric"], side_vents=o["side_vents"])
    pat.finished["placket"] = pl
    return pat


def finished_measures(pat):
    return T.finished_measures(pat)


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = [ST.icon("Interface the placket", "interfacing",
                   "Iron light interfacing onto one half of each placket strip.", section="Prepare"),
           ST.seam("Sew the placket strips on", ["Placket strips"],
                   "Cut the front on the placket marking: down the middle and diagonally into the lower corners. "
                   f"Sew one strip right sides together onto each long edge of the opening with {sa} seam "
                   "allowance, up to the corner.", section="Placket"),
           ST.place("Close the placket", "placket", "front", "Placket opening",
                   "Fold each strip in half over its allowance and press. Lay the right strip over the left one, "
                   "push the lower ends and the little triangle to the inside and sew across them. Topstitch the "
                   "edges of the placket.", section="Placket")]
    base = T.assembly(pat, hem=True, neck=False, done=False)
    i = next(k for k, st in enumerate(base) if st.title in ("Set in the sleeves", "Sew side and sleeve seams"))
    collar = [ST.fold_band("Fold the collar", "collar",
                           "Fold the collar lengthwise right sides together and sew both ends; turn and press, raw "
                           "edges level.", section="Collar", data={"hands": "fold"}),
              ST.seam("Sew the collar on", ["Collar ↔ neckline"],
                             "Lay the collar onto the right side of the neckline, its ends at the middle of the "
                             "placket strips. Fold the placket strips back over it (right sides together) and sew "
                             f"with {sa} seam allowance, stretching the collar slightly. Turn the placket ends and "
                             "cover the allowance at the back with a strip of tape.", section="Collar")]
    out += base[:i] + collar + base[i:]
    out += [ST.icon("Sew buttonholes and buttons", "button",
                    "Sew the buttonholes on the marks of the right placket strip and the buttons on the left one.",
                    section="Finish"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
