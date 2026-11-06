"""Decompose: derive the piece and seam graph from the detected features.

Nodes = pattern pieces (with cutting/fold), edges = seams with their partner edges,
e.g. "Front.Side seam ↔ Back.Side seam".
"""
from __future__ import annotations

import measurements as M
from garments import get


def features_from_measurement(garment: str, meas_mm: dict) -> dict:
    """Features that follow from the measurement itself (waistband, cuffs …)."""
    if garment in ("pants", "pants_basic"):
        return dict(module="pants_basic", waistband=meas_mm.get("waistband_h", 0) > 5,
                    cuffs=meas_mm.get("cuff_h", 0) > 10, pockets=[])
    return dict(module="tshirt_basic")


def options_from_features(feat: dict) -> dict:
    if feat["module"] == "pants_basic":
        return dict(style="jogger", waistband="casing" if feat.get("waistband") else "tunnel",
                    cuffs=bool(feat.get("cuffs")), pockets=list(feat.get("pockets", [])),
                    fabric=feat.get("fabric", "sweat"))
    return dict(feat.get("options", {}))


def graph_from_pattern(pat) -> dict:
    nodes = []
    for p in pat.pieces:
        nodes.append(dict(id=p.key, name=p.name, cut=p.cut_text(), fabric=p.fabric,
                          on_fold=p.on_fold, edges=[e.label or e.name for e in p.edges]))
    edges = []
    for s in pat.seams:
        a = " + ".join(f"{pat.piece(k).name}.{pat.piece(k).edge(e).label or e}" for k, e, _ in s["a"])
        b = " + ".join(f"{pat.piece(k).name}.{pat.piece(k).edge(e).label or e}" for k, e, _ in s["b"])
        edges.append(dict(seam=s["name"], a=a, b=b, type=s.get("type", "equal")))
    return dict(pieces=nodes, seams=edges)


def decompose(feat: dict, size_hint=122) -> dict:
    """Piece graph for the detected features (drafted with standard measurements)."""
    mod = get(feat["module"])
    opts = options_from_features(feat)
    pat = mod.draft(M.size_measures(size_hint), opts)
    g = graph_from_pattern(pat)
    g["module"] = feat["module"]
    g["options"] = opts
    g["missing_photos"] = missing_photos(feat)
    return g


def missing_photos(feat: dict) -> list[str]:
    if feat["module"] == "pants_basic":
        return ["Optional, for a more accurate crotch curve: fold one leg inwards so that the "
                "front and back crotch seams lie flat, and photograph from above (with the card).",
                "Photograph the back flat too if there are pockets/yokes at the back."]
    return ["Fold the sleeve out and photograph the armhole flat."]


def describe(g: dict) -> str:
    lines = ["**Pieces:**"]
    for n in g["pieces"]:
        lines.append(f"- {n['name']}: {n['cut']}" + (" (on fold)" if n["on_fold"] else ""))
    lines.append("**Seams:**")
    for e in g["seams"]:
        lines.append(f"- {e['seam']}: {e['a']} ↔ {e['b']}")
    return "\n".join(lines)
