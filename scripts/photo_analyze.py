"""Photo mode A (inspiration photo): feature list with confidence → module + options.

The actual image description is done by Claude while looking at the photo; it fills the
feature JSON (schema below). This script
  1. checks and normalises the feature list,
  2. phrases the confirmation question ("I can see: … is that right?"),
  3. maps the features onto an existing module + options and openly reports what no
     module covers (with the closest alternative),
  4. can estimate the silhouette automatically from proportions for cut-out images
     (product photo / flat lay on a plain background); ratios only, never measurements!

Body measurements always come from the user (size or measurements), never from an
inspiration photo.

CLI:
  python photo_analyze.py features.json        → mapping + confirmation text
  python photo_analyze.py --image photo.jpg    → automatic proportions (pants)
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA = {
    "garment_type": ["pants", "jogger", "harem", "leggings", "shorts", "tshirt", "longsleeve",
                     "hoodie", "sweatshirt", "sweater", "skirt", "beanie", "loop", "dress", "jacket",
                     "blouse", "shirt", "jeans", "overalls", "body"],
    "silhouette": ["slim", "straight", "wide", "oversized", "harem", "flared", "a-line", "circle_skirt"],
    "length": ["long", "7/8", "knee", "short", "mini", "midi", "maxi", "hip_length", "tunic"],
    "pockets": ["none", "side", "slant", "back_patch", "front_patch", "kangaroo",
                "cargo", "welt", "jetted"],
    "waistband": ["elastic", "casing", "rib", "drawstring", "yoga", "button_zip"],
    "leg_finish": ["rib", "hem", "drawstring"],
    "neckline": ["round", "v", "u-boot", "stand_collar", "collar", "hood"],
    "sleeve": ["set_in", "raglan", "dropped", "none"],
    "sleeve_length": ["short", "long", "3/4", "none"],
    "sleeve_finish": ["rib", "hem"],
    "hem": ["rib", "hemmed"],
    "closure": ["none", "button_placket", "zipper", "snaps"],
    "hood": ["yes", "no"],
    "fabric": ["jersey", "jersey_elastane", "sweat", "fleece", "interlock", "woven", "knit"],
    "style_lines": ["none", "yoke", "vertical_seams", "horizontal_seams"],
}

LABELS = {
    "garment_type": "Garment type", "silhouette": "Silhouette", "length": "Length", "pockets": "Pockets",
    "waistband": "Waistband", "leg_finish": "Leg finish", "neckline": "Neckline", "sleeve": "Sleeve type",
    "sleeve_length": "Sleeve length", "sleeve_finish": "Sleeve finish", "hem": "Hem",
    "closure": "Closure", "hood": "Hood", "fabric": "Likely fabric",
    "style_lines": "Style lines",
}

VALUE_LABELS = {"side": "side pockets", "slant": "slanted side pockets",
                "back_patch": "back patch pockets", "kangaroo": "kangaroo pocket",
                "casing": "fabric waistband with elastic", "elastic": "elastic", "rib": "rib knit",
                "drawstring": "drawstring", "harem": "harem (dropped crotch, tapered)",
                "jersey_elastane": "jersey with elastane", "sweat": "sweat", "button_zip":
                "button + zip", "dropped": "dropped shoulder"}

UNSUPPORTED = {
    "dress": "Dresses are not a module (yet). Alternative: the T-shirt module lengthened (length "
             "\"tunic\") or a top + skirt.",
    "jacket": "Jackets with lining/zip are not covered. Alternative: hoodie (an open front with a zip "
              "is not possible) or sweatshirt.",
    "blouse": "Blouses with button placket/collar are not covered. Alternative: T-shirt in woven fabric "
              "with more ease.",
    "shirt": "Shirts are not covered. Alternative: the T-shirt module.",
    "jeans": "Jeans with a fly are not covered. Alternative: pull-on trousers in woven fabric with a "
             "drawstring casing.",
    "overalls": "Overalls are not covered. Alternative: pants; the bib would have to be added separately.",
    "body": "Bodysuits are not covered. Alternative: the T-shirt module.",
    "cargo": "Cargo pockets are not covered. Alternative: back patch pockets.",
    "welt": "Welt pockets are not covered. Alternative: side pockets.",
    "jetted": "Jetted pockets are not covered. Alternative: side pockets.",
    "front_patch": "Front patch pockets are not an option. Alternative: side pockets.",
    "button_zip": "A waistband with button and zip is not covered. Alternative: elastic waistband "
                  "(pull-on pants).",
    "flared": "Flared legs are not covered. Alternative: wide fit.",
    "button_placket": "Button plackets are not covered. Alternative: no closure.",
    "zipper": "Zips are not covered. Alternative: no closure.",
    "snaps": "Snap plackets are not covered. Alternative: no closure.",
    "stand_collar": "Stand collars are not covered. Alternative: round neck with a wide neckband.",
    "collar": "Shirt collars are not covered. Alternative: round neck.",
    "yoke": "Style lines (yoke) are not covered. The pattern is drafted without the split.",
    "vertical_seams": "Vertical style lines are not covered. The pattern is drafted without the split.",
    "horizontal_seams": "Horizontal style lines are not covered. The pattern is drafted without the split.",
    "u-boot": "Boat necks are not an option. Alternative: wide round neck.",
    "dropped": "Dropped shoulders are not an option. Alternative: raglan or oversized fit.",
}


def normalize(features: dict) -> dict:
    """Check the feature list. Format per feature: {"value": ..., "confidence": 0..1} or just the value."""
    out = {}
    for k, v in features.items():
        if k in ("proportions", "notes"):
            out[k] = v
            continue
        if k not in SCHEMA:
            raise ValueError(f"Unknown feature '{k}'. Allowed: {', '.join(SCHEMA)}")
        if not isinstance(v, dict):
            v = {"value": v, "confidence": 0.7}
        vals = v["value"] if isinstance(v["value"], list) else [v["value"]]
        for x in vals:
            if x not in SCHEMA[k]:
                raise ValueError(f"Value '{x}' is not allowed for '{k}'. Allowed: {', '.join(SCHEMA[k])}")
        out[k] = {"value": v["value"], "confidence": float(v.get("confidence", 0.7))}
    if "garment_type" not in out:
        raise ValueError("Feature 'garment_type' is missing.")
    return out


def _val(f, k, default=None):
    return f[k]["value"] if k in f else default


def _conf_word(c):
    return "certain" if c >= 0.8 else ("likely" if c >= 0.55 else "uncertain")


def confirmation_text(features: dict) -> str:
    f = normalize(features)
    parts = []
    for k, v in f.items():
        if k in ("proportions", "notes"):
            continue
        vals = v["value"] if isinstance(v["value"], list) else [v["value"]]
        txt = ", ".join(VALUE_LABELS.get(x, x) for x in vals)
        parts.append(f"- {LABELS[k]}: **{txt}** ({_conf_word(v['confidence'])}, {v['confidence'] * 100:.0f} %)")
    unsure = [LABELS[k] for k, v in f.items() if k in LABELS and v["confidence"] < 0.55]
    text = "I can see in the photo:\n" + "\n".join(parts)
    if unsure:
        text += f"\n\nI am unsure about: {', '.join(unsure)}. Please confirm or correct."
    text += ("\n\nIs that right? I don't take body measurements from the photo, so please give a size or "
             "measurements. I will ask about the back and hidden details instead of inventing them.")
    return text


def map_to_module(features: dict) -> dict:
    """Features → (module, options, not covered + alternatives)."""
    f = normalize(features)
    kind = _val(f, "garment_type")
    issues = []
    for k, v in f.items():
        if k in ("proportions", "notes"):
            continue
        for x in (v["value"] if isinstance(v["value"], list) else [v["value"]]):
            if x in UNSUPPORTED:
                issues.append(UNSUPPORTED[x])
    sil = _val(f, "silhouette", "straight")
    fit = {"slim": "slim", "straight": "normal", "wide": "wide", "oversized": "oversized",
           "harem": "harem", "flared": "wide"}.get(sil, "normal")
    fabric = _val(f, "fabric")
    opts = {}
    if kind in ("pants", "jogger", "harem", "leggings", "shorts", "jeans", "overalls"):
        module = "pants_basic"
        style = {"harem": "harem", "leggings": "leggings"}.get(kind, "jogger")
        if fit == "harem":
            style = "harem"
        if fit == "slim" and kind != "jogger":
            style = "leggings"
        opts["style"] = style
        opts["fit"] = fit
        t = _val(f, "pockets", [])
        t = t if isinstance(t, list) else [t]
        pk = []
        if any(x in ("side", "slant", "welt", "jetted", "front_patch") for x in t):
            pk.append("side")
        if any(x in ("back_patch", "cargo") for x in t):
            pk.append("back_patch")
        opts["pockets"] = pk
        b = _val(f, "waistband")
        if b:
            opts["waistband"] = {"elastic": "casing", "casing": "casing", "rib": "rib",
                                 "drawstring": "tunnel", "yoga": "yoga",
                                 "button_zip": "casing"}[b]
        ba = _val(f, "leg_finish")
        if ba:
            opts["cuffs"] = ba == "rib"
        lg = _val(f, "length")
        if kind == "shorts":
            lg = lg or "short"
        if lg in ("long", "7/8", "knee", "short"):
            opts["length"] = lg
    elif kind in ("tshirt", "longsleeve", "body", "dress", "blouse", "shirt"):
        module = "tshirt_basic"
        opts["fit"] = fit
        opts["sleeve_style"] = "raglan" if _val(f, "sleeve") == "raglan" else "set_in"
        al = _val(f, "sleeve_length", "long" if kind == "longsleeve" else "short")
        opts["sleeve_length"] = {"short": "short", "long": "long", "3/4": "3/4", "none": "short"}[al]
        opts["neckline"] = "v" if _val(f, "neckline") == "v" else "round"
        if kind == "dress" or _val(f, "length") == "tunic":
            opts["length"] = "tunic"
        if _val(f, "sleeve_finish") == "rib":
            opts["sleeve_cuffs"] = True
        if _val(f, "hem") == "rib":
            opts["hem_band"] = True
    elif kind in ("hoodie", "sweatshirt", "sweater", "jacket"):
        module = "hoodie"
        opts["fit"] = fit if fit != "harem" else "wide"
        opts["hood"] = _val(f, "hood", "yes" if kind == "hoodie" else "no") == "yes" or \
            _val(f, "neckline") == "hood"
        t = _val(f, "pockets", [])
        t = t if isinstance(t, list) else [t]
        opts["kangaroo"] = "kangaroo" in t
        opts["sleeve_style"] = "raglan" if _val(f, "sleeve") == "raglan" else "set_in"
    elif kind == "skirt":
        module = "skirt"
        opts["style"] = {"a-line": "a_line", "circle_skirt": "circle", "wide": "gathered",
                         "straight": "gathered", "slim": "straight"}.get(sil, "gathered")
        lg = _val(f, "length", "knee")
        opts["length"] = {"mini": "mini", "knee": "knee", "midi": "midi", "maxi": "maxi", "short": "mini",
                          "long": "maxi"}.get(lg, "knee")
    elif kind == "beanie":
        module = "beanie"
    elif kind == "loop":
        module = "loop"
    else:
        module = "pants_basic"
        issues.append(f"There is no module for \"{kind}\".")
    if fabric:
        opts["fabric"] = fabric if fabric != "knit" else "jersey"
    prop = f.get("proportions", {})
    if module == "pants_basic" and prop:
        # proportions drive option parameters (never body measurements!)
        if "hem_to_hip" in prop and not opts.get("cuffs"):
            opts["_hem_ratio"] = float(prop["hem_to_hip"])
        if prop.get("crotch") == "deep":
            opts["fit"] = "harem"
            opts["style"] = "harem"
    low = [LABELS[k] for k, v in f.items() if k in LABELS and v["confidence"] < 0.55]
    return dict(module=module, options=opts, not_covered=issues, uncertain=low)


# ---------------------------------------------------------------------------
# Automatic proportions from cut-out images (pants)
# ---------------------------------------------------------------------------

def _simple_mask(img):
    import cv2
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab = cv2.GaussianBlur(lab, (0, 0), 3)
    h, w = lab.shape[:2]
    b = np.concatenate([lab[:10].reshape(-1, 3), lab[-10:].reshape(-1, 3), lab[:, :10].reshape(-1, 3),
                        lab[:, -10:].reshape(-1, 3)])
    d = np.linalg.norm(lab - np.median(b, axis=0), axis=2)
    d8 = np.clip(d / d.max() * 255, 0, 255).astype(np.uint8)
    _, m = cv2.threshold(d8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    n, lab_, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return (lab_ == k).astype(np.uint8) * 255


def pants_proportions(image) -> dict:
    """Ratios of flat-lying / cut-out pants (scale-free)."""
    import cv2

    import photo_measure as PM
    img = cv2.imread(image) if isinstance(image, str) else image
    mask = _simple_mask(img)
    mask, img2, _ = PM.upright(mask, img, 1.0)
    res, geo, _ = PM.measure_pants(mask, img2, 1.0)
    hip = res["hip_flat"]
    r = dict(rise_to_length=res["front_rise"] / res["outseam"],
             hem_to_hip=res["opening_flat"] / hip,
             midleg_to_hip=res["knee_flat"] / hip,
             hem_to_midleg=res["opening_flat"] / max(res["knee_flat"], 1),
             rib=res["cuff_h"] > 0.04 * res["outseam"])
    return r


def classify_pants(r: dict) -> dict:
    harem_score = (r["rise_to_length"] - 0.30) / 0.03 + (0.52 - r["hem_to_midleg"]) / 0.04
    if harem_score > 1.0:
        sil, conf = "harem", min(0.95, 0.6 + harem_score * 0.1)
    elif r["midleg_to_hip"] < 0.43 and r["hem_to_midleg"] > 0.62:
        sil, conf = "slim", 0.75
    elif r["hem_to_hip"] > 0.40:
        sil, conf = "wide", 0.65
    else:
        sil, conf = "straight", 0.6
    feats = {"garment_type": {"value": "pants", "confidence": 0.9},
             "silhouette": {"value": sil, "confidence": round(conf, 2)},
             "leg_finish": {"value": "rib" if r["rib"] else "hem", "confidence": 0.7},
             "proportions": {k: round(float(v), 3) for k, v in r.items() if k != "rib"}}
    if sil == "harem":
        feats["proportions"]["crotch"] = "deep"
    return feats


def main(argv=None):
    ap = argparse.ArgumentParser(description="Photo mode A: map garment features to a module")
    ap.add_argument("features", nargs="?", help="feature JSON file")
    ap.add_argument("--image", help="cut-out photo of pants (automatic proportions)")
    a = ap.parse_args(argv)
    if a.image:
        feats = classify_pants(pants_proportions(a.image))
    else:
        if not a.features:
            ap.error("give a feature JSON file or --image")
        with open(a.features, encoding="utf-8") as f:
            feats = json.load(f)
    print(confirmation_text(feats))
    print()
    print(json.dumps(map_to_module(feats), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
