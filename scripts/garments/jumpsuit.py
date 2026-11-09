"""Jumpsuit and boiler suit: the T-shirt block as a bodice (with blousing at the waist) joined at the
waist seam to the pants block. The front opens to the waist with buttons or with a zip that runs into
the front crotch seam; elastic in the back waist seam allowance, optional tie belt.

Styles
- `jumpsuit` (default): short sleeves, bias-bound neckline (or a collar), buttons, side pockets, belt
- `boiler`: boiler suit: long sleeves, shirt collar, zip, chest pocket, side and back pockets
`length`: long, 7/8 or short (playsuit). Woven (default) or a stable knit.
"""
from __future__ import annotations

from pattern import Pattern, rect_piece

from . import _parts as PT
from . import pants_basic as PB
from . import shirt as SH
from . import tshirt_basic as T
from ._common import clamp, is_adult

DEFAULTS = dict(style="jumpsuit", fabric="woven", stretch=None, fit="normal", length="long", sleeve_length=None,
                closure=None, collar=None, pockets=None, belt=None, chest_pocket=None, sa=10.0, hem_sa=25.0)
STYLE_DEFAULTS = {"jumpsuit": dict(sleeve_length="short", closure="buttons", collar="none", belt=True,
                                   chest_pocket=False, pockets=["side"]),
                  "boiler": dict(sleeve_length="long", closure="zip", collar="shirt", belt=False, chest_pocket=True,
                                 pockets=["side", "back_patch"])}
FINISHED_LABELS = dict(T.FINISHED_LABELS, waist_seam=("Waist seam", "width"), torso=("Neck point to crotch", "length"),
                       **{k: v for k, v in PB.FINISHED_LABELS.items() if k in ("inseam", "hem_circ", "hip")})
FIT_CHECK = "can you sit and bend forward without the crotch pulling up, and does the waist seam sit at your waist?"
SP = "Pants: "


def _resolve(options):
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["style"] not in STYLE_DEFAULTS:
        raise ValueError("jumpsuit style must be jumpsuit or boiler")
    for k, v in STYLE_DEFAULTS[o["style"]].items():
        if o.get(k) is None:
            o[k] = v
    if o["closure"] not in ("buttons", "zip"):
        raise ValueError("closure must be buttons or zip")
    if o["collar"] not in ("none", "stand", "shirt"):
        raise ValueError("collar must be none, stand or shirt")
    return o


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = _resolve(options)
    m = measures
    sa = o["sa"]
    adult = is_adult(m)
    blouse = 30.0 if adult else 20.0
    top = {k: o[k] for k in ("fit", "fabric", "stretch", "sleeve_length", "sa", "construction", "machines",
                             "notch_style") if k in o and o[k] is not None}
    top.update(sleeve_style="set_in", neckline="round", sleeve_cuffs=False, hem_band=False, _auto_neck=99,
               body_length=m["back_length"] + blouse, hem_total=m["hip"] * 1.06, hem_sa=o["hem_sa"] * 0.6,
               neck_finish="bias" if o["collar"] == "none" else "band")
    pat = T.draft(m, top, _garment="jumpsuit")
    pat.checks = [c for c in pat.checks if "over the head" not in c["name"] and c["name"] != "Body length plausible"]
    pat.notes = [n for n in pat.notes if "Neckline enlarged" not in n]
    if o["collar"] != "none":
        pat.pieces = [p for p in pat.pieces if p.key != "neckband"]
        pat.seams = [s for s in pat.seams if not any(k == "neckband" for k, _, _ in s["b"])]
    f, b = pat.piece("front"), pat.piece("back")
    for pc in (f, b):
        h = pc.edge("hem")
        h.sa, h.turned, h.label = sa, False, "Waist seam"
    pat.corners = [c for c in pat.corners if "hem" not in (c.get("a"), c.get("b")) or c.get("piece") == "sleeve"]
    hem_y = float(f.edge("hem").pts[:, 1].mean())
    ext = 0.0
    if o["closure"] == "buttons":
        ext = PT.button_size(m)
        PT.button_stand(f, ext)
        PT.rename_edge_refs(pat, "front", "center", "front_edge")
    else:
        c = f.edge("center")
        c.fold, c.sa, c.label = False, 15.0, "Centre front (zip)"
        f.cut_count, f.mirror = 2, True
    if o["collar"] != "none":
        SH.add_collar(pat, o["collar"], m, sa, ext)
    elif ext:                            # the button stand lengthens the neckline: stretch the binding
        nb = pat.piece("neckband")
        k = 2 * (f.edge("neckline").length + b.edge("neckline").length) / nb.edge("bottom").length
        for e in nb.edges:
            e.pts = e.pts * [k, 1.0]
        for mk in nb.marks:
            mk.pts = mk.pts * [k, 1.0]
    if o["chest_pocket"]:
        SH.chest_pocket(pat, m, sa)
    # pants
    popts = dict(style="trousers", fabric=o["fabric"], stretch=o.get("stretch"), fit="wide" if o["fit"] == "normal"
                 else o["fit"], length=o["length"], waistband="tunnel", cuffs=False, pockets=list(o["pockets"]),
                 sa=sa, hem_sa=o["hem_sa"])
    for k in ("machines", "construction", "notch_style"):
        if k in o:
            popts[k] = o[k]
    pants = PB.draft(m, popts)
    for pc in pants.pieces:
        for e in pc.edges:
            if e.name in ("waistband", "waist_outer"):
                e.sa, e.turned, e.label = sa, False, "Waist seam"
    pants.notes = [n for n in pants.notes if not n.startswith("Elastic")]
    pants.checks = [c for c in pants.checks if "aist" not in c["name"]]
    if o["closure"] == "zip":
        pants.piece("front").edge("crotch").label = "Crotch seam (zip at the top)"
    keymap = PT.merge_into(pat, pants, "pants_", SP, dy=hem_y,
                           part_of={"front": "front", "back": "back", "side_panel": "front"}, skip=("waistband",))
    top_b = [("pants_front", "waistband", 2), ("pants_back", "waistband", 2)]
    if pat.has("pants_side_panel"):
        top_b.append(("pants_side_panel", "waist_outer", 2))
    bod = 2 * (f.edge("hem").length + b.edge("hem").length) - 2 * ext
    pt = sum(pat.piece(k).edge(e).length * n for k, e, n in top_b)
    pat.seams.append(dict(name="Waist seam bodice ↔ pants", a=[("front", "hem", 2), ("back", "hem", 2)], b=top_b,
                          type="ratio", lo=0.85, hi=1.2, note="the back elastic gathers the difference"))
    el = m["waist"] * 0.5 * 0.85
    ew = 20.0 if adult else 15.0
    pat.notes.append(f"Elastic for the back waist: {ew:.0f} mm wide, {el / 10:.0f} cm (side seam to side seam)")
    pat.checks.append(dict(name="Waist seam goes over the hips", kind="min", value=min(bod, pt), target=m["hip"] * 1.02,
                           note="the jumpsuit is stepped into: the waist seam must pass the hips"))
    torso = -hem_y + pat.piece("pants_front").edge("crotch").length
    if o["closure"] == "zip":
        zl = -hem_y - F_neck(pat) + 0.35 * pat.piece("pants_front").edge("crotch").length
        pat.notes.append(f"Zip: {zl / 10:.0f} cm (closed end; front neck to below the waist)")
        pat.options["_zip"] = zl
    else:
        SH.add_buttons(pat, m, None, y_bot=hem_y + 35.0)
    if o["belt"]:
        bl = clamp(m["waist"] * 1.0 + 900, 900, 1900)
        bw = 40.0 if adult else 30.0
        belt = rect_piece("belt", "Tie belt", 2 * bw, bl / 2, sa=sa, cut_count=2, mirror=False,
                          labels=("Belt end", "Belt edge", "Belt end (centre back seam)", "Belt edge"))
        pat.pieces.append(belt)
        pat.seams.append(dict(name="Tie belt", a=[("belt", "right", 1)], b=[("belt", "left", 1)], type="equal"))
        pat.notes.append("Belt loops: 2 thread loops or fabric loops at the side seams, on the waist seam")
    pat.notes.append("Interfacing: light iron-on for the " + ("button stands" if ext else "zip edges")
                     + (" and the collar" if o["collar"] != "none" else ""))
    pat.options.update({k: o[k] for k in ("style", "closure", "collar", "belt", "chest_pocket", "length")})
    pat.options.update(_pants_opts=pants.options, _pants_keys=keymap, _ext=ext, _elastic=el)
    pat.title = {"jumpsuit": "Jumpsuit" if o["length"] != "short" else "Playsuit", "boiler": "Boiler suit"}[o["style"]]
    fin = {k: v for k, v in pat.finished.items() if k in FINISHED_LABELS and k != "length"}
    fin.update({k: v for k, v in pants.finished.items() if k in ("inseam", "hem_circ", "hip")})
    fin.update(waist_seam=bod, torso=torso)
    pat.finished = fin
    return pat


def F_neck(pat) -> float:
    """Front neck depth below the neck point (y of the front neckline at centre front)."""
    ne = pat.piece("front").edge("neckline").pts
    return -float(ne[:, 1].min())


def finished_measures(pat):
    return pat.finished


def assembly(pat):
    import steps as ST
    o = pat.options
    sa = ST.cm(pat.piece("front").edge("side").sa)
    pants = PT.SubView(pat, o["_pants_keys"], o["_pants_opts"], "pants_basic", SP)
    p_steps = PB.assembly(pants)
    p_steps = [s for s in p_steps if s.section not in ("Waistband",) and s.title not in
               ("Pre-wash the fabric", "Cut out all pieces", "Snip the notches", "Set up the machine",
                "Final pressing")]
    p_steps = PT.remap_steps(p_steps, o["_pants_keys"], SP)
    for s in p_steps:
        if s.title == "Sew the crotch seam" and o.get("closure") == "zip":
            s.text = s.text.replace("from the front top edge", "from the zip notch on the front")
    out = []
    if o.get("closure") == "buttons":
        fs = SH.front_steps(pat, sec="Bodice")
        fs[0].text = ("Iron light interfacing onto a strip along the front edges (button stand)"
                      + (" and onto the outer collar pieces." if o.get("collar") != "none" else "."))
        out += fs
    else:
        out.append(ST.icon("Interface the zip edges", "interfacing",
                           "Iron a 2 cm strip of light interfacing along the centre front edges of the bodice and "
                           "the top of the front crotch seam.", section="Prepare"))
        if pat.has("pocket"):
            out += SH.front_steps(pat, sec="Bodice")[1:-1]
    body = T.assembly(pat, hem=False, neck=o.get("collar") == "none", open_bands=True, done=False)
    for st in body:
        out.append(st)
        if st.title == "Sew the shoulder seams" and o.get("collar") != "none":
            out += SH.collar_steps(pat, sec="Collar")
    out += p_steps
    out.append(ST.seam("Sew bodice and pants together", ["Waist seam"],
                       "Slip the bodice into the pants right sides together, waist edges level: side seams, centre "
                       "back and the front edges matching. Pin, easing in any extra width at the back. Sew with "
                       f"{sa} seam allowance and press the allowances up towards the bodice.", section="Waist"))
    out.append(ST.icon("Sew in the back elastic", "elastic_on",
                       f"Pin the elastic ({o.get('_elastic', 0) / 10:.0f} cm) onto the waist seam allowance from "
                       "side seam to side seam and sew it on with a zigzag, stretching it. Stitch the ends down "
                       "firmly at the side seams.", stitch="elastic", section="Waist", data={"hands": "stretch"}))
    if o.get("closure") == "zip":
        out.append(ST.icon("Sew in the zip", "zip",
                           "Press the centre front allowances under. Pin the zip under the edges from the neckline "
                           "down to the end of the crotch seam opening, teeth centred, and topstitch it on with the "
                           "zipper foot; fold the top tape ends in under the neck finish.", section="Front"))
    if pat.has("belt"):
        out.append(ST.seam("Sew the tie belt", ["Tie belt"],
                           "Join the two belt halves at the short ends (centre back). Fold the belt lengthwise right "
                           f"sides together and sew the long edge and the ends with {sa} seam allowance, leaving a "
                           "gap; turn, press and close the gap.", section="Belt"))
    if o.get("closure") == "buttons":
        n = o.get("_buttons", 5)
        out.append(ST.icon("Sew buttonholes and buttons", "button",
                           f"Sew {n} vertical buttonholes on the marks of the right front and the buttons on the "
                           "left front.", section="Finish"))
    out.append(ST.done())
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)

