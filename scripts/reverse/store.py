"""Projekt speichern/laden (Teilegraph + Parameter + Messwerte) und Gradieren.

„Wie das Teil vom letzten Mal, aber 2 Größen größer“: Die gemessenen Fertigmaße werden
mit den Differenzen der Körpermaße zwischen den Größen fortgeschrieben (Gradierregeln
je Größensprung) – nicht linear vergrößert.
"""
from __future__ import annotations

import json
import os
from datetime import date

import measurements as M

KIDS_SIZES = sorted(M.KIDS_TABLE)


def save(path: str, project: dict) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    data = dict(project)
    data.setdefault("gespeichert", date.today().isoformat())
    data.pop("pattern", None)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=float)
    return path


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def size_step(size: float, steps: int) -> float:
    """Kindergrößen springen in 6-cm-Schritten."""
    s = min(KIDS_SIZES, key=lambda k: abs(k - size))
    i = KIDS_SIZES.index(s) + steps
    i = max(0, min(len(KIDS_SIZES) - 1, i))
    return float(KIDS_SIZES[i])


# Gradierregeln Hose: Fertigmaß ← Körpermaß-Differenz × Faktor
PANTS_RULES = {
    "hip_circ": ("hip", None),          # Faktor = Mehrweite des Originals (Hc / Hüfte)
    "thigh_circ": ("thigh", None),
    "waist_relaxed": ("waist", 0.9),
    "opening": ("ankle", 1.12),
    "front_rise": ("crotch_depth", 1.0),
    "inseam": ("inseam", 1.0),
    "outseam": ("side_length", 1.0),
}


def grade_targets(targets: dict, src_size: float, dst_size: float) -> dict:
    a = M.size_measures(src_size)
    b = M.size_measures(dst_size)
    out = dict(targets)
    for k, (body, fac) in PANTS_RULES.items():
        if k not in targets:
            continue
        f = fac if fac is not None else targets[k] / a[body]
        out[k] = targets[k] + (b[body] - a[body]) * f
    # Bund-/Bündchenhöhe: leicht mit der Körperhöhe
    r = b["height"] / a["height"]
    for k in ("waistband_h", "cuff_h"):
        if targets.get(k):
            out[k] = targets[k] * (1 + (r - 1) * 0.5)
    return out
