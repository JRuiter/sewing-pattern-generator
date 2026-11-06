"""Abwickeln: flach gemessene Werte → Fertigmaße (Umfänge, entspannte Längen).

- Doppellage: flach liegendes Teil = 2 Lagen → Umfang = 2 × Breite.
- Bündchen/Gummibund werden entspannt gemessen; die Schnittkante, an die sie genäht
  werden, ist um das Bündchenverhältnis länger (das rechnet das Kleidungsmodul).
- Bei gedehnt gemessenen Werten (Nutzerangabe) wird die Dehnung herausgerechnet.
"""
from __future__ import annotations


def unfold_pants(flat: dict, stretched: dict | None = None) -> dict:
    st = stretched or {}
    t = dict(
        hip_circ=2 * flat["hip_flat"],
        thigh_circ=2 * flat["thigh_flat"],
        knee_circ=2 * flat["knee_flat"],
        opening=2 * flat["opening_flat"],
        waist_relaxed=2 * flat["waist_flat"],
        front_rise=flat["front_rise"],
        inseam=flat["inseam"],
        outseam=flat["outseam"],
        waistband_h=flat.get("waistband_h", 0.0),
        cuff_h=flat.get("cuff_h", 0.0),
    )
    # gedehnt gemessene Umfänge (z. B. Bund gedehnt) auf entspannt zurückrechnen
    for k, (val, pct) in st.items():
        t[k] = val / (1 + pct / 100.0)
    return t


def unfold_top(flat: dict) -> dict:
    return dict(chest_circ=2 * flat["chest_flat"], hem_circ=2 * flat["hem_flat"],
                length=flat["length"], sleeve=flat.get("sleeve", 0.0))


def unfold(garment: str, flat: dict, **kw) -> dict:
    if garment in ("hose", "pants", "pants_basic"):
        return unfold_pants(flat, **kw)
    return unfold_top(flat)
