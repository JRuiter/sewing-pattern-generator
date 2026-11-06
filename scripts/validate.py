"""Sewability validation. A pattern with at least one ERROR is never delivered.

Checks:
  1. Seam pairs equal in length (± 2 mm) or an intended difference/ratio within range
  2. Angles at seam ends (right angles at centre/side seams, smooth joined corners)
  3. Circumferences = body measurement + ease (± 1 %), plausible lengths, head/foot/hip fit through
  4. Geometry: closed outline, no self-intersection, seam allowance present everywhere
  5. Every piece has a grainline and cutting instructions
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from shapely.geometry import LineString, Point, Polygon

import geometry as G
from pattern import Pattern

SEAM_TOL = 2.0     # mm
ANGLE_TOL = 3.0    # degrees (OK)
ANGLE_WARN = 6.0   # degrees (warning, error above)


@dataclass
class Check:
    group: str
    name: str
    status: str          # OK | WARNING | ERROR
    target: str
    actual: str
    delta: str
    note: str = ""


class ValidationError(Exception):
    def __init__(self, report):
        self.report = report
        fails = [c for c in report if c.status == "ERROR"]
        super().__init__("Pattern is not sewable: " + "; ".join(f"{c.name} ({c.actual})" for c in fails))


def _cm(v):
    return f"{v / 10:.1f} cm"


def _mm(v):
    return f"{v:+.1f} mm"


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
            st = "OK" if abs(d) <= SEAM_TOL else "ERROR"
            res.append(Check("Seam pairs", s["name"], st, _cm(a), _cm(b), _mm(d), s.get("note", "")))
        elif t == "ratio":
            r = b / a if a else 0
            st = "OK" if s["lo"] - 0.005 <= r <= s["hi"] + 0.005 else "ERROR"
            res.append(Check("Seam pairs", s["name"], st,
                             f"{s['lo'] * 100:.0f}–{s['hi'] * 100:.0f} % of {_cm(a)}",
                             f"{_cm(b)} = {r * 100:.0f} %", _mm(b - a),
                             s.get("note", "rib band is stretched while sewing")))
        elif t == "ease":
            d = b - a
            st = "OK" if s["lo"] - 0.5 <= d <= s["hi"] + 0.5 else "ERROR"
            res.append(Check("Seam pairs", s["name"], st,
                             f"ease {s['lo']:.0f}–{s['hi']:.0f} mm",
                             f"{_cm(a)} ↔ {_cm(b)}", _mm(d), s.get("note", "sleeve-cap ease")))
    return res


def _angle(pat, piece, a, b):
    pc = pat.piece(piece)
    return G.corner_angle(pc.edge(a).pts, pc.edge(b).pts)


def _status_angle(d):
    return "OK" if d <= ANGLE_TOL else ("WARNING" if d <= ANGLE_WARN else "ERROR")


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
        res.append(Check("Angles/transitions", c["name"], st, f"{c['target']:.0f}°",
                         f"{ang:.1f}°", f"{ang - c['target']:+.1f}°", c.get("note", "")))
    return res


def check_values(pat: Pattern):
    res = []
    for c in pat.checks:
        k = c["kind"]
        v = c["value"]
        if k == "circ":
            rel = (v - c["target"]) / c["target"]
            st = "OK" if abs(rel) <= c.get("tol_rel", 0.01) else "ERROR"
            res.append(Check("Measurements", c["name"], st, _cm(c["target"]), _cm(v),
                             f"{rel * 100:+.1f} %", c.get("note", "")))
        elif k == "min":
            st = "OK" if v >= c["target"] else c.get("fail", "ERROR")
            unit_pct = c.get("unit") == "%" or "stretch" in c["name"].lower()
            fmt = (lambda x: f"{x:.0f} %") if unit_pct else _cm
            res.append(Check("Measurements", c["name"], st, "≥ " + fmt(c["target"]), fmt(v),
                             (f"{v - c['target']:+.0f} %" if unit_pct else _mm(v - c["target"])),
                             c.get("note", "")))
        elif k == "range":
            st = "OK" if c["lo"] <= v <= c["hi"] else c.get("fail", "WARNING")
            d = 0.0 if st == "OK" else (v - c["lo"] if v < c["lo"] else v - c["hi"])
            res.append(Check("Measurements", c["name"], st, f"{_cm(c['lo'])} – {_cm(c['hi'])}", _cm(v),
                             _mm(d), c.get("note", "")))
    return res


def check_geometry(pat: Pattern):
    res = []
    for pc in pat.pieces:
        errs = pc.check_closed()
        ring = pc.seam_ring()
        if G.polyline_self_intersects(np.vstack([ring, ring[:1]])):
            errs.append("seam line intersects itself")
        try:
            cut = pc.cut_ring()
            cpoly = Polygon(cut)
            if not cpoly.is_valid:
                errs.append("cutting line invalid/self-intersecting")
            spoly = Polygon(ring)
            if not cpoly.buffer(0.5).contains(spoly):
                errs.append("cutting line does not enclose the seam line")
            boundary = LineString(np.vstack([cut, cut[:1]]))
            for e in pc.edges:
                if e.fold:
                    continue
                if e.sa <= 0:
                    errs.append(f"edge '{e.label or e.name}' has no seam allowance")
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
                    errs.append(f"seam allowance at '{e.label or e.name}' only {dmin:.1f} mm instead of {e.sa:.0f} mm")
        except Exception as ex:  # pragma: no cover
            errs.append(f"cutting line could not be computed: {ex}")
        res.append(Check("Geometry", f"{pc.name}: outline & seam allowance",
                         "OK" if not errs else "ERROR", "closed, SA present",
                         "ok" if not errs else "; ".join(errs), "", pc.sa_text()))
        info_err = []
        if pc.grain is None:
            info_err.append("grainline missing")
        elif not Polygon(ring).buffer(1).contains(LineString(np.array(pc.grain))):
            info_err.append("grainline not inside the piece")
        if pc.cut_count < 1:
            info_err.append("cutting instruction missing")
        res.append(Check("Labels", f"{pc.name}: grainline & cutting",
                         "OK" if not info_err else "ERROR", "present",
                         pc.cut_text() if not info_err else "; ".join(info_err), "", pc.fabric))
    return res


def validate(pat: Pattern, raise_on_error: bool = False):
    report = check_seams(pat) + check_corners(pat) + check_values(pat) + check_geometry(pat)
    if raise_on_error and any(c.status == "ERROR" for c in report):
        raise ValidationError(report)
    return report


def is_ok(report) -> bool:
    return not any(c.status == "ERROR" for c in report)


def to_markdown(report, title: str = "Sewability check") -> str:
    icon = {"OK": "✅ OK", "WARNING": "⚠️ Warning", "ERROR": "❌ Error"}
    lines = [f"### {title}", "", "| Area | Check | Target | Actual | Δ | Result | Note |",
             "|---|---|---|---|---|---|---|"]
    for c in report:
        lines.append(f"| {c.group} | {c.name} | {c.target} | {c.actual} | {c.delta} | {icon[c.status]} | {c.note} |")
    n_ok = sum(c.status == "OK" for c in report)
    n_w = sum(c.status == "WARNING" for c in report)
    n_f = sum(c.status == "ERROR" for c in report)
    lines += ["", f"**Result:** {n_ok} OK, {n_w} warning(s), {n_f} error(s): "
              + ("the pattern is sewable." if n_f == 0 else "do NOT deliver this pattern.")]
    return "\n".join(lines)


def to_rows(report):
    return [c.__dict__ for c in report]
