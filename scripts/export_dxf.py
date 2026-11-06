"""DXF export for cutting machines and pattern CAD (AAMA layer convention, DXF R12 ASCII).

Each pattern piece becomes one BLOCK, inserted once per layout placement. Inside a block:

| Layer | Content                                                             |
|-------|---------------------------------------------------------------------|
| 1     | cut line (closed polyline incl. seam allowance) and piece texts     |
| 8     | seam line and internal drawn lines (pocket placement, fold-over)    |
| 6     | fold edges ("cut on fold" = mirror line)                            |
| 4     | notches, one LINE per notch starting on the cut line                |
| 7     | grainline                                                           |
| 14    | seam line instead of layer 8 when ``seam_layer="14"``               |

Units are millimetres, scale 1:1, y axis up. A 50 × 50 mm control square is drawn on
layer 8 outside the pieces. No third-party DXF library is needed; R12 ASCII is read
by practically every CAD, cutter and vector program (LibreCAD, Inkscape, …).
"""
from __future__ import annotations

import math
import re

import numpy as np
from shapely.geometry import LineString

import notches as N

SIMPLIFY_TOL = 0.02     # mm; polyline simplification (keeps the 0.1 mm round-trip budget)
CONTROL = 50.0


def _fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class _Writer:
    def __init__(self):
        self.out: list[str] = []

    def pair(self, code: int, value) -> None:
        self.out.append(str(code))
        self.out.append(value if isinstance(value, str) else _fmt(float(value)) if isinstance(value, float) else str(value))

    def text(self) -> str:
        return "\n".join(self.out) + "\n"


def _simplify(pts, closed=False):
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return pts
    ls = LineString(np.vstack([pts, pts[:1]]) if closed else pts)
    simp = np.asarray(ls.simplify(SIMPLIFY_TOL, preserve_topology=False).coords, float)
    if closed and len(simp) > 1 and np.linalg.norm(simp[0] - simp[-1]) < 1e-9:
        simp = simp[:-1]
    return simp


def _polyline(w: _Writer, pts, layer: str, closed=False) -> None:
    pts = _simplify(pts, closed)
    w.pair(0, "POLYLINE")
    w.pair(8, layer)
    w.pair(66, 1)
    w.pair(10, 0.0)
    w.pair(20, 0.0)
    w.pair(30, 0.0)
    w.pair(70, 1 if closed else 0)
    for x, y in pts:
        w.pair(0, "VERTEX")
        w.pair(8, layer)
        w.pair(10, float(x))
        w.pair(20, float(y))
        w.pair(30, 0.0)
    w.pair(0, "SEQEND")
    w.pair(8, layer)


def _line(w: _Writer, a, b, layer: str) -> None:
    w.pair(0, "LINE")
    w.pair(8, layer)
    w.pair(10, float(a[0]))
    w.pair(20, float(a[1]))
    w.pair(30, 0.0)
    w.pair(11, float(b[0]))
    w.pair(21, float(b[1]))
    w.pair(31, 0.0)


def _text(w: _Writer, pos, height: float, text: str, layer: str) -> None:
    w.pair(0, "TEXT")
    w.pair(8, layer)
    w.pair(10, float(pos[0]))
    w.pair(20, float(pos[1]))
    w.pair(30, 0.0)
    w.pair(40, float(height))
    w.pair(1, _ascii(text))


def _ascii(text: str) -> str:
    """R12 files are not UTF-8: transliterate umlauts and drop other non-ASCII characters."""
    table = {"ä": "ae", "ö": "oe", "ü": "ue", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ß": "ss", "×": "x", "·": "-"}
    s = "".join(table.get(c, c) for c in text)
    return s.encode("ascii", "ignore").decode("ascii")


def block_name(i: int, piece) -> str:
    return f"P{i + 1:02d}_" + re.sub(r"[^A-Za-z0-9_]", "_", _ascii(piece.key)).upper()


def piece_block(w: _Writer, i: int, piece, pattern, seam_layer: str = "8", notch_shape: str = "slit") -> None:
    name = block_name(i, piece)
    w.pair(0, "BLOCK")
    w.pair(8, "0")
    w.pair(2, name)
    w.pair(70, 0)
    w.pair(10, 0.0)
    w.pair(20, 0.0)
    w.pair(30, 0.0)
    w.pair(3, name)
    ring = piece.cut_ring()
    _polyline(w, ring, "1", closed=True)
    for e in piece.edges:
        _polyline(w, e.pts, "6" if e.fold else seam_layer)
    for mk in piece.marks:
        _polyline(w, mk.pts, "8")
    for m in N.piece_marks(piece, "slit"):
        if np.linalg.norm(m.cut_pt - m.seam_pt) < 1e-6:          # fold edge: mark into the piece
            _line(w, m.lines[0][0], m.lines[0][-1], "4")
        else:
            _line(w, m.cut_pt, m.seam_pt, "4")
    if piece.grain is not None:
        _line(w, piece.grain[0], piece.grain[1], "7")
    # piece annotation (layer 1)
    x0, y0 = np.min(ring, axis=0)
    seam = piece.seam_ring()
    c = seam.mean(axis=0)
    texts = [f"Piece Name: {piece.name}", f"Size: {pattern.size_label}", f"Quantity: {piece.cut_count}",
             f"Material: {piece.fabric}"]
    if piece.on_fold:
        texts.append("Cut on fold")
    for k, t in enumerate(texts):
        _text(w, (c[0] - 30.0, c[1] + 10.0 - 7.0 * k), 4.0, t, "1")
    w.pair(0, "ENDBLK")
    w.pair(8, "0")


def _insert(w: _Writer, name: str, x: float, y: float, angle: float, mirrored: bool) -> None:
    w.pair(0, "INSERT")
    w.pair(8, "1")
    w.pair(2, name)
    w.pair(10, float(x))
    w.pair(20, float(y))
    w.pair(30, 0.0)
    if mirrored:
        w.pair(41, -1.0)
    w.pair(50, float(angle % 360.0))


LAYERS = [("0", 7), ("1", 7), ("4", 1), ("6", 3), ("7", 5), ("8", 8), ("14", 8)]


def to_dxf(pattern, layout=None, seam_layer: str = "8") -> str:
    """DXF R12 text. With a layout, pieces are inserted at their layout positions."""
    if seam_layer not in ("8", "14"):
        raise ValueError("seam_layer must be '8' or '14'")
    w = _Writer()
    placements = []
    if layout is not None:
        H = layout.canvas_h or layout.page_h
        for pl in layout.placements:
            # layout canvas is y-down: canvas = (xr + dx, -yr + dy) → DXF y-up: (xr + dx, yr + H - dy)
            placements.append((pl.index, pl.dx, H - pl.dy, pl.angle, pl.mirrored))
    else:
        x = 0.0
        for i, p in enumerate(pattern.pieces):
            r = p.cut_ring()
            placements.append((i, x - r[:, 0].min(), -r[:, 1].min(), 0.0, False))
            x += r[:, 0].max() - r[:, 0].min() + 20.0
    # extents
    pts = []
    for i, dx, dy, ang, mir in placements:
        r = pattern.pieces[i].cut_ring().copy()
        if mir:
            r[:, 0] = -r[:, 0]
        a = math.radians(ang)
        rot = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        pts.append(r @ rot.T + np.array([dx, dy]))
    allp = np.vstack(pts) if pts else np.zeros((1, 2))
    xmin, ymin = allp.min(axis=0)
    xmax, ymax = allp.max(axis=0)
    sq_x, sq_y = xmin, ymin - CONTROL - 20.0

    w.pair(0, "SECTION")
    w.pair(2, "HEADER")
    w.pair(9, "$ACADVER")
    w.pair(1, "AC1009")
    w.pair(9, "$INSUNITS")
    w.pair(70, 4)
    w.pair(9, "$MEASUREMENT")
    w.pair(70, 1)
    w.pair(9, "$EXTMIN")
    w.pair(10, float(min(xmin, sq_x)))
    w.pair(20, float(sq_y))
    w.pair(30, 0.0)
    w.pair(9, "$EXTMAX")
    w.pair(10, float(xmax))
    w.pair(20, float(ymax))
    w.pair(30, 0.0)
    w.pair(0, "ENDSEC")

    w.pair(0, "SECTION")
    w.pair(2, "TABLES")
    w.pair(0, "TABLE")
    w.pair(2, "LTYPE")
    w.pair(70, 1)
    w.pair(0, "LTYPE")
    w.pair(2, "CONTINUOUS")
    w.pair(70, 0)
    w.pair(3, "Solid line")
    w.pair(72, 65)
    w.pair(73, 0)
    w.pair(40, 0.0)
    w.pair(0, "ENDTAB")
    w.pair(0, "TABLE")
    w.pair(2, "LAYER")
    w.pair(70, len(LAYERS))
    for name, color in LAYERS:
        w.pair(0, "LAYER")
        w.pair(2, name)
        w.pair(70, 0)
        w.pair(62, color)
        w.pair(6, "CONTINUOUS")
    w.pair(0, "ENDTAB")
    w.pair(0, "ENDSEC")

    w.pair(0, "SECTION")
    w.pair(2, "BLOCKS")
    for i, p in enumerate(pattern.pieces):
        piece_block(w, i, p, pattern, seam_layer)
    w.pair(0, "ENDSEC")

    w.pair(0, "SECTION")
    w.pair(2, "ENTITIES")
    for i, dx, dy, ang, mir in placements:
        _insert(w, block_name(i, pattern.pieces[i]), dx, dy, ang, mir)
    sq = np.array([[sq_x, sq_y], [sq_x + CONTROL, sq_y], [sq_x + CONTROL, sq_y + CONTROL], [sq_x, sq_y + CONTROL]])
    _polyline(w, sq, "8", closed=True)
    _text(w, (sq_x + CONTROL + 5.0, sq_y + 2.0), 4.0, "Control square 50 x 50 mm", "8")
    _text(w, (sq_x, ymax + 10.0), 6.0, f"{pattern.title} - {pattern.size_label}", "8")
    w.pair(0, "ENDSEC")
    w.pair(0, "EOF")
    return w.text()


def write_dxf(pattern, path: str, layout=None, seam_layer: str = "8") -> str:
    with open(path, "w", encoding="ascii", newline="\r\n") as f:
        f.write(to_dxf(pattern, layout, seam_layer))
    return path


# ---------------------------------------------------------------------------
# Minimal reader (round-trip tests, sanity checks)
# ---------------------------------------------------------------------------

def read_dxf(path_or_text: str) -> dict:
    """Parse the subset written above: blocks with polylines/lines/texts per layer and inserts."""
    if "\n" in path_or_text:
        text = path_or_text
    else:
        with open(path_or_text, encoding="ascii") as f:
            text = f.read()
    lines = [s.strip() for s in text.splitlines()]
    pairs = [(int(lines[i]), lines[i + 1]) for i in range(0, len(lines) - 1, 2)]
    blocks: dict[str, dict] = {}
    entities: dict = {"inserts": [], "polylines": [], "texts": []}
    header: dict[str, str] = {}
    cur = entities
    i = 0
    section = None
    while i < len(pairs):
        code, val = pairs[i]
        if code == 0 and val == "SECTION":
            section = pairs[i + 1][1]
            i += 2
            continue
        if section == "HEADER" and code == 9:
            header[val] = pairs[i + 1][1]
        if code == 0 and val == "BLOCK":
            j = i + 1
            name = None
            while pairs[j][0] != 0:
                if pairs[j][0] == 2:
                    name = pairs[j][1]
                j += 1
            cur = {"polylines": [], "lines": [], "texts": []}
            blocks[name] = cur
            i = j
            continue
        if code == 0 and val == "ENDBLK":
            cur = entities
        if code == 0 and val == "POLYLINE":
            j = i + 1
            layer, closed, verts = "0", False, []
            while not (pairs[j][0] == 0 and pairs[j][1] in ("VERTEX", "SEQEND")):
                if pairs[j][0] == 8:
                    layer = pairs[j][1]
                if pairs[j][0] == 70:
                    closed = bool(int(pairs[j][1]) & 1)
                j += 1
            while pairs[j][1] == "VERTEX" and pairs[j][0] == 0:
                j += 1
                x = y = 0.0
                while pairs[j][0] != 0:
                    if pairs[j][0] == 10:
                        x = float(pairs[j][1])
                    if pairs[j][0] == 20:
                        y = float(pairs[j][1])
                    j += 1
                verts.append((x, y))
            cur.setdefault("polylines", []).append({"layer": layer, "closed": closed, "pts": np.array(verts)})
            i = j
            continue
        if code == 0 and val in ("LINE", "TEXT", "INSERT"):
            j = i + 1
            d: dict = {}
            while pairs[j][0] != 0:
                d[pairs[j][0]] = pairs[j][1]
                j += 1
            if val == "LINE":
                cur.setdefault("lines", []).append({"layer": d.get(8), "a": (float(d[10]), float(d[20])),
                                                    "b": (float(d[11]), float(d[21]))})
            elif val == "TEXT":
                cur.setdefault("texts", []).append({"layer": d.get(8), "text": d.get(1, "")})
            else:
                entities["inserts"].append({"name": d[2], "x": float(d[10]), "y": float(d[20]),
                                            "angle": float(d.get(50, 0)), "xscale": float(d.get(41, 1))})
            i = j
            continue
        i += 1
    return {"header": header, "blocks": blocks, "entities": entities}
