"""Creative silhouettes: free design shapes on top of the practice-correct base block.

The garment modules draft a base block that follows common sewing practice. A *design*
(spec field ``design`` or option ``design``, CLI ``--design``) reshapes that block with
explicit, named features, e.g. a five-point starfish sweatshirt, balloon legs, bell
sleeves, a zigzag hem, a pointed elf hood or dinosaur spikes. Nothing here changes a
pattern unless the user asked for it.

A design is a dict (or the name of a preset, see :data:`PRESETS`)::

    {"name": "Starfish",
     "features": [
       {"zone": "side",   "bulge": {"at": 0.5, "cm": 3}},                 # rounder body
       {"zone": "sleeve", "profile": [[0.25, 3], [0.8, 0.5]]},             # arms taper to a point
       {"zone": "hem",    "shape": "points", "count": 2, "depth_cm": 7},  # two "legs"
       {"zone": "hood",   "peak": {"at": 0.72, "cm": 9}},                  # the top point
       {"zone": "hood",   "appendage": {"shape": "spike", "count": 5, "height_cm": 4}}]}

Zones are the seams and hems of the garment (:data:`ZONES`, ``python design.py zones``).
Every zone runs from ``t = 0`` (the attached end: underarm, waist, crotch, neck) to
``t = 1`` (the free end: hem, wrist, front edge). Values are cm per seam edge, outwards
(+) or inwards (−); on hems + means longer.

How a feature is applied (``apply``):

* the same offset profile is put on every edge of the zone, measured along the seam from
  the free end, so the two edges of a seam stay the same length and shape;
* an end that is sewn to something else (armhole, waistband, cuff, pocket) stays where it
  is with an unchanged angle; an end at a free hem moves, and the hem follows;
* hem shapes run across the whole unfolded panel, so a piece cut on the fold gets the
  mirrored half; a point or dip at the fold is marked as intended;
* appendages (spikes, ears, fins …) become pieces of their own that are sewn into the
  zone's seam, with notches for their positions.

Afterwards ``apply`` re-checks the result (rows in the validation report): every feature
is listed as an intended deviation from the base block, the freedom of movement (girth
along the zone against the body plus a minimum ease, openings for head, hand and foot),
the sewability (tip angles of points, inner corners, steepness, appendage sizes) and the
normal validation runs on the reshaped pieces (seam lengths, angles, seam allowances).
Options that a shape cannot have (a hem band on a pointed hem, cuffs on a bell sleeve)
are switched off before drafting (:func:`prepare`) and listed in :func:`describe`, which
writes the feature list the user confirms before the pattern is generated.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import sys
from typing import Any

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ease as E  # noqa: E402
import geometry as G  # noqa: E402
from pattern import Edge, Notch, Piece  # noqa: E402

# --------------------------------------------------------------------------- zones

# zone → seam edges (piece, edge, which end is the free end: "start" | "end" | None = both
# ends are attached) or hem edges ("hem": [(piece, edge)]), plus the girth ring for the
# freedom-of-movement check ((piece, multiplicity), body reference).
_TOP = {
    "side": dict(edges=[("front", "side", "start"), ("back", "side", "start")], label="Side seam",
                 ring=[("front", 2), ("back", 2)], body="torso"),
    "sleeve": dict(edges=[("sleeve", "seam_front", "start"), ("sleeve", "seam_back", "end")],
                   label="Sleeve seam", ring=[("sleeve", 1)], body="arm"),
    "hem": dict(hem=[("front", "hem"), ("back", "hem")], label="Hem", ring=[("front", 2), ("back", 2)],
                body="hip_pass"),
    "sleeve_hem": dict(hem=[("sleeve", "hem")], label="Sleeve hem", ring=[("sleeve", 1)], body="hand"),
}
ZONES: dict[str, dict[str, dict]] = {
    "tshirt_basic": _TOP,
    "hoodie": {**_TOP, "hood": dict(edges=[("hood", "center", "end")], label="Hood centre seam")},
    "dress": {**_TOP,
              "skirt_side": dict(edges=[("skirt_front", "side", "start"), ("skirt_back", "side", "start")],
                                 label="Skirt side seam", ring=[("skirt_front", 2), ("skirt_back", 2)],
                                 body="hip"),
              "hem": dict(hem=[("skirt_front", "hem"), ("skirt_back", "hem"), ("front", "hem"), ("back", "hem")],
                          label="Hem", ring=[("skirt_front", 2), ("skirt_back", 2)], body="stride")},
    "skirt": {"side": dict(edges=[("front", "side", "start"), ("back", "side", "start")], label="Side seam",
                           ring=[("front", 2), ("back", 2)], body="hip"),
              "hem": dict(hem=[("front", "hem"), ("back", "hem")], label="Hem", ring=[("front", 2), ("back", 2)],
                          body="stride")},
    "pants_basic": {"side": dict(edges=[("front", "side", "start"), ("back", "side", "start")],
                                 label="Side seam", ring=[("front", 1), ("back", 1)], body="leg"),
                    "inseam": dict(edges=[("front", "inseam", "end"), ("back", "inseam", "end")],
                                   label="Inseam", ring=[("front", 1), ("back", 1)], body="leg"),
                    "leg_hem": dict(hem=[("front", "hem"), ("back", "hem")], label="Leg opening",
                                    ring=[("front", 1), ("back", 1)], body="foot")},
    "beanie": {"crown": dict(edges=[("beanie", "crown", None)], label="Crown seam"),
               "sides": dict(edges=[("beanie", "right", "start"), ("beanie", "left", "end")], label="Side seam",
                             ring=[("beanie", 2)], body="head"),
               "bottom": dict(hem=[("beanie", "bottom")], label="Lower edge", ring=[("beanie", 2)], body="head")},
    "loop": {"long_edges": dict(edges=[("loop", "bottom", "start"), ("loop", "top", "end")],
                                label="Long edges", fixed_free=True)},
}
# what users (and Claude) call the zones
ALIASES = {"side_seam": "side", "sides_seam": "side", "body": "side", "body_side": "side", "torso": "side",
           "sleeves": "sleeve", "arm": "sleeve", "arms": "sleeve", "cuff": "sleeve_hem", "wrist": "sleeve_hem",
           "legs": "side", "leg": "side", "outseam": "side", "leg_opening": "leg_hem",
           "skirt": "skirt_side", "top": "crown", "edges": "long_edges", "hood_seam": "hood"}

SHAPES = ("points", "zigzag", "scallops", "waves", "curve")
APPENDAGES = ("spike", "ear", "round", "fin")
PLURALS = {"spike": "spikes", "ear": "ears", "round": "round tabs", "fin": "fins"}

# --------------------------------------------------------------------------- presets

# Own shapes only (no characters, faces or logos). "garments": where the preset makes sense.
PRESETS: dict[str, dict] = {
    "starfish": dict(
        name="Starfish", text="five-point star: round body, arms tapering to points, two pointed 'legs' at the "
                              "hem, a pointed hood as the fifth point",
        garments=("hoodie", "tshirt_basic", "dress"),
        features=[{"zone": "side", "bulge": {"at": 0.55, "cm": 3.0, "width": 0.9}},
                  {"zone": "sleeve", "profile": [[0.3, 3.0], [0.85, 0.5]]},
                  {"zone": "hem", "shape": "points", "count": 2, "depth_cm": 7.0},
                  {"zone": "hood", "peak": {"at": 0.7, "cm": 9.0, "width": 0.5}}]),
    "balloon": dict(name="Balloon", text="rounded balloon body, narrow again at the hem",
                    garments=("hoodie", "tshirt_basic", "dress"),
                    features=[{"zone": "side", "bulge": {"at": 0.55, "cm": 5.0, "width": 1.0}}]),
    "bell_sleeves": dict(name="Bell sleeves", text="sleeves widening towards the hand",
                         garments=("hoodie", "tshirt_basic", "dress"),
                         features=[{"zone": "sleeve", "flare": {"cm": 6.0, "from": 0.35}}]),
    "zigzag_hem": dict(name="Zigzag hem", text="pointed zigzag hem", garments=("tshirt_basic", "hoodie", "dress",
                                                                                "skirt"),
                       features=[{"zone": "hem", "shape": "points", "count": 4, "depth_cm": 4.0}]),
    "petal_hem": dict(name="Petal hem", text="rounded scallops like petals", garments=("tshirt_basic", "hoodie",
                                                                                       "dress", "skirt"),
                      features=[{"zone": "hem", "shape": "scallops", "count": 3, "depth_cm": 4.0}]),
    "elf": dict(name="Elf point", text="long pointed tip", garments=("hoodie", "beanie"),
                features=[{"zone": "hood", "peak": {"at": 0.75, "cm": 14.0, "width": 0.6}},
                          {"zone": "crown", "peak": {"at": 0.5, "cm": 12.0, "width": 0.9}}]),
    "cat_ears": dict(name="Cat ears", text="two pointed ears on the crown", garments=("beanie",),
                     features=[{"zone": "crown", "peak": {"at": 0.22, "cm": 5.0, "width": 0.3}},
                               {"zone": "crown", "peak": {"at": 0.78, "cm": 5.0, "width": 0.3}}]),
    "dino_spikes": dict(name="Dino spikes", text="a row of soft spikes in the hood (or crown) seam",
                        garments=("hoodie", "beanie"),
                        features=[{"zone": "hood", "appendage": {"shape": "spike", "count": 6, "height_cm": 4.0,
                                                                 "from": 0.15, "to": 0.95}},
                                  {"zone": "crown", "appendage": {"shape": "spike", "count": 4, "height_cm": 3.0,
                                                                  "from": 0.15, "to": 0.85}}]),
    "balloon_legs": dict(name="Balloon legs", text="wide, rounded legs that narrow to the cuff",
                         garments=("pants_basic",),
                         features=[{"zone": "side", "bulge": {"at": 0.6, "cm": 4.0, "width": 0.8}},
                                   {"zone": "inseam", "bulge": {"at": 0.6, "cm": 3.0, "width": 0.8}}]),
    "flared_legs": dict(name="Flared legs", text="legs that widen towards the hem", garments=("pants_basic",),
                        features=[{"zone": "side", "flare": {"cm": 5.0, "from": 0.5}},
                                  {"zone": "inseam", "flare": {"cm": 5.0, "from": 0.4}}]),
    "tulip_skirt": dict(name="Tulip", text="rounded tulip skirt with a curved hem", garments=("skirt", "dress"),
                        features=[{"zone": "side", "bulge": {"at": 0.45, "cm": 4.0, "width": 0.9}},
                                  {"zone": "skirt_side", "bulge": {"at": 0.45, "cm": 4.0, "width": 0.9}},
                                  {"zone": "hem", "shape": "curve", "depth_cm": 4.0}]),
    "wavy_loop": dict(name="Wavy loop", text="loop scarf with wavy edges", garments=("loop",),
                      features=[{"zone": "long_edges", "shape": "waves", "count": 4, "depth_cm": 3.0}]),
}


class DesignError(ValueError):
    pass


# --------------------------------------------------------------------------- spec

def load(design: Any) -> dict | None:
    """Design dict from a dict, a preset name, a JSON file or a JSON string (None: no design)."""
    if design in (None, "", {}, "none"):
        return None
    if isinstance(design, str):
        s = design.strip()
        if s in PRESETS:
            return {k: copy.deepcopy(v) for k, v in PRESETS[s].items() if k != "garments"} | {"preset": s}
        if s.startswith("{"):
            design = json.loads(s)
        elif os.path.exists(s):
            with open(s, encoding="utf-8") as f:
                design = json.load(f)
        else:
            raise DesignError(f"Unknown design '{s}'. Presets: {', '.join(PRESETS)}; or a JSON file/string.")
    if isinstance(design, list):
        design = {"features": design}
    if not isinstance(design, dict):
        raise DesignError("design must be a preset name, a dict or a list of features")
    d = copy.deepcopy(design)
    if d.get("preset") and not d.get("features"):
        base = load(d["preset"]) or {}
        d = {**base, **d}
    d.setdefault("name", "Design")
    d.setdefault("features", [])
    return d


def zone_name(garment: str, zone: str) -> str | None:
    z = ZONES.get(garment, {})
    zone = str(zone).strip().lower()
    if zone in z:
        return zone
    alias = ALIASES.get(zone)
    if alias in z:
        return alias
    if garment == "dress" and zone in ("skirt_side", "skirt"):
        return "skirt_side"
    return None


def _features(garment: str, design: dict, strict: bool) -> tuple[list[dict], list[str]]:
    """Features that apply to this garment (preset features for other garments are skipped)."""
    out, skipped = [], []
    preset = bool(design.get("preset"))
    for f in design.get("features", []):
        zn = zone_name(garment, f.get("zone", ""))
        if zn is None:
            msg = f"zone '{f.get('zone')}' does not exist for {garment} (zones: {', '.join(ZONES.get(garment, {}))})"
            if strict and not preset:
                raise DesignError(msg)
            skipped.append(msg)
            continue
        out.append({**f, "zone": zn})
    if not out and design.get("features"):
        raise DesignError(f"none of the design features fits {garment}: " + "; ".join(skipped))
    return out, skipped


# --------------------------------------------------------------------------- profiles

def _smooth(stations: list[tuple[float, float]], t: np.ndarray) -> np.ndarray:
    """Cosine interpolation between stations (zero slope at every station: no kinks)."""
    st = sorted(stations)
    ts = np.array([s[0] for s in st])
    vs = np.array([s[1] for s in st])
    out = np.zeros_like(t, dtype=float)
    for i, x in enumerate(t):
        if x <= ts[0]:
            out[i] = vs[0]
            continue
        if x >= ts[-1]:
            out[i] = vs[-1]
            continue
        j = int(np.searchsorted(ts, x, side="right") - 1)
        a, b = ts[j], ts[j + 1]
        w = 0.5 - 0.5 * math.cos(math.pi * (x - a) / (b - a)) if b > a else 1.0
        out[i] = vs[j] + (vs[j + 1] - vs[j]) * w
    return out


def _stations(f: dict) -> list[tuple[float, float]] | None:
    """Stations [(t, mm)] of a profile/bulge/flare/taper feature; endpoints default to 0."""
    if "profile" in f:
        st = [(float(t), float(v) * 10) for t, v in f["profile"]]
    elif "bulge" in f:
        b = f["bulge"]
        at, w, v = float(b.get("at", 0.5)), float(b.get("width", 0.6)), float(b["cm"]) * 10
        st = [(at - w / 2, 0.0), (at, v), (at + w / 2, 0.0)]
        st = [(min(1.0, max(0.0, t)), (v if t in (0.0, 1.0) and abs(t - at) < 1e-9 else vv))
              for t, vv in st]
    elif "flare" in f or "taper" in f:
        b = f.get("flare") or f.get("taper")
        if not isinstance(b, dict):
            b = {"cm": b}
        v = abs(float(b["cm"])) * 10 * (1 if "flare" in f else -1)
        st = [(float(b.get("from", 0.3)), 0.0), (1.0, v)]
    else:
        return None
    st = [(min(1.0, max(0.0, t)), v) for t, v in st]
    if not any(abs(t) < 1e-9 for t, _ in st):
        st.append((0.0, 0.0))
    if not any(abs(t - 1) < 1e-9 for t, _ in st):
        st.append((1.0, 0.0))
    # merge duplicate t (keep the larger magnitude)
    merged: dict[float, float] = {}
    for t, v in st:
        k = round(t, 6)
        merged[k] = v if abs(v) >= abs(merged.get(k, 0.0)) else merged[k]
    return sorted(merged.items())


def _peak(f: dict, t: np.ndarray) -> np.ndarray:
    p = f["peak"]
    at, w, v = float(p.get("at", 0.5)), float(p.get("width", 0.4)), float(p["cm"]) * 10
    x = np.clip(1 - np.abs(t - at) / (w / 2), 0, 1)
    if p.get("sharp", True):
        # pointed tip, soft shoulders: smoothstep of the distance, cusp at the apex
        return v * x * x * (3 - 2 * x)
    return v * 0.5 * (1 - np.cos(np.pi * x))


def _shape(f: dict, u: np.ndarray) -> np.ndarray:
    kind = f.get("shape", "points")
    if kind not in SHAPES:
        raise DesignError(f"unknown shape '{kind}' (shapes: {', '.join(SHAPES)})")
    d = float(f.get("depth_cm", 3.0)) * 10
    n = max(1, int(f.get("count", 3)))
    if kind == "curve":
        return d * np.sin(np.pi * np.clip(u, 0, 1))
    loc = (u * n) % 1.0
    loc[u >= 1.0] = 1.0
    if kind in ("points", "zigzag"):
        return d * (1 - np.abs(2 * loc - 1))
    if kind == "scallops":
        return d * np.sin(np.pi * loc)
    return d * 0.5 * (1 - np.cos(2 * np.pi * loc))           # waves


def _feature_fn(f: dict):
    """δ(t) in mm for one feature."""
    st = _stations(f)
    if st is not None:
        return lambda t: _smooth(st, np.asarray(t, float))
    if "peak" in f:
        return lambda t: _peak(f, np.asarray(t, float))
    if "shape" in f:
        return lambda t: _shape(f, np.asarray(t, float))
    return None


# --------------------------------------------------------------------------- helpers

def _normals(pts: np.ndarray) -> np.ndarray:
    """Outward normals of a CCW outline edge (right of the direction of travel)."""
    d = np.gradient(pts, axis=0)
    n = np.c_[d[:, 1], -d[:, 0]]
    ln = np.linalg.norm(n, axis=1)
    ln[ln < 1e-12] = 1.0
    return n / ln[:, None]


def _seam_edges(pat) -> set[tuple[str, str]]:
    out = set()
    for s in pat.seams:
        for side in ("a", "b"):
            for p, e, _n in s[side]:
                for name in e.split("+"):
                    out.add((p, name))
    return out


def _neighbours(pc: Piece, name: str) -> tuple[Edge, Edge]:
    i = pc.edge_index(name)
    return pc.edges[i - 1], pc.edges[(i + 1) % len(pc.edges)]


def _free(pat, pc: Piece, edge: Edge, seam_edges) -> bool:
    """A free edge: not sewn to anything (hem, front edge of a hood), so it may follow a moved corner."""
    return not edge.fold and (pc.key, edge.name) not in seam_edges


def _self_seam(pat, key: str, name: str) -> bool:
    """The edge is only sewn to its own mirror image (centre back seam of a mirrored pair): both
    sides change alike, so its end may move."""
    found = False
    for sm in pat.seams:
        refs = {(p, e) for side in ("a", "b") for p, e, _n in sm[side]}
        if (key, name) in refs:
            if refs != {(key, name)}:
                return False
            found = True
    return found


def _is_centre(e: Edge) -> bool:
    """Centre front/back of a half panel: a fold, a centre seam or a back opening."""
    return e.fold or e.name.startswith("center")


def _present(pat, refs):
    return [r for r in refs if pat.has(r[0]) and r[1] in {e.name for e in pat.piece(r[0]).edges}]


def _piece_width(pc: Piece, y: float) -> float:
    return G.width_at_y(pc.seam_ring(), y)


# --------------------------------------------------------------------------- prepare

def needs(garment: str, design: dict | None) -> dict:
    """Options a design needs before drafting (a pointed hem cannot have a hem band …)."""
    if not design:
        return {}
    feats, _ = _features(garment, design, strict=False)
    zones = {f["zone"] for f in feats}
    shaped = {f["zone"] for f in feats if "shape" in f or "peak" in f}
    out: dict = {}
    if garment in ("tshirt_basic", "hoodie", "dress") and "hem" in shaped:
        out["hem_band"] = False
        if garment == "hoodie":
            out["kangaroo"] = False                   # the pocket sits on the hem band seam
    if garment in ("tshirt_basic", "hoodie", "dress") and "sleeve_hem" in shaped:
        out["sleeve_cuffs"] = False
    if garment in ("tshirt_basic", "hoodie", "dress") and "sleeve" in zones and any(
            f["zone"] == "sleeve" and ("flare" in f) for f in feats):
        out["sleeve_cuffs"] = False                   # a bell sleeve is open at the hand
    if garment == "pants_basic" and ("leg_hem" in shaped or any("flare" in f for f in feats)):
        out["cuffs"] = False
    if garment == "beanie" and "bottom" in shaped:
        out["brim"] = False
    if garment == "hoodie" and "hood" in zones:
        out["hood"] = True
    return out


def _module_default(garment: str, key: str):
    from garments import get
    mod = get(garment)
    dflt = dict(getattr(mod, "DEFAULTS", {}))
    if garment == "hoodie":
        import garments.tshirt_basic as T
        dflt = {**T.DEFAULTS, **dflt}
    return dflt.get(key)


def prepare(garment: str, options: dict, design: dict | None) -> tuple[dict, list[str]]:
    """Options with what the design needs switched on/off, and a note per real change."""
    o = dict(options or {})
    notes = []
    for k, v in needs(garment, design).items():
        before = o.get(k) if o.get(k) is not None else _module_default(garment, k)
        if before is not None and bool(before) != bool(v):
            notes.append(f"Design: option {k} = {v} (instead of {before}): needed for the shape.")
        o[k] = v
    return o, notes


# --------------------------------------------------------------------------- apply

def apply(pat, design: Any, notes: list[str] | None = None):
    """Reshape the drafted base block `pat` in place with the design; returns the pattern.

    Adds `pat.design` (the resolved design) and `pat.design_checks` (report rows)."""
    d = load(design)
    if not d:
        return pat
    garment = pat.garment
    if garment not in ZONES:
        raise DesignError(f"designs are not available for {garment}")
    feats, skipped = _features(garment, d, strict=True)
    base = copy.deepcopy(pat)
    seam_edges = _seam_edges(pat)
    zones = ZONES[garment]
    rows: list[dict] = []
    applied: list[dict] = []
    # 1. seam zones (profiles, peaks, shapes on seams), then 2. hem zones, then 3. appendages
    order = sorted(feats, key=lambda f: (2 if "appendage" in f else 1 if "hem" in zones[f["zone"]] else 0))
    by_zone: dict[str, list[dict]] = {}
    for f in order:
        if "appendage" in f:
            continue
        by_zone.setdefault(f["zone"], []).append(f)
    for zn, fs in sorted(by_zone.items(), key=lambda kv: 1 if "hem" in zones[kv[0]] else 0):
        z = zones[zn]
        fns = [(f, _feature_fn(f)) for f in fs]
        if any(fn is None for _, fn in fns):
            raise DesignError(f"feature without profile/bulge/flare/taper/peak/shape: {fs}")
        if "hem" in z:
            info = _apply_hem(pat, z, fns, seam_edges)
        else:
            info = _apply_seam(pat, z, fns, seam_edges)
        if info is None:
            continue
        for f, _fn in fns:
            applied.append(dict(zone=zn, feature=f, **info))
    for f in order:
        if "appendage" in f:
            info = _add_appendage(pat, zones[f["zone"]], f)
            if info:
                applied.append(dict(zone=f["zone"], feature=f, **info))
    _retarget_corners(pat, base, applied)
    _update_finished(pat, applied)
    rows += _intended_rows(pat, d, applied)
    rows += _movement_rows(pat, base, applied)
    rows += _sewability_rows(pat, applied)
    pat.design = dict(name=d.get("name", "Design"), preset=d.get("preset"), inspiration=d.get("inspiration", ""),
                      features=[a["feature"] for a in applied], skipped=skipped)
    pat.design_checks = rows
    pat.options["design"] = {k: v for k, v in pat.design.items() if k != "skipped"}
    pat.notes.extend(notes or [])
    pat.notes.append(f"Creative design '{d.get('name', 'Design')}': the shape deviates from the base block on "
                     "purpose; see 'Design' in the validation report.")
    if any("shape" in a["feature"] and a.get("hem") for a in applied):
        pat.notes.append("Shaped hem: finish it with a narrow hem (overlock or zigzag the edge, turn 1 cm, "
                         "topstitch) or a facing; clip into every inner point.")
    if skipped and not d.get("preset"):
        pat.notes.append("Design features not used for this garment: " + "; ".join(skipped))
    return pat


def _arc_param(e: Edge, free: str | None) -> np.ndarray:
    """Distance (mm) of every point from the free end of the edge."""
    s = G.cumlen(e.pts)
    if free == "end":
        return s[-1] - s
    return s


def _apply_seam(pat, z: dict, fns, seam_edges) -> dict | None:
    refs = _present(pat, z["edges"])
    if not refs:
        return None
    # designable length: from the free end to the nearest attached point, the same on every edge
    S = min(pat.piece(p).edge(e).length for p, e, _ in refs)
    free_end_free = []
    for p, e, fr in refs:
        pc = pat.piece(p)
        prev, nxt = _neighbours(pc, e)
        if fr is None or z.get("fixed_free"):
            free_end_free.append(False)
            continue
        nb = prev if fr == "start" else nxt
        free_end_free.append(_free(pat, pc, nb, seam_edges))
    end_free = all(free_end_free)

    def delta(s: np.ndarray) -> np.ndarray:
        """s: distance from the free end in mm → offset in mm."""
        t = 1.0 - np.clip(s / S, 0.0, 1.0)            # t = 0 attached end, 1 free end
        if not any(fr for _, _, fr in refs) or z.get("fixed_free"):
            t = np.clip(s / S, 0.0, 1.0)              # both ends attached: plain arc parameter
        v = sum(fn(t) for _, fn in fns)
        v = np.where(s > S, 0.0, v)
        if not end_free:
            # an attached free end (cuff, band): fade to 0 over the last 15 % with zero slope
            k = np.clip((1.0 - t) / 0.15, 0.0, 1.0)
            v = v * (0.5 - 0.5 * np.cos(np.pi * k))
        # attached end: always 0 with zero slope
        k0 = np.clip(t / 0.12, 0.0, 1.0)
        v = v * (0.5 - 0.5 * np.cos(np.pi * k0))
        return v

    # gentle shapes only on short seams (a short sleeve cannot take a 3 cm bulge): limit the
    # steepness of profiles to 0.8 (≈ 39°); peaks are pointed on purpose and keep their height
    scale = 1.0
    both_attached = not any(fr for _, _, fr in refs) or z.get("fixed_free")
    ss = np.linspace(0, S, 201)
    smooth_fns = [fn for f, fn in fns if "peak" not in f]
    if smooth_fns:
        tt_ = np.clip(ss / S, 0, 1) if both_attached else 1.0 - np.clip(ss / S, 0, 1)
        prof0 = sum(fn(tt_) for fn in smooth_fns)
        steep0 = float(np.abs(np.diff(prof0)).max() / (S / 200)) if S > 0 else 0.0
        if steep0 > 0.8:
            scale = 0.8 / steep0
            fns = [(f, (lambda fn_: (lambda t: fn_(t) * scale))(fn)) if "peak" not in f else (f, fn)
                   for f, fn in fns]

    moved: dict[str, list] = {}
    extremes = []
    for p, e, fr in refs:
        pc = pat.piece(p)
        ed = pc.edge(e)
        old = ed.pts.copy()
        s = _arc_param(ed, fr if fr else "start")
        dv = delta(s)
        ed.pts = old + _normals(old) * dv[:, None]
        moved.setdefault(p, []).append((e, old))
        extremes.append((float(dv.min()), float(dv.max())))
    for p, lst in moved.items():
        _follow(pat.piece(p), lst, seam_edges, pat)
        _rescale_notches(pat.piece(p), lst)
    tt = np.linspace(0, 1, 101)
    prof = delta((1 - tt) * S) if any(fr for _, _, fr in refs) and not z.get("fixed_free") else delta(tt * S)
    return dict(min_mm=min(a for a, _ in extremes), max_mm=max(b for _, b in extremes), length=S,
                profile=prof, end_free=end_free, hem=False, label=z["label"], scale=scale)


def _apply_hem(pat, z: dict, fns, seam_edges) -> dict | None:
    refs = [r for r in _present(pat, z["hem"]) if _free(pat, pat.piece(r[0]), pat.piece(r[0]).edge(r[1]),
                                                       seam_edges)]
    if not refs:
        return None
    pieces_filter = None
    for f, _ in fns:
        if f.get("pieces"):
            pieces_filter = set(f["pieces"])
    # shapes in proportion to the panel (a doll skirt cannot take 4 cm scallops): depth at most
    # 0.45 × the width of one point/scallop, a curve at most 1/4 of the panel
    scale = 1.0
    for f, _fn in fns:
        if "shape" not in f:
            continue
        for p, e in refs:
            pc = pat.piece(p)
            prev, nxt = _neighbours(pc, e)
            panel = pc.edge(e).length * (2 if _is_centre(prev) or _is_centre(nxt) else 1)
            depth = abs(float(f.get("depth_cm", 3.0))) * 10
            lim = 0.25 * panel if f["shape"] == "curve" else 0.45 * panel / max(1, int(f.get("count", 3)))
            if depth > lim:
                scale = min(scale, lim / depth)
    if scale < 0.99:
        fns = [(f, (lambda fn_: (lambda t: fn_(t) * scale))(fn)) if "shape" in f else (f, fn) for f, fn in fns]
    moved: dict[str, list] = {}
    ext = []
    for p, e in refs:
        pc = pat.piece(p)
        ed = pc.edge(e)
        prev, nxt = _neighbours(pc, e)
        old = ed.pts.copy()
        s = G.cumlen(old)
        L = s[-1]
        if _is_centre(prev):
            u = 0.5 + 0.5 * s / L
        elif _is_centre(nxt):
            u = 0.5 * s / L
        else:
            u = s / L
        dv = np.zeros(len(old))
        for f, fn in fns:
            if pieces_filter and p not in set(f.get("pieces") or pieces_filter):
                continue
            dv = dv + fn(u)
        ed.pts = old + _normals(old) * dv[:, None]
        # shaped hem: narrow hem instead of a deep turned one
        if np.abs(dv).max() > 2.0:
            if ed.sa > 0:
                seam_sa = [x.sa for x in pc.edges if x.sa > 0 and not x.turned and x is not ed]
                narrow = min([10.0] + ([float(np.median(seam_sa))] if seam_sa else []))
                ed.sa = min(ed.sa, narrow) if ed.sa > 0 else ed.sa
                ed.turned = False
            if prev.fold or nxt.fold:
                # a point or a dip at the fold is intended (V at the centre)
                h = 1e-3
                f0 = sum(fn(np.array([0.5]))[0] for f, fn in fns)
                fr = sum(fn(np.array([0.5 + h]))[0] for f, fn in fns)
                if abs(fr - f0) / (h * 2 * L) > 0.02:
                    ed.pointed = True
        moved.setdefault(p, []).append((e, old))
        ext.append((float(dv.min()), float(dv.max())))
    for p, lst in moved.items():
        _follow(pat.piece(p), lst, seam_edges, pat)
        _rescale_notches(pat.piece(p), lst)
    uu = np.linspace(0, 1, 201)
    prof = sum(fn(uu) for _, fn in fns)
    return dict(min_mm=min(a for a, _ in ext), max_mm=max(b for _, b in ext), length=0.0, profile=prof,
                end_free=True, hem=True, label=z["label"], scale=scale)


def _follow(pc: Piece, moved: list, seam_edges, pat) -> None:
    """Free neighbour edges follow a moved corner (linear fade along their length)."""
    names = {e for e, _ in moved}
    olds = dict(moved)
    n = len(pc.edges)
    for i, ed in enumerate(pc.edges):
        if ed.name in names:
            continue
        prev, nxt = pc.edges[i - 1], pc.edges[(i + 1) % n]
        d0 = (prev.pts[-1] - olds[prev.name][-1]) if prev.name in names else np.zeros(2)
        d1 = (nxt.pts[0] - olds[nxt.name][0]) if nxt.name in names else np.zeros(2)
        if np.linalg.norm(d0) < 1e-6 and np.linalg.norm(d1) < 1e-6:
            continue
        if not _free(pat, pc, ed, seam_edges) and not ed.fold and not _self_seam(pat, pc.key, ed.name):
            raise DesignError(f"{pc.name}: the design would move the end of '{ed.label or ed.name}', "
                              "which is sewn to another piece")
        s = G.cumlen(ed.pts)
        w = (s / s[-1])[:, None]
        ed.pts = ed.pts + (1 - w) * d0 + w * d1


def _rescale_notches(pc: Piece, moved: list) -> None:
    olds = dict(moved)
    for nt in pc.notches:
        if nt.edge in olds:
            r = pc.edge(nt.edge).length / max(G.length(olds[nt.edge]), 1e-6)
            nt.s = nt.s * r


# --------------------------------------------------------------------------- appendages

def appendage_outline(shape: str, base: float, height: float) -> np.ndarray:
    """Outline from (base, 0) over the tip back to (0, 0), counter-clockwise with the base edge."""
    b, h = base, height
    if shape == "spike":
        c = G.join(G.cubic(G.P(b, 0), G.P(b * 0.9, h * 0.35), G.P(b * 0.62, h * 0.8), G.P(b / 2, h)),
                   G.cubic(G.P(b / 2, h), G.P(b * 0.38, h * 0.8), G.P(b * 0.1, h * 0.35), G.P(0, 0)))
    elif shape == "ear":
        c = G.join(G.cubic(G.P(b, 0), G.P(b * 1.02, h * 0.45), G.P(b * 0.7, h * 0.92), G.P(b * 0.45, h)),
                   G.cubic(G.P(b * 0.45, h), G.P(b * 0.25, h * 0.95), G.P(-b * 0.02, h * 0.45), G.P(0, 0)))
    elif shape == "fin":
        c = G.join(G.cubic(G.P(b, 0), G.P(b * 0.95, h * 0.5), G.P(b * 0.55, h), G.P(b * 0.1, h)),
                   G.cubic(G.P(b * 0.1, h), G.P(b * 0.15, h * 0.6), G.P(0.05 * b, h * 0.25), G.P(0, 0)))
    elif shape == "round":
        c = G.join(G.tangent_curve(G.P(b, 0), (0, 1), G.P(b / 2, h), (-1, 0), 0.55, 0.55),
                   G.tangent_curve(G.P(b / 2, h), (-1, 0), G.P(0, 0), (0, -1), 0.55, 0.55))
    else:
        raise DesignError(f"unknown appendage shape '{shape}' (shapes: {', '.join(APPENDAGES)})")
    return c


def _add_appendage(pat, z: dict, f: dict) -> dict | None:
    a = f["appendage"]
    refs = _present(pat, z.get("edges", []))
    if not refs:
        return None
    shape = a.get("shape", "spike")
    n = max(1, int(a.get("count", 3)))
    h = float(a.get("height_cm", 4.0)) * 10
    t0, t1 = float(a.get("from", 0.15)), float(a.get("to", 0.9))
    p0, e0, fr = refs[0]
    host = pat.piece(p0)
    hedge = host.edge(e0)
    L = hedge.length
    span = abs(t1 - t0) * L
    gap = float(a.get("gap_cm", 0.5)) * 10
    base = float(a.get("base_cm", 0.0)) * 10 or max(20.0, (span - gap * (n - 1)) / n)
    total = n * base + (n - 1) * gap
    key = f"design_{shape}" if not pat.has(f"design_{shape}") else f"design_{shape}_{len(pat.pieces)}"
    sa_seam = hedge.sa
    sa_out = 6.0
    outline = appendage_outline(shape, base, h)
    # the seam edge in two halves (a piece needs at least three edges); the outline is one edge
    edges = [Edge("base", G.line(G.P(0, 0), G.P(base / 2, 0)), sa_seam, label="Seam edge (into the seam)"),
             Edge("base_2", G.line(G.P(base / 2, 0), G.P(base, 0)), sa_seam, label="Seam edge (into the seam)"),
             Edge("outline", outline, sa_out, label="Outline (sew, turn)")]
    name = {"spike": "Spike", "ear": "Ear", "round": "Round tab", "fin": "Fin"}[shape]
    pc = Piece(key, name, edges, cut_count=2 * n, mirror=shape == "fin", fabric=a.get("fabric", "Main fabric"),
               grain=(G.P(base / 2, h * 0.15), G.P(base / 2, h * 0.6)))
    pc.info.append(f"{n} × 2 layers" + (", stuffed" if a.get("stuffed") else ""))
    pat.pieces.append(pc)
    pat.seams.append(dict(name=f"{name}: outline (both layers)", a=[(key, "outline", 1)],
                          b=[(key, "outline", 1)], type="equal"))
    # placement notches on the host seam (both edges of a self seam are the same edge)
    s_from_start = (lambda t: t * L) if fr != "end" else (lambda t: t * L)
    start = s_from_start(min(t0, t1)) + max(0.0, (span - total) / 2)
    pos = []
    for i in range(n):
        a0 = start + i * (base + gap)
        pos.append((a0, a0 + base))
    for p, e, _ in refs:
        pcx = pat.piece(p)
        Le = pcx.edge(e).length
        for a0, a1 in pos:
            for s in (a0, a1):
                if 0 < s < Le:
                    pcx.notches.append(Notch(e, s if fr != "end" else s, 1))
    tip = _tip_angle(outline)
    return dict(min_mm=0.0, max_mm=h, length=L, profile=None, end_free=False, hem=False, label=z["label"],
                appendage=dict(key=key, name=name, count=n, base=base, height=h, total=total, span=span, tip=tip,
                               host=(p0, e0), positions=pos))


def _tip_angle(outline: np.ndarray) -> float:
    """Angle (°) at the tip of an appendage: between the two outline halves at the highest point."""
    i = int(np.argmax(outline[:, 1]))
    if i < 3 or i > len(outline) - 4:
        return 180.0
    a = outline[i] - outline[max(0, i - 6)]
    b = outline[min(len(outline) - 1, i + 6)] - outline[i]
    return 180.0 - G.angle_deg(a, b)


def _update_finished(pat, applied) -> None:
    """Finished measurements the design changed (hem width of a shaped/flared hem)."""
    if "hem_circ" in pat.finished and not pat.has("hem_band"):
        z = ZONES[pat.garment].get("hem")
        if z:
            refs = [r for r in _present(pat, z["hem"]) if r[0] in dict(z.get("ring") or [])]
            ring = dict(z.get("ring") or [])
            if refs:
                pat.finished["hem_circ"] = sum(ring[p] * pat.piece(p).edge(e).length for p, e in refs)


# --------------------------------------------------------------------------- steps

def adjust_steps(pat, body: list) -> list:
    """Booklet steps for a design: appendages are sewn and turned before the seam they sit in,
    the seam step says where they go; a shaped hem gets the clipping/pressing tip."""
    import steps as ST
    feats = (pat.design or {}).get("features") or []
    zones = ZONES.get(pat.garment, {})
    out = list(body)
    for f in feats:
        z = zones.get(f.get("zone"), {})
        if "appendage" in f:
            key = next((p.key for p in pat.pieces if p.key.startswith("design_" + f["appendage"].get("shape",
                                                                                                   "spike"))), None)
            if not key:
                continue
            pc = pat.piece(key)
            n = int(f["appendage"].get("count", 3))
            plural = PLURALS[f["appendage"].get("shape", "spike")]
            seam_name = next((s["name"] for s in pat.seams if s["a"][0][0] == key), None)
            sa = ST.cm(pc.edge("outline").sa)
            prep = [ST.seam(f"Sew the {plural}", [seam_name] if seam_name else [],
                            f"Lay two {plural[:-1]} pieces right sides together. Sew round the outline with {sa} "
                            "seam allowance; leave the straight seam edge open.", section="Design", repeat=n,
                            hint="Trim the allowance at the tip to 3 mm and clip the curves."),
                    ST.icon(f"Turn the {plural} right side out", "turn",
                            "Push the tip out gently with a blunt pencil and press." +
                            (" Stuff lightly." if f["appendage"].get("stuffed") else ""), section="Design")]
            host = z.get("edges", [(None, None, None)])[0]
            idx = next((i for i, s in enumerate(out) if any(
                str(sn).lower().startswith(z.get("label", "~").lower()) or host[1] and str(sn).lower().startswith(
                    host[0] or "~") for sn in s.seams)), None)
            if idx is None:
                idx = max(0, len(out) - 1)
            else:
                target = out[idx]
                target.hint = (f"Pin the {plural} between the notches onto the right side of one piece, "
                               "tips pointing inwards, raw edges level; baste, then sew the seam over them.")
            out[idx:idx] = prep
        elif "shape" in f and "hem" in z:
            for s in out:
                if s.stitch == "hem" and any(e[1] == "hem" for e in s.edges):
                    s.tip = s.tip or ("Shaped hem: clip into every inner point up to 2 mm before the fold and "
                                      "press each point separately.")
    return out


# --------------------------------------------------------------------------- corners

def _retarget_corners(pat, base, applied) -> None:
    """Corners at a reshaped edge whose angle the design changed: the new angle is the target
    (marked intended). Corners at attached ends keep their angle by construction."""
    for c in pat.corners:
        trip = c.get("sum") or [(c["piece"], c["a"], c["b"])]
        try:
            new = sum(G.corner_angle(pat.piece(p).edge(a).pts, pat.piece(p).edge(b).pts) for p, a, b in trip)
            old = sum(G.corner_angle(base.piece(p).edge(a).pts, base.piece(p).edge(b).pts) for p, a, b in trip)
        except KeyError:
            continue
        if abs(new - old) > 1.0:
            c["target"] = round(new, 1)
            c["note"] = (c.get("note", "") + "; " if c.get("note") else "") + "changed by the design (intended)"


# --------------------------------------------------------------------------- report rows

def _row(group, name, status, target, actual, delta="", note=""):
    return dict(group=group, name=name, status=status, target=target, actual=actual, delta=delta, note=note)


def _cm(v):
    return f"{v / 10:+.1f} cm"


def describe_feature(f: dict) -> str:
    """One feature in words (English; translated by i18n.t where shown)."""
    if "bulge" in f:
        b = f["bulge"]
        return f"bulge {float(b['cm']):+.1f} cm at {float(b.get('at', 0.5)) * 100:.0f} %"
    if "flare" in f:
        b = f["flare"] if isinstance(f["flare"], dict) else {"cm": f["flare"]}
        return f"flare +{abs(float(b['cm'])):.1f} cm towards the free end"
    if "taper" in f:
        b = f["taper"] if isinstance(f["taper"], dict) else {"cm": f["taper"]}
        return f"taper −{abs(float(b['cm'])):.1f} cm towards the free end"
    if "profile" in f:
        return "profile " + ", ".join(f"{float(v):+.1f} cm at {float(t) * 100:.0f} %" for t, v in f["profile"])
    if "peak" in f:
        p = f["peak"]
        return f"peak {float(p['cm']):+.1f} cm at {float(p.get('at', 0.5)) * 100:.0f} %"
    if "shape" in f:
        k = f["shape"]
        cnt = "" if k == "curve" else f"{int(f.get('count', 3))} × "
        return f"{cnt}{k}, {float(f.get('depth_cm', 3)):.1f} cm deep"
    if "appendage" in f:
        a = f["appendage"]
        return f"{int(a.get('count', 3))} × {a.get('shape', 'spike')}, {float(a.get('height_cm', 4)):.1f} cm high"
    return "?"


def _intended_rows(pat, d, applied) -> list[dict]:
    rows = []
    for a in applied:
        f = a["feature"]
        what = describe_feature(f)
        if a.get("appendage"):
            ap = a["appendage"]
            actual = f"{ap['count']} × {ap['base'] / 10:.1f} × {ap['height'] / 10:.1f} cm"
        else:
            actual = f"{a['min_mm'] / 10:+.1f} … {a['max_mm'] / 10:+.1f} cm"
        note = f"intended deviation (design '{d.get('name', 'Design')}')"
        if a.get("scale", 1.0) < 0.99:
            note += f"; scaled to {a['scale'] * 100:.0f} % (seam too short for the full shape)"
        rows.append(_row("Design (intended)", f"{a['label']}: {what}", "OK", "base block", actual, "", note))
    return rows


def _min_ease(pat) -> float:
    fab = pat.options.get("fabric") or "jersey"
    try:
        knit = E.fabric_info(fab, pat.options.get("stretch"))[2]
    except ValueError:
        knit = True
    return -0.05 if knit else 0.04


def _stretch(pat) -> float:
    fab = pat.options.get("fabric") or "jersey"
    try:
        return E.fabric_info(fab, pat.options.get("stretch"))[1]
    except ValueError:
        return 0.0


def _body_ref(pat, body: str, t: float) -> float | None:
    """Body girth (mm) the zone has to go round or pass at position t (0 attached, 1 free end)."""
    m = pat.measures
    st = _stretch(pat) / 100 * 0.6

    def g(k, default=None):
        return m.get(k, default)
    if body == "torso":
        chest, hip = g("chest"), max(g("waist", 0), g("hip", 0) * 0.92)
        return chest + (hip - chest) * t if chest else None
    if body == "arm":
        ua, wr = g("upper_arm"), g("wrist")
        if not ua or not wr:
            return None
        hand = 1.55 * wr / (1 + st)
        return max(ua + (wr * 1.15 - ua) * t, hand)
    if body == "leg":
        th, kn, an = g("thigh"), g("knee"), g("ankle")
        if not th or not an:
            return None
        foot = 1.35 * an / (1 + st)
        kn = kn or (th + an) / 2
        v = th + (kn - th) * (t / 0.5) if t < 0.5 else kn + (an - kn) * ((t - 0.5) / 0.5)
        return max(v, foot)
    if body in ("hip", "stride"):
        hip = g("hip")
        return hip * (1.0 if body == "hip" else 1.05) if hip else None
    if body == "hip_pass":
        hip = g("hip")
        return hip / (1 + st) if hip else None
    if body == "hand":
        wr = g("wrist")
        return 1.55 * wr / (1 + st) if wr else None
    if body == "foot":
        an = g("ankle")
        return 1.35 * an / (1 + st) if an else None
    if body == "head":
        hd = g("head")
        return hd * 0.78 if hd else None
    return None


def _girth(pat, ring, y) -> float:
    tot = 0.0
    for p, mult in ring:
        if pat.has(p):
            tot += mult * _piece_width(pat.piece(p), y)
    return tot


def _movement_rows(pat, base, applied) -> list[dict]:
    """Freedom of movement after the reshaping: girth along each zone ≥ body + minimum ease,
    and never unintentionally tighter than the base block."""
    rows = []
    zones = ZONES[pat.garment]
    done = set()
    me = _min_ease(pat)
    for a in applied:
        zn = a["zone"]
        if zn in done or a.get("appendage"):
            continue
        done.add(zn)
        z = zones[zn]
        ring, body = z.get("ring"), z.get("body")
        if not ring or not body:
            continue
        worst = None
        if a["hem"]:
            # opening length along the hem edges (unfolded)
            new = sum(mult * pat.piece(p).edge(e).length for (p, e) in _present(pat, z["hem"])
                      for (rp, mult) in ring if rp == p)
            old = sum(mult * base.piece(p).edge(e).length for (p, e) in _present(base, z["hem"])
                      for (rp, mult) in ring if rp == p)
            ref = _body_ref(pat, body, 1.0)
            if ref:
                need = ref * (1 + max(me, 0.0)) if body in ("hip_pass", "hand", "foot") else ref
                worst = (1.0, new, old, need, None)
        else:
            refs = _present(pat, z["edges"])
            p0, e0, fr = refs[0]
            ed = pat.piece(p0).edge(e0)
            bed = base.piece(p0).edge(e0)
            S = a["length"]
            for t in np.linspace(0.08, 0.95, 12):
                s = (1 - t) * S if fr else t * S
                s_eff = s if fr == "start" or fr is None else ed.length - s
                y = float(G.point_at(ed.pts, s_eff)[1])
                yb = float(G.point_at(bed.pts, s if fr == "start" or fr is None else bed.length - s)[1])
                new = _girth(pat, ring, y)
                old = _girth(base, ring, yb)
                ref = _body_ref(pat, body, float(t))
                if not ref or new <= 0 or old <= 0:
                    continue
                need = ref * (1 + me)
                # worst place: the least room left; a place tighter than the base block counts first
                key = (0 if new < old - 1.0 else 1, new - need)
                if worst is None or key < worst[4]:
                    worst = (float(t), new, old, need, key)
        if worst is None:
            continue
        t, new, old, need, _k = worst
        if new >= old - 1.0:
            st = "OK"
            note = "not tighter than the base block"
        elif new >= need:
            st = "OK"
            note = "tighter than the base block, still enough room"
        else:
            st = "ERROR"
            note = "too tight: less than body + minimum ease (cannot move / pull it on)"
        rows.append(_row("Freedom of movement", f"{a['label']}: girth after the design", st,
                         f"≥ {need / 10:.1f} cm", f"{new / 10:.1f} cm", f"{(new - old) / 10:+.1f} cm vs. base",
                         note + f" (at {t * 100:.0f} %)"))
    return rows


def _point_angles(pts: np.ndarray) -> tuple[float, float]:
    """Smallest outer (convex) and inner (concave) corner angle along a CCW outline edge (°)."""
    rs = G.resample(np.asarray(pts, float), 2.0)
    best_out, best_in = 180.0, 180.0
    k = 3
    for i in range(k, len(rs) - k):
        a, b, c = rs[i - k], rs[i], rs[i + k]
        u, v = b - a, c - b
        ang = 180.0 - G.angle_deg(u, v)
        if ang > 150:
            continue
        if u[0] * v[1] - u[1] * v[0] > 0:          # left turn on a CCW outline: convex point
            best_out = min(best_out, ang)
        else:
            best_in = min(best_in, ang)
    return best_out, best_in


def _sewability_rows(pat, applied) -> list[dict]:
    rows = []
    for a in applied:
        f = a["feature"]
        if a.get("appendage"):
            ap = a["appendage"]
            st = "OK" if ap["total"] <= ap["span"] + 1.0 and ap["total"] <= 0.9 * a["length"] else "ERROR"
            rows.append(_row("Design sewability", f"{ap['name']}: room in the seam ({a['label']})", st,
                             f"≤ {min(ap['span'], 0.9 * a['length']) / 10:.1f} cm", f"{ap['total'] / 10:.1f} cm", "",
                             "all appendages side by side between the notches"))
            tip = ap["tip"]
            st = "OK" if tip >= 40 else ("WARNING" if tip >= 25 else "ERROR")
            rows.append(_row("Design sewability", f"{ap['name']}: tip can be turned", st, "≥ 40°", f"{tip:.0f}°", "",
                             "narrower tips cannot be turned right side out"))
            st = "OK" if ap["base"] >= 25 else "WARNING"
            rows.append(_row("Design sewability", f"{ap['name']}: wide enough to turn", st, "≥ 2.5 cm",
                             f"{ap['base'] / 10:.1f} cm", "", "base width"))
            continue
        # tips and inner corners of the reshaped edges
        zones = ZONES[pat.garment]
        z = zones[a["zone"]]
        refs = [(p, e) for p, e in _present(pat, z["hem"])] if a["hem"] else \
            [(p, e) for p, e, _ in _present(pat, z["edges"])]
        worst_out, worst_in, steep = 180.0, 180.0, 0.0
        for p, e in refs:
            pc = pat.piece(p)
            o, i = _point_angles(pc.edge(e).pts)
            worst_out, worst_in = min(worst_out, o), min(worst_in, i)
        if a["profile"] is not None and not a["hem"] and a["length"] > 0 and "peak" not in f:
            prof = np.asarray(a["profile"], float)
            steep = float(np.abs(np.diff(prof)).max() / (a["length"] / (len(prof) - 1)))
        if worst_out < 180 or worst_in < 180:
            st = "OK" if worst_out >= 60 else ("WARNING" if worst_out >= 35 else "ERROR")
            rows.append(_row("Design sewability", f"{a['label']}: points can be sewn and turned", st, "≥ 60°",
                             f"{worst_out:.0f}°" if worst_out < 180 else "no points", "",
                             "outer points of the reshaped edge"))
            st = "OK" if worst_in >= 60 else "WARNING"
            rows.append(_row("Design sewability", f"{a['label']}: inner corners", st, "≥ 60°",
                             f"{worst_in:.0f}°" if worst_in < 180 else "none", "",
                             "clip into inner corners up to the seam line" if worst_in < 180 else ""))
        if steep:
            st = "OK" if steep <= 1.0 else ("WARNING" if steep <= 2.0 else "ERROR")
            rows.append(_row("Design sewability", f"{a['label']}: steepness of the shape", st, "≤ 1.0",
                             f"{steep:.2f}", "", "offset change per length along the seam (1.0 = 45°)"))
    return rows


# --------------------------------------------------------------------------- confirmation text

def describe(garment: str, design: Any, options: dict | None = None) -> str:
    """The feature list to show the user before generating ("Is that right?")."""
    d = load(design)
    if not d:
        return "No design: the base block as drafted."
    feats, skipped = _features(garment, d, strict=False)
    zones = ZONES.get(garment, {})
    lines = [f"Design '{d.get('name', 'Design')}' for {garment}" + (f" ({d['text']})" if d.get("text") else ""), ""]
    for i, f in enumerate(feats, 1):
        z = zones[f["zone"]]
        lines.append(f"{i}. {z['label']}: {describe_feature(f)}")
    o, notes = prepare(garment, options or {}, d)
    if notes:
        lines += ["", "Needed for the shape:"] + [f"- {n.removeprefix('Design: ')}" for n in notes]
    if skipped:
        lines += ["", "Not used for this garment:"] + [f"- {s}" for s in skipped]
    lines += ["", "Checked after reshaping: seam lengths and angles, seam allowances, room to move (girth ≥ body "
                  "+ minimum ease, head/hand/foot fit through), points and inner corners, appendage sizes. "
                  "The report lists every feature as an intended deviation from the base block."]
    return "\n".join(lines)


def zones_text() -> str:
    out = []
    for g, zs in ZONES.items():
        out.append(f"{g}: " + ", ".join(f"{k} ({v['label']})" for k, v in zs.items()))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Creative silhouettes: presets, zones, feature list")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("presets")
    sub.add_parser("zones")
    dsc = sub.add_parser("describe")
    dsc.add_argument("design", help="preset name, JSON file or JSON string")
    dsc.add_argument("--garment", required=True)
    dsc.add_argument("--options", help="module options as JSON")
    a = ap.parse_args(argv)
    if a.cmd == "presets":
        for k, v in PRESETS.items():
            print(f"{k}: {v['text']} [{', '.join(v['garments'])}]")
    elif a.cmd == "zones":
        print(zones_text())
    else:
        print(describe(a.garment, a.design, json.loads(a.options) if a.options else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
