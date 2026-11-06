"""Körpermaße: Größentabellen, Ableitung fehlender Maße, Plausibilitätsprüfung.

Die Tabellen sind **gerundete Richtwerte**, die aus allgemein zugänglichen
Größenübersichten (Konfektionsgrößen nach Körperhöhe, DIN EN 13402 / übliche deutsche
Konfektionsgrößen) gemittelt wurden. Sie sind keine Kopie einer bestimmten Schnitttabelle.
Werte in der Tabelle: cm. Intern rechnet der Skill in mm.

Maßnamen (intern):
  height        Körperhöhe
  chest         Brustumfang
  waist         Taillenumfang
  hip           Hüftumfang (Gesäß)
  head          Kopfumfang
  neck          Halsumfang
  inseam        Schrittlänge (Innenbein, Schritt–Boden)
  side_length   Seitenlänge (Taille–Boden)
  crotch_depth  Leibhöhe / Schritttiefe (= side_length − inseam)
  arm           Armlänge (Schulterpunkt–Handgelenk)
  back_length   Rückenlänge (7. Halswirbel–Taille)
  shoulder      Schulterbreite (eine Schulter, Halsansatz–Schulterpunkt)
  upper_arm     Oberarmumfang
  wrist         Handgelenkumfang
  thigh         Oberschenkelumfang
  knee          Knieumfang
  ankle         Knöchelumfang
"""
from __future__ import annotations

import re

import numpy as np

# Kinder: Größe = Körperhöhe (cm)
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

# Damen 34–56 und Herren 44–60: Formeln je Größensprung (2 Größen-Nummern)
DAMEN_SIZES = list(range(34, 58, 2))
HERREN_SIZES = list(range(44, 62, 2))


def _damen(size: float) -> dict:
    step = (size - 36) / 2
    chest = 84 + 4 * min(step, 4) + 6 * max(step - 4, 0)          # 36→84, 44→100, 56→136
    return {"height": 168.0, "chest": chest, "waist": chest - 16 + 0.5 * max(step - 4, 0) * 2,
            "hip": chest + 10 - 0.5 * max(step - 4, 0), "head": 55.0 + 0.25 * step,
            "neck": 34.0 + 0.8 * step, "inseam": 78.0, "side_length": 104.0, "arm": 59.5,
            "back_length": 41.0 + 0.2 * step, "shoulder": 12.3 + 0.15 * step}


def _herren(size: float) -> dict:
    step = (size - 48) / 2
    chest = 2.0 * size
    return {"height": 178.0 + 1.0 * min(max(step, -2), 3), "chest": chest,
            "waist": chest - 12 + 2 * max(step, 0), "hip": chest + 4 - 0.5 * max(step, 0),
            "head": 57.0 + 0.3 * step, "neck": 39.0 + 1.0 * step, "inseam": 82.0,
            "side_length": 107.0, "arm": 63.5, "back_length": 45.0 + 0.2 * step,
            "shoulder": 14.5 + 0.2 * step}


ALIASES = {
    "koerperhoehe": "height", "körperhöhe": "height", "groesse_cm": "height", "hoehe": "height",
    "brust": "chest", "brustumfang": "chest", "oberweite": "chest",
    "taille": "waist", "taillenumfang": "waist", "bund": "waist", "bundweite": "waist",
    "huefte": "hip", "hüfte": "hip", "hueftumfang": "hip", "hüftumfang": "hip", "gesaess": "hip",
    "kopf": "head", "kopfumfang": "head", "hals": "neck", "halsumfang": "neck",
    "schrittlaenge": "inseam", "schrittlänge": "inseam", "innenbein": "inseam",
    "seitenlaenge": "side_length", "seitenlänge": "side_length",
    "leibhoehe": "crotch_depth", "leibhöhe": "crotch_depth", "schritttiefe": "crotch_depth",
    "armlaenge": "arm", "armlänge": "arm", "rueckenlaenge": "back_length", "rückenlänge": "back_length",
    "schulterbreite": "shoulder", "schulter": "shoulder", "oberarm": "upper_arm",
    "oberarmumfang": "upper_arm", "handgelenk": "wrist", "oberschenkel": "thigh",
    "oberschenkelumfang": "thigh", "knie": "knee", "knoechel": "ankle", "knöchel": "ankle",
}

LABELS_DE = {
    "height": "Körperhöhe", "chest": "Brustumfang", "waist": "Taillenumfang", "hip": "Hüftumfang",
    "head": "Kopfumfang", "neck": "Halsumfang", "inseam": "Schrittlänge", "side_length": "Seitenlänge",
    "crotch_depth": "Leibhöhe", "arm": "Armlänge", "back_length": "Rückenlänge",
    "shoulder": "Schulterbreite", "upper_arm": "Oberarmumfang", "wrist": "Handgelenkumfang",
    "thigh": "Oberschenkelumfang", "knee": "Knieumfang", "ankle": "Knöchelumfang",
}


def parse_size(size) -> tuple[str, float]:
    """'122', 'Gr. 122', 'Damen 38', 'H50' → (system, Zahl)."""
    if isinstance(size, (int, float)):
        n = float(size)
        return ("kinder" if n >= 80 else "damen"), n
    s = str(size).lower().replace("gr.", "").replace("größe", "").strip()
    system = None
    if s.startswith(("d", "damen")):
        system = "damen"
    elif s.startswith(("h", "herren")):
        system = "herren"
    m = re.search(r"(\d+(?:[.,]\d+)?)", s)
    if not m:
        raise ValueError(f"Größe nicht erkannt: {size}")
    n = float(m.group(1).replace(",", "."))
    if system is None:
        system = "kinder" if n >= 80 else "damen"
    return system, n


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
    system, n = parse_size(size)
    if system == "kinder":
        keys = sorted(KIDS_TABLE)
        n_c = min(max(n, keys[0]), keys[-1])
        arr = np.array([KIDS_TABLE[k] for k in keys])
        vals = [float(np.interp(n_c, keys, arr[:, i])) for i in range(arr.shape[1])]
        m = dict(zip(KIDS_COLS, vals))
        m["height"] = n
        if n != n_c:  # außerhalb der Tabelle: Längen proportional zur Höhe
            f = n / n_c
            for k in ("inseam", "side_length", "arm", "back_length"):
                m[k] *= f
        return _derived_cm(m, adult=False)
    if system == "damen":
        return _derived_cm(_damen(n), adult=True)
    return _derived_cm(_herren(n), adult=True)


def size_measures(size) -> dict:
    """Maße in mm für eine Konfektionsgröße."""
    return {k: v * 10 for k, v in size_measures_cm(size).items()}


def normalize_keys(given: dict) -> dict:
    out = {}
    for k, v in (given or {}).items():
        kk = ALIASES.get(str(k).lower(), str(k).lower())
        out[kk] = float(v)
    return out


def complete_measures(given_cm: dict | None = None, size=None, system: str | None = None):
    """Fehlende Maße ergänzen. Eingabe in cm, Ausgabe in mm.

    Rückgabe: (maße_mm, quelle) mit quelle[maß] in {'Nutzer', 'Tabelle', 'abgeleitet'}.
    Ist keine Größe angegeben, wird bei Kindern die Größe aus der Körperhöhe bestimmt;
    Längenmaße werden dann proportional zur Körperhöhe skaliert.
    """
    g = normalize_keys(given_cm or {})
    if size is None:
        if "height" not in g:
            raise ValueError("Bitte Größe oder Körperhöhe angeben.")
        if system in (None, "kinder") and g["height"] <= 176:
            size = round(g["height"])
        else:
            size = f"{'h' if system == 'herren' else 'd'}{38 if system != 'herren' else 50}"
    base = size_measures_cm(size)
    src = {k: "Tabelle" for k in base}
    if "height" in g and abs(g["height"] - base["height"]) > 0.5:
        f = g["height"] / base["height"]
        for k in ("inseam", "side_length", "arm", "back_length", "crotch_depth"):
            base[k] *= f
            src[k] = "abgeleitet"
    # Umfänge, die der Nutzer nicht nennt, aus genannten Umfängen nachführen
    if "hip" in g and "thigh" not in g:
        base["thigh"] = g["hip"] * base["thigh"] / base["hip"]
        src["thigh"] = "abgeleitet"
    if "chest" in g and "upper_arm" not in g:
        base["upper_arm"] = g["chest"] * base["upper_arm"] / base["chest"]
        src["upper_arm"] = "abgeleitet"
    for k, v in g.items():
        base[k] = v
        src[k] = "Nutzer"
    if ("side_length" in g or "inseam" in g) and "crotch_depth" not in g:
        base["crotch_depth"] = base["side_length"] - base["inseam"]
        src["crotch_depth"] = "abgeleitet"
    if "crotch_depth" in g and "side_length" not in g:
        base["side_length"] = base["inseam"] + g["crotch_depth"]
        src["side_length"] = "abgeleitet"
    return {k: v * 10 for k, v in base.items()}, src


def validate_measures(m_mm: dict) -> list[str]:
    """Plausibilitätsprüfung der Körpermaße. Liefert Warnungen (deutsch)."""
    w = []
    h = m_mm.get("height", 0)
    if h <= 0:
        return ["Körperhöhe fehlt"]
    if not 0.35 <= m_mm["inseam"] / h <= 0.50:
        w.append(f"Schrittlänge {m_mm['inseam'] / 10:.0f} cm wirkt ungewöhnlich für {h / 10:.0f} cm Körperhöhe")
    if not 0.50 <= m_mm["side_length"] / h <= 0.66:
        w.append(f"Seitenlänge {m_mm['side_length'] / 10:.0f} cm wirkt ungewöhnlich für {h / 10:.0f} cm Körperhöhe")
    cd = m_mm["side_length"] - m_mm["inseam"]
    if not 0.10 <= cd / h <= 0.20:
        w.append(f"Leibhöhe {cd / 10:.1f} cm (Seitenlänge − Schrittlänge) wirkt unplausibel")
    if m_mm["waist"] > m_mm["hip"] * 1.15:
        w.append("Taille deutlich größer als Hüfte – bitte nachmessen")
    if m_mm["hip"] < m_mm["waist"] * 0.85:
        w.append("Hüfte deutlich kleiner als Taille – bitte nachmessen")
    if not 0.36 <= m_mm["arm"] / h <= 0.62 and "arm" in m_mm:
        w.append(f"Armlänge {m_mm['arm'] / 10:.0f} cm wirkt ungewöhnlich für {h / 10:.0f} cm Körperhöhe")
    return w


def table_markdown() -> str:
    head = "| Gr. | " + " | ".join(LABELS_DE[c] for c in KIDS_COLS) + " |"
    sep = "|" + "---|" * (len(KIDS_COLS) + 1)
    rows = [f"| {k} | " + " | ".join(f"{v:g}" for v in vals) + " |" for k, vals in KIDS_TABLE.items()]
    return "\n".join([head, sep] + rows)
