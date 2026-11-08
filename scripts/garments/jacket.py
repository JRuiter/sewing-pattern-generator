"""Lined woven jacket and coat on the shirt block: more ease, a button front with an overlap and
separate facings (front facing and back neck facing, interfaced), stand collar or none, welt,
jetted or flap pockets, and a full lining (front and back lining = the pieces minus the facings,
sleeve lining) that is bagged with the shell.

`style="coat"` (or the `coat` module) makes it longer (to the knee) with more ease and flap pockets.
"""
from __future__ import annotations

import geometry as G
from pattern import Pattern

from . import _parts as PT
from . import shirt as SH
from ._common import clamp, is_adult

DEFAULTS = dict(style="jacket", fit="normal", fabric="woven", stretch=None, collar="stand", pockets=None,
                lining=True, buttons=None, sa=10.0, hem_sa=40.0, length=None)
FINISHED_LABELS = dict(SH.T.FINISHED_LABELS)
FIT_CHECK = "does it close over a sweater without pulling, and can you cross your arms in front?"
STYLES = {"jacket": dict(ease=0.17, pockets="welt"), "coat": dict(ease=0.24, pockets="flap")}


def _length(m, style, length):
    if length == "hip" or (length is None and style == "jacket"):
        return m["back_length"] + 0.15 * m["height"]
    if length == "thigh":
        return m["back_length"] + 0.25 * m["height"]
    return m["back_length"] + m["side_length"] - 0.285 * m["height"] + 30      # knee


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in STYLES:
        raise ValueError("jacket style must be jacket or coat")
    st = STYLES[o["style"]]
    o["pockets"] = o["pockets"] or st["pockets"]
    if o["collar"] not in ("stand", "none"):
        raise ValueError("jacket collar must be stand or none")
    m = measures
    sa = o["sa"]
    o.setdefault("chest_total", None)
    if not o.get("chest_total"):
        o["chest_total"] = m["chest"] * (1 + st["ease"] + (0.04 if o["fit"] == "wide" else 0))
    o["body_length"] = o.get("body_length") or _length(m, o["style"], o["length"])
    o["sleeve_length"] = "long"
    pat = SH.base(m, o, o["style"], extra=dict(neck_extra=8.0))
    F = pat.options["_F"]
    f, b, sl = pat.piece("front"), pat.piece("back"), pat.piece("sleeve")
    ext = 25.0 if is_adult(m) else 20.0
    PT.button_stand(f, ext, facing=sa, label="Front edge (facing seam)")
    PT.rename_edge_refs(pat, "front", "center", "front_edge")
    for k in ("front", "back"):
        pat.piece(k).edge("neckline").sa = sa
    hem_y = float(f.edge("hem").pts[0, 1])
    # pockets at hip level
    pw = clamp(0.14 * m["hip"], 110, 175)
    y_p = max(-(m["back_length"] + 0.075 * m["height"]), hem_y + 0.6 * pw)
    pk_pieces, pk_seams = PT.welt_pocket(f, o["pockets"], G.P(F["q"] * 0.5, y_p), pw, sa) if o["pockets"] != "none" \
        else ([], [])
    pat.pieces += pk_pieces
    pat.seams += pk_seams
    if o["collar"] == "stand":
        SH.add_collar(pat, "stand", m, sa, ext)
    if o["lining"]:
        _lining(pat, F, ext, sa, m)
    btn = 25.0 if is_adult(m) else 20.0
    fe = f.edge("front_edge").pts
    top = float(fe[:, 1].max())
    y_bot = y_p if o["style"] == "jacket" else top - 0.62 * (top - hem_y)
    n = o["buttons"] or (3 if o["style"] == "jacket" else 5)
    PT.buttonholes(f, top - btn, y_bot, n, btn + 3)
    pat.options["_buttons"] = n
    pat.notes.append(f"Buttons: {n} buttons, {btn:.0f} mm")
    pat.notes.append("Interfacing: medium iron-on for the facings, the collar, the hems (strip 5 cm) and the "
                     "pocket openings")
    pat.title = {"jacket": "Lined jacket", "coat": "Coat"}[o["style"]] if o["lining"] else \
        {"jacket": "Jacket", "coat": "Coat (unlined)"}[o["style"]]
    pat.options.update(style=o["style"], collar=o["collar"], pockets=o["pockets"], lining=o["lining"], _ext=ext)
    for c in pat.checks:
        if c["name"] == "Body length plausible":
            c["hi"] = 0.75 * m["height"]
    del sl
    return pat


def _lining(pat, F, ext, sa, m):
    """Facings and lining: copies of front and back split along the facing line."""
    from pattern import Edge, Piece
    f, b = pat.piece("front"), pat.piece("back")

    def copy(pc, key, name):
        return Piece(key, name, [Edge(e.name, e.pts.copy(), e.sa, e.fold, e.label, e.turned, e.sa_hint, e.pointed,
                                      e.raw) for e in pc.edges], cut_count=pc.cut_count, mirror=pc.mirror,
                     fabric=pc.fabric, grain=pc.grain)
    N, S = G.P(F["nw"], 0), G.P(F["sx"], F["sy"])
    fw = clamp(0.075 * m["chest"], 55, 85)
    hem_y = float(f.edge("hem").pts[0, 1])
    shift = float(f.edge("shoulder").pts[:, 1].max()) - 0.0      # front may sit higher (bust dart)
    Pf = N + (S - N) * 0.35 + (0, shift - N[1] if shift > N[1] + 1 else 0)
    cut_f = G.join(G.line(Pf + (0, 20), Pf), G.cubic(Pf, Pf + (0, -60), G.P(fw - ext, Pf[1] - 160),
                                                     G.P(fw - ext, Pf[1] - 240)),
                   G.line(G.P(fw - ext, Pf[1] - 240), G.P(fw - ext, hem_y - 20)))
    fl, ff = PT.split_piece(copy(f, "front_x", "Front"), cut_f, ("front_lining", "front_facing"),
                            ("Front lining", "Front facing"), label="Facing seam", sa=sa)
    if "front_edge" in [e.name for e in fl.edges]:
        fl, ff = ff, fl
        fl.key, fl.name, ff.key, ff.name = "front_lining", "Front lining", "front_facing", "Front facing"
    ff.marks = [mk for mk in ff.marks if mk.label in ("Centre front", "Buttonhole")]
    fl.marks = []
    ff.info.append("interface it")
    fl.fabric = "Lining"
    Pb = N + (S - N) * 0.35
    bnd = F["bnd"]
    cut_b = G.join(G.line(Pb + (0, 20), Pb), G.cubic(Pb, Pb + (0, -45), G.P(60, -bnd - 70), G.P(-10, -bnd - 70)))
    bl, bf = PT.split_piece(copy(b, "back_x", "Back"), cut_b, ("back_lining", "back_facing"),
                            ("Back lining", "Back neck facing"), label="Facing seam", sa=sa)
    if "hem" not in [e.name for e in bl.edges]:
        bl, bf = bf, bl
        bl.key, bl.name, bf.key, bf.name = "back_lining", "Back lining", "back_facing", "Back neck facing"
    bf.info.append("interface it")
    bl.fabric = "Lining"
    bl.marks = []
    bf.marks = []
    sll = PT.lining_of(pat.piece("sleeve"), "sleeve_lining", "Sleeve lining", sa=sa)
    for pc in (fl, bl):
        h = pc.edge("hem")
        h.sa, h.turned, h.label = sa, False, "Hem (lining, sewn to the hem allowance)"
    sll.edge("hem").label = "Hem (lining, sewn to the sleeve hem allowance)"
    sll.info.append("leave 20 cm open in one sleeve seam for turning")
    pat.pieces += [ff, bf, fl, bl, sll]
    pat.seams += [
        dict(name="Facing ↔ front edge", a=[("front", "front_edge", 1)], b=[("front_facing", "front_edge", 1)],
             type="equal"),
        dict(name="Facing seam front (facing ↔ lining)", a=[("front_facing", "split", 1)],
             b=[("front_lining", "split", 1)], type="equal"),
        dict(name="Facing seam back (facing ↔ lining)", a=[("back_facing", "split", 1)],
             b=[("back_lining", "split", 1)], type="equal"),
        dict(name="Facing shoulders", a=[("front_facing", "shoulder", 1)], b=[("back_facing", "shoulder", 1)],
             type="equal"),
        dict(name="Lining shoulders", a=[("front_lining", "shoulder", 1)], b=[("back_lining", "shoulder", 1)],
             type="equal"),
        dict(name="Lining side seams", a=[("front_lining", "side", 1)], b=[("back_lining", "side", 1)],
             type="equal"),
        dict(name="Lining sleeve seams", a=[("sleeve_lining", "seam_front", 1)],
             b=[("sleeve_lining", "seam_back", 1)], type="equal"),
    ]
    for s in list(pat.seams):
        if s["name"].startswith("Armhole"):
            ren = {"front": "front_lining", "back": "back_lining", "sleeve": "sleeve_lining"}
            pat.seams.append(dict(s, name="Lining armhole ↔ sleeve lining",
                                  a=[(ren.get(k, k), e, n) for k, e, n in s["a"]],
                                  b=[(ren.get(k, k), e, n) for k, e, n in s["b"]]))
            break
    if pat.has("collar_stand"):
        pat.seams.append(dict(name="Inner collar ↔ facing neckline", a=[("front_facing", "neckline", 1),
                                                                        ("back_facing", "neckline", 1)],
                              b=[("collar_stand", "neck", 1)], type="ease", lo=-2, hi=2))


def finished_measures(pat):
    return SH.T.finished_measures(pat)


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    lined = pat.has("front_facing")
    out = [ST.icon("Interface", "interfacing",
                   "Iron interfacing onto the facings, the outer collar, a 5 cm strip along the hems of body and "
                   "sleeves and behind the pocket openings.", section="Prepare")]
    if o.get("pockets") not in (None, "none") and pat.has("pocket_bag"):
        out += PT.welt_steps(o["pockets"], "front")
    for st in SH.T.assembly(pat, hem=False, neck=False, done=False):
        if st.title == "Hem the sleeves":
            continue
        out.append(st)
    if pat.has("collar_stand"):
        out += [ST.seam("Sew the collar on", ["Collar ↔ neckline"],
                        "Pin the outer collar right sides together onto the neckline of the jacket, from front edge "
                        f"to front edge, and sew with {sa} seam allowance. Clip the neckline allowance.",
                        section="Collar")]
    if lined:
        sec = "Lining"
        out += [ST.seam("Sew facings and lining together", ["Facing seam"],
                        f"Sew the front facings to the front linings and the back neck facing to the back lining "
                        f"with {sa} seam allowance; press towards the lining.", section=sec),
                ST.seam("Sew the lining shoulders", ["Facing shoulders", "Lining shoulders"],
                        "Sew the shoulder seams of facings and lining.", section=sec),
                ST.seam("Set in the lining sleeves", ["Lining armhole"],
                        "Set the sleeve linings into the armholes of the lining like the sleeves.", section=sec),
                ST.seam("Sew the lining side seams", ["Lining side seams", "Lining sleeve seams"],
                        "Sew side and sleeve seams of the lining in one go; leave 20 cm open in one sleeve seam.",
                        section=sec)]
        if pat.has("collar_stand"):
            out.append(ST.seam("Sew the inner collar on", ["Inner collar"],
                               "Sew the inner collar onto the neckline of the facings in the same way.", section=sec))
        out += [ST.seam("Sew facing and jacket together", ["Facing ↔ front edge"],
                        "Lay the lining into the jacket right sides together. Sew from the hem up the front edge, "
                        "round the collar (or along the neckline) and down the other front edge. Trim the corners, "
                        "turn the facings and press.", section="Finish",
                        hint="Understitch the facing close to the seam so it rolls inside."),
                ST.hem("Hem the jacket", [("front", "hem"), ("back", "hem"), ("sleeve", "hem")],
                       pat.piece("front").edge("hem").sa,
                       "Fold the hems of body and sleeves up and press. Sew the lining hems right sides together "
                       "onto the hem allowances (the lining forms a small fold over the hem: it needs that room).",
                       section="Finish"),
                ST.icon("Turn and close the lining", "hand",
                        "Turn the jacket through the opening in the sleeve lining and close it by machine close "
                        "to the fold.", stitch="topstitch", section="Finish")]
    else:
        out.append(ST.hem("Hem the jacket", [("front", "hem"), ("back", "hem"), ("sleeve", "hem")],
                          pat.piece("front").edge("hem").sa, "Fold the hems up twice and stitch them down.",
                          section="Finish"))
    n = o.get("_buttons", 3)
    out += [ST.icon("Sew buttonholes and buttons", "button",
                    f"Sew {n} horizontal buttonholes on the marks of the right front (women) or the left front (men) "
                    "and the buttons on the other front, centre fronts on top of each other.", section="Finish"),
            ST.done("Press the jacket over a ham, with a pressing cloth.")]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
