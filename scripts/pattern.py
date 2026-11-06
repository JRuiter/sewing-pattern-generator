"""Datenmodell für Schnittteile und Schnittmuster.

Ein Schnittteil (Piece) besteht aus einer geschlossenen, gegen den Uhrzeigersinn
laufenden Folge benannter Kanten (Edge). Jede Kante trägt ihre eigene Nahtzugabe;
Bruchkanten haben Nahtzugabe 0 und werden als Strich-Punkt-Linie gezeichnet.
Die Kanten beschreiben die **Nählinie** (Nettokontur); die Schnittlinie wird über
geometry.offset_outline daraus berechnet.
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
    sa: float = 10.0            # Nahtzugabe in mm
    fold: bool = False          # Stoffbruch
    label: str = ""             # z. B. "Saum", "Seitennaht"

    @property
    def length(self) -> float:
        return G.length(self.pts)


@dataclass
class Notch:
    edge: str
    s: float                    # Abstand vom Kantenanfang in mm (negativ: vom Ende)
    count: int = 1              # 1 = einfach (vorne), 2 = doppelt (hinten)


@dataclass
class Mark:
    """Innenlinie, z. B. Taschenposition, Umbruchlinie, Gummidurchzug."""
    pts: np.ndarray
    style: str = "mark"         # mark | fold | placement
    label: str = ""


@dataclass
class Piece:
    key: str
    name: str
    edges: list[Edge]
    cut_count: int = 2
    mirror: bool = True                 # Paar gegengleich zuschneiden
    fabric: str = "Oberstoff"
    grain: tuple | None = None          # (p0, p1) Fadenlaufpfeil
    notches: list[Notch] = field(default_factory=list)
    marks: list[Mark] = field(default_factory=list)
    info: list[str] = field(default_factory=list)   # zusätzliche Beschriftung
    stretch_dir: str = ""                # Hinweis zur Dehnrichtung

    # ----------------------------------------------------------------- Geometrie
    def edge(self, name: str) -> Edge:
        for e in self.edges:
            if e.name == name:
                return e
        raise KeyError(f"{self.name}: Kante '{name}' fehlt")

    def edge_index(self, name: str) -> int:
        return [e.name for e in self.edges].index(name)

    def seam_ring(self) -> np.ndarray:
        r = G.join(*[e.pts for e in self.edges])
        if len(r) > 3 and np.linalg.norm(r[-1] - r[0]) < 1e-6:
            r = r[:-1]
        return r

    def cut_ring(self) -> np.ndarray:
        return G.offset_outline([e.pts for e in self.edges], [e.sa for e in self.edges])

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
                errs.append(f"Lücke {np.linalg.norm(a - b):.1f} mm zwischen "
                            f"'{self.edges[i].name}' und '{self.edges[(i + 1) % n].name}'")
        if G.signed_area(self.seam_ring()) <= 0:
            errs.append("Kontur läuft im Uhrzeigersinn")
        return errs

    def cut_text(self) -> str:
        if self.on_fold:
            if self.cut_count == 1:
                return "1× im Stoffbruch zuschneiden"
            return f"{self.cut_count}× im Stoffbruch zuschneiden"
        if self.cut_count == 2 and self.mirror:
            return "2× gegengleich zuschneiden"
        return f"{self.cut_count}× zuschneiden"

    def sa_text(self) -> str:
        vals = {}
        for e in self.edges:
            if e.fold:
                continue
            vals.setdefault(round(e.sa), []).append(e.label or e.name)
        if not vals:
            return "ohne Nahtzugabe"
        common = max(vals, key=lambda k: len(vals[k]))
        def cm(v):
            return f"{v / 10:.1f}".replace(".", ",")
        parts = [f"Nahtzugabe {cm(common)} cm inkl."]
        for k, names in vals.items():
            if k != common:
                parts.append(f"{', '.join(sorted(set(names)))}: {cm(k)} cm")
        return "; ".join(parts)

    def transformed(self, fn) -> "Piece":
        """Kopie mit allen Punkten durch fn transformiert."""
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
    garment: str                     # Modulname, z. B. pants_basic
    title: str                       # z. B. "Haremshose"
    size_label: str                  # z. B. "Gr. 122"
    pieces: list[Piece]
    measures: dict[str, float]       # Körpermaße in mm
    options: dict[str, Any]
    seams: list[dict] = field(default_factory=list)       # Nahtpaare für Validierung
    corners: list[dict] = field(default_factory=list)     # Winkelprüfungen
    checks: list[dict] = field(default_factory=list)      # weitere Prüfungen (Umfänge …)
    finished: dict[str, float] = field(default_factory=dict)  # Fertigmaße (virtuell genäht)
    notes: list[str] = field(default_factory=list)

    def piece(self, key: str) -> Piece:
        for p in self.pieces:
            if p.key == key:
                return p
        raise KeyError(key)

    def has(self, key: str) -> bool:
        return any(p.key == key for p in self.pieces)

    def edge_len(self, ref: str) -> float:
        """Länge einer Kante, Referenz 'teil.kante' oder 'teil.kante1+kante2'."""
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
        }

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.summary(), f, ensure_ascii=False, indent=2, default=str)


def rect_piece(key: str, name: str, w: float, h: float, *, sa: float = 10.0,
               fold_left: bool = False, fold_bottom: bool = False, cut_count: int = 1,
               fabric: str = "Oberstoff", names=("unten", "rechts", "oben", "links"),
               labels=("", "", "", ""), mirror: bool = False, grain_vertical: bool = True,
               sas=None) -> Piece:
    """Rechteckiges Teil (Bund, Bündchen, Loop …) mit Ursprung unten links."""
    c = [G.P(0, 0), G.P(w, 0), G.P(w, h), G.P(0, h)]
    sas = sas or (sa, sa, sa, sa)
    edges = [
        Edge(names[0], G.line(c[0], c[1]), 0.0 if fold_bottom else sas[0], fold_bottom, labels[0]),
        Edge(names[1], G.line(c[1], c[2]), sas[1], False, labels[1]),
        Edge(names[2], G.line(c[2], c[3]), sas[2], False, labels[2]),
        Edge(names[3], G.line(c[3], c[0]), 0.0 if fold_left else sas[3], fold_left, labels[3]),
    ]
    if grain_vertical:
        grain = (G.P(w * 0.5, h * 0.2), G.P(w * 0.5, h * 0.8)) if h > 60 else (G.P(w * 0.3, h * 0.5), G.P(w * 0.3, h * 0.5 + max(20, h * 0.4)))
    else:
        grain = (G.P(w * 0.2, h * 0.5), G.P(w * 0.8, h * 0.5))
    return Piece(key, name, edges, cut_count=cut_count, mirror=mirror, fabric=fabric, grain=grain)
