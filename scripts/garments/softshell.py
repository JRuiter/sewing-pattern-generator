"""Softshell / outdoor jacket: the zip-up hoodie block in softshell (wide fit, room for layers),
hood with a drawcord casing, separating zip with an inner zip guard, two zip pockets, sleeve
hems with adjustable Velcro tabs and a hem casing with a drawcord and cord stoppers."""
from __future__ import annotations

import geometry as G
from pattern import Pattern, rect_piece

from . import _parts as PT
from . import hoodie as H
from ._common import clamp, is_adult

DEFAULTS = dict(fit="wide", fabric="softshell", stretch=None, hood=True, pockets=True, cuff_tabs=True,
                hem_drawcord=True, sa=10.0, hem_sa=25.0)
FINISHED_LABELS = dict(H.FINISHED_LABELS)
FIT_CHECK = "does it close over a fleece, can you raise your arms without the hem riding up, and does the hood " \
            "turn with your head?"


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    m = measures
    sa = o["sa"]
    hopts = {k: v for k, v in o.items() if k not in ("pockets", "cuff_tabs", "hem_drawcord")}
    hopts.update(front="zip", kangaroo=False, hem_band=False, sleeve_cuffs=False, sleeve_length="long",
                 zip_guard=True)
    pat = H.draft(m, hopts)
    pat.garment = "softshell"
    f = pat.piece("front")
    F = pat.options["_F"]
    hem = f.edge("hem")
    if o["hem_drawcord"]:
        for k in ("front", "back"):
            e = pat.piece(k).edge("hem")
            e.sa, e.turned, e.label = 30.0, True, "Hem casing (drawcord)"
        hem_c = 2 * (f.edge("hem").length + pat.piece("back").edge("hem").length)
        pat.notes.append(f"Drawcord: {(hem_c + 300) / 10:.0f} cm for the hem"
                         + (f" and {(pat.piece('hood').edge('front_edge').length * 2 + 300) / 10:.0f} cm for "
                            "the hood" if pat.has("hood") else "") + ", 2–4 cord stoppers, 4 small eyelets")
    if o["pockets"]:
        pw = clamp(0.16 * m["chest"], 120, 180) if is_adult(m) else clamp(0.2 * m["chest"], 110, 150)
        hem_y = float(hem.pts[0, 1])
        c = G.P(F["q"] * 0.55, hem_y + 0.18 * (-hem_y) + 40)
        pcs, sms = PT.welt_pocket(f, "jetted", c, pw, sa, angle=75.0)
        for p in pcs:
            p.name = p.name.replace("Pocket lips", "Pocket zip facing")
        f.marks[-1].label = "Zip pocket opening"
        pat.pieces += pcs
        pat.seams += sms
        pat.notes.append(f"Pocket zips: 2 × {pw / 10:.0f} cm (not separating)")
    if o["cuff_tabs"]:
        tw = 25.0 if is_adult(m) else 20.0
        tab = rect_piece("cuff_tab", "Sleeve tab", 2 * tw, clamp(0.05 * m["height"], 60, 100), sa=sa, cut_count=2,
                         labels=("Tab end (into the seam)", "Tab edge", "Tab end", "Tab edge"))
        tab.info.append("fold lengthwise; Velcro on the tab and on the sleeve")
        pat.pieces.append(tab)
        pat.seams.append(dict(name="Sleeve tabs", a=[("cuff_tab", "right", 1)], b=[("cuff_tab", "left", 1)],
                              type="equal"))
        pat.notes.append("Velcro: 2 × 5 cm (tabs) and 2 × 8 cm (sleeves), 2 cm wide")
    pat.title = "Softshell jacket"
    pat.options.update(pockets=o["pockets"], cuff_tabs=o["cuff_tabs"], hem_drawcord=o["hem_drawcord"])
    return pat


def finished_measures(pat):
    return H.finished_measures(pat)


def assembly(pat):
    import steps as ST
    o = pat.options
    out = []
    if pat.has("pocket_bag"):
        out += [
            ST.icon("Interface the pocket openings", "interfacing",
                    "Iron a strip of interfacing behind each zip pocket marking.", section="Pockets"),
            ST.icon("Sew the pocket zips in", "zip",
                    "Lay the facing right sides together over the marking and sew a narrow rectangle round the "
                    "opening line. Cut in the middle and into the corners, turn the facing through and press. "
                    "Lay the zip behind the opening and topstitch round it close to the edge.", section="Pockets",
                    repeat=2),
            ST.seam("Close the pocket bags", ["Pocket bag round"],
                    "Sew the pocket bag pieces onto the zip tapes and together round the edges.", section="Pockets",
                    repeat=2)]
    if pat.has("cuff_tab"):
        out += [ST.seam("Sew the sleeve tabs", ["Sleeve tabs"],
                        "Fold each tab lengthwise right sides together, sew the long edge and one end, turn and "
                        "topstitch. Sew the soft Velcro onto the tab.", section="Sleeves", repeat=2),
                ST.icon("Sew the Velcro onto the sleeves", "velcro",
                        "Sew the hook Velcro onto the right side of the sleeve hem, at the back. Baste the tab into "
                        "the sleeve seam at the hem, pointing towards the front.", section="Sleeves", repeat=2)]
    steps = H.assembly(pat)
    done = steps.pop()
    out += steps
    if o.get("hem_drawcord"):
        out += [ST.icon("Set the eyelets", "needle",
                        "Set two small eyelets (or sew buttonholes) on the inside of the hem casing near the zip and "
                        "near the hood edge ends.", section="Drawcord"),
                ST.icon("Thread the drawcords", "elastic", "Thread the drawcords through the hem casing and the "
                        "hood casing with a safety pin; put on the cord stoppers.", section="Drawcord",
                        data={"label": "drawcord, with a safety pin"})]
    out.append(done)
    return out


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
