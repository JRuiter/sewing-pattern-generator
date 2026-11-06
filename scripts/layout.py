"""Anordnung der Schnittteile auf Rolle, Einzelbögen (A0/A1) und Kachelseiten (A4/Letter).

Koordinaten der Anordnung ("Leinwand"): mm, x nach rechts, y nach **unten** (Seitenoben = 0).
Ein Teil wird um `angle` (Grad, gegen den Uhrzeigersinn im Teil-Koordinatensystem)
gedreht und dann verschoben: canvas = (xr + dx, −yr + dy). Der Fadenlauf dreht mit.

Packverfahren: Rasterbasiertes "tiefste Position zuerst" (Bottom-Left-Fill) mit
FFT-Korrelation zur Kollisionsprüfung. Abstand zwischen Teilen ≥ `gap` mm.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw
from scipy.signal import fftconvolve
from shapely.geometry import Polygon, box

import geometry as G

PAPER = {  # Breite × Höhe in mm (Hochformat)
    "A4": (210.0, 297.0), "LETTER": (215.9, 279.4), "A1": (594.0, 841.0), "A0": (841.0, 1189.0),
}
TILE_MARGIN = 8.0       # Druckerrand A4/Letter (≥ 8 mm)
SHEET_MARGIN = 10.0     # Rand bei A0/A1
ROLL_MARGIN = 5.0       # seitlicher Rand auf der Rolle
OVERLAP = 10.0          # Klebeüberlappung
GAP = 10.0              # Mindestabstand zwischen Teilen
ROLL_HEADER = 80.0      # Kopfbereich auf der Rolle (Titel, Legende, Kontrollquadrate)


@dataclass
class Placement:
    index: int          # Index in pattern.pieces
    angle: float
    dx: float
    dy: float
    sheet: int = 0
    copy: int = 0       # für Zuschnittplan (welche Kopie)
    mirrored: bool = False

    def apply(self, pts):
        p = G.as_pts(pts)
        if self.mirrored:
            p = G.mirror_x(p, 0.0)
        r = G.rotate(p, self.angle)
        return np.stack([r[:, 0] + self.dx, -r[:, 1] + self.dy], axis=1)


@dataclass
class Layout:
    kind: str                       # rolle | bogen | kacheln
    page_w: float
    page_h: float
    placements: list[Placement]
    canvas_w: float = 0.0
    canvas_h: float = 0.0
    sheets: int = 1
    tiles: list = field(default_factory=list)   # Kacheln: dict(row, col, label, window)
    grid: tuple = (0, 0)
    reserved: list = field(default_factory=list)  # reservierte Rechtecke (x0, y0, x1, y1)
    meta: dict = field(default_factory=dict)


def _rings(piece):
    return piece.cut_ring()


def _raster(pts, res, pad):
    """Polygon (Leinwandkoordinaten) → Bool-Maske, Ursprung = bbox-Min."""
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
    # konservativ: um 1 Pixel dilatieren
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
         order=None, mirrored=None, margin=0.0, prefer_angle=None, mode="bottom"):
    """Teile auf einer Fläche der Breite `width` (und optional Höhe) packen.

    rings: Liste der Schnittkonturen (Teilkoordinaten). angles: je Teil Liste erlaubter
    Winkel (oder eine gemeinsame Liste). Rückgabe: (placements, unplaced_indices, used_height)
    """
    n = len(rings)
    if angles is None:
        angles = list(range(0, 360, 15))
    per_piece_angles = angles if (len(angles) == n and isinstance(angles[0], (list, tuple))) else [angles] * n
    mirrored = mirrored or [False] * n
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
        # Verschiebung: bnd = gepufferte Bounds in orientierter Lage
        dx = margin + cc * res - bnd[0] - 0.5 * res
        dy = margin + rr * res - bnd[1] - 0.5 * res
        placements.append(Placement(i, float(ang), float(dx), float(dy), mirrored=mirrored[i]))
    used = 0.0
    for pl in placements:
        pts = _oriented(rings[pl.index], pl.angle, pl.mirrored)
        used = max(used, float(pts[:, 1].max() + pl.dy))
    return placements, unplaced, used


def pack_best(rings, width, height=None, angle_step=15, quick=False, **kw):
    """Mehrere Strategien (Winkelsätze × Reihenfolgen × Bewertung) probieren,
    die kürzeste Anordnung gewinnt."""
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
# Rolle
# ---------------------------------------------------------------------------

def layout_roll(pattern, roll_width_mm: float = 610.0, angle_step: int = 15) -> Layout:
    page_w = roll_width_mm - 10.0
    rings = [_rings(p) for p in pattern.pieces]
    reserved = [(0, 0, page_w, ROLL_HEADER)]
    pls, unplaced, used = pack_best(rings, page_w, angle_step=angle_step,
                                    reserved=reserved, margin=ROLL_MARGIN)
    if unplaced:
        names = ", ".join(pattern.pieces[i].name for i in unplaced)
        raise ValueError(f"Teil(e) breiter als die Rolle: {names}")
    page_h = max(used + ROLL_MARGIN + 5.0, page_w + 1.0)   # immer Hochformat
    return Layout("rolle", page_w, page_h, pls, canvas_w=page_w, canvas_h=page_h,
                  reserved=reserved, meta=dict(roll=roll_width_mm))


# ---------------------------------------------------------------------------
# Kacheln (A4 / Letter, auch für übergroße Teile bei A0/A1)
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
        raise ValueError("Teile konnten nicht angeordnet werden")
    _, pls, cw, ch, tiles, grid = best
    return Layout("kacheln", page_w, page_h, pls, canvas_w=cw, canvas_h=ch, tiles=tiles,
                  grid=grid, meta=dict(paper=paper.upper(), margin=margin, pw=pw, ph=ph))


# ---------------------------------------------------------------------------
# Einzelbögen A0 / A1
# ---------------------------------------------------------------------------

def layout_sheets(pattern, paper: str = "A0", angle_step: int = 15):
    """Teile ungeteilt auf möglichst wenige Bögen. Übergroße Teile werden gekachelt.

    Rückgabe: (Layout der Bögen, Layout der gekachelten Übergrößen oder None)
    """
    page_w, page_h = PAPER[paper.upper()]
    rings = [_rings(p) for p in pattern.pieces]
    angles = list(range(0, 360, angle_step))
    remaining = sorted(range(len(rings)), key=lambda i: -Polygon(rings[i]).area)
    # Übergröße feststellen
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
    header = [(0, 0, page_w, 70.0)]   # Kopfbereich je Bogen
    while remaining:
        sub = [rings[i] for i in remaining]
        pls, unplaced, _ = pack(sub, page_w, page_h, angles=angles, margin=SHEET_MARGIN,
                                reserved=header)
        if not pls:
            raise ValueError("Teil passt auf keinen Bogen")
        placed_ids = []
        for p in pls:
            p.index = remaining[p.index]
            p.sheet = sheet
            placements.append(p)
            placed_ids.append(p.index)
        remaining = [i for i in remaining if i not in placed_ids]
        sheet += 1
    lay = Layout("bogen", page_w, page_h, placements, canvas_w=page_w, canvas_h=page_h,
                 sheets=sheet, reserved=header, meta=dict(paper=paper.upper()))
    tiled = layout_tiles(pattern, paper, piece_indices=oversize, angle_step=angle_step, max_cols=3) \
        if oversize else None
    return lay, tiled


# ---------------------------------------------------------------------------
# Zuschnittplan (Stoff, Fadenlauf parallel zur Webkante)
# ---------------------------------------------------------------------------

def grain_angle(piece) -> float:
    """Drehwinkel, der den Fadenlauf senkrecht (parallel zur Webkante) stellt."""
    g0, g1 = np.array(piece.grain[0]), np.array(piece.grain[1])
    v = g1 - g0
    return 90.0 - math.degrees(math.atan2(v[1], v[0]))


def unfolded_ring(piece):
    """Kontur für den einlagigen Zuschnitt: Teile im Bruch werden aufgeklappt."""
    ring = piece.cut_ring()
    folds = [e for e in piece.edges if e.fold]
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


def layout_fabric(pattern, fabric_widths: dict | None = None, gap: float = 5.0):
    """Zuschnittplan je Stoffart: einlagig, alle Kopien, Fadenlauf längs.

    Rückgabe: dict stoff → dict(width, length, placements, rings, pieces)
    """
    fabric_widths = fabric_widths or {}
    groups = {}
    for i, p in enumerate(pattern.pieces):
        fab = "Bündchen" if p.fabric.startswith("Bündchen") else (
            "Futter" if "Futter" in p.fabric else "Oberstoff")
        groups.setdefault(fab, []).append(i)
    plans = {}
    for fab, ids in groups.items():
        width = fabric_widths.get(fab, 700.0 if fab == "Bündchen" else 1500.0)
        rings, meta, angles, mir = [], [], [], []
        for i in ids:
            p = pattern.pieces[i]
            ring = unfolded_ring(p)
            ga = grain_angle(p)
            for k in range(p.cut_count):
                m = bool(p.mirror and p.cut_count % 2 == 0 and k % 2 == 1)
                rings.append(ring)
                meta.append((i, k))
                a = ga if not m else 180 - ga
                angles.append([a % 360, (a + 180) % 360])
                mir.append(m)
        pls, unplaced, used = pack(rings, width, angles=angles, gap=gap, res=5.0, mirrored=mir,
                                   margin=10.0)
        note = None
        if unplaced:
            # Teil länger als die Stoffbreite (z. B. Saumbündchen aus Schlauchware):
            # Plan mit der nötigen Breite rechnen und Hinweis ausgeben.
            need = max(float(np.ptp(np.asarray(r)[:, 0])) for r in rings) + 2 * 10.0 + gap
            note = (f"Mindestens ein Teil ist breiter als {width / 10:.0f} cm: offene Breite ≥ "
                    f"{need / 10:.0f} cm nötig oder das Teil mit Quernaht zweiteilig zuschneiden.")
            width = math.ceil(need / 50.0) * 50.0
            pls, unplaced, used = pack(rings, width, angles=angles, gap=gap, res=5.0, mirrored=mir,
                                       margin=10.0)
            if unplaced:
                raise ValueError(f"{fab}: Teil passt nicht auf {width / 10:.0f} cm Stoffbreite")
        for p in pls:
            pi, k = meta[p.index]
            p.copy = k
        plans[fab] = dict(width=width, length=used + 10.0, placements=pls, rings=rings, meta=meta, note=note)
    return plans
