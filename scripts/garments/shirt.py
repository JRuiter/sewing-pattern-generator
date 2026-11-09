"""Shirt and blouse (woven) on the T-shirt block: front opening with a self-faced button stand,
collar (shirt collar with stand, stand collar, Peter Pan or none), back yoke (shirt), bust dart
(blouse), sleeves with a cuff and a sleeve placket or a short-sleeve hem, optional chest pocket.

Styles
- `shirt` (default): back yoke, shirt collar with stand, cuffs, chest pocket on the left front
- `blouse`: bust dart for adults, no yoke, stand or Peter Pan collar look, no pocket
"""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from . import _parts as PT
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(style="shirt", fit="normal", fabric="woven", stretch=None, sleeve_length="long", collar=None,
                yoke=None, bust_dart=None, pocket=None, cuffs=True, sa=10.0, hem_sa=15.0, buttons=None)
FINISHED_LABELS = dict(T.FINISHED_LABELS, cuff=("Cuff (closed)", "width"), collar=("Collar (neckline)", "width"))
FIT_CHECK = "do the buttons close over the chest without pulling, and can you lift your arms?"
STYLE_DEFAULTS = {"shirt": dict(collar="shirt", yoke=True, bust_dart=False, pocket=True),
                  "blouse": dict(collar="stand", yoke=False, bust_dart=True, pocket=False)}

_TOP_KEYS = ("fit", "fabric", "stretch", "sleeve_length", "sa", "hem_sa", "chest_total", "body_length",
             "sleeve_len_total", "construction", "notch_style", "machines", "length", "neck_extra")


def _resolve(options):
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in STYLE_DEFAULTS:
        raise ValueError("shirt style must be shirt or blouse")
    for k, v in STYLE_DEFAULTS[o["style"]].items():
        if o.get(k) is None:
            o[k] = v
    if o["collar"] not in ("shirt", "stand", "peter_pan", "none"):
        raise ValueError("collar must be shirt, stand, peter_pan or none")
    return o


def base(m: dict, o: dict, garment: str, extra: dict | None = None, cuff_h: float = 0.0):
    """T-shirt block for a front-opening woven top: no neckband, no head check (it opens)."""
    top = {k: o[k] for k in _TOP_KEYS if k in o and o[k] is not None}
    top.update(sleeve_style="set_in", neckline="round", sleeve_cuffs=False, hem_band=False, _auto_neck=99)
    top.update(extra or {})
    pat = T.draft(m, top, _garment=garment)
    if cuff_h and o.get("sleeve_length") == "long":
        top["sleeve_len_total"] = pat.options["_sinfo"]["SL"] - cuff_h
        pat = T.draft(m, top, _garment=garment)
    pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
    pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    for k in ("front", "back"):
        pat.piece(k).edge("neckline").sa = o["sa"] * 0.7
    return pat


def add_bust_dart(pat, m) -> float:
    """Bust dart on the front for adult women; the side seam check takes the intake."""
    F = pat.options["_F"]
    intake = clamp(0.028 * m["chest"], 15.0, 32.0) if is_adult(m) else clamp(0.015 * m["chest"], 0.0, 12.0)
    if intake < 8:
        return 0.0
    PT.bust_dart(pat.piece("front"), -(F["AD"] + 45.0), intake, 0.095 * m["chest"])
    for s in pat.seams:
        if s["name"].startswith("Side seam"):
            s.update(type="ease", lo=-intake - 2, hi=-intake + 2, note="the front includes the bust dart")
    return intake


def add_yoke(pat, depth: float):
    """Back yoke: the back is split horizontally `depth` below the neck point."""
    back = pat.piece("back")
    ring = back.seam_ring()
    y = -depth
    cut = G.line(G.P(-5, y), G.P(float(ring[:, 0].max()) + 20, y))
    lower, yoke = PT.split_piece(back, cut, ("back", "yoke"), ("Back", "Yoke"), label="Yoke seam")
    if G.signed_area(yoke.seam_ring()) and yoke.seam_ring()[:, 1].mean() < lower.seam_ring()[:, 1].mean():
        lower, yoke = yoke, lower
        lower.key, lower.name, yoke.key, yoke.name = "back", "Back", "yoke", "Yoke"
    yoke.cut_count = 2
    yoke.part_of = "back"
    yoke.info.append("outer and inner yoke, both on the fold")
    PT.replace_piece(pat, "back", [lower, yoke])
    pat.seams.append(dict(name="Yoke seam (back ↔ yoke)", a=[("back", "split", 1)], b=[("yoke", "split", 1)],
                          type="equal"))
    return yoke


def add_collar(pat, kind: str, m, sa: float, ext: float):
    f, b = pat.piece("front"), pat.piece("back") if not pat.has("yoke") else pat.piece("yoke")
    fn, bn = f.edge("neckline").length - ext, b.edge("neckline").length
    F = pat.options["_F"]
    fpts = dict(neck=f.edge("neckline").pts[:-1] if ext else f.edge("neckline").pts)
    bpts = dict(neck=b.edge("neckline").pts, N=G.P(F["nw"], 0), S=G.P(F["sx"], F["sy"]))
    pieces, info = PT.collar_pieces(kind, fn + bn, m, sa * 0.7, ext=ext if kind != "peter_pan" else 0.0,
                                    front_neck=fn, back_neck=bn, front_pts=fpts, back_pts=bpts)
    pat.pieces += pieces
    key, edge = info["seam"]
    pat.seams.append(dict(name="Collar ↔ neckline", a=[("front", "neckline", 1), (b.key, "neckline", 1)],
                          b=[(key, edge, 1)], type="ease", lo=-ext - 2 if kind == "peter_pan" else -2, hi=2,
                          note="the collar ends at centre front" if kind == "peter_pan" else "stand to the front edge"))
    if kind == "shirt":
        st, co = pat.piece("collar_stand"), pat.piece("collar")
        pat.seams.append(dict(name="Collar round (upper ↔ under collar)", a=[("collar", "point", 1),
                                                                             ("collar", "outer", 1)],
                              b=[("collar", "point", 1), ("collar", "outer", 1)], type="equal"))
        d = st.edge("top").length - co.edge("bottom").length
        pat.seams.append(dict(name="Collar ↔ collar stand", a=[("collar", "bottom", 1)], b=[("collar_stand", "top", 1)],
                              type="ease", lo=min(d, 0) - 1, hi=max(d, 0) + 1,
                              note="the collar ends where the stand runs onto the button stand"))
    elif kind == "peter_pan":
        pat.seams.append(dict(name="Collar round (upper ↔ under collar)", a=[("collar", "outer", 1)],
                              b=[("collar", "outer", 1)], type="equal"))
    else:
        pat.seams.append(dict(name="Stand collar round", a=[("collar_stand", "front", 1), ("collar_stand", "top", 1)],
                              b=[("collar_stand", "front", 1), ("collar_stand", "top", 1)], type="equal"))
    return info


def neck_binding(pat, sa: float):
    """Collarless neckline: a bias strip from front edge to front edge, turned to the inside."""
    f, b = pat.piece("front"), pat.piece("back") if not pat.has("yoke") else pat.piece("yoke")
    nl = 2 * (f.edge("neckline").length + b.edge("neckline").length)
    h = max(4.0, 0.6 * sa)
    band = rect_piece("neckband", "Neck binding (bias)", nl + 2 * sa, 2 * h, sa=sa * 0.7, cut_count=1,
                      labels=("Seam edge", "End", "Seam edge", "End"), grain_vertical=False)
    band.grain = (G.P(nl * 0.3, h * 0.2), G.P(nl * 0.3 + h * 1.6, h * 1.8))
    band.info.append("cut on the bias (45°)")
    band.marks.append(Mark(G.line(G.P(0, h), G.P(nl + 2 * sa, h)), "fold", "Fold line"))
    pat.pieces.append(band)
    pat.seams.append(dict(name="Neck binding ↔ neckline", a=[("front", "neckline", 2), (b.key, "neckline", 2)],
                          b=[("neckband", "bottom", 1)], type="ratio", lo=1.0, hi=1.0 + 2 * sa / nl + 0.02,
                          note="the ends are folded in at the front edges"))


def add_buttons(pat, m, n: int | None, y_top: float | None = None, y_bot: float | None = None) -> int:
    f = pat.piece("front")
    fe = f.edge("front_edge").pts
    top, bot = float(fe[:, 1].max()), float(fe[:, 1].min())
    btn = PT.button_size(m)
    y_top = top - btn if y_top is None else y_top
    y_bot = bot + clamp(0.18 * (top - bot), 60, 130) if y_bot is None else y_bot
    n = n or max(4, int(round((y_top - y_bot) / clamp(0.11 * (top - bot), 60, 100))) + 1)
    PT.buttonholes(f, y_top, y_bot, n, btn + 3, vertical=True)
    pat.notes.append(f"Buttons: {n + (1 if pat.has('collar_stand') else 0)} buttons, {btn:.0f} mm"
                     + (" (+ 2 smaller ones for the cuffs)" if pat.has("cuff") else ""))
    pat.options["_buttons"] = n
    return n


def add_cuffs(pat, m, sa: float, cuff_h: float, ext: float):
    sl = pat.piece("sleeve")
    hem = sl.edge("hem")
    hem.sa, hem.turned, hem.label = sa, False, "Cuff seam (pleats)"
    cl = clamp(m["wrist"] * 1.25, m["wrist"] + 40, m["wrist"] + 80) + ext
    cf = rect_piece("cuff", "Cuff", cl, 2 * cuff_h, sa=sa, cut_count=2,
                    labels=("Sleeve seam", "Cuff end", "Raw edge (folded in)", "Cuff end"), grain_vertical=False)
    cf.marks.append(Mark(G.line(G.P(0, cuff_h), G.P(cl, cuff_h)), "fold", "Fold line"))
    cf.info.append("interface one half")
    pat.pieces.append(cf)
    sw = hem.length
    pat.seams.append(dict(name="Cuff ends", a=[("cuff", "left", 1)], b=[("cuff", "right", 1)], type="equal"))
    pat.seams.append(dict(name="Cuff ↔ sleeve (pleated)", a=[("sleeve", "hem", 1)], b=[("cuff", "bottom", 1)],
                          type="ratio", lo=0.55, hi=1.0, note="one or two pleats at the back of the sleeve"))
    # sleeve placket: a slit at the back quarter of the sleeve hem, bound with a strip
    hp = hem.pts
    x = float(hp[0, 0] + (hp[-1, 0] - hp[0, 0]) * 0.75)
    y = float(hp[:, 1].mean())
    slit = clamp(0.055 * m["height"], 60, 110)
    sl.marks.append(Mark(G.line(G.P(x, y), G.P(x, y + slit)), "mark", "Sleeve placket (slit)"))
    pk = rect_piece("placket", "Placket binding", 2 * slit + 10, 30.0, sa=0.0, cut_count=2,
                    labels=("Binding edge", "End", "Binding edge", "End"), grain_vertical=False)
    for e in pk.edges:
        e.raw = True
    pk.info.append("press both long edges 6 mm in, then fold in half")
    pat.pieces.append(pk)
    del sw
    return cf


def chest_pocket(pat, m, sa: float):
    F = pat.options["_F"]
    w = clamp(0.115 * m["chest"], 70, 125)
    h = w * 1.15
    pts = [G.P(0, w * 0.15), G.P(w / 2, 0), G.P(w, w * 0.15), G.P(w, h), G.P(0, h)]
    edges = [Edge("bottom", G.join(G.line(pts[0], pts[1]), G.line(pts[1], pts[2])), sa, label="Pocket edge"),
             Edge("side", G.line(pts[2], pts[3]), sa, label="Pocket edge"),
             Edge("top", G.line(pts[3], pts[4]), 25.0, label="Pocket opening (hem)", turned=True),
             Edge("side_l", G.line(pts[4], pts[0]), sa, label="Pocket edge")]
    pk = Piece("pocket", "Chest pocket", edges, cut_count=1, mirror=False,
               grain=(G.P(w / 2, h * 0.3), G.P(w / 2, h * 0.8)))
    pat.pieces.append(pk)
    x0, y0 = F["q"] * 0.25, -(F["AD"] + 10)
    pat.piece("front").marks.append(Mark(np.vstack([p + (x0, y0 - h) for p in pts]), "placement", "Chest pocket"))
    return pk


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = _resolve(options)
    m = measures
    sa = o["sa"]
    adult = is_adult(m)
    cuff_h = (60.0 if adult else 45.0) if o["sleeve_length"] == "long" and o["cuffs"] else 0.0
    pat = base(m, o, "shirt", cuff_h=cuff_h)
    if o["bust_dart"]:
        add_bust_dart(pat, m)
    ext = PT.button_size(m)
    PT.button_stand(pat.piece("front"), ext)
    PT.rename_edge_refs(pat, "front", "center", "front_edge")
    if o["yoke"]:
        add_yoke(pat, clamp(0.075 * m["height"], 70, 135))
    if o["collar"] != "none":
        add_collar(pat, o["collar"], m, sa, ext)
    else:
        neck_binding(pat, sa)
    if cuff_h:
        add_cuffs(pat, m, sa, cuff_h, ext)
    if o["pocket"]:
        chest_pocket(pat, m, sa)
    add_buttons(pat, m, o["buttons"])
    pat.notes.append("Interfacing: light iron-on for " + ("the collar, the stand, " if o["collar"] != "none" else "")
                     + ("the cuffs, " if cuff_h else "") + "the button stand (strip 2 × the stand width)")
    pat.title = {"shirt": "Shirt", "blouse": "Blouse"}[o["style"]] + ("" if o["sleeve_length"] == "long"
                                                                       else " (short sleeves)")
    pat.options.update({k: o[k] for k in ("style", "collar", "yoke", "bust_dart", "pocket", "cuffs")})
    pat.options["_ext"] = ext
    if pat.has("cuff"):
        pat.finished["cuff"] = pat.piece("cuff").edge("bottom").length - ext
    return pat


def finished_measures(pat):
    return T.finished_measures(pat)


def front_steps(pat, sec="Front") -> list:
    import steps as ST
    o = pat.options
    has_col = pat.has("collar") or pat.has("collar_stand")
    out = [ST.icon("Interface the facings", "interfacing",
                   "Iron light interfacing onto " + ", ".join(
                       [x for x, on in (("the wrong side of the outer collar pieces", has_col),
                                        ("one half of each cuff", pat.has("cuff"))) if on]
                       + ["a strip along the front edges (button stand)"]).replace(", a strip", " and a strip", 1)
                   + ".",
                   section="Prepare")]
    if any(mk.label == "Bust dart" for mk in pat.piece("front").marks):
        out.append(PT.dart_steps("Front", "Fold each front right sides together on the middle of the dart, the dart "
                                 "lines on top of each other. Sew from the side edge to the point and run off the "
                                 "fold. Press the dart down.", repeat=2))
    if pat.has("pocket"):
        out += [ST.hem("Hem the pocket opening", [("pocket", "top")], 25.0,
                       "Fold the top edge 1 cm and then 1.5 cm to the wrong side and stitch it down.",
                       section="Pocket"),
                ST.place("Stitch the pocket on", "pocket", "front", "Chest pocket",
                         "Press the other edges 1 cm under. Pin the pocket onto the left front on the marking and "
                         "topstitch it close to the edge, reinforcing the top corners with a small triangle.",
                         section="Pocket")]
    ext = o.get("_ext", 18.0)
    out.append(ST.hem("Fold the button stands", [("front", "front_edge")], 2 * ext,
                      f"Fold each front edge {ST.cm(ext)} to the wrong side and then again {ST.cm(ext)} (on the "
                      "fold line), press and stitch close to the inner fold.", repeat=2, section=sec,
                      stitch="topstitch"))
    del sec
    return out


def collar_steps(pat, sec="Collar") -> list:
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("neckline").sa)
    o = pat.options
    out = []
    if pat.has("collar") and pat.has("collar_stand"):
        out += [ST.seam("Sew the collar", ["Collar round"],
                        "Lay upper and under collar right sides together and sew the points and the outer edge. "
                        "Trim the points, turn, press and topstitch 5 mm from the edge.", section=sec),
                ST.seam("Sew the collar into the stand", ["Collar ↔ collar stand"],
                        "Lay the collar between the two stand pieces (right sides of the stands facing the "
                        "collar), centres matching, and sew along the top edge round the stand ends. Turn.",
                        section=sec)]
    elif pat.has("collar"):
        out.append(ST.seam("Sew the collar", ["Collar round"],
                           "Lay upper and under collar right sides together and sew round the outer edge. Trim, "
                           "clip the curve, turn and press.", section=sec))
    elif pat.has("collar_stand"):
        out.append(ST.seam("Sew the stand collar", ["Stand collar round"],
                           "Lay both stand pieces right sides together and sew the top edge and the ends. Trim, "
                           "turn and press.", section=sec))
    if pat.has("neckband") and not (pat.has("collar") or pat.has("collar_stand")):
        out += [ST.fold_band("Fold the binding in half", "neckband",
                             "Fold the bias strip lengthwise wrong sides together and press; shape it into a curve "
                             "with the iron.", section="Neckline", data={"hands": "fold"}),
                ST.seam("Sew the neck binding on", ["Neck binding"],
                        "Lay the binding on the right side of the neckline, raw edges level, from one front edge to "
                        f"the other; let the ends stick out 1 cm. Sew with {sa} seam allowance, trim and clip the "
                        "allowance.", section="Neckline"),
                ST.topstitch("Stitch the binding down", [("front", "neckline")], 2.0,
                             "Fold the ends in, turn the binding to the inside and stitch it down close to the fold.",
                             section="Neckline")]
    if pat.has("collar") or pat.has("collar_stand"):
        out.append(ST.seam("Sew the collar on", ["Collar ↔ neckline"],
                           "Pin the outer layer of the collar right sides together onto the neckline, centre back "
                           f"and the ends matching, and sew with {sa} seam allowance. Clip the neckline allowance, "
                           "fold the inner layer over it, turn its edge under and topstitch close to the edge.",
                           section=sec, hint="Clip the neckline allowance every 1 cm so it follows the collar."))
    del o
    return out


def cuff_steps(pat, sec="Cuffs") -> list:
    import steps as ST
    if not pat.has("cuff"):
        return []
    sa = ST.cm(pat.piece("cuff").edge("bottom").sa)
    return [
        ST.icon("Bind the sleeve placket", "needle",
                "Cut the slit on the marking. Spread it open into a straight line and sew the binding strip "
                "right sides together onto it with 6 mm allowance; fold the binding over the allowance, press, "
                "topstitch. Fold the front half of the binding inside.", section=sec, repeat=2),
        ST.seam("Sew the cuff ends", ["Cuff ends"],
                f"Fold each cuff right sides together on the fold line and sew both ends with {sa} seam "
                "allowance. Trim, turn and press.", section=sec, repeat=2),
        ST.seam("Sew the cuffs on", ["Cuff ↔ sleeve"],
                "Lay one or two pleats at the back of the sleeve hem (pointing to the placket) until it fits the "
                f"cuff. Sew the outer cuff right sides together onto it with {sa} seam allowance, fold the inner "
                "edge under over the allowance and topstitch all round the cuff.", section=sec, repeat=2),
    ]


def assembly(pat):
    import steps as ST
    base_steps = T.assembly(pat, hem=True, neck=False, done=False)
    out = front_steps(pat)
    yoke = []
    if pat.has("yoke"):
        yoke = [ST.seam("Sew the yoke on", ["Yoke seam"],
                        "Lay the back between the outer yoke (right sides together) and the inner yoke (right side "
                        "on the wrong side of the back). Sew through all three layers and fold both yokes up. "
                        "Topstitch 3 mm above the seam.", section="Back",
                        hint="Sew the front shoulders onto the outer yoke, then the inner yoke over them by "
                        "rolling the shirt up inside the yoke (burrito method).")]
    for st in base_steps:
        if st.title == "Sew the shoulder seams":
            out += yoke + [st] + collar_steps(pat)
        elif st.title == "Hem the sleeves" and pat.has("cuff"):
            continue
        else:
            out.append(st)
        if st.title == "Finish the side seams" or (st.title == "Sew side and sleeve seams" and not
                                                   any(s.title == "Finish the side seams" for s in base_steps)):
            out += cuff_steps(pat)
    n = pat.options.get("_buttons", 6)
    out += [ST.icon("Sew buttonholes and buttons", "button",
                    f"Sew {n} vertical buttonholes on the marks of the right front" +
                    (" and one horizontal one in the collar stand" if pat.has("collar_stand") else "") +
                    (", and one in each cuff" if pat.has("cuff") else "") +
                    ". Lay the fronts on top of each other, centre fronts matching, and sew the buttons on the left "
                    "front through the buttonholes' marks.", section="Finish"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
