"""T-Shirt / Longsleeve: Vorder- und Rückenteil im Bruch, Ärmel, Halsbündchen.
Varianten: eingesetzter Ärmel oder Raglan, kurz/lang/3/4, Rund- oder V-Ausschnitt.

Eigene Konstruktion: Brustweite (inkl. Mehrweite) geviertelt, Armlochtiefe aus der
Brustweite, Schulterschräge ≈ 17°, Ärmelkugelhöhe wird numerisch so bestimmt, dass die
Kugel um die gewünschte Einhaltemenge länger ist als das Armloch.

Koordinaten mm, y nach oben; y = 0 auf Höhe des Halspunkts (Schulter/Hals).
Rumpfteile: Mitte (Bruch) bei x = 0, Seitennaht rechts.
"""
from __future__ import annotations

import math

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Mark, Notch, Pattern, Piece, rect_piece

DEFAULTS = dict(fit="normal", fabric="jersey", stretch=None, sleeve_style="eingesetzt",
                sleeve_length="kurz", neckline="rund", length="normal", band_fabric="buendchen",
                band_stretch=None, sleeve_cuffs=False, hem_band=False, sa=10.0, hem_sa=20.0,
                neck_band_h=None, chest_total=None, body_length=None, sleeve_len_total=None,
                sleeve_opening=None, neck_extra=0.0, cuff_h=None, hem_band_h=None)


def resolve_options(options):
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["sleeve_length"] == "lang" and "sleeve_cuffs" not in (options or {}):
        o["sleeve_cuffs"] = False
    return o


def _body_frame(m, o, adult):
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    be = E.body_ease(o["fit"], o["fabric"], stretch)
    Ct = o["chest_total"] or m["chest"] * (1 + be)
    q = Ct / 4
    nw = m["neck"] / 5 + 15 + o["neck_extra"]                          # halbe Halsausschnittbreite
    fnd = nw + (25 if adult else 15) + (60 if o["neckline"] == "v" else 0) + o["neck_extra"]
    bnd = (20 if adult else 15)
    sh = m["shoulder"] + {"eng": -5, "normal": 0, "weit": 15, "oversized": 0.04 * m["chest"],
                          "harem": 15}[o["fit"]]
    drop = sh * math.tan(math.radians(17))
    sx, sy = nw + sh * math.cos(math.radians(17)), -drop
    AD = 0.18 * Ct + 25 + (0.03 * Ct if o["fit"] in ("weit", "oversized") else 0)
    L = o["body_length"] or (m["back_length"] + 0.13 * m["height"] + (0.12 * m["height"] if o["length"] == "tunika" else 0))
    return dict(Ct=Ct, q=q, nw=nw, fnd=fnd, bnd=bnd, sx=sx, sy=sy, AD=AD, L=L, be=be, stretch=stretch,
                knit=knit, sh=sh)


def _armhole(sx, sy, q, AD, scoop, nw):
    U = G.P(q, -AD)
    S = G.P(sx, sy)
    sdir = G.unit(G.P(nw, 0) - S)                # Schulterlinie Richtung Halspunkt
    arrive = np.array([sdir[1], -sdir[0]])       # ⟂ Schulter, nach oben
    if arrive[1] < 0:
        arrive = -arrive
    return G.tangent_curve(U, (-1, 0), S, arrive, scoop, 0.45)


def _body_piece(key, name, F, depth, scoop, o, hem_y, flare, notches):
    nw, q = F["nw"], F["q"]
    N = G.P(nw, 0)
    S = G.P(F["sx"], F["sy"])
    sdir = G.unit(N - S)
    # Ausschnitt: verlässt N senkrecht zur Schulter, erreicht die Mitte waagerecht
    leave = np.array([sdir[1], -sdir[0]])
    if leave[1] > 0:
        leave = -leave
    if o["neckline"] == "v" and key == "vorderteil":
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
        Edge("mitte", G.line(G.P(0, -depth), G.P(0, hem_y)), 0.0, True, "Mitte (Bruch)"),
        Edge("saum", hem, o["sa"] if o["hem_band"] else o["hem_sa"], label="Saum"),
        Edge("seite", side, o["sa"], label="Seitennaht"),
        Edge("armloch", arm, o["sa"], label="Armloch"),
        Edge("schulter", G.line(S, N), o["sa"], label="Schulter"),
        Edge("ausschnitt", neck, o["sa"] * 0.7, label="Ausschnitt"),
    ]
    gx = q * 0.45
    p = Piece(key, name, edges, cut_count=1, mirror=False, fabric="Oberstoff",
              grain=(G.P(gx, -F["AD"] - 20), G.P(gx, hem_y + 40)))
    p.notches += notches
    return p


def _sleeve(F, o, m, cap_target, adult):
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    arm_ease = {"eng": 0.08, "normal": 0.18, "weit": 0.30, "oversized": 0.40, "harem": 0.30}[o["fit"]]
    if not knit:
        arm_ease += 0.08
    SW = m["upper_arm"] * (1 + arm_ease)
    sl_full = m["arm"] + 10 - (F["sx"] - F["nw"] - m["shoulder"])   # überschnittene Schulter abziehen
    SL0 = o["sleeve_len_total"] or {"kurz": 0.0, "3/4": 0.72 * sl_full, "lang": sl_full}[o["sleeve_length"]]
    cuff_h = (o["cuff_h"] or (40 if adult else 30) * 1.0) if o["sleeve_cuffs"] else 0.0
    if o["sleeve_opening"]:
        op = o["sleeve_opening"]
    elif o["sleeve_length"] == "kurz":
        op = SW * 0.9
    elif o["sleeve_cuffs"]:
        op = None
    else:
        op = max(m["wrist"] * 1.6, SW * 0.55) if o["sleeve_length"] == "lang" else SW * 0.75
    cuff_len = 0.0
    if o["sleeve_cuffs"]:
        cuff_len = o["sleeve_opening"] or m["wrist"] * 1.45
        op = cuff_len / E.band_ratio(o["band_fabric"], o["band_stretch"])

    def build(CH):
        top = G.P(0, 0)
        Uf, Ub = G.P(SW / 2, -CH), G.P(-SW / 2, -CH)
        a, b = 0.5, 0.5
        kf = G.cubic(Uf, Uf + np.array([-a * SW / 2, 0.0]), top + np.array([b * SW / 2, 0.0]), top)
        kb = G.mirror_x(kf, 0)[::-1]       # top → hinten unten
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
    SL = SL0 if SL0 else CH + max(0.1 * m["arm"], 35.0)          # kurz: Ärmelnaht ≥ 3,5 cm
    hem_y = -(SL - cuff_h)
    hf, hb = G.P(op / 2, hem_y), G.P(-op / 2, hem_y)
    nv = G.tangent_curve(Uf, (0, -1), hf, (0, -1), 0.35, 0.35)[::-1]   # Saum vorne → Achsel
    nh = G.tangent_curve(Ub, (0, -1), hb, (0, -1), 0.35, 0.35)
    edges = [
        Edge("kugel_hinten", kb, o["sa"], label="Ärmelkugel hinten"),
        Edge("naht_hinten", nh, o["sa"], label="Ärmelnaht"),
        Edge("saum", G.line(hb, hf), o["sa"] if o["sleeve_cuffs"] else o["hem_sa"], label="Ärmelsaum"),
        Edge("naht_vorne", nv, o["sa"], label="Ärmelnaht"),
        Edge("kugel_vorne", kf, o["sa"], label="Ärmelkugel vorne"),
    ]
    p = Piece("aermel", "Ärmel", edges, cut_count=2, mirror=True, fabric="Oberstoff",
              grain=(G.P(0, -(lo + hi) / 2 - 15), G.P(0, hem_y + 30)))
    p.notches += [Notch("kugel_vorne", -1.0, 1), Notch("kugel_vorne", G.length(kf) * 0.45, 1),
                  Notch("kugel_hinten", G.length(kb) * 0.55, 2)]
    return p, dict(SW=SW, SL=SL, cuff_h=cuff_h, cuff_len=cuff_len, op=op)


def _raglan(front, back, F, o, m, adult):
    """Raglan: Ärmelanteil vom Rumpf abtrennen, Raglanlinien starr auf den Ärmel übertragen."""
    out = {}
    curves = {}
    for pc, depth in ((front, F["fnd"]), (back, F["bnd"])):
        neck = pc.edge("ausschnitt").pts           # N → Mitte
        s_cut = G.length(neck) * 0.35
        Pn = G.point_at(neck, s_cut)
        U = G.P(F["q"], -F["AD"])
        t = G.tangent_at(neck, s_cut)                # Ausschnittrichtung (zur Mitte)
        arr = np.array([-t[1], t[0]])
        if arr[1] < 0:
            arr = -arr
        rag = G.tangent_curve(U, (-1, 0), Pn, arr, 0.45, 0.35)
        neck_rest = G.sub(neck, s_cut, G.length(neck))
        neck_part = G.length(neck) - G.length(neck_rest)
        e = pc.edges
        new = [e[0], e[1], e[2], Edge("raglan", rag, o["sa"], label="Raglannaht"),
               Edge("ausschnitt", neck_rest, e[5].sa, label="Ausschnitt")]
        pc.edges = new
        curves[pc.key] = (rag, neck_part)
    rf, npf = curves["vorderteil"]
    rb, npb = curves["rueckenteil"]
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    t = npf + npb
    cf = np.linalg.norm(rf[-1] - rf[0])
    cb = np.linalg.norm(rb[-1] - rb[0])
    arm_ease = {"eng": 0.08, "normal": 0.18, "weit": 0.30, "oversized": 0.40, "harem": 0.30}[o["fit"]]
    SWh = max(m["upper_arm"] * (1 + arm_ease) / 2, t / 2 + 20)
    dx = SWh - t / 2
    dy = math.sqrt(max(cf ** 2 - dx ** 2, (0.3 * cf) ** 2))
    Nf, Uf = G.P(t / 2, 0), G.P(t / 2 + math.sqrt(max(cf ** 2 - dy ** 2, 1)), -dy)
    Nb = G.P(-t / 2, 0)
    Ub = G.P(-t / 2 - math.sqrt(max(cb ** 2 - dy ** 2, 1)), -dy)
    kf = G.rigid_place(rf, rf[0], rf[-1], Uf, dst_b=Nf)                 # U → N (vorne, rechts)
    kb_m = G.mirror_x(rb, 0.0)
    kb = G.rigid_place(kb_m, kb_m[0], kb_m[-1], Ub, dst_b=Nb)            # U → N (hinten, links)
    shift = np.array([-(Uf[0] + Ub[0]) / 2, 0.0])                      # Achselpunkte symmetrisch
    kf, kb = kf + shift, kb + shift
    Uf, Ub, Nf, Nb = Uf + shift, Ub + shift, Nf + shift, Nb + shift
    sl_full = m["arm"] + 10 + m["shoulder"] * 0.85
    SL = o["sleeve_len_total"] or {"kurz": dy + max(0.1 * m["arm"], 35.0), "3/4": 0.72 * sl_full,
                                   "lang": sl_full}[o["sleeve_length"]]
    cuff_h = (o["cuff_h"] or (40 if adult else 30)) if o["sleeve_cuffs"] else 0.0
    SL = max(SL, dy + cuff_h + 35.0)
    hem_y = -(SL - cuff_h)
    SW = (Uf[0] - Ub[0])
    if o["sleeve_cuffs"]:
        cuff_len = o["sleeve_opening"] or m["wrist"] * 1.45
        op = cuff_len / E.band_ratio(o["band_fabric"], o["band_stretch"])
    else:
        cuff_len = 0.0
        op = o["sleeve_opening"] or (SW * 0.9 if o["sleeve_length"] == "kurz" else max(m["wrist"] * 1.6, SW * 0.55))
    # Ärmelnähte: verlassen die Achsel senkrecht zur Raglanlinie
    def perp(k, side):
        d = G.start_dir(k)                          # Richtung U → N
        p_ = np.array([d[1], -d[0]])
        if p_[1] > 0:
            p_ = -p_
        return p_ if side > 0 else np.array([-p_[0], p_[1]])   # hinten gespiegelt
    def seam(U, side, k, dx=0.0):
        H = G.P(side * op / 2 + dx, hem_y)
        return G.tangent_curve(U, perp(k, side), H, (0, -1), 0.25, 0.3)
    # Halskante: rechtwinklig zu beiden Raglanlinien (glatter Übergang zum Rumpf-Ausschnitt)
    d1 = G.end_dir(kf)
    h0 = np.array([d1[1], -d1[0]])
    if h0[0] > 0:
        h0 = -h0
    d2 = G.end_dir(kb)                      # kb läuft U → N
    h1 = np.array([d2[1], -d2[0]])
    if h1[0] > 0:
        h1 = -h1
    hals = G.tangent_curve(Nf, h0, Nb, h1, 0.35, 0.35)
    # rechtwinklig an beiden Achseln; Länge hinten über Lage des Saumpunkts angleichen
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
        Edge("raglan_hinten", kb[::-1], o["sa"], label="Raglannaht hinten"),
        Edge("naht_hinten", sb, o["sa"], label="Ärmelnaht"),
        Edge("saum", G.line(sb[-1], sf[-1]), o["sa"] if o["sleeve_cuffs"] else o["hem_sa"], label="Ärmelsaum"),
        Edge("naht_vorne", sf[::-1], o["sa"], label="Ärmelnaht"),
        Edge("raglan_vorne", kf, o["sa"], label="Raglannaht vorne"),
        Edge("hals", hals, o["sa"] * 0.7, label="Ausschnitt"),
    ]
    p = Piece("aermel", "Raglanärmel", edges, cut_count=2, mirror=True, fabric="Oberstoff",
              grain=(G.P(0, -dy - 10), G.P(0, hem_y + 30)))
    p.notches += [Notch("raglan_vorne", -15.0, 1), Notch("raglan_hinten", 15.0, 2)]
    return p, dict(SW=SW, SL=SL, cuff_h=cuff_h, cuff_len=cuff_len, op=op)


def draft(measures: dict, options: dict | None = None, _garment="tshirt_basic") -> Pattern:
    o = resolve_options(options)
    m = measures
    adult = m["height"] > 1650 and m["chest"] > 780
    F = _body_frame(m, o, adult)
    hem_band_h = (o["hem_band_h"] or (60 if adult else 45)) if o["hem_band"] else 0.0
    hem_y = -(F["L"] - hem_band_h)
    flare = 0.0 if o["hem_band"] or o["fit"] == "eng" else F["q"] * 0.04
    front = _body_piece("vorderteil", "Vorderteil", F, F["fnd"], 0.62, o, hem_y, flare,
                        [Notch("armloch", G.length(_armhole(F["sx"], F["sy"], F["q"], F["AD"], 0.62, F["nw"])) * 0.45, 1)])
    back = _body_piece("rueckenteil", "Rückenteil", F, F["bnd"], 0.5, o, hem_y, flare,
                       [Notch("armloch", G.length(_armhole(F["sx"], F["sy"], F["q"], F["AD"], 0.5, F["nw"])) * 0.45, 2)])
    fab = o["fabric"]
    seams, corners, checks, notes = [], [], [], []
    if o["sleeve_style"] == "raglan":
        sleeve, sinfo = _raglan(front, back, F, o, m, adult)
        front.notches = [n for n in front.notches if n.edge != "armloch"]
        back.notches = [n for n in back.notches if n.edge != "armloch"]
        front.notches.append(Notch("raglan", -15.0, 1))
        back.notches.append(Notch("raglan", -15.0, 2))
        seams += [
            dict(name="Raglannaht vorne: Vorderteil ↔ Ärmel", a=[("vorderteil", "raglan", 1)],
                 b=[("aermel", "raglan_vorne", 1)], type="equal"),
            dict(name="Raglannaht hinten: Rückenteil ↔ Ärmel", a=[("rueckenteil", "raglan", 1)],
                 b=[("aermel", "raglan_hinten", 1)], type="equal"),
        ]
        neck_parts = [("vorderteil", "ausschnitt", 2), ("rueckenteil", "ausschnitt", 2), ("aermel", "hals", 2)]
        corners += [dict(name="Achsel: Seitennaht ↔ Raglan (Rumpf)", piece="vorderteil", a="seite", b="raglan",
                         target=90),
                    dict(name="Achsel: Ärmelnaht ↔ Raglan (Ärmel vorne)", piece="aermel", a="naht_vorne",
                         b="raglan_vorne", target=90)]
    else:
        cap_target = G.length(front.edge("armloch").pts) + G.length(back.edge("armloch").pts) + \
            E.cap_ease_target_mm(fab)
        sleeve, sinfo = _sleeve(F, o, m, cap_target, adult)
        lo, hi = E.cap_ease_range_mm(fab)
        seams.append(dict(name="Armloch ↔ Ärmelkugel (Einhaltemenge)",
                          a=[("vorderteil", "armloch", 1), ("rueckenteil", "armloch", 1)],
                          b=[("aermel", "kugel_vorne", 1), ("aermel", "kugel_hinten", 1)], type="ease",
                          lo=lo, hi=hi, note=f"{E.fabric_info(fab)[0]}: {lo:.0f}–{hi:.0f} mm"))
        seams.append(dict(name="Schulternaht vorne ↔ hinten", a=[("vorderteil", "schulter", 1)],
                          b=[("rueckenteil", "schulter", 1)], type="equal"))
        neck_parts = [("vorderteil", "ausschnitt", 2), ("rueckenteil", "ausschnitt", 2)]
        corners += [
            dict(name="Achsel: Seitennaht ↔ Armloch vorne", piece="vorderteil", a="seite", b="armloch", target=90),
            dict(name="Achsel: Seitennaht ↔ Armloch hinten", piece="rueckenteil", a="seite", b="armloch", target=90),
            dict(name="Schulter ↔ Armloch (vorne + hinten)", sum=[("vorderteil", "armloch", "schulter"),
                                                                ("rueckenteil", "armloch", "schulter")], target=180),
            dict(name="Ärmelkugel oben (glatt)", piece="aermel", a="kugel_vorne", b="kugel_hinten", target=180),
            dict(name="Ärmel-Achsel ↔ Kugel vorne", piece="aermel", a="naht_vorne", b="kugel_vorne", target=90),
            dict(name="Schulter ↔ Ausschnitt (vorne + hinten)", sum=[("vorderteil", "schulter", "ausschnitt"),
                                                                   ("rueckenteil", "schulter", "ausschnitt")],
                 target=180),
        ]
    pieces = [front, back, sleeve]
    seams.insert(0, dict(name="Seitennaht vorne ↔ hinten", a=[("vorderteil", "seite", 1)],
                         b=[("rueckenteil", "seite", 1)], type="equal"))
    seams.append(dict(name="Ärmelnaht (vorne ↔ hinten)", a=[("aermel", "naht_vorne", 1)],
                      b=[("aermel", "naht_hinten", 1)], type="equal"))
    corners += [
        dict(name="Ausschnitt an vorderer Mitte", piece="vorderteil", a="ausschnitt", b="mitte",
             target=90 if o["neckline"] != "v" else _v_angle(front), note="" if o["neckline"] != "v" else "V-Spitze (gewollter Winkel)"),
        dict(name="Ausschnitt an hinterer Mitte", piece="rueckenteil", a="ausschnitt", b="mitte", target=90),
        dict(name="Saum an Mitte vorne", piece="vorderteil", a="mitte", b="saum", target=90),
        dict(name="Saum ↔ Seitennaht vorne", piece="vorderteil", a="saum", b="seite", target=90),
    ]
    # Halsbündchen
    stretch = F["stretch"]
    neck_len = sum(pieces[[p.key for p in pieces].index(k)].edge(e).length * n for k, e, n in neck_parts)
    nb_h = o["neck_band_h"] or (25 if adult else 20)
    ratio = E.band_ratio(o["band_fabric"], o["band_stretch"])
    if o["neckline"] == "v":
        ratio = min(0.95, ratio + 0.05)
    nbl = neck_len * ratio
    band = rect_piece("halsbuendchen", "Halsbündchen", nbl, 2 * nb_h, sa=o["sa"] * 0.7, cut_count=1,
                      fabric="Bündchen" if o["band_fabric"] == "buendchen" else "Oberstoff",
                      labels=("Ansatz", "Quernaht", "Ansatz", "Quernaht"), grain_vertical=True)
    band.marks.append(Mark(G.line(G.P(0, nb_h), G.P(nbl, nb_h)), "fold", "Umbruch"))
    band.stretch_dir = "Dehnrichtung quer (entlang der Länge)"
    pieces.append(band)
    lo_r, hi_r = E.band_ratio_range(o["band_fabric"])
    seams.append(dict(name="Halsbündchen ↔ Ausschnitt (gedehnt)", a=neck_parts, b=[("halsbuendchen", "unten", 1)],
                      type="ratio", lo=lo_r, hi=min(0.97, hi_r + (0.05 if o["neckline"] == "v" else 0))))
    b_stretch = E.fabric_info(o["band_fabric"], o["band_stretch"])[1]
    deficit = m["head"] * 1.03 - neck_len * (1 + stretch / 100)
    if deficit > 0 and o.get("_auto_neck", 0) < 8:
        # Ausschnitt automatisch vergrößern, bis er über den Kopf passt
        opts2 = dict(options or {})
        opts2["neck_extra"] = o["neck_extra"] + deficit / 5.0 + 2.0
        opts2["_auto_neck"] = o.get("_auto_neck", 0) + 1
        return draft(measures, opts2, _garment)
    if o["neck_extra"] > 0 and o.get("_auto_neck"):
        notes.append(f"Ausschnitt um {o['neck_extra'] / 10:.1f} cm erweitert, damit er über den Kopf passt.")
    checks.append(dict(name="Halsausschnitt passt über den Kopf", kind="min",
                       value=nbl * (1 + b_stretch / 100), target=m["head"] * 1.0,
                       note="Bündchenlänge inkl. nutzbarer Dehnung ≥ Kopfumfang"))
    checks.append(dict(name="Ausschnitt (Stoffkante) passt über den Kopf", kind="min",
                       value=neck_len * (1 + stretch / 100), target=m["head"] * 1.0,
                       note="Ausschnittumfang inkl. Dehnung ≥ Kopfumfang"))
    if o["sleeve_cuffs"]:
        cuff = rect_piece("aermelbuendchen", "Ärmelbündchen", sinfo["cuff_len"], 2 * sinfo["cuff_h"], sa=o["sa"],
                          cut_count=2, fabric="Bündchen", labels=("Ansatz", "Quernaht", "Ansatz", "Quernaht"))
        cuff.marks.append(Mark(G.line(G.P(0, sinfo["cuff_h"]), G.P(sinfo["cuff_len"], sinfo["cuff_h"])), "fold",
                               "Umbruch"))
        pieces.append(cuff)
        seams.append(dict(name="Ärmelbündchen ↔ Ärmelsaum (gedehnt)", a=[("aermel", "saum", 1)],
                          b=[("aermelbuendchen", "unten", 1)], type="ratio", lo=0.70, hi=0.85))
        checks.append(dict(name="Hand passt durch das Ärmelbündchen", kind="min",
                           value=sinfo["cuff_len"] * (1 + b_stretch / 100), target=m["wrist"] * 1.55,
                           note="Handumfang ≈ 1,55 × Handgelenk"))
    if o["hem_band"]:
        hb_len = (front.edge("saum").length + back.edge("saum").length) * 2 * E.band_ratio(o["band_fabric"], o["band_stretch"])
        hband = rect_piece("saumbuendchen", "Saumbündchen", hb_len / 2, 2 * hem_band_h, sa=o["sa"], cut_count=1,
                           fold_left=True, fabric="Bündchen" if o["band_fabric"] == "buendchen" else "Oberstoff",
                           labels=("Ansatz", "Quernaht", "Ansatz", "Mitte"))
        hband.marks.append(Mark(G.line(G.P(0, hem_band_h), G.P(hb_len / 2, hem_band_h)), "fold", "Umbruch"))
        pieces.append(hband)
        seams.append(dict(name="Saumbündchen ↔ Saum (gedehnt)", a=[("vorderteil", "saum", 2), ("rueckenteil", "saum", 2)],
                          b=[("saumbuendchen", "unten", 2)], type="ratio", lo=0.70, hi=0.92))
    # Mehrweite-Prüfung
    pat = Pattern(_garment, "T-Shirt" if o["sleeve_length"] == "kurz" else "Langarmshirt", "", pieces, dict(m), o,
                  seams=seams, corners=corners, checks=checks, notes=notes)
    fin = finished_measures(pat, F=F, sinfo=sinfo, hem_band_h=hem_band_h, nb_h=nb_h)
    pat.finished = fin
    pat.options.update(_F=F, _sinfo=sinfo, _hem_band_h=hem_band_h, _nb_h=nb_h)
    checks.insert(0, dict(name="Brustumfang Schnitt = Körper + Mehrweite", kind="circ", value=fin["chest_circ"],
                          target=F["Ct"], tol_rel=0.01,
                          note=f"Körper {m['chest'] / 10:.1f} cm + {F['be'] * 100:+.0f} % Mehrweite"
                          if not o["chest_total"] else "Zielwert aus Messung/Vorgabe"))
    if o["sleeve_length"] == "lang":
        checks.append(dict(name="Ärmellänge plausibel", kind="range", value=fin["sleeve_len"],
                           lo=m["arm"] * 0.9, hi=m["arm"] * 1.25, note=f"Armlänge {m['arm'] / 10:.1f} cm"))
    checks.append(dict(name="Rumpflänge plausibel", kind="range", value=fin["length"],
                       lo=0.30 * m["height"], hi=0.62 * m["height"], note="ab Halspunkt"))
    return pat


def _v_angle(front):
    return G.corner_angle(front.edge("ausschnitt").pts, front.edge("mitte").pts)


def finished_measures(pat, F=None, sinfo=None, hem_band_h=None, nb_h=None):
    o = pat.options
    F = F or o["_F"]
    sinfo = sinfo or o["_sinfo"]
    hem_band_h = o.get("_hem_band_h", 0.0) if hem_band_h is None else hem_band_h
    f, b = pat.piece("vorderteil"), pat.piece("rueckenteil")
    y = -F["AD"] - 25
    chest = 2 * (G.width_at_y(f.seam_ring(), y) + G.width_at_y(b.seam_ring(), y))
    hem = 2 * (f.edge("saum").length + b.edge("saum").length)
    if pat.has("saumbuendchen"):
        hem = pat.piece("saumbuendchen").edge("unten").length * 2
    length = -float(f.edge("saum").pts[0, 1]) + hem_band_h
    neck = sum(e.length for e in [f.edge("ausschnitt"), b.edge("ausschnitt")]) * 2
    if pat.piece("aermel").edges[-1].name == "hals":
        neck += 2 * pat.piece("aermel").edge("hals").length
    return dict(chest_circ=chest, hem_circ=hem, length=length, sleeve_len=sinfo["SL"],
                sleeve_opening=(sinfo["cuff_len"] if sinfo["cuff_len"] else sinfo["op"]),
                bicep_circ=sinfo["SW"], neckline=neck)


FINISHED_LABELS = {
    "chest_circ": ("Brustweite", "weite"), "hem_circ": ("Saumweite", "weite"), "length": ("Länge ab Halspunkt", "laenge"),
    "sleeve_len": ("Ärmellänge", "laenge"), "sleeve_opening": ("Ärmelöffnung", "weite"),
    "bicep_circ": ("Oberarmweite", "weite"), "neckline": ("Ausschnittumfang", "weite"),
}


def fit_to_targets(targets, base_options, size=None, **kw):
    """Oberteil-Rekonstruktion: Brustweite und Länge direkt aus der Messung (geschlossen lösbar)."""
    import measurements as M
    size = size or 122
    opts = dict(base_options)
    opts.update(chest_total=targets["chest_circ"], body_length=targets["length"])
    pat = draft(M.size_measures(size), opts)
    return dict(cost=0.0, fit=opts.get("fit", "normal"), params=dict(chest_total=targets["chest_circ"],
                body_length=targets["length"]), options=opts, size=size, pattern=pat)


def sewing_steps(pat):
    o = pat.options
    knit = E.fabric_info(o["fabric"])[2]
    st = "mit Overlock oder schmalem Zickzack-/Stretchstich" if knit else "mit Geradstich, Kanten versäubern"
    steps = []
    if o["sleeve_style"] == "raglan":
        steps += [f"**Raglannähte:** Ärmel rechts auf rechts an Vorder- und Rückenteil nähen ({st}); "
                  "einfache Passzeichen vorne, doppelte hinten."]
    else:
        steps += [f"**Schultern:** Vorder- und Rückenteil rechts auf rechts legen, Schulternähte {st} schließen."]
    steps += [
        "**Halsbündchen:** quer zur Runde schließen, längs links auf links falten. Bündchen und Ausschnitt "
        "in Viertel teilen (Quernaht an eine Schulter bzw. hintere Mitte), Bündchen gedehnt rechts auf rechts "
        "annähen. Nahtzugabe nach unten bügeln, auf Wunsch mit Zwillingsnadel absteppen.",
    ]
    if o["sleeve_style"] != "raglan":
        steps.append("**Ärmel einsetzen:** Ärmelkugel mittig (Passzeichen oben) an die Schulternaht stecken, "
                     "Passzeichen vorne/hinten abgleichen, flach einnähen (Kugel ggf. minimal einhalten).")
    steps += [
        "**Seiten- und Ärmelnähte:** in einem Zug vom Saum über die Achsel bis zum Ärmelsaum schließen; "
        "Achselnähte treffen sich genau.",
    ]
    if o["sleeve_cuffs"]:
        steps.append("**Ärmelbündchen:** zur Runde schließen, falten, gedehnt an den Ärmelsaum nähen.")
    else:
        steps.append("**Ärmelsaum:** Saumzugabe umbügeln und mit Zwillingsnadel/Coverstich nähen.")
    if o["hem_band"]:
        steps.append("**Saumbündchen:** zur Runde schließen, falten, in Viertel teilen und gedehnt annähen.")
    else:
        steps.append("**Saum:** Saumzugabe (2 cm) umbügeln und mit Zwillingsnadel/Coverstich nähen.")
    steps.append("Fertig! Nähte bügeln.")
    return steps
