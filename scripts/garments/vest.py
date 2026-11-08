"""Vest / gilet (sleeveless): T-shirt block without sleeves, a slightly lowered armhole finished
with a binding, front closure with a separating zip, snaps (with an overlap) or none (pullover
vest), optional stand collar and patch pockets. Fleece, sweat or woven."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Mark, Pattern, rect_piece

from . import _parts as PT
from . import hoodie as H
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(fit="wide", fabric="fleece", stretch=None, closure="zip", collar=True, pockets=True,
                sa=10.0, hem_sa=20.0, binding_fabric="main")
FINISHED_LABELS = {k: v for k, v in T.FINISHED_LABELS.items() if not k.startswith("sleeve") and k != "bicep_circ"}
FINISHED_LABELS.update(armhole=("Armhole", "width"))
FIT_CHECK = "does it close over a sweater, and do the armholes leave room without gaping?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["closure"] not in ("zip", "snaps", "none"):
        raise ValueError("vest closure must be zip, snaps or none")
    m = measures
    sa = o["sa"]
    top = {k: o[k] for k in ("fit", "fabric", "stretch", "sa", "hem_sa", "chest_total", "body_length",
                             "construction", "machines", "notch_style") if k in o}
    top.update(sleeve_length="short", sleeve_cuffs=False, hem_band=False, neckline="round",
               _auto_neck=99 if o["closure"] != "none" else 0)
    pat = T.draft(m, top, _garment="vest")
    F = pat.options["_F"]
    # no sleeves: drop the sleeve and everything that refers to it
    pat.pieces = [p for p in pat.pieces if p.key not in ("sleeve",)]
    pat.seams = [s for s in pat.seams if not any(k == "sleeve" for k, _, _ in s["a"] + s["b"])]
    pat.corners = [c for c in pat.corners if c.get("piece") != "sleeve"]
    pat.checks = [c for c in pat.checks if "leeve" not in c["name"] and "cap" not in c["name"].lower()]
    f, b = pat.piece("front"), pat.piece("back")
    for pc in (f, b):
        pc.notches = [n for n in pc.notches if n.edge != "armhole"]
        pc.edge("armhole").label = "Armhole (binding)"
    stretch = F["stretch"]
    knit = F["knit"]
    arm = f.edge("armhole").length + b.edge("armhole").length
    ratio = 0.92 if knit else 1.0
    bind_w = 10.0 if is_adult(m) else 8.0
    ab = rect_piece("armhole_binding", "Armhole binding", arm * ratio + 2 * sa, 4 * bind_w, sa=0.0, cut_count=2,
                    labels=("Binding edge", "End", "Binding edge", "End"), grain_vertical=knit)
    for e in ab.edges:
        e.raw = True
    ab.info.append("cut on the bias (woven) or across the stretch (knit); press both long edges to the middle")
    pat.pieces.append(ab)
    pat.seams.append(dict(name="Armhole binding ↔ armhole", a=[("front", "armhole", 1), ("back", "armhole", 1)],
                          b=[("armhole_binding", "bottom", 1)], type="ratio", lo=ratio - 0.02,
                          hi=ratio + 2 * sa / arm + 0.03, note="binding ends overlap at the side seam"))
    # neckline and front
    if o["closure"] == "none":
        pass
    else:
        if pat.has("neckband"):
            pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
            pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
            pat.checks = [c for c in pat.checks if "over the head" not in c["name"]]
            pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
        for pc in (f, b):
            pc.edge("neckline").sa = sa
        if o["closure"] == "zip":
            H._zip_front(pat, sa, False, False, m)
            pat.notes = [n for n in pat.notes if "hood" not in n]
            if o["collar"]:      # the zip runs up the collar
                ch = 45.0 if is_adult(m) else 35.0
                pat.notes.append(f"With the collar the zip may run up to its top: about "
                                 f"{(f.edge('center').length + ch) / 10:.0f} cm.")
        else:
            ext = PT.button_size(m)
            PT.button_stand(f, ext, facing=None)
            pat.options["_ext"] = ext
            PT.rename_edge_refs(pat, "front", "center", "front_edge")
            fe = f.edge("front_edge").pts
            n = max(4, int((fe[:, 1].max() - fe[:, 1].min()) / 90))
            ys = PT.buttonholes(f, float(fe[:, 1].max()) - 20, float(fe[:, 1].min()) + 40, n, 1.0, label="Snap")
            pat.notes.append(f"Snaps: {n + (1 if o['collar'] else 0)} snaps (12–15 mm)")
            del ys
        if o["collar"]:
            neck_half = f.edge("neckline").length + b.edge("neckline").length - \
                (PT.button_size(m) if o["closure"] == "snaps" else 0.0)
            ch = 45.0 if is_adult(m) else 35.0
            L = neck_half + (PT.button_size(m) if o["closure"] == "snaps" else 0.0)
            col = rect_piece("collar", "Stand collar", L, 2 * ch, sa=sa, cut_count=1, fold_left=True,
                             labels=("Neckline seam", "Front end", "Inner neckline seam", "Centre back"))
            col.marks.append(Mark(G.line(G.P(0, ch), G.P(L, ch)), "fold", "Fold line"))
            pat.pieces.append(col)
            pat.seams.append(dict(name="Collar ↔ neckline", a=[("front", "neckline", 1), ("back", "neckline", 1)],
                                  b=[("collar", "bottom", 1)], type="equal"))
    if o["pockets"]:
        pw = clamp(0.15 * m["chest"], 90, 170)
        ph = pw * 1.1
        pk = rect_piece("pocket", "Patch pocket", pw, ph, sa=sa, cut_count=2,
                        labels=("Pocket edge", "Pocket edge", "Pocket opening (hem)", "Pocket edge"),
                        sas=(sa, sa, 25.0, sa))
        pk.edges[2].turned = True
        pat.pieces.append(pk)
        hem_y = float(f.edge("hem").pts[0, 1])
        x0, y0 = F["q"] * 0.3, hem_y + 35
        f.marks.append(Mark(np.array([[x0, y0], [x0 + pw, y0], [x0 + pw, y0 + ph], [x0, y0 + ph]]),
                            "placement", "Patch pocket"))
    pat.title = "Vest"
    pat.options.update(closure=o["closure"], collar=o["collar"], pockets=o["pockets"])
    fin = pat.finished
    pat.finished = {k: v for k, v in fin.items() if k in FINISHED_LABELS}
    pat.finished["armhole"] = 2 * arm
    return pat


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    out = []
    if pat.has("pocket"):
        out += [ST.hem("Hem the pocket openings", [("pocket", "top")], 25.0,
                       "Fold the top edge 2.5 cm to the wrong side and stitch it down.", section="Pockets", repeat=2),
                ST.place("Stitch the pockets on", "pocket", "front", "Patch pocket",
                         "Press the other edges 1 cm under, pin each pocket on its marking and topstitch it close "
                         "to the edge.", section="Pockets", repeat=2)]
    if pat.has("front") and any(e.name == "front_edge" for e in pat.piece("front").edges):
        ext = o.get("_ext", 18.0)
        out.append(ST.hem("Fold the front edges", [("front", "front_edge")], 2 * ext,
                          "Fold each front edge twice to the wrong side on the fold line, press and stitch it "
                          "down.", repeat=2, section="Front", stitch="topstitch"))
    out += [ST.seam("Sew the shoulder seams", ["Shoulder seam"],
                    f"Lay front and back right sides together and sew the shoulders with {sa} seam allowance.",
                    repeat=2, section="Shoulders"),
            ST.seam("Bind the armholes", ["Armhole binding"],
                    "Unfold one edge of the binding and sew it right sides together onto the armhole with 1 cm "
                    "allowance in the crease, the ends overlapping 2 cm at the side seam. Fold it over the "
                    "allowance to the inside and stitch it down from the right side.", repeat=2,
                    section="Armholes"),
            ST.seam("Sew the side seams", ["Side seam"],
                    f"Lay front and back right sides together and sew the side seams with {sa} seam allowance, "
                    "across the binding ends.", repeat=2, section="Sides")]
    if pat.has("collar"):
        out.append(ST.seam("Sew the collar on", ["Collar ↔ neckline"],
                           "Pin one long edge of the collar right sides together onto the neckline, centre back on "
                           f"centre back, and sew with {sa} seam allowance. Fold the collar on the fold line, turn "
                           "the inner edge under and topstitch it down.", section="Collar"))
    if o.get("closure") == "zip":
        out.append(ST.seam("Sew the zip in", ["Zip"],
                           "Pin each half of the separating zip right sides together onto a front edge, the teeth "
                           "towards the middle" + (", up to the top of the collar" if pat.has("collar") else "")
                           + f". Sew with a zipper foot, {sa} from the edge, fold the allowance inside and topstitch "
                           "7 mm from the teeth.", section="Front"))
    elif o.get("closure") == "snaps":
        out.append(ST.icon("Set the snaps", "snap", "Set the snaps on the marks, caps on the right front, sockets on "
                           "the left one.", section="Finish"))
    elif pat.has("neckband"):
        out += [ST.ring("Close the neckband into a ring", "neckband",
                        f"Fold the band crosswise right sides together and sew the short edges with {sa} seam "
                        "allowance.", section="Neckline"),
                ST.attach_band("Sew the neckband on", "neckband", ["Neckband"], "neckline",
                               "Fold the band lengthwise, pin it at the quarters and sew it on, stretching the band.",
                               section="Neckline", data={"hands": "stretch"})]
    hs = pat.piece("front").edge("hem").sa
    out += [ST.hem("Sew the hem", [("front", "hem"), ("back", "hem")], hs,
                   f"Fold the hem {ST.cm(hs)} to the wrong side and stitch it down.", section="Hem"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
