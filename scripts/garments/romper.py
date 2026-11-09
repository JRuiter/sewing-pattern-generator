"""Baby romper (sizes 50–92, knit): a T-shirt bodice joined at the waist seam to the legs, with a snap
opening along both inner legs and across the crotch (ankle to ankle) for nappy changes. Leg ends with
rib cuffs or, with `feet=True`, closed with a sole (footed sleeper). Long or short sleeves."""
from __future__ import annotations

import numpy as np

import geometry as G
from pattern import Edge, Mark, Pattern, Piece

from . import _parts as PT
from . import pants_basic as PB
from . import tshirt_basic as T
from ._common import clamp

DEFAULTS = dict(fabric="jersey", stretch=None, sleeve_length="long", feet=False, sa=7.5, hem_sa=15.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, torso=("Neck point to crotch", "length"),
                       inseam=("Inseam", "length"), sole=("Sole length", "length"))
FIT_CHECK = "can the baby kick and bend the knees freely, and do the snaps close without pulling over the nappy?"
SP = "Legs: "


def _snap_marks(pc: Piece, edge: str, step: float, inset: float = 9.0, skip_end: float = 0.0) -> int:
    """Snap marks along an edge, `inset` mm inside the piece; returns how many."""
    pts = np.asarray(pc.edge(edge).pts, float)
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(pts, axis=0).T))]
    total = seg[-1]
    n = max(2, int((total - skip_end - 20) // step) + 1)
    cen = pc.seam_ring().mean(axis=0)
    for s in np.linspace(10, total - 10 - skip_end, n):
        p = np.array([np.interp(s, seg, pts[:, 0]), np.interp(s, seg, pts[:, 1])])
        d = cen - p
        p = p + inset * d / max(np.hypot(*d), 1e-9)
        pc.marks.append(Mark(G.line(p, p + G.P(0, 1.0)), "mark", "Snap"))
    return n


def _sole(m: dict, sa: float) -> Piece:
    fl = clamp(0.14 * m["height"] + 10, 75, 150)
    fw = 0.42 * fl
    t = np.linspace(0, np.pi, 40)
    # toe a little wider than the heel
    right = np.c_[fw / 2 * np.sin(t) * (1 + 0.12 * np.cos(t)), -fl / 2 * np.cos(t)]
    left = np.c_[-right[:, 0], right[:, 1]][::-1]
    pc = Piece("sole", "Sole", [Edge("outer", right, sa, label="Sole edge"),
                                Edge("inner", left, sa, label="Sole edge")],
               cut_count=2, mirror=False, grain=(G.P(0, -fl * 0.3), G.P(0, fl * 0.3)))
    pc.notches = []
    return pc


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    if m["height"] > 1000:
        raise ValueError("the romper is drafted for babies and toddlers up to size 92")
    sa = o["sa"]
    common = {k: o[k] for k in ("machines", "construction", "notch_style") if k in o}
    top = dict(common, fit="normal", fabric=o["fabric"], stretch=o.get("stretch"), sleeve_length=o["sleeve_length"],
               sleeve_cuffs=o["sleeve_length"] == "long", hem_band=False, sa=sa, hem_sa=o["hem_sa"],
               body_length=m["back_length"] + 35)
    pat = T.draft(m, top, _garment="romper")
    f, b = pat.piece("front"), pat.piece("back")
    for pc in (f, b):
        h = pc.edge("hem")
        h.sa, h.turned, h.label = sa, False, "Waist seam"
    pat.corners = [c for c in pat.corners if "hem" not in (c.get("a"), c.get("b")) or c.get("piece") == "sleeve"]
    pat.checks = [c for c in pat.checks if c["name"] != "Body length plausible"]
    hem_y = float(f.edge("hem").pts[:, 1].mean())
    sole = _sole(m, sa) if o["feet"] else None
    popts = dict(common, style="jogger", fit="wide", fabric=o["fabric"], stretch=o.get("stretch"),
                 waistband="casing", cuffs=not o["feet"], pockets=[], length="long", sa=sa, hem_sa=o["hem_sa"])
    if sole is not None:
        popts["opening_total"] = sole.edge("outer").length + sole.edge("inner").length
        popts["inseam_total"] = m["inseam"] * 0.98
    pants = PB.draft(m, popts)
    for pc in pants.pieces:
        for e in pc.edges:
            if e.name == "waistband":
                e.sa, e.turned, e.label = sa, False, "Waist seam"
            if e.name == "inseam":
                e.sa, e.turned, e.label = 15.0, True, "Inseam (snap facing, turned)"
            if e.name == "hem" and sole is not None:
                e.sa, e.turned, e.label = sa, False, "Foot seam (sole)"
    pants.seams = [s for s in pants.seams if not s["name"].startswith("Inseam")]
    pants.notes = [n for n in pants.notes if not n.startswith("Elastic")]
    pants.checks = [c for c in pants.checks if "aist" not in c["name"]]
    pants.corners = [c for c in pants.corners if "inseam" not in (c.get("a"), c.get("b"))]
    keymap = PT.merge_into(pat, pants, "legs_", SP, dy=hem_y, part_of={"front": "front", "back": "back"},
                           skip=("waistband",))
    lf, lb = pat.piece("legs_front"), pat.piece("legs_back")
    n = _snap_marks(lf, "inseam", 45.0) + _snap_marks(lb, "inseam", 45.0)
    if sole is not None:
        pat.pieces.append(sole)
        pat.seams.append(dict(name="Sole ↔ leg end", a=[("legs_front", "hem", 1), ("legs_back", "hem", 1)],
                              b=[("sole", "outer", 1), ("sole", "inner", 1)], type="ease", lo=-6, hi=6,
                              note="toe at the front leg, heel at the back leg"))
        pat.notes.append("Soles: non-slip sole fabric or a double layer of the main fabric")
    pat.seams.append(dict(name="Waist seam bodice ↔ legs", a=[("front", "hem", 2), ("back", "hem", 2)],
                          b=[("legs_front", "waistband", 2), ("legs_back", "waistband", 2)], type="ratio", lo=0.85,
                          hi=1.18, note="ease the wider part in"))
    pat.notes.append(f"Snaps: {n} snaps (plastic or jersey snaps) along the inner legs, back over front")
    pat.notes.append("Interfacing: a strip of light iron-on interfacing in the snap facings")
    pat.options.update(feet=o["feet"], _pants_opts=pants.options, _pants_keys=keymap, _snaps=n)
    pat.title = "Footed romper" if o["feet"] else "Baby romper"
    fin = {k: v for k, v in pat.finished.items() if k in FINISHED_LABELS and k != "length"}
    fin.update(torso=-hem_y + lf.edge("crotch").length, inseam=lf.edge("inseam").length)
    if sole is not None:
        fin["sole"] = float(np.ptp(sole.seam_ring()[:, 1]))
    pat.finished = fin
    return pat


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    body = T.assembly(pat, hem=False, done=False)
    legs = [
        ST.seam("Sew the front crotch seam", [SP + "Front crotch seam"],
                f"Lay the two front legs right sides together and sew the centre front seam with {sa} seam "
                "allowance, from the top edge down to the crotch point.", section="Legs"),
        ST.seam("Sew the back crotch seam", [SP + "Back crotch seam"],
                "Sew the two back legs together at the centre back the same way.", section="Legs"),
        ST.seam("Sew the leg side seams", [SP + "Side seam"],
                f"Lay front and back legs right sides together and sew the outer leg seams with {sa} seam "
                "allowance. The inner legs stay open.", section="Legs", repeat=2)]
    if pat.has("legs_leg_cuff"):
        legs.append(ST.seam("Sew the leg cuffs on", [SP + "Leg cuff"],
                            "Fold each cuff lengthwise wrong sides together and sew it flat onto the leg end, "
                            "stretching it slightly; its ends stop at the inner leg edges.", section="Legs",
                            repeat=2))
    out = body + legs + [
        ST.seam("Sew bodice and legs together", ["Waist seam"],
                "Lay the bodice and the legs right sides together at the waist, side seams and centres matching, "
                f"and sew with {sa} seam allowance. Press the allowance towards the bodice.", section="Waist"),
        ST.hem("Fold the snap facings", [("legs_front", "inseam"), ("legs_back", "inseam")], 15.0,
               "Iron a strip of interfacing onto the inner leg edges, fold them 1.5 cm to the wrong side and stitch "
               "them down; fold the cuff ends in with them.", section="Snaps", repeat=2)]
    if pat.has("sole"):
        out.append(ST.seam("Sew in the soles", ["Sole"],
                           "Snap the inner leg closed at the foot. Pin the sole right sides together into the leg "
                           "end, toe to the front leg, heel to the back leg, and sew it in with "
                           f"{sa} seam allowance.", section="Feet", repeat=2))
    out += [ST.icon("Set the snaps", "snap", f"Set {o.get('_snaps', 12)} snaps on the marks: the sockets on the back "
                    "legs, the caps on the front legs (the back overlaps the front).", section="Snaps"),
            ST.done()]
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
