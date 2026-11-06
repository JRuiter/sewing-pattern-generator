"""Body measurements: size tables, deriving missing measurements, plausibility checks.

The tables are **rounded reference values** averaged from publicly available size
charts (children's sizes by body height, DIN EN 13402 / common German ready-to-wear
sizes). They are not a copy of any particular pattern company's chart.
Table values: cm. Internally the skill works in mm.

Measurement names (internal):
  height        body height
  chest         chest circumference
  waist         waist circumference
  hip           hip circumference (seat)
  head          head circumference
  neck          neck circumference
  inseam        inseam (inside leg, crotch to floor)
  side_length   side length (waist to floor)
  crotch_depth  rise / crotch depth (= side_length − inseam)
  arm           arm length (shoulder point to wrist)
  back_length   back length (7th cervical vertebra to waist)
  shoulder      shoulder width (one shoulder, neck point to shoulder point)
  upper_arm     upper-arm circumference
  wrist         wrist circumference
  thigh         thigh circumference
  knee          knee circumference
  ankle         ankle circumference
"""
from __future__ import annotations

import re

import numpy as np

# children: size = body height (cm)
# size: chest, waist, hip, head, neck, inseam, side_length, arm, back_length, shoulder
KIDS_COLS = ["chest", "waist", "hip", "head", "neck", "inseam", "side_length", "arm",
             "back_length", "shoulder"]
KIDS_TABLE = {
    86:  [52.0, 50.0, 53.0, 48.5, 25.5, 32.0, 49.0, 30.0, 23.0, 7.5],
    92:  [53.0, 51.0, 55.0, 49.5, 26.0, 36.0, 53.0, 33.0, 24.5, 8.0],
    98:  [55.0, 52.0, 57.0, 50.0, 26.5, 40.0, 57.0, 35.5, 25.5, 8.5],
    104: [56.0, 53.0, 59.0, 50.5, 27.0, 44.0, 61.0, 38.0, 26.5, 9.0],
    110: [58.0, 54.0, 61.0, 51.0, 27.5, 48.0, 65.0, 41.0, 27.5, 9.3],
    116: [60.0, 55.0, 63.0, 51.5, 28.0, 51.0, 68.5, 44.0, 28.5, 9.6],
    122: [62.0, 56.0, 66.0, 52.0, 28.5, 54.0, 72.0, 47.0, 29.5, 10.0],
    128: [64.0, 57.0, 69.0, 52.5, 29.0, 57.5, 76.0, 50.0, 31.0, 10.4],
    134: [66.0, 58.0, 72.0, 53.0, 30.0, 61.0, 80.0, 53.0, 32.5, 10.8],
    140: [69.0, 60.0, 75.0, 53.5, 31.0, 64.5, 84.0, 56.0, 34.0, 11.2],
    146: [72.0, 62.0, 78.0, 54.0, 32.0, 68.0, 88.0, 59.0, 35.5, 11.6],
    152: [76.0, 64.0, 82.0, 54.5, 32.5, 71.5, 92.0, 62.0, 37.0, 12.0],
    158: [80.0, 66.0, 86.0, 55.0, 33.5, 75.0, 96.0, 64.5, 38.5, 12.3],
    164: [84.0, 68.0, 90.0, 55.5, 34.0, 78.0, 100.0, 67.0, 40.0, 12.6],
    170: [88.0, 70.0, 93.0, 56.0, 35.0, 80.5, 103.0, 69.5, 41.5, 13.0],
    176: [91.0, 72.0, 96.0, 56.5, 36.0, 83.0, 106.0, 72.0, 43.0, 13.3],
}

# women 34–56 and men 44–60: formulas per size step (2 size numbers)
WOMEN_SIZES = list(range(34, 58, 2))
MEN_SIZES = list(range(44, 62, 2))


def _women(size: float) -> dict:
    step = (size - 36) / 2
    chest = 84 + 4 * min(step, 4) + 6 * max(step - 4, 0)          # 36→84, 44→100, 56→136
    return {"height": 168.0, "chest": chest, "waist": chest - 16 + 0.5 * max(step - 4, 0) * 2,
            "hip": chest + 10 - 0.5 * max(step - 4, 0), "head": 55.0 + 0.25 * step,
            "neck": 34.0 + 0.8 * step, "inseam": 78.0, "side_length": 104.0, "arm": 59.5,
            "back_length": 41.0 + 0.2 * step, "shoulder": 12.3 + 0.15 * step}


def _men(size: float) -> dict:
    step = (size - 48) / 2
    chest = 2.0 * size
    return {"height": 178.0 + 1.0 * min(max(step, -2), 3), "chest": chest,
            "waist": chest - 12 + 2 * max(step, 0), "hip": chest + 4 - 0.5 * max(step, 0),
            "head": 57.0 + 0.3 * step, "neck": 39.0 + 1.0 * step, "inseam": 82.0,
            "side_length": 107.0, "arm": 63.5, "back_length": 45.0 + 0.2 * step,
            "shoulder": 14.5 + 0.2 * step}


# Accepted input names (English and German) → internal name
ALIASES = {
    "body_height": "height", "hip_circ": "hip", "chest_circ": "chest", "waist_circ": "waist",
    "head_circ": "head", "neck_circ": "neck", "inside_leg": "inseam", "rise": "crotch_depth",
    "arm_length": "arm", "shoulder_width": "shoulder", "bicep": "upper_arm",
    "koerperhoehe": "height", "körperhöhe": "height", "groesse_cm": "height", "hoehe": "height",
    "brust": "chest", "brustumfang": "chest", "oberweite": "chest",
    "taille": "waist", "taillenumfang": "waist", "waistband": "waist", "bundweite": "waist",
    "huefte": "hip", "hüfte": "hip", "hueftumfang": "hip", "hüftumfang": "hip", "gesaess": "hip",
    "kopf": "head", "kopfumfang": "head", "neck": "neck", "halsumfang": "neck",
    "schrittlaenge": "inseam", "schrittlänge": "inseam", "inseam": "inseam",
    "seitenlaenge": "side_length", "seitenlänge": "side_length",
    "leibhoehe": "crotch_depth", "leibhöhe": "crotch_depth", "schritttiefe": "crotch_depth",
    "armlaenge": "arm", "armlänge": "arm", "rueckenlaenge": "back_length", "rückenlänge": "back_length",
    "schulterbreite": "shoulder", "shoulder": "shoulder", "oberarm": "upper_arm",
    "oberarmumfang": "upper_arm", "handgelenk": "wrist", "oberschenkel": "thigh",
    "oberschenkelumfang": "thigh", "knee": "knee", "knoechel": "ankle", "knöchel": "ankle",
}

LABELS = {
    "height": "Body height", "chest": "Chest", "waist": "Waist", "hip": "Hip",
    "head": "Head", "neck": "Neck", "inseam": "Inseam", "side_length": "Side length",
    "crotch_depth": "Rise (crotch depth)", "arm": "Arm length", "back_length": "Back length",
    "shoulder": "Shoulder width", "upper_arm": "Upper arm", "wrist": "Wrist",
    "thigh": "Thigh", "knee": "Knee", "ankle": "Ankle",
}


# US / UK size systems → the base systems above (see references/size_tables.md).
# US toddler 2T–5T and US children 4–16 → kids' size (body height in cm)
US_TODDLER_HEIGHT = {2: 92.0, 3: 98.0, 4: 104.0, 5: 110.0}
US_KIDS_HEIGHT = {4: 104.0, 5: 110.0, 6: 116.0, 7: 122.0, 8: 128.0, 10: 140.0, 12: 152.0,
                  14: 158.0, 16: 164.0}
US_WOMEN_OFFSET = 30     # US misses 8 ≈ German/EU women's 38
UK_WOMEN_OFFSET = 26     # UK women's 12 ≈ German/EU women's 38
US_WOMEN_RANGE = (0, 20)
UK_WOMEN_RANGE = (4, 22)

SIZE_LABELS = {"kids": "size %g", "women": "women's size %g", "men": "men's size %g",
               "us_toddler": "US size %gT", "us_kids": "US kids' size %g",
               "us_women": "US women's size %g", "uk_women": "UK women's size %g"}


def parse_size(size) -> tuple[str, float]:
    """'122', 'size 122', 'w38', 'women 38', 'm50', 'men 50' → (system, number).

    German forms are accepted too: 'Gr. 122', 'Damen 38'/'d38', 'Herren 50'/'h50'.
    US/UK: 'us8' (US women's/misses 0–20), 'uk12' (UK women's 4–22), 'us3t' (US toddler
    2T–5T), 'usk8' / 'us kids 8' (US children 4–16).
    """
    if isinstance(size, (int, float)):
        n = float(size)
        return ("kids" if n >= 80 else "women"), n
    s = str(size).lower().replace("gr.", "").replace("größe", "").replace("size", "").strip()
    m = re.search(r"(\d+(?:[.,]\d+)?)", s)
    if not m:
        raise ValueError(f"Size not recognised: {size}")
    n = float(m.group(1).replace(",", "."))
    if s.startswith(("us", "uk")):
        rest = s[2:].replace("-", " ").replace("_", " ").strip()
        if s.startswith("uk"):
            lo, hi = UK_WOMEN_RANGE
            system = "uk_women"
        elif rest.endswith("t"):
            lo, hi = min(US_TODDLER_HEIGHT), max(US_TODDLER_HEIGHT)
            system = "us_toddler"
        elif rest.startswith(("k", "girls", "boys", "child")):
            lo, hi = min(US_KIDS_HEIGHT), max(US_KIDS_HEIGHT)
            system = "us_kids"
        else:
            lo, hi = US_WOMEN_RANGE
            system = "us_women"
        if not lo <= n <= hi:
            raise ValueError(f"{SIZE_LABELS[system] % n} is outside the supported range {lo:g}–{hi:g}")
        return system, n
    system = None
    if s.startswith(("w", "d")):          # women / Damen
        system = "women"
    elif s.startswith(("m", "h")):        # men / Herren
        system = "men"
    elif s.startswith("k"):               # kids
        system = "kids"
    if system is None:
        system = "kids" if n >= 80 else "women"
    return system, n


def base_size(system: str, n: float) -> tuple[str, float]:
    """US/UK systems → (kids|women|men, number) of the base tables."""
    if system == "us_toddler":
        return "kids", float(np.interp(n, list(US_TODDLER_HEIGHT), list(US_TODDLER_HEIGHT.values())))
    if system == "us_kids":
        return "kids", float(np.interp(n, list(US_KIDS_HEIGHT), list(US_KIDS_HEIGHT.values())))
    if system == "us_women":
        return "women", n + US_WOMEN_OFFSET
    if system == "uk_women":
        return "women", n + UK_WOMEN_OFFSET
    return system, n


def size_label(size) -> str:
    system, n = parse_size(size)
    return SIZE_LABELS[system] % n


def _derived_cm(m: dict, adult: bool) -> dict:
    out = dict(m)
    out.setdefault("crotch_depth", out["side_length"] - out["inseam"])
    out.setdefault("thigh", out["hip"] * (0.58 if adult else 0.56))
    out.setdefault("knee", out["hip"] * (0.38 if adult else 0.40))
    out.setdefault("ankle", out["hip"] * (0.24 if adult else 0.27))
    out.setdefault("upper_arm", out["chest"] * (0.31 if adult else 0.30))
    out.setdefault("wrist", out["chest"] * (0.17 if adult else 0.20))
    return out


def size_measures_cm(size) -> dict:
    system, n = base_size(*parse_size(size))
    if system == "kids":
        keys = sorted(KIDS_TABLE)
        n_c = min(max(n, keys[0]), keys[-1])
        arr = np.array([KIDS_TABLE[k] for k in keys])
        vals = [float(np.interp(n_c, keys, arr[:, i])) for i in range(arr.shape[1])]
        m = dict(zip(KIDS_COLS, vals))
        m["height"] = n
        if n != n_c:  # outside the table: lengths proportional to height
            f = n / n_c
            for k in ("inseam", "side_length", "arm", "back_length"):
                m[k] *= f
        return _derived_cm(m, adult=False)
    if system == "women":
        return _derived_cm(_women(n), adult=True)
    return _derived_cm(_men(n), adult=True)


def size_measures(size) -> dict:
    """Measurements in mm for a ready-to-wear size."""
    return {k: v * 10 for k, v in size_measures_cm(size).items()}


def normalize_keys(given: dict) -> dict:
    out = {}
    for k, v in (given or {}).items():
        kk = ALIASES.get(str(k).lower(), str(k).lower())
        out[kk] = float(v)
    return out


def complete_measures(given_cm: dict | None = None, size=None, system: str | None = None):
    """Fill in missing measurements. Input in cm, output in mm.

    Returns (measures_mm, source) with source[name] in {'user', 'table', 'derived'}.
    Without a size, children's sizes are taken from the body height; length
    measurements are then scaled proportionally to the body height.
    """
    g = normalize_keys(given_cm or {})
    if size is None:
        if "height" not in g:
            raise ValueError("Please give a size or the body height.")
        if system in (None, "kids") and g["height"] <= 176:
            size = round(g["height"])
        else:
            size = f"{'m' if system == 'men' else 'w'}{38 if system != 'men' else 50}"
    base = size_measures_cm(size)
    src = {k: "table" for k in base}
    if "height" in g and abs(g["height"] - base["height"]) > 0.5:
        f = g["height"] / base["height"]
        for k in ("inseam", "side_length", "arm", "back_length", "crotch_depth"):
            base[k] *= f
            src[k] = "derived"
    # circumferences the user did not give follow the ones they did give
    if "hip" in g and "thigh" not in g:
        base["thigh"] = g["hip"] * base["thigh"] / base["hip"]
        src["thigh"] = "derived"
    if "chest" in g and "upper_arm" not in g:
        base["upper_arm"] = g["chest"] * base["upper_arm"] / base["chest"]
        src["upper_arm"] = "derived"
    for k, v in g.items():
        base[k] = v
        src[k] = "user"
    if ("side_length" in g or "inseam" in g) and "crotch_depth" not in g:
        base["crotch_depth"] = base["side_length"] - base["inseam"]
        src["crotch_depth"] = "derived"
    if "crotch_depth" in g and "side_length" not in g:
        base["side_length"] = base["inseam"] + g["crotch_depth"]
        src["side_length"] = "derived"
    return {k: v * 10 for k, v in base.items()}, src


def validate_measures(m_mm: dict) -> list[str]:
    """Plausibility check of the body measurements. Returns warnings."""
    w = []
    h = m_mm.get("height", 0)
    if h <= 0:
        return ["Body height missing"]
    if not 0.35 <= m_mm["inseam"] / h <= 0.50:
        w.append(f"Inseam {m_mm['inseam'] / 10:.0f} cm looks unusual for a body height of {h / 10:.0f} cm")
    if not 0.50 <= m_mm["side_length"] / h <= 0.66:
        w.append(f"Side length {m_mm['side_length'] / 10:.0f} cm looks unusual for a body height of {h / 10:.0f} cm")
    cd = m_mm["side_length"] - m_mm["inseam"]
    if not 0.10 <= cd / h <= 0.20:
        w.append(f"Rise {cd / 10:.1f} cm (side length − inseam) looks implausible")
    if m_mm["waist"] > m_mm["hip"] * 1.15:
        w.append("Waist much larger than hip, please measure again")
    if m_mm["hip"] < m_mm["waist"] * 0.85:
        w.append("Hip much smaller than waist, please measure again")
    if not 0.36 <= m_mm["arm"] / h <= 0.62 and "arm" in m_mm:
        w.append(f"Arm length {m_mm['arm'] / 10:.0f} cm looks unusual for a body height of {h / 10:.0f} cm")
    return w


def table_markdown() -> str:
    head = "| Size | " + " | ".join(LABELS[c] for c in KIDS_COLS) + " |"
    sep = "|" + "---|" * (len(KIDS_COLS) + 1)
    rows = [f"| {k} | " + " | ".join(f"{v:g}" for v in vals) + " |" for k, vals in KIDS_TABLE.items()]
    return "\n".join([head, sep] + rows)
