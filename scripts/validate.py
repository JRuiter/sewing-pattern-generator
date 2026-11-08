"""Sewability validation. A pattern with at least one ERROR is never delivered.

Checks:
  1. Seam pairs equal in length (± 2 mm) or an intended difference/ratio within range
  2. Angles at seam ends (right angles at centre/side seams, smooth joined corners)
  3. Circumferences = body measurement + ease (± 1 %), plausible lengths, head/foot/hip fit through
  4. Geometry: closed outline, no self-intersection, seam allowance present everywhere
  5. Every piece has a grainline and cutting instructions
  6. Fold edges: straight, no seam allowance, the neighbouring edges meet them at a right
     angle (no peak or dip at the centre once unfolded), parallel to the grainline
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
            if c.get("unit") == "%":
                res.append(Check(c.get("group", "Measurements"), c["name"], st,
                                 f"{c['lo'] * 100:.0f} – {c['hi'] * 100:.0f} %", f"{v * 100:.0f} %",
                                 f"{d * 100:+.0f} %", c.get("note", "")))
            else:
                res.append(Check(c.get("group", "Measurements"), c["name"], st,
                                 f"{_cm(c['lo'])} – {_cm(c['hi'])}", _cm(v), _mm(d), c.get("note", "")))
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
                if e.fold or e.raw:
                    continue
                if e.sa <= 0:
                    if e.sa_hint <= 0:   # sa_hint > 0: pattern deliberately without allowances
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


def _fold_flat_error(pc, e, at_start: bool, boundary: LineString) -> float:
    """Max distance (mm) between the turned-up allowance next to a corner, folded at the
    seam line, and the neighbouring cut line. 0 = the hem lies flat under the seam allowance."""
    if at_start:
        corner, along = e.pts[0], G.start_dir(e.pts, 3.0)
    else:
        corner, along = e.pts[-1], -G.end_dir(e.pts, 3.0)
    d = G.start_dir(e.pts, 3.0) if at_start else G.end_dir(e.pts, 3.0)
    n_out = np.array([d[1], -d[0]])
    ring = boundary.coords
    pts = G.resample(np.asarray(ring, float), 0.5)
    rel = pts - corner
    dist = rel @ n_out
    t = rel @ along
    sel = pts[(dist > 0.5) & (dist < e.sa - 0.5) & (t < 0.5) & (t > -(4 * e.sa + 30))]
    if len(sel) == 0:
        return 0.0
    folded = G.mirror_line(sel, corner, corner + d)
    return max(boundary.distance(Point(q)) for q in folded)


def check_turned(pat: Pattern):
    """Hems and casings: the folded allowance must match the neighbouring seam (mirrored corners)."""
    res = []
    for pc in pat.pieces:
        turned = [e for e in pc.edges if e.turned and e.sa > 0]
        if not turned:
            continue
        cut = pc.cut_ring()
        boundary = LineString(np.vstack([cut, cut[:1]]))
        worst = 0.0
        for e in turned:
            for at_start in (True, False):
                worst = max(worst, _fold_flat_error(pc, e, at_start, boundary))
        # A mitred corner is still sewable, the folded hem just does not lie perfectly flat.
        status = "OK" if worst <= 0.5 else "WARNING"
        names = ", ".join(sorted({e.label or e.name for e in turned}))
        res.append(Check("Geometry", f"{pc.name}: turned allowance lies flat", status, "≤ 0.5 mm",
                         f"{worst:.1f} mm", "", f"{names}: corners mirrored at the fold line"))
    return res


def check_notches(pat: Pattern):
    """Every notch starts on the cutting line (also at corners)."""
    import notches as N
    res = []
    style = pat.options.get("notch_style", "slit") if isinstance(pat.options, dict) else "slit"
    for pc in pat.pieces:
        if not pc.notches:
            continue
        marks = N.piece_marks(pc, style if style in N.SHAPES else "slit")
        errs = N.on_cut_line(pc, marks)
        res.append(Check("Labels", f"{pc.name}: notches", "OK" if not errs else "ERROR", "on the cutting line",
                         f"{len(marks)} notch mark(s)" if not errs else "; ".join(errs), "",
                         f"{sum(m.corner for m in marks)} at corners" if any(m.corner for m in marks) else ""))
    return res


FOLD_STRAIGHT_TOL = 0.5   # mm, max deviation of a fold edge from a straight line
FOLD_GRAIN_TOL = 1.0      # degrees between fold edge and grainline (OK)


def _worse(a: str, b: str) -> str:
    order = ("OK", "WARNING", "ERROR")
    return a if order.index(a) >= order.index(b) else b


def check_folds(pat: Pattern):
    """Cut-on-fold edges. The fold is a mirror line: it must be straight and carry no seam
    allowance, and every edge must meet it at 90°, otherwise the unfolded piece gets a peak
    or a dip at the centre (neckline, hem, waist). The fold edge that goes on the fabric fold
    must run along the grain, because the fabric fold does."""
    res = []
    for pc in pat.pieces:
        folds = [i for i, e in enumerate(pc.edges) if e.fold]
        if not folds:
            continue
        status, found, worst_ang = "OK", [], 0.0

        best_grain = None
        for i in folds:
            e = pc.edges[i]
            pts = np.asarray(e.pts, float)
            a, b = pts[0], pts[-1]
            d = G.unit(b - a)
            n = np.array([-d[1], d[0]])
            dev = float(np.abs((pts - a) @ n).max())
            name = e.label or e.name
            if dev > FOLD_STRAIGHT_TOL:
                status = _worse(status, "ERROR")
                found.append(f"'{name}' not straight ({dev:.1f} mm)")
            if e.sa > 0:
                status = _worse(status, "ERROR")
                found.append(f"'{name}' has a seam allowance ({e.sa:.0f} mm)")
            for other, ang in ((pc.edges[i - 1], G.corner_angle(pc.edges[i - 1].pts, e.pts)),
                               (pc.edges[(i + 1) % len(pc.edges)],
                                G.corner_angle(e.pts, pc.edges[(i + 1) % len(pc.edges)].pts))):
                if other.fold or other.pointed:    # V-neck: the point is checked as a corner
                    continue
                dang = abs(ang - 90.0)
                worst_ang = max(worst_ang, dang)
                st = _status_angle(dang)
                if st != "OK":
                    status = _worse(status, st)
                    found.append(f"'{other.label or other.name}' meets '{name}' at {ang:.1f}°")
            if pc.grain is not None:
                g = G.unit(np.asarray(pc.grain[1], float) - np.asarray(pc.grain[0], float))
                gdev = float(np.degrees(np.arccos(min(1.0, abs(float(g @ d))))))
                best_grain = gdev if best_grain is None else min(best_grain, gdev)
        if best_grain is not None and best_grain > FOLD_GRAIN_TOL:
            status = _worse(status, "WARNING")
            found.append(f"fold edge {best_grain:.1f}° off the grainline")
        actual = "; ".join(found) if found else f"ok, corners ≤ {worst_ang:.1f}° off 90°"
        res.append(Check("Geometry", f"{pc.name}: cut-on-fold edge", status,
                         "straight, no SA, 90° corners, on grain", actual, "",
                         ", ".join(pc.edges[i].label or pc.edges[i].name for i in folds)))
    return res


def validate(pat: Pattern, raise_on_error: bool = False):
    report = (check_seams(pat) + check_corners(pat) + check_values(pat) + check_geometry(pat)
              + check_turned(pat) + check_folds(pat) + check_notches(pat))
    if raise_on_error and any(c.status == "ERROR" for c in report):
        raise ValidationError(report)
    return report


def is_ok(report) -> bool:
    return not any(c.status == "ERROR" for c in report)


def to_markdown(report, title: str = "Sewability check") -> str:
    from i18n import t
    icon = {"OK": "✅ OK", "WARNING": "⚠️ " + t("Warning"), "ERROR": "❌ " + t("Error")}
    head = ("Area", "Check", "Target", "Actual", "Δ", "Result", "Note")
    lines = [f"### {t(title)}", "", "| " + " | ".join(t(h) for h in head) + " |",
             "|---|---|---|---|---|---|---|"]
    for c in report:
        cells = [t(c.group), t(c.name), t(c.target), t(c.actual), t(c.delta), icon[c.status], t(c.note)]
        lines.append("| " + " | ".join(cells) + " |")
    n_ok = sum(c.status == "OK" for c in report)
    n_w = sum(c.status == "WARNING" for c in report)
    n_f = sum(c.status == "ERROR" for c in report)
    lines += ["", t(f"**Result:** {n_ok} OK, {n_w} warning(s), {n_f} error(s): ")
              + t("the pattern is sewable." if n_f == 0 else "do NOT deliver this pattern.")]
    return "\n".join(lines)


def to_rows(report):
    from i18n import t
    return [{**c.__dict__, "group": t(c.group), "name": t(c.name), "target": t(c.target), "actual": t(c.actual),
             "delta": t(c.delta), "note": t(c.note)} for c in report]
