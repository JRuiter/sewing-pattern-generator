"""Cardigan (knit): T-shirt block opened at centre front, V or round neckline, one continuous
button band from hem to hem round the neck (cut on the fold at centre back), rib cuffs and an
open hem band, optional patch pockets."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Mark, Pattern, rect_piece

from . import _parts as PT
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(fit="normal", fabric="sweat", stretch=None, neckline="v", sleeve_length="long", sleeve_cuffs=True,
                hem_band=True, band_fabric="main", pockets=True, buttons=None, sa=10.0, hem_sa=20.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, band=("Button band width", "length"))
FIT_CHECK = "does it close over the chest without the band gaping, and do the sleeves end at the wrist?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    top: dict = {k: o[k] for k in ("fit", "fabric", "stretch", "sleeve_length", "sleeve_cuffs", "sa", "hem_sa",
                             "chest_total", "body_length", "construction", "machines", "notch_style", "hem_band",
                             "neckline") if k in o}
    top.update(_auto_neck=99, band_fabric="rib", neck_extra=10.0 if o["neckline"] == "round" else 0.0)
    pat = T.draft(m, top, _garment="cardigan")
    pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
    pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    f, b = pat.piece("front"), pat.piece("back")
    ce = f.edge("center")
    ce.fold, ce.sa, ce.label = False, sa, "Front edge (band)"
    f.cut_count, f.mirror, f.name = 2, True, "Front (left and right)"
    pat.corners = [c for c in pat.corners if not (c.get("piece") == "front" and "center" in (c.get("a"), c.get("b")))]
    for pc in (f, b):
        pc.edge("neckline").sa = sa
        pc.edge("neckline").pointed = False
    hb_h = pat.options.get("_hem_band_h", 0.0) if pat.has("hem_band") else 0.0
    if pat.has("hem_band"):
        hb = pat.piece("hem_band")
        hb.edge("right").label = "Front end (band)"
        hb.info.append("ends at the button band: not sewn into a ring")
    bw = 30.0 if is_adult(m) else 22.0
    edge_len = ce.length + f.edge("neckline").length + b.edge("neckline").length
    ratio = 0.95
    L = edge_len * ratio + hb_h
    band = rect_piece("button_band", "Button band", L, 2 * bw, sa=sa, cut_count=1, fold_left=True,
                      fabric="Rib knit" if o["band_fabric"] == "rib" else "Main fabric",
                      labels=("Seam edge", "Band end (hem)", "Seam edge", "Centre back"))
    band.marks.append(Mark(G.line(G.P(0, bw), G.P(L, bw)), "fold", "Fold line"))
    band.info.append("interface the front part of one half (buttons and buttonholes)")
    band.stretch_dir = "Stretch direction: along the length"
    # buttonholes: across the band, on the part that runs along the front edge
    front_part = ce.length * ratio
    x_hi, x_lo = L - hb_h * ratio - 15.0, L - front_part - hb_h * ratio + clamp(0.02 * m["height"], 20, 40)
    n = o["buttons"] or max(3, int(round((x_hi - x_lo) / 85)) + 1)
    bs = PT.button_size(m)
    for x in np.linspace(x_lo, x_hi, n):
        band.marks.append(Mark(G.line(G.P(x, bw / 2 - bs / 2 - 1.5), G.P(x, bw / 2 + bs / 2 + 1.5)), "mark",
                               "Buttonhole"))
    pat.pieces.append(band)
    refs = [("front", "center", 2), ("front", "neckline", 2), ("back", "neckline", 2)]
    pat.seams.append(dict(name="Button band ↔ front edges and neckline (slightly stretched)", a=refs,
                          b=[("button_band", "bottom", 2)], type="ratio", lo=0.9, hi=1.0 + 1.05 * hb_h / edge_len,
                          note="plus the ends of the hem band"))
    if o["pockets"]:
        F = pat.options["_F"]
        pw = clamp(0.14 * m["chest"], 90, 160)
        ph = pw * 1.05
        pk = rect_piece("pocket", "Patch pocket", pw, ph, sa=sa, cut_count=2,
                        labels=("Pocket edge", "Pocket edge", "Pocket opening (hem)", "Pocket edge"),
                        sas=(sa, sa, 25.0, sa))
        pk.edges[2].turned = True
        pat.pieces.append(pk)
        hem_y = float(f.edge("hem").pts[0, 1])
        x0, y0 = F["q"] * 0.3, hem_y + 25
        f.marks.append(Mark(np.array([[x0, y0], [x0 + pw, y0], [x0 + pw, y0 + ph], [x0, y0 + ph]]),
                            "placement", "Patch pocket"))
    pat.notes.append(f"Buttons: {n} buttons, {bs:.0f} mm; light iron-on interfacing strip for the button band")
    pat.title = "Cardigan"
    pat.options.update(band_fabric=o["band_fabric"], pockets=o["pockets"], _buttons=n)
    pat.finished["band"] = bw
    return pat


def finished_measures(pat):
    return T.finished_measures(pat)


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = []
    if pat.has("pocket"):
        out += [ST.hem("Hem the pocket openings", [("pocket", "top")], 25.0,
                       "Fold the top edge 2.5 cm to the wrong side and stitch it down.", section="Pockets", repeat=2),
                ST.place("Stitch the pockets on", "pocket", "front", "Patch pocket",
                         "Press the other edges 1 cm under, pin each pocket on its marking and topstitch it close "
                         "to the edge.", section="Pockets", repeat=2)]
    out += T.assembly(pat, hem=True, neck=False, done=False, open_bands=True)
    n = pat.options.get("_buttons", 5)
    out += [ST.icon("Interface the button band", "interfacing",
                    "Iron a strip of interfacing onto the front parts of one half of the band.", section="Band"),
            ST.fold_band("Fold the button band in half", "button_band",
                         "Fold the band lengthwise wrong sides together, raw edges level, and press.",
                         section="Band", data={"hands": "fold"}),
            ST.seam("Sew the button band on", ["Button band"],
                    "Pin the band onto the right side of the front edges and the neckline, centre back on the "
                    "back neck, the ends level with the hem. Sew from hem to hem with "
                    f"{sa} seam allowance, stretching the band slightly round the neck. Press the allowance towards "
                    "the body and topstitch it down.", section="Band"),
            ST.icon("Sew buttonholes and buttons", "button",
                    f"Sew {n} buttonholes on the marks of the right band (women) or the left band (men) and the "
                    "buttons opposite them.", section="Finish"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
