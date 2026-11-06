"""Zerlegen: Teile- und Nahtgraph aus erkannten Merkmalen ableiten.

Knoten = Schnittteile (mit Zuschnitt/Bruch), Kanten = Nähte mit Partnerkanten,
z. B. „Vorderhose.Seitennaht ↔ Hinterhose.Seitennaht“.
"""
from __future__ import annotations

import measurements as M
from garments import get


def features_from_measurement(garment: str, meas_mm: dict) -> dict:
    """Merkmale, die aus der Vermessung selbst folgen (Bund, Bündchen …)."""
    if garment in ("hose", "pants", "pants_basic"):
        return dict(module="pants_basic", waistband=meas_mm.get("waistband_h", 0) > 5,
                    cuffs=meas_mm.get("cuff_h", 0) > 10, pockets=[])
    return dict(module="tshirt_basic")


def options_from_features(feat: dict) -> dict:
    if feat["module"] == "pants_basic":
        return dict(style="jogginghose", waistband="bund_gummi" if feat.get("waistband") else "tunnel",
                    cuffs=bool(feat.get("cuffs")), pockets=list(feat.get("pockets", [])),
                    fabric=feat.get("fabric", "sweat"))
    return dict(feat.get("options", {}))


def graph_from_pattern(pat) -> dict:
    nodes = []
    for p in pat.pieces:
        nodes.append(dict(id=p.key, name=p.name, cut=p.cut_text(), fabric=p.fabric,
                          im_bruch=p.on_fold, kanten=[e.label or e.name for e in p.edges]))
    edges = []
    for s in pat.seams:
        a = " + ".join(f"{pat.piece(k).name}.{pat.piece(k).edge(e).label or e}" for k, e, _ in s["a"])
        b = " + ".join(f"{pat.piece(k).name}.{pat.piece(k).edge(e).label or e}" for k, e, _ in s["b"])
        edges.append(dict(naht=s["name"], a=a, b=b, art=s.get("type", "equal")))
    return dict(teile=nodes, naehte=edges)


def decompose(feat: dict, size_hint=122) -> dict:
    """Teilegraph für die erkannten Merkmale (mit Standardmaßen konstruiert)."""
    mod = get(feat["module"])
    opts = options_from_features(feat)
    pat = mod.draft(M.size_measures(size_hint), opts)
    g = graph_from_pattern(pat)
    g["modul"] = feat["module"]
    g["optionen"] = opts
    g["fehlende_fotos"] = missing_photos(feat)
    return g


def missing_photos(feat: dict) -> list[str]:
    if feat["module"] == "pants_basic":
        return ["Optional für eine genauere Schrittkurve: ein Hosenbein nach innen falten, sodass die "
                "vordere und hintere Schrittnaht flach liegen, und von oben fotografieren (mit Karte).",
                "Rückseite flach fotografieren, falls hinten Taschen/Passen sind."]
    return ["Ärmel herausklappen und das Armloch flach fotografieren."]


def describe(g: dict) -> str:
    lines = ["**Teile:**"]
    for n in g["teile"]:
        lines.append(f"- {n['name']} – {n['cut']}" + (" (im Bruch)" if n["im_bruch"] else ""))
    lines.append("**Nähte:**")
    for e in g["naehte"]:
        lines.append(f"- {e['naht']}: {e['a']} ↔ {e['b']}")
    return "\n".join(lines)
