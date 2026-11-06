"""Hoodie / Sweatshirt: T-Shirt-Grundschnitt (Sweat, weit, Langarm mit Bündchen,
Saumbündchen) + Kapuze (zweiteilig, gegengleich) und optionale Kängurutasche.
Ohne Kapuze entsteht ein Sweatshirt mit Halsbündchen."""
from __future__ import annotations

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece

from . import tshirt_basic as T

DEFAULTS = dict(fit="weit", fabric="sweat", hood=True, kangaroo=True, sleeve_style="eingesetzt",
                sleeve_length="lang", sleeve_cuffs=True, hem_band=True, hood_lining=False)

FINISHED_LABELS = dict(T.FINISHED_LABELS, hood_height=("Kapuzenhöhe", "laenge"))


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    hood = bool(o.pop("hood"))
    kang = bool(o.pop("kangaroo"))
    lining = bool(o.pop("hood_lining"))
    if hood:
        o.setdefault("neck_extra", 8.0)
        o["neckline"] = "rund"
    pat = T.draft(measures, o, _garment="hoodie")
    m = measures
    pat.title = "Hoodie" if hood else "Sweatshirt"
    pat.options.update(hood=hood, kangaroo=kang, hood_lining=lining)
    sa = pat.options["sa"]
    front = pat.piece("vorderteil")
    if hood:
        # Halsbündchen entfernen, Kapuze ergänzen
        pat.pieces = [p for p in pat.pieces if p.key != "halsbuendchen"]
        pat.seams = [s for s in pat.seams if not any(k == "halsbuendchen" for k, _, _ in s["b"])]
        pat.checks = [c for c in pat.checks if c["name"] != "Halsausschnitt passt über den Kopf"]
        refs = [("vorderteil", "ausschnitt", 1), ("rueckenteil", "ausschnitt", 1)]
        if pat.piece("aermel").edges[-1].name == "hals":
            refs.append(("aermel", "hals", 1))
        half_neck = sum(pat.piece(k).edge(e).length * n for k, e, n in refs)
        Hh = 0.58 * m["head"] + 25
        Wh = 0.44 * m["head"] + 15
        # Halskante: leicht nach unten gebogen, Länge = halber Ausschnitt
        def neck_curve(bx):
            return G.cubic(G.P(0, 0), G.P(bx * 0.35, 0), G.P(bx * 0.7, -8), G.P(bx, 18))
        lo, hi = half_neck * 0.6, half_neck * 1.05
        for _ in range(50):
            bx = (lo + hi) / 2
            if G.length(neck_curve(bx)) < half_neck:
                lo = bx
            else:
                hi = bx
        neck = neck_curve((lo + hi) / 2)
        B0 = neck[-1]
        Tp = G.P(0, Hh)
        back = G.cubic(B0, B0 + np.array([max(Wh - B0[0], 10) * 0.9 + 15, Hh * 0.3]),
                       G.P(Wh * 0.95, Hh * 1.02), Tp)
        back = G.join(back)
        edges = [
            Edge("hals", neck, sa, label="Halsnaht"),
            Edge("mitte", back, sa, label="Kapuzenmittelnaht"),
            Edge("vorne", G.line(Tp, G.P(0, 0)), 25.0, label="Vorderkante (Tunnel/Beleg)"),
        ]
        hp = Piece("kapuze", "Kapuze", edges, cut_count=4 if lining else 2, mirror=True, fabric="Oberstoff",
                   grain=(G.P(Wh * 0.4, Hh * 0.2), G.P(Wh * 0.4, Hh * 0.75)))
        hp.marks.append(Mark(G.line(G.P(12, Hh * 0.92), G.P(12, 8)), "fold", "Umbruch Vorderkante"))
        if lining:
            hp.info.append("2× Oberstoff + 2× Futter (Jersey)")
        pat.pieces.append(hp)
        pat.seams.append(dict(name="Kapuze ↔ Halsausschnitt (je Seite)", a=refs, b=[("kapuze", "hals", 1)],
                              type="equal"))
        pat.seams.append(dict(name="Kapuzenmittelnaht (links ↔ rechts)", a=[("kapuze", "mitte", 1)],
                              b=[("kapuze", "mitte", 1)], type="equal"))
        pat.corners.append(dict(name="Kapuze: Vorderkante ↔ Halsnaht", piece="kapuze", a="vorne", b="hals",
                                target=90))
        pat.checks.append(dict(name="Kapuze hoch genug", kind="min", value=Hh + 0.0, target=0.55 * m["head"],
                               note="Kapuzenhöhe ≥ 0,55 × Kopfumfang"))
        pat.finished["hood_height"] = Hh
    if kang:
        F = pat.options["_F"]
        q = F["q"]
        hem_y = float(front.edge("saum").pts[0, 1])
        Wk, Hk = q * 0.62, min(0.36 * F["L"], 0.45 * (-hem_y - F["AD"]))
        op = Hk * 0.55
        pts = [G.P(0, 0), G.P(Wk, 0), G.P(Wk, Hk - op), G.P(Wk - op * 0.45, Hk), G.P(0, Hk)]
        edges = [
            Edge("unten", G.line(pts[0], pts[1]), sa, label="Saumnaht"),
            Edge("seite", G.line(pts[1], pts[2]), sa, label="Seite"),
            Edge("eingriff", G.line(pts[2], pts[3]), 15.0, label="Eingriff (umsäumen)"),
            Edge("oben", G.line(pts[3], pts[4]), sa, label="Oberkante (umbügeln)"),
            Edge("mitte", G.line(pts[4], pts[0]), 0.0, True, "Mitte (Bruch)"),
        ]
        kp = Piece("kaengurutasche", "Kängurutasche", edges, cut_count=1, mirror=False, fabric="Oberstoff",
                   grain=(G.P(Wk * 0.35, Hk * 0.2), G.P(Wk * 0.35, Hk * 0.8)))
        pat.pieces.append(kp)
        y0 = hem_y
        front.marks.append(Mark(np.array([[0, y0 + Hk], [Wk - op * 0.45, y0 + Hk], [Wk, y0 + Hk - op],
                                          [Wk, y0]]), "placement", "Kängurutasche"))
    return pat


def finished_measures(pat):
    return T.finished_measures(pat)


def sewing_steps(pat):
    o = pat.options
    steps = []
    if o.get("kangaroo"):
        steps.append("**Kängurutasche:** Eingriffkanten 1,5 cm umbügeln und absteppen, Oberkante 1 cm umbügeln. "
                     "Tasche nach Markierung auf das Vorderteil legen, Oberkante und Seiten aufsteppen; die "
                     "Unterkante wird später mit dem Saumbündchen gefasst.")
    base = T.sewing_steps(pat)
    if o.get("hood"):
        base = [s for s in base if not s.startswith("**Halsbündchen")]
        hood = ["**Kapuze:** Kapuzenteile rechts auf rechts legen und die Mittelnaht schließen. Vorderkante "
                "an der Umbruchlinie nach innen bügeln und absteppen (Tunnel für eine Kordel möglich)" +
                (" – bei gefütterter Kapuze Futter separat nähen und rechts auf rechts an der Vorderkante "
                 "verstürzen" if o.get("hood_lining") else "") + ".",
                "**Kapuze annähen:** Kapuze rechts auf rechts an den Halsausschnitt stecken (Mittelnaht an "
                "hintere Mitte, Vorderkanten treffen sich an der vorderen Mitte, ggf. 1 cm überlappen) und "
                "annähen. Nahtzugabe mit einem Jerseyband versäubern."]
        base = base[:1] + hood + base[1:]
    return steps + base
