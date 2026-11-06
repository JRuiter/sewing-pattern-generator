"""Rock mit Gummibund: gerafft (Rechtecke), A-Linie, Tellerrock (Viertelkreis im Bruch)."""
from __future__ import annotations

import math

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

DEFAULTS = dict(style="gerafft", length="knie", fabric="webware", stretch=None, sa=10.0, hem_sa=25.0,
                waistband_height=None, gather=1.6, flare_deg=None, top_total=None, skirt_length=None)

FINISHED_LABELS = {"top_circ": ("Rockweite oben (ungerafft)", "weite"), "hem_circ": ("Saumweite", "weite"),
                   "length": ("Rocklänge inkl. Bund", "laenge"), "waist_relaxed": ("Bundweite entspannt", "weite")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    adult = m["height"] > 1650
    sa, hem_sa = o["sa"], o["hem_sa"]
    wb_h = o["waistband_height"] or (35.0 if adult else 30.0)
    knee_h = 0.285 * m["height"]
    L = o["skirt_length"] or {"mini": 0.75 * (m["side_length"] - knee_h), "knie": m["side_length"] - knee_h,
                              "midi": m["side_length"] - 0.2 * m["height"],
                              "maxi": m["side_length"] - 0.05 * m["height"]}[o["length"]]
    Lp = L - wb_h
    style = o["style"]
    pieces, seams, corners, checks = [], [], [], []
    if style == "gerafft":
        top = o["top_total"] or max(m["hip"] * o["gather"], m["hip"] * 1.25)
        w = top / 4
        for key, name in (("vorderrock", "Vorderrock"), ("rueckenrock", "Rückenrock")):
            p = rect_piece(key, name, w, Lp, sa=sa, fold_left=True, cut_count=1,
                           names=("saum", "seite", "bund", "mitte"),
                           labels=("Saum", "Seitennaht", "Bund (einreihen)", "Mitte (Bruch)"),
                           sas=(hem_sa, sa, sa, 0.0))
            pieces.append(p)
        hem = top
    elif style == "a_linie":
        top = o["top_total"] or m["hip"] * 1.10
        flare = math.radians(o["flare_deg"] or 12.0)
        w0 = top / 4
        for key, name in (("vorderrock", "Vorderrock"), ("rueckenrock", "Rückenrock")):
            S0 = G.P(w0, 0)
            S1 = G.P(w0 + Lp * math.tan(flare), -Lp)
            sd = G.unit(S1 - S0)                      # Seitennaht-Richtung (nach unten)
            perp_in = np.array([sd[1], -sd[0]])       # ⟂ Seite, zur Mitte hin
            drop = Lp * (1 / math.cos(flare) - 1)     # Saum in der Mitte tiefer
            rise = w0 * math.tan(flare) * 0.5         # Taille in der Mitte tiefer
            H0, T0 = G.P(0, -Lp - drop), G.P(0, -rise)
            hem_c = G.tangent_curve(H0, (1, 0), S1, -perp_in, 0.4, 0.4)
            top_c = G.tangent_curve(S0, perp_in, T0, (-1, 0), 0.4, 0.4)
            edges = [
                Edge("mitte", G.line(T0, H0), 0.0, True, "Mitte (Bruch)"),
                Edge("saum", hem_c, hem_sa, label="Saum"),
                Edge("seite", G.line(S1, S0), sa, label="Seitennaht"),
                Edge("bund", top_c, sa, label="Bund"),
            ]
            pieces.append(Piece(key, name, edges, cut_count=1, mirror=False,
                                grain=(G.P(w0 * 0.4, -Lp * 0.2), G.P(w0 * 0.4, -Lp * 0.8))))
        hem = 4 * pieces[0].edge("saum").length
    elif style == "teller":
        top = o["top_total"] or m["hip"] * 1.05
        r = top / (2 * math.pi)
        R = r + Lp
        for key, name in (("vorderrock", "Tellerrock vorne"), ("rueckenrock", "Tellerrock hinten")):
            # Viertelkreis rechts unterhalb der Mitte: Bruch links (x = 0), Seitennaht oben (y = 0)
            t = np.linspace(-math.pi / 2, 0, 200)
            outer = np.stack([R * np.cos(t), R * np.sin(t)], 1)       # (0,-R) → (R,0)
            inner = np.stack([r * np.cos(t), r * np.sin(t)], 1)[::-1]  # (r,0) → (0,-r)
            edges = [
                Edge("mitte", G.line(G.P(0, -r), G.P(0, -R)), 0.0, True, "Mitte (Bruch)"),
                Edge("saum", outer, 15.0, label="Saum (schmal)"),
                Edge("seite", G.line(G.P(R, 0), G.P(r, 0)), sa, label="Seitennaht"),
                Edge("bund", inner, sa, label="Bund"),
            ]
            pieces.append(Piece(key, name, edges, cut_count=1, mirror=False,
                                grain=(G.P(R * 0.08, -(r + (R - r) * 0.3)), G.P(R * 0.08, -(r + (R - r) * 0.7)))))
        hem = 2 * math.pi * R
    else:
        raise ValueError(f"Unbekannter Rockstil {style}")
    top_len = 2 * sum(p.edge("bund").length for p in pieces)
    band_len = top_len if style != "gerafft" else max(m["hip"] * 1.05, m["waist"] * 1.0)
    band = rect_piece("bund", "Bund (mit Gummi)", band_len / 2, 2 * wb_h, sa=sa, cut_count=1, fold_left=True,
                      labels=("Ansatz", "Quernaht", "Ansatz", "Mitte"))
    band.marks.append(Mark(G.line(G.P(0, wb_h), G.P(band_len / 2, wb_h)), "fold", "Umbruch"))
    pieces.append(band)
    if style == "gerafft":
        seams.append(dict(name="Bund ↔ Rockoberkante (eingereiht)", a=[("vorderrock", "bund", 2), ("rueckenrock", "bund", 2)],
                          b=[("bund", "unten", 2)], type="ratio", lo=1 / (o["gather"] + 0.4), hi=0.85,
                          note="Rock wird eingereiht (gewollte Mehrlänge)"))
    else:
        seams.append(dict(name="Bund ↔ Rockoberkante", a=[("vorderrock", "bund", 2), ("rueckenrock", "bund", 2)],
                          b=[("bund", "unten", 2)], type="equal"))
    seams.insert(0, dict(name="Seitennaht vorne ↔ hinten", a=[("vorderrock", "seite", 1)],
                         b=[("rueckenrock", "seite", 1)], type="equal"))
    corners += [dict(name="Saum ↔ Seitennaht", piece="vorderrock", a="saum", b="seite", target=90),
                dict(name="Seitennaht ↔ Bund", piece="vorderrock", a="seite", b="bund", target=90),
                dict(name="Bund ↔ Mitte", piece="vorderrock", a="bund", b="mitte", target=90)]
    elastic = m["waist"] * 0.9
    checks.append(dict(name="Bund passt über die Hüfte", kind="min", value=band_len, target=m["hip"] * 1.02,
                       note="Bund ungedehnt ≥ Hüfte (Gummi zieht zusammen)"))
    titles = {"gerafft": "Gummizugrock", "a_linie": "A-Linien-Rock", "teller": "Tellerrock"}
    pat = Pattern("skirt", titles[style], "", pieces, dict(m), o, seams=seams, corners=corners, checks=checks,
                  notes=[f"Gummiband {25 if not adult else 30} mm breit, Länge {elastic / 10:.0f} cm (+2 cm)"])
    pat.finished = dict(top_circ=top_len, hem_circ=hem, length=L, waist_relaxed=elastic)
    return pat


def sewing_steps(pat):
    st = pat.options["style"]
    s = ["**Seitennähte:** Vorder- und Rückenrock rechts auf rechts legen, Seitennähte schließen und versäubern."]
    if st == "gerafft":
        s.append("**Einreihen:** Oberkante mit zwei Reihfäden (größte Stichlänge) einreihen, bis sie der "
                 "Bundlänge entspricht; Kräuselung gleichmäßig verteilen.")
    s += ["**Bund:** zur Runde schließen (Quernaht hinten, 3 cm offen lassen), längs falten, rechts auf rechts "
          "an die Rockoberkante nähen. Gummi einziehen, Enden vernähen, Öffnung schließen.",
          "**Saum:** Saumzugabe doppelt umbügeln und festnähen." if st != "teller" else
          "**Saum:** Rock 24 h hängen lassen, Saum begradigen, schmal (2 × 0,7 cm) umnähen.",
          "Fertig!"]
    return s
