"""Headband / ear warmer (knit): a band folded lengthwise and closed into a ring. Style `twist`
gathers the centre front with a twist loop (a short tube wrapped round the band)."""
from __future__ import annotations

import ease as E
import geometry as G
from pattern import Mark, Pattern, rect_piece

from ._common import clamp, resolve

DEFAULTS = dict(style="plain", fabric="jersey", stretch=None, height_cm=None, sa=7.5, circ_total=None)
FINISHED_LABELS = {"circ": ("Circumference (relaxed)", "width"), "height": ("Height", "length")}
FIT_CHECK = "does it sit snugly over the ears without slipping or pressing?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    if o["style"] not in ("plain", "twist"):
        raise ValueError("headband style must be plain or twist")
    m = measures
    head = m["head"]
    _, stretch, knit = E.fabric_info(o["fabric"], o["stretch"])
    # common practice: 85–90 % of the head circumference for knits (negative ease)
    circ = o["circ_total"] or head * (0.87 if stretch >= 30 else 0.95)
    h = o["height_cm"] * 10 if o["height_cm"] else clamp(0.05 * m["height"], 60, 110)
    sa = o["sa"]
    p = rect_piece("band", "Headband", circ, 2 * h, sa=sa, cut_count=1,
                   names=("bottom", "right", "top", "left"),
                   labels=("Long edge", "Cross seam", "Long edge", "Cross seam"), grain_vertical=False)
    p.marks.append(Mark(G.line(G.P(0, h), G.P(circ, h)), "fold", "Fold line"))
    p.stretch_dir = "Stretch direction: along the band"
    pieces = [p]
    seams = [dict(name="Long edges together", a=[("band", "bottom", 1)], b=[("band", "top", 1)], type="equal"),
             dict(name="Cross seam (right ↔ left)", a=[("band", "right", 1)], b=[("band", "left", 1)],
                  type="equal")]
    if o["style"] == "twist":
        tw = rect_piece("twist", "Twist loop", 2 * h * 0.6, 100.0, sa=sa, cut_count=1,
                        names=("bottom", "right", "top", "left"),
                        labels=("Long edge", "Short edge", "Long edge", "Short edge"))
        pieces.append(tw)
        seams.append(dict(name="Twist loop long seam", a=[("twist", "bottom", 1)], b=[("twist", "top", 1)],
                          type="equal"))
    checks = [dict(name="Headband goes over the head", kind="min", value=circ * (1 + stretch / 100),
                   target=head * 1.05, note="circumference incl. stretch"),
              dict(name="Headband stays on (snug)", kind="range", value=circ, lo=head * 0.8, hi=head * 0.98,
                   note="negative ease for knits")]
    pat = Pattern("headband", "Headband" if o["style"] == "plain" else "Twist headband", "", pieces, dict(m), o,
                  seams=seams, corners=[dict(name="Corner", piece="band", a="bottom", b="right", target=90)],
                  checks=checks)
    pat.finished = dict(circ=circ, height=h)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("band").edge("right").sa)
    out = [ST.seam("Sew the long seam", ["Long edges together"],
                   "Fold the band lengthwise right sides together, long edges level, and pin. "
                   f"Sew with {sa} seam allowance along the whole length: you get a tube.", section="Headband"),
           ST.icon("Turn half of the tube", "turn",
                   "Reach into the tube and turn one half right side out over the other half. Now both ends lie "
                   "on top of each other, right sides together.", section="Headband",
                   hint="The long seams lie on top of each other: pin there first.")]
    if pat.has("twist"):
        out.insert(0, ST.seam("Sew the twist loop", ["Twist loop long seam"],
                              "Fold the twist loop lengthwise right sides together and sew the long edge "
                              f"with {sa} seam allowance. Turn it right side out.", section="Twist"))
    out += [ST.seam("Sew the cross seam", ["Cross seam (right ↔ left)"],
                    "Pin the two ends together all round, long seams on top of each other. "
                    f"Sew round with {sa} seam allowance, leaving 4 cm open.", section="Headband"),
            ST.icon("Close the opening by hand", "hand",
                    "Turn the band right side out through the opening. Fold the allowances in and close the opening "
                    "with a ladder stitch.", stitch="hand", section="Headband")]
    if pat.has("twist"):
        out.append(ST.icon("Wrap the twist loop round", "hand",
                           "Gather the band at the cross seam, wrap the twist loop tightly round it and sew the "
                           "loop ends together by hand on the inside.", stitch="hand", section="Twist"))
    out.append(ST.done(""))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
