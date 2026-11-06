"""Unfold: values measured flat → finished measurements (circumferences, relaxed lengths).

- Double layer: a garment lying flat = 2 layers → circumference = 2 × width.
- Cuffs/elastic waistbands are measured relaxed; the pattern edge they are sewn to is
  longer by the cuff ratio (the garment module computes that).
- For values measured stretched (user input) the stretch is taken out.
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
    # convert circumferences measured stretched (e.g. waistband) back to relaxed
    for k, (val, pct) in st.items():
        t[k] = val / (1 + pct / 100.0)
    return t


def unfold_top(flat: dict) -> dict:
    """Circumferences of a top lying flat (double layer). The lengths stay flat features: the
    fit reconstructs them through the flat-lay model (flatlay.py)."""
    t = dict(chest_circ=2 * flat["chest_flat"], hem_circ=2 * flat["hem_flat"])
    if flat.get("bicep_flat"):
        t["bicep_circ"] = 2 * flat["bicep_flat"]
    if flat.get("opening_flat"):
        t["sleeve_opening"] = 2 * flat["opening_flat"]
    return t


def unfold(garment: str, flat: dict, **kw) -> dict:
    if garment in ("pants", "pants_basic"):
        return unfold_pants(flat, **kw)
    return unfold_top(flat)
