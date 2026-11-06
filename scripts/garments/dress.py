"""Dress: T-shirt bodice + skirt, or a lengthened A-line T-shirt dress.

Styles
- `waist_seam` (default): the `tshirt_basic` bodice cut at the waist (+1 cm) and joined to a
  skirt from the `skirt` module (gathered, A-line or circle) at a waist seam. The skirt top
  is solved so that it matches the bodice waist exactly (A-line/circle) or by the gather
  ratio (gathered). Optional elastic in the waist seam, optional in-seam pockets.
- `shirt_dress`: the T-shirt lengthened to dress length with an A-line flare from below the
  underarm; the hem is curved so that it meets the side seam at a right angle.

Sleeve and neckline options are the T-shirt options (sleeve_style, sleeve_length,
neckline, sleeve_cuffs …).
"""
from __future__ import annotations

import math

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Notch, Pattern, Piece

from . import skirt as S
from . import tshirt_basic as T

DEFAULTS = dict(style="waist_seam", skirt="gathered", length="knee", fabric="jersey", gather=1.6,
                flare_cm=None, waist_elastic=True, pockets=False, sa=10.0, hem_sa=20.0)
TOP_KEYS = ("fit", "fabric", "stretch", "sleeve_style", "sleeve_length", "neckline", "band_fabric",
            "band_stretch", "sleeve_cuffs", "sa", "hem_sa", "neck_band_h", "chest_total",
            "sleeve_len_total", "sleeve_opening", "cuff_h", "construction", "notch_style",
            "seam_allowance", "units")
GATHER_RANGE = (1.0, 2.5)

FINISHED_LABELS = dict(T.FINISHED_LABELS, length=("Dress length from neck point", "length"),
                       waist_seam=("Waist seam (bodice)", "width"), skirt_top=("Skirt top edge (ungathered)", "width"),
                       hip_circ=("Width at the hip", "width"), skirt_length=("Skirt length", "length"))


def skirt_length(m, length) -> float:
    knee_h = 0.285 * m["height"]
    return {"mini": 0.75 * (m["side_length"] - knee_h), "knee": m["side_length"] - knee_h,
            "midi": m["side_length"] - 0.2 * m["height"],
            "maxi": m["side_length"] - 0.05 * m["height"]}[length]


def _top_options(o):
    top = {k: o[k] for k in TOP_KEYS if k in o and o[k] is not None}
    top["hem_band"] = False
    return top


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in ("waist_seam", "shirt_dress"):
        raise ValueError("dress style must be waist_seam or shirt_dress")
    m = measures
    Ls = skirt_length(m, o["length"])
    if o["style"] == "shirt_dress":
        pat = _shirt_dress(m, o, Ls)
    else:
        pat = _waist_seam(m, o, Ls)
    pat.options.update({k: o[k] for k in ("style", "skirt", "length", "gather", "waist_elastic", "pockets")})
    pat.title = "T-shirt dress" if o["style"] == "shirt_dress" else \
        {"gathered": "Dress with gathered skirt", "a_line": "Dress with A-line skirt",
         "circle": "Dress with circle skirt"}[o["skirt"]]
    return pat


# ---------------------------------------------------------------------------
# waist seam: bodice + skirt
# ---------------------------------------------------------------------------

def _waist_seam(m, o, Ls):
    adult = m["height"] > 1650 and m["chest"] > 780
    top = _top_options(o)
    top["body_length"] = m["back_length"] + 10.0
    pat = T.draft(m, top, _garment="dress")
    sa = pat.options["sa"]
    for key in ("front", "back"):
        h = pat.piece(key).edge("hem")
        h.sa, h.turned, h.label = sa, False, "Waist seam"
    pat.corners = [c for c in pat.corners if c.get("name") != "Body length plausible"]
    pat.checks = [c for c in pat.checks if c.get("name") != "Body length plausible"]
    waist = 2 * (pat.piece("front").edge("hem").length + pat.piece("back").edge("hem").length)
    style = o["skirt"]
    gather = float(o["gather"]) if style == "gathered" else 1.0
    target = waist * gather
    sk_opts = dict(style=style, fabric=o["fabric"], stretch=o.get("stretch"), sa=sa, hem_sa=o["hem_sa"],
                   skirt_length=Ls, waistband_height=1e-3, top_total=target)
    for _ in range(4):           # match the skirt top edge to the target exactly
        sk = S.draft(m, sk_opts)
        got = 2 * (sk.piece("front").edge("waistband").length + sk.piece("back").edge("waistband").length)
        sk_opts["top_total"] *= target / got
    sk = S.draft(m, sk_opts)
    skirt_pieces = []
    for p in sk.pieces:
        if p.key == "waistband":
            continue
        p.key = "skirt_" + p.key
        p.name = p.name.replace("Front skirt", "Skirt front").replace("Back skirt", "Skirt back") \
            .replace("Circle skirt front", "Skirt front (circle)").replace("Circle skirt back", "Skirt back (circle)")
        p.edge("waistband").label = "Waist seam" + (" (gather)" if style == "gathered" else "")
        skirt_pieces.append(p)
    pat.pieces += skirt_pieces
    if style == "gathered":
        lo, hi = 1 / GATHER_RANGE[1], 1 / GATHER_RANGE[0]
        pat.seams.append(dict(name="Waist seam bodice ↔ skirt (gathered)",
                              a=[("skirt_front", "waistband", 2), ("skirt_back", "waistband", 2)],
                              b=[("front", "hem", 2), ("back", "hem", 2)], type="ratio", lo=lo, hi=hi,
                              note=f"gather ratio {gather:g} (allowed {GATHER_RANGE[0]:g}–{GATHER_RANGE[1]:g})"))
    else:
        pat.seams.append(dict(name="Waist seam bodice ↔ skirt",
                              a=[("front", "hem", 2), ("back", "hem", 2)],
                              b=[("skirt_front", "waistband", 2), ("skirt_back", "waistband", 2)], type="equal"))
    pat.seams.append(dict(name="Skirt side seam front ↔ back", a=[("skirt_front", "side", 1)],
                          b=[("skirt_back", "side", 1)], type="equal"))
    pat.corners += [dict(name="Skirt hem ↔ side seam", piece="skirt_front", a="hem", b="side", target=90),
                    dict(name="Skirt side seam ↔ waist", piece="skirt_front", a="side", b="waistband", target=90),
                    dict(name="Skirt waist ↔ centre", piece="skirt_front", a="waistband", b="center", target=90)]
    _, stretch, knit = E.fabric_info(o["fabric"], o.get("stretch"))
    pat.checks.append(dict(name="Waist seam fits over the shoulders/chest", kind="min",
                           value=waist * (1 + stretch / 100 * 0.6), target=m["chest"] * 1.02,
                           note="pull-on dress without closure: waist seam incl. usable stretch ≥ chest"))
    if o["pockets"]:
        _pockets(pat, sa, adult)
    if o["waist_elastic"]:
        el = m["waist"] * 0.95
        pat.notes.append(f"Elastic for the waist seam: {10 if not adult else 15} mm wide, "
                         f"{el / 10:.0f} cm (+2 cm overlap).")
        pat.options["_elastic"] = el
    fin = dict(pat.finished)
    fin["length"] = fin["length"] + Ls
    fin.update(waist_seam=waist, skirt_top=2 * sum(pat.piece(k).edge("waistband").length
                                                   for k in ("skirt_front", "skirt_back")),
               hem_circ=sk.finished["hem_circ"], skirt_length=Ls)
    pat.finished = fin
    pat.checks.append(dict(name="Dress length plausible", kind="range", value=fin["length"],
                           lo=0.40 * m["height"], hi=0.90 * m["height"], note="from the neck point"))
    return pat


def _pockets(pat, sa, adult):
    k = max(0.75, min(1.45, pat.measures["height"] / 1220.0))
    op_top, op_len = 30.0 * k, 140.0 * k
    w, h = 140.0 * k, 190.0 * k
    # pocket bag: straight edge along the side seam (opening), rounded bag
    p0, p1 = G.P(0, 0), G.P(0, -h)
    mid = G.P(w, -h * 0.45)
    piece = Piece("pocket_bag", "In-seam pocket bag", [
        Edge("side", G.line(p0, p1), sa, label="Side seam (opening)"),
        Edge("bag_lower", G.tangent_curve(p1, (1, 0), mid, (0, 1), 0.55, 0.5), sa, label="Pocket bag seam"),
        Edge("bag_upper", G.tangent_curve(mid, (0, 1), p0, (-1, 0), 0.5, 0.55), sa, label="Pocket bag seam"),
    ], cut_count=4, mirror=True, fabric="Main fabric or cotton jersey",
        grain=(G.P(w * 0.4, -h * 0.25), G.P(w * 0.4, -h * 0.75)))
    piece.notches += [Notch("side", op_top - 10.0, 1)]
    pat.pieces.append(piece)
    for key in ("skirt_front", "skirt_back"):
        sp = pat.piece(key)
        n = 1 if key.endswith("front") else 2
        sp.notches += [Notch("side", -(op_top), n), Notch("side", -(op_top + op_len), n)]
    pat.notes.append(f"In-seam pockets: opening {op_len / 10:.0f} cm starting {op_top / 10:.0f} cm below the "
                     "waist seam (between the notches on the skirt side seams).")


# ---------------------------------------------------------------------------
# shirt dress: lengthened, A-line T-shirt
# ---------------------------------------------------------------------------

def _shirt_dress(m, o, Ls):
    top = _top_options(o)
    top["body_length"] = m["back_length"] + Ls
    pat = T.draft(m, top, _garment="dress")
    F = pat.options["_F"]
    q, AD = F["q"], F["AD"]
    hip_need = m["hip"] * (1 + max(F["be"], 0.06))
    default_extra = max(0.25 * F["Ct"], hip_need * 1.25 - F["Ct"])      # A-line: ≥ 25 % more at the hem
    extra = float(o["flare_cm"]) * 10 if o["flare_cm"] is not None else default_extra
    fl = extra / 4
    for key in ("front", "back"):
        pc = pat.piece(key)
        hem_y = float(pc.edge("hem").pts[0, 1])
        depth = -float(pc.edge("center").pts[0, 1])
        U = G.P(q, -AD)
        S1 = G.P(q + fl, hem_y)
        d_up = G.unit(U - S1)
        side = G.tangent_curve(S1, d_up, U, (0, 1), 0.35, 0.35)
        sdir = G.start_dir(side)                       # leaving the hem upwards
        perp_in = np.array([sdir[1], -sdir[0]])
        if perp_in[0] > 0:
            perp_in = -perp_in
        drop = fl * math.tan(math.atan2(abs(sdir[0]), abs(sdir[1]))) * 0.5
        H0 = G.P(0, hem_y - drop)
        hem = G.tangent_curve(H0, (1, 0), S1, -perp_in, 0.4, 0.4)
        pc.edge("side").pts = side
        pc.edge("hem").pts = hem
        pc.edge("center").pts = G.line(G.P(0, -depth), H0)
    y_hip = -(m["back_length"] + 0.11 * m["height"] * (1.0 if m["height"] > 1650 else 0.9))
    f, b = pat.piece("front"), pat.piece("back")
    hip_w = 2 * (G.width_at_y(f.seam_ring(), y_hip) + G.width_at_y(b.seam_ring(), y_hip))
    pat.checks.append(dict(name="Dress fits over the hip", kind="min", value=hip_w, target=m["hip"] * 1.04,
                           note="width at hip level ≥ hip + 4 %"))
    pat.checks = [c for c in pat.checks if c.get("name") != "Body length plausible"]
    fin = T.finished_measures(pat)
    fin.update(hip_circ=hip_w, skirt_length=Ls)
    pat.finished = fin
    pat.checks.append(dict(name="Dress length plausible", kind="range", value=fin["length"],
                           lo=0.40 * m["height"], hi=0.90 * m["height"], note="from the neck point"))
    pat.options["_flare_extra"] = extra
    return pat


def finished_measures(pat):
    return pat.finished


def sewing_steps(pat):
    o = pat.options
    base = [s for s in T.sewing_steps(pat) if not s.startswith(("**Hem:", "**Hem band", "Done"))]
    if o.get("style") == "shirt_dress":
        return base + ["**Hem:** press the hem allowance under (curved hem: ease in the fullness with steam) "
                       "and sew with a twin needle/coverstitch.", "Done! Press the seams."]
    knit = E.fabric_info(o["fabric"])[2]
    st = "with an overlocker or a narrow zigzag/stretch stitch" if knit else "with a straight stitch, then finish the edges"
    steps = list(base)
    if o.get("pockets"):
        steps.append("**In-seam pockets:** sew a pocket bag to each skirt side seam between the notches "
                     "(right sides together, 7 mm from the edge), press the bags outwards.")
    steps.append(f"**Skirt side seams:** sew skirt front and back right sides together {st}"
                 + (", pivoting around the pocket bags" if o.get("pockets") else "") + ".")
    if o.get("skirt") == "gathered":
        steps.append(f"**Gather the skirt:** run two gathering threads along the top edge and pull them up to "
                     f"the bodice waist (gather ratio {o.get('gather', 1.6):g}); spread the gathers evenly.")
    steps.append("**Waist seam:** pin the skirt right sides together to the bodice (side seams meet, centre "
                 f"front/back meet) and sew {st}.")
    if o.get("waist_elastic"):
        steps.append(f"**Elastic:** sew the elastic ({o['_elastic'] / 10:.0f} cm, joined into a ring) to the "
                     "waist seam allowance while stretching it evenly, then press the seam up.")
    steps += ["**Hem:** press the hem allowance under twice and stitch." if o.get("skirt") != "circle" else
              "**Hem:** let the dress hang for 24 h, level the hem, then sew a narrow hem.",
              "Done! Press the seams."]
    return steps
