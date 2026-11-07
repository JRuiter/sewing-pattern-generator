"""Loop scarf: one rectangle, folded lengthwise (double layer), closed into a ring."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Mark, Pattern, rect_piece

DEFAULTS = dict(fabric="jersey", stretch=None, height=None, wraps=1, sa=10.0, circ_total=None)
FINISHED_LABELS = {"circ": ("Circumference", "width"), "height": ("Height (double layer)", "length")}


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    _, stretch, _ = E.fabric_info(o["fabric"], o["stretch"])
    circ = o["circ_total"] or (m["head"] * 1.2 if o["wraps"] == 1 else m["head"] * 2.6)
    h = o["height"] or (0.17 * m["height"] if m["height"] < 1650 else 300.0)
    p = rect_piece("loop", "Loop", circ, 2 * h, sa=o["sa"], cut_count=1, names=("bottom", "right", "top", "left"),
                   labels=("Long edge", "Cross seam", "Long edge", "Cross seam"), grain_vertical=False)
    p.marks.append(Mark(G.line(G.P(0, h), G.P(circ, h)), "fold", "Fold line"))
    seams = [dict(name="Cross seam (right ↔ left)", a=[("loop", "right", 1)], b=[("loop", "left", 1)], type="equal"),
             dict(name="Long edges together", a=[("loop", "bottom", 1)], b=[("loop", "top", 1)], type="equal")]
    corners = [dict(name="Bottom right corner", piece="loop", a="bottom", b="right", target=90)]
    checks = [dict(name="Loop fits over the head", kind="min", value=circ * (1 + stretch / 100 * 0.5),
                   target=m["head"] * 1.1, note="circumference incl. stretch")]
    pat = Pattern("loop", "Loop", "", [p], dict(m), o, seams=seams, corners=corners, checks=checks)
    pat.finished = dict(circ=circ, height=h)
    return pat


def assembly(pat):
    """The construction as one-action steps (see steps.py)."""
    import steps as ST
    return [
        ST.seam("Sew the long seam", ["Long edges"], "Fold lengthwise right sides together; sew into a tube.",
                section="Loop"),
        ST.icon("Turn the tube", "turn", "Right side out.", section="Loop"),
        ST.seam("Sew the cross seam", ["Cross seam"], "Slip one end into the other (right sides together); "
                "sew around, leaving 5 cm open.", section="Loop"),
        ST.icon("Close the opening by hand", "hand", "Turn and close with a ladder stitch.", stitch="hand",
                section="Loop"),
        ST.done(""),
    ]


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
