"""Fit adjustments from toile feedback (issue #8).

After sewing a test garment people report things like "2 cm too tight at the hip",
"crotch too low", "sleeves 3 cm too long". Two ways to feed that back:

- adjustments: `{"hip": "+2cm", "rise": "-1.5cm"}` (spec `adjustments`, CLI `--adjust`), a
  signed change of a finished measurement;
- fit issues: `{"hip_tight": "2cm", "crotch_low": "1.5cm"}`, translated with `FIT_ISSUES`.

Both are stored in the pattern options (`options.adjustments`), so pattern.json /
project.json keep them and the next run ("same as last time, one size up") applies them
again. Applying works on the module's construction values: the garment is drafted once,
the drafted value is read, and it is drafted again with `value + Δ` as override (or an
option such as the sleeve length). Explicit `construction` overrides win.
"""
from __future__ import annotations

import re

import allowance as A

# adjustment key → ("c", construction value, factor) or ("o", option, finished measurement, factor)
PANTS = {
    "hip": ("c", "hip_width", 1.0, "hip width (circumference)"),
    "seat": ("c", "back_crotch_extension", 0.5, "seat room: back crotch extension (Δ/2 per leg)"),
    "rise": ("c", "rise", 1.0, "front rise / crotch depth"),
    "inseam": ("c", "inseam_finished", 1.0, "leg length (inseam)"),
    "opening": ("c", "hem_width", 1.0, "leg opening (circumference)"),
    "waist": ("o", "elastic_total", "waist_relaxed", 1.0, "elastic length (relaxed waist)"),
}
TOP = {
    "chest": ("c", "chest_width", 1.0, "chest width (circumference)"),
    "length": ("c", "body_length", 1.0, "body length"),
    "armhole": ("c", "armhole_depth", 1.0, "armhole depth"),
    "shoulder": ("c", "shoulder_length", 1.0, "shoulder length"),
    "neckline": ("c", "neck_width_half", 1.0, "neckline width at the shoulder (per side)"),
    "sleeve_length": ("o", "sleeve_len_total", "sleeve_len", 1.0, "sleeve length"),
}
ADJUSTMENTS = {"pants_basic": PANTS, "tshirt_basic": TOP, "hoodie": TOP,
               "dress": {k: v for k, v in TOP.items() if k != "length"}}

# fit issue → (adjustment key, sign)
FIT_ISSUES = {
    "pants_basic": {
        "hip_tight": ("hip", +1), "hip_loose": ("hip", -1), "seat_tight": ("seat", +1),
        "seat_loose": ("seat", -1), "crotch_low": ("rise", -1), "crotch_tight": ("rise", +1),
        "legs_long": ("inseam", -1), "legs_short": ("inseam", +1), "waist_tight": ("waist", +1),
        "waist_loose": ("waist", -1), "opening_tight": ("opening", +1), "opening_wide": ("opening", -1),
    },
    "tshirt_basic": {
        "chest_tight": ("chest", +1), "chest_loose": ("chest", -1), "too_long": ("length", -1),
        "too_short": ("length", +1), "sleeves_long": ("sleeve_length", -1),
        "sleeves_short": ("sleeve_length", +1), "armhole_tight": ("armhole", +1),
        "armhole_low": ("armhole", -1), "shoulders_wide": ("shoulder", -1),
        "shoulders_narrow": ("shoulder", +1), "neckline_gaping": ("neckline", -1),
        "neckline_tight": ("neckline", +1),
    },
}
FIT_ISSUES["hoodie"] = FIT_ISSUES["tshirt_basic"]
FIT_ISSUES["dress"] = {k: v for k, v in FIT_ISSUES["tshirt_basic"].items() if v[0] != "length"}


def parse_delta(v) -> float:
    """'+2cm' / '-15mm' / '1in' / 2 (cm) → mm."""
    if isinstance(v, (int, float)):
        return float(v) * 10
    m = re.fullmatch(r"\s*([+-]?\d+(?:[.,]\d+)?)\s*(mm|cm|in|\"|)\s*", str(v))
    if not m:
        raise ValueError(f"adjustment {v!r} not understood (e.g. '+2cm', '-15mm')")
    x = float(m.group(1).replace(",", "."))
    return x * {"mm": 1.0, "cm": 10.0, "in": 25.4, '"': 25.4, "": 10.0}[m.group(2)]


def resolve(garment: str, adjustments: dict | None) -> dict:
    """Adjustments and fit issues → {adjustment key: Δ mm}."""
    table = ADJUSTMENTS.get(garment, {})
    issues = FIT_ISSUES.get(garment, {})
    out: dict = {}
    for k, v in (adjustments or {}).items():
        if k in issues:
            key, sign = issues[k]
            d = sign * abs(parse_delta(v))
        elif k in table:
            key, d = k, parse_delta(v)
        else:
            known = sorted(set(table) | set(issues))
            raise ValueError(f"unknown adjustment '{k}' for {garment}; known: {', '.join(known) or 'none'}")
        out[key] = out.get(key, 0.0) + d
    return out


def draft(mod, garment: str, measures: dict, options: dict | None):
    """Draft with fit adjustments (options['adjustments']). Returns the pattern; the
    finished measurements before the adjustment are kept in options['_finished_before']."""
    o = dict(options or {})
    deltas = resolve(garment, o.get("adjustments"))
    if not deltas:
        return A.draft(mod, measures, o)
    base = A.draft(mod, measures, o)
    drafted = {r["name"]: r["value"] for r in getattr(base, "construction", []) or []}
    table = ADJUSTMENTS[garment]
    cons = dict(o.get("construction") or {})
    user_cons = set(cons)
    applied = []
    for key, d in deltas.items():
        spec = table[key]
        if spec[0] == "c":
            name, fac = spec[1], spec[2]
            if name in user_cons or name not in drafted:
                continue
            cons[name] = drafted[name] + d * fac
            applied.append((key, d, spec[3]))
        else:
            opt, fin, fac = spec[1], spec[2], spec[3]
            if fin not in base.finished:
                continue
            o[opt] = base.finished[fin] + d * fac
            applied.append((key, d, spec[4]))
    o["construction"] = cons
    pat = A.draft(mod, measures, o)
    # keep only the user's own overrides: the adjustment is re-applied from options['adjustments']
    # on the next run (also in another size), never baked in twice
    pat.options = dict(pat.options)
    pat.options["construction"] = dict(options.get("construction") or {}) if options else {}
    if not pat.options["construction"]:
        pat.options.pop("construction")
    pat.options["_finished_before"] = dict(base.finished)
    pat.options["_adjustments_applied"] = applied
    skipped = sorted(set(deltas) - {a[0] for a in applied})
    if skipped:
        pat.notes.append("Adjustment(s) not applicable to this variant: " + ", ".join(skipped))
    return pat


def markdown(pattern) -> str:
    applied = pattern.options.get("_adjustments_applied") or []
    if not applied:
        return ""
    from i18n import num, t
    rows = ["| " + " | ".join(t(h) for h in ("Adjustment", "Change", "Acts on")) + " |", "|---|---|---|"]
    for key, d, what in applied:
        rows.append(f"| {key} | {num(f'{d / 10:+.1f}')} cm | {t(what)} |")
    return "\n".join(rows)
