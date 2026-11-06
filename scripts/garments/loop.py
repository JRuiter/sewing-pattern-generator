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


def sewing_steps(pat):
    return ["**Long seam:** fold the rectangle lengthwise right sides together and sew the long edges into a tube.",
            "**Turn:** turn the tube right side out. Slip one end into the other (right sides together) and "
            "sew the cross seam, leaving 5 cm open.",
            "**Close:** turn and close the opening by hand (ladder stitch). Done!"]
