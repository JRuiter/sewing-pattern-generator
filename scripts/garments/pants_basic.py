"""Hosen-Grundschnitt: Jogginghose, Haremshose, Leggings.

Eigene parametrische Konstruktion nach den allgemeinen Prinzipien der Hosen-
Grundschnittkonstruktion (Hüftweite in Viertel geteilt, Vorderhose schmaler als
Hinterhose, Schrittverlängerung vorne ≈ 1/20, hinten ≈ 1/10 der Hüftweite,
Hintere Mitte schräg und erhöht). Die Kurven werden so gesetzt, dass alle
Nahtenden rechtwinklig anschließen.

Koordinaten: mm, y nach oben. Oberkante der Hosenteile (Bundansatz) bei y = 0,
Vordere/Hintere Mitte auf Hüfthöhe bei x = 0, Seitennaht rechts.
Kantenreihenfolge (gegen den Uhrzeigersinn):
  schritt (Mitte + Schrittkurve) → innenbein → saum → seite → bund
"""
from __future__ import annotations

import copy
import math

import numpy as np
from scipy.interpolate import CubicSpline

import ease as E
import geometry as G
from pattern import Edge, Mark, Notch, Pattern, Piece, rect_piece

STYLES = {
    "jogginghose": dict(fit="normal", fabric="sweat", cuffs=True, waistband="bund_gummi",
                        pockets=["eingriff"], length="lang"),
    "haremshose": dict(fit="harem", fabric="sweat", cuffs=True, waistband="bund_gummi",
                       pockets=[], length="lang"),
    "leggings": dict(fit="eng", fabric="jersey_elastan", cuffs=False, waistband="yoga",
                     pockets=[], length="lang"),
    "stoffhose": dict(fit="normal", fabric="webware", cuffs=False, waistband="tunnel",
                      pockets=["eingriff"], length="lang"),
}

DEFAULTS = dict(style="jogginghose", fit=None, fabric=None, stretch=None, length=None,
                waistband=None, cuffs=None, pockets=None, cuff_fabric="buendchen",
                cuff_stretch=None, waistband_height=None, cuff_height=None,
                elastic_width=None, crotch_drop=None, blouse=None, sa=10.0, hem_sa=25.0,
                # Overrides (Reverse Engineering / Feineinstellung), alles Fertigmaße in mm
                hip_total=None, fork_factor=1.0, front_rise_total=None, inseam_total=None,
                opening_total=None, elastic_total=None, knee_total=None, thigh_total=None)

TITLES = {"jogginghose": "Jogginghose", "haremshose": "Haremshose", "leggings": "Leggings",
          "stoffhose": "Schlupfhose"}


def resolve_options(options: dict | None) -> dict:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None or k not in o})
    style = STYLES.get(o["style"], STYLES["jogginghose"])
    for k, v in style.items():
        if o.get(k) is None:
            o[k] = copy.deepcopy(v)
    if o["pockets"] is None:
        o["pockets"] = []
    if isinstance(o["pockets"], str):
        o["pockets"] = [] if o["pockets"] in ("", "keine") else [o["pockets"]]
    if o["fit"] == "eng":
        o["pockets"] = [p for p in o["pockets"] if p != "eingriff"]
    return o


def _leg_spline(y_top, x_top, y_bot, x_bot, slope_top, slope_bot=0.0, mid=None, step=2.0):
    """x(y)-Spline von oben nach unten, Steigung dx/dy an den Enden vorgegeben."""
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
    k = m["height"] / 1220.0  # Skalierfaktor für Kleinteile (Kind Gr. 122 = 1)
    k = max(0.75, min(1.45, k))

    # ---------------------------------------------------------------- Weiten
    he = E.hip_ease(fit, fabric, stretch)
    Hc = o["hip_total"] or m["hip"] * (1 + he)
    diff = 10.0 if adult else 5.0
    Wf, Wb = Hc / 4 - diff, Hc / 4 + diff
    if fit == "eng":
        fe, fbe = Hc * 0.040, Hc * 0.080
    else:
        fe, fbe = Hc * 0.050, Hc * 0.100
    fe *= o["fork_factor"]
    fbe *= o["fork_factor"]

    # ---------------------------------------------------------------- Höhen
    wb_type = o["waistband"]
    wb_h = o["waistband_height"] or {"bund_gummi": 30, "buendchen": 35, "yoga": 60,
                                      "tunnel": 0}[wb_type] * (k if adult else 1.0)
    if wb_type == "tunnel":
        wb_h = 0.0
    el_w = o["elastic_width"] or (30.0 if adult else 20.0)
    drop = o["crotch_drop"]
    if drop is None:
        drop = 0.06 * m["height"] if fit == "harem" else 0.0
    rise_body = m["side_length"] - m["inseam"]
    if o["front_rise_total"]:
        R = o["front_rise_total"] - wb_h
    else:
        R = rise_body + E.rise_ease_mm(fit, adult) + drop - wb_h
    cuffs = bool(o["cuffs"])
    cuff_h = (o["cuff_height"] or ((70 if fit == "harem" else 50) * k)) if cuffs else 0.0
    blouse = o["blouse"]
    if blouse is None:
        blouse = (30.0 if fit == "harem" else 15.0) * k if cuffs else 0.0
    length = o["length"]
    leg_frac = {"lang": None, "7/8": 0.82, "knie": 0.45, "kurz": 0.18}[length]
    if o["inseam_total"]:
        inseam_fin = o["inseam_total"]
    elif leg_frac is None:
        inseam_fin = m["inseam"] - (25 if adult else 15) - drop + blouse
    else:
        inseam_fin = m["inseam"] * leg_frac - drop + (blouse if length == "7/8" else 0)
    leg_len = inseam_fin - cuff_h          # senkrechte Länge Schrittlinie → Saumkante

    # ---------------------------------------------------------------- Beinöffnung
    ratio_cuff = E.band_ratio(o["cuff_fabric"], o["cuff_stretch"]) if cuffs else 1.0
    if cuffs:
        cuff_len = o["opening_total"] or max(m["ankle"] * 1.12, m["ankle"] + 15)
        hem_c = cuff_len / ratio_cuff
    else:
        cuff_len = 0.0
        if o["opening_total"]:
            hem_c = o["opening_total"]
        else:
            hem_c = {"eng": m["ankle"] * (1.08 if stretch < 50 else 1.0), "normal": 0.46 * Hc,
                     "weit": 0.62 * Hc, "oversized": 0.66 * Hc, "harem": 0.40 * Hc}[fit]
            if length == "knie":
                hem_c = max(hem_c, m["knee"] * (1.0 + max(he, 0.05)) * 1.05)
            if length == "kurz":
                hem_c = max(hem_c, (Wf + Wb + fe + fbe) * 2 * 0.92)
    hem_front, hem_back = hem_c / 2 - 2 * diff, hem_c / 2 + 2 * diff

    # ---------------------------------------------------------------- Vorderhose
    y_hip = -0.55 * R
    y_cr = -R
    y_hem = y_cr - leg_len
    crease_f = (Wf - fe) / 2
    knee_y = y_cr - leg_len * 0.45
    knee_fr = knee_bk = None
    if length in ("lang", "7/8") and (fit == "eng" or o["knee_total"]):
        kt = o["knee_total"] or m["knee"] * (1 + he + 0.02)
        knee_fr, knee_bk = kt / 2 - 2 * diff, kt / 2 + 2 * diff

    # Innenbein vorne zuerst (Schrittwinkel hängt von seiner Starttangente ab)
    slope_in = 0.0 if fit in ("harem", "weit", "oversized") else None
    inner_hem = crease_f - hem_front / 2
    if slope_in is None:
        # dx/dy < 0: Innenbein läuft nach unten leicht nach innen
        slope_in = -0.15 if fit == "normal" else -0.25
    mid_in = (crease_f - knee_fr / 2, knee_y) if knee_fr else None
    inseam_f = _leg_spline(y_cr, -fe, y_hem, inner_hem, slope_in, 0.0, mid_in)
    d_in = G.start_dir(inseam_f)
    arrive = np.array([d_in[1], -d_in[0]])          # ⟂ zum Innenbein
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

    pk_a = max(35.0, 0.28 * Wf)                  # Eingriff: Abstand an der Oberkante
    pk_b = max(95.0, min(0.62 * R, 170.0))       # Eingriff: Tiefe an der Seitennaht
    if "eingriff" in pockets:
        side_top = G.P(Wf, -pk_b)
        seite_f = G.join(side_f_leg, G.line(side_f_leg[-1], side_top))
        eingriff = G.line(side_top, G.P(Wf - pk_a, 0))
        bund_f = G.line(G.P(Wf - pk_a, 0), cf_top)
        f_edges = [
            Edge("schritt", schritt_f, sa, label="Schrittnaht"),
            Edge("innenbein", inseam_f, sa, label="Innenbein"),
            Edge("saum", saum_f, sa if cuffs else hem_sa, label="Bündchenansatz" if cuffs else "Saum"),
            Edge("seite", seite_f, sa, label="Seitennaht"),
            Edge("eingriff", eingriff, sa, label="Eingriff"),
            Edge("bund", bund_f, sa if wb_type != "tunnel" else el_w + 15, label="Bund"),
        ]
    else:
        seite_f = G.join(side_f_leg, G.line(side_f_leg[-1], G.P(Wf, 0)))
        f_edges = [
            Edge("schritt", schritt_f, sa, label="Schrittnaht"),
            Edge("innenbein", inseam_f, sa, label="Innenbein"),
            Edge("saum", saum_f, sa if cuffs else hem_sa, label="Bündchenansatz" if cuffs else "Saum"),
            Edge("seite", seite_f, sa, label="Seitennaht"),
            Edge("bund", G.line(G.P(Wf, 0), cf_top), sa if wb_type != "tunnel" else el_w + 15,
                 label="Bund"),
        ]
    front = Piece("vorderhose", "Vorderhose", f_edges, cut_count=2, mirror=True,
                  fabric="Oberstoff",
                  grain=(G.P(crease_f, y_cr - 40), G.P(crease_f, max(y_hem + 60, y_cr - leg_len * 0.6))))
    side_notch = 0.5 * G.length(side_f_leg)
    front.notches += [Notch("seite", side_notch, 1), Notch("innenbein", 80, 1),
                      Notch("schritt", G.length(schritt_f) * 0.5, 1)]
    if wb_type == "tunnel":
        front.marks.append(Mark(G.line(G.P(Wf - (pk_a if "eingriff" in pockets else 0), el_w + 7),
                                       G.P(0, el_w + 7)), "fold", "Tunnel umbügeln"))

    # ---------------------------------------------------------------- Hinterhose
    rb = (25.0 if adult else 15.0) if fit != "eng" else (35.0 if adult else 20.0)
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
    back = Piece("hinterhose", "Hinterhose", [
        Edge("schritt", schritt_b, sa, label="Schrittnaht"),
        Edge("innenbein", inseam_b, sa, label="Innenbein"),
        Edge("saum", saum_b, sa if cuffs else hem_sa, label="Bündchenansatz" if cuffs else "Saum"),
        Edge("seite", seite_b, sa, label="Seitennaht"),
        Edge("bund", bund_b, sa if wb_type != "tunnel" else el_w + 15, label="Bund"),
    ], cut_count=2, mirror=True, fabric="Oberstoff",
        grain=(G.P(crease_b, y_cr - 40), G.P(crease_b, max(y_hem + 60, y_cr - leg_len * 0.6))))
    back.notches += [Notch("seite", side_notch, 2), Notch("innenbein", 80, 2),
                     Notch("schritt", G.length(schritt_b) * 0.5, 2)]
    if wb_type == "tunnel":
        back.marks.append(Mark(G.line(G.P(Wb, el_w + 7), G.P(sb, rb + el_w + 7)), "fold",
                               "Tunnel umbügeln"))

    # Seitennähte auf gleiche Länge bringen (Hinterhose oben minimal anpassen)
    dl = G.length(seite_b) - (G.length(seite_f) + (pk_b if "eingriff" in pockets else 0.0))
    if abs(dl) > 0.3:
        back.edges[3].pts = G.join(side_b_leg, G.line(side_b_leg[-1], G.P(Wb, -dl)))
        back.edges[4].pts = G.tangent_curve(G.P(Wb, -dl), (-1, 0), cb_top, waist_arrive, 0.35, 0.35)

    pieces += [front, back]

    # ---------------------------------------------------------------- Taschen
    if "eingriff" in pockets:
        bag_depth = pk_b + 45 * k
        x0 = max(Wf - pk_a - 35 * k, 20.0)
        T0, T1, S1 = G.P(x0, 0), G.P(Wf, 0), G.P(Wf, -bag_depth)
        r = min(35.0 * k, (Wf - x0) * 0.45)
        bag = G.join(G.line(T0, G.P(x0, -bag_depth + r)),
                     G.tangent_curve(G.P(x0, -bag_depth + r), (0, -1), G.P(x0 + r, -bag_depth), (1, 0), 0.55, 0.55),
                     G.line(G.P(x0 + r, -bag_depth), S1))
        E_ = G.P(Wf, -pk_b)
        side_panel = Piece("seitenteil", "Seitenteil (Taschenbeutel außen)", [
            Edge("beutel", bag, sa, label="Beutelnaht"),
            Edge("seite_unten", G.line(S1, E_), sa, label="Seitennaht"),
            Edge("seite_oben", G.line(E_, T1), sa, label="Seitennaht"),
            Edge("bund_aussen", G.line(T1, G.P(Wf - pk_a, 0)), sa, label="Bund"),
            Edge("bund_innen", G.line(G.P(Wf - pk_a, 0), T0), sa, label="Bund"),
        ], cut_count=2, mirror=True, fabric="Oberstoff",
            grain=(G.P((x0 + Wf) / 2, -bag_depth + 30), G.P((x0 + Wf) / 2, -25)))
        side_panel.marks.append(Mark(G.line(E_, G.P(Wf - pk_a, 0)), "placement", "Eingriff"))
        lining = Piece("taschenbeutel", "Taschenbeutel innen", [
            Edge("beutel", bag.copy(), sa, label="Beutelnaht"),
            Edge("seite", G.line(S1, E_), sa, label="Seitennaht"),
            Edge("eingriff", G.line(E_, G.P(Wf - pk_a, 0)), sa, label="Eingriff"),
            Edge("bund", G.line(G.P(Wf - pk_a, 0), T0), sa, label="Bund"),
        ], cut_count=2, mirror=True, fabric="Oberstoff oder Baumwolljersey",
            grain=(G.P(x0 + 25, -bag_depth + 30), G.P(x0 + 25, -25)))
        pieces += [side_panel, lining]
        seams += [
            dict(name="Eingriff: Vorderhose ↔ Taschenbeutel", a=[("vorderhose", "eingriff", 1)],
                 b=[("taschenbeutel", "eingriff", 1)], type="equal"),
            dict(name="Beutelnaht: Taschenbeutel ↔ Seitenteil", a=[("taschenbeutel", "beutel", 1)],
                 b=[("seitenteil", "beutel", 1)], type="equal"),
            dict(name="Taschenbeutel ↔ Seitenteil an der Seitennaht", a=[("taschenbeutel", "seite", 1)],
                 b=[("seitenteil", "seite_unten", 1)], type="equal"),
        ]
    if "aufgesetzt_hinten" in pockets:
        pw, ph = 110 * k, 120 * k
        pocket = rect_piece("gesaesstasche", "Gesäßtasche (aufgesetzt)", pw, ph, sa=sa,
                            cut_count=2, names=("unten", "rechts", "oben", "links"),
                            labels=("", "", "Taschenbeleg", ""), sas=(sa, sa, 25.0, sa))
        pieces.append(pocket)
        px = Wb * 0.55
        py = -0.15 * R
        rect = np.array([[px - pw / 2, py], [px + pw / 2, py], [px + pw / 2, py - ph],
                         [px - pw / 2, py - ph], [px - pw / 2, py]])
        back.marks.append(Mark(rect, "placement", "Gesäßtasche"))

    # ---------------------------------------------------------------- Bund
    top_parts = [("vorderhose", "bund", 2), ("hinterhose", "bund", 2)]
    if "eingriff" in pockets:
        top_parts.append(("seitenteil", "bund_aussen", 2))
    top_len = sum(next(p for p in pieces if p.key == a).edge(e).length * n for a, e, n in top_parts)
    elastic_len = o["elastic_total"] or m["waist"] * (0.90 if not adult else 0.92)
    if wb_type in ("bund_gummi", "buendchen", "yoga"):
        if wb_type == "bund_gummi":
            wb_fab, ratio, label = fabric, 1.0, "Bund (mit Gummi)"
        elif wb_type == "buendchen":
            wb_fab, ratio, label = "buendchen", E.band_ratio("buendchen"), "Bundbündchen"
        else:
            wb_fab, ratio, label = fabric, E.band_ratio(fabric, stretch), "Breiter Bund"
        bl = top_len * ratio
        # Bund im Bruch (halbe Länge): spart Platz auf Rolle/Bogen, Quernaht nur hinten
        band = rect_piece("bund", label, bl / 2, 2 * wb_h, sa=sa, cut_count=1, fold_left=True,
                          fabric="Bündchen" if wb_fab == "buendchen" else "Oberstoff",
                          names=("unten", "rechts", "oben", "links"),
                          labels=("Ansatz", "Quernaht", "Ansatz", "Vordere Mitte"), grain_vertical=True)
        band.marks.append(Mark(G.line(G.P(0, wb_h), G.P(bl / 2, wb_h)), "fold", "Umbruch"))
        band.stretch_dir = "Dehnrichtung quer (entlang der Länge)"
        pieces.append(band)
        if wb_type == "bund_gummi":
            seams.append(dict(name="Bund ↔ Hosenoberkante", a=top_parts, b=[("bund", "unten", 2)],
                              type="equal"))
        else:
            lo_r, hi_r = E.band_ratio_range("buendchen" if wb_type == "buendchen" else "jersey")
            seams.append(dict(name="Bund ↔ Hosenoberkante (gedehnt)", a=top_parts,
                              b=[("bund", "unten", 2)], type="ratio", lo=lo_r, hi=hi_r))
        waist_relaxed = elastic_len if wb_type == "bund_gummi" else bl
        if wb_type == "yoga":
            waist_relaxed = bl
    else:
        waist_relaxed = elastic_len
    if wb_type in ("bund_gummi", "tunnel"):
        notes.append(f"Gummiband {el_w:.0f} mm breit, Länge {elastic_len / 10:.0f} cm "
                     f"(+2 cm Überlappung zum Zusammennähen)")

    # ---------------------------------------------------------------- Bündchen
    if cuffs:
        cuff = rect_piece("beinbuendchen", "Beinbündchen", cuff_len, 2 * cuff_h, sa=sa, cut_count=2,
                          fabric="Bündchen", labels=("Ansatz", "Quernaht", "Ansatz", "Quernaht"),
                          mirror=False)
        cuff.marks.append(Mark(G.line(G.P(0, cuff_h), G.P(cuff_len, cuff_h)), "fold", "Umbruch"))
        cuff.stretch_dir = "Dehnrichtung quer (entlang der Länge)"
        pieces.append(cuff)
        lo_r, hi_r = E.band_ratio_range(o["cuff_fabric"])
        seams.append(dict(name="Beinbündchen ↔ Beinsaum (gedehnt)",
                          a=[("vorderhose", "saum", 1), ("hinterhose", "saum", 1)],
                          b=[("beinbuendchen", "unten", 1)], type="ratio", lo=lo_r, hi=hi_r))

    # ---------------------------------------------------------------- Nahtpaare
    side_a = [("vorderhose", "seite", 1)]
    if "eingriff" in pockets:
        side_a.append(("seitenteil", "seite_oben", 1))
    seams[:0] = [
        dict(name="Seitennaht vorne ↔ hinten", a=side_a, b=[("hinterhose", "seite", 1)], type="equal"),
        dict(name="Innenbeinnaht vorne ↔ hinten", a=[("vorderhose", "innenbein", 1)],
             b=[("hinterhose", "innenbein", 1)], type="equal"),
        dict(name="Schrittnaht vorne (linkes ↔ rechtes Teil)", a=[("vorderhose", "schritt", 1)],
             b=[("vorderhose", "schritt", 1)], type="equal"),
        dict(name="Schrittnaht hinten (linkes ↔ rechtes Teil)", a=[("hinterhose", "schritt", 1)],
             b=[("hinterhose", "schritt", 1)], type="equal"),
    ]

    # ---------------------------------------------------------------- Winkel
    top_f = "eingriff" if "eingriff" in pockets else "bund"
    corners += [
        dict(name="Vordere Mitte ↔ Bund", piece="vorderhose", a="bund", b="schritt", target=90),
        dict(name="Hintere Mitte ↔ Bund", piece="hinterhose", a="bund", b="schritt", target=90),
        dict(name="Schritt ↔ Innenbein (vorne + hinten)", sum=[("vorderhose", "schritt", "innenbein"),
                                                             ("hinterhose", "schritt", "innenbein")],
             target=180),
        dict(name="Innenbein ↔ Saum vorne", piece="vorderhose", a="innenbein", b="saum", target=90),
        dict(name="Saum ↔ Seitennaht vorne", piece="vorderhose", a="saum", b="seite", target=90),
        dict(name="Innenbein ↔ Saum hinten", piece="hinterhose", a="innenbein", b="saum", target=90),
        dict(name="Saum ↔ Seitennaht hinten", piece="hinterhose", a="saum", b="seite", target=90),
        dict(name="Seitennaht ↔ Bund hinten", piece="hinterhose", a="seite", b="bund", target=90),
    ]
    if "eingriff" not in pockets:
        corners.append(dict(name="Seitennaht ↔ Bund (vorne + hinten)",
                            sum=[("vorderhose", "seite", "bund"), ("hinterhose", "seite", "bund")],
                            target=180))
    else:
        corners.append(dict(name="Seitennaht ↔ Bund am Seitenteil", piece="seitenteil",
                            a="seite_oben", b="bund_aussen", target=90))

    pat = Pattern("pants_basic", TITLES.get(o["style"], "Hose"), "", pieces, dict(m), o,
                  seams=seams, corners=corners, checks=checks, notes=notes)

    # ---------------------------------------------------------------- Fertigmaße
    pat.options["_y_hip"] = y_hip
    fin = finished_measures(pat, wb_h=wb_h, cuff_h=cuff_h, waist_relaxed=waist_relaxed,
                            pk_b=pk_b if "eingriff" in pockets else 0.0)
    pat.finished = fin
    pat.options.update(dict(_wb_h=wb_h, _cuff_h=cuff_h, _waist_relaxed=waist_relaxed,
                            _pk_b=pk_b if "eingriff" in pockets else 0.0, _R=R, _hip_total=Hc,
                            _drop=drop, _back_drop=back_drop, _elastic=elastic_len,
                            _cuff_len=cuff_len, _hem_c=hem_c, _blouse=blouse))

    # ---------------------------------------------------------------- Prüfwerte
    tol_hip = 0.01
    checks += [
        dict(name="Hüftumfang Schnitt = Körper + Mehrweite", kind="circ",
             value=fin["hip_circ"], target=Hc, tol_rel=tol_hip,
             note=f"Körper {m['hip'] / 10:.1f} cm + {he * 100:+.0f} % Mehrweite"
             if not o["hip_total"] else "Zielwert aus Messung/Vorgabe"),
        dict(name="Oberkante passt über die Hüfte", kind="min",
             value=top_len * (1 + stretch / 100 * 0.6), target=m["hip"] * 1.02,
             note="Oberkantenumfang inkl. nutzbarer Dehnung ≥ Hüftumfang"),
        dict(name="Leibhöhe (vorne) plausibel", kind="range", value=R + wb_h,
             lo=0.12 * m["height"], hi=0.12 * m["height"] + rise_body * 0.3 + drop + 40,
             note=f"Körper-Leibhöhe {rise_body / 10:.1f} cm" + (f", Harem-Absenkung {drop / 10:.1f} cm" if drop else "")),
        dict(name="Innenbeinlänge plausibel", kind="range", value=fin["inseam"] + drop,
             lo=m["inseam"] * (leg_frac or 0.85) * 0.85, hi=m["inseam"] * (leg_frac or 1.0) * 1.12,
             note=f"Körper-Schrittlänge {m['inseam'] / 10:.1f} cm"),
        dict(name="Fuß passt durch die Beinöffnung", kind="min",
             value=fin["opening"] * (1 + (E.fabric_info(o['cuff_fabric'])[1] if cuffs else stretch) / 100 * 0.6),
             target=m["ankle"] * 1.35, note="Fersen-Rist-Umfang ≈ 1,35 × Knöchel"),
    ]
    if fit == "eng" and stretch < 30:
        checks.append(dict(name="Stoff dehnbar genug für Leggings", kind="min", value=stretch,
                           target=30, note="Leggings brauchen ≥ 30 % Querdehnung"))
    pat.size_label = ""
    return pat


def finished_measures(pat: Pattern, wb_h=None, cuff_h=None, waist_relaxed=None, pk_b=None) -> dict:
    """Virtuelles Zusammennähen: Maße der fertigen Hose (flach gemessen ×2 = Umfang)."""
    o = pat.options
    wb_h = o.get("_wb_h", 0.0) if wb_h is None else wb_h
    cuff_h = o.get("_cuff_h", 0.0) if cuff_h is None else cuff_h
    waist_relaxed = o.get("_waist_relaxed", 0.0) if waist_relaxed is None else waist_relaxed
    pk_b = o.get("_pk_b", 0.0) if pk_b is None else pk_b
    f, b = pat.piece("vorderhose"), pat.piece("hinterhose")
    sf, sb = f.seam_ring(), b.seam_ring()
    # Hüfthöhe: unteres Ende der geraden Mitte = Punkt mit x≈0 am weitesten unten
    y_hip = o.get("_y_hip")
    if y_hip is None:
        cf = f.edge("schritt").pts
        y_hip = float(cf[np.abs(cf[:, 0]) < 1e-6][:, 1].min())
    if pat.has("seitenteil"):  # Vorderhose + Seitenteil liegen im selben Koordinatensystem
        from shapely.geometry import Polygon
        u = Polygon(sf).union(Polygon(pat.piece("seitenteil").seam_ring()))
        sf_hip = np.asarray(u.exterior.coords)
    else:
        sf_hip = sf
    hip = 2 * (G.width_at_y(sf_hip, y_hip) + G.width_at_y(sb, y_hip))
    y_cr_f = float(f.edge("innenbein").pts[0, 1])
    y_cr_b = float(b.edge("innenbein").pts[0, 1])
    thigh = G.width_at_y(sf, y_cr_f - 25) + G.width_at_y(sb, y_cr_b - 25)   # ein Bein
    leg_len = y_cr_f - float(f.edge("saum").pts[0, 1])
    knee = G.width_at_y(sf, y_cr_f - 0.5 * leg_len) + G.width_at_y(sb, y_cr_b - 0.5 * leg_len)
    if pat.has("beinbuendchen"):
        opening = pat.piece("beinbuendchen").edge("unten").length
    else:
        opening = f.edge("saum").length + b.edge("saum").length
    side = f.edge("seite").length + (pat.piece("seitenteil").edge("seite_oben").length
                                     if pat.has("seitenteil") else 0.0)
    rise_f = -y_cr_f + wb_h
    # Rückenhöhe: höchster Punkt Hintere Mitte bis Schritt
    rise_b = float(b.edge("schritt").pts[0, 1]) - y_cr_b + wb_h
    y_hem = float(f.edge("saum").pts[0, 1])
    # Längen senkrecht gemessen (wie mit dem Maßband an der flach liegenden Hose)
    inseam = (y_cr_f - y_hem) + cuff_h
    outseam = -y_hem + wb_h + cuff_h
    top = 2 * (f.edge("bund").length + b.edge("bund").length +
               (pat.piece("seitenteil").edge("bund_aussen").length if pat.has("seitenteil") else 0.0))
    return dict(hip_circ=hip, thigh_circ=thigh, knee_circ=knee, opening=opening, waist_relaxed=waist_relaxed,
                waist_max=top, outseam=outseam, inseam=inseam, front_rise=rise_f, back_rise=rise_b,
                waistband_h=wb_h, cuff_h=cuff_h, crotch_seam=2 * 0 + f.edge("schritt").length +
                b.edge("schritt").length + 2 * wb_h)


FINISHED_LABELS = {
    "hip_circ": ("Hüftweite", "weite"), "thigh_circ": ("Oberschenkelweite", "weite"),
    "knee_circ": ("Beinweite Mitte (halbe Beinlänge)", "weite"),
    "opening": ("Beinöffnung", "weite"), "waist_relaxed": ("Bundweite entspannt", "weite"),
    "waist_max": ("Bundweite gedehnt (Oberkante Hose)", "weite"), "outseam": ("Seitenlänge", "laenge"),
    "inseam": ("Innenbeinlänge", "laenge"), "front_rise": ("Leibhöhe vorne", "laenge"),
    "back_rise": ("Leibhöhe hinten", "laenge"), "waistband_h": ("Bundhöhe", "laenge"),
    "cuff_h": ("Bündchenhöhe", "laenge"), "crotch_seam": ("Schrittnaht gesamt", "laenge"),
}

# Messgrößen, die das Reverse Engineering anpasst: Option → (Fertigmaß, Startwert-Funktion)
FIT_PARAMS = ["hip_total", "fork_factor", "front_rise_total", "inseam_total", "opening_total"]


def sewing_steps(pat: Pattern) -> list[str]:
    o = pat.options
    knit = E.fabric_info(o["fabric"])[2]
    st = "mit der Overlock oder einem schmalen Zickzack-/Stretchstich" if knit else "mit Geradstich, Kanten versäubern"
    steps = []
    if "eingriff" in o["pockets"]:
        steps += [
            "**Eingrifftaschen:** Taschenbeutel innen rechts auf rechts auf die Eingriffkante der Vorderhose "
            "legen und nähen. Nahtzugabe knapp einschneiden, Beutel nach innen wenden, Kante bügeln und "
            "5 mm breit absteppen.",
            "Seitenteil rechts auf rechts unter den Taschenbeutel legen (Markierung „Eingriff“ trifft die "
            "Eingriffkante), Beutelnaht nähen. Seitenteil an Oberkante und Seite innerhalb der Nahtzugabe "
            "an der Vorderhose festheften.",
        ]
    if "aufgesetzt_hinten" in o["pockets"]:
        steps.append("**Gesäßtaschen:** Oberkante 2,5 cm nach innen umbügeln und absteppen, übrige Kanten "
                     "1 cm umbügeln, Taschen nach Markierung auf die Hinterhosen steppen.")
    steps += [
        f"**Seitennähte:** Vorder- und Hinterhose rechts auf rechts legen (Passzeichen: einfach = vorne, "
        f"doppelt = hinten), Seitennähte {st} schließen.",
        "**Innenbeinnähte:** jeweils schließen; die Passzeichen am Innenbein treffen sich.",
        "**Schrittnaht:** ein Hosenbein auf rechts wenden und in das andere (links) stecken, sodass die "
        "Hosenbeine rechts auf rechts liegen. Schrittnaht in einem Zug von der vorderen zur hinteren "
        "Oberkante nähen, die Innenbeinnähte treffen sich genau.",
    ]
    wb = o["waistband"]
    if wb == "bund_gummi":
        steps += [
            "**Bund:** Bundstreifen rechts auf rechts zur Runde legen und die Quernaht (hintere Mitte) "
            "schließen; dabei 3 cm offen lassen (Gummidurchzug). Längs links auf links an der Umbruchlinie "
            "falten.",
            "Bund in Viertel teilen und markieren, ebenso die Hosenoberkante (vordere/hintere Mitte, Seiten). "
            "Bund rechts auf rechts an die Hosenoberkante stecken (offene Stelle hinten innen) und annähen.",
            "Gummiband einziehen, Enden 2 cm überlappend zusammennähen, Öffnung schließen. Gummi gleichmäßig "
            "verteilen und an den Seitennähten im Nahtschatten fixieren.",
        ]
    elif wb in ("buendchen", "yoga"):
        steps += [
            "**Bund:** Bundteil zur Runde schließen (Quernaht hinten), längs links auf links falten. Bund und "
            "Hosenoberkante in Viertel teilen und markieren.",
            "Bund leicht gedehnt rechts auf rechts an die Hosenoberkante nähen (Quernaht trifft die hintere "
            "Mitte). Nicht die Hose dehnen, nur den Bund.",
        ]
    else:
        steps += [
            "**Tunnelzug:** Oberkante 7 mm umbügeln, dann an der Linie „Tunnel umbügeln“ nach innen "
            "umschlagen und knappkantig festnähen; 3 cm Öffnung lassen. Gummi einziehen, Enden "
            "überlappend vernähen, Öffnung schließen.",
        ]
    if o["cuffs"]:
        steps += [
            "**Beinbündchen:** jeweils quer rechts auf rechts zur Runde nähen, längs links auf links falten. "
            "Bündchen und Beinsaum in Viertel teilen und markieren.",
            "Bündchen über das rechts liegende Hosenbein stülpen, Quernaht an die Innenbeinnaht legen und "
            "gedehnt annähen. Nahtzugabe zur Hose bügeln.",
        ]
    else:
        steps.append("**Saum:** Saumzugabe (2,5 cm) nach innen bügeln und mit Zwillingsnadel bzw. "
                     "Geradstich festnähen.")
    steps.append("Fertig! Alle Nähte bügeln (bei Sweat Dampf, nicht drücken).")
    return steps
