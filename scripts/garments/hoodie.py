"""Hoodie / sweatshirt: T-shirt block (sweat, wide, long sleeves with cuffs, hem band)
+ hood (two mirrored pieces) and an optional kangaroo pocket.
Without the hood you get a sweatshirt with a neckband.

`front="zip"` makes a zip-up jacket: the front is split at centre front (seam allowance for
a separating zip, no overlap), the kangaroo pocket becomes two side pockets, hem band and
neckband end at the zip, and an optional zip guard (facing strip) covers the zip inside."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece

from . import tshirt_basic as T

DEFAULTS = dict(fit="wide", fabric="sweat", hood=True, kangaroo=True, sleeve_style="set_in",
                sleeve_length="long", sleeve_cuffs=True, hem_band=True, hood_lining=False,
                front="closed", zip_guard=True, zip_sa=None)

# standard lengths of separating (jacket) zips in cm
ZIP_LENGTHS = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]

FINISHED_LABELS = dict(T.FINISHED_LABELS, hood_height=("Hood height", "length"),
                       zip_opening=("Front opening (zip)", "length"), zip_length=("Zip length", "length"))


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    hood = bool(o.pop("hood"))
    kang = bool(o.pop("kangaroo"))
    lining = bool(o.pop("hood_lining"))
    zip_front = o.pop("front") == "zip"
    zip_guard = bool(o.pop("zip_guard"))
    zip_sa = o.pop("zip_sa")
    if hood:
        o.setdefault("neck_extra", 8.0)
        o["neckline"] = "round"
    pat = T.draft(measures, o, _garment="hoodie")
    m = measures
    pat.title = "Hoodie" if hood else "Sweatshirt"
    pat.options.update(hood=hood, kangaroo=kang, hood_lining=lining, front="zip" if zip_front else "closed",
                       zip_guard=zip_guard and zip_front)
    sa = pat.options["sa"]
    front = pat.piece("front")
    if hood:
        # remove the neckband, add the hood
        pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
        pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
        pat.checks = [c for c in pat.checks if c["name"] != "Neckline fits over the head"]
        refs = [("front", "neckline", 1), ("back", "neckline", 1)]
        if pat.piece("sleeve").edges[-1].name == "neck":
            refs.append(("sleeve", "neck", 1))
        half_neck = sum(pat.piece(k).edge(e).length * n for k, e, n in refs)
        Hh = 0.58 * m["head"] + 25
        Wh = 0.44 * m["head"] + 15
        # neck edge: curved slightly down, length = half the neckline
        def neck_curve(bx):
            return G.cubic(G.P(0, 0), G.P(bx * 0.35, 0), G.P(bx * 0.7, -8), G.P(bx, 18))
        lo, hi = half_neck * 0.6, half_neck * 1.05
        for _ in range(50):
            bx = (lo + hi) / 2
            if G.length(neck_curve(bx)) < half_neck:
                lo = bx
            else:
                hi = bx
        neck = neck_curve((lo + hi) / 2)
        B0 = neck[-1]
        Tp = G.P(0, Hh)
        back = G.cubic(B0, B0 + np.array([max(Wh - B0[0], 10) * 0.9 + 15, Hh * 0.3]),
                       G.P(Wh * 0.95, Hh * 1.02), Tp)
        back = G.join(back)
        edges = [
            Edge("neck", neck, sa, label="Neck seam"),
            Edge("center", back, sa, label="Hood centre seam"),
            Edge("front_edge", G.line(Tp, G.P(0, 0)), 25.0, label="Front edge (casing/facing)", turned=True),
        ]
        hp = Piece("hood", "Hood", edges, cut_count=4 if lining else 2, mirror=True, fabric="Main fabric",
                   grain=(G.P(Wh * 0.4, Hh * 0.2), G.P(Wh * 0.4, Hh * 0.75)))
        hp.marks.append(Mark(G.line(G.P(12, Hh * 0.92), G.P(12, 8)), "fold", "Front edge fold line"))
        if lining:
            hp.info.append("2× main fabric + 2× lining (jersey)")
        pat.pieces.append(hp)
        pat.seams.append(dict(name="Hood ↔ neckline (each side)", a=refs, b=[("hood", "neck", 1)],
                              type="equal"))
        pat.seams.append(dict(name="Hood centre seam (left ↔ right)", a=[("hood", "center", 1)],
                              b=[("hood", "center", 1)], type="equal"))
        pat.corners.append(dict(name="Hood: front edge ↔ neck seam", piece="hood", a="front_edge", b="neck",
                                target=90))
        pat.checks.append(dict(name="Hood tall enough", kind="min", value=Hh + 0.0, target=0.55 * m["head"],
                               note="hood height ≥ 0.55 × head circumference"))
        pat.finished["hood_height"] = Hh
    if kang:
        F = pat.options["_F"]
        q = F["q"]
        hem_y = float(front.edge("hem").pts[0, 1])
        Wk, Hk = q * 0.62, min(0.36 * F["L"], 0.45 * (-hem_y - F["AD"]))
        op = Hk * 0.55
        pts = [G.P(0, 0), G.P(Wk, 0), G.P(Wk, Hk - op), G.P(Wk - op * 0.45, Hk), G.P(0, Hk)]
        edges = [
            Edge("bottom", G.line(pts[0], pts[1]), sa, label="Hem seam"),
            Edge("side", G.line(pts[1], pts[2]), sa, label="Side"),
            Edge("opening", G.line(pts[2], pts[3]), 15.0, label="Opening (hem it)"),
            Edge("top", G.line(pts[3], pts[4]), sa, label="Top edge (press under)"),
            Edge("center", G.line(pts[4], pts[0]), 0.0, True, "Centre (fold)"),
        ]
        kp = Piece("kangaroo_pocket", "Kangaroo pocket", edges, cut_count=1, mirror=False, fabric="Main fabric",
                   grain=(G.P(Wk * 0.35, Hk * 0.2), G.P(Wk * 0.35, Hk * 0.8)))
        if zip_front:
            # two side pockets: split at centre front
            ce = kp.edge("center")
            ce.fold, ce.sa, ce.label = False, sa, "Front edge (towards the zip)"
            kp.cut_count, kp.mirror, kp.name = 2, True, "Front pocket"
        pat.pieces.append(kp)
        y0 = hem_y
        front.marks.append(Mark(np.array([[0, y0 + Hk], [Wk - op * 0.45, y0 + Hk], [Wk, y0 + Hk - op],
                                          [Wk, y0]]), "placement", "Kangaroo pocket"))
    if zip_front:
        _zip_front(pat, sa if zip_sa is None else float(zip_sa), zip_guard, hood, m)
    return pat


def _zip_front(pat, zsa, guard, hood, m):
    """Split the front at centre front for a separating zip."""
    from pattern import rect_piece
    front = pat.piece("front")
    ce = front.edge("center")
    ce.fold, ce.sa, ce.label = False, zsa, "Centre front (zip)"
    front.cut_count, front.mirror = 2, True
    front.name = "Front (left and right)"
    hb_h = pat.options.get("_hem_band_h", 0.0) if pat.has("hem_band") else 0.0
    nb_h = 0.0
    if pat.has("hem_band"):
        hb = pat.piece("hem_band")
        hb.edge("right").label = "Front end (zip)"
        hb.info.append("ends at the zip: not sewn into a ring")
    if pat.has("neckband"):
        nb = pat.piece("neckband")
        nb.edge("right").label = nb.edge("left").label = "Front end (zip)"
        nb.info.append("from zip to zip: not sewn into a ring")
        nb_h = pat.options.get("_nb_h", 0.0)
    cf_len = ce.length + hb_h + nb_h
    fits = [z * 10.0 for z in ZIP_LENGTHS if z * 10.0 <= cf_len - 5.0]
    zip_len = fits[-1] if fits else ZIP_LENGTHS[0] * 10.0
    pat.options["_zip_len"] = zip_len
    pat.finished["zip_opening"] = cf_len
    pat.finished["zip_length"] = zip_len
    if guard:
        gw = 30.0 if m["height"] > 1650 else 25.0
        zg = rect_piece("zip_guard", "Zip guard", 2 * gw, cf_len, sa=pat.options["sa"], cut_count=1,
                        names=("bottom", "right", "top", "left"),
                        labels=("Bottom end", "Raw edges (into the zip seam)", "Top end", "Raw edges"))
        import geometry as G
        from pattern import Mark
        zg.marks.append(Mark(G.line(G.P(gw, 0), G.P(gw, cf_len)), "fold", "Fold line"))
        zg.info.append("left front only (covers the zip inside)")
        pat.pieces.append(zg)
    pat.seams.append(dict(name="Zip: left ↔ right front edge", a=[("front", "center", 1)],
                          b=[("front", "center", 1)], type="equal"))
    pat.checks.append(dict(name="Zip length fits the front opening", kind="range", value=zip_len,
                           lo=cf_len - 65.0, hi=cf_len,
                           note=f"front opening {cf_len / 10:.1f} cm, standard zip rounded down"))
    pat.notes.append(f"Separating (jacket) zip, {zip_len / 10:.0f} cm long (front opening "
                     f"{cf_len / 10:.1f} cm" + (" incl. hem band" if hb_h else "") + ").")
    if hood:
        pat.notes.append("The hood front edges end exactly at the zip (no overlap at centre front).")


def finished_measures(pat):
    return T.finished_measures(pat)


def sewing_steps(pat):
    o = pat.options
    steps = []
    zipped = o.get("front") == "zip"
    if o.get("kangaroo") and zipped:
        steps.append("**Front pockets:** press the openings under by 1.5 cm and topstitch, press the top edge "
                     "under by 1 cm. Place each pocket on its front at the marking, front edge on the centre "
                     "front edge, and stitch the top edge and side; bottom and front edge are caught in the "
                     "hem band and zip seams.")
    elif o.get("kangaroo"):
        steps.append("**Kangaroo pocket:** press the openings under by 1.5 cm and topstitch, press the top edge "
                     "under by 1 cm. Place the pocket on the front at the marking and stitch the top edge and sides; "
                     "the bottom edge is caught later with the hem band.")
    base = T.sewing_steps(pat)
    if o.get("hood"):
        base = [s for s in base if not s.startswith("**Neckband")]
        hood = ["**Hood:** place the hood pieces right sides together and sew the centre seam. Press the front "
                "edge to the inside along the fold line and topstitch (it can take a drawstring)" +
                ("; for a lined hood, sew the lining the same way and join it to the hood right sides together "
                 "along the front edge, then turn" if o.get("hood_lining") else "") + ".",
                "**Attach the hood:** pin the hood right sides together to the neckline (centre seam at centre "
                "back, front edges meet at centre front, overlap by 1 cm if needed) and sew. Finish the seam "
                "allowance with jersey binding."]
        base = base[:1] + hood + base[1:]
    if zipped:
        def open_band(x):
            if x.startswith("**Hem band"):
                return x.replace("sew into a ring, fold,", "leave the ends open, fold lengthwise,")
            if x.startswith("**Neckband"):
                return x.replace("sew it into a ring across the short ends and fold it", "fold it")
            if x.startswith("**Attach the hood"):
                return x.replace("front edges meet at centre front, overlap by 1 cm if needed",
                                 "front edges end exactly at the centre front edges")
            return x
        base = [open_band(x) for x in base]
        zip_step = (f"**Zip:** separate the {o['_zip_len'] / 10:.0f} cm zip. Pin each half right sides together "
                    "to a centre front edge, teeth towards the body, top stop just below the neck seam and "
                    "the bottom end flush with the hem band edge, and sew with a zipper foot. "
                    + ("Fold the zip guard lengthwise, lay it on the inside of the left front over the zip "
                       "tape and catch it in the same seam. " if o.get("zip_guard") else "")
                    + "Press the seam allowances away from the zip and topstitch 7 mm from the edge.")
        base = base[:-1] + [zip_step] + base[-1:]
    return steps + base
