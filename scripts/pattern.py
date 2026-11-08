"""Data model for pattern pieces and patterns.

A pattern piece (Piece) is a closed, counter-clockwise sequence of named edges
(Edge). Every edge carries its own seam allowance; fold edges have a seam allowance
of 0 and are drawn as dash-dot lines. The edges describe the **seam line** (net
outline); the cutting line is computed from it with geometry.offset_outline.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import numpy as np

import geometry as G


@dataclass
class Edge:
    name: str
    pts: np.ndarray
    sa: float = 10.0            # seam allowance in mm
    fold: bool = False          # cut on the fold
    label: str = ""             # e.g. "Hem", "Side seam"
    turned: bool = False        # allowance is folded back (hem, casing): corners are mirrored
    sa_hint: float = 0.0        # pattern without allowances: the allowance to add when cutting
    pointed: bool = False       # meets a fold edge at an intended point (V-neck), not at 90°
    raw: bool = False           # left as a raw cut edge on purpose (fleece, felt): no allowance needed

    @property
    def length(self) -> float:
        return G.length(self.pts)


@dataclass
class Notch:
    edge: str
    s: float                    # distance from the start of the edge in mm (negative: from the end)
    count: int = 1              # 1 = single (front), 2 = double (back)
    shape: str | None = None    # slit | t | v; None = pattern default (option notch_style)


@dataclass
class Mark:
    """Inner line, e.g. pocket placement, fold-over line, elastic casing."""
    pts: np.ndarray
    style: str = "mark"         # mark | fold | placement
    label: str = ""
    template: bool = False      # transferred after cutting: the booklet prints a 1:1 template


@dataclass
class Piece:
    key: str
    name: str
    edges: list[Edge]
    cut_count: int = 2
    mirror: bool = True                 # cut as a mirrored pair
    fabric: str = "Main fabric"
    grain: tuple | None = None          # (p0, p1) grainline arrow
    notches: list[Notch] = field(default_factory=list)
    marks: list[Mark] = field(default_factory=list)
    info: list[str] = field(default_factory=list)   # additional labels
    stretch_dir: str = ""                # note on the stretch direction
    part_of: str = ""                    # part of the front/back view (yoke, side panel, colour block)

    # ----------------------------------------------------------------- geometry
    def edge(self, name: str) -> Edge:
        for e in self.edges:
            if e.name == name:
                return e
        raise KeyError(f"{self.name}: edge '{name}' missing")

    def edge_index(self, name: str) -> int:
        return [e.name for e in self.edges].index(name)

    def seam_ring(self) -> np.ndarray:
        r = G.join(*[e.pts for e in self.edges])
        if len(r) > 3 and np.linalg.norm(r[-1] - r[0]) < 1e-6:
            r = r[:-1]
        return r

    def cut_ring(self) -> np.ndarray:
        return G.offset_outline([e.pts for e in self.edges], [e.sa for e in self.edges],
                                [e.turned for e in self.edges])

    def fabric_ring(self) -> np.ndarray:
        """Outline to cut from the fabric: like cut_ring, but a pattern without seam
        allowance gets the allowances to add (sa_hint), so fabric consumption stays right."""
        if any(e.sa > 0 for e in self.edges) or not any(e.sa_hint > 0 for e in self.edges):
            return self.cut_ring()
        return G.offset_outline([e.pts for e in self.edges], [e.sa_hint for e in self.edges],
                                [e.turned for e in self.edges])

    @property
    def on_fold(self) -> bool:
        return any(e.fold for e in self.edges)

    def check_closed(self, tol: float = 0.5) -> list[str]:
        errs = []
        n = len(self.edges)
        for i in range(n):
            a = self.edges[i].pts[-1]
            b = self.edges[(i + 1) % n].pts[0]
            if np.linalg.norm(a - b) > tol:
                errs.append(f"gap of {np.linalg.norm(a - b):.1f} mm between "
                            f"'{self.edges[i].name}' and '{self.edges[(i + 1) % n].name}'")
        if G.signed_area(self.seam_ring()) <= 0:
            errs.append("outline runs clockwise")
        return errs

    def cut_text(self) -> str:
        from i18n import t
        if self.on_fold:
            if self.cut_count == 1:
                return t("cut 1 on fold")
            return t(f"cut {self.cut_count} on fold")
        if self.cut_count == 2 and self.mirror:
            return t("cut 2 (mirrored pair)")
        return t(f"cut {self.cut_count}")

    def sa_text(self, units: str = "metric") -> str:
        import units as U
        from i18n import t

        def cm(v):
            return U.allowance(v, units).removesuffix(" cm")
        unit = "" if U.check(units) == "imperial" else " cm"

        def grouped(attr):
            vals: dict = {}
            for e in self.edges:
                if not e.fold:
                    vals.setdefault(round(getattr(e, attr) * 2) / 2, []).append(e.label or e.name)
            return vals

        def describe(vals):
            common = max(vals, key=lambda k: len(vals[k]))
            rest = [f"{', '.join(sorted(set(t(n) for n in names)))}: {cm(k)}{unit}" for k, names in vals.items() if k != common]
            return common, rest

        vals = grouped("sa")
        if not vals:
            return t("no seam allowance")
        if all(k == 0 for k in vals):
            hints = {k: v for k, v in grouped("sa_hint").items() if k > 0}
            if not hints:
                return t("NO seam allowance included")
            common, rest = describe(hints)
            return "; ".join([t(f"NO seam allowance included: add {cm(common)}{unit}")] + rest)
        common, rest = describe(vals)
        return "; ".join([t(f"seam allowance {cm(common)}{unit} included")] + rest)

    def transformed(self, fn) -> Piece:
        """Copy with all points transformed by fn."""
        import copy
        p = copy.deepcopy(self)
        for e in p.edges:
            e.pts = fn(e.pts)
        for m in p.marks:
            m.pts = fn(m.pts)
        if p.grain is not None:
            g = fn(np.array(p.grain))
            p.grain = (g[0], g[1])
        return p

    def to_json(self) -> dict:
        return {
            "key": self.key, "name": self.name, "cut_count": self.cut_count,
            "mirror": self.mirror, "fabric": self.fabric,
            "edges": [{"name": e.name, "label": e.label, "sa": e.sa, "fold": e.fold,
                       "length_mm": round(e.length, 1)} for e in self.edges],
        }


@dataclass
class Pattern:
    garment: str                     # module name, e.g. pants_basic
    title: str                       # e.g. "Harem pants"
    size_label: str                  # z. B. "Gr. 122"
    pieces: list[Piece]
    measures: dict[str, float]       # body measurements in mm
    options: dict[str, Any]
    seams: list[dict] = field(default_factory=list)       # seam pairs for validation
    corners: list[dict] = field(default_factory=list)     # angle checks
    checks: list[dict] = field(default_factory=list)      # further checks (circumferences …)
    finished: dict[str, float] = field(default_factory=dict)  # finished measurements (virtually sewn)
    notes: list[str] = field(default_factory=list)
    construction: list[dict] = field(default_factory=list)  # named draft values (construction.py)

    def piece(self, key: str) -> Piece:
        for p in self.pieces:
            if p.key == key:
                return p
        raise KeyError(key)

    def has(self, key: str) -> bool:
        return any(p.key == key for p in self.pieces)

    def edge_len(self, ref: str) -> float:
        """Length of an edge, reference 'piece.edge' or 'piece.edge1+edge2'."""
        key, names = ref.split(".", 1)
        p = self.piece(key)
        return sum(p.edge(n).length for n in names.split("+"))

    def summary(self) -> dict:
        return {
            "garment": self.garment, "title": self.title, "size": self.size_label,
            "options": self.options,
            "measures_mm": {k: round(v, 1) for k, v in self.measures.items()},
            "finished_mm": {k: round(v, 1) for k, v in self.finished.items()},
            "pieces": [p.to_json() for p in self.pieces],
            "construction": self.construction,
        }

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.summary(), f, ensure_ascii=False, indent=2, default=str)


def rect_piece(key: str, name: str, w: float, h: float, *, sa: float = 10.0,
               fold_left: bool = False, fold_bottom: bool = False, cut_count: int = 1,
               fabric: str = "Main fabric", names=("bottom", "right", "top", "left"),
               labels=("", "", "", ""), mirror: bool = False, grain_vertical: bool = True,
               sas=None) -> Piece:
    """Rectangular piece (waistband, rib band, loop …) with its origin at the bottom left."""
    c = [G.P(0, 0), G.P(w, 0), G.P(w, h), G.P(0, h)]
    sas = sas or (sa, sa, sa, sa)
    edges = [
        Edge(names[0], G.line(c[0], c[1]), 0.0 if fold_bottom else sas[0], fold_bottom, labels[0]),
        Edge(names[1], G.line(c[1], c[2]), sas[1], False, labels[1]),
        Edge(names[2], G.line(c[2], c[3]), sas[2], False, labels[2]),
        Edge(names[3], G.line(c[3], c[0]), 0.0 if fold_left else sas[3], fold_left, labels[3]),
    ]
    if grain_vertical:
        grain = (G.P(w * 0.5, h * 0.2), G.P(w * 0.5, h * 0.8)) if h > 60 else \
            (G.P(w * 0.3, h * 0.5), G.P(w * 0.3, h * 0.5 + max(20, h * 0.4))) if h > 45 else \
            (G.P(w * 0.3, h * 0.12), G.P(w * 0.3, h * 0.88))
    else:
        grain = (G.P(w * 0.2, h * 0.5), G.P(w * 0.8, h * 0.5))
    return Piece(key, name, edges, cut_count=cut_count, mirror=mirror, fabric=fabric, grain=grain)
