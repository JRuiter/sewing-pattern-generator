"""Construction values: the named intermediate values of a draft, visible and overridable.

Garment modules compute derived values (hip width with ease, crotch extensions, rise, …)
from the body measurements. Recording them here gives the user a table of
"what was drafted from what" in the report, and lets any recorded value be overridden
via the option ``construction`` (values in mm), e.g.::

    {"options": {"construction": {"back_crotch_extension": 75, "rise": 245}}}

This is the hook for fit adjustments after a toile ("seat too tight" → larger back
crotch extension) without touching the module code.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Value:
    name: str
    value: float          # mm (or a plain number for unit "")
    formula: str          # how it was derived, human readable
    unit: str = "mm"
    overridden: bool = False
    computed: float | None = None   # the drafted value when overridden


class Construction:
    def __init__(self, overrides: dict | None = None):
        self.overrides = {k: float(v) for k, v in (overrides or {}).items()}
        self.values: list[Value] = []
        self._used: set[str] = set()

    def val(self, name: str, computed: float, formula: str, unit: str = "mm") -> float:
        """Record a value; return the override if one was given for `name`."""
        if name in self.overrides:
            v = self.overrides[name]
            self.values.append(Value(name, v, formula, unit, True, float(computed)))
            self._used.add(name)
            return v
        self.values.append(Value(name, float(computed), formula, unit))
        return float(computed)

    def unknown_overrides(self) -> list[str]:
        return sorted(set(self.overrides) - self._used)

    def rows(self) -> list[dict]:
        return [asdict(v) for v in self.values]


def to_markdown(rows: list[dict], unknown: list[str] | None = None) -> str:
    from i18n import num, t
    if not rows:
        return ""

    def cm(v):
        return num(f"{v / 10:.1f}") + " cm"
    lines = ["### " + t("Construction values"), "",
             t("Override any of these with the option `construction`, values in mm")
             + " (" + t("e.g.") + " `{\"construction\": {\"" + rows[0]["name"] + "\": "
             + f"{rows[0]['value']:.0f}" + "}}`).", "",
             "| " + " | ".join(t(h) for h in ("Name", "Value", "Derived from", "Note")) + " |", "|---|---|---|---|"]
    for r in rows:
        v = cm(r["value"]) if r["unit"] == "mm" else num(f"{r['value']:g}")
        note = ""
        if r["overridden"]:
            c = r["computed"]
            note = t("overridden (drafted:") + " " + (cm(c) if r["unit"] == "mm" else num(f"{c:g}")) + ")"
        lines.append(f"| `{r['name']}` | {v} | {t(r['formula'])} | {note} |")
    if unknown:
        lines += ["", "> ⚠️ " + t("Unknown construction value(s) ignored:") + " " + ", ".join(f"`{u}`" for u in unknown)]
    return "\n".join(lines)
