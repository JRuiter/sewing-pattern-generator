"""Print output: vector PDF (1:1, embedded fonts), SVG master (1:1), PNG preview.

Line types: cutting line solid (1.0 pt), seam line dashed (0.6 pt), fold dash-dot
(1.0 pt). No line thinner than 0.5 pt. Every page carries a 5 × 5 cm control square
(141.73 pt) and a 1-inch square.
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from xml.sax.saxutils import escape

import numpy as np
from reportlab.lib.colors import Color, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as rl_canvas
from shapely.geometry import LineString, Polygon, box
from shapely.ops import polylabel

import allowance as A
import geometry as G
import layout as L
import nested as NE
import notches as N
import units as U
from i18n import t as tr

MM = 72.0 / 25.4        # pt je mm
PT = 25.4 / 72.0        # mm je pt
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")
FONT, FONT_B = "DejaVuSans", "DejaVuSans-Bold"
MIN_LW = 0.5

STYLES = {
    "cut": dict(w=1.0, dash=None, color=(0, 0, 0)),
    "seam": dict(w=0.6, dash=(6, 3), color=(0.15, 0.15, 0.15)),
    "fold": dict(w=1.0, dash=(12, 3, 2, 3), color=(0, 0, 0)),
    "notch": dict(w=0.8, dash=None, color=(0, 0, 0)),
    "grain": dict(w=0.8, dash=None, color=(0, 0, 0)),
    "fold_arrow": dict(w=0.8, dash=None, color=(0, 0, 0)),
    "mark_fold": dict(w=0.6, dash=(9, 3, 2, 3), color=(0.2, 0.2, 0.2)),
    "mark_placement": dict(w=0.6, dash=(3, 3), color=(0.2, 0.2, 0.2)),
    "tile": dict(w=0.5, dash=(3, 3), color=(0.45, 0.45, 0.45)),
    "diamond": dict(w=0.6, dash=None, color=(0.3, 0.3, 0.3)),
}
for _s in STYLES.values():
    assert _s["w"] >= MIN_LW


def register_fonts():
    if FONT not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT, os.path.join(FONT_DIR, "DejaVuSans.ttf")))
        pdfmetrics.registerFont(TTFont(FONT_B, os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))


def text_w_mm(text, size_pt, bold=False):
    register_fonts()
    return pdfmetrics.stringWidth(text, FONT_B if bold else FONT, size_pt) * PT


# ---------------------------------------------------------------------------
# primitives
# ---------------------------------------------------------------------------

@dataclass
class Prim:
    kind: str                 # line | text | rect
    style: str = "cut"
    pts: np.ndarray | None = None
    closed: bool = False
    text: str = ""
    size: float = 9.0         # pt
    bold: bool = False
    angle: float = 0.0        # degrees (counter-clockwise, y up)
    fill: tuple | None = None
    ly: float = 0.0           # baseline offset perpendicular to the writing direction (mm)
    sheet: int = 0
    color: tuple | None = None   # overrides the style colour (nested sizes)
    dash: tuple | None = None    # overrides the style dash (nested sizes, cutting line)
    layer: int | None = None     # PDF optional content group (nested sizes)


def text_pos(p):
    """Baseline centre of a text in canvas coordinates (y down)."""
    a = math.radians(p.angle)
    return np.array([p.pts[0] - p.ly * math.sin(a), p.pts[1] - p.ly * math.cos(a)])


def _split_cut_ring(piece):
    """Split the cutting outline into 'cut' / 'fold' runs."""
    ring = piece.cut_ring()
    ring = np.vstack([ring, ring[:1]])
    folds = [LineString(e.pts) for e in piece.edges if e.fold]
    if not folds:
        return [("cut", ring)]
    flags = []
    for i in range(len(ring) - 1):
        mid = (ring[i] + ring[i + 1]) / 2
        from shapely.geometry import Point
        flags.append(any(f.distance(Point(mid)) < 0.6 for f in folds))
    runs, cur, curflag = [], [ring[0]], flags[0]
    for i, fl in enumerate(flags):
        if fl != curflag:
            runs.append(("fold" if curflag else "cut", np.array(cur)))
            cur, curflag = [ring[i]], fl
        cur.append(ring[i + 1])
    runs.append(("fold" if curflag else "cut", np.array(cur)))
    return runs


def _arrow_heads(p0, p1, size=6.0):
    d = G.unit(np.asarray(p1) - np.asarray(p0))
    n = np.array([-d[1], d[0]])
    heads = []
    for tip, dd in ((np.asarray(p1), d), (np.asarray(p0), -d)):
        heads.append(np.array([tip - dd * size + n * size * 0.45, tip, tip - dd * size - n * size * 0.45]))
    return heads


def _fit_text_block(poly, lines, sizes, bolds):
    """Find anchor point and angle for the label block (fits inside the piece)."""
    inner = poly.buffer(-4)
    if inner.is_empty:
        inner = poly
    anchor = polylabel(inner if inner.geom_type == "Polygon" else max(inner.geoms, key=lambda g: g.area), 1.0)
    for scale in (1.0, 0.85, 0.7, 0.6):
        w = max(text_w_mm(t, s * scale, b) for t, s, b in zip(lines, sizes, bolds))
        h = sum(s * scale * PT * 1.35 for s in sizes)
        for ang in (0.0, 90.0):
            ww, hh = (w, h) if ang == 0 else (h, w)
            for cand in [anchor] + [poly.centroid]:
                r = box(cand.x - ww / 2, cand.y - hh / 2, cand.x + ww / 2, cand.y + hh / 2)
                if poly.buffer(-2).contains(r):
                    return (cand.x, cand.y), ang, scale
    return (anchor.x, anchor.y), 0.0, 0.6


FOLD_TEXTS = ("PLACE ON FOLD", "ON FOLD", "FOLD")
FOLD_SIZES = (8.0, 7.0, 6.0, 5.0)
FOLD_MAX_SPAN = 110.0     # mm, bracket length along the fold edge
FOLD_TIP_GAP = 1.5        # mm between the arrow tips and the fold edge


def _free_interval(lo, hi, blocked, centre):
    """Longest part of [lo, hi] outside the `blocked` intervals; ties go to the one nearest `centre`."""
    free, x = [], lo
    for b0, b1 in sorted(blocked):
        if b0 > x:
            free.append((x, min(b0, hi)))
        x = max(x, b1)
        if x >= hi:
            break
    if x < hi:
        free.append((x, hi))
    free = [f for f in free if f[1] - f[0] > 0.5]
    if not free:
        return lo, hi
    return max(free, key=lambda f: (round(f[1] - f[0], 1), -abs((f[0] + f[1]) / 2 - centre)))


def fold_symbol(edge, obstacles=()):
    """Standard "place on fold" symbol for a (straight) fold edge: a bracket parallel to the
    edge whose two legs end in arrows pointing at the fold, labelled "PLACE ON FOLD".

    The bracket is sized to the edge (short doll waistbands get a short bracket, a shorter
    text and a smaller font) and keeps clear of inner lines and the grainline (`obstacles`),
    e.g. the fold line that crosses a waistband at half its height.
    Returns dict(prims, region, text, size, span): `region` is the area the symbol covers
    (the label block avoids it)."""
    a, b = np.asarray(edge.pts[0], float), np.asarray(edge.pts[-1], float)
    L_ = float(np.linalg.norm(b - a))
    t = G.unit(b - a)
    n_in = np.array([-t[1], t[0]])
    off = float(np.clip(0.25 * L_, 5.0, 10.0))      # bracket distance from the fold
    depth = off + max(FOLD_SIZES) * PT * 1.6 + 2.0   # strip that the symbol may occupy

    def at(s, d):
        return a + t * s + n_in * d

    strip = Polygon([at(0, 0), at(L_, 0), at(L_, depth), at(0, depth)])
    blocked = []
    for ob in obstacles:
        hit = strip.intersection(LineString(np.asarray(ob, float)))
        if hit.is_empty:
            continue
        ss = []
        for g in getattr(hit, "geoms", [hit]):
            ss += [float(np.dot(np.asarray(c) - a, t)) for c in g.coords]
        blocked.append((min(ss) - 2.0, max(ss) + 2.0))
    margin = min(3.0, 0.1 * L_)

    def pick(room):
        """First text/size that fits along `room` mm, or None."""
        for tx in map(tr, FOLD_TEXTS):
            for sz in FOLD_SIZES:
                if text_w_mm(tx, sz, True) <= room:
                    return tx, sz
        return None

    lo, hi = _free_interval(margin, L_ - margin, blocked, L_ / 2)
    choice = pick(hi - lo)
    if choice is None:                     # too little room next to the obstacles: use the whole edge
        lo, hi = margin, L_ - margin
        choice = pick(hi - lo) or (tr(FOLD_TEXTS[-1]), FOLD_SIZES[-1])
    text, size = choice
    span = min(0.8 * (hi - lo), FOLD_MAX_SPAN)
    w = max(span, text_w_mm(text, size, True))
    c = float(np.clip(L_ / 2, lo + w / 2, hi - w / 2)) if w <= hi - lo else (lo + hi) / 2
    s0, s1 = c - span / 2, c + span / 2
    head = min(2.5, span / 6)
    prims = [Prim("line", "fold_arrow", np.array([at(s0, FOLD_TIP_GAP), at(s0, off), at(s1, off),
                                                  at(s1, FOLD_TIP_GAP)]))]
    for s in (s0, s1):                                 # arrow heads pointing at the fold
        tip = at(s, FOLD_TIP_GAP)
        prims.append(Prim("line", "fold_arrow", np.array([tip + n_in * head * 1.6 + t * head * 0.6, tip,
                                                          tip + n_in * head * 1.6 - t * head * 0.6])))
    ang = math.degrees(math.atan2(t[1], t[0]))
    if ang > 90 or ang < -90:
        ang += 180
    th = size * PT
    prims.append(Prim("text", text=text, size=size, bold=True, pts=at(c, off + 1.0 + th * 0.5),
                      angle=ang, ly=-th * 0.35))
    half = w / 2 + 1.0
    region = Polygon([at(c - half, 0), at(c + half, 0), at(c + half, off + 2.0 + th * 1.3),
                      at(c - half, off + 2.0 + th * 1.3)])
    return dict(prims=prims, region=region, text=text, size=size, span=span)


def _without(poly, regions):
    """`poly` minus the areas in `regions` (largest remaining part); `poly` if too little is left."""
    if not regions:
        return poly
    from shapely.ops import unary_union
    rest = poly.difference(unary_union(regions))
    if rest.geom_type == "MultiPolygon":
        rest = max(rest.geoms, key=lambda g: g.area)
    if rest.is_empty or rest.geom_type != "Polygon" or rest.area < 0.4 * poly.area:
        return poly
    return rest


def piece_prims(piece, pattern, extra_label=None):
    prims = []
    for kind, pts in _split_cut_ring(piece):
        prims.append(Prim("line", kind, pts))
    for e in piece.edges:
        if not e.fold and e.sa > 0:     # without allowance the cutting line is the seam line
            prims.append(Prim("line", "seam", e.pts))
    # notches: projected onto the cutting line, also at corners (see notches.py)
    style = pattern.options.get("notch_style", "slit") if isinstance(pattern.options, dict) else "slit"
    for m in N.piece_marks(piece, style if style in N.SHAPES else "slit"):
        for ln in m.lines:
            prims.append(Prim("line", "notch", ln))
    # inner lines
    for mk in piece.marks:
        prims.append(Prim("line", "mark_fold" if mk.style == "fold" else "mark_placement", mk.pts))
        if mk.label:
            mid = G.point_at(mk.pts, G.length(mk.pts) / 2)
            t = G.tangent_at(mk.pts, G.length(mk.pts) / 2)
            ang = math.degrees(math.atan2(t[1], t[0]))
            if ang > 90 or ang < -90:
                ang += 180
            prims.append(Prim("text", text=tr(mk.label), size=7, pts=mid, angle=ang, ly=1.5))
    # grainline
    if piece.grain is not None:
        g0, g1 = np.asarray(piece.grain[0], float), np.asarray(piece.grain[1], float)
        prims.append(Prim("line", "grain", np.array([g0, g1])))
        for h in _arrow_heads(g0, g1):
            prims.append(Prim("line", "grain", h))
        d = G.unit(g1 - g0)
        ang = math.degrees(math.atan2(d[1], d[0]))
        if ang > 90 or ang < -90:
            ang += 180
        prims.append(Prim("text", text=tr("Grainline"), size=7, pts=(g0 + g1) / 2, angle=ang, ly=1.5))
    # "place on fold" bracket arrows (see fold_symbol)
    avoid = []
    obstacles = [mk.pts for mk in piece.marks] + ([np.array(piece.grain, float)] if piece.grain is not None else [])
    for e in piece.edges:
        if e.fold:
            sym = fold_symbol(e, obstacles)
            prims += sym["prims"]
            avoid.append(sym["region"])
    # label block
    lines = [tr(piece.name), f"{tr(pattern.title)} · {tr(pattern.size_label)}".strip(" ·"),
             piece.cut_text() + f" ({tr(piece.fabric)})"]
    if piece.on_fold:
        lines.append(tr("place this edge on the fold"))
    lines.append(piece.sa_text(U.of(pattern)))
    if piece.stretch_dir:
        lines.append(tr(piece.stretch_dir))
    for info in piece.info:
        lines.append(tr(info))
    if extra_label:
        lines.append(extra_label)
    sizes = [13.0] + [8.5] * (len(lines) - 1)
    bolds = [True] + [False] * (len(lines) - 1)
    poly = Polygon(piece.seam_ring())
    (ax, ay), tang, scale = _fit_text_block(_without(poly, avoid), lines, sizes, bolds)
    total_h = sum(s * scale * PT * 1.35 for s in sizes)
    y = total_h / 2
    for t, s, b in zip(lines, sizes, bolds):
        hh = s * scale * PT * 1.35
        y -= hh
        prims.append(Prim("text", "label", text=t, size=s * scale, bold=b, pts=np.array([ax, ay]),
                          angle=tang, ly=y + hh * 0.25))
    return prims


def transform_prims(prims, pl: L.Placement):
    out = []
    for p in prims:
        q = Prim(**p.__dict__)
        if p.kind == "line":
            q.pts = pl.apply(p.pts)
        elif p.kind == "text":
            q.pts = pl.apply(np.asarray(p.pts).reshape(1, 2))[0]
            a = (p.angle + pl.angle + 180) % 360 - 180
            if a > 100 or a < -100:      # never upside down: rotate the block by 180°
                a = a + 180 if a < 0 else a - 180   # keep ly: line order stays readable
            q.angle = a
        out.append(q)
    return out


SIZE_LINES = ("cut", "fold", "seam", "notch", "mark_fold", "mark_placement")


def nested_piece_prims(pattern, i):
    """Prims of piece i of a nested pattern: lines per size (own colour, dash, layer), label
    block and grainline once, inside the smallest size, and a size tag on each outline."""
    small = pattern.nest_label_pattern
    prims = [p for p in piece_prims(small.pieces[i], pattern) if p.kind == "text" or p.style in ("grain", "fold_arrow")]
    for n in pattern.nest:
        pc = n["pattern"].pieces[i]
        ring = pc.cut_ring()
        centre = (ring.min(axis=0) + ring.max(axis=0)) / 2
        direction = centre if np.linalg.norm(centre) > 1 else np.array([1.0, -1.0])
        for p in piece_prims(pc, n["pattern"]):
            if p.kind != "line" or p.style not in SIZE_LINES:
                continue
            p.color, p.layer = n["color"], n["layer"]
            if p.style == "cut":
                p.dash = n["dash"]
            prims.append(p)
        tag = NE.size_tag_points(ring, centre, direction)
        prims.append(Prim("text", "label", text=str(n["label"]), size=7, bold=True, pts=tag,
                          color=n["color"], layer=n["layer"]))
    return prims


def layout_prims(pattern, lay: L.Layout):
    prims = []
    if NE.is_nested(pattern):
        for pl in lay.placements:
            pp = transform_prims(nested_piece_prims(pattern, pl.index), pl)
            for p in pp:
                p.sheet = pl.sheet
            prims += pp
        return prims
    for pl in lay.placements:
        pc = pattern.pieces[pl.index]
        pp = transform_prims(piece_prims(pc, pattern), pl)
        for p in pp:
            p.sheet = pl.sheet
        prims += pp
    return prims


# ---------------------------------------------------------------------------
# Drawing: reportlab
# ---------------------------------------------------------------------------

class PdfPage:
    """Map canvas (mm, y down) → PDF page (pt, y up) through a window."""

    def __init__(self, c, page_w, page_h, window=None, offset=(0.0, 0.0), styles=None,
                 text_color=(0, 0, 0), size_colors=True):
        self.c, self.pw, self.ph = c, page_w, page_h
        self.window = window          # (x0, y0, x1, y1) canvas
        self.offset = offset          # position of the window on the page (mm, left/top)
        self.styles = styles or STYLES
        self.text_color = text_color
        self.size_colors = size_colors    # nested sizes: draw each size in its colour

    def to_pdf(self, x, y):
        wx, wy = (self.window[0], self.window[1]) if self.window else (0.0, 0.0)
        ox, oy = self.offset
        return (ox + x - wx) * MM, (self.ph - (oy + y - wy)) * MM

    def line(self, pts, style, closed=False, color=None, dash=None):
        st = self.styles[style]
        c = self.c
        c.setLineWidth(max(st["w"], MIN_LW))
        c.setStrokeColorRGB(*(color or st["color"]))
        dd = dash if dash is not None else st["dash"]
        c.setDash(list(dd) if dd else [])
        c.setLineJoin(1)
        c.setLineCap(0)
        path = c.beginPath()
        x, y = self.to_pdf(*pts[0])
        path.moveTo(x, y)
        for q in pts[1:]:
            path.lineTo(*self.to_pdf(*q))
        if closed:
            path.close()
        c.drawPath(path, stroke=1, fill=0)

    def text(self, x, y, s, size, bold=False, angle=0.0, center=True, color=(0, 0, 0)):
        c = self.c
        px, py = self.to_pdf(x, y)
        c.saveState()
        c.translate(px, py)
        c.rotate(angle)
        c.setFillColorRGB(*color)
        c.setFont(FONT_B if bold else FONT, size)
        if center:
            c.drawCentredString(0, 0, s)
        else:
            c.drawString(0, 0, s)
        c.restoreState()

    def prim(self, p):
        if p.layer is not None:
            self.c._code.append(f"/OC /oc{p.layer} BDC")
        if p.kind == "line":
            col = p.color if self.size_colors else None
            self.line(p.pts, p.style, p.closed, color=col, dash=p.dash)
        elif p.kind == "text":
            x, y = text_pos(p)
            col = p.color if (p.color and self.size_colors) else self.text_color
            self.text(x, y, p.text, p.size, p.bold, p.angle, color=col)
        if p.layer is not None:
            self.c._code.append("EMC")


def control_squares_pdf(c, x_mm, y_top_mm, page_h_mm):
    """5 × 5 cm and 1 × 1 inch, top-left corner at (x_mm, y_top_mm) measured from the top.
    Returns the area used (width, height) in mm."""
    c.setDash([])
    c.setStrokeColor(black)
    c.setLineWidth(0.75)
    side = 50.0 * MM            # 141,7323 pt
    x = x_mm * MM
    y = (page_h_mm - y_top_mm - 50.0) * MM
    c.rect(x, y, side, side, stroke=1, fill=0)
    c.setFont(FONT_B, 9)
    c.drawCentredString(x + side / 2, y + side / 2 + 4, "5 × 5 cm")
    c.setFont(FONT, 6.5)
    c.drawCentredString(x + side / 2, y + side / 2 - 6, "control square")
    c.drawCentredString(x + side / 2, y + side / 2 - 14, "measure it!")
    inch = 72.0
    xi = x + side + 5 * MM
    yi = y + side - inch
    c.rect(xi, yi, inch, inch, stroke=1, fill=0)
    c.setFont(FONT, 7)
    c.drawCentredString(xi + inch / 2, yi + inch / 2 - 2, tr("1 inch"))
    return 50.0 + 5.0 + 25.4, 50.0


def legend_pdf(c, x_mm, y_top_mm, page_h_mm, with_allowance=True):
    if with_allowance:
        first = [("cut", "Cutting line (seam allowance included)"), ("seam", "Seam line")]
    else:
        first = [("cut", "Seam line = outline: NO seam allowance included"),
                 ("cut", "Add the allowances listed on each piece when cutting")]
    items = first + [("fold", "Fold"), ("mark_fold", "Fold-over / pressing line")]
    page = PdfPage(c, 0, page_h_mm)
    for k, (st, label) in enumerate(items):
        y = y_top_mm + 4 + k * 6
        page.line(np.array([[x_mm, y], [x_mm + 18, y]]), st)
        page.text(x_mm + 21, y + 1.2, tr(label), 7.5, center=False)
    page.line(np.array([[x_mm, y_top_mm + 28], [x_mm + 18, y_top_mm + 28]]), "grain")
    for h in _arrow_heads(np.array([x_mm, y_top_mm + 28]), np.array([x_mm + 18, y_top_mm + 28]), 3):
        page.line(h, "grain")
    page.text(x_mm + 21, y_top_mm + 29.2, tr("Grainline (parallel to the selvage)"), 7.5, center=False)
    page.line(np.array([[x_mm + 9, y_top_mm + 31], [x_mm + 9, y_top_mm + 37]]), "notch")
    page.text(x_mm + 21, y_top_mm + 35.2, tr("Notches (single = front, double = back)"), 7.5, center=False)


def size_legend_pdf(c, pattern, x_mm, y_top_mm, page_h_mm):
    """Nested sizes: line sample + size per layer (each in its own layer)."""
    page = PdfPage(c, 0, page_h_mm)
    page.text(x_mm, y_top_mm + 4, tr("Sizes (PDF layers: switch sizes on/off before printing)"), 7.5, True,
              center=False)
    for k, n in enumerate(pattern.nest):
        y = y_top_mm + 10 + k * 5.5
        c._code.append(f"/OC /oc{n['layer']} BDC")
        page.line(np.array([[x_mm, y], [x_mm + 18, y]]), "cut", color=n["color"], dash=n["dash"])
        page.text(x_mm + 21, y + 1.2, tr(f"Size {n['label']}"), 7.5, center=False, color=n["color"])
        c._code.append("EMC")


def header_pdf(c, pattern, page_w_mm, page_h_mm, subtitle, top=6.0, left=8.0, compact=False):
    page = PdfPage(c, page_w_mm, page_h_mm)
    page.text(left, top + 7, f"{tr(pattern.title)} · {tr(pattern.size_label)}", 16, True, center=False)
    page.text(left, top + 13.5, tr(subtitle), 8.5, center=False)
    page.text(left, top + 19, tr("Print at 100 % / \"Actual size\". Do NOT use \"Fit to page\"."),
              8, center=False)
    page.text(left, top + 23.5, tr("Measure the control square before cutting."), 8, center=False)
    page.text(left, top + 28, tr("Original parametric draft. "
              "Sew a test garment the first time you use this pattern."), 7.5, center=False)
    if compact:
        control_squares_pdf(c, left, top + 33, page_h_mm)
    else:
        legend_pdf(c, left, top + 31, page_h_mm, A.has_allowance(pattern))
        control_squares_pdf(c, page_w_mm - 80.4 - 8, top + 4, page_h_mm)
    if NE.is_nested(pattern):
        size_legend_pdf(c, pattern, left + (90 if compact else 100), top + (33 if compact else 31), page_h_mm)


def _setup_canvas(path, w_mm, h_mm, title):
    register_fonts()
    c = rl_canvas.Canvas(path, pagesize=(w_mm * MM, h_mm * MM), pageCompression=1)
    c.setTitle(title)
    c.setAuthor("sewing-pattern-generator")
    c.setCreator("sewing-pattern-generator (reportlab)")
    return c


def render_roll_pdf(pattern, lay: L.Layout, path):
    c = _setup_canvas(path, lay.page_w, lay.page_h, f"{tr(pattern.title)} {tr(pattern.size_label)}")
    header_pdf(c, pattern, lay.page_w, lay.page_h,
               f"Roll {lay.meta['roll']:.0f} mm · page size {lay.page_w:.0f} × {lay.page_h:.0f} mm "
               f"(portrait) · {len(pattern.pieces)} pattern pieces")
    page = PdfPage(c, lay.page_w, lay.page_h)
    for p in layout_prims(pattern, lay):
        page.prim(p)
    c.showPage()
    c.save()
    NE.add_pdf_layers(path, pattern)
    return path


def render_sheets_pdf(pattern, lay: L.Layout, path, tiled: L.Layout | None = None):
    c = _setup_canvas(path, lay.page_w, lay.page_h, f"{pattern.title} {pattern.size_label}")
    prims = layout_prims(pattern, lay)
    n_tiled = sum(not t["empty"] for t in tiled.tiles) if tiled else 0
    total = lay.sheets + n_tiled
    for s in range(lay.sheets):
        header_pdf(c, pattern, lay.page_w, lay.page_h,
                   f"{lay.meta['paper']} sheet {s + 1} of {total} · {lay.page_w:.0f} × {lay.page_h:.0f} mm")
        page = PdfPage(c, lay.page_w, lay.page_h)
        for p in prims:
            if p.sheet == s:
                page.prim(p)
        c.showPage()
    if tiled:
        _render_tiles(c, pattern, tiled, start_no=lay.sheets + 1, total=total, overview=False)
    c.save()
    NE.add_pdf_layers(path, pattern)
    return path


# ---------------------------------------------------------------------------
# Projector (one page 1:1, thick high-contrast lines, calibration grid)
# ---------------------------------------------------------------------------

PROJECTOR_GRID = 100.0      # calibration grid in mm
PROJECTOR_MIN_LW = 1.0      # pt


def projector_styles(dark: bool) -> dict:
    """Line styles for projecting: everything ≥ 1 pt, cutting line 2 pt; bright on dark."""
    out = {}
    for k, st in STYLES.items():
        w = max(PROJECTOR_MIN_LW, st["w"] * 1.5)
        if k == "cut":
            w = 2.0
        col = st["color"]
        if dark:
            col = {"cut": (1, 1, 1), "fold": (1, 1, 1), "seam": (1.0, 0.85, 0.2),
                   "notch": (1, 1, 1), "grain": (0.4, 0.9, 1.0),
                   "fold_arrow": (1, 1, 1)}.get(k, (0.8, 0.8, 0.8))
        out[k] = dict(w=w, dash=st["dash"], color=col)
    return out


def render_projector_pdf(pattern, lay: L.Layout, path, dark: bool = False):
    """Single page at 1:1 for projector sewing: whole layout, 10 cm calibration grid across
    the page, control squares, thick lines; `dark` = black background with bright lines."""
    W, H = lay.page_w, lay.page_h
    c = _setup_canvas(path, W, H, f"{pattern.title} {pattern.size_label} · projector")
    fg = (1, 1, 1) if dark else (0, 0, 0)
    if dark:
        c.setFillColorRGB(0, 0, 0)
        c.rect(0, 0, W * MM, H * MM, stroke=0, fill=1)
    # calibration grid: one 10 × 10 cm square per cell (exactly 283.46 pt)
    c.setDash([])
    c.setLineWidth(PROJECTOR_MIN_LW)
    c.setStrokeColorRGB(*((0.3, 0.3, 0.3) if dark else (0.78, 0.82, 0.9)))
    g = PROJECTOR_GRID
    nx, ny = int(W // g), int(H // g)
    for i in range(nx):
        for j in range(ny):
            c.rect(i * g * MM, (H - (j + 1) * g) * MM, g * MM, g * MM, stroke=1, fill=0)
    page = PdfPage(c, W, H, styles=projector_styles(dark), text_color=fg, size_colors=not dark)
    gc = (0.55, 0.55, 0.55) if dark else (0.45, 0.5, 0.65)
    for i in range(1, nx + 1):
        page.text(i * g - 2, 4, f"{i * 10} cm", 7, color=gc, center=False, angle=0)
    for j in range(1, ny + 1):
        page.text(2, j * g - 2, f"{j * 10} cm", 7, color=gc, center=False)
    # header
    page.text(8, 14, f"{tr(pattern.title)} · {tr(pattern.size_label)}", 18, True, center=False, color=fg)
    page.text(8, 22, tr(f"Projector file · 1:1 · {W:.0f} × {H:.0f} mm · grid {g / 10:.0f} cm · "
              "calibrate until the grid squares and the control square measure exactly."), 9,
              center=False, color=fg)
    page.text(8, 28, tr("Grainline arrows are parallel to the long page edge (lay the selvage along it)."),
              9, center=False, color=fg)
    if dark:
        c.setStrokeColorRGB(1, 1, 1)
        c.setFillColorRGB(1, 1, 1)
    sx = W - 88.4
    c.setLineWidth(PROJECTOR_MIN_LW)
    c.setStrokeColorRGB(*fg)
    c.setFillColorRGB(*fg)
    c.rect(sx * MM, (H - 10 - 50) * MM, 50 * MM, 50 * MM, stroke=1, fill=0)
    c.setFont(FONT_B, 10)
    c.drawCentredString((sx + 25) * MM, (H - 36) * MM, "5 × 5 cm")
    c.rect((sx + 55) * MM, (H - 10) * MM - 72.0, 72.0, 72.0, stroke=1, fill=0)
    c.setFont(FONT, 7)
    c.drawCentredString((sx + 55 + 12.7) * MM, (H - 10 - 12.7) * MM - 2, tr("1 inch"))
    for p in layout_prims(pattern, lay):
        page.prim(p)
    if NE.is_nested(pattern):
        size_legend_pdf(c, pattern, 8, 32, H)
    c.showPage()
    c.save()
    NE.add_pdf_layers(path, pattern)
    return path


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------

def _ink_raster(prims, cw, ch, res=1.0):
    """Occupancy raster (1 mm) of all lines and texts, to find free spots for the control squares."""
    from PIL import Image, ImageDraw
    img = Image.new("1", (int(cw / res) + 2, int(ch / res) + 2), 0)
    d = ImageDraw.Draw(img)
    for p in prims:
        if p.kind == "line":
            d.line([(x / res, y / res) for x, y in p.pts], fill=1, width=int(4 / res))
        elif p.kind == "text":
            w = text_w_mm(p.text, p.size, p.bold) + 4
            h = p.size * PT * 1.6 + 2
            a = math.radians(-p.angle)
            cx, cy = text_pos(p)
            corners = [(-w / 2, -h), (w / 2, -h), (w / 2, h * 0.3), (-w / 2, h * 0.3)]
            pts = [((cx + x * math.cos(a) - y * math.sin(a)) / res,
                    (cy + x * math.sin(a) + y * math.cos(a)) / res) for x, y in corners]
            d.polygon(pts, fill=1)
    return np.array(img, dtype=np.int32)


def _find_free(ink, window, size_w, size_h, exclude=10.0, res=1.0, least_ink=False):
    """Top-left corner of a free window × size spot, or None. least_ink: the spot that
    covers the fewest lines/texts instead of None."""
    x0, y0, x1, y1 = window
    xa, ya = int((x0 + exclude) / res), int((y0 + exclude) / res)
    xb, yb = int((x1 - exclude) / res), int((y1 - exclude) / res)
    sub = ink[max(ya, 0):yb, max(xa, 0):xb]
    if sub.size == 0:
        return None
    pad = np.zeros((sub.shape[0] + 1, sub.shape[1] + 1), dtype=np.int64)
    pad[1:, 1:] = np.cumsum(np.cumsum(sub, 0), 1)
    hh, ww = int(size_h / res), int(size_w / res)
    if hh >= pad.shape[0] or ww >= pad.shape[1]:
        return None
    s = pad[hh:, ww:] - pad[:-hh, ww:] - pad[hh:, :-ww] + pad[:-hh, :-ww]
    free = np.argwhere(s == 0)
    if len(free) == 0:
        if not least_ink:
            return None
        r, cc = np.unravel_index(int(np.argmin(s)), s.shape)
        return (xa + cc) * res, (ya + r) * res
    # prefer the bottom left (away from the page header)
    r, cc = free[np.argmax(free[:, 0] * 10 - free[:, 1])]
    return (xa + cc) * res, (ya + r) * res


def _tile_decorations(lay: L.Layout):
    """Glue areas, alignment lines, diamonds, in canvas coordinates (identical on both pages)."""
    pw, ph = lay.meta["pw"], lay.meta["ph"]
    sx, sy = pw - L.OVERLAP, ph - L.OVERLAP
    nrows, ncols = lay.grid
    deco = []
    W, H = (ncols - 1) * sx + pw, (nrows - 1) * sy + ph
    for c_ in range(1, ncols):
        x = c_ * sx
        deco.append(("glue", (x, 0, x + L.OVERLAP, H)))
        deco.append(("line", np.array([[x, 0], [x, H]])))
        for r in range(nrows):
            cy = r * sy + ph / 2
            deco.append(("diamond", (x + L.OVERLAP / 2, cy)))
            deco.append(("dtext", (x + L.OVERLAP / 2, cy + 9), f"{chr(65 + r)}{c_}|{chr(65 + r)}{c_ + 1}", 90))
    for r in range(1, nrows):
        y = r * sy
        deco.append(("glue", (0, y, W, y + L.OVERLAP)))
        deco.append(("line", np.array([[0, y], [W, y]])))
        for c_ in range(ncols):
            cx = c_ * sx + pw / 2
            deco.append(("diamond", (cx, y + L.OVERLAP / 2)))
            deco.append(("dtext", (cx + 9, y + L.OVERLAP / 2 + 1.2), f"{chr(64 + r)}{c_ + 1}/{chr(65 + r)}{c_ + 1}", 0))
    return deco


def _draw_deco(page: PdfPage, deco, behind: bool):
    c = page.c
    for d in deco:
        if d[0] == "glue" and behind:
            x0, y0, x1, y1 = d[1]
            px0, py0 = page.to_pdf(x0, y1)
            px1, py1 = page.to_pdf(x1, y0)
            c.setFillColor(Color(0.88, 0.88, 0.88))
            c.rect(px0, py0, px1 - px0, py1 - py0, stroke=0, fill=1)
        elif d[0] == "line" and not behind:
            page.line(d[1], "tile")
        elif d[0] == "diamond" and not behind:
            cx, cy = d[1]
            r = 4.0
            page.line(np.array([[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy], [cx, cy - r]]), "diamond")
            page.line(np.array([[cx - r, cy], [cx + r, cy]]), "diamond")
            page.line(np.array([[cx, cy - r], [cx, cy + r]]), "diamond")
        elif d[0] == "dtext" and not behind:
            (x, y), s, ang = d[1], d[2], d[3]
            page.text(x, y, s, 6, angle=ang, color=(0.3, 0.3, 0.3))


def _render_overview(c, pattern, lay, pages, page_w, page_h):
    header_pdf(c, pattern, page_w, page_h,
               f"Overview · {lay.meta['paper']} tiles · {len(pages)} pages to print + this overview",
               compact=True)
    pg = PdfPage(c, page_w, page_h)
    lines = [
        "How to assemble:",
        "1. Print all pages at 100 %. Measure the control square (5 × 5 cm).",
        "2. On every page, trim the left and top margin along the dashed line.",
        "3. Lay the pages onto the grey glue areas of their neighbours as in the plan below:",
        "   diamonds and lines must match exactly. Then glue them down.",
        "4. Cut the pieces out along the solid cutting line (seam allowance is included).",
    ]
    for k, ln in enumerate(lines):
        pg.text(10, 95 + k * 5, tr(ln), 8 if k else 9, bold=(k == 0), center=False)
    # plan
    top = 128.0
    avail_w, avail_h = page_w - 20, page_h - top - 15
    s = min(avail_w / lay.canvas_w, avail_h / max(lay.canvas_h, 1))
    ox, oy = 10.0 + (avail_w - lay.canvas_w * s) / 2, top

    def tp(pts):
        return np.stack([ox + pts[:, 0] * s, oy + pts[:, 1] * s], axis=1)

    for t in lay.tiles:
        x0, y0, x1, y1 = t["window"]
        rect = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]])
        if t["empty"]:
            pg.line(tp(rect), "tile")
            pg.text(ox + (x0 + x1) / 2 * s, oy + (y0 + y1) / 2 * s, tr("empty"), 6, color=(0.5, 0.5, 0.5))
        else:
            pg.line(tp(rect), "diamond")
            pg.text(ox + (x0 + x1) / 2 * s, oy + (y0 + y1) / 2 * s + 2,
                    tr(f"{t['label']} (p. {t['page_no']})"), 7, True, color=(0.35, 0.35, 0.65))
    for pl in lay.placements:
        ring = L.placed_ring(pattern.pieces[pl.index].cut_ring(), pl)
        pg.line(tp(np.vstack([ring, ring[:1]])), "cut")
        cxy = Polygon(ring).representative_point()
        pg.text(ox + cxy.x * s, oy + cxy.y * s, tr(pattern.pieces[pl.index].name).split(" (")[0], 6.5, True)


def _render_tiles(c, pattern, lay: L.Layout, start_no=1, total=None, overview=True):
    page_w, page_h, margin = lay.page_w, lay.page_h, lay.meta["margin"]
    pages = [t for t in lay.tiles if not t["empty"]]
    for k, t in enumerate(pages):
        t["page_no"] = start_no + k + (1 if overview else 0)
    total = total or (len(pages) + (1 if overview else 0))
    prims = layout_prims(pattern, lay)
    deco = _tile_decorations(lay)
    ink = _ink_raster(prims, lay.canvas_w + lay.meta["pw"], lay.canvas_h + lay.meta["ph"])
    if overview:
        c.setPageSize((page_w * MM, page_h * MM))
        _render_overview(c, pattern, lay, pages, page_w, page_h)
        c.showPage()
    warnings = []
    for t in pages:
        c.setPageSize((page_w * MM, page_h * MM))
        win = t["window"]
        page = PdfPage(c, page_w, page_h, window=win, offset=(margin, margin))
        wb = box(*win)
        c.saveState()
        x0, y0 = page.to_pdf(win[0], win[3])
        x1, y1 = page.to_pdf(win[2], win[1])
        clip = c.beginPath()
        clip.rect(x0, y0, x1 - x0, y1 - y0)
        c.clipPath(clip, stroke=0, fill=0)
        # large page label in the background
        cx, cy = (win[0] + win[2]) / 2, (win[1] + win[3]) / 2
        page.text(cx, cy + 15, t["label"], 90, True, color=(0.9, 0.9, 0.93))
        _draw_deco(page, deco, behind=True)
        for p in prims:
            if p.kind == "line":
                bb = G.bbox(p.pts)
                if not wb.intersects(box(bb[0] - 1, bb[1] - 1, bb[2] + 1, bb[3] + 1)):
                    continue
            elif p.kind == "text":
                tx, ty = text_pos(p)
                if not wb.buffer(80).contains(box(tx - 1, ty - 1, tx + 1, ty + 1)):
                    continue
            page.prim(p)
        _draw_deco(page, deco, behind=False)
        c.restoreState()
        # frame (trim edge) and page caption
        frame = np.array([[win[0], win[1]], [win[2], win[1]], [win[2], win[3]], [win[0], win[3]], [win[0], win[1]]])
        page.line(frame, "tile")
        r, col = t["row"], t["col"]
        nb = []
        if col > 0:
            nb.append(tr("left") + f": {chr(65 + r)}{col}")
        if r > 0:
            nb.append(tr("top") + f": {chr(64 + r)}{col + 1}")
        info = (tr(f"Page {t['page_no']}/{total}") + f" · {t['label']} · {tr(pattern.title)} "
                f"{tr(pattern.size_label)}")
        if nb:
            info += " · " + tr("glue to") + " " + ", ".join(nb)
        page.text(win[0] + (L.OVERLAP if col > 0 else 0) + 2, win[1] + (L.OVERLAP if r > 0 else 0) + 4,
                  info, 6.5, center=False, color=(0.25, 0.25, 0.25))
        # control squares in a free spot
        spot = _find_free(ink, win, 84, 56)
        if spot is None:
            # crowded page (small pieces, e.g. doll clothes): also try close to the page edge
            spot = _find_free(ink, win, 56, 56) or _find_free(ink, win, 56, 56, exclude=3.0)
            if spot is None:
                # no free spot: draw the square where it crosses the fewest lines (never hide
                # pattern lines under a white box)
                warnings.append(t["label"])
                spot = _find_free(ink, win, 56, 56, exclude=3.0, least_ink=True) or \
                    (win[0] + L.OVERLAP + 5, win[3] - 70)
                control_squares_pdf_single(c, spot[0] + margin - win[0] + 1, spot[1] + margin - win[1] + 2, page_h)
            else:
                control_squares_pdf_single(c, spot[0] + margin - win[0] + 1, spot[1] + margin - win[1] + 2, page_h)
        else:
            control_squares_pdf(c, spot[0] + margin - win[0] + 1, spot[1] + margin - win[1] + 2, page_h)
        c.showPage()
    lay.meta["square_fallback_pages"] = warnings
    return warnings


def control_squares_pdf_single(c, x_mm, y_top_mm, page_h_mm):
    c.setDash([])
    c.setLineWidth(0.75)
    c.setStrokeColor(black)
    side = 50.0 * MM
    x, y = x_mm * MM, (page_h_mm - y_top_mm - 50.0) * MM
    c.rect(x, y, side, side, stroke=1, fill=0)
    c.setFont(FONT_B, 9)
    c.setFillColor(black)
    c.drawCentredString(x + side / 2, y + side / 2, "5 × 5 cm")
    inch = 72.0
    c.rect(x + 2 * MM, y + 2 * MM, inch, inch, stroke=1, fill=0)
    c.setFont(FONT, 6)
    c.drawCentredString(x + 2 * MM + inch / 2, y + 2 * MM + inch / 2, tr("1 inch"))


def render_tiles_pdf(pattern, lay: L.Layout, path):
    c = _setup_canvas(path, lay.page_w, lay.page_h, f"{pattern.title} {pattern.size_label}")
    warnings = _render_tiles(c, pattern, lay, overview=True)
    c.save()
    NE.add_pdf_layers(path, pattern)
    return path, warnings


# ---------------------------------------------------------------------------
# SVG master
# ---------------------------------------------------------------------------

def _svg_dash(style):
    d = STYLES[style]["dash"]
    return "" if not d else f' stroke-dasharray="{" ".join(f"{v * PT:.2f}" for v in d)}"'


def render_svg(pattern, lay: L.Layout, path, header_h=None):
    """SVG at 1:1 (units mm). Tile/sheet layouts get an extra header area."""
    if lay.kind == "roll":
        W, H, oy, sheets = lay.page_w, lay.page_h, 0.0, [0]
    elif lay.kind == "sheets":
        W, H, oy, sheets = lay.page_w, lay.page_h, 0.0, list(range(lay.sheets))
    else:
        W, H, oy, sheets = lay.canvas_w, lay.canvas_h + 85.0, 85.0, [0]
    prims = layout_prims(pattern, lay)
    total_h = H * len(sheets) + 20 * (len(sheets) - 1)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" '
           'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
           f'width="{W:.2f}mm" height="{total_h:.2f}mm" '
           f'viewBox="0 0 {W:.2f} {total_h:.2f}">',
           f"<title>{escape(tr(pattern.title))} {escape(tr(pattern.size_label))} · "
           f"{escape(tr('scale 1:1 (unit mm)'))}</title>",
           '<style>text{font-family:"DejaVu Sans",Arial,sans-serif}</style>']
    for si, s in enumerate(sheets):
        base = si * (H + 20)
        out.append(f'<g transform="translate(0 {base:.2f})">')
        out.append(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="white" stroke="#bbb" stroke-width="0.3"/>')
        out.append(f'<text x="8" y="13" font-size="5.6" font-weight="bold">{escape(tr(pattern.title))} · '
                   f'{escape(tr(pattern.size_label))}</text>')
        out.append('<text x="8" y="19.5" font-size="3">'
                   + escape(tr("Print at 100 % / actual size. Measure the 5 × 5 cm control square.")) + '</text>')
        sx = W - 88.4
        out.append(f'<rect x="{sx:.2f}" y="10" width="50" height="50" fill="none" stroke="black" stroke-width="0.26"/>')
        out.append(f'<text x="{sx + 25:.2f}" y="36" font-size="3.2" text-anchor="middle" font-weight="bold">5 × 5 cm</text>')
        out.append(f'<rect x="{sx + 55:.2f}" y="10" width="25.4" height="25.4" fill="none" stroke="black" stroke-width="0.26"/>')
        out.append(f'<text x="{sx + 67.7:.2f}" y="23.5" font-size="2.5" text-anchor="middle">' + escape(tr('1 inch')) + '</text>')
        out.append(f'<g transform="translate(0 {oy:.2f})">')
        groups: list = [None] + ([n["layer"] for n in pattern.nest] if NE.is_nested(pattern) else [])
        for grp in groups:
            if grp is not None:
                n = pattern.nest[grp]
                gid = "size_" + "".join(ch if ch.isalnum() else "_" for ch in str(n["label"]))
                out.append(f'<g id="{gid}" class="size-layer" inkscape:groupmode="layer" '
                           f'inkscape:label="{escape(tr("Size " + str(n["label"])))}">')
            for p in prims:
                if p.sheet != s or p.layer != grp:
                    continue
                if p.kind == "line":
                    st = STYLES[p.style]
                    d = " ".join(f"{x:.2f},{y:.2f}" for x, y in p.pts)
                    col = "#" + "".join(f"{int(v * 255):02x}" for v in (p.color or st["color"]))
                    dash = (_svg_dash(p.style) if p.dash is None else
                            f' stroke-dasharray="{" ".join(f"{v * PT:.2f}" for v in p.dash)}"')
                    out.append(f'<polyline points="{d}" fill="none" stroke="{col}" '
                               f'stroke-width="{st["w"] * PT:.3f}"{dash} stroke-linejoin="round"/>')
                elif p.kind == "text":
                    fs = p.size * PT
                    tx, ty = text_pos(p)
                    bold = ' font-weight="bold"' if p.bold else ""
                    fill = ("" if not p.color else
                            ' fill="#' + "".join(f"{int(v * 255):02x}" for v in p.color) + '"')
                    out.append(f'<text x="{tx:.2f}" y="{ty:.2f}" font-size="{fs:.2f}" '
                               f'text-anchor="middle"{bold}{fill} '
                               f'transform="rotate({-p.angle:.2f} {tx:.2f} {ty:.2f})">{escape(p.text)}</text>')
            if grp is not None:
                out.append("</g>")
        out.append("</g></g>")
    out.append("</svg>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return path


# ---------------------------------------------------------------------------
# PNG preview
# ---------------------------------------------------------------------------

def render_png(pattern, lay: L.Layout, path, dpi_mm: float = 0.6, show_tiles=True, title=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if lay.kind == "sheets":
        sheets = list(range(lay.sheets))
        W, H = lay.page_w, lay.page_h
    else:
        sheets = [0]
        W, H = (lay.canvas_w, lay.canvas_h) if lay.kind == "tiles" else (lay.page_w, lay.page_h)
    fig_w = W * len(sheets) / 25.4 * dpi_mm / 2 + 0.5 * len(sheets)
    fig_h = H / 25.4 * dpi_mm / 2 + 0.6
    scale_fig = min(1.0, 22 / max(fig_w, fig_h))
    fig, axs = plt.subplots(1, len(sheets), figsize=(max(4, fig_w * scale_fig), max(4, fig_h * scale_fig)), squeeze=False)
    prims = layout_prims(pattern, lay)
    palette = ["#e8f1fb", "#fdf0e3", "#eaf7ea", "#f6e9f7", "#fff8dc", "#e9f6f6", "#f7ecec", "#eef0f9"]
    for si, s in enumerate(sheets):
        ax = axs[0][si]
        ax.add_patch(plt.Rectangle((0, 0), W, H, fill=False, ec="#999", lw=0.8))
        for pl in [p for p in lay.placements if p.sheet == s]:
            ring = L.placed_ring(pattern.pieces[pl.index].cut_ring(), pl)
            ax.fill(ring[:, 0], ring[:, 1], color=palette[pl.index % len(palette)], zorder=0)
        for p in prims:
            if p.sheet != s:
                continue
            if p.kind == "line":
                st = STYLES[p.style]
                ls = "-" if not st["dash"] else (0, tuple(v * 0.6 for v in st["dash"]))
                if p.dash:
                    ls = (0, tuple(v * 0.6 for v in p.dash))
                ax.plot(p.pts[:, 0], p.pts[:, 1], color=p.color or st["color"], lw=st["w"] * 0.6, ls=ls)
            elif p.kind == "text" and (p.size >= 8 or p.color):
                tx, ty = text_pos(p)
                ax.text(tx, ty, p.text, fontsize=max(3.5, p.size * 0.42), rotation=p.angle,
                        ha="center", va="bottom", rotation_mode="anchor",
                        fontweight="bold" if p.bold else "normal")
        if lay.kind == "tiles" and show_tiles:
            for t in lay.tiles:
                x0, y0, x1, y1 = t["window"]
                ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False,
                                           ec="#c33" if not t["empty"] else "#ccc", lw=0.5, ls="--"))
                ax.text((x0 + x1) / 2, (y0 + y1) / 2, t["label"], color="#c33" if not t["empty"] else "#bbb",
                        fontsize=7, ha="center", va="center", alpha=0.6)
        if lay.kind == "roll":
            ax.add_patch(plt.Rectangle((W - 88.4, 10), 50, 50, fill=False, ec="k", lw=0.6))
            ax.text(8, 14, f"{tr(pattern.title)} · {tr(pattern.size_label)}", fontsize=8, fontweight="bold")
        ax.set_xlim(-5, W + 5)
        ax.set_ylim(H + 5, -5)
        ax.set_aspect("equal")
        ax.axis("off")
        if lay.kind == "sheets":
            ax.set_title(tr(f"{lay.meta['paper']} sheet {s + 1}"), fontsize=8)
    fig.suptitle(title or f"{tr(pattern.title)} {tr(pattern.size_label)} · " + tr(f"preview ({lay.kind})"),
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path
