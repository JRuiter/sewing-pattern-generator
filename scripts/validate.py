"""Nähbarkeits-Validierung. Ein Schnitt mit mindestens einem FEHLER wird nicht ausgeliefert.

Prüfungen:
  1. Nahtpaare gleich lang (± 2 mm) bzw. gewollte Differenz/Verhältnis im Sollbereich
  2. Winkel an Nahtenden (rechte Winkel an Mittel-/Seitennähten, glatte Übergänge)
  3. Umfänge = Körpermaß + Mehrweite (± 1 %), Plausibilität von Längen, Kopf/Fuß/Hüfte passt
  4. Geometrie: geschlossene Kontur, keine Selbstüberschneidung, Nahtzugabe überall vorhanden
  5. Jedes Teil hat Fadenlauf und Zuschnittangabe
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from shapely.geometry import LineString, Point, Polygon

import geometry as G
from pattern import Pattern

SEAM_TOL = 2.0     # mm
ANGLE_TOL = 3.0    # Grad (OK)
ANGLE_WARN = 6.0   # Grad (Warnung, darüber Fehler)


@dataclass
class Check:
    group: str
    name: str
    status: str          # OK | WARNUNG | FEHLER
    soll: str
    ist: str
    delta: str
    note: str = ""


class ValidationError(Exception):
    def __init__(self, report):
        self.report = report
        fails = [c for c in report if c.status == "FEHLER"]
        super().__init__("Schnitt nicht nähbar: " + "; ".join(f"{c.name} ({c.ist})" for c in fails))


def _cm(v):
    return f"{v / 10:.1f} cm".replace(".", ",")


def _mm(v):
    return f"{v:+.1f} mm".replace(".", ",")


def _sum_len(pat: Pattern, refs):
    return sum(pat.piece(p).edge(e).length * n for p, e, n in refs)


def _ref_text(pat, refs):
    out = []
    for p, e, n in refs:
        pc = pat.piece(p)
        lab = pc.edge(e).label or e
        out.append(f"{f'{n}× ' if n != 1 else ''}{pc.name}.{lab}")
    return " + ".join(out)


def check_seams(pat: Pattern):
    res = []
    for s in pat.seams:
        a, b = _sum_len(pat, s["a"]), _sum_len(pat, s["b"])
        t = s.get("type", "equal")
        if t == "equal":
            d = b - a
            st = "OK" if abs(d) <= SEAM_TOL else "FEHLER"
            res.append(Check("Nahtpaare", s["name"], st, _cm(a), _cm(b), _mm(d), s.get("note", "")))
        elif t == "ratio":
            r = b / a if a else 0
            st = "OK" if s["lo"] - 0.005 <= r <= s["hi"] + 0.005 else "FEHLER"
            res.append(Check("Nahtpaare", s["name"], st,
                             f"{s['lo'] * 100:.0f}–{s['hi'] * 100:.0f} % von {_cm(a)}",
                             f"{_cm(b)} = {r * 100:.0f} %", _mm(b - a),
                             s.get("note", "Bündchen wird beim Annähen gedehnt")))
        elif t == "ease":
            d = b - a
            st = "OK" if s["lo"] - 0.5 <= d <= s["hi"] + 0.5 else "FEHLER"
            res.append(Check("Nahtpaare", s["name"], st,
                             f"Einhalten {s['lo']:.0f}–{s['hi']:.0f} mm",
                             f"{_cm(a)} ↔ {_cm(b)}", _mm(d), s.get("note", "Einhaltemenge")))
    return res


def _angle(pat, piece, a, b):
    pc = pat.piece(piece)
    return G.corner_angle(pc.edge(a).pts, pc.edge(b).pts)


def _status_angle(d):
    return "OK" if d <= ANGLE_TOL else ("WARNUNG" if d <= ANGLE_WARN else "FEHLER")


def check_corners(pat: Pattern):
    res = []
    for c in pat.corners:
        if "sum" in c:
            ang = sum(_angle(pat, p, a, b) for p, a, b in c["sum"])
            tol = 4.0
        else:
            ang = _angle(pat, c["piece"], c["a"], c["b"])
            tol = 0.0
        d = abs(ang - c["target"])
        st = _status_angle(max(0.0, d - tol))
        res.append(Check("Winkel/Übergänge", c["name"], st, f"{c['target']:.0f}°",
                         f"{ang:.1f}°".replace(".", ","), f"{ang - c['target']:+.1f}°".replace(".", ","), c.get("note", "")))
    return res


def check_values(pat: Pattern):
    res = []
    for c in pat.checks:
        k = c["kind"]
        v = c["value"]
        if k == "circ":
            rel = (v - c["target"]) / c["target"]
            st = "OK" if abs(rel) <= c.get("tol_rel", 0.01) else "FEHLER"
            res.append(Check("Maße", c["name"], st, _cm(c["target"]), _cm(v),
                             f"{rel * 100:+.1f} %".replace(".", ","), c.get("note", "")))
        elif k == "min":
            st = "OK" if v >= c["target"] else c.get("fail", "FEHLER")
            unit_pct = c.get("unit") == "%" or "Dehnung" in c["name"] or "dehnbar" in c["name"]
            fmt = (lambda x: f"{x:.0f} %") if unit_pct else _cm
            res.append(Check("Maße", c["name"], st, "≥ " + fmt(c["target"]), fmt(v),
                             (f"{v - c['target']:+.0f} %" if unit_pct else _mm(v - c["target"])),
                             c.get("note", "")))
        elif k == "range":
            st = "OK" if c["lo"] <= v <= c["hi"] else c.get("fail", "WARNUNG")
            d = 0.0 if st == "OK" else (v - c["lo"] if v < c["lo"] else v - c["hi"])
            res.append(Check("Maße", c["name"], st, f"{_cm(c['lo'])} – {_cm(c['hi'])}", _cm(v),
                             _mm(d), c.get("note", "")))
    return res


def check_geometry(pat: Pattern):
    res = []
    for pc in pat.pieces:
        errs = pc.check_closed()
        ring = pc.seam_ring()
        if G.polyline_self_intersects(np.vstack([ring, ring[:1]])):
            errs.append("Nählinie überschneidet sich selbst")
        try:
            cut = pc.cut_ring()
            cpoly = Polygon(cut)
            if not cpoly.is_valid:
                errs.append("Schnittlinie ungültig/selbstüberschneidend")
            spoly = Polygon(ring)
            if not cpoly.buffer(0.5).contains(spoly):
                errs.append("Schnittlinie umschließt Nählinie nicht")
            boundary = LineString(np.vstack([cut, cut[:1]]))
            for e in pc.edges:
                if e.fold:
                    continue
                if e.sa <= 0:
                    errs.append(f"Kante '{e.label or e.name}' ohne Nahtzugabe")
                    continue
                L = e.length
                margin = max(e.sa, 5.0) + 2.0
                if L < 2 * margin + 2:
                    continue
                dmin = 1e9
                for s in np.linspace(margin, L - margin, max(3, int(L / 20))):
                    p = G.point_at(e.pts, s)
                    t = G.tangent_at(e.pts, s)
                    n = np.array([t[1], -t[0]])
                    ray = LineString([p, p + n * (e.sa * 3 + 5)])
                    hit = ray.intersection(boundary)
                    if hit.is_empty:
                        dist = 0.0
                    else:
                        dist = min(Point(p).distance(g) for g in getattr(hit, "geoms", [hit]))
                    dmin = min(dmin, dist)
                if dmin < e.sa - 1.0:
                    errs.append(f"Nahtzugabe an '{e.label or e.name}' nur {dmin:.1f} mm statt {e.sa:.0f} mm")
        except Exception as ex:  # pragma: no cover
            errs.append(f"Schnittlinie nicht berechenbar: {ex}")
        res.append(Check("Geometrie", f"{pc.name}: Kontur & Nahtzugabe",
                         "OK" if not errs else "FEHLER", "geschlossen, NZ vorhanden",
                         "ok" if not errs else "; ".join(errs), "", pc.sa_text()))
        info_err = []
        if pc.grain is None:
            info_err.append("Fadenlauf fehlt")
        elif not Polygon(ring).buffer(1).contains(LineString(np.array(pc.grain))):
            info_err.append("Fadenlauf liegt nicht im Teil")
        if pc.cut_count < 1:
            info_err.append("Zuschnittangabe fehlt")
        res.append(Check("Beschriftung", f"{pc.name}: Fadenlauf & Zuschnitt",
                         "OK" if not info_err else "FEHLER", "vorhanden",
                         pc.cut_text() if not info_err else "; ".join(info_err), "", pc.fabric))
    return res


def validate(pat: Pattern, raise_on_error: bool = False):
    report = check_seams(pat) + check_corners(pat) + check_values(pat) + check_geometry(pat)
    if raise_on_error and any(c.status == "FEHLER" for c in report):
        raise ValidationError(report)
    return report


def is_ok(report) -> bool:
    return not any(c.status == "FEHLER" for c in report)


def to_markdown(report, title: str = "Nähbarkeits-Prüfung") -> str:
    icon = {"OK": "✅ OK", "WARNUNG": "⚠️ Warnung", "FEHLER": "❌ Fehler"}
    lines = [f"### {title}", "", "| Bereich | Prüfung | Soll | Ist | Δ | Ergebnis | Hinweis |",
             "|---|---|---|---|---|---|---|"]
    for c in report:
        lines.append(f"| {c.group} | {c.name} | {c.soll} | {c.ist} | {c.delta} | {icon[c.status]} | {c.note} |")
    n_ok = sum(c.status == "OK" for c in report)
    n_w = sum(c.status == "WARNUNG" for c in report)
    n_f = sum(c.status == "FEHLER" for c in report)
    lines += ["", f"**Ergebnis:** {n_ok} OK, {n_w} Warnung(en), {n_f} Fehler – "
              + ("Schnitt ist nähbar." if n_f == 0 else "Schnitt NICHT ausliefern.")]
    return "\n".join(lines)


def to_rows(report):
    return [c.__dict__ for c in report]
