"""Underwear (knit with elastane): briefs and boxer briefs.

Styles
- `briefs` (default): front and back on the fold, a lined gusset between them (sewn with the
  "burrito" method so no seam shows inside), elastic at the waist and the leg openings,
  stitched on and turned (or picot elastic). `leg_cut` normal / high / low; `rise` mid / low.
- `boxers`: boxer briefs: the leggings block cut short (`leg_length` in cm, default by size),
  a lined crotch gusset, an elastic casing waist and turned hems.
Negative ease at the hip: the fabric must have at least 30 % stretch with good recovery.
"""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Edge, Pattern, Piece

from . import pants_basic as PB
from ._common import clamp, is_adult

DEFAULTS = dict(style="briefs", fabric="jersey_elastane", stretch=None, leg_cut="normal", rise="mid",
                leg_length=None, sa=7.5, hem_sa=20.0)
FINISHED_LABELS = {"hip": ("Hip (unstretched)", "width"), "top": ("Top edge", "width"),
                   "crotch": ("Crotch length (front + gusset + back)", "length"),
                   "leg_opening": ("Leg opening", "width"), "side": ("Side seam", "length"),
                   "waist_elastic": ("Waist elastic", "width"), "leg_elastic": ("Leg elastic (each)", "width")}
FIT_CHECK = "does the waist elastic sit flat without rolling, and do the leg openings neither cut in nor gape?"


def _gusset(cwf: float, cwb: float, gl: float, sa: float) -> Piece:
    edges = [Edge("front", G.line(G.P(-cwf, 0), G.P(cwf, 0)), sa, label="Gusset front end"),
             Edge("side", G.tangent_curve(G.P(cwf, 0), (-0.25, 1), G.P(cwb, gl), (0.4, 1), 0.4, 0.4), sa,
                  label="Leg opening (elastic)", turned=True),
             Edge("back", G.line(G.P(cwb, gl), G.P(-cwb, gl)), sa, label="Gusset back end"),
             Edge("side_l", G.tangent_curve(G.P(-cwb, gl), (0.4, -1), G.P(-cwf, 0), (-0.25, -1), 0.4, 0.4), sa,
                  label="Leg opening (elastic)", turned=True)]
    pc = Piece("gusset", "Gusset", edges, cut_count=2, mirror=False,
               grain=(G.P(0, gl * 0.2), G.P(0, gl * 0.8)))
    pc.info.append("outer and lining (cotton jersey)")
    return pc


def _briefs(m: dict, o: dict) -> Pattern:
    sa = o["sa"]
    _, stretch, _knit = E.fabric_info(o["fabric"], o.get("stretch"))
    neg = 0.90 if stretch >= 40 else 0.94
    H = m["hip"] * neg
    cd = m["crotch_depth"]
    qf, qb = H / 4 * 0.94, H / 4 * 1.06
    low = o["rise"] == "low"
    rf, rb, gl = 0.62 * cd, 0.80 * cd, 0.42 * cd
    if low:
        rf, rb = rf - 0.12 * cd, rb - 0.12 * cd
    side = {"normal": 0.30, "high": 0.12, "low": 0.48}[o["leg_cut"]] * cd
    side = clamp(side, 15, 0.6 * rf)
    cwf = clamp(0.032 * m["hip"], 18, 34)
    cwb = clamp(0.065 * m["hip"], 30, 70)
    # front: centre fold → crotch → leg → side → top
    top_f = G.tangent_curve(G.P(qf, 0), (-1, 0.05), G.P(0, -8), (-1, 0), 0.35, 0.35)
    leg_f = G.tangent_curve(G.P(cwf, -rf), (0.1, 1), G.P(qf, -side), (1, 0.2), 0.55, 0.45)
    front = Piece("front", "Front", [
        Edge("center", G.line(G.P(0, -8), G.P(0, -rf)), 0.0, True, "Centre front (fold)"),
        Edge("crotch", G.line(G.P(0, -rf), G.P(cwf, -rf)), sa, label="Gusset seam"),
        Edge("leg", leg_f, sa, label="Leg opening (elastic)", turned=True),
        Edge("side", G.line(G.P(qf, -side), G.P(qf, 0)), sa, label="Side seam"),
        Edge("waist", top_f, sa, label="Top edge (elastic)", turned=True)],
        cut_count=1, mirror=False, grain=(G.P(cwf * 0.6, -20), G.P(cwf * 0.6, -rf * 0.85)))
    # back: more seat coverage, centre raised
    top_b = G.tangent_curve(G.P(qb, 0), (-1, 0), G.P(0, 15), (-1, 0), 0.35, 0.35)
    leg_b = G.tangent_curve(G.P(cwb, -rb), (0.35, 1), G.P(qb, -side), (1, -0.1), 0.45, 0.55)
    back = Piece("back", "Back", [
        Edge("center", G.line(G.P(0, 15), G.P(0, -rb)), 0.0, True, "Centre back (fold)"),
        Edge("crotch", G.line(G.P(0, -rb), G.P(cwb, -rb)), sa, label="Gusset seam"),
        Edge("leg", leg_b, sa, label="Leg opening (elastic)", turned=True),
        Edge("side", G.line(G.P(qb, -side), G.P(qb, 0)), sa, label="Side seam"),
        Edge("waist", top_b, sa, label="Top edge (elastic)", turned=True)],
        cut_count=1, mirror=False, grain=(G.P(cwb * 0.6, -10), G.P(cwb * 0.6, -rb * 0.85)))
    gus = _gusset(cwf, cwb, gl, sa)
    for pc in (front, back):
        pc.stretch_dir = "Stretch direction: across (around the body)"
    gus.stretch_dir = "Stretch direction: across"
    top = 2 * (front.edge("waist").length + back.edge("waist").length)
    leg = front.edge("leg").length + back.edge("leg").length + gus.edge("side").length
    we = clamp(min(top * 0.85, m["waist"] * 0.95 if not low else top * 0.85), 0.6 * m["hip"], top)
    le = leg * 0.85
    seams = [dict(name="Side seams", a=[("front", "side", 1)], b=[("back", "side", 1)], type="equal"),
             dict(name="Gusset ↔ front", a=[("front", "crotch", 2)], b=[("gusset", "front", 1)], type="equal"),
             dict(name="Gusset ↔ back", a=[("back", "crotch", 2)], b=[("gusset", "back", 1)], type="equal")]
    corners = [dict(name="Side ↔ top edge (front)", piece="front", a="side", b="waist", target=90),
               dict(name="Side ↔ top edge (back)", piece="back", a="side", b="waist", target=90),
               dict(name="Centre ↔ top edge (front)", piece="front", a="waist", b="center", target=90),
               dict(name="Centre ↔ top edge (back)", piece="back", a="waist", b="center", target=90)]
    crotch = rf + rb + gl + 8 + 15
    body_crotch = 2.1 * cd
    checks = [dict(name="Hip with negative ease", kind="range", value=2 * (qf + qb), lo=0.84 * m["hip"],
                   hi=0.98 * m["hip"], note="knit with elastane stretches to the body"),
              dict(name="Crotch length", kind="range", value=crotch, lo=0.7 * body_crotch, hi=1.0 * body_crotch,
                   note="front + gusset + back against the body crotch length (low rise sits lower)"),
              dict(name="Leg elastic", kind="range", value=le, lo=0.75 * leg, hi=0.92 * leg,
                   note="stretched slightly onto the leg opening")]
    if stretch < 30:
        checks.append(dict(name="Fabric stretch for underwear", kind="range", value=stretch, lo=30, hi=200,
                           note="at least 30 % stretch with good recovery"))
    ew = 10.0 if is_adult(m) else 8.0
    notes = [f"Elastic: waist {we / 10:.0f} cm ({ew + 2:.0f}–{ew + 10:.0f} mm plush or waistband elastic), "
             f"legs 2 × {le / 10:.0f} cm ({ew - 2:.0f}–{ew:.0f} mm, picot or lingerie elastic)",
             "Gusset lining: cotton jersey (breathable)"]
    gus.fabric = "Main fabric + cotton jersey"
    o = dict(o, _waist_elastic=we, _leg_elastic=le)
    pat = Pattern("underwear", "Briefs", "", [front, back, gus], dict(m), o, seams=seams, corners=corners,
                  checks=checks, notes=notes)
    pat.finished = dict(hip=2 * (qf + qb), top=top, crotch=crotch, leg_opening=leg, side=side,
                        waist_elastic=we, leg_elastic=le)
    return pat


def _boxers(m: dict, o: dict) -> Pattern:
    leg_cm = o["leg_length"] or clamp(0.16 * m["inseam"], 40, 160) / 10
    popts = dict(style="leggings", fit="slim", fabric=o["fabric"], stretch=o.get("stretch"), waistband="casing",
                 cuffs=False, pockets=[], length="short", inseam_total=leg_cm * 10, sa=o["sa"], hem_sa=o["hem_sa"])
    for k in ("machines", "construction", "notch_style"):
        if k in o:
            popts[k] = o[k]
    pat = PB.draft(m, popts)
    pat.garment = "underwear"
    pat.title = "Boxer briefs"
    cd = m["crotch_depth"]
    gl = 0.30 * cd
    cw = clamp(0.03 * m["hip"], 18, 32)
    g = Piece("gusset", "Crotch gusset (lining)", [
        Edge("front", G.line(G.P(-cw, 0), G.P(cw, 0)), 5.0, label="Gusset end", turned=True),
        Edge("side", G.line(G.P(cw, 0), G.P(cw, gl)), 5.0,
             label="Gusset edge (turned under)", turned=True),
        Edge("back", G.line(G.P(cw, gl), G.P(-cw, gl)), 5.0, label="Gusset end", turned=True),
        Edge("side_l", G.line(G.P(-cw, gl), G.P(-cw, 0)), 5.0,
             label="Gusset edge (turned under)", turned=True)],
        cut_count=1, mirror=False, fabric="Cotton jersey", grain=(G.P(0, gl * 0.2), G.P(0, gl * 0.8)))
    pat.pieces.append(g)
    pat.notes.append("Crotch gusset: cotton jersey, stitched over the crotch seam on the inside")
    pat.options.update(style="boxers", leg_length=leg_cm)
    pat.finished["leg_length"] = leg_cm * 10
    return pat


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in ("briefs", "boxers"):
        raise ValueError("underwear style must be briefs or boxers")
    if o["leg_cut"] not in ("normal", "high", "low") or o["rise"] not in ("mid", "low"):
        raise ValueError("leg_cut must be normal, high or low; rise must be mid or low")
    return _briefs(measures, o) if o["style"] == "briefs" else _boxers(measures, o)


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    if pat.options.get("style") == "boxers":
        base = PB.assembly(pat)
        done = base.pop()
        i = next((k for k, st in enumerate(base) if st.section and "aist" in st.section), len(base))
        gus = ST.icon("Stitch the gusset in", "needle",
                       "Press the gusset edges under, lay it on the inside over the crotch seam, centred, and "
                       "stitch it on all round with a narrow zigzag.", section="Crotch")
        return base[:i] + [gus] + base[i:] + [done]
    return [
        ST.seam("Sew the gusset to the front", ["Gusset ↔ front"],
                "Lay the outer gusset on the front right sides together and the gusset lining right side onto "
                f"the wrong side of the front (front between them). Sew through all three layers with {sa} seam "
                "allowance.", section="Gusset"),
        ST.seam("Sew the gusset to the back (burrito)", ["Gusset ↔ back"],
                "Pin the outer gusset to the back right sides together. Roll front and back up, wrap the lining "
                "around them and pin it to the back too. Sew through all layers, then pull everything out through "
                "the opening: no seam shows on the inside.", section="Gusset",
                hint="Roll the pieces tightly so they fit inside the gusset."),
        ST.seam("Sew the side seams", ["Side seams"],
                f"Sew front and back together at the sides with {sa} seam allowance.", section="Body"),
        ST.icon("Sew on the leg elastic", "elastic_on",
                "Divide the leg opening and the elastic into quarters. Sew the elastic onto the wrong side with a "
                "zigzag, stretching it evenly (a little more at the back), turn it in and topstitch with a zigzag "
                "or twin needle.", section="Leg openings", repeat=2),
        ST.icon("Sew on the waist elastic", "elastic_on",
                "Close the elastic into a ring, quarter it and the top edge, and sew it on the same way, "
                "stretching it to fit.", section="Waist"),
        ST.done("Press lightly with steam (no heat on the elastic)."),
    ]


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
