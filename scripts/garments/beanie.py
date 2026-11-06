"""Beanie (Jersey/Bündchen): zwei gleiche Teile mit runder Kuppel, optional Umschlagbündchen."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

DEFAULTS = dict(fabric="jersey", stretch=None, brim=True, slouch=False, sa=7.0, hem_sa=20.0, circ_total=None)
FINISHED_LABELS = {"circ": ("Mützenweite (entspannt)", "weite"), "height": ("Mützenhöhe", "laenge")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    head = m["head"]
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    circ = o["circ_total"] or head * (0.86 if stretch >= 30 else 0.98)
    W = circ / 2
    H = head * (0.36 if not o["slouch"] else 0.48)
    Hs = H - W * 0.42
    sa = o["sa"]
    brim_h = 0.10 * head if o["brim"] else 0.0
    right = G.line(G.P(W, 0), G.P(W, Hs))
    dome = G.join(G.tangent_curve(G.P(W, Hs), (0, 1), G.P(W / 2, H), (-1, 0), 0.55, 0.55),
                  G.tangent_curve(G.P(W / 2, H), (-1, 0), G.P(0, Hs), (0, -1), 0.55, 0.55))
    left = G.line(G.P(0, Hs), G.P(0, 0))
    edges = [Edge("unten", G.line(G.P(0, 0), G.P(W, 0)), sa if o["brim"] else o["hem_sa"],
                  label="Bündchenansatz" if o["brim"] else "Saum"),
             Edge("rechts", right, sa, label="Seitennaht"), Edge("kuppel", dome, sa, label="Kuppelnaht"),
             Edge("links", left, sa, label="Seitennaht")]
    p = Piece("muetze", "Mütze", edges, cut_count=2, mirror=False, fabric="Oberstoff",
              grain=(G.P(W / 2, H * 0.15), G.P(W / 2, H * 0.7)))
    p.stretch_dir = "Dehnrichtung quer"
    pieces = [p]
    seams = [dict(name="Kuppelnaht vorne ↔ hinten", a=[("muetze", "kuppel", 1)], b=[("muetze", "kuppel", 1)],
                  type="equal"),
             dict(name="Seitennähte", a=[("muetze", "rechts", 1)], b=[("muetze", "links", 1)], type="equal")]
    if o["brim"]:
        bl = circ * 0.92
        b = rect_piece("umschlag", "Umschlagbündchen", bl, 2 * brim_h, sa=sa, cut_count=1, fabric="Bündchen",
                       labels=("Ansatz", "Quernaht", "Ansatz", "Quernaht"))
        b.marks.append(Mark(G.line(G.P(0, brim_h), G.P(bl, brim_h)), "fold", "Umbruch"))
        pieces.append(b)
        seams.append(dict(name="Umschlagbündchen ↔ Mützenkante (gedehnt)", a=[("muetze", "unten", 2)],
                          b=[("umschlag", "unten", 1)], type="ratio", lo=0.88, hi=0.96))
    corners = [dict(name="Seite ↔ Kuppel (glatt)", piece="muetze", a="rechts", b="kuppel", target=180),
               dict(name="Unterkante ↔ Seite", piece="muetze", a="unten", b="rechts", target=90)]
    checks = [dict(name="Mütze passt über den Kopf", kind="min", value=circ * (1 + stretch / 100), target=head * 1.05,
                   note="Weite inkl. Dehnung"),
              dict(name="Mütze sitzt (nicht zu weit)", kind="range", value=circ, lo=head * 0.78, hi=head * 1.0,
                   note="negative Mehrweite bei Jersey")]
    pat = Pattern("beanie", "Beanie", "", pieces, dict(m), o, seams=seams, corners=corners, checks=checks)
    pat.finished = dict(circ=circ, height=H + brim_h)
    return pat


def sewing_steps(pat):
    s = ["**Mütze:** beide Teile rechts auf rechts legen, Seiten- und Kuppelnaht in einem Zug nähen "
         "(Overlock oder Zickzack)."]
    if pat.options.get("brim"):
        s.append("**Umschlag:** Bündchen zur Runde schließen, längs falten, gedehnt an die Mützenkante nähen.")
    else:
        s.append("**Saum:** 2 cm umbügeln, mit Zwillingsnadel nähen.")
    s.append("Wenden – fertig!")
    return s
