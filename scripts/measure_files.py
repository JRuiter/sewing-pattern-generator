"""Read and write body measurements as XML measurement files (.smis / .vit).

Open-source pattern CAD programs store an individual's body measurements as a small XML
file: a unit (mm, cm or inch) and a list of ``<m name="…" value="…"/>`` entries with
standardised measurement names (``waist_circ``, ``hip_circ``, ``leg_crotch_to_floor`` …).
Supporting that format means measurements taken once can be reused here and in such
programs, and saved profiles (one file per person) are interchangeable.

Reading accepts ``.smis`` and the older ``.vit`` files (same structure). Values may be
plain numbers or simple formulas that reference other measurements of the same file
(``+ - * /``, parentheses); anything else is skipped with a warning.
"""
from __future__ import annotations

import ast
import datetime as _dt
import operator
import xml.etree.ElementTree as ET

# skill key → standard measurement name in the XML files
NAME_MAP = {
    "height": "height",
    "chest": "bust_circ",
    "waist": "waist_circ",
    "hip": "hip_circ",
    "head": "head_circ",
    "neck": "neck_circ",
    "inseam": "leg_crotch_to_floor",
    "side_length": "height_waist_side",
    "crotch_depth": "rise_length_side_sitting",
    "arm": "arm_shoulder_tip_to_wrist",
    "back_length": "neck_back_to_waist_b",
    "shoulder": "shoulder_length",
    "upper_arm": "arm_upper_circ",
    "wrist": "arm_wrist_circ",
    "thigh": "leg_thigh_upper_circ",
    "knee": "leg_knee_circ",
    "ankle": "leg_ankle_circ",
}
REVERSE_MAP = {v: k for k, v in NAME_MAP.items()}
# accepted as a fallback when the preferred name is missing
FALLBACKS = {"neck": ["neck_mid_circ"], "chest": ["body_bust_circ", "highbust_circ"],
             "ankle": ["leg_ankle_high_circ"], "thigh": ["leg_thigh_mid_circ"],
             "back_length": ["neck_back_to_waist_side"]}
TO_MM = {"mm": 1.0, "cm": 10.0, "inch": 25.4}

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv}


def _eval(expr: str, env: dict) -> float:
    """Evaluate a simple arithmetic formula safely (numbers, names from env, + - * /)."""
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.Name) and n.id in env:
            return float(env[n.id])
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            v = ev(n.operand)
            return -v if isinstance(n.op, ast.USub) else v
        raise ValueError(f"unsupported formula element in {expr!r}")
    return ev(ast.parse(expr.replace(",", "."), mode="eval"))


def read_file(path: str) -> tuple[dict, list[str]]:
    """Measurements in **cm** under the skill's keys, plus a list of warnings."""
    root = ET.parse(path).getroot()
    unit = (root.findtext("unit") or "cm").strip()
    if unit not in TO_MM:
        raise ValueError(f"unknown unit {unit!r} in {path}")
    f = TO_MM[unit] / 10.0                          # → cm
    raw: dict[str, str] = {}
    for m in root.iter("m"):
        name, value = m.get("name"), m.get("value")
        if name and value is not None:
            raw[name] = value.strip()
    warnings = []
    values: dict[str, float] = {}
    pending = dict(raw)
    for _ in range(len(pending) + 1):               # resolve formulas that reference each other
        progress = False
        for name, expr in list(pending.items()):
            try:
                values[name] = _eval(expr, values)
                del pending[name]
                progress = True
            except (ValueError, SyntaxError, ZeroDivisionError):
                continue
        if not progress:
            break
    for name, expr in pending.items():
        warnings.append(f"measurement {name} = {expr!r} could not be evaluated and was skipped")
    out: dict[str, float] = {}
    for key, std in NAME_MAP.items():
        for cand in [std] + FALLBACKS.get(key, []):
            if cand in values and values[cand] > 0:
                out[key] = round(values[cand] * f, 2)
                break
    unused = sorted(n for n in values if n not in REVERSE_MAP and not any(n in v for v in FALLBACKS.values()))
    if unused:
        warnings.append(f"{len(unused)} measurement(s) not used by the skill: " + ", ".join(unused[:12])
                        + (" …" if len(unused) > 12 else ""))
    return out, warnings


def write_file(path: str, measures_mm: dict, unit: str = "cm", given_name: str = "", family_name: str = "",
               notes: str = "", gender: str = "unknown") -> str:
    """Write body measurements (skill keys, mm) as an individual measurement file (.smis)."""
    if unit not in TO_MM:
        raise ValueError(f"unit must be one of {sorted(TO_MM)}")
    if gender not in ("unknown", "male", "female"):
        gender = "unknown"
    root = ET.Element("smis")
    root.append(ET.Comment(" Body measurements written by the sewing-pattern-generator skill "))
    ET.SubElement(root, "version").text = "0.3.4"
    ET.SubElement(root, "read-only").text = "false"
    ET.SubElement(root, "notes").text = notes or f"Exported {_dt.date.today().isoformat()}"
    ET.SubElement(root, "unit").text = unit
    ET.SubElement(root, "pm_system").text = "998"
    pers = ET.SubElement(root, "personal")
    ET.SubElement(pers, "family-name").text = family_name
    ET.SubElement(pers, "given-name").text = given_name
    ET.SubElement(pers, "birth-date").text = "1800-01-01"
    ET.SubElement(pers, "gender").text = gender
    ET.SubElement(pers, "email").text = ""
    body = ET.SubElement(root, "body-measurements")
    div = TO_MM[unit]
    for key, std in NAME_MAP.items():
        if key in measures_mm and measures_mm[key]:
            v = measures_mm[key] / div
            ET.SubElement(body, "m", name=std, value=f"{v:.2f}".rstrip("0").rstrip("."))
    ET.indent(root, space="    ")
    ET.ElementTree(root).write(path, encoding="UTF-8", xml_declaration=True)
    return path
