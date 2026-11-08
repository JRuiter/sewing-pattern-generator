"""T-shirt / long sleeve: front and back on the fold, sleeve, neckband.
Variants: set-in or raglan sleeve, short/long/3/4, round or V neck.

Original draft: chest width (incl. ease) divided into quarters, armhole depth from the
chest width, shoulder slope ≈ 17°; the sleeve-cap height is solved numerically so that
the cap is longer than the armhole by the desired amount of ease.

Coordinates mm, y up; y = 0 at the level of the neck point (shoulder/neck).
Body pieces: centre (fold) at x = 0, side seam to the right.
"""
from __future__ import annotations

import math

import numpy as np

import ease as E
import geometry as G
from construction import Construction
from pattern import Edge, Mark, Notch, Pattern, Piece, rect_piece

DEFAULTS = dict(fit="normal", fabric="jersey", stretch=None, sleeve_style="set_in",
                sleeve_length="short", neckline="round", length="normal", band_fabric="rib",
                band_stretch=None, sleeve_cuffs=False, hem_band=False, sa=10.0, hem_sa=20.0,
                neck_band_h=None, chest_total=None, body_length=None, sleeve_len_total=None,
                sleeve_opening=None, neck_extra=0.0, cuff_h=None, hem_band_h=None,
                bicep_total=None, hem_total=None,
                # back opening (doll clothes, woven tops): centre back split, closed with Velcro or
                # snaps; opening_sa = allowance of the opening edge (overlap + turn-under)
                back_opening=False, opening_sa=None,
                # neckline finish: band (stretched neckband) or bias (bias binding strip, woven)
                neck_finish="band",
                # limits for unusual proportions (dolls): deepest armhole (mm, from the neck point)
                # and the short-sleeve opening as a share of the upper-arm width
                armhole_depth_max=None, sleeve_taper=0.9)


def resolve_options(options):
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["sleeve_length"] == "long" and "sleeve_cuffs" not in (options or {}):
        o["sleeve_cuffs"] = False
    return o


def _body_frame(m, o, adult, C: Construction | None = None):
    C = C or Construction()
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    be = E.body_ease(o["fit"], o["fabric"], stretch)
    Ct = C.val("chest_width", o["chest_total"] or m["chest"] * (1 + be),
               "option chest_total" if o["chest_total"] else f"chest × (1 + {be * 100:.0f} % ease)")
    q = Ct / 4
    nw = C.val("neck_width_half", m["neck"] / 5 + 15 + o["neck_extra"], "neck / 5 + 1.5 cm")
    fnd = C.val("front_neck_depth", nw + (25 if adult else 15) + (60 if o["neckline"] == "v" else 0) + o["neck_extra"],
                "neck_width_half + " + ("2.5 cm" if adult else "1.5 cm") + (" + 6 cm (V-neck)" if o["neckline"] == "v" else ""))
    bnd = C.val("back_neck_depth", (20 if adult else 15), "fixed")
    sh = C.val("shoulder_length", m["shoulder"] + {"slim": -5, "normal": 0, "wide": 15, "oversized": 0.04 * m["chest"],
                                                   "harem": 15}[o["fit"]], f"shoulder + allowance for fit '{o['fit']}'")
    slope = math.radians(C.val("shoulder_slope", 17.0, "fixed", unit="°"))
    drop = sh * math.tan(slope)
    sx, sy = nw + sh * math.cos(slope), -drop
    ad = 0.18 * Ct + 25 + (0.03 * Ct if o["fit"] in ("wide", "oversized") else 0)
    ad_how = "18 % of chest_width + 2.5 cm" + (" + 3 %" if o["fit"] in ("wide", "oversized") else "")
    if o["armhole_depth_max"] and ad > o["armhole_depth_max"]:
        ad, ad_how = o["armhole_depth_max"], ad_how + ", limited to option armhole_depth_max"
    AD = C.val("armhole_depth", ad, ad_how)
    L = C.val("body_length", o["body_length"] or (m["back_length"] + 0.13 * m["height"]
                                                  + (0.12 * m["height"] if o["length"] == "tunic" else 0)),
              "option body_length" if o["body_length"] else "back length + 13 % of height"
              + (" + 12 % (tunic)" if o["length"] == "tunic" else ""))
    return dict(Ct=Ct, q=q, nw=nw, fnd=fnd, bnd=bnd, sx=sx, sy=sy, AD=AD, L=L, be=be, stretch=stretch,
                knit=knit, sh=sh)


def _armhole(sx, sy, q, AD, scoop, nw):
    U = G.P(q, -AD)
    S = G.P(sx, sy)
    sdir = G.unit(G.P(nw, 0) - S)                # shoulder line towards the neck point
    arrive = np.array([sdir[1], -sdir[0]])       # ⟂ shoulder, upwards
    if arrive[1] < 0:
        arrive = -arrive
    return G.tangent_curve(U, (-1, 0), S, arrive, scoop, 0.45)


def _body_piece(key, name, F, depth, scoop, o, hem_y, flare, notches):
    nw, q = F["nw"], F["q"]
    N = G.P(nw, 0)
    S = G.P(F["sx"], F["sy"])
    sdir = G.unit(N - S)
    # neckline: leaves N perpendicular to the shoulder, reaches the centre horizontally
    leave = np.array([sdir[1], -sdir[0]])
    if leave[1] > 0:
        leave = -leave
    if o["neckline"] == "v" and key == "front":
        mid = G.P(nw * 0.45, -depth * 0.42)
        neck = G.join(G.tangent_curve(N, leave, mid, G.unit(G.P(0, -depth) - mid), 0.4, 0.3),
                      G.line(mid, G.P(0, -depth)))
    else:
        neck = G.tangent_curve(N, leave, G.P(0, -depth), (-1, 0), 0.55, 0.55)
    arm = _armhole(F["sx"], F["sy"], q, F["AD"], scoop, nw)
    hem_out = G.P(q + flare, hem_y)
    side = G.tangent_curve(hem_out, (0, 1), G.P(q, -F["AD"]), (0, 1), 0.3, 0.3) if flare else G.line(hem_out, G.P(q, -F["AD"]))
    hem = G.line(G.P(0, hem_y), hem_out)
    edges = [
        Edge("center", G.line(G.P(0, -depth), G.P(0, hem_y)), 0.0, True, "Centre (fold)"),
        Edge("hem", hem, o["sa"] if o["hem_band"] else o["hem_sa"], label="Hem",
             turned=not o["hem_band"]),
        Edge("side", side, o["sa"], label="Side seam"),
        Edge("armhole", arm, o["sa"], label="Armhole"),
        Edge("shoulder", G.line(S, N), o["sa"], label="Shoulder"),
        Edge("neckline", neck, o["sa"] * 0.7, label="Neckline",
             pointed=o["neckline"] == "v" and key == "front"),
    ]
    gx = q * 0.45
    p = Piece(key, name, edges, cut_count=1, mirror=False, fabric="Main fabric",
              grain=(G.P(gx, -F["AD"] - 20), G.P(gx, hem_y + 40)))
    p.notches += notches
    if key == "back" and o["back_opening"]:
        open_back(p, opening_sa(o))
    return p


def opening_sa(o) -> float:
    """Allowance of a back opening edge: overlap for Velcro/snaps plus turn-under."""
    return float(o["opening_sa"] or 2.5 * o["sa"])


def open_back(piece, osa: float, length: float | None = None, sa: float | None = None) -> None:
    """Turn the centre (fold) edge of a back piece into a back opening.

    The piece is then cut twice (mirrored). With `length` only the top part of the centre
    edge (measured from its start) is the opening; the rest becomes a centre back seam with
    allowance `sa`."""
    ce = piece.edge("center")
    i = piece.edge_index("center")
    L = G.length(ce.pts)
    piece.cut_count, piece.mirror = 2, True
    if length is None or length >= L - 1.0:
        ce.fold, ce.sa, ce.turned = False, osa, True
        ce.label = "Back opening (turn under)"
        return
    # not "turned": below the opening the edge continues as a seam (clip the allowance at the notch)
    top = Edge("center_open", G.sub(ce.pts, 0.0, length), osa, False, "Back opening (turn under)")
    rest = Edge("center", G.sub(ce.pts, length, L), sa, False, "Centre back seam")
    piece.edges[i:i + 1] = [top, rest]
    piece.notches.append(Notch("center", 0.0, 2))


def _sleeve(F, o, m, cap_target, adult):
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    arm_ease = {"slim": 0.08, "normal": 0.18, "wide": 0.30, "oversized": 0.40, "harem": 0.30}[o["fit"]]
    if not knit:
        arm_ease += 0.08
    SW = o["bicep_total"] or m["upper_arm"] * (1 + arm_ease)
    sl_full = m["arm"] + 10 - (F["sx"] - F["nw"] - m["shoulder"])   # subtract the dropped shoulder
    SL0 = o["sleeve_len_total"] or {"short": 0.0, "3/4": 0.72 * sl_full, "long": sl_full}[o["sleeve_length"]]
    cuff_h = (o["cuff_h"] or (40 if adult else 30) * 1.0) if o["sleeve_cuffs"] else 0.0
    if o["sleeve_opening"]:
        op = o["sleeve_opening"]
    elif o["sleeve_length"] == "short":
        op = SW * o["sleeve_taper"]
    elif o["sleeve_cuffs"]:
        op = None
    else:
        op = max(m["wrist"] * 1.6, SW * 0.55) if o["sleeve_length"] == "long" else SW * 0.75
    cuff_len = 0.0
    if o["sleeve_cuffs"]:
        cuff_len = o["sleeve_opening"] or m["wrist"] * 1.45
        op = cuff_len / E.band_ratio(o["band_fabric"], o["band_stretch"])

    def build(CH):
        top = G.P(0, 0)
        Uf, Ub = G.P(SW / 2, -CH), G.P(-SW / 2, -CH)
        a, b = 0.5, 0.5
        kf = G.cubic(Uf, Uf + np.array([-a * SW / 2, 0.0]), top + np.array([b * SW / 2, 0.0]), top)
        kb = G.mirror_x(kf, 0)[::-1]       # top → back bottom
        return kf, kb, Uf, Ub

    lo, hi = 10.0, SW * 1.4
    for _ in range(60):
        CH = (lo + hi) / 2
        kf, kb, _, _ = build(CH)
        if G.length(kf) * 2 < cap_target:
            lo = CH
        else:
            hi = CH
    CH = (lo + hi) / 2
    kf, kb, Uf, Ub = build(CH)
    SL = SL0 if SL0 else CH + max(0.1 * m["arm"], 50.0 if cuff_h else 35.0) + cuff_h   # short: sleeve seam ≥ 3.5 cm (+ cuff)
    hem_y = -(SL - cuff_h)
    hf, hb = G.P(op / 2, hem_y), G.P(-op / 2, hem_y)
    nv = G.tangent_curve(Uf, (0, -1), hf, (0, -1), 0.35, 0.35)[::-1]   # hem front → underarm
    nh = G.tangent_curve(Ub, (0, -1), hb, (0, -1), 0.35, 0.35)
    edges = [
        Edge("cap_back", kb, o["sa"], label="Sleeve cap back"),
        Edge("seam_back", nh, o["sa"], label="Sleeve seam"),
        Edge("hem", G.line(hb, hf), o["sa"] if o["sleeve_cuffs"] else o["hem_sa"], label="Sleeve hem",
             turned=not o["sleeve_cuffs"]),
        Edge("seam_front", nv, o["sa"], label="Sleeve seam"),
        Edge("cap_front", kf, o["sa"], label="Sleeve cap front"),
    ]
    p = Piece("sleeve", "Sleeve", edges, cut_count=2, mirror=True, fabric="Main fabric",
              grain=(G.P(0, -(lo + hi) / 2 - 15), G.P(0, hem_y + 30)))
    p.notches += [Notch("cap_front", -1.0, 1), Notch("cap_front", G.length(kf) * 0.45, 1),
                  Notch("cap_back", G.length(kb) * 0.55, 2)]
    return p, dict(SW=SW, SL=SL, cuff_h=cuff_h, cuff_len=cuff_len, op=op)


def _raglan(front, back, F, o, m, adult):
    """Raglan: separate the sleeve part from the body and transfer the raglan lines rigidly to the sleeve."""
    curves = {}
    for pc, _depth in ((front, F["fnd"]), (back, F["bnd"])):
        neck = pc.edge("neckline").pts           # N → centre
        s_cut = G.length(neck) * 0.35
        Pn = G.point_at(neck, s_cut)
        U = G.P(F["q"], -F["AD"])
        t = G.tangent_at(neck, s_cut)                # neckline direction (towards the centre)
        arr = np.array([-t[1], t[0]])
        if arr[1] < 0:
            arr = -arr
        rag = G.tangent_curve(U, (-1, 0), Pn, arr, 0.45, 0.35)
        neck_rest = G.sub(neck, s_cut, G.length(neck))
        neck_part = G.length(neck) - G.length(neck_rest)
        e = pc.edges
        new = [e[0], e[1], e[2], Edge("raglan", rag, o["sa"], label="Raglan seam"),
               Edge("neckline", neck_rest, e[5].sa, label="Neckline", pointed=e[5].pointed)]
        pc.edges = new
        curves[pc.key] = (rag, neck_part)
    rf, npf = curves["front"]
    rb, npb = curves["back"]
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    t = npf + npb
    cf = np.linalg.norm(rf[-1] - rf[0])
    cb = np.linalg.norm(rb[-1] - rb[0])
    arm_ease = {"slim": 0.08, "normal": 0.18, "wide": 0.30, "oversized": 0.40, "harem": 0.30}[o["fit"]]
    SWh = max((o["bicep_total"] or m["upper_arm"] * (1 + arm_ease)) / 2, t / 2 + 20)
    dx = SWh - t / 2
    dy = math.sqrt(max(cf ** 2 - dx ** 2, (0.3 * cf) ** 2))
    Nf, Uf = G.P(t / 2, 0), G.P(t / 2 + math.sqrt(max(cf ** 2 - dy ** 2, 1)), -dy)
    Nb = G.P(-t / 2, 0)
    Ub = G.P(-t / 2 - math.sqrt(max(cb ** 2 - dy ** 2, 1)), -dy)
    kf = G.rigid_place(rf, rf[0], rf[-1], Uf, dst_b=Nf)                 # U → N (front, right)
    kb_m = G.mirror_x(rb, 0.0)
    kb = G.rigid_place(kb_m, kb_m[0], kb_m[-1], Ub, dst_b=Nb)            # U → N (back, left)
    shift = np.array([-(Uf[0] + Ub[0]) / 2, 0.0])                      # underarm points symmetric
    kf, kb = kf + shift, kb + shift
    Uf, Ub, Nf, Nb = Uf + shift, Ub + shift, Nf + shift, Nb + shift
    sl_full = m["arm"] + 10 + m["shoulder"] * 0.85
    SL = o["sleeve_len_total"] or {"short": dy + max(0.1 * m["arm"], 35.0), "3/4": 0.72 * sl_full,
                                   "long": sl_full}[o["sleeve_length"]]
    cuff_h = (o["cuff_h"] or (40 if adult else 30)) if o["sleeve_cuffs"] else 0.0
    SL = max(SL, dy + cuff_h + 35.0)
    hem_y = -(SL - cuff_h)
    SW = (Uf[0] - Ub[0])
    if o["sleeve_cuffs"]:
        cuff_len = o["sleeve_opening"] or m["wrist"] * 1.45
        op = cuff_len / E.band_ratio(o["band_fabric"], o["band_stretch"])
    else:
        cuff_len = 0.0
        op = o["sleeve_opening"] or (SW * o["sleeve_taper"] if o["sleeve_length"] == "short"
                                     else max(m["wrist"] * 1.6, SW * 0.55))
    # sleeve seams leave the underarm perpendicular to the raglan line
    def perp(k, side):
        d = G.start_dir(k)                          # direction U → N
        p_ = np.array([d[1], -d[0]])
        if p_[1] > 0:
            p_ = -p_
        return p_ if side > 0 else np.array([-p_[0], p_[1]])   # back mirrored
    def seam(U, side, k, dx=0.0):
        H = G.P(side * op / 2 + dx, hem_y)
        return G.tangent_curve(U, perp(k, side), H, (0, -1), 0.25, 0.3)
    # neck edge: perpendicular to both raglan lines (smooth transition to the body neckline)
    d1 = G.end_dir(kf)
    h0 = np.array([d1[1], -d1[0]])
    if h0[0] > 0:
        h0 = -h0
    d2 = G.end_dir(kb)                      # kb runs U → N
    h1 = np.array([d2[1], -d2[0]])
    if h1[0] > 0:
        h1 = -h1
    hals = G.tangent_curve(Nf, h0, Nb, h1, 0.35, 0.35)
    # right angles at both underarms; match the back length via the hem point
    pf_ = perp(kf, 1)
    pb_ = perp(kb, -1)
    pb_ = np.array([-pb_[0], pb_[1]])
    sf = G.tangent_curve(Uf, pf_, G.P(op / 2, hem_y), (0, -1), 0.25, 0.3)
    target = G.length(sf)
    lo_, hi_ = 0.02, 0.7
    for _ in range(40):
        kk = (lo_ + hi_) / 2
        sb = G.tangent_curve(Ub, pb_, G.P(-op / 2, hem_y), (0, -1), kk, 0.3)
        if G.length(sb) > target:
            hi_ = kk
        else:
            lo_ = kk
    edges = [
        Edge("raglan_back", kb[::-1], o["sa"], label="Raglan seam back"),
        Edge("seam_back", sb, o["sa"], label="Sleeve seam"),
        Edge("hem", G.line(sb[-1], sf[-1]), o["sa"] if o["sleeve_cuffs"] else o["hem_sa"], label="Sleeve hem",
             turned=not o["sleeve_cuffs"]),
        Edge("seam_front", sf[::-1], o["sa"], label="Sleeve seam"),
        Edge("raglan_front", kf, o["sa"], label="Raglan seam front"),
        Edge("neck", hals, o["sa"] * 0.7, label="Neckline"),
    ]
    p = Piece("sleeve", "Raglan sleeve", edges, cut_count=2, mirror=True, fabric="Main fabric",
              grain=(G.P(0, -dy - 10), G.P(0, hem_y + 30)))
    p.notches += [Notch("raglan_front", -15.0, 1), Notch("raglan_back", 15.0, 2)]
    return p, dict(SW=SW, SL=SL, cuff_h=cuff_h, cuff_len=cuff_len, op=op)


def draft(measures: dict, options: dict | None = None, _garment="tshirt_basic") -> Pattern:
    o = resolve_options(options)
    m = measures
    adult = m["height"] > 1650 and m["chest"] > 780
    C = Construction(o.get("construction"))
    F = _body_frame(m, o, adult, C)
    hem_band_h = (o["hem_band_h"] or (60 if adult else 45)) if o["hem_band"] else 0.0
    hem_y = -(F["L"] - hem_band_h)
    flare = 0.0 if o["hem_band"] or o["fit"] == "slim" else F["q"] * 0.04
    if o["hem_total"] and not o["hem_band"]:
        flare = max(-0.15 * F["q"], o["hem_total"] / 4 - F["q"])
    front = _body_piece("front", "Front", F, F["fnd"], 0.62, o, hem_y, flare,
                        [Notch("armhole", G.length(_armhole(F["sx"], F["sy"], F["q"], F["AD"], 0.62, F["nw"])) * 0.45, 1)])
    back = _body_piece("back", "Back", F, F["bnd"], 0.5, o, hem_y, flare,
                       [Notch("armhole", G.length(_armhole(F["sx"], F["sy"], F["q"], F["AD"], 0.5, F["nw"])) * 0.45, 2)])
    fab = o["fabric"]
    seams, corners, checks, notes = [], [], [], []
    if o["sleeve_style"] == "raglan":
        sleeve, sinfo = _raglan(front, back, F, o, m, adult)
        front.notches = [n for n in front.notches if n.edge != "armhole"]
        back.notches = [n for n in back.notches if n.edge != "armhole"]
        front.notches.append(Notch("raglan", -15.0, 1))
        back.notches.append(Notch("raglan", -15.0, 2))
        seams += [
            dict(name="Raglan seam front: front ↔ sleeve", a=[("front", "raglan", 1)],
                 b=[("sleeve", "raglan_front", 1)], type="equal"),
            dict(name="Raglan seam back: back ↔ sleeve", a=[("back", "raglan", 1)],
                 b=[("sleeve", "raglan_back", 1)], type="equal"),
        ]
        neck_parts = [("front", "neckline", 2), ("back", "neckline", 2), ("sleeve", "neck", 2)]
        corners += [dict(name="Underarm: side seam ↔ raglan (body)", piece="front", a="side", b="raglan",
                         target=90),
                    dict(name="Underarm: sleeve seam ↔ raglan (sleeve front)", piece="sleeve", a="seam_front",
                         b="raglan_front", target=90)]
    else:
        cap_target = G.length(front.edge("armhole").pts) + G.length(back.edge("armhole").pts) + \
            E.cap_ease_target_mm(fab)
        sleeve, sinfo = _sleeve(F, o, m, cap_target, adult)
        lo, hi = E.cap_ease_range_mm(fab)
        seams.append(dict(name="Armhole ↔ sleeve cap (ease)",
                          a=[("front", "armhole", 1), ("back", "armhole", 1)],
                          b=[("sleeve", "cap_front", 1), ("sleeve", "cap_back", 1)], type="ease",
                          lo=lo, hi=hi, note=f"{E.fabric_info(fab)[0]}: {lo:.0f}–{hi:.0f} mm"))
        seams.append(dict(name="Shoulder seam front ↔ back", a=[("front", "shoulder", 1)],
                          b=[("back", "shoulder", 1)], type="equal"))
        neck_parts = [("front", "neckline", 2), ("back", "neckline", 2)]
        corners += [
            dict(name="Underarm: side seam ↔ armhole front", piece="front", a="side", b="armhole", target=90),
            dict(name="Underarm: side seam ↔ armhole back", piece="back", a="side", b="armhole", target=90),
            dict(name="Shoulder ↔ armhole (front + back)", sum=[("front", "armhole", "shoulder"),
                                                                ("back", "armhole", "shoulder")], target=180),
            dict(name="Sleeve cap top (smooth)", piece="sleeve", a="cap_front", b="cap_back", target=180),
            dict(name="Sleeve underarm ↔ cap front", piece="sleeve", a="seam_front", b="cap_front", target=90),
            dict(name="Shoulder ↔ neckline (front + back)", sum=[("front", "shoulder", "neckline"),
                                                                   ("back", "shoulder", "neckline")],
                 target=180),
        ]
    pieces = [front, back, sleeve]
    seams.insert(0, dict(name="Side seam front ↔ back", a=[("front", "side", 1)],
                         b=[("back", "side", 1)], type="equal"))
    seams.append(dict(name="Sleeve seam (front ↔ back)", a=[("sleeve", "seam_front", 1)],
                      b=[("sleeve", "seam_back", 1)], type="equal"))
    corners += [
        dict(name="Neckline at centre front", piece="front", a="neckline", b="center",
             target=90 if o["neckline"] != "v" else _v_angle(front), note="" if o["neckline"] != "v" else "V point (intended angle)"),
        dict(name="Neckline at centre back", piece="back", a="neckline", b="center", target=90),
        dict(name="Hem at centre front", piece="front", a="center", b="hem", target=90),
        dict(name="Hem ↔ side seam front", piece="front", a="hem", b="side", target=90),
    ]
    # neckband
    stretch = F["stretch"]
    neck_len = sum(pieces[[p.key for p in pieces].index(k)].edge(e).length * n for k, e, n in neck_parts)
    nb_h = o["neck_band_h"] or (25 if adult else 20)
    if o["neck_finish"] == "bias":
        # bias binding: a strip as long as the neckline, folded lengthwise and sewn on flat;
        # its ends are turned in at the back opening (or joined at a shoulder)
        nb_h = o["neck_band_h"] or max(4.0, 0.6 * o["sa"])
        band = rect_piece("neckband", "Neck binding (bias)", neck_len, 2 * nb_h, sa=o["sa"] * 0.7, cut_count=1,
                          fabric="Main fabric", labels=("Seam edge", "End", "Seam edge", "End"),
                          grain_vertical=False)
        band.grain = (G.P(neck_len * 0.3, nb_h * 0.2), G.P(neck_len * 0.3 + nb_h * 1.6, nb_h * 1.8))
        band.info.append("cut on the bias (45°)")
        band.marks.append(Mark(G.line(G.P(0, nb_h), G.P(neck_len, nb_h)), "fold", "Fold line"))
        pieces.append(band)
        seams.append(dict(name="Neck binding ↔ neckline", a=neck_parts, b=[("neckband", "bottom", 1)],
                          type="equal"))
        nbl = neck_len
    else:
        ratio = E.band_ratio(o["band_fabric"], o["band_stretch"])
        if o["neckline"] == "v":
            ratio = min(0.95, ratio + 0.05)
        nbl = neck_len * ratio
        band = rect_piece("neckband", "Neckband", nbl, 2 * nb_h, sa=o["sa"] * 0.7, cut_count=1,
                          fabric="Rib knit" if o["band_fabric"] == "rib" else "Main fabric",
                          labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"), grain_vertical=True)
        band.marks.append(Mark(G.line(G.P(0, nb_h), G.P(nbl, nb_h)), "fold", "Fold line"))
        band.stretch_dir = "Stretch direction: along the length"
        pieces.append(band)
        lo_r, hi_r = E.band_ratio_range(o["band_fabric"])
        seams.append(dict(name="Neckband ↔ neckline (stretched)", a=neck_parts, b=[("neckband", "bottom", 1)],
                          type="ratio", lo=lo_r, hi=min(0.97, hi_r + (0.05 if o["neckline"] == "v" else 0))))
    b_stretch = E.fabric_info(o["band_fabric"], o["band_stretch"])[1]
    if o["back_opening"]:
        # the garment opens at the back: the head goes through the neckline plus both opening edges
        open_len = back.edge("center").length
        checks.append(dict(name="Head fits through the back opening", kind="min",
                           value=neck_len * (1 + stretch / 100) + 2 * open_len, target=m["head"] * 1.05,
                           note="neckline + both edges of the back opening ≥ head circumference + 5 %"))
    else:
        deficit = m["head"] * 1.03 - neck_len * (1 + stretch / 100)
        if deficit > 0 and o.get("_auto_neck", 0) < 8:
            # enlarge the neckline automatically until it fits over the head
            opts2 = dict(options or {})
            opts2["neck_extra"] = o["neck_extra"] + deficit / 5.0 + 2.0
            opts2["_auto_neck"] = o.get("_auto_neck", 0) + 1
            return draft(measures, opts2, _garment)
        if o["neck_extra"] > 0 and o.get("_auto_neck"):
            notes.append(f"Neckline enlarged by {o['neck_extra'] / 10:.1f} cm so that it fits over the head.")
        if o["neck_finish"] != "bias":
            checks.append(dict(name="Neckline fits over the head", kind="min",
                               value=nbl * (1 + b_stretch / 100), target=m["head"] * 1.0,
                               note="neckband length incl. usable stretch ≥ head circumference"))
        checks.append(dict(name="Neckline (fabric edge) fits over the head", kind="min",
                           value=neck_len * (1 + stretch / 100), target=m["head"] * 1.0,
                           note="neckline incl. stretch ≥ head circumference"))
    if o["sleeve_cuffs"]:
        cuff = rect_piece("sleeve_cuff", "Sleeve cuff", sinfo["cuff_len"], 2 * sinfo["cuff_h"], sa=o["sa"],
                          cut_count=2, fabric="Rib knit", labels=("Seam edge", "Cross seam", "Seam edge", "Cross seam"))
        cuff.marks.append(Mark(G.line(G.P(0, sinfo["cuff_h"]), G.P(sinfo["cuff_len"], sinfo["cuff_h"])), "fold",
                               "Fold line"))
        pieces.append(cuff)
        seams.append(dict(name="Sleeve cuff ↔ sleeve hem (stretched)", a=[("sleeve", "hem", 1)],
                          b=[("sleeve_cuff", "bottom", 1)], type="ratio", lo=0.70, hi=0.85))
        checks.append(dict(name="Hand fits through the sleeve cuff", kind="min",
                           value=sinfo["cuff_len"] * (1 + b_stretch / 100), target=m["wrist"] * 1.55,
                           note="hand circumference ≈ 1.55 × wrist"))
    if o["hem_band"]:
        hb_len = (front.edge("hem").length + back.edge("hem").length) * 2 * E.band_ratio(o["band_fabric"], o["band_stretch"])
        hband = rect_piece("hem_band", "Hem band", hb_len / 2, 2 * hem_band_h, sa=o["sa"], cut_count=1,
                           fold_left=True, fabric="Rib knit" if o["band_fabric"] == "rib" else "Main fabric",
                           labels=("Seam edge", "Cross seam", "Seam edge", "Centre"))
        hband.marks.append(Mark(G.line(G.P(0, hem_band_h), G.P(hb_len / 2, hem_band_h)), "fold", "Fold line"))
        pieces.append(hband)
        seams.append(dict(name="Hem band ↔ hem (stretched)", a=[("front", "hem", 2), ("back", "hem", 2)],
                          b=[("hem_band", "bottom", 2)], type="ratio", lo=0.70, hi=0.92))
    # ease check
    pat = Pattern(_garment, "T-Shirt" if o["sleeve_length"] == "short" else "Long-sleeve shirt", "", pieces, dict(m), o,
                  seams=seams, corners=corners, checks=checks, notes=notes)
    fin = finished_measures(pat, F=F, sinfo=sinfo, hem_band_h=hem_band_h, nb_h=nb_h)
    pat.finished = fin
    pat.options.update(_F=F, _sinfo=sinfo, _hem_band_h=hem_band_h, _nb_h=nb_h)
    checks.insert(0, dict(name="Chest circumference pattern = body + ease", kind="circ", value=fin["chest_circ"],
                          target=F["Ct"], tol_rel=0.01,
                          note=f"body {m['chest'] / 10:.1f} cm + {F['be'] * 100:+.0f} % ease"
                          if not o["chest_total"] else "target from measurement/override"))
    if o["sleeve_length"] == "long":
        checks.append(dict(name="Sleeve length plausible", kind="range", value=fin["sleeve_len"],
                           lo=m["arm"] * 0.9, hi=m["arm"] * 1.25, note=f"arm length {m['arm'] / 10:.1f} cm"))
    checks.append(dict(name="Body length plausible", kind="range", value=fin["length"],
                       lo=0.30 * m["height"], hi=0.62 * m["height"], note="from the neck point"))
    pat.construction = C.rows()
    if C.unknown_overrides():
        pat.notes.append("Unknown construction value(s) ignored: " + ", ".join(C.unknown_overrides()))
    return pat


def _v_angle(front):
    return G.corner_angle(front.edge("neckline").pts, front.edge("center").pts)


def finished_measures(pat, F=None, sinfo=None, hem_band_h=None, nb_h=None):
    o = pat.options
    F = F or o["_F"]
    sinfo = sinfo or o["_sinfo"]
    hem_band_h = o.get("_hem_band_h", 0.0) if hem_band_h is None else hem_band_h
    f, b = pat.piece("front"), pat.piece("back")
    y = -F["AD"] - 25
    chest = 2 * (G.width_at_y(f.seam_ring(), y) + G.width_at_y(b.seam_ring(), y))
    hem = 2 * (f.edge("hem").length + b.edge("hem").length)
    if pat.has("hem_band"):
        hem = pat.piece("hem_band").edge("bottom").length * 2
    length = -float(f.edge("hem").pts[0, 1]) + hem_band_h
    neck = sum(e.length for e in [f.edge("neckline"), b.edge("neckline")]) * 2
    if pat.piece("sleeve").edges[-1].name == "neck":
        neck += 2 * pat.piece("sleeve").edge("neck").length
    return dict(chest_circ=chest, hem_circ=hem, length=length, sleeve_len=sinfo["SL"],
                sleeve_opening=(sinfo["cuff_len"] if sinfo["cuff_len"] else sinfo["op"]),
                bicep_circ=sinfo["SW"], neckline=neck)


FINISHED_LABELS = {
    "chest_circ": ("Chest width", "width"), "hem_circ": ("Hem width", "width"), "length": ("Length from neck point", "length"),
    "sleeve_len": ("Sleeve length", "length"), "sleeve_opening": ("Sleeve opening", "width"),
    "bicep_circ": ("Upper-arm width", "width"), "neckline": ("Neckline circumference", "width"),
}


def back_opening_steps(pat, edge: str | None = None) -> list:
    """Finish the centre back opening and close it with Velcro (doll clothes, small children)."""
    import steps as S
    o = pat.options
    osa = opening_sa(o)
    b = pat.piece("back")
    edge = edge or ("center_open" if any(e.name == "center_open" for e in b.edges) else "center")
    sec = "Back opening"
    return [
        S.finish("Finish the opening edges", [("back", edge)], "Both centre back edges.", repeat=2,
                 section=sec),
        S.hem("Turn in the opening edges", [("back", edge)], osa,
              f"Press {S.cm(osa)} to the inside and stitch it down.", stitch="topstitch", repeat=2, section=sec),
        S.icon("Sew on the Velcro", "velcro",
               "The edges overlap at the centre back: soft side on the left back, hook side on the right back "
               "(or 2–3 snaps).", stitch="topstitch", section=sec,
               tip="The garment opens completely: easy dressing."),
    ]


def assembly(pat, hem: bool = True, neck: bool = True, open_bands: bool = False, done: bool = True) -> list:
    """The construction as one-action steps (see steps.py).

    hem/neck=False leave out the hem and the neckline (dress, hoodie with hood);
    open_bands: neckband and hem band are not closed into rings (zip front)."""
    import steps as S
    o = pat.options
    knit = E.fabric_info(o["fabric"])[2]
    out: list = []
    sa = S.cm(pat.piece("front").edge("side").sa)

    def finished(title, edges):
        if S.needs_finish(o, knit):
            out.append(S.finish(title, edges, "Both allowances together; press them towards the back.",
                                repeat=2, section=out[-1].section))

    if o["sleeve_style"] == "raglan":
        out.append(S.seam("Sew the raglan seams", ["Raglan seam"],
                          "Sleeve right sides together to front and back; single notches at the front, double at "
                          "the back.", repeat=2, section="Sleeves"))
        finished("Finish the raglan seams", [("sleeve", "raglan_front"), ("sleeve", "raglan_back")])
    else:
        out.append(S.seam("Sew the shoulder seams", ["Shoulder seam"],
                          "Lay front and back right sides together, shoulder edges level, and pin. "
                          f"Sew with {sa} seam allowance from the neckline to the armhole. "
                          "Press the allowances towards the back.", repeat=2, section="Shoulders",
                          hint=("Knit stretches at the shoulder: sew a strip of clear elastic or twill tape "
                                "into the seam." if knit else "")))
        finished("Finish the shoulder seams", [("front", "shoulder"), ("back", "shoulder")])
    if o.get("back_opening"):
        out += back_opening_steps(pat)
    if neck and pat.has("neckband"):
        sec = "Neckline"
        nb = pat.piece("neckband")
        if o.get("neck_finish") == "bias":
            out += [
                S.fold_band("Fold the binding in half", "neckband", "Lengthwise, wrong sides together; press.",
                            section=sec),
                S.seam("Sew the neck binding on", ["Neck binding"],
                       "Raw edges to the neckline, right sides together; let each end stick out past the opening "
                       "edge by the allowance.", section=sec),
                S.topstitch("Stitch the binding down", [("front", "neckline"), ("back", "neckline")], 2.0,
                            "Fold the ends in, turn the binding to the inside over the allowance and stitch close "
                            "to the fold.", section=sec),
            ]
        elif o.get("back_opening") or open_bands:
            out += [
                S.fold_band("Fold the neckband in half", "neckband", "Lengthwise, wrong sides together.",
                            section=sec),
                S.attach_band("Sew the neckband on", "neckband", ["Neckband"], "neckline",
                              "Right sides together, stretching it slightly, from one front/opening edge to the "
                              "other; fold the ends in.", section=sec),
            ]
        else:
            out += [
                S.ring("Close the neckband into a ring", "neckband", "Right sides together across the short ends.",
                       section=sec),
                S.fold_band("Fold the neckband in half", "neckband", "Lengthwise, wrong sides together.",
                            section=sec),
                S.quarter("Mark quarters", "neckband", "neckline",
                          "Band: cross seam = centre back. Neckline: centre front, centre back, shoulders.",
                          section=sec, data={"quarters": "neck"}),
                S.attach_band("Sew the neckband on", "neckband", ["Neckband"], "neckline",
                              "Right sides together, raw edges meet; stretch the band, not the neckline.",
                              section=sec),
                S.topstitch("Press the allowance down and topstitch", [("front", "neckline"), ("back", "neckline")],
                            6.0, "Optional, gives a flat, professional neckline.", section=sec),
            ]
        del nb
    if o["sleeve_style"] != "raglan":
        out.append(S.seam("Set in the sleeves", ["Armhole"],
                          "Open the body out flat, right side up. "
                          "Lay the sleeve right side down on the armhole: top of the cap on the shoulder seam, "
                          "single notch on the front, double notch on the back. "
                          "Pin from the middle to both ends, easing in the extra length of the cap. "
                          f"Sew with {sa} seam allowance, sleeve underneath; press the allowances towards the "
                          "sleeve.", repeat=2, section="Sleeves",
                          tip="Sleeve on the bottom: the feed dogs ease the cap in without pleats.",
                          data={"view": "flat_sleeve"}))
        finished("Finish the armhole seams", [("sleeve", "cap_front"), ("sleeve", "cap_back")])
    out.append(S.seam("Sew side and sleeve seams", ["Side seam", "Sleeve seam"],
                      "Fold the garment right sides together at the shoulders, the sleeves folded in half lengthwise. "
                      "Pin side and sleeve seam so that the " +
                      ("raglan" if o["sleeve_style"] == "raglan" else "armhole") +
                      " seams meet exactly at the underarm. "
                      f"Sew in one go with {sa} seam allowance, from the hem over the underarm to the sleeve hem. "
                      "Press the allowances towards the back.",
                      repeat=2, section="Sides", data={"view": "folded"} if o["sleeve_style"] != "raglan" else {},
                      alt=("Cuffs first: sew the cuffs on while the sleeve is still flat, then sew side, sleeve "
                           "and cuff seam in one go. Easier on small sizes." if o["sleeve_cuffs"] and
                           pat.has("sleeve_cuff") else "")))
    finished("Finish the side seams", [("front", "side"), ("back", "side")])
    if o["sleeve_cuffs"] and pat.has("sleeve_cuff"):
        sec = "Cuffs"
        out += [
            S.ring("Close the cuffs into rings", "sleeve_cuff",
                   f"Fold each cuff crosswise right sides together, short edges level. Sew with {sa} seam "
                   "allowance; finger-press the allowances open.", repeat=2, section=sec),
            S.fold_band("Fold the cuffs in half", "sleeve_cuff",
                        "Fold the ring lengthwise wrong sides together, raw edges level. "
                        "The seam allowance is now inside; the right side shows all round.", repeat=2,
                        section=sec, data={"hands": "fold"}),
            S.attach_band("Sew the cuffs on", "sleeve_cuff", ["Sleeve cuff"], "sleeve hem",
                          "Turn the sleeve right side out. Slide the cuff over the sleeve end, raw edges level, "
                          "cuff seam on the sleeve seam. Pin at the quarters. "
                          "Sew with the cuff on top, stretching the cuff (not the sleeve) to the length of the "
                          "sleeve between two pins.", repeat=2, section=sec,
                          hint="One hand in front of the presser foot, one behind it: both stretch evenly.",
                          data={"hands": "stretch"}),
        ]
    else:
        hs = pat.piece("sleeve").edge("hem").sa
        out.append(S.hem("Hem the sleeves", [("sleeve", "hem")], hs, f"Press {S.cm(hs)} to the inside.",
                         repeat=2, section="Sleeve hems"))
    if hem:
        sec = "Hem"
        if o["hem_band"] and pat.has("hem_band"):
            if not open_bands:
                out.append(S.ring("Close the hem band into a ring", "hem_band",
                                  "Fold the band crosswise right sides together, short edges level. "
                                  f"Sew with {sa} seam allowance; finger-press the allowances open.", section=sec))
            out.append(S.fold_band("Fold the hem band in half", "hem_band",
                                   "Fold lengthwise wrong sides together, raw edges level; press lightly.",
                                   section=sec, data={"hands": "fold"}))
            if not open_bands:
                out.append(S.quarter("Mark quarters", "hem_band", "hem",
                                     "Band: put a pin at the cross seam and fold the band flat to find the "
                                     "opposite point; fold again for the two quarter points. "
                                     "Garment: pins at centre front, centre back and both side seams.",
                                     section=sec, data={"quarters": "hem"}))
            out.append(S.attach_band("Sew the hem band on", "hem_band", ["Hem band"], "hem",
                                     "Garment right side out: slide the band over it, raw edges level"
                                     + ("; band ends flush with the front edges." if open_bands else
                                        ", cross seam on a side seam; match the quarter pins.")
                                     + f" Sew with {sa} seam allowance, band on top, stretching only the band. "
                                     "Press the allowances towards the garment.",
                                     section=sec, data={"hands": "stretch"},
                                     hint="Sew a little slower over the side seams: four layers."))
        else:
            hs = pat.piece("front").edge("hem").sa
            out.append(S.hem("Sew the hem", [("front", "hem"), ("back", "hem")], hs,
                             f"Press {S.cm(hs)} to the inside.", section=sec))
    if done:
        out.append(S.done())
    return out


def sewing_steps(pat):
    import steps as S
    return S.as_texts(assembly(pat), pat.options)

