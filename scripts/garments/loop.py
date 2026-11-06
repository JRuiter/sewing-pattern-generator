"""Loop / Schlauchschal: ein Rechteck, längs gefaltet (doppellagig), zur Runde geschlossen."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Mark, Pattern, rect_piece

DEFAULTS = dict(fabric="jersey", stretch=None, height=None, wraps=1, sa=10.0, circ_total=None)
FINISHED_LABELS = {"circ": ("Umfang", "weite"), "height": ("Höhe (doppellagig)", "laenge")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    circ = o["circ_total"] or (m["head"] * 1.2 if o["wraps"] == 1 else m["head"] * 2.6)
    h = o["height"] or (0.17 * m["height"] if m["height"] < 1650 else 300.0)
    p = rect_piece("loop", "Loop", circ, 2 * h, sa=o["sa"], cut_count=1, names=("unten", "rechts", "oben", "links"),
                   labels=("Längskante", "Quernaht", "Längskante", "Quernaht"), grain_vertical=False)
    p.marks.append(Mark(G.line(G.P(0, h), G.P(circ, h)), "fold", "Umbruch"))
    seams = [dict(name="Quernaht (rechts ↔ links)", a=[("loop", "rechts", 1)], b=[("loop", "links", 1)], type="equal"),
             dict(name="Längskanten aufeinander", a=[("loop", "unten", 1)], b=[("loop", "oben", 1)], type="equal")]
    corners = [dict(name="Ecke unten rechts", piece="loop", a="unten", b="rechts", target=90)]
    checks = [dict(name="Loop passt über den Kopf", kind="min", value=circ * (1 + stretch / 100 * 0.5),
                   target=m["head"] * 1.1, note="Umfang inkl. Dehnung")]
    pat = Pattern("loop", "Loop", "", [p], dict(m), o, seams=seams, corners=corners, checks=checks)
    pat.finished = dict(circ=circ, height=h)
    return pat


def sewing_steps(pat):
    return ["**Längsnaht:** Rechteck längs rechts auf rechts falten, lange Kanten zu einem Schlauch nähen.",
            "**Wenden:** Schlauch auf rechts wenden. Ein Ende in das andere stecken (rechts auf rechts), "
            "Quernaht bis auf 5 cm schließen.",
            "**Schließen:** wenden und die Öffnung von Hand (Matratzenstich) schließen. Fertig!"]
