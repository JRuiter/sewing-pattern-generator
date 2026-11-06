"""Mehrweite (Bequemlichkeitszugabe) je Passform × Stoff × Dehnbarkeit.

Alle Werte als Anteil des Körperumfangs (z. B. 0.10 = 10 % Mehrweite). Negative Werte
bedeuten negative Mehrweite (Leggings, figurnah aus elastischem Jersey).
"""
from __future__ import annotations

FABRICS = {
    # name: (Anzeigename, typische Querdehnung %, ist_maschenware)
    "webware": ("Webware", 0, False),
    "jersey": ("Jersey", 40, True),
    "jersey_elastan": ("Jersey mit Elasthan", 60, True),
    "interlock": ("Interlock", 35, True),
    "sweat": ("Sweat / French Terry", 25, True),
    "fleece": ("Fleece", 20, True),
    "buendchen": ("Bündchen", 80, True),
}

FIT_LABELS = {"eng": "eng / figurnah", "normal": "normal", "weit": "weit",
              "oversized": "oversized", "harem": "Harem (weit, tiefer Schritt)"}

# Basistabelle Mehrweite in % des Körperumfangs bei Dehnung 0 (Webware) und bei
# typischer Maschenware (≈ 30 % Dehnung)
_BODY = {  # Oberteile: Brust
    "eng": (0.06, 0.00), "normal": (0.14, 0.09), "weit": (0.22, 0.17),
    "oversized": (0.32, 0.27), "harem": (0.22, 0.17),
}
_HIP = {  # Hosen/Röcke: Hüfte
    "eng": (0.06, 0.00), "normal": (0.14, 0.10), "weit": (0.22, 0.18),
    "oversized": (0.30, 0.26), "harem": (0.34, 0.30),
}


def fabric_info(fabric: str, stretch: float | None = None):
    if fabric not in FABRICS:
        raise ValueError(f"Unbekannter Stoff '{fabric}'. Erlaubt: {', '.join(FABRICS)}")
    label, default_stretch, knit = FABRICS[fabric]
    s = default_stretch if stretch is None else float(stretch)
    return label, s, knit


def _interp(table, fit, stretch, knit):
    woven, knitv = table[fit]
    if not knit:
        return woven
    # oberhalb 30 % Dehnung je 10 % zusätzlicher Dehnung 1 % weniger Mehrweite
    return knitv - max(stretch - 30, 0) * 0.001


def body_ease(fit: str, fabric: str, stretch: float | None = None) -> float:
    """Mehrweite Brustumfang (Anteil)."""
    _, s, knit = fabric_info(fabric, stretch)
    if fit == "eng" and knit and s >= 40:
        return -min(0.10, (s - 30) * 0.002)       # leicht negativ
    return _interp(_BODY, fit, s, knit)


def hip_ease(fit: str, fabric: str, stretch: float | None = None) -> float:
    """Mehrweite Hüftumfang (Anteil). Leggings: negative Mehrweite."""
    _, s, knit = fabric_info(fabric, stretch)
    if fit == "eng":
        if not knit or s < 30:
            # figurnah aus wenig dehnbarem Stoff: nur geringe Mehrweite
            return 0.06 if not knit else 0.02
        return -min(0.12, 0.04 + (s - 30) * 0.0015)   # 50 % → −7 %, 80 % → −11,5 %
    return _interp(_HIP, fit, s, knit)


def rise_ease_mm(fit: str, adult: bool) -> float:
    """Zugabe zur Leibhöhe (Sitzfreiheit) in mm."""
    base = 20.0 if adult else 15.0
    return {"eng": base * 0.25, "normal": base, "weit": base * 1.3,
            "oversized": base * 1.6, "harem": base * 1.3}[fit]


def band_ratio(band_fabric: str, stretch: float | None = None) -> float:
    """Länge eines Bündchens / Halsbündchens im Verhältnis zur Ansatzkante."""
    _, s, _ = fabric_info(band_fabric, stretch)
    if band_fabric == "buendchen":
        return max(0.70, min(0.85, 0.85 - (s - 50) * 0.005))     # 50 % → 0,85; 80 % → 0,70
    return max(0.80, min(0.92, 0.92 - (s - 30) * 0.004))          # Jersey-Streifen


def band_ratio_range(band_fabric: str) -> tuple[float, float]:
    return (0.70, 0.85) if band_fabric == "buendchen" else (0.80, 0.92)


def cap_ease_range_mm(fabric: str) -> tuple[float, float]:
    """Plausible Einhaltemenge Ärmelkugel gegenüber Armloch."""
    _, _, knit = fabric_info(fabric)
    if not knit:
        return (10.0, 25.0)
    if fabric in ("sweat", "fleece"):
        return (0.0, 8.0)
    return (0.0, 5.0)


def cap_ease_target_mm(fabric: str) -> float:
    lo, hi = cap_ease_range_mm(fabric)
    return lo + (hi - lo) * 0.4


def describe(fit: str, fabric: str, stretch: float | None = None) -> str:
    label, s, _ = fabric_info(fabric, stretch)
    return f"Passform {FIT_LABELS.get(fit, fit)}, {label} ({s:.0f} % Dehnung)"
