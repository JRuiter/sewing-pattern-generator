"""Common practice: target ranges that a pattern's defaults must meet.

The drafting formulas in the garment modules aim at these values; the checks below compare the
result with the same table, so a default that drifts away from current ready-to-wear and
pattern-making practice shows up in the validation report as a warning ("Common practice"),
even when the pattern is sewable. Anything special (a deep scoop neck, a cropped length) has to
come from an explicit option; the report then names it as intended.

The ranges are guide values from pattern-making textbooks and ready-to-wear measurements
(fractions of the body measurement or mm). Change the table, not the code, to retune them.
"""
from __future__ import annotations

GROUP = "Common practice"

# chest ease of tops, fraction of the chest (knits; woven: + WOVEN_EXTRA)
TOP_CHEST_EASE = {
    "slim": (-0.12, 0.08), "normal": (0.05, 0.18), "wide": (0.14, 0.28),
    "oversized": (0.30, 0.48), "boxy": (0.34, 0.55), "harem": (0.14, 0.28),
}
# hip ease of pants and skirts, fraction of the hip (knits; woven: + WOVEN_EXTRA)
HIP_EASE = {
    "slim": (-0.15, 0.08), "normal": (0.05, 0.18), "wide": (0.14, 0.28),
    "oversized": (0.20, 0.36), "boxy": (0.20, 0.36), "harem": (0.25, 0.45),
}
WOVEN_EXTRA = 0.06

# crew neck: front drop as a multiple of the half neck width (V-neck and options excluded)
CREW_DEPTH_REL = (0.80, 1.10)
# half neck width: neck / 5 + this many mm
NECK_WIDTH_PLUS = (5.0, 30.0)
# sleeve cap height relative to the highest cap that suits the shoulder (tshirt_basic.cap_height_max)
CAP_REL = (0.55, 1.05)


def _ease_range(table: dict, fit: str, knit: bool) -> tuple[float, float]:
    lo, hi = table.get(fit, table["normal"])
    return (lo, hi) if knit else (lo + WOVEN_EXTRA, hi + WOVEN_EXTRA)


def _rng(name, value, lo, hi, note="", unit=None) -> dict:
    d = dict(name=name, kind="range", value=value, lo=lo, hi=hi, note=note, group=GROUP)
    if unit:
        d["unit"] = unit
    return d


def top_checks(o: dict, m: dict, F: dict, knit: bool, cap_height: float | None = None,
               cap_max: float | None = None) -> list[dict]:
    """Checks for tops (T-shirt, sweater, hoodie, dress bodice)."""
    out = []
    if not o.get("chest_total") and not (o.get("construction") or {}).get("chest_width"):
        lo, hi = _ease_range(TOP_CHEST_EASE, o["fit"], knit)
        out.append(_rng(f"Chest ease for fit '{o['fit']}'", F["Ct"] / m["chest"] - 1, lo, hi,
                        "guide value for this fit", unit="%"))
    special_neck = o.get("neckline") == "v" or (o.get("neck_extra") and not o.get("_auto_neck")) or \
        any(k in (o.get("construction") or {}) for k in ("front_neck_depth", "neck_width_half"))
    if not special_neck:
        lo, hi = CREW_DEPTH_REL
        out.append(_rng("Crew neck depth (front)", F["fnd"], lo * F["nw"], hi * F["nw"],
                        "about as deep as the half neck width"))
        lo, hi = NECK_WIDTH_PLUS
        out.append(_rng("Neck width (half)", F["nw"], m["neck"] / 5 + lo, m["neck"] / 5 + hi,
                        "neck / 5 + 0.5 to 3 cm"))
    if cap_height is not None and cap_max:
        lo, hi = CAP_REL
        out.append(_rng("Sleeve cap height for this shoulder", cap_height, lo * cap_max, hi * cap_max,
                        "lower cap for a dropped shoulder"))
    return out


def hip_checks(o: dict, m: dict, hip_total: float, knit: bool) -> list[dict]:
    """Checks for pants and skirts."""
    lo, hi = _ease_range(HIP_EASE, o["fit"], knit)
    return [_rng(f"Hip ease for fit '{o['fit']}'", hip_total / m["hip"] - 1, lo, hi,
                 "guide value for this fit", unit="%")]
