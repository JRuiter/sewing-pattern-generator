"""Pinafore / strap dress (woven or sweat): a lined bib bodice (front higher than the back),
two straps crossing at the back and buttoned onto the bib, and a gathered (or A-line) skirt at
the waist seam. Worn over a T-shirt or a blouse; pulled on over the head."""
from __future__ import annotations

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from . import _parts as PT
from . import dress as D
from ._common import is_adult

DEFAULTS = dict(fabric="woven", stretch=None, fit="wide", skirt="gathered", length="knee", gather=1.5,
                pockets=False, sa=10.0, hem_sa=25.0)
FINISHED_LABELS = {k: v for k, v in D.FINISHED_LABELS.items() if not k.startswith("sleeve") and
                   k not in ("bicep_circ", "neckline")}
FINISHED_LABELS.update(strap=("Strap length", "length"))
FIT_CHECK = "does the bib reach to just below the armpits, and do the straps stay on the shoulders when you move?"


def _copy(pc, key, name, fabric):
    return Piece(key, name, [Edge(e.name, e.pts.copy(), e.sa, e.fold, e.label, e.turned, e.sa_hint, e.pointed, e.raw)
                             for e in pc.edges], cut_count=pc.cut_count, mirror=pc.mirror, fabric=fabric,
                 grain=pc.grain)


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    dopts = {k: v for k, v in o.items()}
    dopts.update(style="waist_seam", back_opening=False, waist_elastic=False, sleeve_length="short",
                 neck_finish="bias")
    pat = D.draft(m, dopts)
    pat.garment = "pinafore"
    F = pat.options["_F"]
    q, AD = F["q"], F["AD"]
    # drop sleeve and neck finish
    pat.pieces = [p for p in pat.pieces if p.key not in ("sleeve", "neckband")]
    pat.checks = [c for c in pat.checks if "leeve" not in c["name"] and "cap" not in c["name"].lower()
                  and "head" not in c["name"] and "Neck" not in c["name"]]
    pat.notes = [n for n in pat.notes if "Neckline" not in n]
    for key, y_cf in (("front", -AD * 0.82), ("back", -(AD + 20))):
        pc = pat.piece(key)
        y_s = -(AD + 20)
        cut = G.cubic(G.P(-5, y_cf), G.P(q * 0.45, y_cf), G.P(q * 0.55, y_s), G.P(q + 30, y_s))
        parts = PT.split_piece(pc, cut, (key, key + "_x"), ("Front bib" if key == "front" else "Back bodice", ""),
                               label="Top edge (lined)", sa=sa)
        lower = next(p for p in parts if "hem" in [e.name for e in p.edges])
        lower.key = key
        lower.name = "Front bib" if key == "front" else "Back bodice"
        lower.marks = []
        i = [p.key for p in pat.pieces].index(key)
        pat.pieces[i] = lower
    pat.seams = [s for s in pat.seams if all(any(e.name == en for e in pat.piece(k).edges)
                                             for k, en, _ in s["a"] + s["b"] if pat.has(k))
                 and all(pat.has(k) for k, _, _ in s["a"] + s["b"])]
    pat.corners = [c for c in pat.corners if "sum" not in c and pat.has(c["piece"]) and
                   {c["a"], c["b"]} <= {e.name for e in pat.piece(c["piece"]).edges}]
    f, b = pat.piece("front"), pat.piece("back")
    f.edge("split").name = "top"
    b.edge("split").name = "top"
    fl = _copy(f, "front_lining", "Front bib lining", "Lining or main fabric")
    bl = _copy(b, "back_lining", "Back bodice lining", "Lining or main fabric")
    for pc in (fl, bl):
        pc.edge("hem").label = "Lower edge (turned under)"
    pat.pieces += [fl, bl]
    pat.seams += [dict(name="Top edge (bodice ↔ lining)", a=[("front", "top", 1), ("back", "top", 1)],
                       b=[("front_lining", "top", 1), ("back_lining", "top", 1)], type="equal"),
                  dict(name="Lining side seams", a=[("front_lining", "side", 1)], b=[("back_lining", "side", 1)],
                       type="equal")]
    # straps: from the back top edge over the shoulder to the bib, crossed at the back
    sw = 30.0 if is_adult(m) else 22.0
    sl = (AD * 0.82 + AD + 20) * 1.12 + 80
    strap = rect_piece("strap", "Strap", 2 * sw, sl, sa=sa, cut_count=2,
                       labels=("Strap end (into the back seam)", "Strap edge", "Strap end (buttonhole)",
                               "Strap edge"))
    strap.marks.append(Mark(G.line(G.P(sw, 0), G.P(sw, sl)), "fold", "Fold line"))
    strap.marks.append(Mark(G.line(G.P(sw / 2, sl - 25), G.P(sw / 2, sl - 25 - PT.button_size(m) - 3)), "mark",
                            "Buttonhole"))
    pat.pieces.append(strap)
    pat.seams.append(dict(name="Straps", a=[("strap", "right", 1)], b=[("strap", "left", 1)], type="equal"))
    ftop = f.edge("top").pts
    bx = float(ftop[:, 0].max()) * 0.55
    f.marks.append(Mark(G.line(G.P(bx, float(ftop[:, 1].max()) - 18), G.P(bx, float(ftop[:, 1].max()) - 22)),
                        "mark", "Button"))
    btop = b.edge("top").pts
    b.marks.append(Mark(G.line(G.P(q * 0.35, float(btop[:, 1].max())), G.P(q * 0.35 + sw, float(btop[:, 1].max()))),
                        "placement", "Strap (crossed)"))
    pat.notes.append(f"Buttons: 2 buttons, {PT.button_size(m):.0f} mm")
    pat.title = "Pinafore dress"
    pat.finished = {k: v for k, v in pat.finished.items() if k in FINISHED_LABELS}
    pat.finished["strap"] = sl
    pat.finished["length"] = -float(f.edge("hem").pts[0, 1]) - abs(float(ftop[:, 1].max())) + \
        pat.finished.get("skirt_length", 0)
    return pat


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = [ST.seam("Sew the straps", ["Straps"],
                   f"Fold each strap lengthwise right sides together and sew the long edge and the buttonhole end "
                   f"with {sa} seam allowance. Turn, press and topstitch.", section="Straps", repeat=2),
           ST.place("Baste the straps on", "strap", "back", "Strap (crossed)",
                    "Cross the straps and baste their open ends onto the right side of the back top edge on the "
                    "markings, pointing down.", stitch="baste", section="Straps"),
           ST.seam("Sew the side seams", ["Side seam"],
                   f"Sew the side seams of the bodice with {sa} seam allowance.", section="Bodice"),
           ST.seam("Sew the lining side seams", ["Lining side seams"],
                   "Sew the side seams of the lining the same way.", section="Bodice"),
           ST.seam("Sew bodice and lining together", ["Top edge"],
                   "Lay the lining into the bodice right sides together, the straps between them, and sew round the "
                   f"top edge with {sa} seam allowance. Clip the curves, turn and press; topstitch the top edge.",
                   section="Bodice")]
    base = [st for st in D.assembly(pat) if st.section in ("Skirt", "Pockets", "Waist", "Hem")
            or st.title.startswith(("Sew skirt", "Gather", "Sew the hem", "Finish the waist", "Sew the skirt"))]
    out += base
    out += [ST.topstitch("Close the lining at the waist", [("front_lining", "hem"), ("back_lining", "hem")], 2.0,
                         "Turn the lower edge of the lining under over the waist seam allowance and stitch it down "
                         "close to the fold (or stitch in the ditch from the right side).", section="Finish"),
            ST.icon("Sew on the buttons", "button",
                    "Try the dress on, button the straps onto the bib and sew the buttons on.", section="Finish"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
