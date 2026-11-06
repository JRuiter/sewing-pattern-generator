"""User-defined seam and hem allowances (issue #1).

Options (spec `options` or CLI):
- `seam_allowance_mm`: seam allowance for all seams (garment default otherwise, usually 10 mm).
- `hem_allowance_mm`: allowance of hems that are turned up (garment default otherwise).
- `seam_allowance: "none"` (or `seam_allowance_mm: 0`): pattern **without** allowances. Only
  the seam line is drawn; the labels and instructions list what to add when cutting.

The values are mapped onto the module options `sa` / `hem_sa` before drafting. Construction
allowances that are part of the design (elastic casings, facings, the narrow hem of a circle
skirt) stay as drafted unless the pattern has no allowances at all. Fold edges stay at 0.
"""
from __future__ import annotations

SEAM_RANGE = (0.0, 30.0)
HEM_RANGE = (0.0, 60.0)


def _num(v, what, rng) -> float:
    try:
        x = float(str(v).lower().replace("mm", "").strip())
    except ValueError:
        raise ValueError(f"{what} must be a number in mm, got {v!r}") from None
    if not rng[0] <= x <= rng[1]:
        raise ValueError(f"{what} must be between {rng[0]:g} and {rng[1]:g} mm, got {x:g}")
    return x


def no_allowance(options: dict) -> bool:
    o = options or {}
    if str(o.get("seam_allowance", "")).lower() in ("none", "0", "no", "false"):
        return True
    v = o.get("seam_allowance_mm")
    return v is not None and _num(v, "seam_allowance_mm", SEAM_RANGE) == 0


def module_options(options: dict | None) -> dict:
    """Options for the garment module: seam_allowance_mm/hem_allowance_mm → sa/hem_sa."""
    o = dict(options or {})
    if no_allowance(o):
        # draft with the default allowances; they are recorded as hints and then removed
        o.pop("seam_allowance_mm", None)
        o.pop("hem_allowance_mm", None)
        o["seam_allowance"] = "none"
        return o
    if o.get("seam_allowance_mm") is not None:
        o["sa"] = _num(o["seam_allowance_mm"], "seam_allowance_mm", SEAM_RANGE)
    if o.get("hem_allowance_mm") is not None:
        o["hem_sa"] = _num(o["hem_allowance_mm"], "hem_allowance_mm", HEM_RANGE)
    return o


def strip(pattern) -> None:
    """Remove all allowances (pattern without seam allowance) and keep them as hints."""
    for piece in pattern.pieces:
        for e in piece.edges:
            if not e.fold:
                e.sa_hint, e.sa = e.sa, 0.0
    pattern.options["seam_allowance"] = "none"
    pattern.notes.append("The pattern has NO seam allowance: add the allowances listed on each piece "
                         "when you cut (mark them with chalk or a seam gauge).")


def draft(mod, measures: dict, options: dict | None):
    """Draft with the user's allowance options."""
    o = module_options(options)
    pat = mod.draft(measures, o)
    if no_allowance(o):
        strip(pat)
    return pat


def has_allowance(pattern) -> bool:
    return str(pattern.options.get("seam_allowance", "")).lower() != "none"
