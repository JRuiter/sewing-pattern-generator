"""Metric / imperial units for inputs and reports (issue #13).

Internally everything stays in mm and the pattern files stay 1:1; only texts change.
- `metric`: lengths in cm, fabric in m.
- `imperial`: lengths in inches (fractions of 1/8 in), fabric in yards rounded **up**
  to 1/8 yd, fabric widths in inches.
"""
from __future__ import annotations

import math
from fractions import Fraction

MM_PER_IN = 25.4
MM_PER_YD = 914.4
UNITS = ("metric", "imperial")


def check(units: str | None) -> str:
    u = (units or "metric").lower()
    if u in ("imperial", "inch", "inches", "in", "us", "uk"):
        return "imperial"
    if u in ("metric", "cm", "mm"):
        return "metric"
    raise ValueError(f"units must be one of {', '.join(UNITS)}, got {units!r}")


def of(pattern) -> str:
    opts = pattern.options if isinstance(getattr(pattern, "options", None), dict) else {}
    return check(opts.get("units"))


def inch_text(mm: float, step: int = 8) -> str:
    """mm → inches as a mixed fraction rounded to 1/step in, e.g. 9.5 mm → 3/8"."""
    q = Fraction(round(mm / MM_PER_IN * step), step)
    whole, frac = divmod(q, 1)
    if frac == 0:
        return f'{whole}"'
    if whole == 0:
        return f'{frac.numerator}/{frac.denominator}"'
    return f'{whole} {frac.numerator}/{frac.denominator}"'


def length(mm: float, units: str = "metric", digits: int = 1) -> str:
    """Body/finished measurement or allowance."""
    if check(units) == "imperial":
        return inch_text(mm)
    return _dc(f"{mm / 10:.{digits}f} cm")


def _dc(text: str) -> str:
    """Decimal comma in German output."""
    import i18n
    return text.replace(".", ",") if i18n.is_de() else text


def allowance(mm: float, units: str = "metric") -> str:
    if check(units) == "imperial":
        return inch_text(mm)
    t = f"{mm / 10:.2f}"
    return _dc((t[:-1] if t.endswith("0") else t) + " cm")


def yards(mm: float) -> float:
    """Fabric length in yards, rounded up to 1/8 yd."""
    return math.ceil(mm / MM_PER_YD * 8 - 1e-9) / 8


def fabric_length(mm: float, units: str = "metric") -> str:
    if check(units) == "imperial":
        y = Fraction(int(round(yards(mm) * 8)), 8)
        whole, frac = divmod(y, 1)
        if frac == 0:
            return f"{whole} yd"
        return (f"{whole} " if whole else "") + f"{frac.numerator}/{frac.denominator} yd"
    return _dc(f"{mm / 1000:.2f} m")


def fabric_width(mm: float, units: str = "metric") -> str:
    if check(units) == "imperial":
        return f'{mm / MM_PER_IN:.0f}"'
    return f"{mm / 10:.0f} cm"


def to_cm(values: dict | None, units: str = "metric") -> dict | None:
    """User measurements in the given units → cm (the unit of `measures_cm`)."""
    if values is None or check(units) == "metric":
        return values
    return {k: float(v) * 2.54 for k, v in values.items()}
