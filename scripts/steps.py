"""Structured sewing steps: one action per step, the data behind the IKEA-style booklet.

A garment module describes its construction as a list of :class:`Step` objects
(``assembly(pattern)``). Every step is one action ("Sew the side seams", "Fold the
band in half") with:

* ``title``    the action, imperative, a few words (printed big next to the step number)
* ``text``     at most one sentence of detail (what goes where, which notch, how far)
* ``diagram``  how the step is drawn (see ``diagrams.DIAGRAMS``), from the real pieces
* ``seams``    seam names of the seam graph (``Pattern.seams``, matched by prefix)
* ``edges``    ``(piece, edge)`` pairs for steps on a single edge (hem, fold, topstitch)
* ``stitch``   the kind of stitching (seam / finish / hem / topstitch / baste / elastic /
  zip / hand / press). Which machine and which stitch settings that means is decided by
  :func:`tool_for` from the machines the user owns (option ``machines``), so the same step
  list gives an overlocker step for one user and a zigzag step for another.

``sewing_steps(pattern)`` of a module (plain text, one string per step) is derived from
the steps with :func:`as_texts`, so the Markdown instructions and the booklet always say
the same thing.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import ease as E

# --------------------------------------------------------------------------- model

STITCH_KINDS = ("seam", "band", "finish", "hem", "topstitch", "baste", "gather", "elastic", "zip", "hand",
                "press", "")


@dataclass
class Step:
    title: str
    text: str = ""
    diagram: str = "icon"                       # see diagrams.DIAGRAMS
    seams: list[str] = field(default_factory=list)
    edges: list[tuple[str, str]] = field(default_factory=list)
    pieces: list[str] = field(default_factory=list)
    stitch: str = ""                            # see STITCH_KINDS
    repeat: int = 1                             # ×2: do it on both legs / sleeves
    tip: str = ""                               # warning or hint (the "!" box)
    section: str = ""                           # group heading (Pockets, Waistband, …)
    amount: float = 0.0                         # mm: hem depth, fold distance, opening …
    stretch: bool = False                       # stretch the band while sewing
    data: dict = field(default_factory=dict)    # extra drawing hints

    def as_text(self, options: dict | None = None) -> str:
        """One line of the Markdown instructions."""
        parts = [f"**{self.title}**" + ("." if not self.title.endswith(("!", ".", "?")) else "")]
        if self.text:
            parts.append(self.text)
        tool = tool_for(options or {}, self.stitch, self.data.get("knit")) if self.stitch else None
        if tool and tool.get("phrase"):
            parts.append(f"({tool['phrase']})")
        if self.repeat > 1:
            parts.append(f"Do this {_times(self.repeat)}.")
        if self.tip:
            parts.append(f"Tip: {self.tip}")
        return " ".join(parts)


def _times(n: int) -> str:
    return {2: "twice", 3: "three times", 4: "four times"}.get(n, f"{n} times")


def as_texts(steps: list[Step], options: dict | None = None) -> list[str]:
    return [s.as_text(options) for s in steps]


# --------------------------------------------------------------------------- machines

MACHINE_NAMES = {
    "sewing": "Sewing machine",
    "overlocker": "Overlocker",
    "coverstitch": "Coverstitch machine",
    "iron": "Iron",
    "hand": "Hand needle",
}


def owned_machines(options: dict) -> set[str] | None:
    """The machines the user owns (option ``machines``, see machines.py), or None if not specified."""
    import machines as MC
    m = MC.of(options)
    return None if m is None else set(m)


def _settings(d: dict) -> str:
    w, ln = d.get("width_mm"), d.get("length_mm")
    if w and ln:
        return f" {w:g} × {ln:g} mm"
    if ln:
        return f" {ln:g} mm"
    return ""


def tool_for(options: dict, kind: str, knit: bool | None = None) -> dict:
    """Machine and stitch for a kind of stitching.

    Returns ``{"machine": key, "name": ..., "stitch": ..., "phrase": ...}``; ``machine`` is
    one of ``MACHINE_NAMES``. When the user named their machines (option ``machines``),
    seams, edge finishes, hems and topstitching come from ``machines.method``; otherwise, and
    for basting, gathering, elastic, zips, hand sewing and pressing, the rules below apply
    (a plain sewing machine with zigzag).
    """
    import machines as MC
    if knit is None:
        knit = E.fabric_info((options or {}).get("fabric", "jersey"), (options or {}).get("stretch"))[2]
    if kind in MC.KINDS and MC.of(options) is not None:
        d = MC.method(options, kind, bool(knit))
        if d:
            return {"machine": d["machine"], "name": MACHINE_NAMES.get(d["machine"], d["machine"]),
                    "stitch": d["stitch"] + _settings(d), "phrase": d["text"]}
    own = owned_machines(options)
    if own is None and kind in ("seam", "band", "hem"):
        # machines not known: the picture shows the sewing machine, the text stays generic
        if kind == "hem":
            phrase = MC.hem_phrase(options, bool(knit)).removeprefix("with ")
            stitch = "twin needle 4 mm, stitch 3 mm" if knit else "straight stitch 3 mm"
        else:
            phrase = MC.seam_phrase(options, bool(knit)).removeprefix("with ")
            stitch = "narrow zigzag 1 × 2.5 mm (or overlocker)" if knit else "straight stitch 2.5 mm"
        return {"machine": "sewing", "name": MACHINE_NAMES["sewing"], "stitch": stitch, "phrase": phrase}
    have = (lambda k: k in own) if own is not None else (lambda k: False)
    stretch_stitch = have("stretch_stitch")
    twin = have("twin_needle") or own is None

    def res(machine, stitch, phrase=None):
        return {"machine": machine, "name": MACHINE_NAMES[machine], "stitch": stitch,
                "phrase": phrase if phrase is not None else f"{MACHINE_NAMES[machine].lower()}: {stitch}"}

    if kind in ("seam", "band"):
        if knit and have("overlocker"):
            return res("overlocker", "4-thread overlock", "overlocker, 4-thread")
        if knit and stretch_stitch:
            return res("sewing", "stretch stitch (lightning bolt)")
        if knit:
            return res("sewing", "narrow zigzag 1 × 2.5 mm")
        return res("sewing", "straight stitch 2.5 mm")
    if kind == "finish":
        if have("overlocker"):
            return res("overlocker", "3-thread overlock along the edge", "overlocker, 3-thread")
        return res("sewing", "wide zigzag 4 × 1.5 mm over the edge")
    if kind == "hem":
        if knit and have("coverstitch"):
            return res("coverstitch", "coverstitch, 2 needles", "coverstitch machine")
        if knit and twin:
            return res("sewing", "twin needle 4 mm, stitch 3 mm")
        if knit:
            return res("sewing", "narrow zigzag 1.5 × 3 mm")
        return res("sewing", "straight stitch 3 mm")
    if kind == "topstitch":
        if knit and have("coverstitch"):
            return res("coverstitch", "coverstitch, 2 needles", "coverstitch machine")
        if knit and twin:
            return res("sewing", "twin needle 4 mm, stitch 3 mm")
        return res("sewing", "straight stitch 3 mm")
    if kind == "baste":
        return res("sewing", "longest straight stitch, no backstitch")
    if kind == "gather":
        return res("sewing", "2 rows of the longest straight stitch, loose ends")
    if kind == "elastic":
        if have("straight_only"):
            return res("sewing", "straight stitch 3 mm, stretching the elastic")
        return res("sewing", "wide zigzag 4 × 2.5 mm")
    if kind == "zip":
        return res("sewing", "straight stitch 2.5 mm, zipper foot")
    if kind == "hand":
        return res("hand", "ladder stitch", "by hand, ladder stitch")
    if kind == "press":
        return res("iron", "steam" if knit else "steam, cotton setting", "")
    return {}


def needs_finish(options: dict, knit: bool) -> bool:
    """Is a separate "finish the seam allowances" step needed after a seam?

    Woven: always. Knit: only when the user's machines are known and the seam is not sewn on
    the overlocker (then the allowances are finished together with a wide zigzag)."""
    if not knit:
        return True
    import machines as MC
    if MC.of(options) is None:
        return False
    d = MC.method(options, "finish", True)
    return bool(d) and d["machine"] != "overlocker" and d["stitch"] != "none"


def machines_needed(steps: list[Step], options: dict, knit: bool | None = None) -> list[dict]:
    """The distinct tools a step list uses, in first-use order (for the tools page)."""
    out: dict[str, dict] = {}
    for s in steps:
        if not s.stitch:
            continue
        t = tool_for(options, s.stitch, s.data.get("knit", knit))
        if t and t["machine"] not in out:
            out[t["machine"]] = t
    return list(out.values())


# --------------------------------------------------------------------------- builders
# Small helpers so the garment modules read like a list of actions.

def cm(mm: float) -> str:
    return f"{mm / 10:g} cm" if mm >= 15 else f"{mm:.0f} mm"


def seam(title: str, seams: list[str], text: str = "", **kw) -> Step:
    """Pin two pieces right sides together and sew one or more seams of the seam graph."""
    kw.setdefault("stitch", "seam")
    return Step(title, text, "seam", seams=list(seams), **kw)


def finish(title: str, edges: list[tuple[str, str]], text: str = "", **kw) -> Step:
    kw.setdefault("stitch", "finish")
    return Step(title, text, "edge", edges=list(edges), **kw)


def hem(title: str, edges: list[tuple[str, str]], amount: float, text: str = "", **kw) -> Step:
    kw.setdefault("stitch", "hem")
    return Step(title, text, "hem", edges=list(edges), amount=amount, **kw)


def press(title: str, edges: list[tuple[str, str]], text: str = "", amount: float = 0.0, **kw) -> Step:
    kw.setdefault("stitch", "press")
    return Step(title, text, "press", edges=list(edges), amount=amount, **kw)


def topstitch(title: str, edges: list[tuple[str, str]], amount: float, text: str = "", **kw) -> Step:
    kw.setdefault("stitch", "topstitch")
    return Step(title, text, "topstitch", edges=list(edges), amount=amount, **kw)


def ring(title: str, piece: str, text: str = "", **kw) -> Step:
    """Close a band into a ring across its short ends (right sides together)."""
    kw.setdefault("stitch", "seam")
    return Step(title, text, "ring", pieces=[piece], **kw)


def fold_band(title: str, piece: str, text: str = "", **kw) -> Step:
    """Fold a band lengthwise, wrong sides together (raw edges meet)."""
    kw.setdefault("stitch", "press")
    return Step(title, text, "fold", pieces=[piece], **kw)


def quarter(title: str, piece: str, target: str, text: str = "", **kw) -> Step:
    """Divide band and opening into quarters and mark them with pins."""
    return Step(title, text, "quarter", pieces=[piece], data={"target": target, **kw.pop("data", {})}, **kw)


def attach_band(title: str, piece: str, seams: list[str], target: str, text: str = "", **kw) -> Step:
    """Sew a ring-shaped band to an opening, stretching the band."""
    kw.setdefault("stitch", "band")
    kw.setdefault("stretch", True)
    return Step(title, text, "attach", pieces=[piece], seams=list(seams),
                data={"target": target, **kw.pop("data", {})}, **kw)


def gather(title: str, edges: list[tuple[str, str]], text: str = "", **kw) -> Step:
    kw.setdefault("stitch", "gather")
    return Step(title, text, "gather", edges=list(edges), **kw)


def place(title: str, piece: str, on: str, mark: str, text: str = "", **kw) -> Step:
    """Place a piece (pocket) onto a placement mark of another piece and stitch it on."""
    kw.setdefault("stitch", "topstitch")
    return Step(title, text, "place", pieces=[piece, on], data={"mark": mark, **kw.pop("data", {})}, **kw)


def icon(title: str, picture: str, text: str = "", **kw) -> Step:
    """A step drawn as a pictogram (turn, thread elastic, snip notches, done …)."""
    return Step(title, text, "icon", data={"picture": picture, **kw.pop("data", {})}, **kw)


# --------------------------------------------------------------------------- common steps

def prepare(pattern) -> list[Step]:
    """Steps before sewing (same for all garments)."""
    knit = E.fabric_info(pattern.options.get("fabric", "jersey"), pattern.options.get("stretch"))[2]
    return [
        icon("Pre-wash the fabric", "wash",
             "Wash and dry it the way you will wash the garment later, so it shrinks now, not after sewing.",
             section="Prepare"),
        icon("Cut out all pieces", "cut",
             "Follow the cutting layout; grainline arrows parallel to the selvage.", section="Prepare"),
        icon("Snip the notches", "notch", "Cut 3–4 mm into the seam allowance at every notch.",
             section="Prepare"),
        icon("Set up the machine", "needle",
             ("Jersey/stretch needle 75–80, polyester thread." if knit else
              "Universal needle 80, polyester thread.") + " Sew a test seam on a scrap first.",
             section="Prepare"),
    ]


def done(text: str = "Press all seams.", **kw) -> Step:
    return icon("Done!", "done", text, section="Finish", **kw)


def covered_seams(pattern, steps: list[Step]) -> set[str]:
    """Names of the seams of the seam graph that the steps sew."""
    names = set()
    for s in steps:
        for sm in pattern.seams:
            if any(sm["name"].startswith(p) for p in s.seams):
                names.add(sm["name"])
    return names


def resolve_seams(pattern, step: Step) -> list[dict]:
    return [sm for sm in pattern.seams if any(sm["name"].startswith(p) for p in step.seams)]


def number(steps: list[Step]) -> list[tuple[int, Step]]:
    return list(enumerate(steps, 1))


def assembly(pattern) -> list[Step]:
    """All steps for a pattern: preparation + the garment module's assembly."""
    from garments import get
    mod = get(pattern.garment)
    if hasattr(mod, "assembly"):
        body = mod.assembly(pattern)
    elif hasattr(mod, "sewing_steps"):                    # legacy text-only module
        body = [Step(t.split("**")[1].rstrip(":") if t.startswith("**") else t,
                     t.split("**", 2)[2].strip() if t.startswith("**") else "") for t in mod.sewing_steps(pattern)]
    else:
        body = [Step("Sew the pieces together", "Right sides together, matching the notches.", stitch="seam")]
    knit = E.fabric_info(pattern.options.get("fabric", "jersey"), pattern.options.get("stretch"))[2]
    for s in body:
        s.data.setdefault("knit", knit)
    return prepare(pattern) + body
