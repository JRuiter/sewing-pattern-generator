"""Pants block: jogger, harem pants, leggings, pull-on trousers.

Original parametric draft following the general principles of pants block drafting
(hip width split into quarters, front leg narrower than back leg, crotch extension
front ≈ 1/20 and back ≈ 1/10 of the hip width, centre back slanted and raised). The
curves are placed so that every seam end meets at a right angle.

Coordinates: mm, y up. Top edge of the legs (waistband seam) at y = 0, centre
front/back at hip level at x = 0, side seam to the right.
Edge order (counter-clockwise):
  crotch (centre + crotch curve) → inseam → hem → side → waistband
"""
from __future__ import annotations

import copy

import numpy as np
from scipy.interpolate import CubicSpline

import ease as E
import geometry as G
from construction import Construction
from pattern import Edge, Mark, Notch, Pattern, Piece, rect_piece

STYLES = {
    "jogger": dict(fit="normal", fabric="sweat", cuffs=True, waistband="casing",
                        pockets=["side"], length="long"),
    "harem": dict(fit="harem", fabric="sweat", cuffs=True, waistband="casing",
                       pockets=[], length="long"),
    "leggings": dict(fit="slim", fabric="jersey_elastane", cuffs=False, waistband="yoga",
                     pockets=[], length="long"),
    "trousers": dict(fit="normal", fabric="woven", cuffs=False, waistband="tunnel",
                      pockets=["side"], length="long"),
}

DEFAULTS = dict(style="jogger", fit=None, fabric=None, stretch=None, length=None,
                waistband=None, cuffs=None, pockets=None, cuff_fabric="rib",
                cuff_stretch=None, waistband_height=None, cuff_height=None,
                elastic_width=None, crotch_drop=None, blouse=None, sa=10.0, hem_sa=25.0,
                # leg shape below the knee (without cuffs): straight, tapered, bootcut, flare;
                # flare_cm = leg opening minus leg width at the knee (circumference, cm)
                leg_shape="straight", flare_cm=None,
                # shorts/knee length: fold-back turn-up (cm, 0 = none), part of the hem allowance
                turn_up=None,
                # cargo patch pocket on the thigh: box pleat and flap
                cargo_pleat=True, cargo_flap=True,
                # overrides (reverse engineering / fine tuning), all finished measurements in mm
                hip_total=None, fork_factor=1.0, front_rise_total=None, inseam_total=None,
                opening_total=None, elastic_total=None, knee_total=None, thigh_total=None)

TITLES = {"jogger": "Joggers", "harem": "Harem pants", "leggings": "Leggings",
          "trousers": "Pull-on trousers"}


def resolve_options(options: dict | None) -> dict:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None or k not in o})
    style = STYLES.get(o["style"], STYLES["jogger"])
    for k, v in style.items():
        if o.get(k) is None:
            o[k] = copy.deepcopy(v)
    if o["pockets"] is None:
        o["pockets"] = []
    if isinstance(o["pockets"], str):
        o["pockets"] = [] if o["pockets"] in ("", "none") else [o["pockets"]]
    if o["fit"] == "slim":
        o["pockets"] = [p for p in o["pockets"] if p != "side"]
    if o["leg_shape"] not in LEG_SHAPES:
        raise ValueError(f"leg_shape must be one of {', '.join(LEG_SHAPES)}")
    if o["leg_shape"] != "straight" and (o["cuffs"] or o["length"] not in ("long", "7/8")):
        o["leg_shape"] = "straight"      # shaping below the knee needs a long, uncuffed leg
    if o["turn_up"] is None:
        o["turn_up"] = 0.0
    if o["turn_up"] and (o["cuffs"] or o["length"] not in ("short", "knee")):
        o["turn_up"] = 0.0               # turn-ups only for shorts / knee length without cuffs
    return o


LEG_SHAPES = ("straight", "tapered", "bootcut", "flare")


def _leg_spline(y_top, x_top, y_bot, x_bot, slope_top, slope_bot=0.0, mid=None, step=2.0):
    """x(y) spline from top to bottom with given slopes dx/dy at the ends."""
    ys = [y_bot, y_top]
    xs = [x_bot, x_top]
    if mid is not None:
        ys.insert(1, mid[1])
        xs.insert(1, mid[0])
    cs = CubicSpline(ys, xs, bc_type=((1, slope_bot), (1, slope_top)))
    n = max(10, int(abs(y_top - y_bot) / step))
    yy = np.linspace(y_top, y_bot, n)
    return np.stack([cs(yy), yy], axis=1)


def _width_between(edge_left, edge_right, y):
    def x_at(e):
        e = np.asarray(e)
        order = np.argsort(e[:, 1])
        return float(np.interp(y, e[order, 1], e[order, 0]))
    return x_at(edge_right) - x_at(edge_left)


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve_options(options)
    m = measures
    adult = m["height"] > 1650 and m["chest"] > 780
    fit, fabric = o["fit"], o["fabric"]
    _, stretch, knit = E.fabric_info(fabric, o["stretch"])
    o["stretch"] = stretch
    sa, hem_sa = o["sa"], o["hem_sa"]
    turn_up = float(o["turn_up"] or 0.0) * 10        # cm → mm
    if turn_up:
        hem_sa = hem_sa + 2 * turn_up                # the turn-up is folded out twice its height
    k = m["height"] / 1220.0  # scale factor for small parts (child size 122 = 1)
    k = max(0.75, min(1.45, k))

    # ---------------------------------------------------------------- widths
    C = Construction(o.get("construction"))
    he = E.hip_ease(fit, fabric, stretch)
    Hc = C.val("hip_width", o["hip_total"] or m["hip"] * (1 + he),
               "option hip_total" if o["hip_total"] else f"hip × (1 + {he * 100:.0f} % ease)")
    diff = C.val("front_back_offset", 10.0 if adult else 5.0,
                 "front quarter narrower, back quarter wider by this amount")
    Wf = C.val("front_width", Hc / 4 - diff, "hip_width / 4 − front_back_offset")
    Wb = C.val("back_width", Hc / 4 + diff, "hip_width / 4 + front_back_offset")
    pct_f, pct_b = (4.0, 8.0) if fit == "slim" else (5.0, 10.0)
    fe = C.val("front_crotch_extension", Hc * pct_f / 100 * o["fork_factor"],
               f"{pct_f:g} % of hip_width" + (f" × fork_factor {o['fork_factor']:g}" if o["fork_factor"] != 1 else ""))
    fbe = C.val("back_crotch_extension", Hc * pct_b / 100 * o["fork_factor"],
                f"{pct_b:g} % of hip_width" + (f" × fork_factor {o['fork_factor']:g}" if o["fork_factor"] != 1 else ""))

    # ---------------------------------------------------------------- heights
    wb_type = o["waistband"]
    wb_h = o["waistband_height"] or {"casing": 30, "rib": 35, "yoga": 60,
                                      "tunnel": 0}[wb_type] * (k if adult else 1.0)
    if wb_type == "tunnel":
        wb_h = 0.0
    el_w = o["elastic_width"] or (30.0 if adult else 20.0)
    drop = o["crotch_drop"]
    if drop is None:
        drop = 0.06 * m["height"] if fit == "harem" else 0.0
    rise_body = m["side_length"] - m["inseam"]
    if o["front_rise_total"]:
        R = C.val("rise", o["front_rise_total"] - wb_h, "option front_rise_total − waistband height")
    else:
        R = C.val("rise", rise_body + E.rise_ease_mm(fit, adult) + drop - wb_h,
                  "(side length − inseam) + seat ease" + (" + harem drop" if drop else "")
                  + (" − waistband height" if wb_h else ""))
    cuffs = bool(o["cuffs"])
    cuff_h = (o["cuff_height"] or ((70 if fit == "harem" else 50) * k)) if cuffs else 0.0
    blouse = o["blouse"]
    if blouse is None:
        blouse = (30.0 if fit == "harem" else 15.0) * k if cuffs else 0.0
    length = o["length"]
    leg_frac = {"long": None, "7/8": 0.82, "knee": 0.45, "short": 0.18}[length]
    if o["inseam_total"]:
        inseam_fin = o["inseam_total"]
    elif leg_frac is None:
        inseam_fin = m["inseam"] - (25 if adult else 15) - drop + blouse
    else:
        inseam_fin = m["inseam"] * leg_frac - drop + (blouse if length == "7/8" else 0)
    inseam_fin = C.val("inseam_finished", inseam_fin,
                       "option inseam_total" if o["inseam_total"] else "inseam − allowance to the floor"
                       + (" − harem drop" if drop else "") + (" + blousing" if blouse else ""))
    leg_len = inseam_fin - cuff_h          # vertical length crotch line → hem edge

    # ---------------------------------------------------------------- leg opening
    ratio_cuff = E.band_ratio(o["cuff_fabric"], o["cuff_stretch"]) if cuffs else 1.0
    if cuffs:
        cuff_len = o["opening_total"] or max(m["ankle"] * 1.12, m["ankle"] + 15)
        hem_c = cuff_len / ratio_cuff
    else:
        cuff_len = 0.0
        if o["opening_total"]:
            hem_c = o["opening_total"]
        else:
            hem_c = {"slim": m["ankle"] * (1.08 if stretch < 50 else 1.0), "normal": 0.46 * Hc,
                     "wide": 0.62 * Hc, "oversized": 0.66 * Hc, "harem": 0.40 * Hc}[fit]
            if length == "knee":
                hem_c = max(hem_c, m["knee"] * (1.0 + max(he, 0.05)) * 1.05)
            if length == "short":
                hem_c = max(hem_c, (Wf + Wb + fe + fbe) * 0.92)   # nearly as wide as the thigh
    hem_how = "cuff length / cuff stretch ratio" if cuffs else \
        ("option opening_total" if o["opening_total"] else f"leg opening for fit '{fit}'")
    leg_shape = o["leg_shape"]
    knee_shape = None
    if leg_shape != "straight":
        # leg width at the knee of the straight leg (thigh → straight hem, linear), then
        # the shape below the knee: tapered narrows, bootcut/flare widen by flare_cm
        top_w = Wf + fe + Wb + fbe
        kt0 = top_w + (hem_c - top_w) * 0.45
        if fit == "slim":
            kt0 = m["knee"] * (1 + he + 0.02)
        kt0 = max(kt0, m["knee"] * (1 + max(he, 0.05)))
        knee_shape = C.val("knee_width", kt0, "leg width at the knee for the shaped leg")
        if leg_shape == "tapered":
            hem_c = max(m["ankle"] * 1.35 + 20, min(hem_c, knee_shape) * 0.8)
            hem_how = "tapered: 80 % of the narrower of knee and straight opening (foot must fit)"
        else:
            default = {"bootcut": 60.0, "flare": 160.0}[leg_shape] * (k if adult else k * 0.6)
            flare = float(o["flare_cm"]) * 10 if o["flare_cm"] is not None else default
            hem_c = knee_shape + flare
            hem_how = f"{leg_shape}: knee width + flare {flare / 10:.1f} cm"
    hem_c = C.val("hem_width", hem_c, hem_how)
    hem_front, hem_back = hem_c / 2 - 2 * diff, hem_c / 2 + 2 * diff

    # ---------------------------------------------------------------- front leg
    y_hip = -0.55 * R
    y_cr = -R
    y_hem = y_cr - leg_len
    crease_f = (Wf - fe) / 2
    knee_y = y_cr - leg_len * 0.45
    knee_fr = knee_bk = None
    if length in ("long", "7/8") and (fit == "slim" or o["knee_total"] or knee_shape):
        kt = o["knee_total"] or knee_shape or m["knee"] * (1 + he + 0.02)
        knee_fr, knee_bk = kt / 2 - 2 * diff, kt / 2 + 2 * diff

    # front inseam first (the crotch angle depends on its start tangent)
    slope_in = 0.0 if fit in ("harem", "wide", "oversized") else None
    inner_hem = crease_f - hem_front / 2
    if slope_in is None:
        # dx/dy < 0: the inseam runs slightly inwards going down
        slope_in = -0.15 if fit == "normal" else -0.25
    mid_in = (crease_f - knee_fr / 2, knee_y) if knee_fr else None
    inseam_f = _leg_spline(y_cr, -fe, y_hem, inner_hem, slope_in, 0.0, mid_in)
    d_in = G.start_dir(inseam_f)
    arrive = np.array([d_in[1], -d_in[0]])          # ⟂ to the inseam
    cf_top = G.P(0, 0)
    cf_bot = G.P(0, y_hip)
    curve_f = G.tangent_curve(cf_bot, (0, -1), G.P(-fe, y_cr), arrive, 0.55, 0.45)
    schritt_f = G.join(G.line(cf_top, cf_bot), curve_f)
    mid_out = (crease_f + knee_fr / 2, knee_y) if knee_fr else None
    side_f_leg = _leg_spline(y_cr, Wf, y_hem, crease_f + hem_front / 2, 0.0, 0.0, mid_out)[::-1]
    saum_f = G.line(inseam_f[-1], side_f_leg[0])

    pockets = list(o["pockets"])
    pieces = []
    seams, corners, checks, notes = [], [], [], []

    pk_a = max(35.0, 0.28 * Wf)                  # pocket opening: distance along the top edge
    pk_b = max(95.0, min(0.62 * R, 170.0))       # pocket opening: depth along the side seam
    if "side" in pockets:
        side_top = G.P(Wf, -pk_b)
        seite_f = G.join(side_f_leg, G.line(side_f_leg[-1], side_top))
        eingriff = G.line(side_top, G.P(Wf - pk_a, 0))
        bund_f = G.line(G.P(Wf - pk_a, 0), cf_top)
        f_edges = [
            Edge("crotch", schritt_f, sa, label="Crotch seam"),
            Edge("inseam", inseam_f, sa, label="Inseam"),
            Edge("hem", saum_f, sa if cuffs else hem_sa, label="Cuff seam" if cuffs else "Hem",
                 turned=not cuffs),
            Edge("side", seite_f, sa, label="Side seam"),
            Edge("pocket_opening", eingriff, sa, label="Pocket opening"),
            Edge("waistband", bund_f, sa if wb_type != "tunnel" else el_w + 15, label="Waistband seam",
                 turned=wb_type == "tunnel"),
        ]
    else:
        seite_f = G.join(side_f_leg, G.line(side_f_leg[-1], G.P(Wf, 0)))
        f_edges = [
            Edge("crotch", schritt_f, sa, label="Crotch seam"),
            Edge("inseam", inseam_f, sa, label="Inseam"),
            Edge("hem", saum_f, sa if cuffs else hem_sa, label="Cuff seam" if cuffs else "Hem",
                 turned=not cuffs),
            Edge("side", seite_f, sa, label="Side seam"),
            Edge("waistband", G.line(G.P(Wf, 0), cf_top), sa if wb_type != "tunnel" else el_w + 15,
                 label="Waistband seam"),
        ]
    front = Piece("front", "Front leg", f_edges, cut_count=2, mirror=True,
                  fabric="Main fabric",
                  grain=(G.P(crease_f, y_cr - 40), G.P(crease_f, max(y_hem + 60, y_cr - leg_len * 0.6))))
    side_notch = 0.5 * G.length(side_f_leg)
    front.notches += [Notch("side", side_notch, 1), Notch("inseam", 80, 1),
                      Notch("crotch", G.length(schritt_f) * 0.5, 1)]
    if wb_type == "tunnel":
        front.marks.append(Mark(G.line(G.P(Wf - (pk_a if "side" in pockets else 0), el_w + 7),
                                       G.P(0, el_w + 7)), "fold", "Fold casing"))

    # ---------------------------------------------------------------- back leg
    rb = (25.0 if adult else 15.0) if fit != "slim" else (35.0 if adult else 20.0)
    sb = (25.0 if adult else 15.0)
    crease_b = (Wb - fbe) / 2
    inner_hem_b = crease_b - hem_back / 2
    cb_top = G.P(sb, rb)
    cb_bot = G.P(0, y_hip)

    def build_back(d):
        mid_in_b = (crease_b - knee_bk / 2, knee_y) if knee_bk else None
        ins = _leg_spline(y_cr - d, -fbe, y_hem, inner_hem_b, slope_in, 0.0, mid_in_b)
        din = G.start_dir(ins)
        arr = np.array([din[1], -din[0]])
        cb_dir = G.unit(cb_bot - cb_top)
        crv = G.tangent_curve(cb_bot, cb_dir, G.P(-fbe, y_cr - d), arr, 0.55, 0.5)
        return ins, G.join(G.line(cb_top, cb_bot), crv)

    lo, hi = -15.0, 45.0
    target = G.length(inseam_f)
    for _ in range(50):
        d = 0.5 * (lo + hi)
        ins_b, _ = build_back(d)
        if G.length(ins_b) > target:
            lo = d
        else:
            hi = d
    inseam_b, schritt_b = build_back(0.5 * (lo + hi))
    back_drop = 0.5 * (lo + hi)
    mid_out_b = (crease_b + knee_bk / 2, knee_y) if knee_bk else None
    side_b_leg = _leg_spline(y_cr, Wb, y_hem, crease_b + hem_back / 2, 0.0, 0.0, mid_out_b)[::-1]
    seite_b = G.join(side_b_leg, G.line(side_b_leg[-1], G.P(Wb, 0)))
    cb_dir = G.unit(cb_bot - cb_top)
    waist_arrive = np.array([cb_dir[1], -cb_dir[0]])
    bund_b = G.tangent_curve(G.P(Wb, 0), (-1, 0), cb_top, waist_arrive, 0.35, 0.35)
    saum_b = G.line(inseam_b[-1], side_b_leg[0])
    back = Piece("back", "Back leg", [
        Edge("crotch", schritt_b, sa, label="Crotch seam"),
        Edge("inseam", inseam_b, sa, label="Inseam"),
        Edge("hem", saum_b, sa if cuffs else hem_sa, label="Cuff seam" if cuffs else "Hem",
                 turned=not cuffs),
        Edge("side", seite_b, sa, label="Side seam"),
        Edge("waistband", bund_b, sa if wb_type != "tunnel" else el_w + 15, label="Waistband seam",
             turned=wb_type == "tunnel"),
    ], cut_count=2, mirror=True, fabric="Main fabric",
        grain=(G.P(crease_b, y_cr - 40), G.P(crease_b, max(y_hem + 60, y_cr - leg_len * 0.6))))
    back.notches += [Notch("side", side_notch, 2), Notch("inseam", 80, 2),
                     Notch("crotch", G.length(schritt_b) * 0.5, 2)]
    if wb_type == "tunnel":
        back.marks.append(Mark(G.line(G.P(Wb, el_w + 7), G.P(sb, rb + el_w + 7)), "fold",
                               "Fold casing"))

    # make the side seams equal (adjust the top of the back leg slightly)
    dl = G.length(seite_b) - (G.length(seite_f) + (pk_b if "side" in pockets else 0.0))
    if abs(dl) > 0.3:
        back.edges[3].pts = G.join(side_b_leg, G.line(side_b_leg[-1], G.P(Wb, -dl)))
        back.edges[4].pts = G.tangent_curve(G.P(Wb, -dl), (-1, 0), cb_top, waist_arrive, 0.35, 0.35)

    pieces += [front, back]

    # ---------------------------------------------------------------- pockets
    if "side" in pockets:
        bag_depth = pk_b + 45 * k
        x0 = max(Wf - pk_a - 35 * k, 20.0)
        T0, T1, S1 = G.P(x0, 0), G.P(Wf, 0), G.P(Wf, -bag_depth)
        r = min(35.0 * k, (Wf - x0) * 0.45)
        bag = G.join(G.line(T0, G.P(x0, -bag_depth + r)),
                     G.tangent_curve(G.P(x0, -bag_depth + r), (0, -1), G.P(x0 + r, -bag_depth), (1, 0), 0.55, 0.55),
                     G.line(G.P(x0 + r, -bag_depth), S1))
        E_ = G.P(Wf, -pk_b)
        side_panel = Piece("side_panel", "Side panel (outer pocket bag)", [
            Edge("bag", bag, sa, label="Pocket bag seam"),
            Edge("side_lower", G.line(S1, E_), sa, label="Side seam"),
            Edge("side_upper", G.line(E_, T1), sa, label="Side seam"),
            Edge("waist_outer", G.line(T1, G.P(Wf - pk_a, 0)), sa, label="Waistband seam"),
            Edge("waist_inner", G.line(G.P(Wf - pk_a, 0), T0), sa, label="Waistband seam"),
        ], cut_count=2, mirror=True, fabric="Main fabric",
            grain=(G.P((x0 + Wf) / 2, -bag_depth + 30), G.P((x0 + Wf) / 2, -25)))
        side_panel.marks.append(Mark(G.line(E_, G.P(Wf - pk_a, 0)), "placement", "Pocket opening"))
        lining = Piece("pocket_bag", "Inner pocket bag", [
            Edge("bag", bag.copy(), sa, label="Pocket bag seam"),
            Edge("side", G.line(S1, E_), sa, label="Side seam"),
            Edge("pocket_opening", G.line(E_, G.P(Wf - pk_a, 0)), sa, label="Pocket opening"),
            Edge("waistband", G.line(G.P(Wf - pk_a, 0), T0), sa, label="Waistband seam"),
        ], cut_count=2, mirror=True, fabric="Main fabric or cotton jersey",
            grain=(G.P(x0 + 25, -bag_depth + 30), G.P(x0 + 25, -25)))
        pieces += [side_panel, lining]
        seams += [
            dict(name="Pocket opening: front leg ↔ pocket bag", a=[("front", "pocket_opening", 1)],
                 b=[("pocket_bag", "pocket_opening", 1)], type="equal"),
            dict(name="Pocket bag seam: pocket bag ↔ side panel", a=[("pocket_bag", "bag", 1)],
                 b=[("side_panel", "bag", 1)], type="equal"),
            dict(name="Pocket bag ↔ side panel at the side seam", a=[("pocket_bag", "side", 1)],
                 b=[("side_panel", "side_lower", 1)], type="equal"),
        ]
    if "back_patch" in pockets:
        pw, ph = 110 * k, 120 * k
        pocket = rect_piece("back_pocket", "Back patch pocket", pw, ph, sa=sa,
                            cut_count=2, names=("bottom", "right", "top", "left"),
                            labels=("", "", "Pocket facing", ""), sas=(sa, sa, 25.0, sa))
        pieces.append(pocket)
        px = Wb * 0.55
        py = -0.15 * R
        rect = np.array([[px - pw / 2, py], [px + pw / 2, py], [px + pw / 2, py - ph],
                         [px - pw / 2, py - ph], [px - pw / 2, py]])
        back.marks.append(Mark(rect, "placement", "Back pocket"))

    if "cargo" in pockets:
        _cargo(o, front, pieces, notes, side_f_leg, y_cr, leg_len, k, sa, adult)

    # ---------------------------------------------------------------- turn-up marks
    if turn_up:
        for pc in (front, back):
            h = pc.edge("hem").pts
            pc.marks.append(Mark(np.array([h[0] + (0, -turn_up), h[-1] + (0, -turn_up)]), "fold",
                                 "Turn-up fold"))
            pc.marks.append(Mark(np.array([h[0], h[-1]]) + (0, 0.01), "fold", "Hem edge"))
        notes.append(f"Turn-up {turn_up / 10:.1f} cm: the hem allowance includes twice its height "
                     f"plus {o['hem_sa'] / 10:.1f} cm to turn under.")

    # ---------------------------------------------------------------- waistband
    top_parts = [("front", "waistband", 2), ("back", "waistband", 2)]
    if "side" in pockets:
        top_parts.append(("side_panel", "waist_outer", 2))
    top_len = sum(next(p for p in pieces if p.key == a).edge(e).length * n for a, e, n in top_parts)
    elastic_len = o["elastic_total"] or m["waist"] * (0.90 if not adult else 0.92)
    if wb_type in ("casing", "rib", "yoga"):
        if wb_type == "casing":
            wb_fab, ratio, label = fabric, 1.0, "Waistband (elastic)"
        elif wb_type == "rib":
            wb_fab, ratio, label = "rib", E.band_ratio("rib"), "Rib waistband"
        else:
            wb_fab, ratio, label = fabric, E.band_ratio(fabric, stretch), "Wide yoga waistband"
        bl = top_len * ratio
        # waistband on the fold (half length): saves space on roll/sheet, cross seam only at the back
        band = rect_piece("waistband", label, bl / 2, 2 * wb_h, sa=sa, cut_count=1, fold_left=True,
                          fabric="Rib knit" if wb_fab == "rib" else "Main fabric",
                          names=("bottom", "right", "top", "left"),
                          labels=("Seam edge", "Cross seam", "Seam edge", "Centre front"), grain_vertical=True)
        band.marks.append(Mark(G.line(G.P(0, wb_h), G.P(bl / 2, wb_h)), "fold", "Fold line"))
        band.stretch_dir = "Stretch direction: along the length"
        pieces.append(band)
        if wb_type == "casing":
            seams.append(dict(name="Waistband ↔ pants top edge", a=top_parts, b=[("waistband", "bottom", 2)],
                              type="equal"))
        else:
            lo_r, hi_r = E.band_ratio_range("rib" if wb_type == "rib" else "jersey")
            seams.append(dict(name="Waistband ↔ pants top edge (stretched)", a=top_parts,
                              b=[("waistband", "bottom", 2)], type="ratio", lo=lo_r, hi=hi_r))
        waist_relaxed = elastic_len if wb_type == "casing" else bl
        if wb_type == "yoga":
            waist_relaxed = bl
    else:
        waist_relaxed = elastic_len
    if wb_type in ("casing", "tunnel"):
        notes.append(f"Elastic {el_w:.0f} mm wide, length {elastic_len / 10:.0f} cm "
                     f"(+2 cm overlap for joining)")

    # ---------------------------------------------------------------- cuffs
    if cuffs:
        cuff = rect_piece("leg_cuff", "Leg cuff", cuff_len, 2 * cuff_h, sa=sa, cut_count=2,
                          fabric="Rib knit", labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"),
                          mirror=False)
        cuff.marks.append(Mark(G.line(G.P(0, cuff_h), G.P(cuff_len, cuff_h)), "fold", "Fold line"))
        cuff.stretch_dir = "Stretch direction: along the length"
        pieces.append(cuff)
        lo_r, hi_r = E.band_ratio_range(o["cuff_fabric"])
        seams.append(dict(name="Leg cuff ↔ leg opening (stretched)",
                          a=[("front", "hem", 1), ("back", "hem", 1)],
                          b=[("leg_cuff", "bottom", 1)], type="ratio", lo=lo_r, hi=hi_r))

    # ---------------------------------------------------------------- seam pairs
    side_a = [("front", "side", 1)]
    if "side" in pockets:
        side_a.append(("side_panel", "side_upper", 1))
    seams[:0] = [
        dict(name="Side seam front ↔ back", a=side_a, b=[("back", "side", 1)], type="equal"),
        dict(name="Inseam front ↔ back", a=[("front", "inseam", 1)],
             b=[("back", "inseam", 1)], type="equal"),
        dict(name="Front crotch seam (left ↔ right piece)", a=[("front", "crotch", 1)],
             b=[("front", "crotch", 1)], type="equal"),
        dict(name="Back crotch seam (left ↔ right piece)", a=[("back", "crotch", 1)],
             b=[("back", "crotch", 1)], type="equal"),
    ]

    # ---------------------------------------------------------------- angles
    corners += [
        dict(name="Centre front ↔ waistband", piece="front", a="waistband", b="crotch", target=90),
        dict(name="Centre back ↔ waistband", piece="back", a="waistband", b="crotch", target=90),
        dict(name="Crotch ↔ inseam (front + back)", sum=[("front", "crotch", "inseam"),
                                                             ("back", "crotch", "inseam")],
             target=180),
        dict(name="Inseam ↔ hem front", piece="front", a="inseam", b="hem", target=90),
        dict(name="Hem ↔ side seam front", piece="front", a="hem", b="side", target=90),
        dict(name="Inseam ↔ hem back", piece="back", a="inseam", b="hem", target=90),
        dict(name="Hem ↔ side seam back", piece="back", a="hem", b="side", target=90),
        dict(name="Side seam ↔ waistband back", piece="back", a="side", b="waistband", target=90),
    ]
    if "side" not in pockets:
        corners.append(dict(name="Side seam ↔ waistband (front + back)",
                            sum=[("front", "side", "waistband"), ("back", "side", "waistband")],
                            target=180))
    else:
        corners.append(dict(name="Side seam ↔ waistband at the side panel", piece="side_panel",
                            a="side_upper", b="waist_outer", target=90))

    pat = Pattern("pants_basic", TITLES.get(o["style"], "Pants"), "", pieces, dict(m), o,
                  seams=seams, corners=corners, checks=checks, notes=notes)

    # ---------------------------------------------------------------- finished measurements
    pat.options["_y_hip"] = y_hip
    fin = finished_measures(pat, wb_h=wb_h, cuff_h=cuff_h, waist_relaxed=waist_relaxed,
                            pk_b=pk_b if "side" in pockets else 0.0)
    pat.finished = fin
    pat.options.update(dict(_wb_h=wb_h, _cuff_h=cuff_h, _waist_relaxed=waist_relaxed,
                            _pk_b=pk_b if "side" in pockets else 0.0, _R=R, _hip_total=Hc,
                            _drop=drop, _back_drop=back_drop, _elastic=elastic_len,
                            _cuff_len=cuff_len, _hem_c=hem_c, _blouse=blouse))

    # ---------------------------------------------------------------- checks
    tol_hip = 0.01
    checks += [
        dict(name="Hip circumference pattern = body + ease", kind="circ",
             value=fin["hip_circ"], target=Hc, tol_rel=tol_hip,
             note=f"body {m['hip'] / 10:.1f} cm + {he * 100:+.0f} % ease"
             if not o["hip_total"] else "target from measurement/override"),
        dict(name="Top edge fits over the hip", kind="min",
             value=top_len * (1 + stretch / 100 * 0.6), target=m["hip"] * 1.02,
             note="top edge incl. usable stretch ≥ hip"),
        dict(name="Front rise plausible", kind="range", value=R + wb_h,
             lo=0.12 * m["height"], hi=0.12 * m["height"] + rise_body * 0.3 + drop + 40,
             note=f"body rise {rise_body / 10:.1f} cm" + (f", harem drop {drop / 10:.1f} cm" if drop else "")),
        dict(name="Inseam length plausible", kind="range", value=fin["inseam"] + drop,
             lo=m["inseam"] * (leg_frac or 0.85) * 0.85, hi=m["inseam"] * (leg_frac or 1.0) * 1.12,
             note=f"body inseam {m['inseam'] / 10:.1f} cm"),
        dict(name="Foot fits through the leg opening", kind="min",
             value=fin["opening"] * (1 + (E.fabric_info(o['cuff_fabric'])[1] if cuffs else stretch) / 100 * 0.6),
             target=m["ankle"] * 1.35, note="heel-instep circumference ≈ 1.35 × ankle"),
    ]
    if fit == "slim" and stretch < 30:
        checks.append(dict(name="Fabric stretchy enough for leggings", kind="min", value=stretch,
                           target=30, note="leggings need ≥ 30 % crosswise stretch"))
    pat.size_label = ""
    pat.construction = C.rows()
    if C.unknown_overrides():
        pat.notes.append("Unknown construction value(s) ignored: " + ", ".join(C.unknown_overrides()))
    return pat


def _cargo(o, front, pieces, notes, side_leg, y_cr, leg_len, k, sa, adult):
    """Cargo patch pocket on the side of the thigh (front leg, next to the side seam)."""
    from shapely.geometry import Polygon, box
    poly = Polygon(front.seam_ring())
    order = np.argsort(side_leg[:, 1])

    def side_x(y):
        return float(np.interp(y, side_leg[order, 1], side_leg[order, 0]))
    ph = min(175.0 * k, 0.45 * leg_len)
    pw = min(150.0 * k, 0.55 * G.width_at_y(front.seam_ring(), y_cr - 0.1 * leg_len))
    y_top = y_cr - 0.12 * leg_len - 45.0 * k
    gap = 12.0 * k
    for _ in range(40):
        x1 = min(side_x(y_top), side_x(y_top - ph)) - gap
        rect = box(x1 - pw, y_top - ph, x1, y_top)
        if poly.buffer(-3).contains(rect):
            break
        pw *= 0.95
        ph *= 0.97
    pleat = (20.0 * k) if o["cargo_pleat"] else 0.0
    pocket = rect_piece("cargo_pocket", "Cargo pocket", pw + 2 * pleat, ph, sa=sa, cut_count=2,
                        names=("bottom", "right", "top", "left"),
                        labels=("", "", "Pocket facing", ""), sas=(sa, sa, 25.0, sa))
    if pleat:
        c = (pw + 2 * pleat) / 2
        for dx, lab in ((-pleat, "Pleat fold"), (pleat, "Pleat fold")):
            pocket.marks.append(Mark(G.line(G.P(c + dx, 0), G.P(c + dx, ph)), "fold", lab))
        pocket.marks.append(Mark(G.line(G.P(c, 0), G.P(c, ph)), "placement", "Pleat centre"))
    pieces.append(pocket)
    rect = np.array([[x1 - pw, y_top], [x1, y_top], [x1, y_top - ph], [x1 - pw, y_top - ph], [x1 - pw, y_top]])
    front.marks.append(Mark(rect, "placement", "Cargo pocket"))
    if o["cargo_flap"]:
        fh = 55.0 * k
        flap = rect_piece("cargo_flap", "Cargo pocket flap", pw + 6.0, fh, sa=sa, cut_count=4,
                          names=("bottom", "right", "top", "left"),
                          labels=("Flap edge", "", "Stitching edge", ""))
        flap.info.append("2 outer + 2 facing")
        pieces.append(flap)
        fy = y_top + 15.0
        front.marks.append(Mark(G.line(G.P(x1 - pw - 3, fy), G.P(x1 + 3, fy)), "placement", "Flap"))
    notes.append(f"Cargo pocket {pw / 10:.1f} × {ph / 10:.1f} cm" + (" with box pleat" if pleat else "")
                 + (" and flap" if o["cargo_flap"] else "") + "; a snap or Velcro for the flap is optional.")


def finished_measures(pat: Pattern, wb_h=None, cuff_h=None, waist_relaxed=None, pk_b=None) -> dict:
    """Virtual sewing: measurements of the finished pants (measured flat × 2 = circumference)."""
    o = pat.options
    wb_h = o.get("_wb_h", 0.0) if wb_h is None else wb_h
    cuff_h = o.get("_cuff_h", 0.0) if cuff_h is None else cuff_h
    waist_relaxed = o.get("_waist_relaxed", 0.0) if waist_relaxed is None else waist_relaxed
    pk_b = o.get("_pk_b", 0.0) if pk_b is None else pk_b
    f, b = pat.piece("front"), pat.piece("back")
    sf, sb = f.seam_ring(), b.seam_ring()
    # hip level: lower end of the straight centre = lowest point with x≈0
    y_hip = o.get("_y_hip")
    if y_hip is None:
        cf = f.edge("crotch").pts
        y_hip = float(cf[np.abs(cf[:, 0]) < 1e-6][:, 1].min())
    if pat.has("side_panel"):  # front leg + side panel share one coordinate system
        from shapely.geometry import Polygon
        u = Polygon(sf).union(Polygon(pat.piece("side_panel").seam_ring()))
        sf_hip = np.asarray(u.exterior.coords)
    else:
        sf_hip = sf
    hip = 2 * (G.width_at_y(sf_hip, y_hip) + G.width_at_y(sb, y_hip))
    y_cr_f = float(f.edge("inseam").pts[0, 1])
    y_cr_b = float(b.edge("inseam").pts[0, 1])
    thigh = G.width_at_y(sf, y_cr_f - 25) + G.width_at_y(sb, y_cr_b - 25)   # one leg
    leg_len = y_cr_f - float(f.edge("hem").pts[0, 1])
    knee = G.width_at_y(sf, y_cr_f - 0.5 * leg_len) + G.width_at_y(sb, y_cr_b - 0.5 * leg_len)
    if pat.has("leg_cuff"):
        opening = pat.piece("leg_cuff").edge("bottom").length
    else:
        opening = f.edge("hem").length + b.edge("hem").length
    rise_f = -y_cr_f + wb_h
    # back rise: highest point of centre back to crotch
    rise_b = float(b.edge("crotch").pts[0, 1]) - y_cr_b + wb_h
    y_hem = float(f.edge("hem").pts[0, 1])
    # lengths measured vertically (like a tape measure on the pants lying flat)
    inseam = (y_cr_f - y_hem) + cuff_h
    outseam = -y_hem + wb_h + cuff_h
    top = 2 * (f.edge("waistband").length + b.edge("waistband").length +
               (pat.piece("side_panel").edge("waist_outer").length if pat.has("side_panel") else 0.0))
    return dict(hip_circ=hip, thigh_circ=thigh, knee_circ=knee, opening=opening, waist_relaxed=waist_relaxed,
                waist_max=top, outseam=outseam, inseam=inseam, front_rise=rise_f, back_rise=rise_b,
                waistband_h=wb_h, cuff_h=cuff_h, crotch_seam=2 * 0 + f.edge("crotch").length +
                b.edge("crotch").length + 2 * wb_h)


FINISHED_LABELS = {
    "hip_circ": ("Hip width", "width"), "thigh_circ": ("Thigh width", "width"),
    "knee_circ": ("Leg width at mid-leg", "width"),
    "opening": ("Leg opening", "width"), "waist_relaxed": ("Waistband relaxed", "width"),
    "waist_max": ("Waistband stretched (pants top edge)", "width"), "outseam": ("Outseam", "length"),
    "inseam": ("Inseam", "length"), "front_rise": ("Front rise", "length"),
    "back_rise": ("Back rise", "length"), "waistband_h": ("Waistband height", "length"),
    "cuff_h": ("Cuff height", "length"), "crotch_seam": ("Crotch seam total", "length"),
}

# measurements fitted by reverse engineering: option → (finished measurement, start-value function)
FIT_PARAMS = ["hip_total", "fork_factor", "front_rise_total", "inseam_total", "opening_total"]


def sewing_steps(pat: Pattern) -> list[str]:
    o = pat.options
    knit = E.fabric_info(o["fabric"])[2]
    st = "with an overlocker or a narrow zigzag/stretch stitch" if knit else "with a straight stitch, then finish the edges"
    steps = []
    if "side" in o["pockets"]:
        steps += [
            "**Side pockets:** place the inner pocket bag right sides together on the pocket opening of the "
            "front leg and sew. Clip the seam allowance, turn the bag to the inside, press the edge and "
            "topstitch 5 mm from the edge.",
            "Place the side panel right sides together under the pocket bag (the \"pocket opening\" mark meets "
            "the opening edge) and sew the bag seam. Baste the side panel to the front leg at the top edge "
            "and side within the seam allowance.",
        ]
    if "cargo" in o["pockets"]:
        cargo = ["**Cargo pockets:** press the top edge 2.5 cm to the inside and topstitch."]
        if o.get("cargo_pleat", True):
            cargo.append("Fold the box pleat: bring both \"pleat fold\" lines to the pleat centre on the "
                         "wrong side, press and baste across top and bottom.")
        cargo.append("Press the other edges under by 1 cm and stitch the pocket onto the front leg at the "
                     "\"Cargo pocket\" marking (edgestitch, reinforce the top corners).")
        if o.get("cargo_flap", True):
            cargo.append("Sew outer flap and facing right sides together along the sides and the flap edge, "
                         "trim, turn, press and topstitch. Sew the open edge onto the \"Flap\" line upside "
                         "down, fold it down and topstitch 7 mm from the fold.")
        steps.append(" ".join(cargo))
    if "back_patch" in o["pockets"]:
        steps.append("**Back pockets:** press the top edge 2.5 cm to the inside and topstitch, press the other "
                     "edges under by 1 cm, then stitch the pockets onto the back legs at the marking.")
    steps += [
        f"**Side seams:** place front and back legs right sides together (notches: single = front, "
        f"double = back) and sew the side seams {st}.",
        "**Inseams:** sew each inseam; the notches on the inseam meet.",
        "**Crotch seam:** turn one leg right side out and slip it into the other (wrong side out) so the "
        "legs lie right sides together. Sew the crotch seam in one go from the front to the back top "
        "edge; the inseams meet exactly.",
    ]
    wb = o["waistband"]
    if wb == "casing":
        steps += [
            "**Waistband:** fold the waistband strip right sides together into a ring and sew the cross seam "
            "(centre back), leaving 3 cm open for the elastic. Fold lengthwise wrong sides together along the "
            "fold line.",
            "Divide waistband and pants top edge into quarters and mark them (centre front/back, sides). "
            "Pin the waistband right sides together to the top edge (opening at the back, inside) and sew.",
            "Thread the elastic, overlap the ends by 2 cm and sew them together, close the opening. Spread the "
            "gathers evenly and secure the elastic in the side seams by stitching in the ditch.",
        ]
    elif wb in ("rib", "yoga"):
        steps += [
            "**Waistband:** sew the waistband into a ring (cross seam at the back) and fold it lengthwise "
            "wrong sides together. Divide waistband and pants top edge into quarters and mark them.",
            "Sew the waistband to the pants top edge right sides together, stretching it slightly (cross seam "
            "at centre back). Stretch only the waistband, not the pants.",
        ]
    else:
        steps += [
            "**Elastic casing:** press the top edge under by 7 mm, then fold it to the inside along the "
            "\"fold casing\" line and edgestitch, leaving a 3 cm opening. Thread the elastic, sew the ends "
            "together with an overlap and close the opening.",
        ]
    if o["cuffs"]:
        steps += [
            "**Leg cuffs:** sew each cuff into a ring right sides together, then fold it lengthwise wrong "
            "sides together. Divide cuff and leg opening into quarters and mark them.",
            "Slip the cuff over the right-side-out leg, put its seam at the inseam and sew it on while "
            "stretching. Press the seam allowance towards the pants.",
        ]
    elif o.get("turn_up"):
        steps.append(f"**Hem with turn-up:** press {o['hem_sa'] / 10:.1f} cm under and sew it down. Fold the "
                     "leg to the inside along the \"Hem edge\", then fold the turn-up back to the outside "
                     "along the \"Turn-up fold\" and tack it at the side seam and inseam.")
    else:
        steps.append(f"**Hem:** press the hem allowance ({o['hem_sa'] / 10:.1f} cm) to the inside and sew it "
                     "with a twin needle or a straight stitch.")
    steps.append("Done! Press all seams (with sweat: steam, do not press down hard).")
    return steps
