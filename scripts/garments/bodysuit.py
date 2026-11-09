"""Bodysuit, swimsuit and baby wrap bodysuit (knit with elastane): the T-shirt block lengthened to
the crotch, with leg openings and a crotch.

Styles
- `body` (default): sleeves (short/long/none), snap crotch (back overlaps front), leg openings and
  neckline bound with bands; babies get an envelope neckline from the T-shirt options if wanted
- `swimsuit`: sleeveless, scoop neck, front lined, crotch seam, elastic in the leg openings and
  armholes (swim fabric)
- `wrap`: baby kimono body: two fronts cross over the chest and close with snaps at the side, no
  neckline over the head
"""
from __future__ import annotations

import numpy as np

import ease as E
import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(style="body", fit="slim", fabric="jersey_elastane", stretch=None, sleeve_length="short",
                leg_cut="normal", sa=7.5, hem_sa=20.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, torso=("Neck point to crotch", "length"), leg_opening=("Leg opening",
                                                                                                  "width"))
FIT_CHECK = "does it reach the crotch without pulling on the shoulders when you bend, and do the leg openings lie " \
            "flat?"


def _lower(pc: Piece, F, m, y_c, y_leg, cw, back: bool, turned_crotch: float | None, leg_k: float):
    """Replace centre/hem/side of a T-shirt body piece with centre → crotch → leg opening → side."""
    side = pc.edge("side").pts
    sp = side[np.argsort(side[:, 1])]
    xs = float(np.interp(y_leg, sp[:, 1], sp[:, 0]))
    upper = side[side[:, 1] > y_leg + 0.5]
    top = pc.edge("center").pts[0]
    leg = G.tangent_curve(G.P(cw, y_c), (0, 1), G.P(xs, y_leg), (1, 0.15), leg_k, 0.45 if back else 0.6)
    edges = [Edge("center", G.line(top, G.P(0, y_c)), 0.0, True, pc.edge("center").label),
             Edge("crotch", G.line(G.P(0, y_c), G.P(cw, y_c)), turned_crotch or pc.edge("side").sa,
                  label="Crotch (snap facing)" if turned_crotch else "Crotch seam", turned=bool(turned_crotch)),
             Edge("leg", leg, pc.edge("side").sa, label="Leg opening"),
             Edge("side", np.vstack([G.P(xs, y_leg), upper]), pc.edge("side").sa, label="Side seam")]
    rest = [e for e in pc.edges if e.name in ("armhole", "raglan", "shoulder", "neckline")]
    pc.edges = edges + rest
    gx = F["q"] * 0.45
    pc.grain = (G.P(gx, -F["AD"] - 20), G.P(gx, y_c * 0.5 + -F["AD"] * 0.5))
    del m


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in ("body", "swimsuit", "wrap"):
        raise ValueError("bodysuit style must be body, swimsuit or wrap")
    m = measures
    sa = o["sa"]
    style = o["style"]
    sleeveless = style == "swimsuit" or o["sleeve_length"] == "none"
    top: dict = {k: o[k] for k in ("fit", "fabric", "stretch", "sa", "hem_sa", "chest_total", "construction",
                             "machines", "notch_style", "neckline") if k in o}
    top.update(sleeve_length="short" if sleeveless else o["sleeve_length"], hem_band=False, sleeve_cuffs=False,
               body_length=m["back_length"] + m["crotch_depth"] + 30)
    if style == "wrap":
        top["_auto_neck"] = 99
    pat = T.draft(m, top, _garment="bodysuit")
    F = pat.options["_F"]
    _, stretch, knit = E.fabric_info(o["fabric"], o.get("stretch"))
    f, b = pat.piece("front"), pat.piece("back")
    vert = 0.97 if stretch >= 40 else 1.0            # stretchy fabric: a little shorter, it fits close
    y_c = -(m["back_length"] + m["crotch_depth"] * 0.92) * vert
    cut = {"normal": 0.30, "high": 0.55, "low": 0.12}.get(o["leg_cut"], 0.30)
    y_leg = y_c + cut * m["crotch_depth"] + (0.12 * m["crotch_depth"])
    cw = clamp(0.035 * m["hip"], 20, 40)
    snap = 20.0 if style in ("body", "wrap") else None
    _lower(f, F, m, y_c, y_leg, cw, False, snap, 0.35)
    _lower(b, F, m, y_c, y_leg, cw, True, snap, 0.55)
    if snap:
        b.edge("crotch").sa = 30.0
        b.edge("crotch").label = "Crotch (snap facing, overlaps the front)"
    pat.corners = [c for c in pat.corners if not ({c.get("a"), c.get("b")} & {"hem"})]
    pat.checks = [c for c in pat.checks if c["name"] not in ("Body length plausible",)]
    # leg openings: band (body) or elastic (swimsuit)
    leg_len = f.edge("leg").length + b.edge("leg").length
    if style == "swimsuit":
        el = leg_len * 2 * 0.8
        pat.notes.append(f"Swim elastic 8–10 mm: leg openings 2 × {el / 2 / 10:.0f} cm, armholes and neckline "
                         "about 85 % of their length")
        for pc in (f, b):
            pc.edge("leg").sa, pc.edge("leg").turned, pc.edge("leg").label = 10.0, True, "Leg opening (elastic, turned)"
        pat.seams.append(dict(name="Crotch seam", a=[("front", "crotch", 1)], b=[("back", "crotch", 1)], type="equal"))
        pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
        pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["a"] + s["b"])]
        pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
        for pc in (f, b):
            e = pc.edge("neckline")
            e.sa, e.turned, e.label = 10.0, True, "Neckline (elastic, turned)"
        lin = Piece("front_lining", "Front lining", [Edge(e.name, e.pts.copy(), e.sa, e.fold, e.label, e.turned)
                                                     for e in f.edges], cut_count=1, mirror=False,
                    fabric="Swim lining", grain=f.grain)
        pat.pieces.append(lin)
    else:
        bh = 12.0 if is_adult(m) else 10.0
        ratio = 0.85
        lb = rect_piece("leg_band", "Leg band", leg_len * ratio, 4 * bh, sa=0.0, cut_count=2,
                        labels=("Band edge", "End", "Band edge", "End"), grain_vertical=True,
                        fabric="Rib knit" if not style == "wrap" else "Main fabric")
        for e in lb.edges:
            e.raw = True
        lb.stretch_dir = "Stretch direction: along the length"
        lb.info.append("press both long edges to the middle, then fold (binding)")
        pat.pieces.append(lb)
        pat.seams.append(dict(name="Leg band ↔ leg opening (stretched)", a=[("front", "leg", 1), ("back", "leg", 1)],
                              b=[("leg_band", "bottom", 1)], type="ratio", lo=0.8, hi=0.9))
        n = 3 if is_adult(m) else (3 if m["height"] > 800 else 4)
        pat.notes.append(f"Snaps: {n} snaps (plastic or metal) for the crotch" + (" + 3 for the wrap" if style == "wrap"
                                                                                   else ""))
        pat.options["_snaps"] = n
        for pc in (f, b):
            ce = pc.edge("crotch").pts
            for x in np.linspace(cw * 0.25, cw * 0.9, 2):
                pc.marks.append(Mark(G.line(G.P(x, float(ce[0, 1]) + 8), G.P(x, float(ce[0, 1]) + 9)), "mark", "Snap"))
    if sleeveless:
        pat.pieces = [p for p in pat.pieces if p.key != "sleeve"]
        pat.seams = [s for s in pat.seams if not any(k == "sleeve" for k, _, _ in s["a"] + s["b"])]
        pat.corners = [c for c in pat.corners if c.get("piece") != "sleeve"]
        pat.checks = [c for c in pat.checks if "leeve" not in c["name"] and "cap" not in c["name"].lower()]
        for pc in (f, b):
            pc.notches = [nt for nt in pc.notches if nt.edge != "armhole"]
            e = pc.edge("armhole")
            if style == "swimsuit":
                e.sa, e.turned, e.label = 10.0, True, "Armhole (elastic, turned)"
            else:
                e.label = "Armhole (band)"
        if style != "swimsuit":
            arm = f.edge("armhole").length + b.edge("armhole").length
            ab = rect_piece("armhole_band", "Armhole band", arm * 0.88, 4 * 10.0, sa=0.0, cut_count=2,
                            labels=("Band edge", "End", "Band edge", "End"))
            for e in ab.edges:
                e.raw = True
            pat.pieces.append(ab)
            pat.seams.append(dict(name="Armhole band ↔ armhole (stretched)", a=[("front", "armhole", 1),
                                                                               ("back", "armhole", 1)],
                                  b=[("armhole_band", "bottom", 1)], type="ratio", lo=0.84, hi=0.92))
    if style == "wrap":
        _wrap_front(pat, F, m, sa)
    torso = -y_c
    pat.checks.append(dict(name="Neck point to crotch", kind="range", value=2 * torso,
                           lo=2 * (m["back_length"] + m["crotch_depth"] * 0.8),
                           hi=2 * (m["back_length"] + m["crotch_depth"] * 1.1),
                           note="front + back, vertical stretch included"))
    pat.title = {"body": "Bodysuit", "swimsuit": "Swimsuit", "wrap": "Wrap bodysuit"}[style]
    pat.options.update(style=style, leg_cut=o["leg_cut"])
    pat.finished = {k: v for k, v in pat.finished.items() if k in FINISHED_LABELS and not (sleeveless and "sleeve"
                                                                                           in k)}
    pat.finished.update(torso=torso, leg_opening=2 * leg_len, length=torso)
    return pat


def _wrap_front(pat, F, m, sa):
    """Kimono front: the outer front reaches across to the opposite side seam below the chest."""
    f = pat.piece("front")
    q = F["q"]
    names = {e.name: e for e in f.edges}
    side = names["side"].pts
    crotch, leg = names["crotch"].pts, names["leg"].pts
    y_w = -(F["AD"] + 0.25 * (m["back_length"] - F["AD"]))
    sp = side[np.argsort(side[:, 1])]
    xs_w = float(np.interp(y_w, sp[:, 1], sp[:, 0]))
    N = names["shoulder"].pts[-1]
    W = G.P(-xs_w, y_w)
    wrap = G.cubic(N, N + G.P(-0.2 * q, -0.4 * F["AD"]), W + G.P(0.5 * q, 0.2 * F["AD"]), W)
    far_side = G.mirror_x(side[side[:, 1] <= y_w + 0.1], 0.0)[::-1]       # W down to the far leg point
    far_side = np.vstack([W, far_side[far_side[:, 1] < y_w - 0.5]])
    far_leg = G.mirror_x(leg, 0.0)[::-1]
    full_crotch = G.line(G.P(-float(crotch[-1, 0]), float(crotch[0, 1])), crotch[-1])
    f.edges = [Edge("side_far", far_side, sa, label="Side seam (other side)"),
               Edge("leg_far", far_leg, sa, label="Leg opening"),
               Edge("crotch", full_crotch, 20.0, label="Crotch (snap facing)", turned=True),
               Edge("leg", leg, sa, label="Leg opening"),
               names["side"], names["armhole"], names["shoulder"],
               Edge("wrap", wrap, sa * 0.7, label="Wrap edge (band)")]
    f.cut_count, f.mirror, f.name = 2, True, "Front (outer and inner)"
    f.marks = [mk for mk in f.marks if mk.label != "Snap"]
    f.marks.append(Mark(G.line(G.P(0, -F["fnd"]), G.P(0, float(crotch[0, 1]))), "mark", "Centre front"))
    f.marks.append(Mark(G.line(W + G.P(15, 5), W + G.P(15, 6)), "mark", "Snap"))
    b = pat.piece("back")
    pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
    pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
    pat.corners = [c for c in pat.corners if not (c.get("piece") == "front" and
                                                    {c.get("a"), c.get("b")} & {"center", "neckline"})
                   and not ("sum" in c and any(p == "front" and "neckline" in (a, bb) for p, a, bb in c["sum"]))]
    bl = 2 * (f.edge("wrap").length + b.edge("neckline").length) * 0.9
    band = rect_piece("wrap_band", "Wrap band", bl, 4 * 10.0, sa=0.0, cut_count=1,
                      labels=("Band edge", "End", "Band edge", "End"))
    for e in band.edges:
        e.raw = True
    pat.pieces.append(band)
    pat.seams.append(dict(name="Wrap band ↔ wrap edges and back neck", a=[("front", "wrap", 2), ("back", "neckline", 2)],
                          b=[("wrap_band", "bottom", 1)], type="ratio", lo=0.86, hi=0.94))
    pat.seams.append(dict(name="Crotch: front ↔ back", a=[("front", "crotch", 1)], b=[("back", "crotch", 2)],
                          type="equal", note="the full-width front against both back halves"))
    for s in pat.seams:
        if s["name"].startswith("Leg band"):
            s["a"] = [("front", "leg", 1), ("back", "leg", 1)]
    pat.notes.append("The outer front closes with a snap at the opposite side seam, the inner front with a snap "
                     "inside.")


def assembly(pat):
    import steps as ST
    o = pat.options
    style = o.get("style")
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = []
    if style == "swimsuit":
        out.append(ST.icon("Baste the lining", "needle", "Lay the front lining wrong side onto the wrong side of the "
                           "front and baste them together within the allowances: from now on they are one layer.",
                           stitch="baste", section="Front"))
    base = T.assembly(pat, hem=False, neck=style == "body", done=False)
    for st in base:
        if st.title == "Sew side and sleeve seams" and not pat.has("sleeve"):
            st.title = "Sew the side seams"
            st.text = f"Lay front and back right sides together and sew the side seams with {sa} seam allowance."
            st.data = {}
        out.append(st)
    if style == "wrap":
        out.insert(len(out) - 2 if len(out) > 2 else 0,
                   ST.seam("Bind the wrap edges", ["Wrap band"],
                           "Bind the wrap edges and the back neck in one go with the band, stretching it slightly.",
                           section="Neckline"))
    if pat.has("armhole_band"):
        out.append(ST.seam("Bind the armholes", ["Armhole band"],
                           "Sew the band onto the armholes, stretching it slightly; fold it over and stitch it down.",
                           section="Armholes", repeat=2))
    if style == "swimsuit":
        out += [ST.seam("Sew the crotch seam", ["Crotch seam"],
                        f"Sew front and back together at the crotch with {sa} seam allowance.", section="Crotch"),
                ST.icon("Sew in the elastic", "elastic_on",
                        "Sew the swim elastic with a zigzag onto the wrong side of the leg openings, armholes and "
                        "neckline, stretching it slightly (more at the back of the leg). Turn it in and topstitch "
                        "with a zigzag or twin needle.", section="Openings")]
    else:
        out += [ST.seam("Bind the leg openings", ["Leg band"],
                        "Sew the band onto each leg opening from the front crotch to the back crotch, stretching it. "
                        "Fold it over the allowance and stitch it down.", section="Leg openings", repeat=2),
                ST.hem("Fold the crotch facings", [("front", "crotch"), ("back", "crotch")], 20.0,
                       "Fold the crotch edges of front and back to the inside and stitch them down; interface them "
                       "with a strip of interfacing first.", section="Crotch"),
                ST.icon("Set the snaps", "snap", f"Set {o.get('_snaps', 3)} snaps on the marks: sockets on the back "
                        "crotch (it overlaps), caps on the front.", section="Crotch")]
    out.append(ST.done())
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
