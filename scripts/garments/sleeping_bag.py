"""Baby sleeping bag and swaddle sack (sizes from the baby's length, 50–110), lined, with a zip.

Styles
- `sleeping_bag` (default): sleeveless bag on the T-shirt block, wide at the bottom so the legs can
  kick, a two-way zip in the centre front from the neck down, lined (bagged out at the neckline and
  armholes); warmth by `tog`
- `swaddle`: swaddle sack for newborns (50–68): a lined bag up to the armpits with two wrap wings that
  hold the arms against the body and close with Velcro; zip in the centre front

`tog`: 0.5 (summer, 24–27 °C: jersey + jersey lining), 1.0 (all year, 20–24 °C: + thin wadding) or
2.5 (winter, 16–20 °C: + thick wadding). Sleeping bags must not have a hood or a loose neckline: the
neckline is checked against the head (the head must not slip in).
"""
from __future__ import annotations

import geometry as G
from pattern import Edge, Pattern, Piece, rect_piece

from . import _parts as PT
from . import tshirt_basic as T
from ._common import clamp

DEFAULTS = dict(style="sleeping_bag", fabric="jersey", stretch=None, tog=1.0, sa=10.0, hem_sa=10.0)
FINISHED_LABELS = {"length": ("Bag length (shoulder to bottom)", "length"), "chest_circ": ("Chest", "width"),
                   "bottom": ("Bottom width (flat × 2)", "width"), "zip": ("Zip length", "length")}
FIT_CHECK = "is there a hand's width of room below the feet, and does the neckline sit close without the head " \
            "slipping in?"
TOG = {0.5: ("summer, 24–27 °C", "jersey lining, no wadding", None),
       1.0: ("all year, 20–24 °C", "jersey lining + thin wadding (about 80 g/m²)", "Wadding: thin (80 g/m²)"),
       2.5: ("winter, 16–20 °C", "jersey lining + thick wadding (150–200 g/m²)", "Wadding: thick (150–200 g/m²)")}


def _bag_length(m: dict, style: str) -> float:
    if style == "swaddle":
        return 0.62 * m["height"] + 80          # armpit to bottom + room
    return 0.76 * m["height"] + 100              # shoulder to bottom + a hand's width for the feet


def _wadding(pat, wad: str | None):
    if not wad:
        return
    for key in ("front", "back"):
        pc = pat.piece(key)
        w = Piece(key + "_wadding", pc.name + " wadding", [Edge(e.name, e.pts.copy(), 0.0, e.fold, e.label, False,
                                                                 raw=True) for e in pc.edges],
                  cut_count=pc.cut_count, mirror=pc.mirror, fabric=wad, grain=pc.grain)
        w.info.append("cut on the seam line, no allowance")
        pat.pieces.append(w)


def _sleeping_bag(m, o):
    sa = o["sa"]
    L = _bag_length(m, "sleeping_bag")
    top = {k: o[k] for k in ("fabric", "stretch", "machines", "construction", "notch_style") if k in o}
    top.update(fit="wide", sleeve_length="short", hem_band=False, sa=sa, hem_sa=sa, body_length=L,
               hem_total=max(m["chest"] * 2.1, m["hip"] * 2.0), _auto_neck=99)
    pat = T.draft(m, top, _garment="sleeping_bag")
    pat.pieces = [p for p in pat.pieces if p.key not in ("sleeve", "neckband")]
    pat.seams = [s for s in pat.seams if not any(k in ("sleeve", "neckband") for k, _, _ in s["a"] + s["b"])]
    pat.corners = [c for c in pat.corners if c.get("piece") != "sleeve" and "hem" not in (c.get("a"), c.get("b"))]
    pat.checks = [c for c in pat.checks if "leeve" not in c["name"] and "cap" not in c["name"].lower()
                  and "head" not in c["name"] and c["name"] != "Body length plausible"]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    f, b = pat.piece("front"), pat.piece("back")
    for pc in (f, b):
        pc.notches = [nt for nt in pc.notches if nt.edge != "armhole"]
        pc.edge("armhole").label = "Armhole (lined)"
        pc.edge("neckline").label = "Neckline (lined)"
        pc.edge("neckline").sa = sa * 0.7
        h = pc.edge("hem")
        h.sa, h.turned, h.label = sa, False, "Bottom seam"
    c = f.edge("center")
    c.fold, c.sa, c.label = False, 15.0, "Centre front (zip)"
    f.cut_count, f.mirror = 2, True
    pat.seams.append(dict(name="Bottom seam front ↔ back", a=[("front", "hem", 2)], b=[("back", "hem", 2)],
                          type="equal"))
    zl = clamp(0.75 * L, 250, 700)
    neck = 2 * (f.edge("neckline").length + pat.piece("back").edge("neckline").length)
    pat.checks.append(dict(name="Head cannot slip through the neckline", kind="range", value=neck,
                           lo=0.55 * m["head"], hi=0.85 * m["head"],
                           note="the zip opens the neckline for dressing; closed it stays smaller than the head"))
    pat.finished = dict(length=L, chest_circ=pat.finished.get("chest_circ", 0.0),
                        bottom=2 * (2 * f.edge("hem").length + 2 * b.edge("hem").length) / 2, zip=zl)
    return pat, zl


def _swaddle(m, o):
    sa = o["sa"]
    L = _bag_length(m, "swaddle")
    cw = m["chest"] * 1.25 / 4               # quarter: room for the legs to bend (hip-healthy)
    bw = max(m["chest"], m["hip"]) * 1.9 / 4
    r = 0.6 * bw
    y_b = -L

    def body(key, name, cut, fold_center):
        side = G.tangent_curve(G.P(cw, 0), (0, -1), G.P(bw, y_b + r), (0.05, -1), 0.4, 0.4)
        bot = G.join(G.quad(G.P(bw, y_b + r), G.P(bw, y_b), G.P(bw - r, y_b)), G.line(G.P(bw - r, y_b), G.P(0, y_b)))
        # counter-clockwise: centre (down), bottom (to the side), side (up), top (to the centre)
        edges = [Edge("center", G.line(G.P(0, 0), G.P(0, y_b)), 0.0 if fold_center else 15.0, fold_center,
                      "Centre back (fold)" if fold_center else "Centre front (zip)"),
                 Edge("hem", bot[::-1], sa, label="Bottom seam"),
                 Edge("side", side[::-1], sa, label="Side seam"),
                 Edge("top", G.line(G.P(cw, 0), G.P(0, 0)), sa, label="Top edge (lined)")]
        return Piece(key, name, edges, cut_count=cut, mirror=not fold_center,
                     grain=(G.P(cw * 0.5, -L * 0.2), G.P(cw * 0.5, -L * 0.7)))

    f = body("front", "Front", 2, False)
    b = body("back", "Back", 1, True)
    wl, wh = clamp(0.75 * m["chest"], 260, 420), clamp(0.55 * m["back_length"], 90, 150)
    wing = rect_piece("wing", "Wrap wing", wl, wh, sa=sa, cut_count=4,
                      labels=("Wing edge", "Wing end (Velcro)", "Wing edge", "Wing end (into the side seam)"))
    wing.info.append("2 outer + 2 lining")
    pat = Pattern("sleeping_bag", "", "", [f, b, wing], dict(m), {}, seams=[
        dict(name="Side seam front ↔ back", a=[("front", "side", 1)], b=[("back", "side", 1)], type="equal"),
        dict(name="Bottom seam front ↔ back", a=[("front", "hem", 2)], b=[("back", "hem", 2)], type="equal"),
        dict(name="Wings (outer ↔ lining)", a=[("wing", "bottom", 1), ("wing", "right", 1), ("wing", "top", 1)],
             b=[("wing", "bottom", 1), ("wing", "right", 1), ("wing", "top", 1)], type="equal")],
        corners=[dict(name="Top ↔ centre (front)", piece="front", a="top", b="center", target=90),
                 dict(name="Side ↔ top (front)", piece="front", a="side", b="top", target=90)])
    pat.checks.append(dict(name="Room for the legs (hip-healthy)", kind="min", value=4 * bw, target=1.7 * m["hip"],
                           note="the legs must be able to bend up and out (M position)"))
    pat.notes.append(f"Velcro: 2 × {wh * 0.7 / 10:.0f} cm (soft side on the inner wing)")
    zl = clamp(0.8 * L, 250, 600)
    pat.finished = dict(length=L, chest_circ=4 * cw, bottom=4 * bw, zip=zl)
    return pat, zl


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    if o["style"] not in ("sleeping_bag", "swaddle"):
        raise ValueError("style must be sleeping_bag or swaddle")
    tog = float(o["tog"])
    if tog not in TOG:
        raise ValueError("tog must be 0.5, 1.0 or 2.5")
    if m["height"] > 1100 or (o["style"] == "swaddle" and m["height"] > 700):
        raise ValueError("sleeping bags are drafted for 50–110 cm, swaddle sacks for 50–68 cm")
    pat, zl = _swaddle(m, o) if o["style"] == "swaddle" else _sleeping_bag(m, o)
    for key in ("front", "back"):
        pat.pieces.append(PT.lining_of(pat.piece(key), sa=o["sa"]))
        pat.pieces[-1].fabric = "Lining: jersey"
    _wadding(pat, TOG[tog][2])
    pat.seams.append(dict(name="Lining side seams", a=[("front_lining", "side", 1)], b=[("back_lining", "side", 1)],
                          type="equal"))
    pat.seams.append(dict(name="Lining bottom seam", a=[("front_lining", "hem", 2)], b=[("back_lining", "hem", 2)],
                          type="equal"))
    pat.notes.append(f"Zip: two-way, {zl / 10:.0f} cm (or the next longer one), with a zip garage at the top")
    when, layers, _w = TOG[tog]
    pat.notes.append(f"Warmth {tog:g} TOG: {when}; layers: outer fabric + {layers}")
    pat.notes.append("Safe sleep: no hood, no loose ties; the baby sleeps on the back; dress lightly underneath")
    o["tog"] = tog
    pat.options = dict(o, _zip=zl, **{k: v for k, v in pat.options.items() if k.startswith("_")})
    pat.title = "Swaddle sack" if o["style"] == "swaddle" else "Baby sleeping bag"
    return pat


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    swaddle = o.get("style") == "swaddle"
    out = []
    if pat.has("front_wadding"):
        out.append(ST.icon("Baste the wadding on", "needle",
                           "Lay each wadding piece onto the wrong side of its outer piece and baste or quilt them "
                           "together within the seam allowance: from now on they are one layer.",
                           stitch="baste", section="Prepare"))
    if swaddle:
        out += [ST.seam("Sew the wings", ["Wings"],
                        f"Lay each outer and lining wing right sides together and sew round with {sa} seam "
                        "allowance, leaving the end for the side seam open. Turn, press and sew the Velcro on: hook "
                        "side on the outer of the left wing, soft side on the lining of the right wing.",
                        section="Wings", repeat=2),
                ST.seam("Sew the side seams", ["Side seam"],
                        f"Sew front and back together at the sides with {sa} seam allowance, catching a wing in each "
                        "side seam at the top (pointing inwards).", section="Bag")]
    else:
        out += [ST.seam("Sew the shoulder seams", ["Shoulder seam"],
                        f"Sew the outer front and back together at the shoulders with {sa} seam allowance.",
                        section="Bag"),
                ST.seam("Sew the side seams", ["Side seam"],
                        f"Sew the outer side seams with {sa} seam allowance.", section="Bag")]
    out.append(ST.seam("Sew the bottom seam", ["Bottom seam"],
                       "Sew the bottom edges of front and back together; clip the curves.", section="Bag"))
    out += [ST.seam("Sew the lining", ["Lining side seams", "Lining bottom seam"],
                    "Sew the lining the same way" + ("" if swaddle else ", shoulders included") + ".",
                    section="Lining"),
            ST.icon("Sew in the zip", "zip",
                    "Sew the zip right sides together onto the centre front edges of the outer bag, the top stop "
                    "1.5 cm below the top edge. Lay the lining over it right sides together and sew the centre "
                    "front edges again through all layers.", section="Zip")]
    if swaddle:
        out.append(ST.icon("Close the top edge", "needle",
                           "Sew outer and lining together along the top edge, right sides together, folding the zip "
                           "tape ends in (zip garage). Turn the bag right side out through the zip and press.",
                           section="Finish"))
    else:
        out.append(ST.icon("Sew the neckline and armholes", "needle",
                           "With outer and lining right sides together, sew round the neckline (folding the zip "
                           "tape ends in) and round both armholes, stopping 2 cm before the shoulder seams. Clip "
                           "the curves, pull the bag through the shoulders to the right side and close the "
                           "shoulder gaps by hand.", section="Finish"))
    out.append(ST.done("Press lightly (not on the wadding). Check that no thread ends or loose parts are left "
                       "inside."))
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)

