"""Notch geometry: where a notch sits on the cut line and what it looks like.

A notch is defined on the seam line (edge + arc length). It has to be visible on the
cut line, because that is where the fabric is snipped. This module projects the seam-line
position onto the cut line:

* ``straight``: along the edge normal (default along an edge).
* ``bisector``: along the bisector of the two edge normals. Used automatically for a
  notch that sits on a corner (within ``CORNER_TOL`` of an edge end), e.g. the
  underarm point or the crotch point. A plain normal there would miss the mitred
  corner of the cut line.

Shapes:

* ``slit``: a single line from the cut line inwards to just past the seam line (default).
* ``t``: slit plus a short cross bar at the seam line (good for heavy or loose fabrics).
* ``v``: a V cut into the allowance (good for cutting machines and projector use).

All coordinates are piece coordinates in mm (y up, contour counter-clockwise).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from shapely.geometry import LineString, Point

import geometry as G

SHAPES = ("slit", "t", "v")
CORNER_TOL = 1.5        # mm from an edge end: notch counts as a corner notch
PAST_SEAM = 2.0         # slit continues this far past the seam line into the piece
FOLD_DEPTH = 6.0        # notch length on a fold edge (no allowance there)
V_HALF_WIDTH = 1.5      # half opening of a V notch on the cut line
V_MAX_DEPTH = 5.0
T_HALF_BAR = 2.0
MULTI_SPACING = 3.0     # distance between the lines of a double/triple notch


@dataclass
class NotchMark:
    """Resolved notch: point on the cut line, point on the seam line and the drawn lines."""
    cut_pt: np.ndarray          # where the notch meets the cut line
    seam_pt: np.ndarray         # where it meets the seam line
    direction: np.ndarray       # unit vector from cut line into the piece
    lines: list[np.ndarray]     # polylines to draw (first point of lines[0] = cut_pt)
    corner: bool = False


def _outward_normal(pts, s):
    t = G.tangent_at(pts, s)
    return np.array([t[1], -t[0]])          # right of travel = outside for a CCW contour


def _ray_hit(origin, direction, ring_ls: LineString, max_len: float):
    """First intersection of the ray origin + u * direction (0 < u <= max_len) with the ring."""
    seg = LineString([origin + direction * 0.01, origin + direction * max_len])
    inter = seg.intersection(ring_ls)
    if inter.is_empty:
        return None
    pts = []
    for g in getattr(inter, "geoms", [inter]):
        pts.extend(np.asarray(g.coords, float))
    return min(pts, key=lambda q: float(np.linalg.norm(q - origin)))


def _corner_bisector(piece, edge_idx: int, at_end: bool):
    """Outward bisector at the corner at the end (or start) of edge `edge_idx`."""
    n = len(piece.edges)
    if at_end:
        e_in, e_out = piece.edges[edge_idx], piece.edges[(edge_idx + 1) % n]
    else:
        e_in, e_out = piece.edges[(edge_idx - 1) % n], piece.edges[edge_idx]
    corner = e_out.pts[0]
    n_in = _outward_normal(e_in.pts, e_in.length - 0.5)
    n_out = _outward_normal(e_out.pts, 0.5)
    b = n_in + n_out
    if np.linalg.norm(b) < 1e-6:                  # 180° turn, cannot happen on a valid piece
        b = n_in
    return corner, G.unit(b), max(e_in.sa, e_out.sa)


def resolve(piece, notch, shape: str = "slit", cut_ring=None) -> list[NotchMark]:
    """All marks for one notch (one per line of a double/triple notch)."""
    if shape not in SHAPES:
        raise ValueError(f"unknown notch shape {shape!r}, expected one of {SHAPES}")
    e = piece.edge(notch.edge)
    idx = piece.edge_index(notch.edge)
    ring = piece.cut_ring() if cut_ring is None else cut_ring
    ring_ls = LineString(np.vstack([ring, ring[:1]]))
    total = e.length
    s0 = notch.s if notch.s >= 0 else total + notch.s
    marks = []
    for k in range(notch.count):
        off = (k - (notch.count - 1) / 2) * MULTI_SPACING
        s = min(max(s0 + off, 0.0), total)
        at_start, at_end = s <= CORNER_TOL, s >= total - CORNER_TOL
        corner = (at_start or at_end) and notch.count == 1
        if corner:
            p, d_out, sa = _corner_bisector(piece, idx, at_end=at_end)
        else:
            p = G.point_at(e.pts, s)
            d_out = _outward_normal(e.pts, s)
            sa = e.sa
        if sa <= 0:                                   # fold edge: short mark into the piece
            q = p
            d_in = -d_out
            lines = [np.array([p, p + d_in * FOLD_DEPTH])]
            marks.append(NotchMark(q, p, d_in, lines, corner))
            continue
        q = _ray_hit(p, d_out, ring_ls, max_len=4.0 * sa + 10.0)
        if q is None:
            q = p + d_out * sa
        d_in = G.unit(p - q)
        side = np.array([-d_in[1], d_in[0]])
        inner = p + d_in * PAST_SEAM
        if shape == "slit":
            lines = [np.array([q, inner])]
        elif shape == "t":
            lines = [np.array([q, inner]), np.array([inner - side * T_HALF_BAR, inner + side * T_HALF_BAR])]
        else:
            depth = min(V_MAX_DEPTH, 0.5 * float(np.linalg.norm(p - q)))
            tip = q + d_in * depth
            lines = [np.array([q + side * V_HALF_WIDTH, tip, q - side * V_HALF_WIDTH])]
        marks.append(NotchMark(q, p, d_in, lines, corner))
    return marks


def piece_marks(piece, shape: str = "slit") -> list[NotchMark]:
    ring = piece.cut_ring()
    out = []
    for nt in piece.notches:
        out.extend(resolve(piece, nt, getattr(nt, "shape", None) or shape, ring))
    return out


def on_cut_line(piece, marks, tol: float = 0.3) -> list[str]:
    """Problems: notch marks that do not start on the cut line (used by the validation)."""
    ring = piece.cut_ring()
    ls = LineString(np.vstack([ring, ring[:1]]))
    errs = []
    for m in marks:
        if float(np.linalg.norm(m.cut_pt - m.seam_pt)) < 1e-6:     # fold edge
            continue
        d = ls.distance(Point(m.cut_pt))
        if d > tol:
            errs.append(f"notch {d:.1f} mm away from the cut line")
    return errs
