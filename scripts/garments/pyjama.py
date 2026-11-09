"""Pyjama set: a top and pants ordered together, with one cutting layout and one booklet. Sleepwear
ease: the top in the wide fit, the pants wide with an elastic casing waist.

Options
- `top`: `tshirt` (default, knit pullover with neckband) or `shirt` (woven button shirt, collar
  optional, no cuffs)
- `length`: `long` (default) or `short` (shorty: short sleeves and shorts)
- `cuffs`: rib cuffs on the sleeves and legs (default for children up to 140 in knit)
"""
from __future__ import annotations

import ease as E
from pattern import Pattern

from . import _parts as PT
from . import pants_basic as PB
from . import shirt as SH
from . import tshirt_basic as T

DEFAULTS = dict(top="tshirt", fabric=None, stretch=None, length="long", cuffs=None, collar="none", sa=10.0,
                hem_sa=20.0)
FINISHED_LABELS = dict(T.FINISHED_LABELS, **{"pants_" + k: ("Pants: " + v[0], v[1])
                                              for k, v in PB.FINISHED_LABELS.items()})
FIT_CHECK = "is the top loose enough to sleep in, and does the pants waist stay up without pressing?"
SP = "Pants: "


def draft(measures: dict, options: dict | None = None) -> Pattern:
    o = dict(DEFAULTS)
    o.update({k: v for k, v in (options or {}).items() if v is not None})
    if o["top"] not in ("tshirt", "shirt") or o["length"] not in ("long", "short"):
        raise ValueError("pyjama top must be tshirt or shirt, length long or short")
    m = measures
    fabric = o["fabric"] or ("woven" if o["top"] == "shirt" else "jersey")
    knit = E.fabric_info(fabric, o.get("stretch"))[2]
    cuffs = o["cuffs"] if o["cuffs"] is not None else (knit and m["height"] <= 1400 and o["length"] == "long")
    short = o["length"] == "short"
    common = {k: o[k] for k in ("sa", "machines", "construction", "notch_style") if k in o}
    if o["top"] == "shirt":
        pat = SH.draft(m, dict(common, style="shirt", fit="wide", fabric=fabric, stretch=o.get("stretch"),
                               sleeve_length="short" if short else "long", collar=o["collar"], yoke=False,
                               pocket=True, cuffs=False, hem_sa=o["hem_sa"]))
    else:
        pat = T.draft(m, dict(common, fit="wide", fabric=fabric, stretch=o.get("stretch"),
                              sleeve_length="short" if short else "long", sleeve_cuffs=bool(cuffs) and not short,
                              hem_sa=o["hem_sa"]), _garment="pyjama")
    pat.garment = "pyjama"
    popts = dict(common, style="jogger", fit="wide", fabric=fabric, stretch=o.get("stretch"), waistband="casing",
                 cuffs=bool(cuffs) and not short, pockets=[], length="short" if short else "long",
                 hem_sa=o["hem_sa"])
    pants = PB.draft(m, popts)
    keymap = PT.merge_into(pat, pants, "pants_", SP)
    for k, v in pants.finished.items():
        pat.finished["pants_" + k] = v
    pat.options.update(top=o["top"], length=o["length"], cuffs=bool(cuffs), _pants_opts=pants.options,
                       _pants_keys=keymap, _top_garment="shirt" if o["top"] == "shirt" else "tshirt_basic")
    pat.title = "Shorty pyjamas" if short else "Pyjamas"
    return pat


def finished_measures(pat):
    return pat.finished


_PREP = ("Pre-wash the fabric", "Cut out all pieces", "Snip the notches", "Set up the machine", "Final pressing")


def assembly(pat):
    import steps as ST
    o = pat.options
    top = SH.assembly(pat) if o.get("_top_garment") == "shirt" else T.assembly(pat, done=False)
    top = [s for s in top if s.title != "Final pressing"]
    for s in top:
        s.section = "Top" + (": " + s.section if s.section else "")
    pants = PT.SubView(pat, o["_pants_keys"], o["_pants_opts"], "pants_basic", SP)
    ps = [s for s in PB.assembly(pants) if s.title not in _PREP]
    ps = PT.remap_steps(ps, o["_pants_keys"], SP)
    for s in ps:
        s.section = "Pants" + (": " + s.section if s.section else "")
    return top + ps + [ST.done()]


def sewing_steps(pat):
    import steps as ST
    return ST.as_texts(assembly(pat), pat.options)
