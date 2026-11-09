"""Wrap top and wrap dress (knit): the fronts cross over each other; the wrap edge runs from the
neck point down to the opposite side at the waist and is finished together with the back neck
by one band; two ties close it (one through a slot in the side seam). `style="dress"` lengthens
it to the knee with a flared hem."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, rect_piece

from . import dress as D
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(style="top", fit="normal", fabric="jersey", stretch=None, sleeve_length="short", length="knee",
                overlap=0.85, sa=10.0, hem_sa=20.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, waist=("Waist (wrapped)", "width"))
FIT_CHECK = "does the wrap cover the chest without gaping when you bend forward, and do the ties sit at the waist?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in ("top", "dress"):
        raise ValueError("wrap style must be top or dress")
    m = measures
    sa = o["sa"]
    top: dict = {k: o[k] for k in ("fit", "fabric", "stretch", "sleeve_length", "sa", "hem_sa", "chest_total",
                             "construction", "machines", "notch_style") if k in o}
    top.update(neckline="round", hem_band=False, sleeve_cuffs=False, _auto_neck=99)
    if o["style"] == "dress":
        top["body_length"] = m["back_length"] + D.skirt_length(m, o["length"])
        top["hem_total"] = m["hip"] * 1.45
    pat = T.draft(m, top, _garment="wrap")
    F = pat.options["_F"]
    pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
    pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    f, b = pat.piece("front"), pat.piece("back")
    q = F["q"]
    hem = f.edge("hem").pts
    hem_y = float(hem[0, 1])
    y_w = -m["back_length"] * 0.98
    x_w = -o["overlap"] * q
    x_h = -o["overlap"] * float(hem[-1, 0]) if o["style"] == "dress" else x_w
    N = f.edge("shoulder").pts[-1]
    W = G.P(x_w, y_w)
    wrap = G.cubic(N, N + G.P(-0.15 * q, -0.30 * F["AD"]), W + G.P(0.45 * q, 0.35 * F["AD"]), W)
    names = [e.name for e in f.edges]
    keep = {e.name: e for e in f.edges}
    d = G.unit(G.P(x_h, hem_y) - W)
    perp = np.array([-d[1], d[0]]) if -d[1] > 0 else np.array([d[1], -d[0]])
    hem_line = G.line(G.P(x_h, hem_y), hem[-1]) if abs(x_h - x_w) < 0.5 else \
        G.tangent_curve(G.P(x_h, hem_y), perp, hem[-1], (1, 0), 0.3, 0.4)
    new = [Edge("hem", hem_line, keep["hem"].sa, label="Hem", turned=True),
           keep["side"], keep["armhole"], keep["shoulder"],
           Edge("wrap", wrap, sa * 0.7, label="Wrap edge (band)"),
           Edge("front_edge", G.line(W, G.P(x_h, hem_y)), 20.0, label="Front edge (hem)", turned=True)]
    del names
    f.edges = new
    f.cut_count, f.mirror, f.name = 2, True, "Front (left and right)"
    f.marks.append(Mark(G.line(G.P(0, -F["fnd"]), G.P(0, hem_y)), "mark", "Centre front"))
    sp = f.edge("side").pts[np.argsort(f.edge("side").pts[:, 1])]
    xs = float(np.interp(y_w, sp[:, 1], sp[:, 0]))
    f.marks.append(Mark(G.line(G.P(xs - 2, y_w + 10), G.P(xs - 2, y_w - 15)), "mark", "Tie slot (one side only)"))
    pat.corners = [c for c in pat.corners if not (c.get("piece") == "front" and
                                                    {c.get("a"), c.get("b")} & {"center", "neckline"})
                   and not ("sum" in c and any(p == "front" and "neckline" in (a, bb) for p, a, bb in c["sum"]))]
    pat.corners.append(dict(name="Hem ↔ front edge", piece="front", a="front_edge", b="hem", target=90))
    knit = F["knit"]
    ratio = 0.9 if knit else 1.0
    bl = 2 * (f.edge("wrap").length + b.edge("neckline").length) * ratio
    bh = 15.0 if is_adult(m) else 12.0
    band = rect_piece("wrap_band", "Wrap band", bl, 2 * bh, sa=sa * 0.7, cut_count=1,
                      labels=("Seam edge", "End", "Seam edge", "End"), grain_vertical=knit,
                      fabric="Main fabric")
    band.marks.append(Mark(G.line(G.P(0, bh), G.P(bl, bh)), "fold", "Fold line"))
    if knit:
        band.stretch_dir = "Stretch direction: along the length"
    pat.pieces.append(band)
    pat.seams.append(dict(name="Wrap band ↔ wrap edges and back neck", a=[("front", "wrap", 2), ("back", "neckline", 2)],
                          b=[("wrap_band", "bottom", 1)], type="ratio", lo=ratio - 0.03, hi=min(1.0, ratio + 0.05)))
    tl = clamp(0.62 * m["waist"], 300, 700)
    tw = 25.0 if is_adult(m) else 20.0
    tie = rect_piece("tie", "Tie", 2 * tw, tl, sa=sa, cut_count=2,
                     labels=("Tie end (into the seam)", "Tie edge", "Tie end", "Tie edge"))
    pat.pieces.append(tie)
    pat.seams.append(dict(name="Ties", a=[("tie", "right", 1)], b=[("tie", "left", 1)], type="equal"))
    waist = 2 * (q + q) * 1.0
    pat.title = "Wrap dress" if o["style"] == "dress" else "Wrap top"
    pat.options.update(style=o["style"], overlap=o["overlap"])
    pat.finished["waist"] = waist
    pat.finished["neckline"] = 2 * (f.edge("wrap").length + b.edge("neckline").length)
    for c in pat.checks:
        if c["name"] == "Body length plausible" and o["style"] == "dress":
            c["hi"] = 0.9 * m["height"]
    return pat


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = [ST.seam("Sew the ties", ["Ties"],
                   f"Fold each tie lengthwise right sides together and sew the long edge and one end with {sa} seam "
                   "allowance. Turn with a safety pin and press.", section="Ties"),
           ST.hem("Hem the front edges", [("front", "front_edge")], 20.0,
                  "Fold the straight front edge below the wrap 2 cm to the wrong side and stitch it down.",
                  repeat=2, section="Front")]
    base = T.assembly(pat, hem=True, neck=False, done=False)
    i = next(k for k, st in enumerate(base) if st.title in ("Set in the sleeves", "Sew side and sleeve seams"))
    band = [ST.fold_band("Fold the band in half", "wrap_band",
                         "Fold the band lengthwise wrong sides together, raw edges level, and press.",
                         section="Wrap edge", data={"hands": "fold"}),
            ST.seam("Sew the band on", ["Wrap band"],
                    "Pin the band onto the right side of the wrap edges and the back neck, from one waist point to "
                    f"the other, centre back on the back neck. Sew with {sa} seam allowance, stretching the band "
                    "slightly over the bust. Press the allowance towards the body and topstitch it.",
                    section="Wrap edge", hint="Stretch the band a little more over the bust: the edge then lies "
                    "flat against the body and does not gape.")]
    for st in base[i:]:
        if st.title == "Sew side and sleeve seams":
            st.text += (" Catch one tie in the left side seam at the waist marking, pointing inwards; leave a 2.5 cm "
                        "slot open in the right side seam at the marking.")
    out += base[:i] + band + base[i:]
    out += [ST.icon("Sew on the second tie", "needle",
                    "Sew the second tie onto the end of the wrap edge of the outer front, at the waist point.",
                    section="Ties"),
            ST.done("Press the band and the hems. Wrap the inner front, pull its tie through the slot, wrap the "
                    "outer front over it and tie both at the side.")]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
