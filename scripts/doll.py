"""Doll clothes mode: patterns for fabric dolls, soft toys and fashion dolls.

Dolls are not small children: they have no size table, a big head, short stiff arms and
legs, and their clothes need narrow seam allowances (6 mm instead of 1 cm) and an
opening at the back, because a stuffed doll head rarely fits through a neckline.

How it works
- Measurements come from the user (tape measure or string around the doll), in cm.
  Only the body height is required; everything else is filled in from typical fabric-doll
  proportions and follows the circumferences that were given (`complete_measures`).
- The garment modules are drafted at a **virtual scale**: the doll is enlarged to the
  leg length of a child of about size 110 (all measurements × S), drafted with the
  normal module (all drafting rules, curves and minimum lengths apply proportionally),
  and the finished pattern is scaled back by 1/S. Seam and hem allowances are passed in
  at × S, so after scaling they are exactly the doll allowances (default 6 mm / 10 mm).
  Validation runs on the scaled-back pattern, so every check is in real doll millimetres.
- Doll defaults: woven fabric, wide fit (stiff arms), back opening with Velcro/snaps and
  a bias-bound neckline for tops and dresses, no pockets or rib cuffs, a narrow elastic
  casing for pants and skirts. Every default can be overridden by an option.

Supported garments: `dress`, `skirt`, `pants_basic`, `tshirt_basic`.
"""
from __future__ import annotations

import copy
import re

import adjust as ADJ

SUPPORTED = ("dress", "skirt", "pants_basic", "tshirt_basic")
DOLL_SA_MM = 6.0          # seam allowance
DOLL_HEM_MM = 10.0        # turned-up hems
DOLL_ELASTIC_MM = 6.0     # elastic width for casings
SMALL_DOLL_MM = 300.0     # below this height (fashion dolls, mini dolls):
DOLL_SA_SMALL_MM = 5.0    # … seam allowance
DOLL_HEM_SMALL_MM = 8.0   # … hem allowance
HEIGHT_RANGE_CM = (20.0, 100.0)
ARMHOLE_MAX_BACK = 0.70   # deepest armhole as a share of the back length

# Virtual drafting scale: the doll's side length (waist to floor) is enlarged to that of a
# child of size 110; the module "height" is the matching child height.
VIRTUAL_SIDE_MM = 650.0
VIRTUAL_HEIGHT_MM = 1100.0

# Typical fabric (rag/Waldorf-style) doll, as a fraction of the body height. Rounded from
# measurements of 30–55 cm cloth dolls; only used for measurements the user did not give.
PROPORTIONS = {
    "chest": 0.62, "waist": 0.60, "hip": 0.66, "head": 0.72, "neck": 0.32,
    "inseam": 0.28, "side_length": 0.44, "arm": 0.27, "back_length": 0.20, "shoulder": 0.07,
    "upper_arm": 0.22, "wrist": 0.16, "thigh": 0.38, "knee": 0.30, "ankle": 0.24,
}
CIRCUMFERENCES = ("chest", "waist", "hip", "neck", "upper_arm", "wrist", "thigh", "knee", "ankle")

# options in mm (or cm) that describe lengths: scaled with the pattern
LENGTH_OPTIONS = (
    "sa", "hem_sa", "seam_allowance_mm", "hem_allowance_mm", "opening_sa", "neck_band_h",
    "chest_total", "body_length", "sleeve_len_total", "sleeve_opening", "neck_extra", "cuff_h",
    "hem_band_h", "bicep_total", "hem_total", "waistband_height", "cuff_height", "elastic_width",
    "crotch_drop", "blouse", "hip_total", "front_rise_total", "inseam_total", "opening_total",
    "elastic_total", "knee_total", "thigh_total", "top_total", "skirt_length", "flare_cm", "turn_up",
    "armhole_depth_max",
)
# private (computed) option values that are not lengths
NOT_LENGTHS = {"be", "stretch", "knit", "_auto_neck", "units", "fork_factor", "gather"}
NON_MM_CONSTRUCTION = {"shoulder_slope"}


def is_doll(spec: dict) -> bool:
    s = spec.get("size")
    return bool(spec.get("doll")) or (isinstance(s, str) and s.strip().lower().startswith("doll"))


def size_label(measures_mm: dict) -> str:
    return f"doll {measures_mm['height'] / 10:.0f} cm (made to measure)"


# ---------------------------------------------------------------------------- measurements

def complete_measures(given_cm: dict | None):
    """Doll measurements (cm) → (measures_mm, source). Body height is required."""
    import measurements as M
    g = M.normalize_keys(given_cm or {})
    if "height" not in g:
        raise ValueError(
            "Doll mode needs at least the doll's height (head to feet, cm). Better: also chest, waist, "
            "hip, head, arm length (shoulder to wrist), inseam and side length (waist to the soles), "
            "measured with a tape or a string around the doll.")
    h = g["height"]
    lo, hi = HEIGHT_RANGE_CM
    if not lo <= h <= hi:
        raise ValueError(f"Doll height {h:g} cm is outside the supported range {lo:g}–{hi:g} cm")
    base = {k: f * h for k, f in PROPORTIONS.items()}
    src = {k: "derived" for k in base}
    base["height"], src["height"] = h, "user"
    # circumferences the user did not give follow the ones they did give (chunky or slim doll)
    ref = [g[k] / base[k] for k in ("chest", "waist", "hip") if k in g]
    if ref:
        f = sum(ref) / len(ref)
        for k in CIRCUMFERENCES:
            if k not in g:
                base[k] *= f
    if "inseam" in g and "side_length" not in g:
        base["side_length"] = g["inseam"] + (PROPORTIONS["side_length"] - PROPORTIONS["inseam"]) * h
    if "side_length" in g and "inseam" not in g:
        base["inseam"] = g["side_length"] - (PROPORTIONS["side_length"] - PROPORTIONS["inseam"]) * h
    for k, v in g.items():
        base[k] = v
        src[k] = "user"
    if "crotch_depth" in g:
        if "side_length" not in g:
            base["side_length"] = base["inseam"] + g["crotch_depth"]
        elif "inseam" not in g:
            base["inseam"] = base["side_length"] - g["crotch_depth"]
    base["crotch_depth"] = base["side_length"] - base["inseam"]
    src.setdefault("crotch_depth", "derived")
    return {k: v * 10 for k, v in base.items()}, src


def validate_measures(m: dict) -> list[str]:
    """Plausibility warnings for doll measurements (mm)."""
    w = []
    h = m["height"]
    if m["side_length"] <= m["inseam"] + 0.03 * h:
        w.append("Side length must be clearly longer than the inseam (side length = waist to soles, "
                 "inseam = crotch to soles); please measure again")
    if not 0.25 <= m["side_length"] / h <= 0.65:
        w.append(f"Side length {m['side_length'] / 10:.1f} cm looks unusual for a doll of {h / 10:.0f} cm")
    if not 0.30 <= m["chest"] / h <= 1.20:
        w.append(f"Chest {m['chest'] / 10:.1f} cm looks unusual for a doll of {h / 10:.0f} cm")
    if m["hip"] < m["waist"] * 0.8 or m["waist"] > m["chest"] * 1.4:
        w.append("Waist, hip and chest do not fit together, please measure again")
    if m["head"] > m["chest"] * 1.6:
        w.append("The head is much bigger than the chest: tops and dresses get a back opening anyway, "
                 "pants and skirts are pulled on over the feet")
    return w


# ---------------------------------------------------------------------------- options

def defaults(garment: str, options: dict | None, measures_mm: dict | None = None) -> dict:
    """Doll defaults for a garment; explicit options win. measures in mm."""
    if garment not in SUPPORTED:
        raise ValueError(f"Doll mode supports {', '.join(SUPPORTED)}; not '{garment}'")
    import ease as E
    o = dict(options or {})
    o.setdefault("fabric", "woven")
    if garment in ("tshirt_basic", "dress"):
        o.setdefault("fit", "wide")               # doll arms do not bend: room to dress them
        o.setdefault("back_opening", True)
        knit = E.fabric_info(o["fabric"], o.get("stretch"))[2]
        o.setdefault("neck_finish", "band" if knit else "bias")
        o.setdefault("pockets", False)
        o.setdefault("sleeve_cuffs", False)
        if garment == "dress":
            o.setdefault("waist_elastic", False)     # the back opening makes it unnecessary
        # doll arms are cylinders: (nearly) straight short sleeves
        o.setdefault("sleeve_taper", 0.97 if o.get("sleeve_style") == "raglan" else 1.0)
        if measures_mm:
            # dolls are short in the body: the underarm stays well above the waist, and the
            # stuffed arm needs less ease than a child's arm (it does not bend)
            o.setdefault("armhole_depth_max", ARMHOLE_MAX_BACK * measures_mm["back_length"])
            o.setdefault("bicep_total", measures_mm["upper_arm"] * (1.10 if knit else 1.20))
    if garment == "pants_basic":
        o.setdefault("style", "trousers")
        o.setdefault("fit", "wide")
        o.setdefault("pockets", [])
        o.setdefault("cuffs", False)
        o.setdefault("waistband", "tunnel")
        o.setdefault("elastic_width", DOLL_ELASTIC_MM)
    if str(o.get("seam_allowance", "")).lower() not in ("none", "0", "no", "false"):
        small = bool(measures_mm) and measures_mm["height"] < SMALL_DOLL_MM
        o.setdefault("seam_allowance_mm", DOLL_SA_SMALL_MM if small else DOLL_SA_MM)
        o.setdefault("hem_allowance_mm", DOLL_HEM_SMALL_MM if small else DOLL_HEM_MM)
    o["doll"] = True
    return o


def _scale_options(o: dict, f: float) -> dict:
    import allowance as A
    out = dict(o)
    # allowances are checked in doll millimetres, then passed on as the module's sa / hem_sa
    if not A.no_allowance(out):
        if out.get("seam_allowance_mm") is not None:
            out["sa"] = A._num(out.pop("seam_allowance_mm"), "seam_allowance_mm", A.SEAM_RANGE)
        if out.get("hem_allowance_mm") is not None:
            out["hem_sa"] = A._num(out.pop("hem_allowance_mm"), "hem_allowance_mm", A.HEM_RANGE)
    for k in LENGTH_OPTIONS:
        v = out.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = v * f
    if out.get("construction"):
        out["construction"] = {k: (v if k in NON_MM_CONSTRUCTION else float(v) * f)
                               for k, v in out["construction"].items()}
    if out.get("adjustments"):
        out["adjustments"] = {k: f"{ADJ.parse_delta(v) * f:.3f}mm" for k, v in out["adjustments"].items()}
    return out


def _scale_value(k, v, f):
    if k in NOT_LENGTHS or isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v * f
    if isinstance(v, dict):
        return {kk: _scale_value(kk, vv, f) for kk, vv in v.items()}
    if k == "_adjustments_applied":
        return [(a, d * f, what) for a, d, what in v]
    return v


def scale_text(text: str, f: float) -> str:
    """Rescale lengths written as '25 mm' / '4.5 cm' in a note."""
    def rep(mo):
        x = float(mo.group(1)) * f
        if mo.group(2) == "mm":
            return f"{x:.0f} mm"
        return f"{x:.1f} cm" if x < 10 else f"{x:.0f} cm"
    def rep_range(mo):
        a = float(mo.group(1)) * f
        b = float(mo.group(3)) * f
        if mo.group(4) == "mm":
            return f"{a:.0f}{mo.group(2)}{b:.0f} mm"
        return f"{a:.1f}{mo.group(2)}{b:.1f} cm"
    text = re.sub(r"(\d+(?:\.\d+)?)(\s?[–-]\s?)(\d+(?:\.\d+)?)\s?(cm|mm)\b", rep_range, text)
    return re.sub(r"(?<![\d.–-])(\d+(?:\.\d+)?)\s?(cm|mm)\b", rep, text)


def scale_pattern(pat, f: float) -> None:
    """Scale a drafted pattern (geometry, allowances, notches, checks, values) by f in place."""
    for pc in pat.pieces:
        for e in pc.edges:
            e.pts = e.pts * f
            e.sa *= f
            e.sa_hint *= f
        for n in pc.notches:
            n.s *= f
        for mk in pc.marks:
            mk.pts = mk.pts * f
        if pc.grain is not None:
            pc.grain = (pc.grain[0] * f, pc.grain[1] * f)
    for s in pat.seams:
        if s.get("type") == "ease":
            s["lo"], s["hi"] = s["lo"] * f, s["hi"] * f
        if "note" in s:
            s["note"] = scale_text(s["note"], f)
    for c in pat.checks:
        pct = c.get("unit") == "%" or "stretch" in c["name"].lower()
        if pct:
            continue
        for k in ("value", "target", "lo", "hi"):
            if k in c:
                c[k] = c[k] * f
        if "note" in c:
            c["note"] = scale_text(c["note"], f)
    pat.finished = {k: v * f for k, v in pat.finished.items()}
    for r in pat.construction:
        if r.get("unit") == "mm":
            r["value"] *= f
            if r.get("computed") is not None:
                r["computed"] *= f
    opts = dict(pat.options)
    for k in LENGTH_OPTIONS:
        v = opts.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            opts[k] = v * f
    for k, v in list(opts.items()):
        if k.startswith("_"):
            opts[k] = _scale_value(k, v, f)
    pat.options = opts
    pat.notes = [scale_text(n, f) for n in pat.notes]


def scale_factor(measures_mm: dict) -> float:
    return VIRTUAL_SIDE_MM / measures_mm["side_length"]


def draft(mod, garment: str, measures_mm: dict, options: dict):
    """Draft a doll garment (see the module docstring). measures in mm, options with doll defaults."""
    S = scale_factor(measures_mm)
    virtual = {k: v * S for k, v in measures_mm.items()}
    virtual["height"] = VIRTUAL_HEIGHT_MM
    user_opts = copy.deepcopy(options)
    pat = ADJ.draft(mod, garment, virtual, _scale_options(options, S))
    scale_pattern(pat, 1.0 / S)
    pat.measures = dict(measures_mm)
    for k in ("construction", "adjustments"):
        if k in user_opts:
            pat.options[k] = user_opts[k]
    for k in ("seam_allowance_mm", "hem_allowance_mm"):
        if k in user_opts:
            pat.options[k] = user_opts[k]
    pat.options["doll"] = True
    pat.options["_doll_scale"] = S
    for c in pat.checks:
        if c["name"] == "Front rise plausible":
            # the child rule (12 % of the height + …) does not fit a doll's deep, round seat
            c["hi"] = max(c["hi"], 1.35 * measures_mm["crotch_depth"])
    pat.notes += doll_notes(pat)
    return pat


def doll_notes(pat) -> list[str]:
    o = pat.options
    sa = o.get("sa", DOLL_SA_MM)
    notes = [f"Doll clothes: narrow seam allowances ({sa:.0f} mm). Sew with a short stitch (1.5–2 mm) "
             "and finish woven edges with pinking shears, a narrow zigzag or a little fray stop.",
             "Thin, soft fabrics work best (cotton poplin, batiste, old T-shirts); thick fabric makes "
             "the tiny seams bulky."]
    if o.get("back_opening"):
        notes.append("The back opens completely: close it with narrow Velcro (1 cm) or 2–3 small snaps.")
    if pat.garment in ("pants_basic", "skirt"):
        notes.append("Pull the elastic through with a small safety pin; for very small dolls a thin "
                     "elastic cord also works.")
    return notes


# ---------------------------------------------------------------------------- photo mode B

# child-size reference for the virtual scale of a garment photo: pants outseam, top length
VIRTUAL_OUTSEAM_MM = 640.0
VIRTUAL_TOP_LENGTH_MM = 420.0


def photo_scale(garment: str, flat_mm: dict) -> float:
    """Virtual scale for a doll garment measured from a photo (photo mode B)."""
    if garment in ("pants", "pants_basic"):
        return VIRTUAL_OUTSEAM_MM / flat_mm["outseam"]
    return VIRTUAL_TOP_LENGTH_MM / flat_mm["length"]


def scale_flat(flat_mm: dict, f: float) -> dict:
    return {k: (v * f if not k.startswith("_") and isinstance(v, (int, float)) and not isinstance(v, bool)
                else v) for k, v in flat_mm.items()}


def photo_options(garment: str, base_options: dict | None, S: float) -> dict:
    """Module options for fitting a doll garment at the virtual scale S (doll defaults, × S)."""
    g = "pants_basic" if garment in ("pants", "pants_basic") else "tshirt_basic"
    o = defaults(g, base_options)
    o = _scale_options(o, S)
    for k in ("seam_allowance_mm", "hem_allowance_mm"):
        o.pop(k, None)
    return o


def finish_virtual(pat, S: float, measures_mm: dict | None = None):
    """Scale a pattern drafted at the virtual scale S back to the doll (photo mode B, projects)."""
    scale_pattern(pat, 1.0 / S)
    if measures_mm is not None:
        pat.measures = dict(measures_mm)
    else:
        pat.measures = {k: v / S for k, v in pat.measures.items()}
    pat.options["doll"] = True
    pat.options["_doll_scale"] = S
    # no doll body is known (only the garment): plausibility ranges against the virtual
    # child body would only confuse
    pat.checks = [c for c in pat.checks if not (c["kind"] == "range" and "plausible" in c["name"])]
    pat.notes += doll_notes(pat)
    return pat


def draft_project(mod, garment: str, size, options_virtual: dict, S: float, adjustments=None):
    """Draft a saved doll project (photo mode B, options at the virtual scale) and scale it back."""
    import measurements as M
    body = M.size_measures(size)
    o = dict(options_virtual)
    if adjustments:
        o["adjustments"] = _scale_options({"adjustments": adjustments}, S)["adjustments"]
    pat = ADJ.draft(mod, garment, body, o)
    finish_virtual(pat, S)
    if adjustments:
        pat.options["adjustments"] = dict(adjustments)
    return pat


def scale_rows(rows: list[dict], f: float) -> list[dict]:
    """Deviation rows (reverse/verify.py) back to doll millimetres."""
    out = []
    for r in rows:
        r = dict(r)
        for k in ("target", "actual", "delta"):
            r[k] = r[k] * f
        r["tol"] = r["tol"] * f
        out.append(r)
    return out
