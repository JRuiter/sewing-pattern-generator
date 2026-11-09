"""Bags (no body measurements): `tote` (outer bag and lining with boxed corners, two handles,
optional inner pocket) and `drawstring` (gym bag cut on the fold, casing with two cords that
also form the shoulder straps). Size from a preset or from width/height/depth in cm."""
from __future__ import annotations

import geometry as G
from pattern import Edge, Mark, Pattern, Piece, rect_piece

from ._common import resolve

NO_MEASURES = True
PRESETS = {
    "tote": {"small": (30, 32, 8), "medium": (38, 40, 10), "large": (45, 42, 14)},
    "drawstring": {"small": (30, 38, 0), "medium": (35, 42, 0), "large": (40, 48, 0)},
}
DEFAULTS = dict(style="tote", bag_size="medium", width_cm=None, height_cm=None, depth_cm=None, fabric="woven",
                stretch=None, pocket=True, handle_cm=None, lining=True, sa=10.0)
FINISHED_LABELS = {"width": ("Width", "width"), "height": ("Height", "length"), "depth": ("Depth", "width")}
FIT_CHECK = "is the size right, and do the handles sit comfortably on the shoulder?"
FABRIC_NOTE = "sturdy woven fabric such as canvas, denim or cotton twill (from about 250 g/m²)"


def _size(o: dict) -> tuple[float, float, float]:
    style = o["style"]
    if style not in PRESETS:
        raise ValueError("bag style must be tote or drawstring")
    if o["bag_size"] not in PRESETS[style]:
        raise ValueError("bag_size must be small, medium or large")
    W, H, D = PRESETS[style][o["bag_size"]]
    W = o["width_cm"] or W
    H = o["height_cm"] or H
    D = o["depth_cm"] if o["depth_cm"] is not None else D
    return W * 10.0, H * 10.0, D * 10.0


def _boxed_panel(key: str, name: str, Wp: float, Hp: float, c: float, sa: float, fabric: str) -> Piece:
    """Rectangle Wp × Hp with a square c × c cut out of both lower corners (boxed corners)."""
    pts = [G.P(c, 0), G.P(Wp - c, 0), G.P(Wp - c, c), G.P(Wp, c), G.P(Wp, Hp), G.P(0, Hp), G.P(0, c), G.P(c, c)]
    names = ["bottom", "box_r_v", "box_r_h", "right", "top", "left", "box_l_h", "box_l_v"]
    labels = ["Bottom", "Boxed corner", "Boxed corner", "Side seam", "Top edge", "Side seam", "Boxed corner",
              "Boxed corner"]
    edges = [Edge(n, G.line(pts[i], pts[(i + 1) % 8]), sa, label=lab) for i, (n, lab) in enumerate(zip(names, labels))]
    return Piece(key, name, edges, cut_count=2, mirror=False, fabric=fabric,
                 grain=(G.P(Wp / 2, Hp * 0.25), G.P(Wp / 2, Hp * 0.75)))


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = resolve(DEFAULTS, options)
    W, H, D = _size(o)
    sa = o["sa"]
    pieces, seams, notes = [], [], []
    if o["style"] == "tote":
        c = D / 2
        Wp, Hp = W + D, H + c
        outer = _boxed_panel("panel", "Bag", Wp, Hp, c, sa, "Main fabric")
        outer.info.append("Optional: iron-on interfacing")
        pieces.append(outer)
        notes.append("Optional: medium iron-on interfacing for the bag pieces if the fabric is soft")
        seams += [dict(name="Side seams", a=[("panel", "right", 1)], b=[("panel", "left", 1)], type="equal"),
                  dict(name="Bottom seam", a=[("panel", "bottom", 1)], b=[("panel", "bottom", 1)], type="equal"),
                  dict(name="Boxed corners", a=[("panel", "box_r_h", 2), ("panel", "box_l_h", 2)],
                       b=[("panel", "box_r_v", 2), ("panel", "box_l_v", 2)], type="equal")]
        if o["lining"]:
            lin = _boxed_panel("lining", "Lining", Wp, Hp, c, sa, "Lining")
            pieces.append(lin)
            seams += [dict(name="Lining side seams", a=[("lining", "right", 1)], b=[("lining", "left", 1)],
                           type="equal"),
                      dict(name="Lining bottom seam", a=[("lining", "bottom", 1)], b=[("lining", "bottom", 1)],
                           type="equal"),
                      dict(name="Lining boxed corners", a=[("lining", "box_r_h", 2), ("lining", "box_l_h", 2)],
                           b=[("lining", "box_r_v", 2), ("lining", "box_l_v", 2)], type="equal"),
                      dict(name="Top edge (bag ↔ lining)", a=[("panel", "top", 2)], b=[("lining", "top", 2)],
                           type="equal")]
        else:
            outer.edge("top").sa = 30.0
            outer.edge("top").turned = True
            outer.edge("top").label = "Hem"
        # handles: cut 4 × the finished width, pressed in quarters
        hw = 30.0
        hl = (o["handle_cm"] or (60 if o["bag_size"] != "small" else 50)) * 10.0
        hd = rect_piece("handle", "Handle", 2 * hw, hl, sa=10.0, cut_count=2,
                        names=("end_a", "right", "end_b", "left"),
                        labels=("Handle end", "Folded edge", "Handle end", "Folded edge"))
        for e in (hd.edge("right"), hd.edge("left")):
            e.sa, e.turned = hw, True
        hd.marks.append(Mark(G.line(G.P(hw, 0), G.P(hw, hl)), "fold", "Fold line"))
        pieces.append(hd)
        gap = min(W * 0.35, 120.0)
        for x in ((Wp - gap) / 2, (Wp + gap) / 2):
            for pc in [outer]:
                pc.marks.append(Mark(G.line(G.P(x - hw / 2, Hp - 1), G.P(x + hw / 2, Hp - 1)), "placement", "Handle"))
        if o["pocket"] and o["lining"]:
            pw, ph = min(W * 0.55, 200.0), min(H * 0.45, 170.0)
            pk = rect_piece("pocket", "Inner pocket", pw, ph, sa=10.0, cut_count=1, fabric="Lining",
                            labels=("Pocket edge", "Pocket edge", "Pocket opening", "Pocket edge"))
            pk.edge("top").sa, pk.edge("top").turned = 25.0, True
            pieces.append(pk)
            x0, y0 = (Wp - pw) / 2, Hp - 60 - ph
            pieces[1].marks.append(Mark(G.join(G.line(G.P(x0, y0 + ph), G.P(x0, y0)), G.line(G.P(x0, y0), G.P(x0 + pw, y0)),
                                               G.line(G.P(x0 + pw, y0), G.P(x0 + pw, y0 + ph))), "placement",
                                        "Pocket placement"))
        title = "Tote bag"
    else:
        Hp = H + 45.0
        bag = rect_piece("bag", "Bag", W, Hp, sa=sa, fold_bottom=True, cut_count=1,
                         names=("bottom", "right", "top", "left"),
                         labels=("Bottom fold", "Side seam", "Casing", "Side seam"), grain_vertical=False)
        bag.edge("top").sa, bag.edge("top").turned = 45.0, True
        bag.marks.append(Mark(G.line(G.P(W - 2, Hp - 40), G.P(W - 2, Hp)), "mark", "Leave open"))
        bag.marks.append(Mark(G.line(G.P(2, Hp - 40), G.P(2, Hp)), "mark", "Leave open"))
        pieces.append(bag)
        seams += [dict(name="Side seams", a=[("bag", "right", 1)], b=[("bag", "right", 1)], type="equal"),
                  dict(name="Side seams (left)", a=[("bag", "left", 1)], b=[("bag", "left", 1)], type="equal")]
        cord = 2 * W + 2 * H + 300
        notes.append(f"Cord: 2 pieces of {cord / 10:.0f} cm (5–8 mm thick)")
        tab = rect_piece("tab", "Corner loop", 40.0, 80.0, sa=10.0, cut_count=2,
                         labels=("Loop end", "Loop edge", "Loop end", "Loop edge"))
        pieces.append(tab)
        bag.marks.append(Mark(G.line(G.P(W - 1, 20), G.P(W - 1, 50)), "placement", "Corner loop"))
        bag.marks.append(Mark(G.line(G.P(1, 20), G.P(1, 50)), "placement", "Corner loop"))
        title = "Drawstring bag"
    label = f"{W / 10:g} × {H / 10:g}" + (f" × {D / 10:g} cm" if D else " cm")
    pat = Pattern("bag", title, label, pieces, dict(measures), o, seams=seams, corners=[], checks=[], notes=notes)
    pat.finished = dict(width=W, height=H, depth=D)
    return pat


BOX_X_HINT = ("The handles carry the load: sew a square with a cross through all layers over every handle end, "
              "between the two stitching lines.")


def assembly(pat):
    import steps as ST
    o = pat.options
    out = []
    if o["style"] == "drawstring":
        sa = ST.cm(pat.piece("bag").edge("right").sa)
        out += [
            ST.press("Press the corner loops", [("tab", "right"), ("tab", "left")],
                     "Press each loop in half lengthwise, then fold both long edges into the middle and press again.",
                     section="Loops"),
            ST.topstitch("Topstitch the loops", [("tab", "right")], 2.0,
                         "Topstitch along the open long edge. Fold each loop in half crosswise.", section="Loops"),
            ST.place("Baste the loops on", "tab", "bag", "Corner loop",
                     "Pin the folded loops at the marks of the lower corners onto the right side, loop pointing "
                     "inwards, raw ends level with the side edge, and baste them.", stitch="baste", section="Bag"),
            ST.seam("Sew the side seams", ["Side seams"],
                    f"Fold the bag right sides together at the bottom fold. Sew both side seams with {sa} seam "
                    "allowance, from the bottom up to the 'leave open' mark; the top 4 cm stay open.", section="Bag",
                    hint="Backstitch well at the mark and over the loops."),
            ST.press("Press the allowances open", [("bag", "right"), ("bag", "left")],
                     "Press the allowances open, also along the open part; topstitch them down there in a U shape.",
                     section="Bag"),
            ST.hem("Sew the casing", [("bag", "top")], 45.0,
                   "Fold the upper edge 1 cm, then 3.5 cm to the wrong side and press. Sew close to the lower fold "
                   "all round; front and back stay separate tunnels.", section="Casing"),
            ST.icon("Thread the cords", "elastic",
                    "Thread one cord with a safety pin through the front tunnel and back through the back tunnel, "
                    "the second cord the other way round, starting at the other side. Pull each pair of ends through "
                    "the loop of its corner and knot it.", section="Casing", data={"label": "cord, with a safety pin"}),
            ST.done(""),
        ]
        return out
    sa = ST.cm(pat.piece("panel").edge("right").sa)
    hd = pat.piece("handle")
    out += [
        ST.press("Press the handles", [("handle", "right"), ("handle", "left")],
                 "Press each handle in half lengthwise, open it, fold both long edges into the middle and press, then "
                 "fold in half again: 4 layers.", section="Handles"),
        ST.topstitch("Topstitch the handles", [("handle", "right"), ("handle", "left")], 3.0,
                     "Topstitch 3 mm from both long edges.", section="Handles"),
    ]
    if pat.has("pocket"):
        pk = pat.piece("pocket")
        out += [
            ST.hem("Hem the pocket opening", [("pocket", "top")], pk.edge("top").sa,
                   f"Fold the upper pocket edge 1 cm, then {ST.cm(pk.edge('top').sa - 10)} to the wrong side and "
                   "sew it down close to the lower fold.", section="Inner pocket"),
            ST.press("Press the pocket edges", [("pocket", "left"), ("pocket", "bottom"), ("pocket", "right")],
                     "Press the other three edges 1 cm to the wrong side.", section="Inner pocket"),
            ST.place("Sew the pocket onto the lining", "pocket", "lining", "Pocket placement",
                     "Pin the pocket onto the marked spot of one lining piece and topstitch sides and bottom 2 mm from "
                     "the edge.", section="Inner pocket", amount=2.0),
        ]
    out += [
        ST.seam("Sew side and bottom seams", ["Side seams", "Bottom seam"],
                f"Lay both bag pieces right sides together. Sew the side seams and the bottom seam with {sa} seam "
                "allowance; the cut-out corners stay open.", section="Bag"),
        ST.seam("Sew the boxed corners", ["Boxed corners"],
                "Pull each open corner apart so that side seam and bottom seam lie on top of each other. Sew the raw "
                f"edge straight across with {sa} seam allowance.", section="Bag", diagram="boxed_corner",
                hint="Press the side seam and the bottom seam allowances in opposite directions so they nest."),
    ]
    if pat.has("lining"):
        out += [
            ST.icon("Turn the bag", "turn", "Turn the outer bag right side out and push the corners out.",
                    section="Bag"),
            ST.seam("Sew the lining", ["Lining side seams", "Lining bottom seam"],
                    f"Sew the lining the same way with {sa} seam allowance, but leave 12 cm open in the bottom seam "
                    "for turning.", section="Lining"),
            ST.seam("Box the lining corners", ["Lining boxed corners"],
                    f"Sew the corners of the lining like those of the bag, with {sa} seam allowance.", section="Lining",
                    diagram="boxed_corner"),
            ST.place("Baste the handles on", "handle", "panel", "Handle",
                     "Pin the handle ends at the marks, raw ends level with the top edge, the "
                     f"handle hanging down (not twisted). Baste {ST.cm(hd.edge('end_a').sa / 2)} from the edge.",
                     stitch="baste", section="Bag"),
            ST.seam("Sew the top edge", ["Top edge"],
                    "Put the bag (right side out) into the lining (wrong side out), right sides together. Match the "
                    f"side seams and sew round the top edge with {sa} seam allowance.", section="Finish"),
            ST.icon("Turn and close the lining", "turn",
                    "Turn the bag through the opening in the lining. Fold the allowances of the opening in and "
                    "topstitch it closed close to the edge.", section="Finish"),
            ST.topstitch("Topstitch the top edge", [("panel", "top")], 5.0,
                         "Push the lining into the bag, press the top edge and topstitch 5 mm from it.",
                         section="Finish", hint=BOX_X_HINT, data={"handles": "up"}),
        ]
    else:
        hem = pat.piece("panel").edge("top").sa
        out.append(ST.icon("Turn the bag", "turn", "Turn the bag right side out and push the corners out.",
                           section="Bag"))
        own = ST.owned_machines(o)
        if own is not None and "overlocker" in own:
            # the overlocker finishes the raw edge, so a single turn is enough (flatter than a double fold)
            # without a sewing machine the "finish" kind means "already done by the overlock seam":
            # this raw edge is overlocked on its own, like a seam
            import machines as MC
            out += [ST.finish("Finish the top edge", [("panel", "top")],
                              "Overlock the top edge all round, just skimming it with the knife.", section="Finish",
                              stitch="finish" if MC.has_sewing_machine(own) else "seam", data={"no_phrase": True}),
                    ST.hem("Hem the top edge", [("panel", "top")], hem,
                           f"Fold the top edge {ST.cm(hem)} to the wrong side and press. Slip the handle ends "
                           "under the fold at the marks, the handles hanging down (not twisted), and sew close to "
                           "the overlocked edge.", section="Finish", stitch="topstitch",
                           data={"handles": "down"})]
        else:
            out.append(ST.hem("Hem the top edge", [("panel", "top")], hem,
                              f"Fold the top edge 1 cm, then {ST.cm(hem - 10)} to the wrong side. Slip the handle "
                              "ends under the fold at the marks, the handles hanging down (not twisted), and sew "
                              "close to the lower fold.", section="Finish", stitch="topstitch",
                              data={"handles": "down"}))
        out.append(ST.topstitch("Secure the handles", [("panel", "top")], 3.0,
                                "Fold the handles up and topstitch close to the top edge, catching them.",
                                section="Finish", hint=BOX_X_HINT, data={"handles": "up"}))
    out.append(ST.done("Press the bag; press the boxed corners into shape."))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
