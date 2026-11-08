"""Bucket hat (sun hat) from the head circumference: oval crown, side band (two halves) and a
sloping brim (two halves, cut twice: upper and under brim). Lined, or `reversible` with a second
fabric. The brim is topstitched in rows to keep it stiff."""
from __future__ import annotations

import math

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece

from ._common import clamp, resolve

DEFAULTS = dict(fabric="woven", stretch=None, reversible=False, brim_cm=None, band_cm=None, sa=7.5, ease_cm=1.5,
                brim_slope=35.0)
FINISHED_LABELS = {"circ": ("Head opening", "width"), "brim": ("Brim width", "length"),
                   "band": ("Side band height", "length")}
FIT_CHECK = "does it sit on the head without pressing, the brim slightly sloping down?"


def _sector(r_in: float, r_out: float, ang: float, names, labels, sa, sa_out=None):
    """Flat development of a cone frustum (annular sector), symmetric about the y axis, opening upward:
    edges counter-clockwise: outer arc, side, inner arc, side."""
    a0, a1 = 90 + math.degrees(ang) / 2, 90 - math.degrees(ang) / 2
    # outer arc from right to left (counter-clockwise), inner arc back from left to right
    t_out = np.radians(np.linspace(a1, a0, max(20, int(r_out * ang / 2))))
    t_in = np.radians(np.linspace(a0, a1, max(20, int(r_in * ang / 2))))
    outer = np.column_stack([r_out * np.cos(t_out), r_out * np.sin(t_out)])
    inner = np.column_stack([r_in * np.cos(t_in), r_in * np.sin(t_in)])
    left = G.line(outer[-1], inner[0])
    right = G.line(inner[-1], outer[0])
    so = sa if sa_out is None else sa_out
    return [Edge(names[0], outer, so, label=labels[0]), Edge(names[1], left, sa, label=labels[1]),
            Edge(names[2], inner, sa, label=labels[2]), Edge(names[3], right, sa, label=labels[1])]


def _frustum(L_small: float, L_big: float, width: float):
    """Radii and angle of the flat development of a frustum with circumferences L_small < L_big."""
    r_in = width * L_small / (L_big - L_small)
    ang = L_small / r_in
    return r_in, r_in + width, ang


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    m = measures
    sa = o["sa"]
    head = m["head"] + o["ease_cm"] * 10
    band_h = o["band_cm"] * 10 if o["band_cm"] else clamp(0.13 * m["head"], 55, 80)
    brim_w = o["brim_cm"] * 10 if o["brim_cm"] else clamp(0.12 * m["head"], 45, 75)
    # side band: slightly conical (top 8 % smaller)
    top_c = head * 0.92
    rb_in, rb_out, ab = _frustum(top_c, head, band_h)
    band_edges = _sector(rb_in, rb_out, ab / 2, ("bottom", "left", "top", "right"),
                         ("Brim seam", "Side seam", "Crown seam"), sa)
    # the sector opens upward, the small arc (crown) is the inner one: band seen upside down; fine for cutting
    # brim: cone with the given slope (35° below horizontal)
    slope = math.radians(o["brim_slope"])
    outer_c = head + 2 * math.pi * brim_w * math.cos(slope)
    r_in, r_out, a_brim = _frustum(head, outer_c, brim_w)
    brim_edges = _sector(r_in, r_out, a_brim / 2, ("outer", "left", "inner", "right"),
                         ("Brim edge", "Brim side seam", "Brim seam"), sa)
    # crown: ellipse, head oval 1.15 : 1, circumference = top of the band
    k = 1.15
    b = top_c / (math.pi * (3 * (k + 1) - math.sqrt((3 * k + 1) * (k + 3))))
    a = k * b
    t = np.linspace(0, 2 * math.pi, 361)
    ell = np.column_stack([b * np.cos(t), a * np.sin(t)])      # long axis front–back (y)
    half = len(ell) // 2
    crown_edges = [Edge("seam_r", ell[:half + 1], sa, label="Crown seam"),
                   Edge("seam_l", ell[half:], sa, label="Crown seam")]
    alt = "Second fabric" if o["reversible"] else "Lining"
    pieces = []
    for suffix, fab in (("", "Main fabric"), ("_in", alt)):
        crown = Piece("crown" + suffix, "Crown" + (" (inside)" if suffix else ""), [Edge(e.name, e.pts.copy(), e.sa,
                      label=e.label) for e in crown_edges], cut_count=1, mirror=False, fabric=fab,
                      grain=(G.P(0, -a * 0.5), G.P(0, a * 0.5)))
        crown.marks.append(Mark(np.vstack([[0, a], [0, a - 12]]), "mark", "Front"))
        band = Piece("band" + suffix, "Side band" + (" (inside)" if suffix else ""),
                     [Edge(e.name, e.pts.copy(), e.sa, label=e.label) for e in band_edges], cut_count=2,
                     mirror=False, fabric=fab, grain=(G.P(0, rb_in + band_h * 0.2), G.P(0, rb_in + band_h * 0.8)))
        pieces += [crown, band]
    for suffix, name in (("", "Brim"), ("_in", "Under brim")):
        br = Piece("brim" + suffix, name, [Edge(e.name, e.pts.copy(), e.sa, label=e.label) for e in brim_edges],
                   cut_count=2, mirror=False, fabric="Main fabric" if not suffix else alt,
                   grain=(G.P(0, r_in + brim_w * 0.2), G.P(0, r_in + brim_w * 0.8)))
        pieces.append(br)
    pieces[1].info.append("Optional: iron-on interfacing on the outer side band")
    seams = []
    for suffix, lab in (("", " (outside)"), ("_in", " (inside)")):
        seams += [dict(name=f"Side band seams{lab}", a=[(f"band{suffix}", "left", 1)], b=[(f"band{suffix}", "right", 1)],
                       type="equal"),
                  dict(name=f"Crown ↔ side band{lab}", a=[(f"crown{suffix}", "seam_r", 1), (f"crown{suffix}", "seam_l", 1)],
                       b=[(f"band{suffix}", "top", 2)], type="equal")]
    seams += [dict(name="Brim side seams", a=[("brim", "left", 1)], b=[("brim", "right", 1)], type="equal"),
              dict(name="Under brim side seams", a=[("brim_in", "left", 1)], b=[("brim_in", "right", 1)],
                   type="equal"),
              dict(name="Brim outer edge", a=[("brim", "outer", 2)], b=[("brim_in", "outer", 2)], type="equal"),
              dict(name="Brim ↔ side band", a=[("brim", "inner", 2)], b=[("band", "bottom", 2)], type="equal")]
    checks = [dict(name="Head opening", kind="range", value=2 * G.length(band_edges[0].pts), lo=m["head"] + 5,
                   hi=m["head"] + 25, note="head + 0.5–2.5 cm")]
    pat = Pattern("bucket_hat", "Bucket hat", "", pieces, dict(m), o, seams=seams, corners=[], checks=checks)
    pat.finished = dict(circ=head, brim=brim_w, band=band_h)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("band").edge("left").sa)
    rev = pat.options.get("reversible")
    out = [ST.icon("Interface the outer side band", "interfacing",
                   "Optional, for a firmer hat: iron interfacing onto the wrong side of the outer side band pieces.",
                   section="Prepare"),
           ST.seam("Close the side band", ["Side band seams (outside)"],
                   f"Lay both side band halves right sides together and sew both short ends with {sa} seam allowance: "
                   "a ring. Press the allowances open.", section="Hat"),
           ST.seam("Sew the crown in", ["Crown ↔ side band (outside)"],
                   "Pin the crown right sides together into the narrow edge of the band: the long axis of the oval "
                   f"front and back, the side seams at the sides. Sew with {sa} seam allowance.", section="Hat",
                   hint="Clip the band allowance every 1.5 cm so it follows the curve."),
           ST.seam("Close the brims", ["Brim side seams", "Under brim side seams"],
                   f"Sew the two halves of each brim together at the short ends with {sa} seam allowance: two rings. "
                   "Press the allowances open.", section="Brim"),
           ST.seam("Sew the brim edge", ["Brim outer edge"],
                   f"Lay the two brim rings right sides together and sew round the outer edge with {sa} seam "
                   "allowance. Turn, press and baste the inner edges together.", section="Brim",
                   hint="Clip the allowance of the outer edge in small notches before turning."),
           ST.topstitch("Topstitch the brim", [("brim", "outer")], 5.0,
                        "Topstitch rows 7 mm apart all round the brim, starting 5 mm from the outer edge.",
                        section="Brim"),
           ST.seam("Sew the brim on", ["Brim ↔ side band"],
                   "Pin the brim to the lower edge of the outer hat (right side of the brim to the right side of the "
                   f"hat), side seams matching. Sew with {sa} seam allowance.", section="Brim"),
           ST.seam("Sew the inner hat", ["Side band seams (inside)", "Crown ↔ side band (inside)"],
                   "Sew band and crown of the " + ("second hat" if rev else "lining") + " the same way.",
                   section="Inside"),
           ST.topstitch("Join outer and inner hat", [("band", "bottom")], 3.0,
                        "Fold the lower allowance of the inner hat to the wrong side. Slip it into the outer hat, "
                        "wrong sides together, so the fold covers the brim seam. Pin and topstitch close to the fold "
                        "from the outside, through all layers.", section="Finish"),
           ST.done("Press the brim over a rolled towel.")]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
