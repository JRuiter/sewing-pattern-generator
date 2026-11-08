"""Ease (wearing allowance) per fit × fabric × stretch.

All values as a fraction of the body circumference (e.g. 0.10 = 10 % ease). Negative
values mean negative ease (leggings, close-fitting stretch jersey).
"""
from __future__ import annotations

FABRICS = {
    # name: (display name, typical crosswise stretch %, is_knit)
    "woven": ("Woven", 0, False),
    "jersey": ("Jersey", 40, True),
    "jersey_elastane": ("Jersey with elastane", 60, True),
    "interlock": ("Interlock", 35, True),
    "sweat": ("Sweat / French Terry", 25, True),
    "fleece": ("Fleece", 20, True),
    "rib": ("Rib knit", 80, True),
    "corduroy": ("Corduroy", 0, False),
    "velvet": ("Velvet", 0, False),
    "softshell": ("Softshell", 10, False),
}

# fabrics with a nap or pile: all pieces must point the same way on the fabric
NAP_FABRICS = ("corduroy", "velvet")

PRESS_NOTES = {
    "sweat": " with steam; do not press down hard on sweat.",
    "fleece": ": fleece only with a cool iron through a cloth, or not at all.",
    "corduroy": " from the wrong side on a terry towel; do not press down hard (the pile goes flat).",
    "velvet": " from the wrong side on a terry towel; do not press down hard (the pile goes flat).",
}

FIT_LABELS = {"slim": "slim / close-fitting", "normal": "normal", "wide": "wide",
              "oversized": "oversized", "boxy": "boxy",
              "harem": "harem (wide, dropped crotch)"}

# Base ease table as a fraction of the body circumference at 0 % stretch (woven) and
# for typical knits (≈ 30 % stretch)
_BODY = {  # tops: chest
    "slim": (0.06, 0.00), "normal": (0.14, 0.09), "wide": (0.22, 0.17),
    "oversized": (0.40, 0.35), "boxy": (0.44, 0.40), "harem": (0.22, 0.17),
}
_HIP = {  # pants/skirts: hip
    "slim": (0.06, 0.00), "normal": (0.14, 0.10), "wide": (0.22, 0.18),
    "oversized": (0.30, 0.26), "boxy": (0.30, 0.26), "harem": (0.34, 0.30),
}


def fabric_info(fabric: str, stretch: float | None = None):
    if fabric not in FABRICS:
        raise ValueError(f"Unknown fabric '{fabric}'. Allowed: {', '.join(FABRICS)}")
    label, default_stretch, knit = FABRICS[fabric]
    s = default_stretch if stretch is None else float(stretch)
    return label, s, knit


def _interp(table, fit, stretch, knit):
    woven, knitv = table[fit]
    if not knit:
        return woven
    # above 30 % stretch: 1 % less ease per additional 10 % stretch
    return knitv - max(stretch - 30, 0) * 0.001


def has_nap(options: dict | None) -> bool:
    """Does the main fabric have a nap (option `nap`, default from the fabric)?"""
    o = options or {}
    if o.get("nap") is not None:
        return bool(o["nap"])
    return o.get("fabric") in NAP_FABRICS


def press_note(fabric: str | None) -> str:
    """How to press the finished garment (appended to "Press all seams")."""
    if fabric in PRESS_NOTES:
        return PRESS_NOTES[fabric]
    return " with steam." if fabric and fabric_info(fabric)[2] else "."


def body_ease(fit: str, fabric: str, stretch: float | None = None) -> float:
    """Chest ease (fraction)."""
    _, s, knit = fabric_info(fabric, stretch)
    if fit == "slim" and knit and s >= 40:
        return -min(0.10, (s - 30) * 0.002)       # slightly negative
    return _interp(_BODY, fit, s, knit)


def hip_ease(fit: str, fabric: str, stretch: float | None = None) -> float:
    """Hip ease (fraction). Leggings: negative ease."""
    _, s, knit = fabric_info(fabric, stretch)
    if fit == "slim":
        if not knit or s < 30:
            # close-fitting in low-stretch fabric: only a little ease
            return 0.06 if not knit else 0.02
        return -min(0.12, 0.04 + (s - 30) * 0.0015)   # 50 % → −7 %, 80 % → −11.5 %
    return _interp(_HIP, fit, s, knit)


def rise_ease_mm(fit: str, adult: bool) -> float:
    """Rise ease (sitting room) in mm."""
    base = 20.0 if adult else 15.0
    return {"slim": base * 0.25, "normal": base, "wide": base * 1.3,
            "oversized": base * 1.6, "boxy": base * 1.6, "harem": base * 1.3}[fit]


def band_ratio(band_fabric: str, stretch: float | None = None, use: str = "neck") -> float:
    """Length of a rib band / neckband relative to the edge it is sewn to.

    use="hem": a hem band only hugs the body lightly (it has to go over the hips and should not
    balloon the garment), so it is longer than a neckband or a cuff."""
    _, s, _ = fabric_info(band_fabric, stretch)
    if use == "hem":
        if band_fabric == "rib":
            return max(0.80, min(0.90, 0.90 - (s - 50) * 0.003))   # 50 % → 0.90; 80 % → 0.81
        return max(0.85, min(0.95, 0.95 - (s - 30) * 0.003))
    if band_fabric == "rib":
        return max(0.70, min(0.85, 0.85 - (s - 50) * 0.005))     # 50 % → 0.85; 80 % → 0.70
    return max(0.80, min(0.92, 0.92 - (s - 30) * 0.004))          # jersey strip


def band_ratio_range(band_fabric: str, use: str = "neck") -> tuple[float, float]:
    if use == "hem":
        return (0.78, 0.92) if band_fabric == "rib" else (0.83, 0.97)
    return (0.70, 0.85) if band_fabric == "rib" else (0.80, 0.92)


def cap_ease_range_mm(fabric: str) -> tuple[float, float]:
    """Plausible sleeve-cap ease relative to the armhole."""
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
    from i18n import t
    label, s, _ = fabric_info(fabric, stretch)
    fabric_txt = f"{t(label)} (" + t(f"{s:.0f} % stretch") + ")"
    if fit is None:                                  # accessories: no fit
        return fabric_txt
    return t(f"{FIT_LABELS.get(fit, fit)} fit") + ", " + fabric_txt
