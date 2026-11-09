"""The sewist's machines: which ones there are, and how each kind of step is sewn with them.

Options (spec `options.machines`, CLI `--machines`, a profile or the workshop file):
a list (or comma-separated string) of

| key | meaning |
|---|---|
| `sewing` | household sewing machine with straight **and zigzag** stitch (always assumed) |
| `straight_only` | the sewing machine has **only** a straight stitch (old/industrial machine) |
| `stretch_stitch` | the sewing machine has a stretch stitch (lightning bolt / triple stretch) |
| `twin_needle` | a twin needle (stretch twin needle 4 mm) fits the sewing machine |
| `overlocker` | overlocker / serger (3/4-thread) |
| `coverstitch` | coverstitch machine (or a combi machine with cover stitch) |
| `hand` | hand needle; listed **without** any sewing-machine key it means "no sewing machine" |
| `no_sewing_machine` | there is no sewing machine (alias `overlocker_only` = overlocker + this) |

Without a sewing machine (e.g. `["overlocker", "hand"]`) every seam and edge finish is
sewn on the overlocker (7.5 mm seam allowance, woven fabric too) and every step that needs
a straight stitch is done **by hand**: topstitching → back stitch, hems and casings →
blind/hem stitch, basting → tacking stitch, bar tacks → hand bar tack, joining elastic → a
box of hand stitches.

German and common aliases work too (`overlock`, `serger`, `coverlock`, `zickzack`,
`zwillingsnadel`, …). Without the option (`None`) the instructions stay generic
("overlocker or narrow zigzag"), as before.

What changes with the machines:
- **Seam allowances** (only when the user did not set them): knit seams sewn on the
  overlocker get 7.5 mm (the knife trims, a wider allowance would be cut off anyway); woven
  seams on a straight-stitch-only machine get 15 mm for French seams. Doll clothes keep
  their own narrow allowances.
- **Sewing steps:** every seam/hem phrase in the garment modules comes from
  `seam_phrase` / `hem_phrase`, so the steps name the user's machine.
- **Instructions:** a "Your machines" section with one row per kind of step (seam, edge
  finish, hem, topstitching, bands) and the machine settings.

For the step model (`method(options, kind, knit)`) every kind of step returns a dict
`{"machine", "stitch", "width_mm", "length_mm", "needle", "text"}`; `tool_for` gives just the
machine (for an icon).
"""
from __future__ import annotations

KEYS = ("sewing", "straight_only", "stretch_stitch", "twin_needle", "overlocker", "coverstitch", "hand",
        "no_sewing_machine")
SEWING_MACHINE_KEYS = ("sewing", "straight_only", "stretch_stitch", "twin_needle")

LABELS = {
    "sewing": "Sewing machine (straight stitch and zigzag)",
    "straight_only": "Sewing machine with straight stitch only",
    "stretch_stitch": "Stretch stitch on the sewing machine",
    "twin_needle": "Twin needle",
    "overlocker": "Overlocker / serger",
    "coverstitch": "Coverstitch machine",
    "hand": "Hand needle",
    "no_sewing_machine": "No sewing machine",
}

ALIASES = {
    "sewing": "sewing", "sewing_machine": "sewing", "machine": "sewing", "naehmaschine": "sewing",
    "nähmaschine": "sewing", "zigzag": "sewing", "zickzack": "sewing",
    "straight_only": "straight_only", "straight": "straight_only", "geradstich": "straight_only",
    "stretch_stitch": "stretch_stitch", "stretch": "stretch_stitch", "stretchstich": "stretch_stitch",
    "lightning": "stretch_stitch", "triple_stretch": "stretch_stitch",
    "twin_needle": "twin_needle", "twin": "twin_needle", "double_needle": "twin_needle",
    "zwillingsnadel": "twin_needle",
    "overlocker": "overlocker", "overlock": "overlocker", "serger": "overlocker", "overlockmaschine": "overlocker",
    "coverstitch": "coverstitch", "cover": "coverstitch", "coverlock": "coverstitch",
    "covermaschine": "coverstitch", "cover_stitch": "coverstitch",
    "hand": "hand", "hand_needle": "hand", "needle": "hand", "handnadel": "hand", "von_hand": "hand",
    "no_sewing_machine": "no_sewing_machine", "no_sewing": "no_sewing_machine", "none": "no_sewing_machine",
    "keine_naehmaschine": "no_sewing_machine", "keine_nähmaschine": "no_sewing_machine",
    "overlocker_only": "overlocker_only", "nur_overlock": "overlocker_only", "serger_only": "overlocker_only",
}

KINDS = ("seam", "finish", "hem", "topstitch", "band")

OVERLOCK_SA_MM = 7.5      # knit seams sewn on the overlocker
FRENCH_SEAM_SA_MM = 15.0  # woven seams on a straight-stitch-only machine


def parse(value) -> frozenset[str] | None:
    """List/comma string → set of machine keys (None = not specified).

    A sewing machine is assumed unless the list says there is none: `no_sewing_machine`
    (`overlocker_only`), or `hand` without any sewing-machine key."""
    if value is None or value == "":
        return None
    items = value.split(",") if isinstance(value, str) else list(value)
    out = set()
    for it in items:
        k = str(it).strip().lower().replace("-", "_").replace(" ", "_")
        if not k:
            continue
        if k not in ALIASES:
            raise ValueError(f"Unknown machine '{it}'. Allowed: {', '.join(KEYS)}, overlocker_only")
        if ALIASES[k] == "overlocker_only":
            out |= {"overlocker", "no_sewing_machine"}
        else:
            out.add(ALIASES[k])
    if "hand" in out and not out & set(SEWING_MACHINE_KEYS):
        out.add("no_sewing_machine")
    if "no_sewing_machine" in out:
        out -= set(SEWING_MACHINE_KEYS)
        out.add("hand")
    else:
        out.add("sewing")
    return frozenset(out)


def has_sewing_machine(m) -> bool:
    return m is not None and "no_sewing_machine" not in m


def of(options: dict | None) -> frozenset[str] | None:
    return parse((options or {}).get("machines"))


def to_list(machines) -> list[str] | None:
    """For options/pattern.json: sorted list in the order of KEYS."""
    m = parse(machines) if not isinstance(machines, frozenset) else machines
    return None if m is None else [k for k in KEYS if k in m]


def _zigzag(m) -> bool:
    return "straight_only" not in m


def _d(machine, stitch, text, width=None, length=None, needle=None):
    return {"machine": machine, "stitch": stitch, "width_mm": width, "length_mm": length,
            "needle": needle, "text": text}


def method(options: dict | None, kind: str, knit: bool) -> dict | None:
    """How a kind of step (seam, finish, hem, topstitch, band) is sewn with the user's machines.

    None if the machines are not known (generic wording)."""
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {', '.join(KINDS)}")
    m = of(options)
    if m is None:
        return None
    needle = "jersey/stretch needle 80" if knit else "universal needle 80"
    if not has_sewing_machine(m):
        return _no_machine(m, kind, knit)
    if kind == "seam":
        if knit:
            if "overlocker" in m:
                return _d("overlocker", "4-thread overlock", "with the overlocker (4-thread overlock stitch, "
                          "differential feed about 1.3 so the seam does not wave)", width=6.0, length=3.0,
                          needle="overlocker needles (ELx705 or as the manual says)")
            if "stretch_stitch" in m:
                return _d("sewing", "stretch stitch", "with the stretch stitch (lightning bolt) of the sewing "
                          "machine", length=2.5, needle=needle)
            if _zigzag(m):
                return _d("sewing", "narrow zigzag", "with a narrow zigzag (width 1 mm, length 2.5 mm)",
                          width=1.0, length=2.5, needle=needle)
            return _d("sewing", "long straight stitch", "with a long straight stitch (3.5 mm), stretching the "
                      "fabric slightly as you sew, and a second row 2 mm beside it (a plain straight stitch "
                      "would pop when the knit stretches)", length=3.5, needle=needle)
        if _zigzag(m) or "overlocker" in m:
            return _d("sewing", "straight stitch", "with a straight stitch (2.5 mm)", length=2.5, needle=needle)
        return _d("sewing", "French seam", "as a French seam: sew wrong sides together 6 mm from the edge, "
                  "trim to 3 mm, fold right sides together and sew again 9 mm from the fold",
                  length=2.5, needle=needle)
    if kind == "finish":
        if knit:
            if "overlocker" in m:
                return _d("overlocker", "already finished", "nothing to do: the overlock seam is already "
                          "finished", needle=None)
            if _zigzag(m):
                return _d("sewing", "wide zigzag", "press both allowances to one side and finish them together "
                          "with a wide zigzag (width 4 mm, length 2 mm)", width=4.0, length=2.0, needle=needle)
            return _d("sewing", "none", "knit fabric does not fray: the edges can stay raw", needle=needle)
        if "overlocker" in m:
            return _d("overlocker", "3-thread overlock", "finish each allowance with the overlocker (3-thread) "
                      "and press the seam open", width=5.0, length=2.5,
                      needle="overlocker needles")
        if _zigzag(m):
            return _d("sewing", "zigzag", "finish each allowance edge with a zigzag (width 4 mm, length 2 mm, "
                      "or the three-step zigzag) and press the seam open", width=4.0, length=2.0, needle=needle)
        return _d("sewing", "French seam", "French seams enclose the edges; where that is not possible, trim "
                  "the edges with pinking shears", needle=needle)
    if kind == "hem":
        if knit:
            if "coverstitch" in m:
                return _d("coverstitch", "2-needle cover stitch", "with the coverstitch machine from the right "
                          "side (2 needles, 4 mm apart), catching the raw edge underneath", width=4.0, length=3.0,
                          needle="coverstitch needles")
            if "twin_needle" in m:
                return _d("sewing", "twin needle", "with the stretch twin needle (4 mm) from the right side, "
                          "stitch length 3 mm", width=4.0, length=3.0, needle="stretch twin needle 4.0/75")
            if "stretch_stitch" in m:
                return _d("sewing", "stretch stitch", "with the stretch stitch from the right side", length=2.5,
                          needle=needle)
            if _zigzag(m):
                return _d("sewing", "narrow zigzag", "with a narrow zigzag (width 1.5 mm, length 3 mm) from the "
                          "right side", width=1.5, length=3.0, needle=needle)
            return _d("sewing", "long straight stitch", "with a long straight stitch (4 mm) while stretching "
                      "the hem gently; for a hem that stretches a lot, hand-sew it with a catch stitch",
                      length=4.0, needle=needle)
        return _d("sewing", "straight stitch", "with a straight stitch (2.5 mm) close to the inner fold",
                  length=2.5, needle=needle)
    if kind == "topstitch":
        if knit and "coverstitch" in m:
            return _d("coverstitch", "2-needle cover stitch", "with the coverstitch machine", width=4.0,
                      length=3.0, needle="coverstitch needles")
        if knit and "twin_needle" in m:
            return _d("sewing", "twin needle", "with the twin needle", width=4.0, length=3.0,
                      needle="stretch twin needle 4.0/75")
        if knit and _zigzag(m):
            return _d("sewing", "narrow zigzag", "with a narrow zigzag (width 1 mm, length 3 mm) or the "
                      "stretch stitch", width=1.0, length=3.0, needle=needle)
        return _d("sewing", "straight stitch", "with a straight stitch (3 mm)", length=3.0, needle=needle)
    # band: cuffs, waistbands, neckbands sewn on while stretching
    if not knit:
        return _d("sewing", "straight stitch", "with a straight stitch (2.5 mm)", length=2.5, needle=needle)
    if "overlocker" in m:
        return _d("overlocker", "4-thread overlock", "with the overlocker, stretching only the band",
                  width=6.0, length=3.0, needle="overlocker needles")
    return method(options, "seam", knit)


HAND_NEEDLE = "hand sewing needle, polyester thread"


def _no_machine(m, kind: str, knit: bool) -> dict:
    """Overlocker (and maybe coverstitch) but no sewing machine: straight stitches by hand."""
    ov = "overlocker" in m
    if kind in ("seam", "band"):
        if ov:
            return _d("overlocker", "4-thread overlock", "with the overlocker (4-thread overlock stitch"
                      + (", differential feed about 1.3" if knit else ", differential 1.0") + ")"
                      + (", stretching only the band" if kind == "band" and knit else ""),
                      width=6.0, length=3.0, needle="overlocker needles (ELx705 or as the manual says)")
        return _d("hand", "back stitch", "by hand with a back stitch (stitches 2–3 mm)", length=2.5,
                  needle=HAND_NEEDLE)
    if kind == "finish":
        if ov:
            return _d("overlocker", "already finished", "nothing to do: the overlock seam is already finished; "
                      "press the allowances to one side", needle=None)
        return _d("hand", "overcast stitch", "overcast the edges by hand", needle=HAND_NEEDLE)
    if kind == "hem":
        if knit and "coverstitch" in m:
            return _d("coverstitch", "2-needle cover stitch", "with the coverstitch machine from the right side",
                      width=4.0, length=3.0, needle="coverstitch needles")
        return _d("hand", "blind stitch", "by hand with a blind (hem) stitch, catching only a thread or two of "
                  "the outer fabric" + ("; finish the raw edge with the overlocker first" if ov else ""),
                  length=5.0, needle=HAND_NEEDLE)
    # topstitch
    if knit and "coverstitch" in m:
        return _d("coverstitch", "2-needle cover stitch", "with the coverstitch machine", width=4.0, length=3.0,
                  needle="coverstitch needles")
    return _d("hand", "back stitch", "by hand with a back stitch (stitches 2–3 mm, visible from the right side)",
              length=2.5, needle=HAND_NEEDLE)


def tool_for(options: dict | None, kind: str, knit: bool) -> str | None:
    """'sewing' | 'overlocker' | 'coverstitch' for a kind of step (None if unknown)."""
    d = method(options, kind, knit)
    return None if d is None else d["machine"]


# --------------------------------------------------------------- phrases for the garment modules

GENERIC_SEAM_KNIT = "with an overlocker or a narrow zigzag/stretch stitch"
GENERIC_SEAM_WOVEN = "with a straight stitch, then finish the edges"
GENERIC_HEM_KNIT = "with a twin needle/coverstitch"
GENERIC_HEM_WOVEN = "with a straight stitch"


def seam_phrase(options: dict | None, knit: bool) -> str:
    """'with …' for a seam incl. its edge finish (generic wording if the machines are unknown)."""
    d = method(options, "seam", knit)
    if d is None:
        return GENERIC_SEAM_KNIT if knit else GENERIC_SEAM_WOVEN
    if knit:
        f = method(options, "finish", knit)
        if f and f["stitch"] == "wide zigzag":
            return d["text"] + ", then finish both allowances together with a wide zigzag"
        return d["text"]
    if d["stitch"] == "French seam" or d["machine"] == "overlocker":
        return d["text"]
    f = method(options, "finish", knit)
    tail = "the overlocker" if f and f["machine"] == "overlocker" else "a zigzag"
    return d["text"] + f", then finish the edges with {tail}"


def hem_phrase(options: dict | None, knit: bool) -> str:
    d = method(options, "hem", knit)
    if d is None:
        return GENERIC_HEM_KNIT if knit else GENERIC_HEM_WOVEN
    return d["text"]


def topstitch_phrase(options: dict | None, knit: bool, default: str) -> str:
    d = method(options, "topstitch", knit)
    return default if d is None else d["text"]


# --------------------------------------------------------------- seam allowances

def allowance_defaults(options: dict | None, knit: bool) -> dict:
    """Seam allowance options that follow from the machines (only where the user set none)."""
    o = options or {}
    m = of(o)
    if (m is None or o.get("seam_allowance_mm") is not None or o.get("sa") is not None
            or str(o.get("seam_allowance", "")).lower() == "none"):
        return {}
    if "overlocker" in m and (knit or not has_sewing_machine(m)):
        return {"seam_allowance_mm": OVERLOCK_SA_MM}
    if not knit and "straight_only" in m:
        return {"seam_allowance_mm": FRENCH_SEAM_SA_MM}
    return {}


# --------------------------------------------------------------- instructions section

ROW_LABELS = {"seam": "Seams", "finish": "Edge finish", "hem": "Hems", "topstitch": "Topstitching",
              "band": "Cuffs, bands, waistband"}
MACHINE_NAMES = {"sewing": "Sewing machine", "overlocker": "Overlocker", "coverstitch": "Coverstitch",
                 "hand": "Hand needle"}

OVERLOCKER_HINTS = [
    "Pull pins out before they reach the knife (clips are safer at the overlocker).",
    "CURVES",
    "Leave a thread chain of 5 cm at the end of every seam; thread it back under the stitches with a "
    "darning needle or secure it with a drop of seam sealant.",
]


def curved_parts(pattern) -> str:
    """The curved seams of this garment, for the overlocker hints: "crotch, pocket bag", "armhole,
    neckline" or "" (no typical curves)."""
    keys = {pc.key for pc in pattern.pieces}
    names = " ".join(sm["name"].lower() for sm in getattr(pattern, "seams", []))
    if "crotch" in names or pattern.garment.startswith("pants"):
        return "crotch, pocket bag" if "pocket bag" in names or "pocket_bag" in keys else "crotch"
    if "armhole" in names or "raglan" in names or "sleeve" in keys:
        return "armhole, neckline"
    if "neck" in names:
        return "neckline"
    return ""


def curves_hint(pattern) -> str:
    c = curved_parts(pattern)
    return (f"Sew curves ({c}) slowly and guide only the fabric just in front of the presser foot." if c else
            "Sew curves slowly and guide only the fabric just in front of the presser foot.")


def missing_tips(m: frozenset[str], knit: bool) -> list[str]:
    tips = []
    if not has_sewing_machine(m):
        return tips
    if knit and "overlocker" not in m and "straight_only" not in m:
        tips.append("No overlocker: that is fine. Sew knit seams with the narrow zigzag or stretch stitch; "
                    "the fabric does not fray, so the edges need no further finishing (optional wide zigzag).")
    if knit and "coverstitch" not in m and "twin_needle" not in m:
        tips.append("A stretch twin needle (4 mm, about 5 €) fits almost every household machine and gives hems "
                    "that look like a coverstitch.")
    if knit and "straight_only" in m:
        tips.append("A straight-stitch-only machine is not ideal for knits: seams can pop when stretched. Prefer "
                    "a woven fabric, or use the double row of long straight stitches described below.")
    return tips


HAND_PARTS = (("topstitch", "topstitching with a back stitch"), ("hem", "hems and casings with a blind stitch"),
              ("baste", "basting with a tacking stitch"), ("bartack", "bar tacks by hand"),
              ("elastic", "elastic ends with a box of hand stitches"))


def markdown(pattern, kinds: set[str] | None = None) -> str | None:
    """'Your machines' section for the sewing instructions (None if the machines are unknown).
    ``kinds``: the stitch kinds the steps use; the table and the hand-sewing note then list only
    those (no "cuffs, bands, waistband" row for a bag)."""
    import ease as E
    from i18n import num
    from i18n import t as T
    o = pattern.options
    m = of(o)
    if m is None:
        return None
    knit = E.fabric_info(o.get("fabric", "jersey"), o.get("stretch"))[2]
    have = [k for k in KEYS if k in m and not (k == "sewing" and "straight_only" in m)]
    lines = [T("You told me you sew with:") + " " + ", ".join(T(LABELS[k]) for k in have) + ".", ""]
    if not has_sewing_machine(m):
        parts = [p for k, p in HAND_PARTS if kinds is None or k in kinds]
        if kinds is None or len(parts) == len(HAND_PARTS):
            lines += [T("There is no sewing machine, so every step that needs a straight stitch is done **by hand**: "
                        "topstitching with a back stitch, hems and casings with a blind stitch, basting with a "
                        "tacking stitch, bar tacks by hand, elastic ends with a box of hand stitches."), ""]
        elif parts:
            lines += [T("There is no sewing machine, so every step that needs a straight stitch is done **by hand**:")
                      + " " + ", ".join(T(p) for p in parts) + ".", ""]
    lines += ["| " + " | ".join(T(h) for h in ("Step", "Machine", "Stitch", "Settings")) + " |", "|---|---|---|---|"]
    for kind in KINDS:
        if kinds is not None and kind not in kinds:
            continue
        d = method(o, kind, knit)
        assert d is not None
        st = []
        if d["width_mm"]:
            st.append(T("width") + f" {num(d['width_mm'])} mm")
        if d["length_mm"]:
            st.append(T("length") + f" {num(d['length_mm'])} mm")
        if d["needle"]:
            st.append(T(d["needle"]))
        lines.append(f"| {T(ROW_LABELS[kind])} | {T(MACHINE_NAMES[d['machine']])} | {T(d['stitch'])} | "
                     f"{', '.join(st)} |")
    sa = o.get("_sa_from_machines")
    if sa == OVERLOCK_SA_MM:
        lines += ["", T("Seam allowance 7.5 mm because you sew the seams on the overlocker: guide the fabric so "
                        "the knife just skims the edge.")]
    elif sa == FRENCH_SEAM_SA_MM:
        lines += ["", T("Seam allowance 15 mm so every seam can be sewn as a French seam (6 mm + 9 mm).")]
    tips = [T(x) for x in missing_tips(m, knit)]
    if "overlocker" in m:
        tips += [T("At the overlocker:") + " " + T(curves_hint(pattern) if h == "CURVES" else h)
                 for h in OVERLOCKER_HINTS]
    if tips:
        lines += [""] + [f"- {x}" for x in tips]
    lines += ["", T("Test the stitch on a scrap of your fabric first (two layers, same direction as the seam).")]
    return "\n".join(lines)
