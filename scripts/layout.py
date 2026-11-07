"""Arranging pattern pieces on a roll, single sheets (A0/A1) and tiled pages (A4/Letter).

Layout ("canvas") coordinates: mm, x to the right, y **down** (top of page = 0).
A piece is rotated by `angle` (degrees, counter-clockwise in piece coordinates) and then
moved: canvas = (xr + dx, −yr + dy). The grainline rotates with the piece.

Packing: raster-based bottom-left fill with FFT correlation for collision checks.
Distance between pieces ≥ `gap` mm.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw
from scipy.signal import fftconvolve
from shapely.geometry import Polygon, box

import ease as E
import geometry as G

PAPER = {  # width × height in mm (portrait)
    "A4": (210.0, 297.0), "LETTER": (215.9, 279.4), "A1": (594.0, 841.0), "A0": (841.0, 1189.0),
}
TILE_MARGIN = 8.0       # printer margin A4/Letter (≥ 8 mm)
SHEET_MARGIN = 10.0     # margin on A0/A1
ROLL_MARGIN = 5.0       # side margin on the roll
OVERLAP = 10.0          # glue overlap
GAP = 10.0              # minimum distance between pieces
ROLL_HEADER = 80.0      # header area on the roll (title, legend, control squares)


@dataclass
class Placement:
    index: int          # index into pattern.pieces
    angle: float
    dx: float
    dy: float
    sheet: int = 0
    copy: int = 0       # for the cutting layout (which copy)
    mirrored: bool = False
    layers: int = 1     # cutting layout: copies cut at once (2 = through both layers of folded fabric)
    pinned: bool = False  # cutting layout: placed against the fabric fold

    def apply(self, pts):
        p = G.as_pts(pts)
        if self.mirrored:
            p = G.mirror_x(p, 0.0)
        r = G.rotate(p, self.angle)
        return np.stack([r[:, 0] + self.dx, -r[:, 1] + self.dy], axis=1)


@dataclass
class Layout:
    kind: str                       # roll | sheets | tiles
    page_w: float
    page_h: float
    placements: list[Placement]
    canvas_w: float = 0.0
    canvas_h: float = 0.0
    sheets: int = 1
    tiles: list = field(default_factory=list)   # tiles: dict(row, col, label, window)
    grid: tuple = (0, 0)
    reserved: list = field(default_factory=list)  # reserved rectangles (x0, y0, x1, y1)
    meta: dict = field(default_factory=dict)


def _rings(piece):
    return piece.cut_ring()


def _raster(pts, res, pad):
    """Polygon (canvas coordinates) → boolean mask, origin = bbox minimum."""
    poly = Polygon(pts).buffer(pad, join_style=2)
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    x0, y0, x1, y1 = poly.bounds
    w = int(math.ceil((x1 - x0) / res)) + 2
    h = int(math.ceil((y1 - y0) / res)) + 2
    img = Image.new("1", (w, h), 0)
    ext = [((x - x0) / res + 0.5, (y - y0) / res + 0.5) for x, y in poly.exterior.coords]
    ImageDraw.Draw(img).polygon(ext, fill=1, outline=1)
    m = np.array(img, dtype=np.float32)
    # conservative: dilate by 1 pixel
    m2 = m.copy()
    m2[1:, :] = np.maximum(m2[1:, :], m[:-1, :])
    m2[:-1, :] = np.maximum(m2[:-1, :], m[1:, :])
    m2[:, 1:] = np.maximum(m2[:, 1:], m2[:, :-1].copy())
    m2[:, :-1] = np.maximum(m2[:, :-1], m2[:, 1:].copy())
    return m2, x0 + pad * 0, y0, poly.bounds


def _oriented(ring, angle, mirrored=False):
    p = G.mirror_x(ring, 0.0) if mirrored else ring
    r = G.rotate(p, angle)
    return np.stack([r[:, 0], -r[:, 1]], axis=1)


def pack(rings, width, height=None, angles=None, gap=GAP, res=2.0, reserved=(),
         order=None, mirrored=None, margin=0.0, prefer_angle=None, mode="bottom", pinned=None):
    """Pack pieces onto an area of width `width` (and optionally height).

    rings: list of cutting outlines (piece coordinates). angles: per piece a list of
    allowed angles (or one shared list). pinned: per piece True if it has to touch the
    left edge (x = 0, e.g. the fabric fold); its leftmost point is placed exactly at x = 0.
    Returns (placements, unplaced_indices, used_height)
    """
    n = len(rings)
    if angles is None:
        angles = list(range(0, 360, 15))
    per_piece_angles = angles if (len(angles) == n and isinstance(angles[0], (list, tuple))) else [angles] * n
    mirrored = mirrored or [False] * n
    pinned = pinned or [False] * n
    cols = int(math.floor((width - 2 * margin) / res))
    if height is None:
        est = sum(max(G.bbox(r)[2] - G.bbox(r)[0], G.bbox(r)[3] - G.bbox(r)[1]) for r in rings)
        rows = int((est + gap * n + max([r[3] for r in reserved], default=0)) / res) + 20
    else:
        rows = int(math.floor((height - 2 * margin) / res))
    occ = np.zeros((rows, cols), dtype=np.float32)
    for (x0, y0, x1, y1) in reserved:
        r0 = max(0, int((y0 - margin) / res) - 1)
        r1 = min(rows, int(math.ceil((y1 - margin) / res)) + 1)
        c0 = max(0, int((x0 - margin) / res) - 1)
        c1 = min(cols, int(math.ceil((x1 - margin) / res)) + 1)
        occ[r0:r1, c0:c1] = 1
    if order is None:
        order = sorted(range(n), key=lambda i: -Polygon(rings[i]).area)
    placements, unplaced = [], []
    pad = gap / 2 + res * 0.5
    cur_max = 0
    for i in order:
        best = None
        for ang in per_piece_angles[i]:
            pts = _oriented(rings[i], ang, mirrored[i])
            mask, _, _, bnd = _raster(pts, res, pad)
            mh, mw = mask.shape
            if mw > cols or mh > rows:
                continue
            ov = fftconvolve(occ, mask[::-1, ::-1], mode="valid")
            feas = ov < 0.5
            if pinned[i]:
                feas[:, 1:] = False
            if not feas.any():
                continue
            rr = np.argmax(feas.any(axis=1))
            cc = int(np.argmax(feas[rr]))
            bottom = rr + mh
            pref = 0.0
            if prefer_angle is not None:
                pref = min(abs((ang - prefer_angle[i]) % 180), 180 - abs((ang - prefer_angle[i]) % 180))
            if mode == "blf":
                score = (rr, pref, cc, bottom)
            elif mode == "total":
                score = (max(cur_max, bottom), rr, pref, cc)
            else:
                score = (bottom, pref, cc)
            if best is None or score < best[0]:
                best = (score, ang, rr, cc, mask, bnd)
        if best is None:
            unplaced.append(i)
            continue
        _, ang, rr, cc, mask, bnd = best
        mh, mw = mask.shape
        occ[rr:rr + mh, cc:cc + mw] = np.maximum(occ[rr:rr + mh, cc:cc + mw], mask)
        cur_max = max(cur_max, rr + mh)
        # offset: bnd = buffered bounds in the rotated position
        dx = margin + cc * res - bnd[0] - 0.5 * res
        dy = margin + rr * res - bnd[1] - 0.5 * res
        if pinned[i]:
            dx = -float(_oriented(rings[i], ang, mirrored[i])[:, 0].min())
        placements.append(Placement(i, float(ang), float(dx), float(dy), mirrored=mirrored[i]))
    used = 0.0
    for pl in placements:
        pts = _oriented(rings[pl.index], pl.angle, pl.mirrored)
        used = max(used, float(pts[:, 1].max() + pl.dy))
    return placements, unplaced, used


def pack_best(rings, width, height=None, angle_step=15, quick=False, **kw):
    """Try several strategies (angle sets × orders × scoring); the shortest layout wins."""
    n = len(rings)
    area = sorted(range(n), key=lambda i: -Polygon(rings[i]).area)

    def longest(i):
        b = G.bbox(rings[i])
        return -max(b[2] - b[0], b[3] - b[1])
    length_order = sorted(range(n), key=longest)
    angle_sets = [[0, 90, 180, 270], list(range(0, 360, angle_step))]
    modes = ["total", "blf"] if quick else ["total", "blf", "bottom"]
    orders = [area] if quick else [area, length_order]
    best = None
    for angs in angle_sets:
        for order in orders:
            for mode in modes:
                pls, unplaced, used = pack(rings, width, height, angles=angs, order=order, mode=mode, **kw)
                score = (len(unplaced), used)
                if best is None or score < best[0]:
                    best = (score, pls, unplaced, used)
    return best[1], best[2], best[3]


def placed_ring(ring, pl: Placement):
    pts = _oriented(ring, pl.angle, pl.mirrored)
    return pts + np.array([pl.dx, pl.dy])


def min_gap(rings, placements) -> float:
    polys = [Polygon(placed_ring(rings[p.index], p)) for p in placements]
    d = 1e9
    for i in range(len(polys)):
        for j in range(i + 1, len(polys)):
            if placements[i].sheet == placements[j].sheet:
                d = min(d, polys[i].distance(polys[j]))
    return d


# ---------------------------------------------------------------------------
# Roll
# ---------------------------------------------------------------------------

def layout_roll(pattern, roll_width_mm: float = 610.0, angle_step: int = 15) -> Layout:
    page_w = roll_width_mm - 10.0
    rings = [_rings(p) for p in pattern.pieces]
    reserved = [(0, 0, page_w, ROLL_HEADER)]
    pls, unplaced, used = pack_best(rings, page_w, angle_step=angle_step,
                                    reserved=reserved, margin=ROLL_MARGIN)
    if unplaced:
        names = ", ".join(pattern.pieces[i].name for i in unplaced)
        raise ValueError(f"piece(s) wider than the roll: {names}")
    page_h = max(used + ROLL_MARGIN + 5.0, page_w + 1.0)   # always portrait
    return Layout("roll", page_w, page_h, pls, canvas_w=page_w, canvas_h=page_h,
                  reserved=reserved, meta=dict(roll=roll_width_mm))


# ---------------------------------------------------------------------------
# Projector: one page, grainline parallel to the long page edge
# ---------------------------------------------------------------------------

PROJECTOR_HEADER = 70.0


def layout_projector(pattern, width_mm: float = 1500.0) -> Layout:
    """All pieces on one page of `width_mm` (default: a 150 cm wide fabric), grainline
    vertical so the page can be projected straight onto the fabric."""
    rings = [_rings(p) for p in pattern.pieces]
    angles = []
    for p in pattern.pieces:
        ga = grain_angle(p)
        angles.append([ga % 360, (ga + 180) % 360])
    reserved = [(0, 0, width_mm, PROJECTOR_HEADER)]
    best = None
    for mode in ("bottom", "total", "blf"):
        pls, unplaced, used = pack(rings, width_mm, angles=angles, reserved=reserved,
                                   margin=ROLL_MARGIN, mode=mode)
        if best is None or (len(unplaced), used) < best[0]:
            best = ((len(unplaced), used), pls, unplaced, used)
    _, pls, unplaced, used = best
    if unplaced:
        names = ", ".join(pattern.pieces[i].name for i in unplaced)
        raise ValueError(f"piece(s) wider than the projector page ({width_mm / 10:.0f} cm): {names}")
    page_h = math.ceil((used + ROLL_MARGIN + 5.0) / 10.0) * 10.0
    return Layout("roll", width_mm, page_h, pls, canvas_w=width_mm, canvas_h=page_h,
                  reserved=reserved, meta=dict(projector=True, roll=width_mm))


# ---------------------------------------------------------------------------
# Tiles (A4 / Letter, also for oversized pieces on A0/A1)
# ---------------------------------------------------------------------------

def _tile_windows(canvas_w, canvas_h, pw, ph):
    sx, sy = pw - OVERLAP, ph - OVERLAP
    ncols = max(1, int(math.ceil((canvas_w - OVERLAP) / sx)))
    nrows = max(1, int(math.ceil((canvas_h - OVERLAP) / sy)))
    tiles = []
    for r in range(nrows):
        for c in range(ncols):
            tiles.append(dict(row=r, col=c, label=f"{chr(65 + r)}{c + 1}",
                              window=(c * sx, r * sy, c * sx + pw, r * sy + ph)))
    return tiles, (nrows, ncols)


def _nonempty(tiles, polys):
    out = []
    for t in tiles:
        w = box(*t["window"])
        t["empty"] = not any(w.intersects(p) for p in polys)
        out.append(t)
    return out


def layout_tiles(pattern, paper: str = "A4", piece_indices=None, angle_step: int = 15,
                 max_cols: int = 6) -> Layout:
    page_w, page_h = PAPER[paper.upper()]
    margin = TILE_MARGIN if paper.upper() in ("A4", "LETTER") else SHEET_MARGIN
    pw, ph = page_w - 2 * margin, page_h - 2 * margin
    sx = pw - OVERLAP
    idx = list(range(len(pattern.pieces))) if piece_indices is None else list(piece_indices)
    rings_all = [_rings(p) for p in pattern.pieces]
    rings = [rings_all[i] for i in idx]
    widest = max(min(G.bbox(r)[2] - G.bbox(r)[0], G.bbox(r)[3] - G.bbox(r)[1]) for r in rings)
    best = None
    for ncols in range(1, max_cols + 1):
        cw = (ncols - 1) * sx + pw
        if cw < widest + 2 * GAP:
            continue
        pls, unplaced, used = pack_best(rings, cw, angle_step=angle_step, margin=3.0, quick=True,
                                        res=3.0)
        if unplaced:
            continue
        for p in pls:
            p.index = idx[p.index]
        ch = used + 3.0
        tiles, grid = _tile_windows(cw, ch, pw, ph)
        polys = [Polygon(placed_ring(rings_all[p.index], p)).buffer(1) for p in pls]
        tiles = _nonempty(tiles, polys)
        n_pages = sum(not t["empty"] for t in tiles)
        score = (n_pages, len(tiles))
        if best is None or score < best[0]:
            best = (score, pls, cw, ch, tiles, grid)
    if best is None:
        raise ValueError("pieces could not be arranged")
    _, pls, cw, ch, tiles, grid = best
    return Layout("tiles", page_w, page_h, pls, canvas_w=cw, canvas_h=ch, tiles=tiles,
                  grid=grid, meta=dict(paper=paper.upper(), margin=margin, pw=pw, ph=ph))


# ---------------------------------------------------------------------------
# Single sheets A0 / A1
# ---------------------------------------------------------------------------

def layout_sheets(pattern, paper: str = "A0", angle_step: int = 15):
    """Whole pieces on as few sheets as possible. Oversized pieces are tiled.

    Returns (layout of the sheets, layout of the tiled oversized pieces or None)
    """
    page_w, page_h = PAPER[paper.upper()]
    rings = [_rings(p) for p in pattern.pieces]
    angles = list(range(0, 360, angle_step))
    remaining = sorted(range(len(rings)), key=lambda i: -Polygon(rings[i]).area)
    # detect oversized pieces
    oversize = []
    for i in list(remaining):
        fits = False
        for a in angles:
            pts = _oriented(rings[i], a)
            w, h = np.ptp(pts[:, 0]) + GAP, np.ptp(pts[:, 1]) + GAP
            if w <= page_w - 2 * SHEET_MARGIN and h <= page_h - 2 * SHEET_MARGIN - 70:
                fits = True
                break
        if not fits:
            oversize.append(i)
            remaining.remove(i)
    placements, sheet = [], 0
    header = [(0, 0, page_w, 70.0)]   # header area per sheet
    while remaining:
        sub = [rings[i] for i in remaining]
        pls, unplaced, _ = pack(sub, page_w, page_h, angles=angles, margin=SHEET_MARGIN,
                                reserved=header)
        if not pls:
            raise ValueError("piece does not fit on any sheet")
        placed_ids = []
        for p in pls:
            p.index = remaining[p.index]
            p.sheet = sheet
            placements.append(p)
            placed_ids.append(p.index)
        remaining = [i for i in remaining if i not in placed_ids]
        sheet += 1
    lay = Layout("sheets", page_w, page_h, placements, canvas_w=page_w, canvas_h=page_h,
                 sheets=sheet, reserved=header, meta=dict(paper=paper.upper()))
    tiled = layout_tiles(pattern, paper, piece_indices=oversize, angle_step=angle_step, max_cols=3) \
        if oversize else None
    return lay, tiled


# ---------------------------------------------------------------------------
# Cutting layout (fabric, grainline parallel to the selvage)
# ---------------------------------------------------------------------------

def grain_angle(piece) -> float:
    """Rotation that makes the grainline vertical (parallel to the selvage)."""
    g0, g1 = np.array(piece.grain[0]), np.array(piece.grain[1])
    v = g1 - g0
    return 90.0 - math.degrees(math.atan2(v[1], v[0]))


def unfolded_ring(piece, keep=None):
    """Outline for cutting: fold edges are unfolded (mirrored), except the edge `keep`."""
    ring = piece.fabric_ring()
    folds = [e for e in piece.edges if e.fold and e.name != keep]
    if not folds:
        return ring
    from shapely.ops import unary_union
    poly = Polygon(ring)
    for e in folds:
        a, b = e.pts[0], e.pts[-1]
        poly = unary_union([poly, Polygon(G.mirror_line(np.asarray(poly.exterior.coords), a, b))])
    poly = poly.buffer(0.01).buffer(-0.01)
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    return np.asarray(poly.exterior.coords)


FABRIC_LAYOUTS = ("auto", "folded", "single")
FOLDED_MIN_WIDTH = 1300.0   # auto mode only tries the folded layout from this width on
FABRIC_MARGIN = 10.0


def fabric_group(piece) -> str:
    if piece.fabric.startswith("Rib knit"):
        return "Rib knit"
    return "Lining" if "Lining" in piece.fabric else "Main fabric"


def _fold_edge(piece):
    """The fold edge that is most parallel to the grainline (placed on the fabric fold)."""
    folds = [e for e in piece.edges if e.fold]
    if not folds:
        return None
    g = np.array(piece.grain[1]) - np.array(piece.grain[0])
    g = g / (np.linalg.norm(g) or 1.0)

    def par(e):
        v = e.pts[-1] - e.pts[0]
        return abs(float(np.dot(v, g))) / (np.linalg.norm(v) or 1.0)
    return max(folds, key=par)


def _mirrored_edge(edge):
    import copy
    e = copy.copy(edge)
    e.pts = G.mirror_x(edge.pts, 0.0)
    return e


def _fold_angle(piece, ring, edge) -> float | None:
    """Rotation that makes the fold edge vertical and the leftmost line of the piece."""
    v = edge.pts[-1] - edge.pts[0]
    base = 90.0 - math.degrees(math.atan2(v[1], v[0]))
    for a in (base % 360, (base + 180) % 360):
        pts = _oriented(ring, a)
        ep = _oriented(edge.pts, a)
        if abs(float(ep[:, 0].max() - pts[:, 0].min())) < 1.0 and np.ptp(ep[:, 0]) < 1.0:
            return a
    return None


def up_y(angle: float) -> float:
    """y component of the piece's "up" direction (towards the waist/neck) after rotating by
    `angle`; > 0 means the top of the piece points to the top end of the fabric. Mirroring
    (x → −x) does not change it."""
    return math.cos(math.radians(angle))


def _nap_angles(angles: list[float]) -> list[float]:
    """Fabric with a nap: only the rotations with the top of the piece towards the top end."""
    keep = [a for a in angles if up_y(a) > 1e-6]
    return keep or [max(angles, key=up_y)]


def _single_items(pattern, ids, nap=False):
    """Single layer: fold pieces unfolded, every copy placed separately."""
    items = []
    for i in ids:
        p = pattern.pieces[i]
        ring = unfolded_ring(p)
        ga = grain_angle(p)
        for k in range(p.cut_count):
            m = bool(p.mirror and p.cut_count % 2 == 0 and k % 2 == 1)
            a = ga if not m else 180 - ga
            angles = [a % 360, (a + 180) % 360]
            items.append(dict(ring=ring, meta=(i, k), angles=_nap_angles(angles) if nap else angles, mirrored=m,
                              pinned=False, layers=1))
    return items


def _folded_items(pattern, ids, half, nap=False):
    """Double layer folded selvage to selvage (fold at x = 0).

    Fold pieces lie with their fold edge on the fabric fold; every other placement cuts
    a mirrored pair through both layers. Pieces wider than the folded width go to a
    single-layer section. Returns (items, single_ids, notes).
    """
    items, single, notes = [], [], []
    avail = half - FABRIC_MARGIN
    for i in ids:
        p = pattern.pieces[i]
        fe = _fold_edge(p)
        if fe is not None:
            ring = unfolded_ring(p, keep=fe.name)
            a = _fold_angle(p, ring, fe)
            mirrored = False
            if a is not None and nap and up_y(a) <= 1e-6:
                # top end down: the mirror image lies on the fold with the top end up
                a = _fold_angle(p, G.mirror_x(ring, 0.0), _mirrored_edge(fe))
                mirrored = True
            if a is None or float(np.ptp(_oriented(ring, a, mirrored)[:, 0])) > avail:
                single.append(i)
                continue
            for k in range(p.cut_count):
                items.append(dict(ring=ring, meta=(i, k), angles=[a], mirrored=mirrored, pinned=True, layers=1))
            continue
        ring = p.fabric_ring()
        ga = grain_angle(p)
        w = min(float(np.ptp(_oriented(ring, ga)[:, 0])), float(np.ptp(_oriented(ring, ga + 180)[:, 0])))
        if w > avail - 5.0:
            single.append(i)
            continue
        n = p.cut_count
        angles = [ga % 360, (ga + 180) % 360]
        for k in range(0, n, 2):
            items.append(dict(ring=ring, meta=(i, k), angles=_nap_angles(angles) if nap else angles, mirrored=False,
                              pinned=False, layers=2 if k + 1 < n else 1))
        if n % 2:
            notes.append(f"{p.name}: the last copy is cut through the top layer only.")
    return items, single, notes


def _pack_items(items, width, gap, margin):
    """Pack cutting-layout items; tries several orders/strategies, the shortest wins."""
    rings = [it["ring"] for it in items]
    n = len(rings)
    area = sorted(range(n), key=lambda i: (not items[i]["pinned"], -Polygon(rings[i]).area))

    def longest(i):
        pts = _oriented(rings[i], items[i]["angles"][0])
        return (not items[i]["pinned"], -float(np.ptp(pts[:, 1])))
    best = None
    for order in (area, sorted(range(n), key=longest)):
        for mode in ("bottom", "total", "blf"):
            res = pack(rings, width, angles=[it["angles"] for it in items], gap=gap, res=5.0,
                       mirrored=[it["mirrored"] for it in items], pinned=[it["pinned"] for it in items],
                       margin=margin, order=order, mode=mode)
            score = (len(res[1]), res[2])
            if best is None or score < best[0]:
                best = (score, res)
    return best[1]


def _plan_single(pattern, ids, width, gap, nap=False):
    items = _single_items(pattern, ids, nap)
    pls, unplaced, used = _pack_items(items, width, gap, FABRIC_MARGIN)
    note = None
    if unplaced:
        # piece longer than the fabric width (e.g. a hem band from tubular rib):
        # compute the plan with the width needed and add a note.
        need = max(float(np.ptp(_oriented(it["ring"], it["angles"][0])[:, 0])) for it in items) \
            + 2 * FABRIC_MARGIN + gap + 15.0
        note = (f"At least one piece is wider than {width / 10:.0f} cm: an open width ≥ "
                f"{need / 10:.0f} cm is needed, or cut the piece in two with a cross seam.")
        width = math.ceil(need / 50.0) * 50.0
        pls, unplaced, used = _pack_items(items, width, gap, FABRIC_MARGIN)
        if unplaced:
            raise ValueError(f"piece does not fit on {width / 10:.0f} cm fabric width")
    return items, pls, used, width, note


def _finish(items, pls, mode, width, length, notes, fold_length=0.0, single_section=False):
    for p in pls:
        p.copy = items[p.index]["meta"][1]
        p.layers = items[p.index]["layers"]
        p.pinned = items[p.index]["pinned"]
    return dict(mode=mode, width=width, length=length, placements=pls,
                rings=[it["ring"] for it in items], meta=[it["meta"] for it in items],
                note=" ".join(n for n in notes if n) or None, fold_length=fold_length,
                single_section=single_section)


def plan_single(pattern, ids, width, gap=5.0, nap=False):
    items, pls, used, width, note = _plan_single(pattern, ids, width, gap, nap)
    return _finish(items, pls, "single", width, used + FABRIC_MARGIN, [note])


def plan_folded(pattern, ids, width, gap=5.0, nap=False):
    """Folded layout; returns None if no piece can be cut double-layered."""
    half = width / 2.0
    items, single, notes = _folded_items(pattern, ids, half, nap)
    if not items:
        return None
    pls, unplaced, used = _pack_items(items, half - FABRIC_MARGIN, gap, 0.0)
    for k in unplaced:
        single.append(items[k]["meta"][0])
    if unplaced:
        keep = [k for k in range(len(items)) if k not in unplaced]
        items = [items[k] for k in keep]
        pls, unplaced, used = _pack_items(items, half - FABRIC_MARGIN, gap, 0.0)
    fold_len = used + gap
    if single:
        single = sorted(set(single))
        names = ", ".join(pattern.pieces[i].name for i in single)
        notes.append(f"Unfold the rest of the fabric for: {names} (single layer, wider than the folded fabric).")
        s_items, s_pls, s_used, s_width, s_note = _plan_single(pattern, single, width, gap, nap)
        notes.append(s_note)
        off = len(items)
        for p in s_pls:
            p.index += off
            p.dy += fold_len
        items += s_items
        pls += s_pls
        width = max(width, s_width)
        length = fold_len + s_used + FABRIC_MARGIN
    else:
        length = fold_len + FABRIC_MARGIN
    return _finish(items, pls, "folded", width, length, notes, fold_length=fold_len,
                   single_section=bool(single))


def layout_fabric(pattern, fabric_widths: dict | None = None, gap: float = 5.0, mode: str = "auto"):
    """Cutting layout per fabric, grainline lengthwise (parallel to the selvage).

    mode: "single" (single layer, all copies), "folded" (double layer folded selvage to
    selvage, fold pieces on the fold) or "auto" (both from a width of 130 cm, the shorter
    one wins; ties go to folded).
    Returns dict fabric → dict(mode, width, length, placements, rings, meta, note, fold_length)
    """
    if mode not in FABRIC_LAYOUTS:
        raise ValueError(f"fabric layout must be one of {', '.join(FABRIC_LAYOUTS)}")
    fabric_widths = fabric_widths or {}
    groups: dict = {}
    for i, p in enumerate(pattern.pieces):
        groups.setdefault(fabric_group(p), []).append(i)
    plans = {}
    nap_main = E.has_nap(pattern.options)
    for fab, ids in groups.items():
        width = fabric_widths.get(fab, 700.0 if fab == "Rib knit" else 1500.0)
        nap = nap_main and fab == "Main fabric"
        try:
            single = plan_single(pattern, ids, width, gap, nap) if mode != "folded" else None
        except ValueError as ex:
            raise ValueError(f"{fab}: {ex}") from None
        folded = None
        if mode == "folded" or (mode == "auto" and width >= FOLDED_MIN_WIDTH):
            folded = plan_folded(pattern, ids, width, gap, nap)
        if folded is None:
            plan = single if single is not None else plan_single(pattern, ids, width, gap, nap)
        elif single is None or folded["length"] <= single["length"]:
            plan = folded
        else:
            plan = single
        if mode == "auto" and single is not None and folded is not None:
            plan["alternative"] = dict(mode="single" if plan is folded else "folded",
                                       length=(single if plan is folded else folded)["length"])
        plan["nap"] = nap
        plans[fab] = plan
    return plans
