"""Structured sewing steps: one action per step, the data behind the illustrated booklet.

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

import re
from dataclasses import dataclass, field

import ease as E
import geometry as G

# --------------------------------------------------------------------------- model

STITCH_KINDS = ("seam", "band", "finish", "hem", "topstitch", "baste", "gather", "elastic", "zip", "hand",
                "bartack", "press", "")


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
    tip: str = ""                               # warning: the yellow "Important" box
    hint: str = ""                              # helpful hint: the green "Tip" box
    alt: str = ""                               # another way to do it: the blue "Alternative" box
    section: str = ""                           # group heading (Pockets, Waistband, …)
    amount: float = 0.0                         # mm: hem depth, fold distance, opening …
    stretch: bool = False                       # stretch the band while sewing
    data: dict = field(default_factory=dict)    # extra drawing hints

    def as_text(self, options: dict | None = None) -> str:
        """One line of the Markdown instructions."""
        from i18n import t
        title = t(self.title)
        parts = [f"**{title}**" + ("." if not title.endswith(("!", ".", "?")) else "")]
        if self.text:
            parts.append(t(self.text))
        tool = tool_for(options or {}, self.stitch, self.data.get("knit")) if self.stitch else None
        if tool and tool.get("phrase"):
            parts.append(f"({t(tool['phrase'])})")
        if self.repeat > 1:
            parts.append(t(f"Do this {_times(self.repeat)}."))
        if self.tip:
            parts.append(t("Tip:") + " " + t(self.tip))
        if self.hint:
            parts.append(t(self.hint))
        if self.alt:
            parts.append(t("Alternative:") + " " + t(self.alt))
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


# no sewing machine: what each straight-stitch kind of step becomes by hand
HAND_STITCHES = {
    "baste": ("tacking stitch, 1 cm long", "by hand with a tacking stitch (long running stitches)"),
    "gather": ("2 rows of running stitch", "by hand: two rows of running stitches, pull the threads"),
    "elastic": ("box of hand stitches", "overlap the ends and sew a box of small hand stitches through both"),
    "zip": ("back stitch", "by hand with a back stitch"),
    "bartack": ("hand bar tack", "by hand: 4–5 stitches on top of each other, then wrap them with buttonhole "
                "stitches"),
    "hand": ("ladder stitch", "by hand, ladder stitch"),
}


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
    if own is not None and not MC.has_sewing_machine(own) and kind in HAND_STITCHES:
        stitch, phrase = HAND_STITCHES[kind]
        return {"machine": "hand", "name": MACHINE_NAMES["hand"], "stitch": stitch, "phrase": phrase}
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
    if kind == "bartack":
        return res("sewing", "narrow zigzag 2 × 0.3 mm, 1 cm long", "with a bar tack (dense narrow zigzag)")
    if kind == "press":
        return res("iron", "steam" if knit else "steam, cotton setting", "")
    return {}


def needs_finish(options: dict, knit: bool) -> bool:
    """Is a separate "finish the seam allowances" step needed after a seam?

    Woven: yes, unless the seams are overlocked anyway (no sewing machine). Knit: no; knit does not
    fray, and an overlocker finishes while it sews."""
    import machines as MC
    m = MC.of(options)
    if not knit:
        # without a sewing machine the woven seams are overlocked, which finishes them
        return not (m is not None and not MC.has_sewing_machine(m) and "overlocker" in m)
    return False


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
    return f"{mm / 10:g} cm" if mm >= 15 else f"{round(mm, 1):g} mm"


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

def prepare(pattern, plans: dict | None = None) -> list[Step]:
    """Steps before sewing (same for all garments). With the cutting layout (``plans``) the cutting
    step shows the real layout and says how to cut (folded or single layer, mirrored pairs)."""
    knit = E.fabric_info(pattern.options.get("fabric", "jersey"), pattern.options.get("stretch"))[2]
    cut_text = "Follow the cutting layout; grainline arrows parallel to the selvage."
    if any(L_group(pc) == "Rib knit" for pc in pattern.pieces):
        cut_text += (" Rib knit: the ribs run along the grainline, so every band stretches along its length "
                     "(across the fabric).")
    modes = {pl.get("mode") for pl in (plans or {}).values()}
    if modes == {"single"}:
        hint = ("Single layer: cut the second piece of a pair with the paper piece turned over (printed side "
                "down).") if any(pc.cut_count >= 2 and not pc.on_fold for pc in pattern.pieces) else \
            "Cut with long strokes; keep the fabric flat on the table."
    else:
        hint = "Cut both layers at once with long strokes; keep the fabric flat on the table."
    return [
        icon("Pre-wash the fabric", "wash",
             "Wash and dry it the way you will wash the garment later, so it shrinks now, not after sewing.",
             section="Prepare"),
        icon("Cut out all pieces", "cut", cut_text, section="Prepare",
             tip=("Nap: no piece turned round, all with the waist up. Stroke the fabric to check the direction."
                  if E.has_nap(pattern.options) else ""),
             hint=hint, data={"plans": plans} if plans else {}),
    ] + ([icon("Snip the notches", "notch", "Cut 3–4 mm into the seam allowance at every notch.",
               section="Prepare", tip="Never deeper than half the seam allowance.")]
         if any(pc.notches for pc in pattern.pieces) else []) + [_setup_step(pattern, knit)]


def L_group(pc) -> str:
    import layout as L
    return L.fabric_group(pc)


def _setup_step(pattern, knit: bool) -> Step:
    """Set up every machine the garment is sewn with (needle, thread, test seam)."""
    import machines as MC
    m = MC.of(pattern.options)
    parts = []
    if m is None or MC.has_sewing_machine(m):
        parts.append("Sewing machine: " + ("jersey/stretch needle 75–80" if knit else "universal needle 80")
                     + ", polyester thread.")
    if m is not None and "overlocker" in m:
        parts.append("Overlocker: 4 cones of polyester thread, differential "
                     + ("1.3 (knits, also sweat and rib), 1.5 if the seam waves" if knit else "1.0") + ".")
    if m is not None and "coverstitch" in m and knit:
        parts.append("Coverstitch: 2 needles, test the hem on a folded scrap.")
    parts.append("Sew a test seam on two layers of a scrap.")
    title = ("Set up the overlocker" if m is not None and not MC.has_sewing_machine(m) and "overlocker" in m
             else "Set up the machine" if len(parts) <= 2 else "Set up the machines")
    return icon(title, "needle", " ".join(parts), section="Prepare",
                hint="See the basics page at the front of the booklet.")


def done(text: str = "Press all seams.", **kw) -> Step:
    return icon("Final pressing", "done", text, section="Finish", **kw)


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


# --------------------------------------------------------------------------- progress
# What is already sewn when a step starts. The pictures draw it (grey dashed seams, pockets
# already on the front, pieces joined), so every picture can be checked against the garment
# on the table.

def annotate_progress(pattern, steps: list[Step]) -> list[Step]:
    """Store in every step what the earlier steps sewed (``step.data["done"]``):

    * ``seams``   ``[(piece, edge)]`` sewn to another piece (seam line = the edge)
    * ``lines``   ``[(piece, edge, mm)]`` stitched along the edge at a distance (hems, topstitching)
    * ``placed``  ``[(pocket, host, mark)]`` pieces stitched onto a placement mark
    * ``joined``  names of the seams of the seam graph sewn so far
    * ``rings``   band pieces closed into a ring
    """
    seams: list = []
    lines: list = []
    placed: list = []
    joined: list = []
    rings: list = []
    for s in steps:
        s.data["done"] = {"seams": list(seams), "lines": list(lines), "placed": list(placed),
                          "joined": list(joined), "rings": list(rings)}
        for sm in resolve_seams(pattern, s) if s.seams else []:
            joined.append(sm["name"])
            for p, e, _n in sm["a"] + sm["b"]:
                if (p, e) not in seams:
                    seams.append((p, e))
        if s.diagram in ("hem", "topstitch") and s.amount > 0:
            for p, e in s.edges:
                d = max(s.amount - 5.0, s.amount * 0.6) if s.diagram == "hem" else s.amount
                lines.append((p, e, d))
        if s.diagram == "place" and len(s.pieces) >= 2:
            placed.append((s.pieces[0], s.pieces[1], s.data.get("mark", "")))
        if s.diagram == "ring" and s.pieces:
            rings.append(s.pieces[0])
    return steps


CURVED_SEAMS = ("crotch", "pocket bag", "armhole", "raglan", "neck", "hood", "sleeve seam")
_SA_RX = re.compile(r"(\d+(?:\.\d+)?) (mm|cm) seam allowance")
_HAND_HEM_RX = re.compile(r"Sew it down [^.]* from the fold, from the right side\.")


def step_allowance(pattern, step: Step) -> float | None:
    """The seam allowance the pieces really have where a step sews (most common value), or None."""
    vals: list[float] = []
    if step.seams:
        for sm in resolve_seams(pattern, step):
            for p, e, _n in sm["a"]:
                if pattern.has(p):
                    vals += [ed.sa for ed in pattern.piece(p).edges if ed.name == e]
    elif step.diagram == "ring" and step.pieces and pattern.has(step.pieces[0]):
        # the short ends of the band (labels may already be translated, so go by length)
        eds = sorted((ed for ed in pattern.piece(step.pieces[0]).edges if not ed.fold and ed.sa > 0),
                     key=lambda ed: G.length(ed.pts))
        vals = [ed.sa for ed in eds[:2]]
    vals = [round(v, 1) for v in vals if v > 0]
    return max(set(vals), key=vals.count) if vals else None


def fix_allowance(pattern, step: Step) -> None:
    """Write the allowance of the real pieces into the step text ("Sew with 7.5 mm seam allowance"),
    so the text never contradicts the parts list (e.g. a narrower neckline allowance)."""
    found = _SA_RX.findall(step.text)
    if not found or len(set(found)) > 1:
        return
    sa = step_allowance(pattern, step)
    if sa:
        step.text = _SA_RX.sub(cm(sa) + " seam allowance", step.text)


def number(steps: list[Step]) -> list[tuple[int, Step]]:
    return list(enumerate(steps, 1))


def assembly(pattern, plans: dict | None = None) -> list[Step]:
    """All steps for a pattern: preparation + the garment module's assembly (``plans``: the cutting
    layout, drawn in the cutting step)."""
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
    own = owned_machines(pattern.options)
    out: list[Step] = []
    pins_told = False
    for s in body:
        s.data.setdefault("knit", knit)
        tool = tool_for(pattern.options, s.stitch, s.data["knit"]) if s.stitch else {}
        mach = tool.get("machine")
        # finishing the overlocker already did (or knit that does not fray): no step of its own
        if s.stitch == "finish" and own is not None and tool.get("stitch") in ("already finished", "none"):
            continue
        # optional topstitching by hand: a back stitch does not stretch with the neckline, leave it out
        if s.stitch == "topstitch" and mach == "hand" and s.text.startswith("Optional"):
            continue
        fix_allowance(pattern, s)
        if mach == "overlocker":
            # the overlocker sews both allowances together: they cannot be pressed open
            s.text = s.text.replace("finger-press the allowances open", "press the allowances to one side")
            s.text = s.text.replace("press the allowances open", "press the allowances to one side")
            if s.stitch in ("seam", "band"):
                names = " ".join(s.seams).lower()
                curved = any(w in names for w in CURVED_SEAMS)
                text = ("Sew the curve slowly; pull the clips before they reach the knife." if curved
                        else "Pull the pins before they reach the knife." if not pins_told else "")
                pins_told = pins_told or bool(text)
                if text and not s.tip:
                    s.tip = text
                elif text and not s.hint and "knife" not in s.tip:
                    s.hint = text
        if mach == "hand" and s.stitch == "hem":
            s.text = _HAND_HEM_RX.sub("Sew it down by hand with a blind stitch: catch only 1–2 threads of the "
                                      "outer fabric.", s.text)
        if mach != "sewing" and "free arm" in s.hint:
            s.hint = ""
        if s.data.get("picture") == "done" and s.text == "Press all seams.":
            s.text = "Press all seams" + E.press_note(pattern.options.get("fabric"))
        out.append(s)
    body = out
    return annotate_progress(pattern, prepare(pattern, plans) + body)
