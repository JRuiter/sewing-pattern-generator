"""Swim trunks: the pants block at shorts length in quick-dry fabric, elastic waistband with a
drawcord through two eyelets, side pockets with mesh bags and a mesh brief liner sewn into the
waistband seam. `liner=False` leaves the liner out; `length` short (default) or knee."""
from __future__ import annotations

import geometry as G
from pattern import Mark, Pattern

from . import pants_basic as PB
from . import underwear as U

DEFAULTS = dict(fabric="swim_woven", stretch=None, fit="normal", length="short", liner=True, pockets=None,
                sa=10.0, hem_sa=20.0)
FINISHED_LABELS = dict(PB.FINISHED_LABELS)
FIT_CHECK = "do the trunks stay up with the drawcord loose, and does the liner sit close without cutting in?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["length"] not in ("short", "knee"):
        raise ValueError("swim trunks length must be short or knee")
    m = measures
    popts = {k: v for k, v in o.items() if k not in ("liner",)}
    popts.update(style="trousers", waistband="casing", cuffs=False, pocket_bag_fabric="mesh")
    if popts.get("pockets") is None:
        popts["pockets"] = ["side"]
    pat = PB.draft(m, popts)
    pat.garment = "swim_trunks"
    pat.title = "Swim trunks"
    band = pat.piece("waistband")
    h = max(float(p[1]) for e in band.edges for p in e.pts)
    for x in (18.0,):
        band.marks.append(Mark(G.line(G.P(x, h * 0.75 - 3), G.P(x, h * 0.75 + 3)), "mark", "Eyelet (drawcord)"))
    pat.notes.append(f"Drawcord: {(m['waist'] + 700) / 10:.0f} cm flat cord; 2 eyelets 8 mm (or 2 buttonholes)")
    if o["liner"]:
        lin = U.draft(m, dict(style="briefs", fabric="jersey", sa=o["sa"], rise="mid"))
        ren = {"front": "liner_front", "back": "liner_back", "gusset": "liner_gusset"}
        for pc in lin.pieces:
            pc.key = ren[pc.key]
            pc.name = "Liner " + pc.name.lower()
            pc.fabric = "Mesh"
            pc.info = []
            if pc.key == "liner_gusset":
                pc.cut_count = 1
            for e in pc.edges:
                if e.name == "waist":
                    e.label, e.turned = "Top edge (into the waistband seam)", False
        for s in lin.seams:
            s["name"] = "Liner " + s["name"].lower()
            for side in ("a", "b"):
                s[side] = [(ren[k], e, n) for k, e, n in s[side]]
        for c in lin.corners:
            c["piece"] = ren[c["piece"]]
            c["name"] = "Liner: " + c["name"]
        pat.pieces += lin.pieces
        pat.seams += lin.seams
        pat.corners += lin.corners
        pat.notes.append(f"Liner: swim mesh; leg elastic 2 × {lin.options['_leg_elastic'] / 10:.0f} cm, 6–8 mm")
        pat.options["_liner_leg"] = lin.options["_leg_elastic"]
    pat.options.update(liner=o["liner"])
    return pat


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    sa = ST.cm(pat.piece("front").edge("side").sa)
    base = PB.assembly(pat)
    done = base.pop()
    out = []
    liner = []
    if pat.has("liner_front"):
        liner = [
            ST.seam("Liner: sew the gusset to the front", ["Liner gusset ↔ front"],
                    f"Sew the mesh gusset to the liner front with {sa} seam allowance.", section="Liner"),
            ST.seam("Liner: sew the gusset to the back", ["Liner gusset ↔ back"],
                    "Sew the other end of the gusset to the liner back.", section="Liner"),
            ST.seam("Liner: sew the side seams", ["Liner side seams"],
                    "Sew the side seams of the liner.", section="Liner"),
            ST.icon("Liner: leg elastic", "elastic_on",
                    "Sew the leg elastic onto the wrong side of the liner leg openings with a zigzag, stretching it "
                    "evenly; turn it in and topstitch.", section="Liner", repeat=2),
            ST.icon("Baste the liner in", "needle",
                    "Put the liner into the trunks, wrong side of the liner to wrong side of the trunks, side seams "
                    "and centres matching, and baste the top edges together; ease the trunks onto the liner.",
                    stitch="baste", section="Liner")]
    eyelet = ST.icon("Set the eyelets", "eyelet",
                     "Interface the eyelet spots on the waistband (outer half, either side of centre front) and set "
                     "two eyelets 8 mm, or sew two vertical buttonholes.", section="Waistband")
    for st in base:
        if st.title.startswith("Close the waistband") or (st.section == "Waistband" and not liner and eyelet
                                                         and st.title.startswith("Sew the waistband")):
            out += liner + [eyelet]
            liner, eyelet = [], None
        if st.title == "Thread the elastic":
            st.text = ("Thread the elastic with a safety pin, overlap the ends 2 cm and sew them together. Then "
                       "thread the drawcord in through one eyelet, round the casing on top of the elastic and out "
                       "through the other; knot its ends.")
        out.append(st)
    if eyelet:
        out.append(eyelet)
    out += liner
    out.append(done)
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
